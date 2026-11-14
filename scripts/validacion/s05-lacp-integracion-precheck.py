#!/usr/bin/env python3
"""NETLAB360 S05: plan/precheck de LACP multisede, sin cambios de configuración.

SOLO permite plan y precheck. No crea, reinicia o elimina recursos.
Los sondeos ICMP solo consultan la red y pueden actualizar cachés ARP.
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
import time
from urllib.request import urlopen

import yaml

ROOT = Path(__file__).resolve().parents[2]
STATE = Path.home() / "netlab360-bootstrap/s05/lacp-multisede/state.json"
IPAM = ROOT / "inventario/ipam/topologia-s02.yaml"
SITES = {
    "HQ": {
        "sw": "nl360-s02-sw-hq", "host": "nl360-s02-h-hq-120",
        "vlan": 120, "ip": "10.70.20.40", "gateway": "10.70.20.1",
        "access": ("a110", "a120", "a130", "ha-hq21", "ha-hq23"),
        "new_ns": "nl360-s05-lacp-hq",
    },
    "S1": {
        "sw": "nl360-s02-sw-s1", "host": "nl360-s02-h-s1-220",
        "vlan": 220, "ip": "10.71.20.40", "gateway": "10.71.20.1",
        "access": ("a210", "a220", "a230", "ha-s121"),
        "new_ns": "nl360-s05-lacp-s1",
    },
    "S2": {
        "sw": "nl360-s02-sw-s2", "host": "nl360-s02-h-s2-320",
        "vlan": 320, "ip": "10.72.20.40", "gateway": "10.72.20.1",
        "access": ("a310", "a320", "a330"),
        "new_ns": "nl360-s05-lacp-s2",
    },
}
PROTECTED = ("ens33", "tr-sw", "br0", "ha-hq21", "ha-hq23", "ha-s121")
NEW_NAMES = ("s5bond0", "s5p1", "s5p2")
SERVICES = (
    "netlab360-s04-exporter",
    "netlab360-s05-noc",
    "netlab360-s05-ha-backend-hq",
    "netlab360-s05-ha-backend-s1",
    "netlab360-s05-ha-frontal-hq",
    "netlab360-s05-ha-monitor-s2",
)


def run(*argv: str, timeout: int = 15, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Comando rechazado ({result.returncode}): {' '.join(argv)} / "
            + (result.stderr or result.stdout)[-600:]
        )
    return result


def privileged(*argv: str, **kwargs) -> subprocess.CompletedProcess:
    return run("sudo", "-n", *argv, **kwargs)


def read_bridge_vlans(ns: str, *, attempts: int = 2, timeout: int = 30) -> str:
    """Consulta read-only con espera acotada; nunca omite validación VLAN."""
    if attempts < 1 or attempts > 3 or timeout < 16 or timeout > 60:
        raise ValueError("Parámetros de diagnóstico fuera de rango")
    last = None
    for i in range(1, attempts + 1):
        try:
            result = privileged("ip", "netns", "exec", ns,
                                "bridge", "vlan", "show", timeout=timeout)
            print(f"S05_LACP_VLAN_LECTURA_{ns}=OK_INTENTO_{i}")
            return result.stdout
        except subprocess.TimeoutExpired as exc:
            last = exc
            print(f"S05_LACP_VLAN_LECTURA_{ns}=TIMEOUT_INTENTO_{i}", flush=True)
            if i < attempts:
                time.sleep(1)
    raise RuntimeError(f"Consulta VLAN no validada para {ns} tras {attempts} intentos") from last


def inventory(selected: list[str] | None = None) -> None:
    selected = selected or list(SITES)
    if len(set(selected)) != len(selected) or any(site not in SITES for site in selected):
        raise ValueError("Selección de sedes repetida o desconocida")
    data = yaml.safe_load(IPAM.read_text(encoding="utf-8"))
    if data.get("schema_version") != "0.2" or set(data["sites"]) != set(SITES):
        raise ValueError("Topología S02 distinta de la esperada")
    mgmt = data["management_host"]
    if (str(mgmt["host_ip"]) != "192.168.47.40"
            or str(mgmt["gateway"]) != "192.168.47.2"
            or mgmt["interface"] != "ens33" or mgmt["locked"] is not True):
        raise ValueError("IPAM de gestión inesperado")
    seen = set()
    for site in selected:
        row = SITES[site]
        vlans = [v for v in data["sites"][site]["vlans"] if v["id"] == row["vlan"]]
        if len(vlans) != 1:
            raise ValueError(f"VLAN de servicios sin identidad única: {site}")
        segment = ipaddress.ip_network(vlans[0]["subnet"])
        proposed = ipaddress.ip_address(row["ip"])
        gateway = ipaddress.ip_address(row["gateway"])
        if proposed not in segment or gateway != ipaddress.ip_address(vlans[0]["gateway"]):
            raise ValueError(f"IP fuera del prefijo esperado: {site}")
        if proposed == gateway or proposed in seen:
            raise ValueError(f"IP repetida: {proposed}")
        seen.add(proposed)
        print(f"S05_LACP_PLAN_{site}=VLAN{row['vlan']} IP_CANDIDATA={proposed} SIN_ASIGNAR")
    if set(selected) == set(SITES):
        print("S05_LACP_PLAN=3_SEDES_3_BONDS_CANDIDATOS_NO_DESPLEGADOS")
    else:
        print("S05_LACP_PLAN_SEDES_SOLICITADAS=" + ",".join(selected))
        print("S05_LACP_PLAN=ALCANCE_SELECTIVO_SIN_VERIFICAR_OTRAS_SEDES")


def parse_vlan_map(source: str) -> dict[str, set[int]]:
    """Interpreta salida tabular bridge vlan show, con VLAN continuadas."""
    ports: dict[str, set[int]] = {}
    current: str | None = None
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("port "):
            continue
        fields = line.split()
        if fields[0].isdecimal() and current is not None:
            vlan = int(fields[0])
        elif len(fields) > 1 and fields[1].isdecimal():
            current = fields[0]
            vlan = int(fields[1])
        else:
            continue
        ports.setdefault(current, set()).add(vlan)
    return ports


def ip_set(source: str) -> set[str]:
    addresses = set()
    for item in json.loads(source):
        for addr in item.get("addr_info", []):
            if addr.get("family") == "inet" and addr.get("local"):
                addresses.add(str(addr["local"]))
    return addresses


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "precheck"))
    parser.add_argument("--sites", nargs="+", choices=tuple(SITES),
                        default=list(SITES),
                        help="Solo revisar estas sedes (por ejemplo, --sites S1 S2)")
    args = parser.parse_args()
    selected = list(args.sites)
    if len(set(selected)) != len(selected):
        parser.error("--sites no admite sedes duplicadas")
    inventory(selected)
    if args.action == "plan":
        print("S05_LACP_PLAN_SOLO_LECTURA=OK")
        return
    if os.geteuid() == 0:
        raise RuntimeError("No ejecutar como root: usar usuario normal y sudo -v")
    if run("hostname").stdout.strip() != "netlab360-lab":
        raise RuntimeError("Hostname no corresponde a NETLAB360")
    if run("git", "-C", str(ROOT), "status", "--porcelain").stdout.strip():
        raise RuntimeError("Git tiene cambios locales")
    if STATE.exists() or STATE.is_symlink():
        raise RuntimeError("Ya hay estado LACP multisede; revisar su propiedad sin sobrescribir")
    addr = run("ip", "-4", "-o", "address", "show", "dev", "ens33").stdout
    route = run("ip", "-4", "route", "show", "default").stdout
    if "192.168.47.40/24" not in addr or "default via 192.168.47.2 dev ens33" not in route:
        raise RuntimeError("Red de gestión distinta de baseline")
    if run("modinfo", "bonding", check=False).returncode:
        raise RuntimeError("Módulo bonding no disponible")
    print("S05_LACP_GESTION_PROTEGIDA=SI")

    names = {line.split()[0] for line in privileged("ip", "netns", "list").stdout.splitlines() if line.strip()}
    candidates = {SITES[site]["ip"] for site in selected}
    if any(SITES[site]["new_ns"] in names for site in selected):
        raise RuntimeError("Namespace nuevo ya ocupado; no reutilizar recursos")
    all_ips = ip_set(run("ip", "-j", "-4", "address", "show").stdout)
    for ns in sorted(names):
        all_ips |= ip_set(privileged("ip", "netns", "exec", ns,
                                   "ip", "-j", "-4", "address", "show").stdout)
    for r in ("nl360-s02-r-hq", "nl360-s02-r-s1", "nl360-s02-r-s2"):
        identity = privileged("docker", "inspect", "--format",
                              "{{.State.Running}} {{.HostConfig.NetworkMode}} {{.State.Pid}}",
                              r).stdout.strip().split()
        if len(identity) != 3 or identity[:2] != ["true", "none"]:
            raise RuntimeError(f"Router FRR inesperado: {r}={identity}")
        pid = identity[2]
        if not pid.isdecimal() or int(pid) <= 1:
            raise RuntimeError(f"PID del router inválido: {r}")
        all_ips |= ip_set(privileged("nsenter", "-t", pid, "-n",
                                     "ip", "-j", "-4", "address", "show").stdout)
        print(f"S05_LACP_FRR_{r}=RUNNING_NONE")
    collisions = candidates & all_ips
    if collisions:
        raise RuntimeError("IP candidata ya observada en inventario: " + ",".join(sorted(collisions)))
    print(f"S05_LACP_IPS_INVENTARIO_AUDITADO={len(all_ips)}_DIRECCIONES_DISTINTAS")

    for site in selected:
        row = SITES[site]
        sw = row["sw"]
        if sw not in names or row["host"] not in names:
            raise RuntimeError(f"Switch o host de VLAN ausente: {site}")
        devs = json.loads(privileged("ip", "netns", "exec", sw, "ip", "-j", "-d",
                                     "link", "show").stdout)
        devnames = {d["ifname"] for d in devs}
        needed = {"br0", "tr-sw", *row["access"]}
        if not needed.issubset(devnames):
            raise RuntimeError(f"Puertos anteriores faltantes en {site}: {needed-devnames}")
        if any(name in devnames for name in NEW_NAMES):
            raise RuntimeError(f"Interfaz candidata ocupada en switch {site}")
        bridge = next(d for d in devs if d["ifname"] == "br0")
        if bridge.get("linkinfo", {}).get("info_kind") != "bridge":
            raise RuntimeError(f"br0 no es bridge Linux en {site}")
        vlan_text = read_bridge_vlans(sw)
        vlans = parse_vlan_map(vlan_text)
        if row["vlan"] not in vlans.get("tr-sw", set()):
            raise RuntimeError(f"Troncal no incluye VLAN {site}")
        for iface in row["access"]:
            if iface.startswith("a") and iface[1:].isdecimal():
                expected = int(iface[1:])
            else:
                expected = row["vlan"]
            if expected not in vlans.get(iface, set()):
                raise RuntimeError(f"VLAN anterior distinta en {site}/{iface}")
        # ICMP de un host en la misma VLAN; fallo no prueba ausencia absoluta.
        response = privileged("ip", "netns", "exec", row["host"], "ping",
                               "-n", "-c", "1", "-W", "1", row["ip"], check=False, timeout=6)
        if response.returncode == 0:
            raise RuntimeError(f"IP candidata RESPONDE al ping en {site}: {row['ip']}")
        print(f"S05_LACP_{site}_SW_VLAN_PROTEGIDOS=OK")
        print(f"S05_LACP_{site}_IP_CANDIDATA={row['ip']}_NO_ASIGNADA_Y_SIN_RESPUESTA_ICMP")

    for unit in SERVICES:
        if run("systemctl", "is-active", unit, check=False).stdout.strip() != "active":
            raise RuntimeError(f"Servicio no activo: {unit}")
    try:
        with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=8) as response:
            data = json.load(response)
        if not data.get("ha_service", {}).get("available"):
            raise RuntimeError("NOC no observa HA con datos válidos")
    except Exception as error:
        raise RuntimeError("NOC API no disponible") from error
    print("S05_LACP_NOC_HTTP_HA=OK")
    print("S05_LACP_ADVERTENCIA=PING_SIN_RESPUESTA_NO_DEMUESTRA_IP_LIBRE_EN_TODA_LA_RED")
    print("S05_LACP_PRECHECK_SEDES=" + ",".join(selected))
    print("S05_LACP_PRECHECK=OK_SIN_CAMBIOS_DE_CONFIGURACION")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as exc:
        print(f"S05_LACP_PRECHECK_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
