"""S07: observaciones de scrapes Prometheus S04, sin cambios de red."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener

from adaptadores_noc import NoRedirect, unique_pairs, reject_constant, now_utc
from contrato_eventos import make_event, normalize_batch

JOB = "netlab360-s04-multisede"
INSTANCE = "127.0.0.1:9110"
PREFIX = "netlab360_s04_"
METRICS = ("up", PREFIX+"source_up", PREFIX+"topology_mode",
           PREFIX+"router_running", PREFIX+"wan_admin_up", PREFIX+"vlan_admin_up")
QUERY = ('{__name__=~"' + "|".join(METRICS) + '",job="' + JOB
         + '",instance="' + INSTANCE + '"}[120s]')
URL = "http://127.0.0.1:9091/api/v1/query?" + urlencode({"query": QUERY})
MODES = ("offline", "partial", "active", "unknown")
WAN = {"HQ": ("s1p", "s1b", "s2p", "s2b"),
       "S1": ("s1p", "s1b"), "S2": ("s2p", "s2b")}
VLANS = {"HQ": (110, 120, 130), "S1": (210, 220, 230), "S2": (310, 320, 330)}
MAX_BYTES = 524288


def labels_for(name, **labels):
    return tuple(sorted({"__name__": name, "job": JOB, "instance": INSTANCE,
                         **labels}.items()))


def expected_keys():
    keys = {labels_for("up"), labels_for(PREFIX+"source_up")}
    keys.update(labels_for(PREFIX+"topology_mode", mode=m) for m in MODES)
    for site in WAN:
        keys.add(labels_for(PREFIX+"router_running", router="R-"+site))
        keys.update(labels_for(PREFIX+"wan_admin_up", site=site, interface=i)
                    for i in WAN[site])
        keys.update(labels_for(PREFIX+"vlan_admin_up", site=site, vlan=str(v))
                    for v in VLANS[site])
    return keys


def parse_matrix(payload):
    """Extraer último scrape real de cada serie autorizada, no hora de consulta."""
    if not isinstance(payload, dict) or payload.get("status") != "success" or payload.get("warnings"):
        return {}
    data = payload.get("data")
    if not isinstance(data, dict) or data.get("resultType") != "matrix":
        return {}
    rows = data.get("result")
    if not isinstance(rows, list):
        return {}
    expected = expected_keys()
    result, seen, repeated = {}, set(), set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("metric"), dict):
            continue
        metric = row["metric"]
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in metric.items()):
            continue
        if metric.get("context", "s04") != "s04" or metric.get("laboratory", "netlab360-lab") != "netlab360-lab":
            continue
        key = tuple(sorted((k, v) for k, v in metric.items()
                           if k not in ("context", "laboratory")))
        if key not in expected:
            continue
        if key in seen:
            repeated.add(key)
        seen.add(key)
        values = row.get("values")
        if not isinstance(values, list) or not values or len(values) > 1000:
            continue
        last = None
        valid = True
        for pair in values:
            if not isinstance(pair, list) or len(pair) != 2:
                valid = False
                break
            epoch, value = pair
            if (type(epoch) not in (int, float) or not 0 <= epoch <= 4102444800
                    or not math.isfinite(epoch) or (last is not None and epoch <= last[0])):
                valid = False
                break
            last = (epoch, value)
        if valid and last is not None and last[1] in ("-1", "0", "1"):
            result[key] = (last[0], int(last[1]))
    return {k: v for k, v in result.items() if k not in repeated}


def project(payload, received):
    values = parse_matrix(payload)
    up = values.get(labels_for("up"))
    collector = values.get(labels_for(PREFIX+"source_up"))
    events = []

    def add(subject, resource, sample, state="UNKNOWN", site=None, peer=None, details=None):
        stamp = datetime.fromtimestamp(sample[0], timezone.utc).isoformat() if sample else None
        events.append(make_event(source="PROMETHEUS_S04", subject=subject,
                      resource_id=resource, site=site, peer_site=peer,
                      observed_at_utc=stamp, received_at_utc=received,
                      available=sample is not None, state=state,
                      details={"timestamp_scope": "PROMETHEUS_SCRAPE", **(details or {})}))

    up_ok = up is not None and up[1] in (0, 1)
    add("EXPORTER", "S04-EXPORTER", up if up_ok else None,
        "NORMAL" if up_ok and up[1] == 1 else "FAULT" if up_ok else "UNKNOWN",
        details={"scope": "SCRAPE_AVAILABILITY", "up": up[1]} if up_ok else {})
    collector_ok = (up_ok and up[1] == 1 and collector is not None
                    and collector[0] == up[0] and collector[1] in (0, 1))
    add("EXPORTER", "S04-COLLECTOR", collector if collector_ok else None,
        "NORMAL" if collector_ok and collector[1] == 1 else "UNKNOWN",
        details={"scope": "COLLECTOR_READ", "source_up": collector[1]} if collector_ok else {})
    gate = collector_ok and collector[1] == 1

    def sample(name, **labels):
        row = values.get(labels_for(name, **labels))
        return row if gate and row is not None and row[0] == up[0] else None

    modes = {m: sample(PREFIX+"topology_mode", mode=m) for m in MODES}
    mode = None
    if all(row is not None and row[1] in (0, 1) for row in modes.values()):
        selected = [m for m, row in modes.items() if row[1] == 1]
        if len(selected) == 1:
            mode = selected[0]
    add("TOPOLOGY", "MULTISEDE", modes[mode] if mode else None,
        details={"scope": "ROUTER_EXISTENCE_ONLY", "reported_topology": mode} if mode else {})

    for site, interfaces in WAN.items():
        row = sample(PREFIX+"router_running", router="R-"+site)
        add("METRIC", "R-"+site, row, site=site,
            details={"scope": "CONTAINER_RUNNING_ONLY", "running": row[1]} if row else {})
        for interface in interfaces:
            row = sample(PREFIX+"wan_admin_up", site=site, interface=interface)
            peer = ("S1" if interface.startswith("s1") else "S2") if site == "HQ" else "HQ"
            add("WAN", f"WAN-END-{site}-{interface}", row, site=site, peer=peer,
                details={"scope": "ADMIN_STATE_ONLY", "admin_up": row[1],
                         "interface": interface} if row else {})
        for vlan in VLANS[site]:
            row = sample(PREFIX+"vlan_admin_up", site=site, vlan=str(vlan))
            add("VLAN", f"VLAN-{vlan}", row, site=site,
                details={"scope": "ADMIN_STATE_ONLY", "admin_up": row[1],
                         "vlan": vlan} if row else {})
    return events


def read_prometheus():
    try:
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(URL, timeout=10) as response:
            if response.status != 200:
                raise ValueError("HTTP_STATUS")
            raw = response.read(MAX_BYTES+1)
        if len(raw) > MAX_BYTES:
            raise ValueError("BODY_TOO_LARGE")
        payload = json.loads(raw, object_pairs_hook=unique_pairs,
                             parse_constant=reject_constant)
        return payload, now_utc(), "HTTP_OK"
    except (OSError, ValueError, UnicodeError, RecursionError):
        return None, now_utc(), "UNAVAILABLE_OR_INVALID"


def collect():
    payload, received, status = read_prometheus()
    batch = normalize_batch(project(payload, received))
    batch["sources"] = {"PROMETHEUS_S04": status}
    batch["mode"] = "READ_ONLY"
    return batch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args()
    batch = collect()
    if not args.summary:
        print(json.dumps(batch, ensure_ascii=False, indent=2, allow_nan=False))
        return
    print("NETLAB360 | S07-001C1 | PROMETHEUS SCRAPES")
    for e in sorted(batch["events"], key=lambda e: (e["subject"], e["resource_id"])):
        print(f"{e['resource_id']:24} | {e['quality']:7} | {e['state']:8} | {e['details']}")
    print("CALIDAD=" + json.dumps(dict(Counter(e["quality"] for e in batch["events"]))))
    print("MUTACIONES_AUTORIZADAS=NO")


if __name__ == "__main__":
    main()
