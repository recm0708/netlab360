"""Lectura puntual de adyacencias OSPF y FIB de routers S02 propios."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import socket
import subprocess

from contrato_eventos import make_event, normalize_batch

SITES = ("HQ", "S1", "S2")
LOOPS = {"HQ":"10.79.0.1", "S1":"10.79.0.2", "S2":"10.79.0.3"}
NAMES = {s: "nl360-s02-r-"+s.lower() for s in SITES}
# Interface -> (peer, local address, remote address)
LINKS = {
    "HQ": {"s1p":("S1","10.78.0.1","10.78.0.2"),
           "s1b":("S1","10.78.0.5","10.78.0.6"),
           "s2p":("S2","10.78.0.9","10.78.0.10"),
           "s2b":("S2","10.78.0.13","10.78.0.14")},
    "S1": {"s1p":("HQ","10.78.0.2","10.78.0.1"),
           "s1b":("HQ","10.78.0.6","10.78.0.5")},
    "S2": {"s2p":("HQ","10.78.0.10","10.78.0.9"),
           "s2b":("HQ","10.78.0.14","10.78.0.13")},
}
OWNER = "NETLAB360_S02_WAN_LINKS_V1"
STATES = {"Full","Down","Attempt","Init","2-Way","ExStart","Exchange","Loading"}


def now():
    return datetime.now(timezone.utc).isoformat()


def run(*argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=15, check=False)
    if p.returncode or len(p.stdout) > 262144:
        raise RuntimeError("READ_FAILED")
    return p.stdout


def management():
    if socket.gethostname() != "netlab360-lab":
        raise RuntimeError("HOSTNAME")
    if "192.168.47.40/24" not in run("ip","-4","-o","addr","show","dev","ens33"):
        raise RuntimeError("MANAGEMENT_IP")
    if not run("ip","-4","route","show","default").startswith("default via 192.168.47.2 dev ens33"):
        raise RuntimeError("MANAGEMENT_ROUTE")


def ownership():
    path = Path.home() / "netlab360-bootstrap/s02/wan-links-state.json"
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 262144:
        raise RuntimeError("STATE_INVALID")
    doc = json.loads(path.read_text(encoding="utf-8"))
    ids = doc.get("ids")
    if doc.get("owner") != OWNER or not isinstance(ids, dict) or set(ids) != {"R-"+s for s in SITES}:
        raise RuntimeError("OWNER_INVALID")
    if not all(isinstance(v,str) and re.fullmatch(r"[0-9a-f]{64}",v) for v in ids.values()):
        raise RuntimeError("ID_INVALID")
    if len(set(ids.values())) != 3:
        raise RuntimeError("ID_DUPLICATE")
    return ids


def inspect(site, expected):
    rows = json.loads(run("sudo","-n","docker","inspect",NAMES[site]))
    if not isinstance(rows,list) or len(rows)!=1:
        raise RuntimeError("INSPECT_INVALID")
    row = rows[0]
    if (row["Id"] != expected or row["Name"] != "/"+NAMES[site]
            or row["State"]["Running"] is not True
            or row["HostConfig"]["NetworkMode"] != "none"
            or (row["Config"].get("Labels") or {}).get("com.docker.compose.project") != "netlab360-s02-wan"
            or type(row["State"]["Pid"]) is not int or row["State"]["Pid"] <= 1):
        raise RuntimeError("ROUTER_IDENTITY")
    return row["State"]["Pid"]


def parse_neighbors(site, raw):
    """Parser conservador de la tabla FRR: identidad, interfaz y vecino."""
    if not isinstance(raw,str) or len(raw)>262144:
        return None
    result = {}
    header = False
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Neighbor ID") and "State" in line and "Interface" in line:
            header = True
            continue
        if not header:
            # FRR puede mostrar encabezados de instancia/VRF antes de la tabla.
            if line.startswith(("VRF:", "OSPF Instance:", "OSPF instance:")):
                continue
            return None
        fields = line.split()
        if len(fields)<6 or not fields[1].isdigit():
            return None
        state = fields[2].split("/")[0]
        if state not in STATES:
            return None
        candidates = [(i,t.split(":",1)[0]) for i,t in enumerate(fields)
                      if t.split(":",1)[0] in LINKS[site]]
        if len(candidates)!=1:
            return None
        i, iface = candidates[0]
        peer, local, remote = LINKS[site][iface]
        if (i<4 or fields[0]!=LOOPS[peer] or fields[i-1]!=remote
                or iface in result):
            return None
        if ":" in fields[i] and fields[i].split(":",1)[1] not in (local, local+"/30"):
            return None
        result[iface] = state
    return result if header else None


def parse_route(site, peer, raw):
    try:
        rows = json.loads(raw)
        if not isinstance(rows,list) or len(rows)!=1 or not isinstance(rows[0],dict):
            return None
        row = rows[0]
        iface = row.get("dev")
        if iface not in LINKS[site]:
            return None
        next_peer, _, gateway = LINKS[site][iface]
        via = peer if site=="HQ" else "HQ"
        if (next_peer != via or row.get("gateway") != gateway
                or row.get("dst") != LOOPS[peer]
                or row.get("type","unicast") != "unicast"):
            return None
        return {"interface":iface,"gateway":gateway,"destination":LOOPS[peer],
                "selection":"PRIMARY" if iface.endswith("p") else "BACKUP",
                "traffic_measured":False}
    except (ValueError, TypeError, KeyError):
        return None


def project_site(site, record):
    events = []
    received = record["received_at_utc"]
    neighbors = record.get("neighbors")
    states = parse_neighbors(site, neighbors["raw"]) if neighbors else None
    for iface,(peer,_,_) in LINKS[site].items():
        state = states.get(iface) if states is not None else None
        events.append(make_event(source="FRR_S02",subject="OSPF",
                      resource_id=f"OSPF-{site}-{iface}",site=site,peer_site=peer,
                      observed_at_utc=neighbors["observed_at_utc"] if neighbors else None,
                      received_at_utc=received,available=state is not None,
                      state="NORMAL" if state=="Full" else "DEGRADED" if state else "UNKNOWN",
                      details={"scope":"OSPF_NEIGHBOR_ONLY","interface":iface,
                               "neighbor_state":state,"router_id":LOOPS[peer]} if state else {}))
    for peer in SITES:
        if peer==site:
            continue
        row=record.get("routes",{}).get(peer)
        details=parse_route(site,peer,row["raw"]) if row else None
        events.append(make_event(source="FRR_S02",subject="FIB",
                      resource_id=f"FIB-{site}-{peer}",site=site,peer_site=peer,
                      observed_at_utc=row["observed_at_utc"] if row else None,
                      received_at_utc=received,available=details is not None,
                      state=("NORMAL" if details["selection"]=="PRIMARY" else "DEGRADED")
                      if details else "UNKNOWN",
                      details={"scope":"FIB_SELECTION_ONLY",**details} if details else {}))
    return events


def capture(*argv):
    # Completion time of this explicit local observation, not an exporter timestamp.
    raw=run(*argv)
    return {"observed_at_utc":now(),"raw":raw}


def collect():
    management()
    ids=ownership()
    records={}
    for site in SITES:
        record={"neighbors":None,"routes":{},"received_at_utc":now()}
        try:
            expected=ids["R-"+site]
            pid=inspect(site,expected)
            try:
                record["neighbors"]=capture("sudo","-n","docker","exec",expected,
                                              "vtysh","-c","show ip ospf neighbor")
            except (RuntimeError,OSError,subprocess.TimeoutExpired):
                pass
            for peer in SITES:
                if peer==site:
                    continue
                try:
                    record["routes"][peer]=capture("sudo","-n","nsenter","-t",str(pid),
                                                   "-n","ip","-j","-4","route","get",LOOPS[peer])
                except (RuntimeError,OSError,subprocess.TimeoutExpired):
                    pass
            if inspect(site,expected)!=pid:
                raise RuntimeError("PID_CHANGED")
        except (RuntimeError,OSError,subprocess.TimeoutExpired,ValueError,KeyError,TypeError):
            record={"neighbors":None,"routes":{},"error":"ROUTER_UNAVAILABLE_OR_UNVERIFIED"}
        record["received_at_utc"]=now()
        records[site]=record
    management()
    batch=normalize_batch([e for site,r in records.items() for e in project_site(site,r)])
    batch["mode"]="READ_ONLY"
    batch["sources"]={"FRR_S02":"LOCAL_READ"}
    return records,batch


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary",action="store_true")
    args=parser.parse_args()
    raw,batch=collect()
    if not args.summary:
        print(json.dumps({"raw":raw,"batch":batch},ensure_ascii=False,indent=2,allow_nan=False))
        return
    for e in sorted(batch["events"],key=lambda e:(e["subject"],e["resource_id"])):
        print(f"{e['resource_id']:18} | {e['quality']:7} | {e['state']:8} | {e['details']}")
    print("CALIDAD="+json.dumps(dict(Counter(e["quality"] for e in batch["events"]))))
    print("MUTACIONES_AUTORIZADAS=NO")


if __name__=="__main__":
    main()
