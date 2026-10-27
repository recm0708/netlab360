#!/usr/bin/env python3
"""S04 G4: evidencia de persistencia de TSDB tras reiniciar SOLO Prometheus 9091.

Uso sobre Ubuntu: --before (guarda baseline) -> Ctrl+C y reiniciar Prometheus
en su terminal original -> --after (compara series y nueva hora de arranque).
NO detiene procesos ni altera FRR, ens33, Docker, WAN, VLAN o Prometheus.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
from urllib.parse import urlencode
from urllib.request import urlopen

PROM = "http://127.0.0.1:9091"
DIR = Path.home() / "netlab360-bootstrap/s04/evidencias"
PRE = DIR / "S04_G4_TSDB_Antes_Reinicio.json"
POST = DIR / "S04_G4_TSDB_Despues_Reinicio.json"
START = datetime(2026, 10, 27, 6, 4, 45, tzinfo=timezone.utc).timestamp()
END = datetime(2026, 10, 27, 6, 7, 0, tzinfo=timezone.utc).timestamp()
WAN = 'netlab360_s04_wan_admin_up{site="HQ",interface="s1p"}'
FIRING = 'ALERTS{alertname="NETLAB360S04WANAdminDown",alertstate="firing",site="HQ",interface="s1p"}'


def get_json(url: str) -> dict:
    if not url.startswith(PROM + "/api/v1/"):
        raise ValueError("URL ajena a Prometheus S04")
    with urlopen(url, timeout=10) as response:
        return json.load(response)


def query_range(expr: str, reader=get_json) -> list:
    qs = urlencode({"query": expr, "start": START, "end": END, "step": "2s"})
    doc = reader(PROM + "/api/v1/query_range?" + qs)
    if doc.get("status") != "success":
        raise RuntimeError("Prometheus no devolvio consulta exitosa")
    results = doc["data"]["result"]
    if not isinstance(results, list) or len(results) != 1:
        raise RuntimeError("Historico ausente o con cardinalidad inesperada")
    values = results[0].get("values", [])
    if not values:
        raise RuntimeError("Historico no contiene muestras")
    return [[float(v[0]), float(v[1])] for v in values]


def check_values(wan: list, firing: list) -> None:
    wan_vals = [value for _, value in wan]
    alert_vals = [value for _, value in firing]
    if not (len(wan) > 1 and 0.0 in wan_vals and 1.0 in wan_vals):
        raise RuntimeError("No se observan los estados WAN DOWN/UP reales")
    if not alert_vals or any(value != 1.0 for value in alert_vals):
        raise RuntimeError("Serie de alerta firing invalida")
    if any(wan[i][0] >= wan[i + 1][0] for i in range(len(wan) - 1)):
        raise RuntimeError("Timestamps de WAN no monotónicos")


def snapshot(reader=get_json) -> dict:
    status = reader(PROM + "/api/v1/status/runtimeinfo")
    if status.get("status") != "success":
        raise RuntimeError("Prometheus no comunica runtimeinfo")
    started = status.get("data", {}).get("startTime")
    if not isinstance(started, str) or not started:
        raise RuntimeError("Falta startTime de Prometheus")
    wan = query_range(WAN, reader)
    firing = query_range(FIRING, reader)
    check_values(wan, firing)
    return {
        "schema": "NETLAB360_S04_G4_TSDB_V1",
        "prometheus_start_utc": started,
        "window_start_utc": "2026-10-27T06:04:45Z",
        "window_end_utc": "2026-10-27T06:07:00Z",
        "step_seconds": 2,
        "wan": wan,
        "firing": firing,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def validate_after(before: dict, after: dict) -> None:
    if before.get("schema") != after.get("schema"):
        raise RuntimeError("Version de baseline no coincide")
    if before.get("prometheus_start_utc") == after.get("prometheus_start_utc"):
        raise RuntimeError("Prometheus no fue reiniciado: startTime es el mismo")
    for key in ("window_start_utc", "window_end_utc", "step_seconds", "wan", "firing"):
        if before.get(key) != after.get(key):
            raise RuntimeError(f"TSDB distinta tras reinicio: {key}")


def write_exclusive(path: Path, data: dict) -> None:
    if path.is_symlink() or path.exists():
        raise RuntimeError(f"No sobrescribir registro anterior: {path}")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description="S04 G4 persistencia historica")
    choices = parser.add_mutually_exclusive_group(required=True)
    choices.add_argument("--before", action="store_true")
    choices.add_argument("--after", action="store_true")
    args = parser.parse_args()
    if os.geteuid() == 0 or socket.gethostname() != "netlab360-lab":
        raise RuntimeError("Ejecutar como usuario normal en VM NETLAB360")
    if not DIR.is_dir() or DIR.is_symlink():
        raise RuntimeError("Directorio de evidencias externo inexistente/invalido")
    current = snapshot()
    if args.before:
        write_exclusive(PRE, current)
        print("========== S04 G4 BASELINE ANTES DE REINICIO ==========")
        print("S04_G4_PROMETHEUS_START=" + current["prometheus_start_utc"])
        print(f"S04_G4_WAN_MUESTRAS_ANTES={len(current['wan'])}")
        print(f"S04_G4_ALERTA_FIRING_MUESTRAS_ANTES={len(current['firing'])}")
        print(f"S04_G4_REGISTRO_ANTES={PRE}")
        print("S04_G4_BASELINE=OK")
    else:
        if not PRE.is_file() or PRE.is_symlink():
            raise RuntimeError("No existe baseline previa protegida")
        before = json.loads(PRE.read_text(encoding="utf-8"))
        validate_after(before, current)
        write_exclusive(POST, current)
        print("========== S04 G4 TSDB DESPUES DE REINICIO ==========")
        print("S04_G4_PROMETHEUS_START_ANTES=" + before["prometheus_start_utc"])
        print("S04_G4_PROMETHEUS_START_DESPUES=" + current["prometheus_start_utc"])
        print(f"S04_G4_WAN_MUESTRAS_DESPUES={len(current['wan'])}")
        print(f"S04_G4_ALERTA_FIRING_MUESTRAS_DESPUES={len(current['firing'])}")
        print(f"S04_G4_REGISTRO_DESPUES={POST}")
        print("S04_G4_PERSISTENCIA_TSDB=OK")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"S04_G4_ERROR={type(exc).__name__}: {exc}")
        raise SystemExit(1)
