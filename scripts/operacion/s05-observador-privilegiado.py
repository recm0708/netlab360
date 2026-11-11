#!/usr/bin/python3
"""NETLAB360: snapshot de 3 contenedores FRR y FIB HQ, solo lectura.

Uso único autorizado por sudoers: /usr/local/libexec/netlab360-observer snapshot
NO permite elegir nombres, destinos, comandos ni directorios. Este archivo debe
instalarse root:root 0755 en /usr/local/libexec, jamás ejecutarse desde Git como root.
"""
from __future__ import annotations

import json
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
