"""S05 topology: offline graph contract and truthful status tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

APP = Path(__file__).resolve().parents[1] / "servicios/topologia-s05/app.py"
spec = importlib.util.spec_from_file_location("netlab360_s05_graph", APP)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TopologyGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = module.inventory()
        cls.extensions = {"schema_version": 1, "nodes": [], "links": []}

    def build(self, snapshot=None, ns=None, ext=None):
        return module.graph(
            self.inventory, snapshot, ns, self.extensions if ext is None else ext
        )

    @staticmethod
    def active_snapshot():
        return {
            "topology": "active",
            "sites": {
                site: {
                    "running": 1,
                    "wan": {name: {"admin_up": 1} for name in ("s1p", "s1b", "s2p", "s2b")},
                    "vlans": {
                        str(v): {"admin_up": 1}
                        for v in (
                            {"HQ": (110, 120, 130), "S1": (210, 220, 230),
                             "S2": (310, 320, 330)}[site]
                        )
                    },
                }
                for site in ("HQ", "S1", "S2")
            },
        }

    def test_three_sites_full_inventory_not_invented(self):
        result = self.build()
        self.assertEqual(result["counts"]["sites"], 3)
        self.assertEqual(result["counts"]["routers"], 3)
        self.assertEqual(result["counts"]["switches"], 3)
        self.assertEqual(result["counts"]["hosts"], 9)
        self.assertEqual(result["counts"]["wan"], 4)
        self.assertEqual(len(result["nodes"]), 15)
        self.assertEqual(len(result["links"]), 16)
        self.assertTrue(all(n["status"] == "unknown" for n in result["nodes"]))
        self.assertTrue(all(l["status"] == "unknown" for l in result["links"]))

    def test_observed_offline(self):
        snapshot = self.active_snapshot()
        snapshot["topology"] = "offline"
        for site in snapshot["sites"].values():
            site["running"] = 0
        out = self.build(snapshot, set())
        self.assertEqual({n["status"] for n in out["nodes"]}, {"offline"})
        self.assertTrue(all(
            link["status"] == "offline"
            for link in out["links"] if link["type"] == "wan"
        ))

    def test_wan_requires_both_ends_up(self):
        snap = self.active_snapshot()
        snap["sites"]["HQ"]["wan"]["s1p"]["admin_up"] = 0
        out = self.build(snap, set())
        wan = {l["id"]: l for l in out["links"] if l["type"] == "wan"}
        self.assertEqual(wan["WAN-PRIMARIA-HQ-S1"]["status"], "admin-down")
        self.assertEqual(wan["WAN-RESPALDO-HQ-S1"]["status"], "admin-up")
        self.assertEqual(wan["WAN-PRIMARIA-HQ-S2"]["status"], "admin-up")
        self.assertNotIn("active", {l["status"] for l in wan.values()})

    def test_one_end_not_observed_is_unknown(self):
        snap = self.active_snapshot()
        snap["sites"]["S1"]["wan"]["s1p"]["admin_up"] = -1
        wan = [l for l in self.build(snap)["links"]
               if l["id"] == "WAN-PRIMARIA-HQ-S1"][0]
        self.assertEqual(wan["status"], "unknown")

    def test_namespace_is_not_assumed_alive(self):
        snap = self.active_snapshot()
        result = self.build(snap, {"nl360-s02-sw-hq", "nl360-s02-h-hq-110"})
        hosts = {n["id"]: n for n in result["nodes"]}
        self.assertEqual(hosts["SW-HQ"]["status"], "namespace-present")
        self.assertEqual(hosts["H-HQ-110"]["status"], "namespace-present")
        self.assertEqual(hosts["H-HQ-120"]["status"], "offline")
        self.assertEqual(hosts["H-HQ-110"]["vlan_admin"], "admin-up")
        self.assertNotIn("server", {n["type"] for n in result["nodes"]})

    def test_extension_only_realized_and_valid(self):
        ext = {"schema_version": 1, "nodes": [
            {"id": "HA-HQ-A", "site": "HQ", "type": "server", "label": "HA verificado",
             "realized": True, "evidence": "issue con pruebas"},
            {"id": "FUTURO-S1", "site": "S1", "type": "server", "realized": False}
        ], "links": []}
        out = self.build(ext=ext)
        self.assertEqual(out["counts"]["extensions"], 1)
        self.assertEqual(out["nodes"][-1]["status"], "unknown")
        ext["nodes"][0]["id"] = "R-HQ"
        with self.assertRaises(ValueError):
            self.build(ext=ext)


if __name__ == "__main__":
    unittest.main()
