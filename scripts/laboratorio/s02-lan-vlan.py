#!/usr/bin/env python3
"""NETLAB360 S02: 3 switches bridge vlan_filtering, 9 VLAN, 9 hosts isolados.

plan y precheck no modifican sistema. up crea 12 netns y enlaces exclusivos.
down limpia recursos propios. No modifica ens33/VMnet8 ni rutas del host.
Supone los 3 FRR y cuatro WAN funcionales, con snapshot VMware disponible.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

# Repo relativo al script: funciona tanto en la VM como en GitHub Actions.
ROOT = Path(__file__).resolve().parents[2]
IPAM = ROOT / "inventario/ipam/topologia-s02.yaml"
STATE = Path.home() / "netlab360-bootstrap/s02/lan-vlan-state.json"
WAN_STATE = Path.home() / "netlab360-bootstrap/s02/wan-links-state.json"
OWNER = "NETLAB360_S02_LAN_8021Q_V1"
ROUTERS = {"HQ": "nl360-s02-r-hq", "S1": "nl360-s02-r-s1", "S2": "nl360-s02-r-s2"}
WAN_OWNER = "NETLAB360_S02_WAN_LINKS_V1"


def run(*argv: str, allow: bool = False, timeout: int = 35) -> str:
    p = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
    if p.returncode and not allow:
        raise RuntimeError(f"Fallo ({p.returncode}): {' '.join(argv)}\n{p.stdout[-1000:]} {p.stderr[-1200:]}")
    return p.stdout


def sudo(*argv: str, **kwargs) -> str:
    return run("sudo", "-n", *argv, **kwargs)


def plan() -> dict:
    d = yaml.safe_load(IPAM.read_text(encoding="utf-8"))
    if d.get("schema_version") != "0.2" or set(d["sites"]) != set(ROUTERS):
        raise ValueError("Inventario S02 inesperado")
    out = {}
    for site in ROUTERS:
        vlans = d["sites"][site]["vlans"]
        if len(vlans) != 3 or len(set(v["id"] for v in vlans)) != 3:
            raise ValueError(f"VLAN no validas en {site}")
        site_rows = []
        for v in vlans:
            net = ipaddress.ip_network(v["subnet"])
            gw = ipaddress.ip_address(v["gateway"])
            # Usuarios .10, servicios .20, gestion interna .30.
            last_octets = {10: 10, 20: 20, 30: 30}
            if v["id"] % 100 not in last_octets:
                raise ValueError(f"VLAN no admitida para host prueba: {v['id']}")
            lastoct = last_octets[v["id"] % 100]
            ipaddr = ipaddress.ip_address(int(net.network_address) + lastoct)
            if ipaddr not in net or gw not in net or ipaddr == gw:
                raise ValueError(f"Subred/host fuera de rango: {v}")
            site_rows.append({
                "vid": int(v["id"]), "name": v["name"],
                "subnet": str(net), "gateway": str(gw),
                "host_ip": str(ipaddr) + "/" + str(net.prefixlen),
                "host": f"nl360-s02-h-{site.lower()}-{v['id']}",
            })
            print(f"S02_VLAN_PLAN={site} VID={v['id']} SUBNET={net} GW={gw} HOST={ipaddr}")
        out[site] = {"switch": f"nl360-s02-sw-{site.lower()}", "vlans": site_rows}
    print("S02_LAN_PLAN_SEDES=3 SWITCHES=3 VLAN=9 HOSTS=9")
    return out


def router_state() -> dict:
    if not WAN_STATE.is_file() or WAN_STATE.is_symlink():
        raise RuntimeError("WAN S02 sin propiedad/estado; LAN bloqueada")
    own = json.loads(WAN_STATE.read_text())
    if own.get("owner") != WAN_OWNER:
        raise RuntimeError("WAN S02 no pertenece al proyecto")
    result = {}
    for site, name in ROUTERS.items():
        doc = json.loads(sudo("docker", "inspect", name))[0]
        logical = "R-" + site
        if (not doc["State"]["Running"] or
            doc["HostConfig"]["NetworkMode"] != "none" or
            doc["Id"] != own["ids"].get(logical) or
            (doc["Config"].get("Labels") or {}).get("com.docker.compose.project") != "netlab360-s02-wan"):
            raise RuntimeError(f"Router no validado: {name}")
        result[site] = {"name": name, "pid": str(doc["State"]["Pid"]), "id": doc["Id"]}
    return result


def router_ns(routers: dict, site: str, *args: str, allow: bool = False) -> str:
    return sudo("nsenter", "-t", routers[site]["pid"], "-n", *args, allow=allow)


def nsexec(name: str, *args: str, allow: bool = False) -> str:
    return sudo("ip", "netns", "exec", name, *args, allow=allow)


def ip_ns(name: str, *args: str) -> str:
    return sudo("ip", "-n", name, *args)


def host_state() -> dict:
    a = run("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    r = run("ip", "-4", "route", "show", "table", "main")
    if "192.168.47.40/24" not in a or "default via 192.168.47.2 dev ens33" not in r:
        raise RuntimeError("Gestion host inesperada")
    return {"ens33": a, "routes": r}


def check(plan_data: dict, routers: dict) -> dict:
    before = host_state()
    if STATE.exists() or STATE.is_symlink():
        raise RuntimeError("LAN state existente; usar status/down o diagnostico")
    existing_ns = {s.split()[0] for s in sudo("ip", "netns", "list").splitlines() if s.strip()}
    for site, row in plan_data.items():
        desired = [row["switch"]] + [v["host"] for v in row["vlans"]]
        for n in desired:
            if n in existing_ns:
                raise RuntimeError(f"Namespace existente: {n}")
        for dev in ("trunk0", "lrouter"):
            if router_ns(routers, site, "ip", "link", "show", "dev", dev, allow=True):
                raise RuntimeError(f"Interfaz ya existe {site}/{dev}")
        for v in row["vlans"]:
            dev = f"trunk0.{v['vid']}"
            if router_ns(routers, site, "ip", "link", "show", "dev", dev, allow=True):
                raise RuntimeError(f"Subinterfaz ya existe {site}/{dev}")
    if run("git", "-C", str(ROOT), "status", "--porcelain").strip():
        raise RuntimeError("Git tiene cambios locales")
    for site, target, dev in (("HQ", "10.79.0.2", "s1p"),
                              ("HQ", "10.79.0.3", "s2p"),
                              ("S1", "10.79.0.1", "s1p"),
                              ("S2", "10.79.0.1", "s2p")):
        route = router_ns(routers, site, "ip", "-4", "route", "get", target, allow=True)
        if f"dev {dev}" not in route:
            raise RuntimeError(f"WAN principal no validada antes de LAN: {site}->{target} {route}")
    print("S02_WAN_PRINCIPALES_PRELAN=OK")
    print("S02_LAN_PRECHECK=OK")
    return before


def owns(data: dict, routers: dict) -> None:
    if data.get("owner") != OWNER or set(data.get("router_ids", {})) != set(ROUTERS):
        raise RuntimeError("Estado LAN de propietario invalido")
    for s in ROUTERS:
        if data["router_ids"][s] != routers[s]["id"]:
            raise RuntimeError(f"Router cambió desde LAN up: {s}")


def cleanup(d: dict, routers: dict) -> None:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("No hay LAN state")
    data = json.loads(STATE.read_text())
    owns(data, routers)
    names = data.get("namespaces", [])
    for site in ROUTERS:
        for device in ("trunk0", "tr-r"):
            if router_ns(routers, site, "ip", "link", "show", "dev", device, allow=True):
                router_ns(routers, site, "ip", "link", "delete", "dev", device)
                print(f"S02_LAN_TRUNK_RETIRADO={site}/{device}")
    for name in reversed(names):
        if name in {s.split()[0] for s in sudo("ip", "netns", "list").splitlines() if s.strip()}:
            pids = sudo("ip", "netns", "pids", name).split()
            for pid in pids:
                if pid.isdigit():
                    sudo("kill", "-TERM", pid, allow=True)
            sudo("ip", "netns", "delete", name)
            print(f"S02_LAN_NETNS_RETIRADO={name}")
    if host_state() != data["host"]:
        raise RuntimeError("Ruta/IP host cambió, conservar state")
    STATE.unlink()
    print("S02_LAN_DOWN=OK")


def up(d: dict, routers: dict) -> None:
    before = check(d, routers)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    reserved = [name for site, row in d.items()
                for name in [row["switch"]] + [v["host"] for v in row["vlans"]]]
    value = {"owner": OWNER, "date": datetime.now().isoformat(),
             "host": before, "router_ids": {s: routers[s]["id"] for s in ROUTERS},
             "namespaces": reserved}
    STATE.write_text(json.dumps(value, indent=2))
    try:
        for site, entry in d.items():
            sw = entry["switch"]
            sudo("ip", "netns", "add", sw)
            ip_ns(sw, "link", "set", "lo", "up")
            ip_ns(sw, "link", "add", "br0", "type", "bridge", "vlan_filtering", "1")
            ip_ns(sw, "link", "set", "br0", "up")

            # Link router--switch, ambos extremos aislados.
            ip_ns(sw, "link", "add", "tr-sw", "type", "veth", "peer", "name", "tr-r")
            ip_ns(sw, "link", "set", "tr-r", "netns", routers[site]["pid"])
            router_ns(routers, site, "ip", "link", "set", "tr-r", "name", "trunk0")
            ip_ns(sw, "link", "set", "tr-sw", "master", "br0")
            nsexec(sw, "bridge", "vlan", "del", "dev", "tr-sw", "vid", "1", allow=True)
            for v in entry["vlans"]:
                nsexec(sw, "bridge", "vlan", "add", "dev", "tr-sw", "vid", str(v["vid"]))
            ip_ns(sw, "link", "set", "tr-sw", "up")
            router_ns(routers, site, "ip", "link", "set", "trunk0", "up")

            for v in entry["vlans"]:
                vid = v["vid"]
                host = v["host"]
                port = f"a{vid}"
                peer = f"e{vid}"
                sudo("ip", "netns", "add", host)
                ip_ns(host, "link", "set", "lo", "up")
                ip_ns(sw, "link", "add", port, "type", "veth", "peer", "name", peer)
                ip_ns(sw, "link", "set", peer, "netns", host)
                ip_ns(host, "link", "set", peer, "name", "eth0")
                ip_ns(sw, "link", "set", port, "master", "br0")
                nsexec(sw, "bridge", "vlan", "del", "dev", port, "vid", "1", allow=True)
                nsexec(sw, "bridge", "vlan", "add", "dev", port, "vid",
                       str(vid), "pvid", "untagged")
                ip_ns(sw, "link", "set", port, "up")
                ip_ns(host, "addr", "add", v["host_ip"], "dev", "eth0")
                ip_ns(host, "link", "set", "eth0", "up")
                ip_ns(host, "route", "add", "default", "via", v["gateway"], "dev", "eth0")

                dev = f"trunk0.{vid}"
                router_ns(routers, site, "ip", "link", "add", "link", "trunk0",
                          "name", dev, "type", "vlan", "id", str(vid))
                router_ns(routers, site, "ip", "addr", "add",
                          v["gateway"] + "/" + v["subnet"].split("/")[1], "dev", dev)
                router_ns(routers, site, "ip", "link", "set", dev, "up")
                print(f"S02_VLAN_CREADA={site} VID={vid} HOST={v['host_ip']}", flush=True)

            output = sudo("docker", "exec", routers[site]["name"], "vtysh", "-b")
            if any(x in output.lower() for x in ("processing failure", "invalid input", "unknown command")):
                raise RuntimeError(f"Error al aplicar FRR {site}: {output}")
            print(f"S02_ROUTER_LAN_REAPLICADA={site}")
        if host_state() != before:
            raise RuntimeError("Host cambio durante construccion LAN")
        print("S02_SWITCHES=3 VLAN=9 HOSTS=9")
        print("S02_HOST_GESTION_INTACTO=SI")
        print("S02_LAN_UP=OK")
    except BaseException:
        print("S02_LAN_UP_INCOMPLETO: rollback recursos propios", file=sys.stderr)
        try:
            cleanup(d, router_state())
        except Exception as e:
            print(f"S02_LAN_ROLLBACK_ERROR={e}; estado conservado", file=sys.stderr)
        raise


def status(d: dict, routers: dict) -> None:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("LAN aun no desplegada")
    state = json.loads(STATE.read_text())
    owns(state, routers)
    for site, entry in d.items():
        sw = entry["switch"]
        print(f"========== SWITCH {site} ==========")
        print(nsexec(sw, "bridge", "vlan", "show").strip())
        print(f"S02_LAN_HOSTS_{site}={len(entry['vlans'])}")
        for v in entry["vlans"]:
            print(ip_ns(v["host"], "-4", "-br", "addr").strip())
        print(router_ns(routers, site, "ip", "-4", "-br", "addr").strip())
    if host_state() != state["host"]:
        raise RuntimeError("Gestion host alterada")
    print("S02_LAN_ESTADO=OK")
    print("S02_HOST_GESTION_INTACTO=SI")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("plan", "precheck", "up", "status", "down"))
    parser.add_argument("--snapshot-confirmado", action="store_true")
    args = parser.parse_args()
    d = plan()
    if args.action == "plan":
        return
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal")
    if args.snapshot_confirmado != (args.action == "up"):
        raise RuntimeError("up requiere --snapshot-confirmado; otros modos no")
    routers = router_state()
    if args.action == "precheck":
        check(d, routers)
    elif args.action == "up":
        up(d, routers)
    elif args.action == "status":
        status(d, routers)
    else:
        cleanup(d, routers)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"S02_LAN_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
