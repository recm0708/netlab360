#!/usr/bin/env python3
"""S05: ensayo controlado de fallback HTTP HQ->S1->HQ, sin tocar WAN.

Precheck de solo lectura: --precheck
Prueba real: --run --hold-seconds 8
Exclusivamente detiene e inicia la unidad S05 netlab360-s05-ha-backend-hq.
El frontal y backend S1 siguen activos; se recupera backend HQ en finally.
"""
from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.request import urlopen

ROOT = "netlab360-s05-ha-backend-hq.service"
BACKUP = "netlab360-s05-ha-backend-s1.service"
FRONTEND = "netlab360-s05-ha-frontal-hq.service"
CLIENT = "nl360-s02-h-s2-320"
PROBE = """
import json
from urllib.request import Request, build_opener, ProxyHandler
req=Request("http://10.70.20.23:8080/api/v1/service",
            headers={"Cache-Control":"no-store"})
with build_opener(ProxyHandler({})).open(req, timeout=4) as response:
    assert response.status == 200
    data=json.load(response)
print(json.dumps(data, sort_keys=True))
"""


def log(*args):
    print(*args, flush=True)


def cmd(*args: str, timeout: float = 15) -> str:
    out = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if out.returncode:
        raise RuntimeError(f"Comando fallido {args}: {out.stderr[-400:]}")
    return out.stdout.strip()


def sudo(*args: str) -> str:
    return cmd("sudo", "-n", *args)


def probe() -> dict:
    raw = sudo("ip", "netns", "exec", CLIENT, "/usr/bin/python3",
               "-c", PROBE)
    data = json.loads(raw)
    if (data.get("service") != "netlab360-s05-ha" or
            data.get("role") != "frontend" or
            data.get("status") != "available"):
        raise RuntimeError("Servicio HA sin estructura de disponibilidad")
    return data


def expected(backend: str, phase: str) -> dict:
    result = probe()
    if result.get("active_backend") != backend or result.get("selected_path") != phase:
        raise RuntimeError(f"Seleccion HTTP inesperada: {result}")
    return result


def wait(backend: str, phase: str, timeout: float = 12) -> dict:
    end = time.monotonic() + timeout
    last = ""
    while time.monotonic() < end:
        try:
            return expected(backend, phase)
        except (RuntimeError, OSError, TimeoutError) as exc:
            last = str(exc)
        time.sleep(0.4)
    raise RuntimeError(f"Timeout HTTP {phase} {backend}: {last}")


def check() -> None:
    if cmd("hostname") != "netlab360-lab":
        raise RuntimeError("Máquina no autorizada")
    for unit in (ROOT, BACKUP, FRONTEND):
        if cmd("systemctl", "is-active", unit) != "active":
            raise RuntimeError("Servicio HA no activo: " + unit)
    if cmd("systemctl", "is-active", "netlab360-s05-noc") != "active":
        raise RuntimeError("NOC no activo")
    if "192.168.47.40/24" not in cmd("ip", "-4", "-br", "address", "show", "ens33"):
        raise RuntimeError("Gestión inesperada")
    if "default via 192.168.47.2 dev ens33" not in cmd(
        "ip", "-4", "route", "show", "default"
    ):
        raise RuntimeError("Ruta host inesperada")
    expected("BACKEND_HQ", "PRINCIPAL")
    log("S05_HTTP_PRECHECK=OK_PRINCIPAL_HQ")


def fib_check() -> None:
    with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=5) as response:
        graph = json.load(response)
    route = graph.get("routing", {}).get("routes") or {}
    if (not graph.get("routing", {}).get("available") or
            route.get("S1", {}).get("dev") != "s1p" or
            route.get("S2", {}).get("dev") != "s2p"):
        raise RuntimeError("FIB no preservada")
    log("S05_HTTP_WAN_SIN_CAMBIOS=S1:s1p,S2:s2p")


def experiment(hold: int) -> None:
    check()
    fib_check()
    log("========== INICIO_PRUEBA_S05_HTTP_HA ==========")
    log("S05_HTTP_FASE_1=PRINCIPAL_BACKEND_HQ")
    log("S05_HTTP_NEXT_HOP_INTERSEDE=SE_OBSERVA_S1_POR_VLAN")
    log(f"S05_HTTP_VENTANA_RESPALDO_SOLICITADA={hold}_SEG")
    paused = False
    try:
        sudo("systemctl", "stop", ROOT)
        paused = True
        if cmd("systemctl", "show", "-p", "ActiveState", "--value", ROOT) != "inactive":
            raise RuntimeError("Backend principal no se detuvo")
        log("S05_HTTP_BACKEND_HQ=DETENIDO_CONTROLADAMENTE")
        wait("BACKEND_S1", "RESPALDO")
        log("S05_HTTP_FASE_2=RESPALDO_BACKEND_S1")
        start = time.monotonic()
        count = 0
        while time.monotonic() - start < hold:
            expected("BACKEND_S1", "RESPALDO")
            count += 1
            time.sleep(0.5)
        log(f"S05_HTTP_RESPALDO_MUESTRAS_CORRECTAS={count}")
        log("S05_HTTP_FALLBACK_VERIFICADO=OK")
    finally:
        if paused:
            log("S05_HTTP_RESTAURACION_SOLICITADA=BACKEND_HQ")
            sudo("systemctl", "start", ROOT)
            recovered = wait("BACKEND_HQ", "PRINCIPAL", timeout=15)
            log("S05_HTTP_FASE_3=PRINCIPAL_BACKEND_HQ")
            log(f"S05_HTTP_RETORNO_BACKEND={recovered['active_backend']}")
            log("S05_HTTP_RETORNO=OK")
    fib_check()
    log("S05_HTTP_PRUEBA_CICLO_COMPLETO=OK")
    log("========== FIN_PRUEBA_S05_HTTP_HA ==========")


def main() -> None:
    def interrupt(_sig, _frame):
        raise KeyboardInterrupt("Interrupción; restaurar backend HQ")
    signal.signal(signal.SIGHUP, interrupt)
    signal.signal(signal.SIGTERM, interrupt)
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--precheck", action="store_true")
    group.add_argument("--run", action="store_true")
    p.add_argument("--hold-seconds", type=int, default=8)
    args = p.parse_args()
    if args.hold_seconds < 5 or args.hold_seconds > 20:
        raise RuntimeError("hold-seconds debe estar entre 5 y 20")
    log("S05_HTTP_HORA_PANAMA=" +
        datetime.now(ZoneInfo("America/Panama")).isoformat(timespec="seconds"))
    if args.precheck:
        check()
        fib_check()
    else:
        experiment(args.hold_seconds)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError,
            subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
        log(f"S05_HTTP_PRUEBA_ERROR={type(exc).__name__}: {exc}")
        sys.exit(2)
