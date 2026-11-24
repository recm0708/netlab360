#!/usr/bin/env python3
"""Regresion estadistica B4 con fixtures ARTIFICIALES exclusivos de tests."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts/analitica/b4_perfil_estadistico_real.py"
spec = importlib.util.spec_from_file_location("b4_profile", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

HEADER = "fecha_local,segundos_desde_inicio,sondeo,fase,interfaz_fib,icmp_ok,rtt_ms,codigo_ping\n"


class B4ProfileTests(unittest.TestCase):
    def test_phase_statistics_and_fib_counts(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-stat-test-") as d:
            path = Path(d) / "sample.csv"
            path.write_text(
                HEADER +
                "2026-10-13T11:00:00-05:00,0.0,1,normal,wan-p,1,0.1,0\n" +
                "2026-10-13T11:00:01-05:00,1.0,2,normal,wan-p,1,0.3,0\n" +
                "2026-10-13T11:00:02-05:00,2.0,3,cambio_respaldo,wan-b,0,,1\n" +
                "2026-10-13T11:00:03-05:00,3.0,4,respaldo,wan-b,1,0.2,0\n",
                encoding="utf-8"
            )
            s = module.analyze_csv(path)
            self.assertEqual(s["samples"], 4)
            self.assertEqual(s["icmp_failed"], 1)
            self.assertEqual(s["stable_fib_mismatches"], 0)
            self.assertEqual(s["phases"]["normal"]["rtt_mean_ms"], 0.2)
            self.assertEqual(s["phases"]["normal"]["rtt_p95_nearest_rank_ms"], 0.3)
            self.assertEqual(s["phases"]["cambio_respaldo"]["rtt_observations"], 0)

    def test_different_route_in_stable_phase_not_hidden(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-stat-test-") as d:
            path = Path(d) / "sample.csv"
            path.write_text(
                HEADER + "t,1.0,1,normal,wan-b,true,0.03,0\n",
                encoding="utf-8"
            )
            self.assertEqual(module.analyze_csv(path)["stable_fib_mismatches"], 1)

    def test_duplicate_probe_rejected(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-stat-test-") as d:
            path = Path(d) / "sample.csv"
            path.write_text(
                HEADER +
                "t,1.0,1,normal,wan-p,1,0.03,0\n" +
                "t,2.0,1,normal,wan-p,1,0.03,0\n",
                encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                module.analyze_csv(path)

    def test_non_finite_rtt_rejected(self):
        with tempfile.TemporaryDirectory(prefix="nl360-b4-stat-test-") as d:
            path = Path(d) / "sample.csv"
            path.write_text(
                HEADER + "t,1.0,1,normal,wan-p,1,nan,0\n",
                encoding="utf-8"
            )
            with self.assertRaises(ValueError):
                module.analyze_csv(path)

    def test_unknown_icmp_encoding_rejected(self):
        with self.assertRaises(ValueError):
            module.icmp_bool("desconocido")


if __name__ == "__main__":
    unittest.main()
