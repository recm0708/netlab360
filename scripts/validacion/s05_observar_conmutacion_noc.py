#!/usr/bin/env python3
"""S05: observador SOLO LECTURA de conmutación WAN mostrada por el NOC.

No modifica Docker, FRR, interfaces, FIB, rutas ni ens33.
Lee únicamente 127.0.0.1:9130/api/v1/graph.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = "http://127.0.0.1:9130/api/v1/graph"
DEST = Path.home() / "netlab360-bootstrap/s05/evidencias/failover-noc"


class ObservacionError(Exception):
    """Fuente no confiable o validación incumplida."""


def consultar() -> dict:
    req = Request(API, headers={"Accept": "application/json", "Cache-Control": "no-cache"})
    try:
        with urlopen(req, timeout=6) as response:
            if response.status != 200:
                raise ObservacionError(f"HTTP inesperado {response.status}")
            data = json.load(response)
    except (OSError, ValueError, HTTPError, URLError, TimeoutError) as exc:
        raise ObservacionError(f"NOC 9130 no consultable: {exc}") from exc
    if not isinstance(data, dict) or data.get("project") != "NETLAB360":
        raise ObservacionError("Identidad o estructura de respuesta NOC inesperada")
    return data


def clasificar(data: dict, sede: str) -> dict:
    telemetry = data.get("telemetry") or {}
    routing = data.get("routing") or {}
    links = {link.get("id"): link for link in data.get("links", []) if isinstance(link, dict)}
    p = links.get(f"WAN-PRIMARIA-HQ-{sede}") or {}
    b = links.get(f"WAN-RESPALDO-HQ-{sede}") or {}
    primary = p.get("route_selection")
    backup = b.get("route_selection")
    reliable = telemetry.get("available") is True and routing.get("available") is True
    if not reliable:
        phase = "SIN_FUENTE_VERIFICABLE"
    elif primary == "selected" and backup == "standby":
        phase = "PRINCIPAL"
    elif backup == "selected" and primary in ("unavailable", "standby"):
        phase = "RESPALDO"
    else:
        phase = "TRANSICION"
    fib = (routing.get("routes") or {}).get(sede) or {}
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "sample_utc": data.get("observed_at_utc"),
        "sede": sede,
        "fase": phase,
        "topologia": telemetry.get("topology"),
        "fuente_s04": telemetry.get("available"),
        "fuente_fib": routing.get("available"),
        "principal": primary,
        "respaldo": backup,
        "principal_admin": p.get("status"),
        "respaldo_admin": b.get("status"),
        "fib_interfaz": fib.get("dev"),
        "fib_siguiente_salto": fib.get("gateway"),
        "trafico_medido": routing.get("traffic_measured"),
    }


def precheck(sede: str) -> dict:
    sample = clasificar(consultar(), sede)
    print(f"S05_NOC_SEDE={sede}", flush=True)
    print(f"S05_NOC_TOPOLOGIA={sample['topologia']}", flush=True)
    print(f"S05_NOC_FUENTE_S04={sample['fuente_s04']}", flush=True)
    print(f"S05_NOC_FUENTE_FIB={sample['fuente_fib']}", flush=True)
    print(f"S05_NOC_RUTA={sample['fib_interfaz']}", flush=True)
    print(f"S05_NOC_FASE={sample['fase']}", flush=True)
    if sample["topologia"] != "active" or sample["fase"] != "PRINCIPAL":
        raise ObservacionError("Es necesaria fuente S04/FIB confiable y ruta principal antes de iniciar")
    if sample["trafico_medido"] is not False:
        raise ObservacionError("Contrato de telemetría inesperado; no inferir medición")
    print("S05_NOC_PRECHECK=OK_SIN_CAMBIOS", flush=True)
    return sample


def observar(sede: str, seconds: int, interval: float) -> int:
    precheck(sede)
    DEST.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = DEST / f"S05_NOC_{sede}_OBSERVACION_{stamp}.jsonl"
    states = ["PRINCIPAL", "RESPALDO", "PRINCIPAL"]
    progress = 1
    last_phase = "PRINCIPAL"
    started = time.monotonic()
    samples = 0
    errors = 0
    print(f"S05_NOC_ARCHIVO={path}", flush=True)
    print(f"S05_NOC_OBSERVADOR_LISTO={sede}", flush=True)
    with path.open("x", encoding="utf-8") as stream:
        while time.monotonic() - started < seconds:
            try:
                state = clasificar(consultar(), sede)
                errors = 0
            except ObservacionError as exc:
                errors += 1
                state = {"sede": sede, "fase": "ERROR_CONSULTA",
                         "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                         "detalle": str(exc)[:200]}
            stream.write(json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()
            samples += 1
            phase = state["fase"]
            if phase != last_phase:
                print(f"S05_NOC_CAMBIO={sede}:{last_phase}->{phase} "
                      f"FIB={state.get('fib_interfaz')} "
                      f"NEXT_HOP={state.get('fib_siguiente_salto')}", flush=True)
                last_phase = phase
            if progress < 3 and phase == states[progress]:
                progress += 1
                if progress == 2:
                    print(f"S05_NOC_RESPALDO_OBSERVADO={sede}:OK", flush=True)
                else:
                    print(f"S05_NOC_RETORNO_PRINCIPAL_OBSERVADO={sede}:OK", flush=True)
                    break
            if errors >= 5:
                print("S05_NOC_FUENTE_PERDIDA=SI", flush=True)
                break
            time.sleep(interval)
    print(f"S05_NOC_MUESTRAS={samples}", flush=True)
    print(f"S05_NOC_CAPTURA_JSONL={path}", flush=True)
    ok = progress == 3
    print(f"S05_NOC_CICLO_COMPLETO={'OK' if ok else 'INCOMPLETO'}", flush=True)
    return 0 if ok else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--precheck", action="store_true", help="Sólo estado inicial")
    actions.add_argument("--watch", action="store_true", help="Registrar conmutación de NOC")
    parser.add_argument("--site", choices=("S1", "S2"), required=True)
    parser.add_argument("--seconds", type=int, default=90)
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args()
    if not 15 <= args.seconds <= 180 or not 0.25 <= args.interval <= 3:
        parser.error("Límites: 15-180 segundos y 0.25-3 s de muestreo")
    if args.precheck:
        precheck(args.site)
        return 0
    return observar(args.site, args.seconds, args.interval)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ObservacionError, OSError, ValueError, KeyboardInterrupt) as exc:
        print(f"S05_NOC_OBSERVACION_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(2)
