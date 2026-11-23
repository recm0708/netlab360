#!/usr/bin/env python3
"""S06-036: verificar programacion independiente de un futuro rollback.

La unica accion activa permitida crea un temporizador systemd transitorio
que genera un archivo marcador, NUNCA toca interfaces ni qdisc.
No implementa ni autoriza aun una degradacion o restauracion real.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time

BASE = Path.home() / "netlab360-bootstrap/s06"
REPO = Path(__file__).resolve().parents[2]
NS = "nl360-s02-h-hq-120"
DEVICE = "eth0"
MANAGEMENT = "192.168.47.40/24"
GATEWAY = "192.168.47.2"
BASELINE_QDISC = "noqueue"
UNIT_PATTERN = re.compile(r"^netlab360-s06-wd-probe-[0-9a-f]{8}$")


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run(args: list[str], *, timeout: float = 12) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=False, text=True,
                          capture_output=True, timeout=timeout)


def get_output(args: list[str]) -> str:
    result = run(args)
    if result.returncode:
        raise RuntimeError(
            f"Comando de consulta no disponible: {args[:3]} "
            f"rc={result.returncode}: {result.stderr[-250:]}"
        )
    return result.stdout


def classify_qdisc(data: object) -> str:
    if not isinstance(data, list):
        raise ValueError("La consulta qdisc no produjo una lista JSON")
    entries = [x for x in data if isinstance(x, dict)]
    if any(x.get("kind") == "netem" for x in entries):
        return "BLOCKED_NETEM_PRESENT"
    roots = [
        x for x in entries
        if x.get("root") is True or x.get("parent") == "root"
    ]
    if len(roots) != 1 or roots[0].get("kind") != BASELINE_QDISC:
        return "BLOCKED_QDISC_NOT_NOQUEUE"
    return "CANDIDATE_NOQUEUE"


def check_read_only() -> dict:
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal, no como root")
    current = get_output(["git", "-C", str(REPO), "status", "--porcelain"])
    if current.strip():
        raise RuntimeError("Git con cambios locales")
    ip = get_output(["ip", "-4", "-o", "addr", "show", "dev", "ens33"])
    route = get_output(["ip", "-4", "route", "show", "default"])
    if MANAGEMENT not in ip or f"default via {GATEWAY} dev ens33" not in route:
        raise RuntimeError("Red administrativa fuera de referencia")
    namespaces = {
        line.split()[0] for line in get_output(
            ["sudo", "-n", "ip", "netns", "list"]
        ).splitlines() if line.strip()
    }
    if len(namespaces) != 21 or NS not in namespaces:
        raise RuntimeError("Namespace candidato o inventario inesperados")
    addr = json.loads(get_output(
        ["sudo", "-n", "ip", "-n", NS, "-j", "addr", "show", "dev", DEVICE]
    ))
    if len(addr) != 1 or addr[0].get("ifname") != DEVICE:
        raise RuntimeError("Interfaz experimental inesperada")
    info = [x for x in addr[0].get("addr_info", [])
            if x.get("family") == "inet"]
    if len(info) != 1 or info[0].get("local") != "10.70.20.20" or info[0].get("prefixlen") != 24:
        raise RuntimeError("Direccion IP experimental alterada")
    routes = json.loads(get_output(
        ["sudo", "-n", "ip", "-n", NS, "-j", "route", "show", "default"]
    ))
    if (len(routes) != 1 or routes[0].get("gateway") != "10.70.20.1"
            or routes[0].get("dev") != DEVICE):
        raise RuntimeError("Ruta experimental fuera de referencia")
    raw = json.loads(get_output(
        ["sudo", "-n", "ip", "netns", "exec", NS,
         "tc", "-j", "qdisc", "show", "dev", DEVICE]
    ))
    state = classify_qdisc(raw)
    if state != "CANDIDATE_NOQUEUE":
        raise RuntimeError(f"qdisc no autorizada para planificacion: {state}")
    return {
        "target": {"namespace": NS, "device": DEVICE,
                   "ip": "10.70.20.20/24"},
        "qdisc_state": state,
        "management_protected": True,
        "namespace_count": 21,
        "observed_utc": utc(),
        "actions_on_network": "NONE",
    }


def validate_marker_path(path: Path) -> None:
    # Validacion antes de construir la accion temporal root.
    allowed = (BASE / "watchdog-tests").resolve()
    if path.parent.resolve() != allowed:
        raise ValueError("Marcador fuera de ubicacion autorizada")
    if not re.fullmatch(r"^wd_[0-9a-f]{8}\.ready$", path.name):
        raise ValueError("Nombre del marcador invalido")
    if path.is_symlink() or path.exists():
        raise ValueError("Marcador preexistente o symlink")


def build_timer_args(unit: str, marker: Path) -> list[str]:
    if not UNIT_PATTERN.fullmatch(unit):
        raise ValueError("Nombre de unidad no permitido")
    validate_marker_path(marker)
    return [
        "sudo", "-n", "systemd-run",
        "--unit=" + unit,
        "--collect",
        "--on-active=3s",
        "--timer-property=AccuracySec=1s",
        "/usr/bin/touch", str(marker)
    ]


def write_report(folder: Path, result: dict) -> None:
    output = folder / "S06_036_Resultado_Watchdog.json"
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check-only", action="store_true")
    group.add_argument("--test-timer", action="store_true")
    args = parser.parse_args()

    os.umask(0o077)
    record = check_read_only()
    print("S06_036_PRECHECK=OK")
    print("S06_036_QDISC=" + record["qdisc_state"])
    if args.check_only:
        print("S06_036_MODO=SOLO_LECTURA")
        print("S06_036_CAMBIOS_RED=NINGUNO")
        return

    folder = BASE / "watchdog-tests"
    folder.mkdir(parents=True, mode=0o700, exist_ok=True)
    if folder.is_symlink() or (folder.stat().st_mode & 0o777) != 0o700:
        raise RuntimeError("Directorio marcador no es privado")
    token = secrets.token_hex(4)
    marker = folder / ("wd_" + token + ".ready")
    unit = "netlab360-s06-wd-probe-" + token
    args_timer = build_timer_args(unit, marker)
    record.update({
        "schema": "NETLAB360_S06_WATCHDOG_PROBE_V1",
        "timer_unit": unit,
        "marker": str(marker),
        "operation": "systemd_transient_marker_only",
        "qdisc_mutation_allowed": False,
        "network_change_executed": False,
        "timer_fired": False,
    })
    response = run(args_timer, timeout=12)
    if response.returncode:
        raise RuntimeError(
            f"No fue posible programar temporizador de prueba: "
            f"{response.stderr[-350:]}"
        )
    print("S06_036_TIMER_PROGRAMADO=SI")
    print("S06_036_TIMER_UNIDAD=" + unit)
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if marker.is_file() and not marker.is_symlink():
            record["timer_fired"] = True
            break
        time.sleep(0.5)

    record["completed_utc"] = utc()
    # Guardar siempre resultado, aun cuando systemd no haya ejecutado el marcador.
    report = folder / ("S06_036_" + token)
    report.mkdir(mode=0o700)
    write_report(report, record)
    print("S06_036_REPORTE=" + str(report / "S06_036_Resultado_Watchdog.json"))
    print("S06_036_MARCADOR=" + str(marker))
    if not record["timer_fired"]:
        raise RuntimeError("Temporizador no disparo marcador dentro de ventana")
    check_read_only()
    print("S06_036_TIMER_INDEPENDIENTE=VERIFICADO")
    print("S06_036_CAMBIOS_RED=NINGUNO")
    print("S06_036_GATE=PREPARACION_NO_AUTORIZA_NETEM")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"S06_036_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
