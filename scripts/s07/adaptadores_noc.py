"""Adaptadores de solo lectura del NOC S05 y diagnóstico S06."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import math
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

from contrato_eventos import make_event, normalize_batch

URLS = {
    "NOC_S05": "http://127.0.0.1:9130/api/v1/graph",
    "IA_S06": "http://127.0.0.1:9130/api/v1/s06/diagnostics",
}
SITES = ("HQ", "S1", "S2")
WAN = {f"WAN-{role}-HQ-{peer}": peer
       for peer in ("S1", "S2") for role in ("PRIMARIA", "RESPALDO")}
VLANS = {f"H-{site}-{vid}": (site, vid)
         for site, prefix in zip(SITES, (100, 200, 300))
         for vid in (prefix+10, prefix+20, prefix+30)}
METHODS = ("P95_RTT", "IsolationForest", "LogisticRegression")
MAX_BYTES = 262144


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def obj(value):
    return value if isinstance(value, dict) else {}


def rows_by_id(value):
    """No seleccionar arbitrariamente una fila si su identidad se repite."""
    if not isinstance(value, list):
        return {}
    rows = {}
    repeated = set()
    for row in value:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        key = row["id"]
        if key in rows:
            repeated.add(key)
        rows[key] = row
    return {key: row for key, row in rows.items() if key not in repeated}


def emit(source, subject, resource, received, *, site=None, peer=None,
         stamp=None, valid=False, state="UNKNOWN", details=None):
    return make_event(source=source, subject=subject, resource_id=resource,
                      site=site, peer_site=peer, observed_at_utc=stamp,
                      received_at_utc=received, available=valid,
                      state=state, details=details)


def graph_events(payload, received):
    """Proyectar señales del inventario fijo; nunca inferir OSPF/forwarding."""
    g = obj(payload)
    if (g.get("project") != "NETLAB360" or g.get("phase") != "S05"
            or type(g.get("schema_version")) is not int
            or g["schema_version"] != 1):
        g = {}
    events = []

    def add(subject, resource, **kw):
        events.append(emit("NOC_S05", subject, resource, received, **kw))

    tele = obj(g.get("telemetry"))
    topology = tele.get("topology")
    tele_ok = tele.get("available") is True
    stamp = tele.get("last_sample_utc")
    add("TOPOLOGY", "MULTISEDE", stamp=stamp,
        valid=tele_ok and topology in ("active", "offline"),
        state="NORMAL" if topology == "active" else "UNKNOWN",
        details={"scope": "TOPOLOGY_OBSERVATION",
                 "reported_topology": topology if topology in ("active", "offline") else "unknown"})

    links = rows_by_id(g.get("links"))
    for resource, peer in WAN.items():
        row = obj(links.get(resource))
        flag = row.get("status")
        ok = (tele_ok and row.get("type") == "wan"
              and row.get("from") == "R-HQ" and row.get("to") == "R-"+peer
              and flag in ("admin-up", "admin-down", "offline", "unknown"))
        # Admin-up no demuestra tráfico ni adyacencia; admin-down no confirma incidente.
        add("WAN", resource, site="HQ", peer=peer, stamp=stamp, valid=ok,
            state="UNKNOWN", details={"scope": "ADMIN_STATE_ONLY",
                                      "admin_state": flag if ok else "unknown"})

    nodes = rows_by_id(g.get("nodes"))
    for node, (site, vid) in VLANS.items():
        row = obj(nodes.get(node))
        flag = row.get("vlan_admin")
        ok = (tele_ok and row.get("site") == site and row.get("type") == "host"
              and type(row.get("vlan")) is int and row["vlan"] == vid
              and flag in ("admin-up", "admin-down", "unknown"))
        add("VLAN", f"VLAN-{vid}", site=site, stamp=stamp, valid=ok,
            state="UNKNOWN", details={"scope": "ADMIN_STATE_ONLY",
                                      "admin_state": flag if ok else "unknown",
                                      "vlan": vid})

    lacp = obj(g.get("lacp"))
    sites = obj(lacp.get("sites"))
    for site in SITES:
        row = obj(sites.get(site))
        status = row.get("status")
        a, b = row.get("switch_members"), row.get("client_members")
        ok = (lacp.get("status") in ("observed", "partial")
              and type(a) is int and type(b) is int
              and 0 <= a <= 2 and 0 <= b <= 2
              and status == ("up" if min(a, b) == 2
                             else "degraded" if min(a, b) == 1 else "down"))
        add("LACP", "LACP-"+site, site=site, stamp=lacp.get("observed_at_utc"),
            valid=ok, state={"up": "NORMAL", "degraded": "DEGRADED",
                             "down": "FAULT"}.get(status, "UNKNOWN") if ok else "UNKNOWN",
            details={"scope": "BOND_MEMBER_STATE", "switch_members": a,
                     "client_members": b} if ok else {})

    sdn = obj(g.get("sdn"))
    connected, flows = sdn.get("connected"), sdn.get("flow_count")
    ok = (sdn.get("available") is True
          and ((connected is True and sdn.get("status") == "connected"
                and type(flows) is int and 0 < flows <= 10**9)
               or (connected is False and sdn.get("status") == "disconnected"
                   and flows is None)))
    add("SDN", "FAUCET", stamp=sdn.get("observed_at_utc"), valid=ok,
        state=("NORMAL" if connected else "FAULT") if ok else "UNKNOWN",
        details={"scope": "CONTROLLER_ONLY", "connected": connected,
                 "flow_count": flows} if ok else {})

    ha = obj(g.get("ha_service"))
    status, backend, selected = (ha.get(k) for k in ("status", "active_backend", "selected_path"))
    ok = (ha.get("available") is True and status in ("running", "offline", "unknown")
          and (backend, selected) in ((None, None), ("BACKEND_HQ", "PRINCIPAL"),
                                      ("BACKEND_S1", "RESPALDO"))
          and (status == "running" or backend is None))
    state = "UNKNOWN"
    if ok and status == "offline":
        state = "FAULT"
    elif ok and status == "running":
        state = {"BACKEND_HQ": "NORMAL", "BACKEND_S1": "DEGRADED"}.get(backend, "UNKNOWN")
    add("HTTP_HA", "FRONTAL_HQ", site="HQ", peer="S2",
        stamp=ha.get("observed_at_utc"), valid=ok, state=state,
        details={"scope": "HTTP_FROM_S2", "status": status,
                 "active_backend": backend, "selected_path": selected}
        if ok else {})
    return events


def ia_events(payload, received):
    root = obj(payload)
    if (root.get("schema") != "NETLAB360_S06_047_NOC_AI_ADAPTER_V1"
            or root.get("mode") != "READ_ONLY_EXPLORATORY"
            or root.get("network_mutations_authorized") is not False
            or root.get("production_deployment_authorized") is not False
            or root.get("graph_s05_independent") is not True):
        root = {}
    routes = obj(root.get("routes"))
    events = []
    for peer in ("S1", "S2"):
        route = "HQ_A_"+peer
        row = obj(routes.get(route))
        methods = obj(row.get("methods"))
        predictions = list(methods.values())
        valid_predictions = (set(methods) == set(METHODS)
                             and all(v in ("NORMAL", "DEGRADED") for v in predictions))
        consensus = (predictions[0] if valid_predictions
                     and all(v == predictions[0] for v in predictions) else "UNKNOWN")
        state = "NORMAL" if consensus == "NORMAL" else "UNKNOWN"
        rtt = row.get("rtt_avg_ms")
        loss = row.get("loss_pct")
        ok = (row.get("available") is True and row.get("route") == route
              and row.get("ground_truth") == "UNKNOWN"
              and row.get("network_mutations_authorized") is False
              and row.get("production_deployment_authorized") is False
              and valid_predictions and row.get("consensus") == consensus
              and row.get("state") == state
              and row.get("reason") == {
                  "NORMAL": "BASELINE_AND_UNANIMOUS_NORMAL_SCOPED",
                  "DEGRADED": "DEGRADATION_INDICATION_UNCONFIRMED",
                  "UNKNOWN": "MODEL_DISAGREEMENT"}[consensus]
              and type(rtt) in (int, float) and 0 <= rtt <= 10**9 and math.isfinite(rtt)
              and type(loss) in (int, float) and loss == 0)
        details = ({"scope": "HQ_CLIENT_EGRESS_NETWORK_STATE", "consensus": consensus,
                    "rtt_avg_ms": rtt, "loss_pct": loss,
                    **{key: methods[key] for key in METHODS}} if ok else {})
        events.append(emit("IA_S06", "ICMP_DIAGNOSIS", route, received,
                           site="HQ", peer=peer, stamp=row.get("observed_at_utc"),
                           valid=ok, state=state if ok else "UNKNOWN", details=details))
    return events


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def unique_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def reject_constant(value):
    raise ValueError("NONFINITE_JSON")


def read_source(source):
    """Solo endpoints fijos, sin proxy, redirects, argumentos de URL ni shell."""
    if source not in URLS:
        raise ValueError("INVALID_SOURCE")
    try:
        opener = build_opener(ProxyHandler({}), NoRedirect())
        with opener.open(URLS[source], timeout=15) as response:
            if response.status != 200:
                raise ValueError("HTTP_STATUS")
            raw = response.read(MAX_BYTES+1)
        if len(raw) > MAX_BYTES:
            raise ValueError("BODY_TOO_LARGE")
        payload = json.loads(raw, object_pairs_hook=unique_pairs,
                             parse_constant=reject_constant)
        if not isinstance(payload, dict):
            raise ValueError("JSON_NOT_OBJECT")
        return payload, now_utc(), "HTTP_OK"
    except (OSError, ValueError, UnicodeError, RecursionError):
        return None, now_utc(), "UNAVAILABLE_OR_INVALID"


def collect():
    events = []
    sources = {}
    for source, adapter in (("NOC_S05", graph_events), ("IA_S06", ia_events)):
        payload, received, transport = read_source(source)
        sources[source] = transport
        events.extend(adapter(payload, received))
    batch = normalize_batch(events)
    batch["sources"] = sources
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
    print("========== NETLAB360 S07-001B ==========")
    print("MODO=SOLO_LECTURA")
    for source, status in batch["sources"].items():
        print(f"FUENTE={source} TRANSPORTE={status}")
    for e in sorted(batch["events"], key=lambda x: (x["source"], x["subject"], x["resource_id"])):
        print(f"{e['source']:8} | {e['subject']:14} | {e['resource_id']:22} | "
              f"{e['quality']:7} | {e['state']:8} | {json.dumps(e['details'], ensure_ascii=False)}")
    print("EVENTOS=" + str(len(batch["events"])))
    print("CALIDAD=" + json.dumps(dict(Counter(e["quality"] for e in batch["events"])), sort_keys=True))
    print("MUTACIONES_AUTORIZADAS=NO")


if __name__ == "__main__":
    main()
