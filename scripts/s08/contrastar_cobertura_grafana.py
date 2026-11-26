#!/usr/bin/env python3
"""Contrastar los contadores que alimentan las matrices de cobertura de Grafana."""
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ejecutar_paneles_grafana as G
from api import slo_contract as S

COUNTERS = {"A": "adquisición", "B": "adquisición correcta",
            "C": "medidas", "D": "éxitos"}
PANELS = {6: 30, 8: 90, 10: 360}
PROBES = set(S.PROBES)


def matrix_points(panel, results, end):
    """Validar las etiquetas y leyendas reales antes de construir la matriz."""
    assert set(results) == set(COUNTERS)
    transform = panel["transformations"]
    assert [t["id"] for t in transform] == [
        "seriesToRows", "extractFields", "groupingToMatrix", "organize"]
    extractor = transform[1]["options"]
    assert extractor["format"] == "regexp" and extractor["source"] == "Metric"
    pattern = extractor["regExp"]
    assert pattern.startswith("/") and pattern.endswith("/")
    regex = re.compile(pattern[1:-1].replace("(?<", "(?P<"))
    assert transform[2]["options"] == {
        "rowField": "Sonda", "columnField": "Contador",
        "valueField": "Value", "emptyValue": "null"}
    matrix = {}
    by_ref = {}
    for ref, suffix in COUNTERS.items():
        result = results[ref]
        points = G.frame_points(result)
        assert set(points) == {(probe, end) for probe in PROBES}
        assert len(result["frames"]) == len(PROBES)
        for frame in result["frames"]:
            schema = frame["schema"]
            assert schema.get("refId") == ref
            fields = schema["fields"]
            assert len(fields) == 2
            number = next(f for f in fields if f["type"] == "number")
            probe = number["labels"]["probe_id"]
            legend = number["config"]["displayNameFromDS"]
            assert legend == probe + " " + suffix
            # Series to rows utiliza el nombre del frame o de su campo de valor.
            assert not schema.get("name") or schema["name"] == legend
            match = regex.fullmatch(legend)
            assert match and match.groupdict() == {"Sonda": probe, "Contador": suffix}
            value = points[(probe, end)]
            assert value >= 0 and value.is_integer()
            row = matrix.setdefault(probe, {})
            assert suffix not in row
            row[suffix] = int(value)
        by_ref[ref] = points
    assert set(matrix) == PROBES
    assert all(set(row) == set(COUNTERS.values()) for row in matrix.values())
    for row in matrix.values():
        assert row["adquisición correcta"] <= row["adquisición"]
        assert row["éxitos"] <= row["medidas"]
    return matrix, by_ref


def run(destination, password):
    """Contrastar las doce consultas agrupadas con Prometheus al mismo corte."""
    dashboard = G.fetch(G.BASE + "/api/dashboards/uid/" + G.DASH, password)["dashboard"]
    reference = json.loads((G.ROOT / "servicios/observabilidad/grafana/dashboards/sondas.json").read_text())
    assert dashboard["timezone"] == reference["timezone"] == "America/Panama"
    expected = {p["id"]: p for p in reference["panels"] if p["id"] in PANELS}
    panels = {p["id"]: p for p in dashboard["panels"] if p["id"] in PANELS}
    assert set(panels) == set(PANELS)
    end = (int(time.time()) - 30) // G.STEP * G.STEP
    evidence = []
    for panel_id, nominal in PANELS.items():
        panel = panels[panel_id]
        assert panel["type"] == "table"
        assert panel["transformations"] == expected[panel_id]["transformations"]
        keys = ("refId", "expr", "datasource", "instant", "range", "legendFormat", "format")
        assert [{k: t[k] for k in keys} for t in panel["targets"]] == [
            {k: t[k] for k in keys} for t in expected[panel_id]["targets"]]
        queries = [dict(t, intervalMs=G.STEP * 1000, maxDataPoints=1000)
                   for t in panel["targets"]]
        assert all(q["format"] == "time_series" and q["instant"] and not q["range"]
                   for q in queries)
        payload = {"from": str((end - G.SPAN) * 1000), "to": str(end * 1000), "queries": queries}
        response = G.fetch(G.BASE + "/api/ds/query", password, payload)["results"]
        matrix, points = matrix_points(panel, response, end)
        for target in queries:
            ref = target["refId"]
            direct = G.prom_points(G.fetch(G.PROM + "/api/v1/query?" + urlencode({
                "query": target["expr"], "time": end})), True)
            G.compare_points(points[ref], direct, PROBES, [end])
            print(f"TABLA={panel_id} REF={ref} PUNTOS=5 MATCH")
        evidence.append({"panel_id": panel_id, "nominal": nominal, "rows": matrix,
                         "queries": 4, "numeric_cells": 20})
    assert len(evidence) == 3
    with destination.open("x", encoding="utf-8") as handle:
        json.dump({"end": end, "tables": evidence}, handle, indent=2,
                  ensure_ascii=False, allow_nan=False)
    print("MATRICES_CONTRASTADAS=3/3 FILAS=15/15 CELDAS=60/60")
    print("LEYENDAS_ORIGINALES_VERIFICADAS=60/60")
    print("RENDERIZACION_NAVEGADOR=PENDIENTE")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: contrastar_cobertura_grafana.py EVIDENCIA")
    run(Path(sys.argv[1]), sys.stdin.readline().strip())
