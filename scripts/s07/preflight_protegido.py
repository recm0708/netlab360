#!/usr/bin/python3
"""Preflight privilegiado S07. Exclusivamente lecturas; no autoriza cambios."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import sys
import time

SCHEMA = "NETLAB360_S07_PROTECTED_PREFLIGHT_V1"
STATE = Path("/var/lib/netlab360/s07-preflight")
TARGET = "S1/s1b"
MAX_DURATION = 30
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


# Parsers reutilizados de S07 y S03; sin importar código del directorio del usuario.
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


def parse_frr_costs(raw: str) -> dict[str, int]:
    """Extraer costos SOLO de stanza interface, no falsos positivos globales."""
    costs: dict[str, int] = {}
    current = None
    for raw_line in raw.splitlines():
        line = raw_line.rstrip()
        if line.startswith("interface "):
            current = line[len("interface "):].strip()
            continue
        if current and line.startswith((" ", "\t")):
            match = re.fullmatch(r"\s+ip ospf cost\s+(\d+)\s*", line)
            if match:
                if current in costs:
                    raise ValueError(f"Costo OSPF duplicado en {current}")
                costs[current] = int(match.group(1))
            continue
        if line and not line.startswith((" ", "\t")):
            current = None
    return costs



def run(*argv):
    p = subprocess.run(argv, capture_output=True, text=True, timeout=5,
                       env={"PATH":"/usr/sbin:/usr/bin:/sbin:/bin","LC_ALL":"C"})
    if p.returncode or len(p.stdout)>262144:
        raise ValueError("READ_FAILED")
    return p.stdout


def management():
    if socket.gethostname()!="netlab360-lab":
        raise ValueError("HOSTNAME")
    addr=json.loads(run("/usr/sbin/ip","-j","-4","addr","show","dev","ens33"))
    routes=json.loads(run("/usr/sbin/ip","-j","-4","route","show","default"))
    if len(addr)!=1 or not any(x.get("local")=="192.168.47.40" and x.get("prefixlen")==24 for x in addr[0]["addr_info"]):
        raise ValueError("MANAGEMENT_IP")
    if len(routes)!=1 or routes[0].get("gateway")!="192.168.47.2" or routes[0].get("dev")!="ens33":
        raise ValueError("MANAGEMENT_ROUTE")
    return {"address":"192.168.47.40/24","gateway":"192.168.47.2","device":"ens33"}


def inspect(site):
    rows=json.loads(run("/usr/bin/docker","inspect",NAMES[site]))
    if len(rows)!=1:
        raise ValueError("ROUTER_IDENTITY")
    r=rows[0]
    if (r["Name"]!="/"+NAMES[site] or not re.fullmatch(r"[0-9a-f]{64}",r["Id"])
        or r["State"]["Running"] is not True or r["HostConfig"]["NetworkMode"]!="none"
        or (r["Config"].get("Labels") or {}).get("com.docker.compose.project")!="netlab360-s02-wan"
        or type(r["State"]["Pid"]) is not int or r["State"]["Pid"]<=1):
        raise ValueError("ROUTER_IDENTITY")
    return {"id":r["Id"],"pid":r["State"]["Pid"]}


def secure(p,mode,kind):
    s=p.lstat()
    if s.st_uid!=0 or s.st_gid!=0 or stat.S_IMODE(s.st_mode)!=mode or not kind(s.st_mode):
        raise ValueError("UNSAFE_STATE")


@contextmanager
def exclusive(path):
    fd=os.open(path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        s=os.fstat(fd)
        if not stat.S_ISREG(s.st_mode) or stat.S_IMODE(s.st_mode)!=0o600:
            raise ValueError("LOCK_UNSAFE")
        if os.geteuid()==0 and (s.st_uid!=0 or s.st_gid!=0):
            raise ValueError("LOCK_UNSAFE")
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("RESOURCE_BUSY") from None
        yield
    finally:
        os.close(fd)


def profile():
    return {s:{i:10 if i.endswith("p") else 100 for i in LINKS[s]} for s in SITES}


def pin_ids(pin):
    ids=pin.get("ids")
    if pin.get("schema")!="NETLAB360_S07_ROUTER_PIN_V1" or pin.get("profile")!=profile() or type(ids) is not dict or set(ids)!=set(SITES):
        raise ValueError("PIN_INVALID")
    if any(type(v) is not str or not re.fullmatch(r"[0-9a-f]{64}",v) for v in ids.values()) or len(set(ids.values()))!=3:
        raise ValueError("PIN_INVALID")
    return ids


def read_pin(path):
    secure(path,0o600,stat.S_ISREG)
    if path.stat().st_size>8192:
        raise ValueError("PIN_INVALID")
    return pin_ids(json.loads(path.read_text()))


def load_gate():
    cpu=len(os.sched_getaffinity(0))
    load=os.getloadavg()[0]
    match=re.search(r"^MemAvailable:\s+(\d+) kB$",Path("/proc/meminfo").read_text(),re.M)
    mem=int(match.group(1)) if match else 0
    if cpu<1 or load/cpu>1 or mem<524288:
        raise ValueError("HOST_LOAD_LIMIT")
    return {"load1":round(load,3),"cpus":cpu,"memory_available_kib":mem,
            "max_load_per_cpu":1,"minimum_memory_kib":524288}


def observe(ids):
    started=datetime.now(timezone.utc).isoformat()
    tick=time.monotonic()
    initial=management()
    load=load_gate()
    rows=[]
    neighbors=[]
    routes=[]
    identity={}
    for site in SITES:
        before=inspect(site)
        if before["id"]!=ids[site]:
            raise ValueError("PIN_MISMATCH")
        identity[site]=before
        raw=run("/usr/bin/docker","exec",before["id"],"vtysh","-c","show running-config")
        costs=parse_frr_costs(raw)
        for iface,wanted in profile()[site].items():
            got=costs.get(iface)
            if type(got) is not int or not 1<=got<=65535:
                raise ValueError("COST_UNKNOWN")
            rows.append({"site":site,"interface":iface,"desired":wanted,"observed":got})
        n=parse_neighbors(site,run("/usr/bin/docker","exec",before["id"],"vtysh","-c","show ip ospf neighbor"))
        if n is None or set(n)!=set(LINKS[site]) or any(v!="Full" for v in n.values()):
            raise ValueError("OSPF_NOT_FULL_OR_UNKNOWN")
        neighbors.extend({"site":site,"interface":i,"state":v} for i,v in sorted(n.items()))
        for peer in SITES:
            if peer==site:
                continue
            r=parse_route(site,peer,run("/usr/bin/nsenter","-t",str(before["pid"]),"-n","/usr/sbin/ip","-j","-4","route","get",LOOPS[peer]))
            if r is None or r["selection"]!="PRIMARY":
                raise ValueError("FIB_NOT_PRIMARY_OR_UNKNOWN")
            routes.append({"site":site,"peer":peer,**r})
        if inspect(site)!=before:
            raise ValueError("ROUTER_CHANGED")
    if any(inspect(s)!=identity[s] for s in SITES):
        raise ValueError("ROUTER_CHANGED")
    if management()!=initial:
        raise ValueError("MANAGEMENT_CHANGED")
    elapsed=time.monotonic()-tick
    if elapsed>MAX_DURATION:
        raise ValueError("PREFLIGHT_TIMEOUT")
    return {"schema":SCHEMA,"mode":"PRIVILEGED_READ_ONLY",
            "started_at_utc":started,"ended_at_utc":datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds":round(elapsed,6),"target":TARGET,"management":initial,
            "load":load,"identity_verified":True,"costs":rows,"neighbors":neighbors,"routes":routes,
            "configuration_status":"MET" if all(r["desired"]==r["observed"] for r in rows) else "NOT_MET",
            "end_to_end_availability":"NOT_MEASURED","execution_authorized":False,
            "network_mutations_authorized":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("op",choices=["enroll","check"])
    a=p.parse_args()
    if os.geteuid()!=0:
        p.error("root required")
    os.umask(0o077)
    try:
        secure(STATE,0o700,stat.S_ISDIR)
        path=STATE/"router-pin.json"
        with exclusive(STATE/"preflight.lock"):
            if a.op=="enroll":
                if path.exists() or path.is_symlink():
                    raise ValueError("PIN_EXISTS")
                ids={s:inspect(s)["id"] for s in SITES}
                pin={"schema":"NETLAB360_S07_ROUTER_PIN_V1","ids":ids,"profile":profile()}
                pin_ids(pin)
                r=observe(ids)
                if r["configuration_status"]!="MET":
                    raise ValueError("ENROLL_REQUIRES_BASELINE")
                fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                with os.fdopen(fd,"w") as f:
                    json.dump(pin,f,sort_keys=True)
                    f.write("\n")
                    f.flush()
                    os.fsync(f.fileno())
                r["pin_status"]="ENROLLED_BY_ROOT"
            else:
                r=observe(read_pin(path))
                r["pin_status"]="VERIFIED"
            print(json.dumps({"ok":True,**r},indent=2,allow_nan=False))
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as e:
        print(json.dumps({"schema":SCHEMA,"ok":False,
                          "reason":str(e) if type(e) is ValueError and re.fullmatch(r"[A-Z_]+",str(e)) else "PREFLIGHT_ERROR",
                          "execution_authorized":False,"network_mutations_authorized":False}))
        sys.exit(3)


if __name__=="__main__":
    main()
