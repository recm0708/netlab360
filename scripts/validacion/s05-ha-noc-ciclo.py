#!/usr/bin/env python3
"""Validación de aplicación HA *desde el NOC* sin tocar FRR ni enlaces WAN.

La única perturbación es detener y restaurar la unit backend HTTP HQ de S05.
Se muestrea /api/v1/graph en 127.0.0.1:9130, conservando JSONL.
Una prueba positiva exige HQ -> S1 -> HQ, 3 nodos y FIB WAN invariantes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from urllib.request import urlopen

ROOT = "netlab360-s05-ha-backend-hq.service"
UNITS = (ROOT, "netlab360-s05-ha-backend-s1.service",
         "netlab360-s05-ha-frontal-hq.service")
OUTPUT_DIR = Path.home() / "netlab360-bootstrap/s05/evidencias/ha-noc"
NODES = {"BACKEND_HQ", "BACKEND_S1", "FRONTAL_HQ"}


def cmd(*argv: str) -> str:
    p = subprocess.run(argv, text=True, capture_output=True, timeout=12)
    if p.returncode:
        raise RuntimeError(f"Comando {argv[:3]} falló: {p.stderr[-300:]}")
    return p.stdout.strip()


def sample() -> dict:
    with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=5) as r:
        graph = json.load(r)
    nodes = {x["id"]: x for x in graph["nodes"] if x["id"] in NODES}
    if set(nodes) != NODES or graph.get("counts", {}).get("extensions") != 3:
        raise RuntimeError("El NOC no tiene aún los tres servicios HA")
    ha = graph.get("ha_service") or {}
    routes = (graph.get("routing") or {}).get("routes") or {}
    if not graph.get("routing", {}).get("available"):
        raise RuntimeError("FIB NOC ausente")
    if routes.get("S1", {}).get("dev") != "s1p" or routes.get("S2", {}).get("dev") != "s2p":
        raise RuntimeError("La FIB WAN no coincide con la línea base")
    return {
        "observed_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "ha_available": ha.get("available") is True,
        "active": ha.get("active_backend"),
        "path": ha.get("selected_path"),
        "status": ha.get("status"),
        "nodes": {k: v.get("status") for k, v in nodes.items()},
        "fib_s1": "s1p",
        "fib_s2": "s2p",
    }


def is_phase(value: dict, backend: str) -> bool:
    return (value["ha_available"] is True and
            value["active"] == backend and
            value["status"] == "running" and
            value["nodes"]["FRONTAL_HQ"] == "running" and
            value["nodes"][backend] == "running" and
            value["path"] == ("PRINCIPAL" if backend == "BACKEND_HQ" else "RESPALDO"))


def wait_phase(backend: str, timeout: float = 12, sink=None) -> dict:
    end = time.monotonic() + timeout
    last = None
    while time.monotonic() < end:
        try:
            obs = sample()
            if sink is not None:
                sink(obs)
            if is_phase(obs, backend):
                return obs
            last = obs
        except (OSError, ValueError, RuntimeError, KeyError, TimeoutError) as exc:
            last = str(exc)
        time.sleep(0.5)
    raise RuntimeError(f"Fase HTTP NOC no observada: {backend}; último={str(last)[:250]}")


def precheck() -> None:
    if cmd("hostname") != "netlab360-lab":
        raise RuntimeError("Hostname no coincide")
    for unit in UNITS + ("netlab360-s05-noc.service", "netlab360-s04-exporter.service",
                        "netlab360-s05-ha-monitor-s2.service"):
        if cmd("systemctl", "is-active", unit) != "active":
            raise RuntimeError("Servicio no activo: " + unit)
    if "192.168.47.40/24" not in cmd("ip", "-4", "-br", "address", "show", "ens33"):
        raise RuntimeError("Gestión VMnet8 inesperada")
    if "default via 192.168.47.2 dev ens33" not in cmd("ip", "-4", "route", "show", "default"):
        raise RuntimeError("Gateway host inesperado")
    wait_phase("BACKEND_HQ", timeout=8)
    print("S05_HA_NOC_PRECHECK=OK_PRINCIPAL_HQ", flush=True)


def run_trial(hold: int) -> None:
    precheck()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = OUTPUT_DIR / f"S05_HA_NOC_CICLO_{stamp}.jsonl"
    if path.exists():
        raise RuntimeError("Archivo de evidencia ya existe")
    record_count = 0
    last_phase = None
    observations: list[str] = []
    stopped = False
    with path.open("x", encoding="utf-8") as fp:
        os.chmod(path, 0o600)
        def record(row: dict) -> None:
            nonlocal record_count, last_phase
            fp.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
            fp.flush()
            record_count += 1
            actual = row.get("active")
            if actual != last_phase:
                last_phase = actual
                print("S05_HA_NOC_TRANSICION=" + str(actual), flush=True)
            if actual in NODES and row.get("ha_available"):
                observations.append(actual)

        record(sample())
        print("S05_HA_NOC_JSONL=" + str(path), flush=True)
        print("S05_HA_NOC_FASE_1=BACKEND_HQ", flush=True)
        try:
            cmd("sudo", "-n", "systemctl", "stop", ROOT)
            stopped = True
            print("S05_HA_NOC_BACKEND_HQ=DETENIDO_CONTROLADO", flush=True)
            wait_phase("BACKEND_S1", timeout=12, sink=record)
            print("S05_HA_NOC_FASE_2=BACKEND_S1", flush=True)
            end = time.monotonic() + hold
            while time.monotonic() < end:
                try:
                    record(sample())
                except (OSError, ValueError, RuntimeError, KeyError, TimeoutError) as exc:
                    print("S05_HA_NOC_MUESTRA_NO_CONFIABLE=" +
                          type(exc).__name__, flush=True)
                time.sleep(0.5)
        finally:
            if stopped:
                print("S05_HA_NOC_RESTAURACION_SOLICITADA=HQ", flush=True)
                cmd("sudo", "-n", "systemctl", "start", ROOT)
                wait_phase("BACKEND_HQ", timeout=15, sink=record)
                print("S05_HA_NOC_FASE_3=BACKEND_HQ", flush=True)
        final = sample()
        record(final)
    if "BACKEND_HQ" not in observations or "BACKEND_S1" not in observations:
        raise RuntimeError("NOC no observó el ciclo completo")
    if not is_phase(final, "BACKEND_HQ"):
        raise RuntimeError("NOC sin retorno a HQ")
    for unit in UNITS:
        if cmd("systemctl", "is-active", unit) != "active":
            raise RuntimeError("Servicio no recuperado: " + unit)
    print(f"S05_HA_NOC_MUESTRAS={record_count}", flush=True)
    print("S05_HA_NOC_CICLO=HQ_S1_HQ_OK", flush=True)
    print("S05_HA_NOC_FIB_S1=s1p", flush=True)
    print("S05_HA_NOC_FIB_S2=s2p", flush=True)
    print("S05_HA_NOC_SERVICIOS_RESTAURADOS=OK", flush=True)


def main() -> None:
    def interrupt(_sig, _frame):
        raise KeyboardInterrupt("Interrupción; restauración automática de HQ")
    signal.signal(signal.SIGHUP, interrupt)
    signal.signal(signal.SIGTERM, interrupt)
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--precheck", action="store_true")
    mode.add_argument("--run", action="store_true")
    p.add_argument("--hold-seconds", type=int, default=10)
    args = p.parse_args()
    if not (5 <= args.hold_seconds <= 20):
        raise ValueError("hold-seconds fuera de 5..20")
    if args.precheck:
        precheck()
    else:
        run_trial(args.hold_seconds)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyboardInterrupt,
            subprocess.TimeoutExpired) as exc:
        print(f"S05_HA_NOC_ERROR={type(exc).__name__}:{exc}", file=sys.stderr)
        sys.exit(2)
