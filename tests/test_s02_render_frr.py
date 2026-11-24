#!/usr/bin/env python3
"""Regresion offline generacion FRR S02: no requiere Docker ni permisos."""
from __future__ import annotations

import importlib.util
import pathlib
import unittest

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/automatizacion/render_frr_s02.py"
SPEC = importlib.util.spec_from_file_location("nl360_render_s02", SCRIPT)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestRenderS02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = yaml.safe_load((ROOT / "inventario/ipam/topologia-s02.yaml").read_text())
        cls.result = mod.render(cls.inventory)

    def test_three_real_routers(self):
        self.assertEqual(set(self.result), {"R-HQ", "R-S1", "R-S2"})

    def test_hq_four_wan_and_three_vlan(self):
        cfg = self.result["R-HQ"]
        for name in ("s1p", "s1b", "s2p", "s2b"):
            self.assertIn(f"interface {name}\n", cfg)
            self.assertIn(f" no passive-interface {name}\n", cfg)
        for vlan in (110, 120, 130):
            self.assertIn(f"interface trunk0.{vlan}\n", cfg)
        self.assertEqual(cfg.count(" ip ospf cost 10\n"), 2)
        self.assertEqual(cfg.count(" ip ospf cost 100\n"), 2)

    def test_branches_both_links_correct(self):
        for router, code, vlans in (
            ("R-S1", "s1", (210, 220, 230)),
            ("R-S2", "s2", (310, 320, 330)),
        ):
            cfg = self.result[router]
            for d in ("p", "b"):
                self.assertIn(f"interface {code}{d}\n", cfg)
                self.assertIn(f" no passive-interface {code}{d}\n", cfg)
            for vlan in vlans:
                self.assertIn(f"interface trunk0.{vlan}\n", cfg)
            self.assertEqual(cfg.count(" ip ospf cost 10\n"), 1)
            self.assertEqual(cfg.count(" ip ospf cost 100\n"), 1)

    def test_candidate_required(self):
        wrong = dict(self.inventory)
        wrong["status"] = "deployed"
        with self.assertRaises(ValueError):
            mod.render(wrong)


if __name__ == "__main__":
    unittest.main()
