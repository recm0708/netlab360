#!/usr/bin/python3
"""NETLAB360: snapshot de 3 contenedores FRR y FIB HQ, solo lectura.

Uso único autorizado por sudoers: /usr/local/libexec/netlab360-observer snapshot
NO permite elegir nombres, destinos, comandos ni directorios. Este archivo debe
instalarse root:root 0755 en /usr/local/libexec, jamás ejecutarse desde Git como root.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
import os
import shutil
from pathlib import Path
import subprocess
import sys

STATE = Path("/home/rc-aa-ec/netlab360-bootstrap/s02/wan-links-state.json")
PROJECT = "netlab360-s02-wan"
NAMES = {
    "R-HQ": "nl360-s02-r-hq",
    "R-S1": "nl360-s02-r-s1",
    "R-S2": "nl360-s02-r-s2",
}
TARGETS = {"S1": "10.79.0.2", "S2": "10.79.0.3"}
ROUTE_DEVS = {"S1": {"s1p": "10.78.0.2", "s1b": "10.78.0.6"},
              "S2": {"s2p": "10.78.0.10", "s2b": "10.78.0.14"}}



# Solo nombres y comandos constantes. El sudoers existente permite UNICAMENTE
# ejecutar este binario root:root con argumento "snapshot".
LACP_STATES = Path("/home/rc-aa-ec/netlab360-bootstrap/s05/lacp-multisede")
SDN_STATE = Path("/home/rc-aa-ec/netlab360-bootstrap/s05/sdn-faucet/state-sdn.json")
SDN_OWNER = "NETLAB360_S05_SDN_V1"
SDN_BRIDGE = "br-s05-sdn"
SDN_PORTS = {"sdna0", "sdnb0", "sdnc0"}
LACP_SITES = {
    "HQ": ("nl360-s02-sw-hq", "nl360-s05-lacp-hq"),
    "S1": ("nl360-s02-sw-s1", "nl360-s05-lacp-s1"),
    "S2": ("nl360-s02-sw-s2", "nl360-s05-lacp-s2"),
}


def optional_read(*argv: str, timeout: float = 2.0) -> str:
    """Consulta privilegiada de destino fijo; nunca invoca shell ni escribe."""
    p = subprocess.run(list(argv), capture_output=True, text=True,
                       timeout=timeout, check=False,
                       env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})
    if p.returncode:
        raise RuntimeError("Sondeo read-only no disponible")
    return p.stdout


def safe_json(path: Path, owner: str) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise RuntimeError("Archivo de propietario no disponible")
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or obj.get("owner") != owner:
        raise RuntimeError("Owner no coincide")
    return obj


def observed_bond(namespace: str, device: str, alias: str) -> dict:
    raw = json.loads(optional_read(
        "/usr/sbin/ip", "-n", namespace, "-j", "-d",
        "link", "show", "dev", device))
    if not isinstance(raw, list) or len(raw) != 1:
        raise RuntimeError("Ambigüedad de dispositivo")
    row = raw[0]
    info = row.get("linkinfo") or {}
    data = info.get("info_data") or {}
    ports = data.get("ad_num_ports")
    if (str(row.get("ifname", "")).split("@", 1)[0] != device
            or row.get("ifalias") != alias
            or info.get("info_kind") != "bond"
            or str(data.get("mode")) != "802.3ad"
            or isinstance(ports, bool) or not isinstance(ports, int)
            or not 0 <= ports <= 2):
        raise RuntimeError("Bond o datos 802.3ad no acreditados")
    return {
        "active_members": ports,
        "link_up": "UP" in row.get("flags", [])
                   and "LOWER_UP" in row.get("flags", []),
    }


def lacp_observation() -> dict:
    """Cada sede es UNKNOWN si faltan permisos, propiedad o sondeo real."""
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sites = {}
    for site, (switch, client) in LACP_SITES.items():
        unknown = {"status": "unknown", "switch_members": None,
                   "client_members": None, "source": "iproute2 -j -d Linux bond"}
        try:
            state = safe_json(LACP_STATES / ("state-" + site.lower() + ".json"),
                              "NETLAB360_S05_LACP_" + site + "_V1")
            alias = state.get("alias")
            if (state.get("status") != "active" or state.get("site") != site
                    or state.get("sw") != switch or state.get("client") != client
                    or not isinstance(alias, str)
                    or re.fullmatch(r"S05_" + site + r"_[0-9a-f]{16}", alias) is None):
                raise RuntimeError("Estado LACP no confiable")
            a = observed_bond(switch, "s5bond0", alias)
            b = observed_bond(client, "bond0", alias)
            if not a["link_up"] or not b["link_up"] or min(
                    a["active_members"], b["active_members"]) == 0:
                status = "down"
            elif a["active_members"] == 2 and b["active_members"] == 2:
                status = "up"
            else:
                status = "degraded"
            sites[site] = {"status": status,
                           "switch_members": a["active_members"],
                           "client_members": b["active_members"],
                           "source": unknown["source"]}
        except (OSError, RuntimeError, ValueError, KeyError, TypeError,
                subprocess.TimeoutExpired):
            sites[site] = unknown
    return {
        "owner": "NETLAB360_S05_LACP_OBSERVATION_V1",
        "observed_at_utc": stamp,
        "available": all(v["status"] != "unknown" for v in sites.values()),
        "sites": sites,
    }


def sdn_observation() -> dict:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    unknown = {"owner": "NETLAB360_S05_SDN_OBSERVATION_V1",
               "observed_at_utc": stamp, "available": False,
               "status": "unknown", "connected": None,
               "flow_count": None, "source": "OVS OpenFlow13 / Docker"}
    try:
        state = safe_json(SDN_STATE, SDN_OWNER)
        if state.get("status") != "active" or state.get("bridge") != SDN_BRIDGE:
            raise RuntimeError("Estado SDN no coincide")
        owner = optional_read("/usr/bin/ovs-vsctl", "--timeout=3",
                              "get", "Bridge", SDN_BRIDGE,
                              "external_ids:netlab360-owner").strip().strip('"')
        if owner != SDN_OWNER:
            raise RuntimeError("Bridge OVS no pertenece a S05")
        ports = set(optional_read("/usr/bin/ovs-vsctl", "--timeout=3",
                                  "list-ports", SDN_BRIDGE).splitlines())
        if ports != SDN_PORTS:
            raise RuntimeError("Puertos OVS ajenos o ausentes")
        container = json.loads(optional_read(
            "/usr/bin/docker", "inspect", "nl360-s05-faucet"))
        if (not isinstance(container, list) or len(container) != 1
                or container[0].get("Name") != "/nl360-s05-faucet"
                or (container[0].get("Config", {}).get("Labels") or {}).get(
                    "netlab360.owner") != SDN_OWNER):
            raise RuntimeError("Identidad de Faucet no comprobada")
        running = container[0].get("State", {}).get("Running") is True
        connection = optional_read(
            "/usr/bin/ovs-vsctl", "--timeout=3", "--format=csv",
            "--data=bare", "--no-heading", "--columns=is_connected",
            "list", "Controller").strip().lower()
        if connection not in ("true", "false"):
            raise RuntimeError("Controlador OVS ambiguo")
        connected = connection == "true" and running
        if connected:
            flow = optional_read(
                "/usr/bin/ovs-ofctl", "-O", "OpenFlow13",
                "dump-flows", SDN_BRIDGE, timeout=2.0)
            count = sum("actions=" in line and "cookie=" in line
                        for line in flow.splitlines())
            if count < 1:
                raise RuntimeError("No hay flujos OpenFlow acreditados")
        else:
            count = None
        return {**unknown, "available": True,
                "status": "connected" if connected else "disconnected",
                "connected": connected, "flow_count": count}
    except (OSError, RuntimeError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired):
        return unknown




def run(*argv: str) -> str:
    p = subprocess.run(list(argv), capture_output=True, text=True,
                       timeout=5, check=False, env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})
    if p.returncode:
        raise RuntimeError(f"Consulta fallida ({argv[0]}): exit={p.returncode}")
    return p.stdout


def ensure_state() -> dict:
    if STATE.is_symlink() or not STATE.is_file():
        raise RuntimeError("WAN state no es un archivo regular")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("owner") != "NETLAB360_S02_WAN_LINKS_V1":
        raise RuntimeError("Owner WAN no reconocido")
    ids = state.get("ids")
    if not isinstance(ids, dict) or set(ids) != set(NAMES):
        raise RuntimeError("IDs WAN diferentes del inventario")
    if any(not isinstance(ids[key], str) or len(ids[key]) != 64 for key in NAMES):
        raise RuntimeError("IDs de contenedor inválidos")
    return ids


def inspect(name: str, expected_id: str) -> dict:
    rows = json.loads(run("/usr/bin/docker", "inspect", name))
    if not isinstance(rows, list) or len(rows) != 1:
        raise RuntimeError("Docker inspección ambigua")
    d = rows[0]
    if (d.get("Id") != expected_id or
            d.get("Name", "").lstrip("/") != name or
            d.get("HostConfig", {}).get("NetworkMode") != "none" or
            (d.get("Config", {}).get("Labels") or {}).get(
                "com.docker.compose.project") != PROJECT):
        raise RuntimeError("Contenedor no pertenece a S02")
    running = d.get("State", {}).get("Running") is True
    pid = d.get("State", {}).get("Pid", 0)
    if running and (not isinstance(pid, int) or pid <= 1):
        raise RuntimeError("PID de contenedor inválido")
    return {"id": expected_id, "running": running, "pid": pid if running else None}


def interfaces(pid: int) -> dict:
    raw = json.loads(run("/usr/bin/nsenter", "-t", str(pid), "-n",
                         shutil.which("ip", path="/usr/sbin:/usr/bin:/sbin:/bin") or "/usr/sbin/ip", "-j", "link", "show"))
    if not isinstance(raw, list):
        raise RuntimeError("ip -j link no devolvió lista")
    return {str(x["ifname"]).split("@", 1)[0]:
            {"flags": x.get("flags", [])} for x in raw if isinstance(x, dict)
            and isinstance(x.get("ifname"), str)}


def fib(pid: int, site: str, target: str) -> dict | None:
    # Una ruta ausente es información no observada, no un motivo para inventarla.
    try:
        raw = json.loads(run("/usr/bin/nsenter", "-t", str(pid), "-n",
                             shutil.which("ip", path="/usr/sbin:/usr/bin:/sbin:/bin") or "/usr/sbin/ip", "-j", "-4", "route", "get", target))
        if not isinstance(raw, list) or len(raw) != 1:
            return None
        dev = raw[0].get("dev")
        gateway = raw[0].get("gateway")
        if dev not in ROUTE_DEVS[site] or gateway != ROUTE_DEVS[site][dev]:
            return None
        return {"dev": dev, "gateway": gateway, "target": target,
                "origin": "Linux FIB R-HQ"}
    except (ValueError, KeyError, RuntimeError):
        return None


def snapshot() -> dict:
    if os.geteuid() != 0:
        raise RuntimeError("Este ejecutable requiere root mediante sudoers acotado")
    if os.uname().nodename != "netlab360-lab":
        raise RuntimeError("Máquina no autorizada")
    ids = ensure_state()
    result = {"project": "NETLAB360", "owner": "NETLAB360_S02_WAN_LINKS_V1",
              "routers": {}, "routes": {}}
    for logical, cname in NAMES.items():
        d = inspect(cname, ids[logical])
        d["links"] = interfaces(d["pid"]) if d["running"] else {}
        result["routers"][logical] = d
    hq = result["routers"]["R-HQ"]
    if hq["running"]:
        for site, target in TARGETS.items():
            route = fib(hq["pid"], site, target)
            if route is not None:
                result["routes"][site] = route
    # Las observaciones opcionales nunca pueden invalidar el contrato FRR/FIB.
    try:
        result["lacp"] = lacp_observation()
    except Exception:
        result["lacp"] = {"owner": "NETLAB360_S05_LACP_OBSERVATION_V1",
                          "observed_at_utc": None, "available": False,
                          "sites": {}}
    try:
        result["sdn"] = sdn_observation()
    except Exception:
        result["sdn"] = {"owner": "NETLAB360_S05_SDN_OBSERVATION_V1",
                         "observed_at_utc": None, "available": False,
                         "status": "unknown", "connected": None,
                         "flow_count": None}
    return result


def main() -> int:
    if sys.argv != [sys.argv[0], "snapshot"]:
        print("Uso exclusivo: netlab360-observer snapshot", file=sys.stderr)
        return 2
    try:
        print(json.dumps(snapshot(), ensure_ascii=False, sort_keys=True))
        return 0
    except (RuntimeError, ValueError, OSError, KeyError,
            subprocess.TimeoutExpired) as exc:
        print(f"S05_PRIV_OBSERVER_ERROR={str(exc)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
