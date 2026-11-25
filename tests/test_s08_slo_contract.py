"""Pruebas offline del catálogo Blackbox y semántica de presupuesto de errores."""
import importlib.util
from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_slo_test", PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_slo_test import slo_contract as S


class SLOTests(unittest.TestCase):
    def test_catalog(self):
        rows = [S.probe(key) for key in S.PROBES]
        self.assertEqual(len(rows), 5)
        self.assertEqual({r["origin"] for r in rows}, {"HQ", "S2"})
        self.assertEqual({r["module"] for r in rows}, {"icmp_v4", "tcp_v4", "http_service"})
        self.assertEqual(S.probe("s2-hq-http")["target"], "http://10.70.20.23:8080/api/v1/service")

    def test_no_free_target(self):
        for target in ("192.168.47.40", "http://127.0.0.1", None, True, {}):
            with self.assertRaises(ValueError):
                S.probe(target)

    def test_absent(self):
        row = S.summarize(5, 0, 0, 0, 0)
        self.assertEqual(row["quality"], "ABSENT")
        self.assertIsNone(row["observed_availability_pct"])
        self.assertIsNone(row["burn_rate_observed"])
        self.assertIsNone(row["meets_observed_target"])

    def test_partial_no_false_pass(self):
        row = S.summarize(5, 30, 28, 27, 27)
        self.assertEqual(row["quality"], "PARTIAL")
        self.assertEqual(row["observed_availability_pct"], 100)
        self.assertEqual(row["unobserved_scrapes"], 3)
        self.assertIsNone(row["meets_observed_target"])

    def test_error_budget_boundary(self):
        row = S.summarize(60, 360, 360, 360, 357)
        self.assertEqual(row["allowed_failures_observed"], 3)
        self.assertEqual(row["remaining_budget_observed"], 0)
        self.assertTrue(row["meets_observed_target"])
        failed = S.summarize(60, 360, 360, 360, 356)
        self.assertFalse(failed["meets_observed_target"])
        self.assertGreater(failed["burn_rate_observed"], 1)

    def test_nominal_shortfall(self):
        row = S.summarize(15, 89, 89, 89, 89)
        self.assertEqual(row["nominal_slots"], 90)
        self.assertEqual(row["nominal_shortfall"], 1)
        self.assertIsNone(row["meets_observed_target"])

    def test_invalid_counts(self):
        for args in ((3, 30, 30, 30, 30), (5, True, 1, 1, 1), (5, 1, 2, 1, 1),
                     (5, 30, 20, 21, 21), (5, 30, 30, 20, 21)):
            with self.assertRaises(ValueError):
                S.summarize(*args)


if __name__ == "__main__":
    unittest.main()
