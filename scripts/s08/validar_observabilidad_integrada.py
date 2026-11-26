#!/usr/bin/env python3
"""Contrastar el lector integrado con agregaciones PromQL al mismo corte."""
import json
from pathlib import Path
import sys
from urllib.parse import urlencode

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "servicios/consola-s08"))
from api import observability_reader as R, readers, slo_contract as S


def aggregate(function, metric, minutes, end):
    expression = f'{function}({metric}{{job="{R.JOB}"}}[{minutes}m])'
    path = "/api/v1/query?" + urlencode({"query": expression, "time": str(end)})
    payload, _, transport = readers._fetch_fixed(9091, path, R.MAX_BYTES)
    if transport != "OK" or payload.get("status") != "success" or payload.get("warnings"):
        raise ValueError("AGGREGATE_UNAVAILABLE")
    data = payload["data"]
    if data["resultType"] != "vector":
        raise ValueError("AGGREGATE_TYPE")
    result = {}
    for row in data["result"]:
        key = row["metric"]["probe_id"]
        S.probe(key)
        if key in result or abs(row["value"][0] - end) > .001:
            raise ValueError("AGGREGATE_IDENTITY")
        number = float(row["value"][1])
        if not 0 <= number <= 400 or number != int(number):
            raise ValueError("AGGREGATE_VALUE")
        result[key] = int(number)
    return result


def main(destination):
    snapshot = R.collect()
    if set(snapshot["transport"].values()) != {"OK"}:
        raise ValueError("SOURCE_UNAVAILABLE")
    end = snapshot["window_end_unix"]
    checks = []
    for minutes in S.WINDOWS_MIN:
        direct = {field: aggregate(fn, metric, minutes, end) for field, fn, metric in (
            ("scrape_count", "count_over_time", "up"),
            ("scrape_ok", "sum_over_time", "up"),
            ("probe_count", "count_over_time", "probe_success"),
            ("probe_ok", "sum_over_time", "probe_success"),
        )}
        for row in snapshot["probes"]:
            key = row["probe"]["id"]
            window = next(w for w in row["windows"] if w["window_minutes"] == minutes)
            for field, values in direct.items():
                if window[field] != values.get(key, 0):
                    raise ValueError(f"PROMQL_MISMATCH:{key}:{minutes}:{field}")
            checks.append({"probe_id": key, "window_minutes": minutes,
                           "fields": {f: values.get(key, 0) for f, values in direct.items()}})
            print(f"SONDA={key} VENTANA={minutes}m MUESTRAS={window['probe_count']}"
                  f" CALIDAD={window['quality']} SLI={window['observed_availability_pct']}"
                  " PROMQL=MATCH")
    for row in snapshot["probes"]:
        latest = row["latest"]
        if (row["quality"] != "VALID" or latest["duration_seconds"] is None):
            raise ValueError("LATEST_PROBE_NOT_AVAILABLE")
        if row["probe"]["module"] == "http_service" and latest["http_status_code"] is None:
            raise ValueError("HTTP_STATUS_NOT_AVAILABLE")
    if len(checks) != 15:
        raise ValueError("WINDOW_COUNT")
    with destination.open("x", encoding="utf-8") as handle:
        json.dump({"snapshot": snapshot, "comparison": checks}, handle, ensure_ascii=False,
                  allow_nan=False, indent=2)
    print("VENTANAS_CONTRASTADAS=15/15 CAMPOS=60/60")
    print("ULTIMAS_OBSERVACIONES_VALIDAS=5/5")
    print("EVIDENCIA=" + str(destination))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: validar_observabilidad_integrada.py EVIDENCIA")
    main(Path(sys.argv[1]))
