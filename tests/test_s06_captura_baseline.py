"""S06: pruebas offline del capturador sin red, Docker ni cambios de runtime."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/s06/capturar_baseline.py"
SPEC = importlib.util.spec_from_file_location("s06_baseline_unit", SCRIPT)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def prom(names, value=1):
    return {"status": "success", "data": {"resultType": "vector", "result": [
        {"metric": {"__name__": name},
         "value": [1795390000, str(value)]}
        for name in names
    ]}}


def good_graph():
    return {
        "telemetry": {"available": True},
        "routing": {"available": True},
        "ha_service": {"status": "running", "active_backend": "BACKEND_HQ"},
        "lacp": {"available": True, "sites": {
            site: {"status": "up", "switch_members": 2, "client_members": 2}
            for site in ("HQ", "S1", "S2")
        }},
        "sdn": {"available": True, "status": "connected", "flow_count": 31},
        "nodes": [{} for _ in range(18)],
        "links": [{} for _ in range(21)],
        "source_warnings": [],
    }


class TestS06Baseline(unittest.TestCase):
    def test_familias_metricas_exactas(self):
        items = mod.parse_prom_vector(prom(sorted(mod.METRICS)), s04_only=True)
        self.assertEqual({m["name"] for m in items}, mod.METRICS)

    def test_rechaza_metrica_ajena(self):
        with self.assertRaisesRegex(ValueError, "Nombre"):
            mod.parse_prom_vector(prom(["otro_colector"]), s04_only=True)

    def test_rechaza_nan(self):
        with self.assertRaisesRegex(ValueError, "finito"):
            mod.parse_prom_vector(prom(["netlab360_s04_source_up"], "NaN"),
                                  s04_only=True)

    def test_rechaza_resultado_de_tipo_matriz(self):
        response = prom(["netlab360_s04_source_up"])
        response["data"]["resultType"] = "matrix"
        with self.assertRaisesRegex(ValueError, "Prometheus"):
            mod.parse_prom_vector(response, s04_only=True)

    def test_sin_scrape_no_pasa_calidad(self):
        metrics = mod.parse_prom_vector(prom(sorted(mod.METRICS)), s04_only=True)
        ok, reason = mod.quality({"source_ok": True, "topology": "active"},
                                 good_graph(), {"healthy": True}, metrics, [])
        self.assertFalse(ok)
        self.assertIn("prom_scrape_unavailable", reason)

    def test_baseline_sana_no_equivale_ground_truth(self):
        originals = {
            ("s04", "/api/v1/state"): {"source_ok": True, "topology": "active"},
            ("noc", "/api/v1/graph"): good_graph(),
            ("noc", "/healthz"): {"healthy": True},
        }
        def response(source, path, *, params=None, timeout=6):
            if source == "prom":
                query = params["query"]
                return (prom(["up"]) if query == mod.JOB_QUERY
                        else prom(sorted(mod.METRICS)))
            return originals[(source, path)]
        with mock.patch.object(mod, "request_json", side_effect=response):
            sample = mod.get_sample()
        self.assertTrue(sample["observed_healthy"])
        self.assertEqual(sample["ground_truth_label"], "UNKNOWN")
        self.assertFalse(sample["ground_truth_verified"])
        self.assertEqual(len(sample["metric_samples"]), 5)
        self.assertEqual(sample["noc"]["node_count"], 18)

    def test_metrica_source_zero_no_pasa(self):
        metrics = mod.parse_prom_vector(prom(sorted(mod.METRICS)), s04_only=True)
        for m in metrics:
            if m["name"] == "netlab360_s04_source_up":
                m["value"] = 0
        scrape = mod.parse_prom_vector(prom(["up"]), s04_only=False)
        ok, reasons = mod.quality({"source_ok": True, "topology": "active"},
                                  good_graph(), {"healthy": True}, metrics, scrape)
        self.assertFalse(ok)
        self.assertIn("source_metric_not_one", reasons)

    def test_fallo_ha_no_pasa(self):
        graph = good_graph()
        graph["ha_service"]["active_backend"] = "BACKEND_S1"
        metrics = mod.parse_prom_vector(prom(sorted(mod.METRICS)), s04_only=True)
        scrape = mod.parse_prom_vector(prom(["up"]), s04_only=False)
        ok, reasons = mod.quality({"source_ok": True, "topology": "active"},
                                  graph, {"healthy": True}, metrics, scrape)
        self.assertFalse(ok)
        self.assertIn("http_ha_baseline_unknown", reasons)

    def test_limites_de_captura(self):
        mod.validate_limits(12, 2.0, 6)
        for inputs in ((0, 2, 6), (61, 2, 6),
                       (12, 0.5, 6), (12, 31, 6),
                       (12, 2, 1), (12, 2, 11)):
            with self.subTest(inputs=inputs):
                with self.assertRaises(ValueError):
                    mod.validate_limits(*inputs)

    def test_escritura_atomica_en_directorio_aislado(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "metadata.json"
            mod.write_json(p, {"ground_truth_label": "UNKNOWN"})
            self.assertEqual(json.loads(p.read_text())["ground_truth_label"],
                             "UNKNOWN")
            self.assertFalse(p.with_name("metadata.json.tmp").exists())

    def test_sqlite_solo_lectura(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "events.sqlite3"
            con = sqlite3.connect(p)
            con.execute('CREATE TABLE "active"(fingerprint TEXT)')
            con.execute('CREATE TABLE "events"(id INTEGER)')
            con.execute('INSERT INTO "events" VALUES (1)')
            con.commit()
            con.close()
            self.assertEqual(mod.sqlite_counts(p), {"active": 0, "events": 1})

    def test_descarta_resultado_prom_invalido(self):
        response = prom(["netlab360_s04_source_up"])
        response["status"] = "error"
        with self.assertRaises(ValueError):
            mod.parse_prom_vector(response, s04_only=True)


if __name__ == "__main__":
    unittest.main()
