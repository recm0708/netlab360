#!/usr/bin/env python3
"""Precheck de solo lectura: servicios HTTP HA S05; no instala ni inicia nada."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from urllib.request import urlopen

HOME = Path.home()
REPO = HOME / "proyectos/netlab360"
STATE = HOME / "netlab360-bootstrap/s05/ha/state.json"
EXPECTED = (
    ("BACKEND_HQ", "nl360-s05-ha-hq", "10.70.20.21/24", 8088),
    ("BACKEND_S1", "nl360-s05-ha-s1", "10.71.20.21/24", 8088),
    ("FRONTAL_HQ", "nl360-s05-ha-fe", "10.70.20.23/24", 8080),
)
UNITS = (
    "netlab360-s05-ha-backend-hq.service",
    "netlab360-s05-ha-backend-s1.service",
    "netlab360-s05-ha-frontal-hq.service",
)


def run(*cmd: str, root: bool = False) -> str:
    full = (["sudo", "-n"] if root else []) + list(cmd)
    r = subprocess.run(full, text=True, capture_output=True, timeout=15)
    if r.returncode:
        raise RuntimeError("Consulta fallida: " + " ".join(cmd) + " " +
                           r.stderr[-300:])
    return r.stdout


def main() -> None:
    if sys.argv != [sys.argv[0], "--check"]:
        raise RuntimeError("Uso: --check, sin otras acciones")
    if run("hostname").strip() != "netlab360-lab":
        raise RuntimeError("VM inesperada")
    if run("git", "-C", str(REPO), "status", "--porcelain").strip():
        raise RuntimeError("Git no está limpio")
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if (data.get("owner") != "NETLAB360_S05_HA_RED_V1" or
            data.get("status") != "active" or
            set(data.get("namespaces", [])) != {n for _, n, _, _ in EXPECTED}):
        raise RuntimeError("Red S05 HA no está validada")
    print("S05_HTTP_RED_HA=ACTIVA", flush=True)

    management = run("ip", "-4", "-br", "address", "show", "ens33")
    default = run("ip", "-4", "route", "show", "default")
    if "192.168.47.40/24" not in management or \
            "default via 192.168.47.2 dev ens33" not in default:
        raise RuntimeError("Red administrativa inesperada")
    print("S05_HTTP_GESTION=INTACTA")

    namespaces = {x.split()[0] for x in run("ip", "netns", "list", root=True).splitlines()}
    for role, ns, address, port in EXPECTED:
        if ns not in namespaces:
            raise RuntimeError("Namespace ausente: " + ns)
        addr = run("ip", "-n", ns, "-4", "-br", "address", "show", "eth0", root=True)
        if address not in addr:
            raise RuntimeError("Dirección no coincide en " + ns)
        listeners = run("ip", "netns", "exec", ns, "ss", "-H", "-lnt", root=True)
        # No permitimos listener preexistente en los puertos de HA.
        if any(x.split()[3].rsplit(":", 1)[-1] == str(port)
               for x in listeners.splitlines() if len(x.split()) > 3):
            raise RuntimeError(f"Puerto {port} ocupado en {ns}")
        print(f"S05_HTTP_NS_{role}={ns} IP={address} PUERTO_{port}=LIBRE")

    for unit in UNITS:
        destination = Path("/etc/systemd/system") / unit
        if destination.exists() or destination.is_symlink():
            raise RuntimeError("Unidad preexistente: " + unit)
        if not (REPO / "servicios/systemd" / unit).is_file():
            raise RuntimeError("Unidad no está en Git: " + unit)
    print("S05_HTTP_UNITS_DESTINO=LIBRES")

    for unit in ("netlab360-s04-exporter", "netlab360-s05-noc"):
        if run("systemctl", "is-active", unit).strip() != "active":
            raise RuntimeError("Observador detenido: " + unit)
    with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=5) as r:
        noc = json.load(r)
    routes = noc.get("routing", {}).get("routes") or {}
    if (noc.get("telemetry", {}).get("available") is not True or
            noc.get("routing", {}).get("available") is not True or
            routes.get("S1", {}).get("dev") != "s1p" or
            routes.get("S2", {}).get("dev") != "s2p"):
        raise RuntimeError("Fuente NOC/FIB no confiable")
    print("S05_HTTP_FIB=S1:s1p,S2:s2p")
    print("S05_HTTP_INSTANCIAS=NO_DESPLEGADAS")
    print("S05_HTTP_PRECHECK=OK_SIN_CAMBIOS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"S05_HTTP_PRECHECK_ERROR={type(exc).__name__}:{exc}", file=sys.stderr)
        sys.exit(2)
