"""Regresion offline de la fuente unica de verdad NETLAB360 S03."""
import importlib.util
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s03sot", ROOT/"scripts/automatizacion/s03_generar_sot.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestS03SoT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = yaml.safe_load((ROOT/"inventario/ipam/topologia-s02.yaml").read_text())
        cls.sot, cls.inv = mod.build(cls.source)

    def test_three_routers_nine_vlan(self):
        self.assertEqual(set(self.sot["devices"]), {"R-HQ", "R-S1", "R-S2"})
        self.assertEqual(sum(len(v["vlans"]) for v in self.sot["devices"].values()), 9)

    def test_eight_wan_endpoints(self):
        self.assertEqual(sum(len(v["wan"]) for v in self.sot["devices"].values()), 8)
        self.assertEqual(len(self.sot["devices"]["R-HQ"]["wan"]), 4)

    def test_inventory_is_local_and_does_not_claim_live(self):
        h = self.inv["all"]["children"]["routers"]["hosts"]
        self.assertEqual(set(h), set(self.sot["devices"]))
        self.assertTrue(all(x["ansible_connection"] == "local" for x in h.values()))
        self.assertEqual(self.sot["source_status"], "candidate")
        self.assertIn("NOT proof", self.sot["caution"])


if __name__ == "__main__":
    unittest.main()
