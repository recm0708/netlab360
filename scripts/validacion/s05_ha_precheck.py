#!/usr/bin/env python3
"""NETLAB360 S05: auditoría de HA multisede, exclusivamente de solo lectura.

No despliega ni elimina interfaces, servicios, namespaces, rutas o contenedores.
Las IP indicadas son CANDIDATAS; ausencia de una IP en esta muestra no prueba
disponibilidad fuera del laboratorio o ausencia de reservas administrativas.
Uso: sudo -v; python3 scripts/validacion/s05-ha-precheck.py --check
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.request import urlopen

import yaml

ROOT = Path(__file__).resolve().parents[2]
BASE = Path.home() / "netlab360-bootstrap"
WAN = BASE / "s02/wan-links-state.json"
LAN = BASE / "s02/lan-vlan-state.json"
HA = BASE / "s05/ha/state.json"
IPAM = ROOT / "inventario/ipam/topologia-s02.yaml"

ROUTERS = {
    "HQ": "nl360-s02-r-hq",
    "S1": "nl360-s02-r-s1",
    "S2": "nl360-s02-r-s2",
}
SWITCHES = {
    "HQ": ("nl360-s02-sw-hq", 120),
    "S1": ("nl360-s02-sw-s1", 220),
    "S2": ("nl360-s02-sw-s2", 320),
}
HOSTS = {
    "HQ": ("nl360-s02-h-hq-120", "10.70.20.20", "10.70.20.1"),
    "S1": ("nl360-s02-h-s1-220", "10.71.20.20", "10.71.20.1"),
    "S2": ("nl360-s02-h-s2-320", "10.72.20.20", "10.72.20.1"),
}
CANDIDATES = {
    "BACKEND_HQ": ("10.70.20.21", "HQ", 120, "nl360-s05-ha-hq"),
    "BACKEND_S1": ("10.71.20.21", "S1", 220, "nl360-s05-ha-s1"),
    "FRONTAL_HQ": ("10.70.20.23", "HQ", 120, "nl360-s05-ha-fe"),
}


def command(*args: str, root: bool = False) -> str:
    argv = (["sudo", "-n"] if root else []) + list(args)
    p = subprocess.run(argv, text=True, capture_output=True, timeout=18)
    if p.returncode:
        raise RuntimeError(
            f"Consulta fallida exit={p.returncode}: {' '.join(args)} "
            f"stderr={p.stderr[-400:]}"
        )
    return p.stdout


def addresses(raw: str) -> set[str]:
    out = set()
    for row in json.loads(raw):
        for addr in row.get("addr_info", []):
            if addr.get("family") == "inet" and addr.get("local"):
                out.add(addr["local"])
    return out


# El marcador de propiedad evita interpretar estados ajenos como recursos HA del laboratorio.
def read_json(path: Path, expected_owner: str) -> dict:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError(f"Estado ausente o enlace simbólico: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("owner") != expected_owner:
        raise RuntimeError(f"Ownership diferente del proyecto en: {path}")
    return value


# Corroboramos las fuentes de observabilidad antes de habilitar otra comprobación HA.
def api_state() -> None:
    with urlopen("http://127.0.0.1:9110/api/v1/state", timeout=7) as r:
        s04 = json.load(r)
    with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=7) as r:
        graph = json.load(r)
    route = graph.get("routing", {}).get("routes") or {}
    if (s04.get("source_ok") is not True
            or s04.get("topology") != "active"
            or graph.get("telemetry", {}).get("available") is not True
            or graph.get("routing", {}).get("available") is not True
            or route.get("S1", {}).get("dev") != "s1p"
            or route.get("S2", {}).get("dev") != "s2p"):
        raise RuntimeError("Observación S04/NOC/FIB sin línea base estable")
    print("S05_HA_TELEMETRIA_S04_NOC=OK")
    print("S05_HA_FIB_PRINCIPALES=S1:s1p,S2:s2p")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    args = parser.parse_args()
    assert args.check
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal, no como root")
    if command("hostname").strip() != "netlab360-lab":
        raise RuntimeError("Hostname ajeno a NETLAB360")
    if command("git", "-C", str(ROOT), "status", "--porcelain").strip():
        raise RuntimeError("Git tiene cambios locales sin revisar")

    print("========== S05 HA PRECHECK SOLO LECTURA ==========")
    print("S05_HA_PROPIETARIO=NETLAB360_S05")
    print("S05_HA_MODO=SOLO_LECTURA")

    addr = command("ip", "-j", "-4", "address", "show", "dev", "ens33")
    if "192.168.47.40" not in addresses(addr):
        raise RuntimeError("ens33 no coincide con la dirección de gestión")
    if "default via 192.168.47.2 dev ens33" not in command(
        "ip", "-4", "route", "show", "default"
    ):
        raise RuntimeError("Puerta de enlace administrativa no coincide")
    print("S05_HA_ENS33=192.168.47.40/24_INTACTA")

    if HA.exists() or HA.is_symlink():
        raise RuntimeError(f"Ya existe registro HA S05: {HA}; no recrear")

    wan = read_json(WAN, "NETLAB360_S02_WAN_LINKS_V1")
    lan = read_json(LAN, "NETLAB360_S02_LAN_8021Q_V1")
    declared_ns = set(lan.get("namespaces", []))
    actual_ns = {
        line.split()[0] for line in command("ip", "netns", "list", root=True).splitlines()
        if line.strip()
    }
    if not declared_ns.issubset(actual_ns) or len(declared_ns) != 12:
        raise RuntimeError("Los 12 namespaces S02 no coinciden con su estado")
    if any(row[-1] in actual_ns for row in CANDIDATES.values()):
        raise RuntimeError("Existe ya un namespace HA propuesto; no duplicar")
    print("S05_HA_S02_NAMESPACES=12_VERIFICADOS")
    print("S05_HA_NAMESPACES_NUEVOS=NINGUNO")

    routers = {}
    for site, name in ROUTERS.items():
        d = json.loads(command("docker", "inspect", name, root=True))[0]
        if (d.get("Id") != wan.get("ids", {}).get("R-" + site)
                or d.get("HostConfig", {}).get("NetworkMode") != "none"
                or not d.get("State", {}).get("Running")
                or (d.get("Config", {}).get("Labels") or {}).get(
                    "com.docker.compose.project") != "netlab360-s02-wan"):
            raise RuntimeError(f"Router FRR {site} no coincide con ownership esperado")
        routers[site] = str(d["State"]["Pid"])
    print("S05_HA_ROUTERS_PROTEGIDOS=HQ,S1,S2")

    planned = yaml.safe_load(IPAM.read_text(encoding="utf-8"))
    if planned.get("schema_version") != "0.2":
        raise RuntimeError("Versión IPAM no corresponde a S02")
    for site, (sw, vid) in SWITCHES.items():
        if sw not in actual_ns:
            raise RuntimeError(f"Switch S02 ausente: {sw}")
        command("ip", "-n", sw, "link", "show", "br0", root=True)
        vlan_out = command(
            "ip", "netns", "exec", sw, "bridge", "vlan", "show", root=True
        )
        if not re.search(rf"(?<!\d){vid}(?!\d)", vlan_out):
            raise RuntimeError(f"VLAN de servicios {site}/{vid} no observable")
        print(f"S05_HA_SWITCH_{site}=br0_VLAN_{vid}_VERIFICADO")

    observed = addresses(command("ip", "-j", "-4", "address", "show"))
    for ns in sorted(actual_ns):
        observed |= addresses(command("ip", "-n", ns, "-j", "-4", "address", "show", root=True))
    for site, pid in routers.items():
        observed |= addresses(command("nsenter", "-t", pid, "-n",
                                      "ip", "-j", "-4", "address", "show", root=True))

    for site, (ns, ip, gateway) in HOSTS.items():
        host_addresses = addresses(
            command("ip", "-n", ns, "-j", "-4", "address", "show", root=True)
        )
        if ip not in host_addresses:
            raise RuntimeError(f"Host S02 de VLAN de servicios alterado: {site}")
        route = command("ip", "-n", ns, "-4", "route", "show", "default", root=True)
        if f"default via {gateway}" not in route:
            raise RuntimeError(f"Gateway S02 de {site} alterado")
        print(f"S05_HA_HOST_SERVICIOS_{site}={ip}_OK")

    for role, (ip, site, vid, ns) in CANDIDATES.items():
        subnet = next(
            x["subnet"] for x in planned["sites"][site]["vlans"]
            if x["id"] == vid
        )
        if ipaddress.ip_address(ip) not in ipaddress.ip_network(subnet):
            raise RuntimeError(f"IP candidata fuera de VLAN {role}: {ip}")
        if ip in observed:
            raise RuntimeError(f"COLISION_IP_OBSERVADA={role}:{ip}")
        print(f"S05_HA_IP_CANDIDATA_{role}={ip}_SIN_ASIGNACION_OBSERVADA")
        print(f"S05_HA_NS_PROPUESTO_{role}={ns}")

    api_state()
    print("S05_HA_IPAM_LIMITACION=INSPECCION_NO_EQUIVALE_A_RESERVA_EXCLUSIVA")
    print("S05_HA_FRONTAL_LIMITACION=PUNTO_UNICO_DE_FALLA_POTENCIAL")
    print("S05_HA_CAMBIOS_INFRAESTRUCTURA=NINGUNO")
    print("S05_HA_PRECHECK=OK_DISENO_PENDIENTE")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"S05_HA_PRECHECK_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr)
        sys.exit(2)
