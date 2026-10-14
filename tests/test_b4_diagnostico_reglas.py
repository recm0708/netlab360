#!/usr/bin/env python3
"""Fixtures sintéticos exclusivos de tests; NO se publican como telemetría real."""
import importlib.util
import math
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts/analitica/b4-diagnostico-reglas.py"
spec = importlib.util.spec_from_file_location("b4_rules", SOURCE)
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)


def row(seq, phase="normal", fib="wan-p", ok="1", rtt="0.03"):
    return {"fecha_local": "2026-10-13T11:00:00-05:00",
            "segundos_desde_inicio": str(seq - 1), "sondeo": str(seq),
            "fase": phase, "interfaz_fib": fib,
            "icmp_ok": ok, "rtt_ms": rtt, "codigo_ping": "0"}


class B4RulesTests(unittest.TestCase):
    def test_expected_fib_and_phase_change_not_incident(self):
        result = rules.evaluate_rows([
            row(1), row(2, "cambio_respaldo", "wan-b"),
            row(3, "respaldo", "wan-b"),
            row(4, "restaurada", "wan-p")
        ], normal_p95=0.049)
        self.assertEqual(result["samples"], 4)
        self.assertEqual(result["signal_occurrences"], 0)
        self.assertEqual(result["transition_count"], 3)

    def test_three_different_signals(self):
        sample = [
            row(1, "normal", "wan-b", "1", "0.20"),
            row(2, "respaldo", "wan-b", "0", ""),
            row(3, "cambio_respaldo", "wan-p", "1", "0.03")
        ]
        result = rules.evaluate_rows(sample, normal_p95=0.049)
        self.assertEqual(result["signal_counts"], {
            "ICMP_FALLIDO": 1,
            "FIB_INESPERADA_FASE_ESTABLE": 1,
            "RTT_SOBRE_REFERENCIA": 1,
        })
        self.assertEqual(result["signal_occurrences"], 3)
        self.assertAlmostEqual(result["rtt_reference_threshold_ms"], 0.147)

    def test_no_fib_alarm_in_transition(self):
        result = rules.evaluate_rows(
            [row(1, "cambio_principal", "wan-b")], normal_p95=0.049
        )
        self.assertEqual(result["signal_counts"]["FIB_INESPERADA_FASE_ESTABLE"], 0)

    def test_invalid_threshold_or_missing_reference(self):
        with self.assertRaises(ValueError):
            rules.evaluate_rows([row(1)], normal_p95=0)
        with self.assertRaises(ValueError):
            rules.evaluate_rows([row(1)], normal_p95=math.nan)
        with self.assertRaises(ValueError):
            rules.evaluate_rows([row(1)], normal_p95=0.05, factor=1.0)

    def test_duplicate_probe_rejected(self):
        with self.assertRaises(ValueError):
            rules.evaluate_rows([row(1), row(1)], normal_p95=0.049)

    def test_invalid_icmp_rejected(self):
        with self.assertRaises(ValueError):
            rules.evaluate_rows([row(1, ok="inventado")], normal_p95=0.049)

    def test_non_finite_rtt_rejected(self):
        with self.assertRaises(ValueError):
            rules.evaluate_rows([row(1, rtt="nan")], normal_p95=0.049)

    def test_csv_empty_rejected(self):
        with self.assertRaises(ValueError):
            rules.evaluate_rows([], normal_p95=0.049)


if __name__ == "__main__":
    unittest.main()
