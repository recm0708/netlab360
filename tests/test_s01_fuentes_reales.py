#!/usr/bin/env python3
"""Pruebas con datos ARTIFICIALES de test; no se mezclan con datos reales B4."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "scripts/analitica/b4_auditar_fuentes_reales.py"
spec = importlib.util.spec_from_file_location("b4_audit", TARGET)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class B4SourcesTests(unittest.TestCase):
    def test_csv_rows(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-test-") as d:
            source = Path(d) / "test.csv"
            source.write_text("seq,ruta\n1,wan-p\n2,wan-b\n", encoding="utf-8")
            r = mod.csv_summary(source)
            self.assertEqual(r["rows"], 2)
            self.assertEqual(r["columns"], ["seq", "ruta"])

    def test_jsonl_known_events(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-test-") as d:
            source = Path(d) / "test.jsonl"
            source.write_text(
                json.dumps({"observed_at": "2026-10-13T17:39:33-05:00",
                            "event": "WAN_PRIMARY_DOWN"}) + "\n", encoding="utf-8"
            )
            result = mod.jsonl_summary(source)
            self.assertEqual(result["events"], 1)
            self.assertEqual(result["types"], {"WAN_PRIMARY_DOWN": 1})

    def test_unknown_events_not_silently_accepted(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-test-") as d:
            source = Path(d) / "bad.jsonl"
            source.write_text(
                json.dumps({"observed_at": "2026-10-13T17:39:33-05:00",
                            "event": "INVENTADO"}) + "\n", encoding="utf-8"
            )
            with self.assertRaises(AssertionError):
                mod.jsonl_summary(source)

    def test_dataset_readiness_not_invented(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-test-") as d:
            old = mod.BASE
            try:
                mod.BASE = Path(d)
                result = mod.inspect()
            finally:
                mod.BASE = old
            self.assertEqual(result["total_event_rows"], 0)
            self.assertFalse(result["independent_normal_labels_available"])
            self.assertFalse(result["ml_supervised_evaluation_ready"])


if __name__ == "__main__":
    unittest.main()
