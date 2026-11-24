"""Pruebas offline del preparador runtime FRR S02 (sin sudo/Docker)."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts/automatizacion/preparar_runtime_frr_s02.py"
SPEC = importlib.util.spec_from_file_location("s02runtime", SRC)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class TestRuntimeS02(unittest.TestCase):
    def test_missing_daemons_are_added(self):
        template = "# frr\nmgmtd=yes\nstaticd=yes\n"
        out = module.build_daemons(template)
        self.assertEqual(out.count("zebra=yes\n"), 1)
        self.assertEqual(out.count("ospfd=yes\n"), 1)
        self.assertIn("mgmtd=yes", out)

    def test_disabled_daemons_are_replaced_once(self):
        template = "# base\nzebra=no\nospfd=no\nstaticd=yes\n"
        out = module.build_daemons(template)
        self.assertNotIn("zebra=no", out)
        self.assertNotIn("ospfd=no", out)
        self.assertEqual(out.count("zebra=yes"), 1)
        self.assertEqual(out.count("ospfd=yes"), 1)

    def test_alternative_whitespace_and_comments(self):
        template = " zebra = no\nospfd = no\n# ospfd=no\n"
        out = module.build_daemons(template)
        self.assertNotIn(" zebra = no", out)
        self.assertIn("# ospfd=no", out)
        self.assertTrue(out.endswith("zebra=yes\nospfd=yes\n"))

    def test_expected_three_routers(self):
        self.assertEqual(set(module.ROUTERS), {"R-HQ", "R-S1", "R-S2"})
        self.assertEqual(len(module.HASHES), 3)


if __name__ == "__main__":
    unittest.main()
