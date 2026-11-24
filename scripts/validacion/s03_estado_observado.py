#!/usr/bin/env python3
"""NETLAB360 S03: comparar SoT declarativo contra interfaces IPv4 y OSPF reales.

SOLO LECTURA: Docker inspect; nsenter ip -j -4 addr; vtysh neighbors.
No hace apply, no cambia FRR, ip, nftables, SSH, interfaces ni Docker.
Salida normalizada sin timestamp para permitir comparar hashes en dos lecturas.
"""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path.home() / "proyectos/netlab360"
SOT = Path.home() / "netlab360-bootstrap/s03/rendered/sot-s03.json"
OUTPUT = Path.home() / "netlab360-bootstrap/s03/observado/estado-real-s03.json"
FULL = {"R-HQ": 4, "R-S1": 2, "R-S2": 2}


def run(*args: str) -> str:
    p = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if p.returncode:
        raise RuntimeError(f"Comando solo lectura falló ({p.returncode}): {' '.join(args)}\n{p.stderr}")
    return p.stdout


def addr_map(ip_json: list[dict]) -> dict[str, set[str]]:
    out = {}
    for item in ip_json:
        interface = item["ifname"].split("@", 1)[0]
        prefixes = set()
        for addr in item.get("addr_info", []):
            if addr.get("family") == "inet":
                prefixes.add(f"{addr['local']}/{int(addr['prefixlen'])}")
        out[interface] = prefixes
    return out


# Derivamos las direcciones esperadas de la fuente declarativa sin aplicar configuración.
def expected_ips(device: dict) -> dict[str, set[str]]:
    out = {"lo": {str(ipaddress.ip_interface(device["loopback"]))}}
    for v in device["vlans"]:
        mask = ipaddress.ip_network(v["subnet"]).prefixlen
        out[v["interface"]] = {f"{v['gateway']}/{mask}"}
    for wan in device["wan"]:
        out[wan["interface"]] = {str(ipaddress.ip_interface(wan["address"]))}
    return out


# Contrastamos el inventario candidato con la identidad y estado real de los routers.
def audit() -> dict:
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal; validar sudo -v antes")
    source = SOT.read_bytes()
    sot = json.loads(source)
    if (sot.get("project") != "NETLAB360"
            or sot.get("source_status") != "candidate"
            or set(sot.get("devices", {})) != set(FULL)):
        raise RuntimeError("SoT fuente no corresponde a 3 routers S02 candidate")
    host = run("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    gateway = run("ip", "-4", "route", "show", "default")
    if "192.168.47.40/24" not in host or "default via 192.168.47.2 dev ens33" not in gateway:
        raise RuntimeError("Gestión host inesperada")
    report = {
        "project": "NETLAB360",
        "scope": "read-only IPv4 interfaces and OSPF neighbor counts; not policy/ACL compliance",
        "source_status": "candidate",
        "sot_sha256": hashlib.sha256(source).hexdigest(),
        "devices": {},
    }
    vlan_ok = wan_ok = loop_ok = 0
    for logical, device in sorted(sot["devices"].items()):
        cname = device["container"]
        meta = json.loads(run("sudo", "-n", "docker", "inspect", cname))[0]
        if (not meta["State"]["Running"]
                or meta["HostConfig"]["NetworkMode"] != "none"
                or (meta["Config"].get("Labels") or {}).get("com.docker.compose.project") != "netlab360-s02-wan"):
            raise RuntimeError(f"Contenedor fuera de alcance S02: {cname}")
        pid = str(meta["State"]["Pid"])
        ipdata = json.loads(run("sudo", "-n", "nsenter", "-t", pid, "-n",
                               "ip", "-j", "-4", "addr", "show"))
        actual = addr_map(ipdata)
        desired = expected_ips(device)
        for interface, required in desired.items():
            current = actual.get(interface, set())
            if not required.issubset(current):
                raise RuntimeError(
                    f"S03_DRIFT={logical}/{interface}: deseado={sorted(required)} observado={sorted(current)}"
                )
            if interface == "lo":
                loop_ok += 1
            elif interface.startswith("trunk0."):
                vlan_ok += 1
            else:
                wan_ok += 1
        neighbors = run("sudo", "-n", "docker", "exec", cname,
                        "vtysh", "-c", "show ip ospf neighbor")
        full = sum("Full" in row for row in neighbors.splitlines())
        if full != FULL[logical]:
            raise RuntimeError(f"S03_OSPF_DRIFT={logical}, Full={full}, esperado={FULL[logical]}")
        report["devices"][logical] = {
            "container": cname,
            "loopback": sorted(actual["lo"] & desired["lo"]),
            "vlan_interfaces": {v["interface"]: sorted(actual[v["interface"]] & desired[v["interface"]])
                                for v in device["vlans"]},
            "wan_interfaces": {v["interface"]: sorted(actual[v["interface"]] & desired[v["interface"]])
                               for v in device["wan"]},
            "ospf_neighbors_full": full,
        }
        print(f"S03_OBSERVADO_{logical}=LOOPBACK_OK VLAN={len(device['vlans'])} WAN={len(device['wan'])} OSPF_FULL={full}")
    print(f"S03_COMPARACION_LOOPBACK={loop_ok}/3")
    print(f"S03_COMPARACION_VLAN={vlan_ok}/9")
    print(f"S03_COMPARACION_WAN_EXTREMOS={wan_ok}/8")
    print("S03_OBSERVADO_OSPF_FULL=4+2+2")
    print("S03_HOST_GESTION_INTACTO=SI")
    if (loop_ok, vlan_ok, wan_ok) != (3, 9, 8):
        raise RuntimeError("Inventario declarado y observado no tiene cardinalidad prevista")
    return report


def main() -> None:
    doc = audit()
    if OUTPUT.is_symlink():
        raise RuntimeError("Destino de estado observado es symlink")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.parent.is_symlink():
        raise RuntimeError("Directorio de observado es symlink")
    OUTPUT.write_text(json.dumps(doc, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    print(f"S03_ESTADO_OBSERVADO={OUTPUT}")
    print("S03_AUDITORIA_READONLY=OK")
    print("S03_APLICACION_ANSIBLE_EJECUTADA=NO")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"S03_AUDITORIA_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
