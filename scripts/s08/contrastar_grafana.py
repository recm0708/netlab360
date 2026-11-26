#!/usr/bin/env python3
"""Contrastar el origen aprovisionado de Grafana con Prometheus y NETLAB360."""
import base64
import json
import math
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "servicios/consola-s08"))
from api import observability_reader as R, readers, slo_contract as S

UID = "netlab360-prometheus"
DASH = "netlab360-s08-observacion"
BASE = "http://127.0.0.1:3000"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPEN = build_opener(ProxyHandler({}), NoRedirect())


def get(path, password=None):
    req = Request(BASE + path)
    if password is not None:
        req.add_header("Authorization", "Basic " + base64.b64encode(
            ("netlab360-admin:" + password).encode()).decode())
    with OPEN.open(req, timeout=15) as response:
        return readers.decode(response.read(2_097_153), 2_097_152)


def compare(destination, password):
    health = get("/api/health")
    assert health["version"] == "13.3.2" and health["database"] == "ok"
    try:
        get("/api/dashboards/uid/" + DASH)
    except HTTPError as error:
        assert error.code in (401, 403), "GRAFANA_UNEXPECTED_AUTH_STATUS"
    else:
        raise ValueError("GRAFANA_ANONYMOUS_ACCESS")
    source = get("/api/datasources/uid/" + UID, password)
    assert source["uid"] == UID and source["type"] == "prometheus"
    assert source["url"] == "http://127.0.0.1:9091" and source["readOnly"] is True
    dashboard = get("/api/dashboards/uid/" + DASH, password)["dashboard"]
    expected = json.loads((ROOT / "servicios/observabilidad/grafana/dashboards/sondas.json").read_text())
    assert dashboard["uid"] == DASH and dashboard["editable"] is False
    def contract(data):
        return {p["id"]: [(t["expr"], t["datasource"]["uid"], t["instant"], t["range"])
                          for t in p["targets"]] for p in data["panels"]}
    assert contract(dashboard) == contract(expected)
    print("GRAFANA_VERSION=13.3.2 DASHBOARD=10/10 FUENTE=OK", flush=True)
    snapshot = R.collect()
    assert set(snapshot["transport"].values()) == {"OK"}
    end = snapshot["window_end_unix"]
    proxy = "/api/datasources/proxy/uid/" + UID + "/api/v1/query?"
    fields = {}
    for metric in R.METRICS:
        data = get(proxy + urlencode({"query": R.expression(metric), "time": str(end)}), password)
        actual = R.series(data, metric, end)
        transport, direct = R.fetch(metric, end)
        assert transport == "OK" and actual == direct
        fields[metric] = sum(len(v) for v in actual.values())
        print(f"METRICA={metric} MUESTRAS={fields[metric]} CONTRASTE=MATCH", flush=True)
    windows = []
    selector = '{job="' + R.JOB + '"}'
    for minutes in S.WINDOWS_MIN:
        values = {}
        queries = {
            "scrape_count": f"count_over_time(up{selector}[{minutes}m])",
            "scrape_ok": f"sum_over_time(up{selector}[{minutes}m])",
            "probe_count": f"count_over_time(probe_success{selector}[{minutes}m])",
            "probe_ok": f"sum_over_time(probe_success{selector}[{minutes}m])",
            "observed_availability_pct": f"100 * sum_over_time(probe_success{selector}[{minutes}m]) / count_over_time(probe_success{selector}[{minutes}m])",
        }
        for field, expr in queries.items():
            data = get(proxy + urlencode({"query": expr, "time": str(end)}), password)
            assert data["status"] == "success" and not data.get("warnings")
            assert data["data"]["resultType"] == "vector"
            values[field] = {}
            for series in data["data"]["result"]:
                key = series["metric"]["probe_id"]
                S.probe(key)
                assert key not in values[field]
                assert abs(series["value"][0] - end) <= .001
                number = float(series["value"][1])
                assert math.isfinite(number)
                values[field][key] = number
            assert set(values[field]) == set(S.PROBES)
        for row in snapshot["probes"]:
            key = row["probe"]["id"]
            w = next(w for w in row["windows"] if w["window_minutes"] == minutes)
            for field in queries:
                assert math.isclose(values[field][key], w[field], rel_tol=0, abs_tol=1e-9)
            windows.append({"probe_id": key, "window_minutes": minutes, "quality": w["quality"],
                            "fields": {f: v[key] for f, v in values.items()}})
            print(f"SONDA={key} VENTANA={minutes}m CALIDAD={w['quality']} GRAFANA=MATCH")
    assert len(windows) == 15
    with destination.open("x", encoding="utf-8") as handle:
        json.dump({"version": health["version"], "dashboard_uid": DASH, "datasource_uid": UID,
                   "window_end_unix": end, "series_counts": fields, "windows": windows},
                  handle, indent=2, allow_nan=False)
    print("SERIES_CONTRASTADAS=4/4 VENTANAS=15/15 CAMPOS=75/75")
    print("ACCESO_ANONIMO_DASHBOARD=DENEGADO")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: contrastar_grafana.py EVIDENCIA")
    compare(Path(sys.argv[1]), sys.stdin.readline().strip())
