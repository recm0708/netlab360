#!/usr/bin/env python3
"""Ejecutar consultas reales del dashboard y contrastarlas con Prometheus."""
import base64
import json
import math
from pathlib import Path
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contrastar_grafana import BASE, DASH, OPEN, ROOT, UID, get
from api import readers, slo_contract as S

PROM = "http://127.0.0.1:9091"
STEP = 10
SPAN = 300


def fetch(url, password=None, payload=None):
    """Consultar únicamente orígenes locales con respuestas acotadas."""
    req = Request(url, data=None if payload is None else json.dumps(payload).encode())
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    if password is not None:
        req.add_header("Authorization", "Basic " + base64.b64encode(
            ("netlab360-admin:" + password).encode()).decode())
    with OPEN.open(req, timeout=20) as response:
        return readers.decode(response.read(2_097_153), 2_097_152)


def add_point(points, probe, stamp, value):
    """Rechazar muestras duplicadas, no finitas o con sondas desconocidas."""
    S.probe(probe)
    key = (probe, stamp)
    assert key not in points
    assert isinstance(value, (int, float)) and not isinstance(value, bool)
    assert math.isfinite(value)
    points[key] = float(value)


def frame_points(result):
    """Extraer valores de los data frames reales, sin inferir etiquetas ni huecos."""
    assert result.get("status", 200) == 200 and not result.get("error")
    points = {}
    for frame in result["frames"]:
        fields = frame["schema"]["fields"]
        columns = frame["data"]["values"]
        assert len(fields) == len(columns)
        times = [i for i, field in enumerate(fields) if field["type"] == "time"]
        assert len(times) == 1
        stamps = columns[times[0]]
        assert all(isinstance(t, int) and t % 1000 == 0 for t in stamps)
        numbers = [i for i, field in enumerate(fields) if field["type"] == "number"]
        assert numbers
        for i in numbers:
            labels = fields[i]["labels"]
            assert labels["job"] == "netlab360-s08-blackbox"
            assert len(columns[i]) == len(stamps)
            for stamp, value in zip(stamps, columns[i]):
                add_point(points, labels["probe_id"], stamp // 1000, value)
    assert points
    return points


def prom_points(response, instant):
    """Normalizar vector o matriz Prometheus conservando tiempo e identidad."""
    assert response["status"] == "success" and not response.get("warnings")
    data = response["data"]
    assert data["resultType"] == ("vector" if instant else "matrix")
    points = {}
    for series in data["result"]:
        labels = series["metric"]
        assert labels["job"] == "netlab360-s08-blackbox"
        samples = [series["value"]] if instant else series["values"]
        for stamp, value in samples:
            assert int(stamp) == stamp
            add_point(points, labels["probe_id"], int(stamp), float(value))
    assert points
    return points


def compare_points(actual, expected, probes, stamps):
    """Exigir cobertura exacta y tolerancia numérica explícita."""
    assert set(expected) == {(p, t) for p in probes for t in stamps}
    assert set(actual) == set(expected)
    for key in expected:
        assert math.isclose(actual[key], expected[key], rel_tol=0, abs_tol=1e-9), key


def run(destination, password):
    """Ejecutar cada target aprovisionado al mismo corte fijo y registrar resultados."""
    dashboard = get("/api/dashboards/uid/" + DASH, password)["dashboard"]
    expected = json.loads((ROOT / "servicios/observabilidad/grafana/dashboards/sondas.json").read_text())
    assert dashboard["uid"] == DASH
    assert {p["id"] for p in dashboard["panels"]} == set(range(1, 11))
    assert len(dashboard["panels"]) == 10
    expected_panels = {p["id"]: p for p in expected["panels"]}
    end = (int(time.time()) - 30) // STEP * STEP
    start = end - SPAN
    rows = []
    for panel in dashboard["panels"]:
        reference = expected_panels[panel["id"]]
        assert panel["title"] == reference["title"]
        keys = ("refId", "expr", "datasource", "instant", "range", "legendFormat")
        contract = lambda targets: [{k: t[k] for k in keys} for t in targets]
        assert contract(panel["targets"]) == contract(reference["targets"])
        for target in panel["targets"]:
            assert target["datasource"]["uid"] == UID
            assert target["instant"] != target["range"]
            instant = target["instant"]
            query = dict(target, format="time_series", intervalMs=STEP * 1000,
                         maxDataPoints=1000)
            payload = {"from": str(start * 1000), "to": str(end * 1000), "queries": [query]}
            result = fetch(BASE + "/api/ds/query", password, payload)["results"]
            assert set(result) == {target["refId"]}
            actual = frame_points(result[target["refId"]])
            args = {"query": target["expr"]}
            if instant:
                args["time"] = end
                endpoint = "/api/v1/query"
                stamps = [end]
            else:
                args.update(start=start, end=end, step=STEP)
                endpoint = "/api/v1/query_range"
                stamps = range(start, end + 1, STEP)
            direct = prom_points(fetch(PROM + endpoint + "?" + urlencode(args)), instant)
            probes = {"s2-hq-http"} if panel["id"] == 4 else set(S.PROBES)
            compare_points(actual, direct, probes, stamps)
            rows.append({"panel_id": panel["id"], "title": panel["title"],
                         "ref_id": target["refId"], "mode": "instant" if instant else "range",
                         "points": len(actual), "probes": sorted(probes), "result": "MATCH"})
            print(f"PANEL={panel['id']} REF={target['refId']} PUNTOS={len(actual)} MATCH", flush=True)
    assert len(rows) == 19
    assert sum(row["points"] for row in rows) == 571
    with destination.open("x", encoding="utf-8") as handle:
        json.dump({"dashboard_uid": DASH, "start": start, "end": end, "step": STEP,
                   "queries": rows}, handle, indent=2, ensure_ascii=False, allow_nan=False)
    print("PANELES_EJECUTADOS=10/10 CONSULTAS=19/19 PUNTOS=571/571")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: ejecutar_paneles_grafana.py EVIDENCIA")
    run(Path(sys.argv[1]), sys.stdin.readline().strip())
