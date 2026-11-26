"""Contrato de identidad y cobertura de las matrices de Grafana."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/s08"))
import contrastar_cobertura_grafana as C


class CoverageTests(unittest.TestCase):
    def setUp(self):
        dashboard = json.loads((ROOT / "servicios/observabilidad/grafana/dashboards/sondas.json").read_text())
        self.panel = next(p for p in dashboard["panels"] if p["id"] == 6)
        self.results = {}
        for ref, counter in C.COUNTERS.items():
            self.results[ref] = {"frames": [
                {"schema": {"refId": ref, "fields": [
                    {"name": "Time", "type": "time"},
                    {"name": "Value", "type": "number",
                     "labels": {"job": "netlab360-s08-blackbox", "probe_id": probe},
                     "config": {"displayNameFromDS": probe + " " + counter}}]},
                 "data": {"values": [[10000], [29]]}}
                for probe in sorted(C.PROBES)]}

    def test_matrix(self):
        matrix, points = C.matrix_points(self.panel, self.results, 10)
        self.assertEqual(set(matrix), C.PROBES)
        self.assertEqual(sum(len(row) for row in matrix.values()), 20)
        self.assertEqual(sum(len(p) for p in points.values()), 20)

    def test_wrong_legend(self):
        result = copy.deepcopy(self.results)
        result["B"]["frames"][0]["schema"]["fields"][1]["config"]["displayNameFromDS"] = "wrong"
        with self.assertRaises(AssertionError):
            C.matrix_points(self.panel, result, 10)

    def test_missing_probe(self):
        self.results["A"]["frames"].pop()
        with self.assertRaises(AssertionError):
            C.matrix_points(self.panel, self.results, 10)

    def test_duplicate_probe(self):
        self.results["A"]["frames"].append(self.results["A"]["frames"][0])
        with self.assertRaises(AssertionError):
            C.matrix_points(self.panel, self.results, 10)

    def test_inconsistent_counts(self):
        self.results["D"]["frames"][0]["data"]["values"][1][0] = 31
        with self.assertRaises(AssertionError):
            C.matrix_points(self.panel, self.results, 10)


if __name__ == "__main__":
    unittest.main()
