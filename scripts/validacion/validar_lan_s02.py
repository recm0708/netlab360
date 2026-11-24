#!/usr/bin/env python3
"""NETLAB360 S02 LAN: verificar nueve VLAN 802.1Q y conectividad L3.

Solo lectura + ping de red. Sin cambios en hosts, FW o FRR.
"""
from __future__ import annotations
import importlib.util
import ipaddress
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("s02lan", ROOT / "scripts/laboratorio/s02_lan_vlan.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def cmd(*args: str, allow: bool = False) -> str:
    p = subprocess.run(args, capture_output=True, text=True, timeout=20)
    if p.returncode and not allow:
        raise RuntimeError(f"exit {p.returncode} {' '.join(args)} {p.stdout} {p.stderr}")
    return p.stdout


def ping(source: str, dest: str) -> bool:
    out = cmd("sudo", "-n", "ip", "netns", "exec", source,
              "ping", "-n", "-c", "2", "-W", "2", dest)
    return re.search(r"(?:^|,\s)0% packet loss(?:,|$)", out, re.MULTILINE) is not None


def main() -> None:
    d = mod.plan()
    if not mod.STATE.is_file() or mod.STATE.is_symlink():
        raise RuntimeError("Estado LAN sin propietario o no creado")
    routers = mod.router_state()
    state = json.loads(mod.STATE.read_text(encoding="utf-8"))
    mod.owns(state, routers)
    count = 0
    for site, values in d.items():
        sw = values["switch"]
        vshow = cmd("sudo", "-n", "ip", "netns", "exec", sw, "bridge", "vlan", "show")
        for v in values["vlans"]:
            vid = str(v["vid"])
            if not re.search(r"\b" + re.escape(vid) + r"\b", vshow):
                raise RuntimeError(f"VLAN {site}/{vid} no existe en bridge")
            if not ping(v["host"], v["gateway"]):
                raise RuntimeError(f"Gateway VLAN inaccesible: {site}/{vid}")
            count += 1
            print(f"S02_VLAN_GATEWAY_{site}_{vid}=OK")
    if count != 9:
        raise RuntimeError("Recuento gateways incorrecto")
    print("S02_VLAN_GATEWAYS=9/9")
    cases = (
        ("HQ", 110, "HQ", 120),
        ("HQ", 110, "S1", 220),
        ("HQ", 110, "S2", 320),
        ("S1", 210, "S2", 320),
        ("S2", 310, "S1", 220),
        ("S1", 210, "HQ", 120),
    )
    index = {(site, v["vid"]): v
             for site, row in d.items() for v in row["vlans"]}
    for a, va, b, vb in cases:
        src = index[(a, va)]["host"]
        dst = ipaddress.ip_interface(index[(b, vb)]["host_ip"]).ip
        if not ping(src, str(dst)):
            raise RuntimeError(f"ICMP {a}:{va}->{b}:{vb} falló")
        print(f"S02_ICMP_VLAN_{a}{va}_A_{b}{vb}=OK")
    print("S02_LAN_COMUNICACION=6/6")
    if not mod.management_snapshot_equal(mod.host_state(), state["host"]):
        raise RuntimeError("Cambio en la ruta/IP de gestión")
    print("S02_HOST_GESTION_INTACTO=SI")
    print("S02_LAN_VALIDADA=OK")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"S02_LAN_VALIDACION_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
