"""G5: métricas discretas y SLO propuesto, sin Prometheus real."""
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / "scripts/observabilidad/s04_sli_slo_observabilidad.py"
spec = importlib.util.spec_from_file_location("netlab360_g5_sli", P)
assert spec and spec.loader
sli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sli)


class SLIValidation(unittest.TestCase):
    def test_exact_396_success_is_observed_100(self):
        result = sli.summarize(396.0, 396.0, 99.0)
        self.assertEqual(result["pct"], 100.0)
        self.assertEqual(result["fail"], 0)
        self.assertEqual(result["allowance"], 3)
        self.assertTrue(result["would_pass_proposed_target"])

    def test_error_budget_boundary_discrete(self):
        passed = sli.summarize(393, 396, 99.0)
        failed = sli.summarize(392, 396, 99.0)
        self.assertEqual(passed["error_budget_remaining"], 0)
        self.assertTrue(passed["would_pass_proposed_target"])
        self.assertEqual(failed["error_budget_remaining"], -1)
        self.assertFalse(failed["would_pass_proposed_target"])

    def test_no_samples_cannot_appear_healthy(self):
        with self.assertRaises(ValueError):
            sli.summarize(0, 0, 99.0)

    def test_invalid_counts_and_nan_rejected(self):
        for pair in ((5, 4), (-1, 4), (1, float("nan")), (3.2, 4)):
            with self.assertRaises(ValueError):
                sli.summarize(*pair, 99.0)

    def test_source_conditional_is_not_user_sla(self):
        def fake(expr):
            if "count_over_time" in expr:
                return 396.0
            if "sum_over_time" in expr:
                return 396.0
            raise AssertionError(expr)
        result = sli.measure(minutes=15, target=99.0, scalar=fake)
        self.assertEqual(result["nominal_scrape_slots"], 450)
        self.assertEqual(result["sli"]["scrape"]["total"], 396)
        self.assertEqual(result["sli"]["fuente_condicional"]["total"], 396)
        self.assertEqual(result["evaluation"], "provisional_not_formal_slo")
        self.assertIn("ninguno es disponibilidad de red", result["scope"])

    def test_window_limit_and_proposal_limit(self):
        with self.assertRaises(ValueError):
            sli.measure(minutes=5)
        with self.assertRaises(ValueError):
            sli.measure(target=0.0)


if __name__ == "__main__":
    unittest.main()
