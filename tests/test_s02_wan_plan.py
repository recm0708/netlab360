"""NETLAB360 S02: pruebas OFFLINE de correspondencia IPAM -> WAN veth."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s02_wan_links", ROOT / "scripts/laboratorio/s02-wan-links.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestWanS02Plan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            cls.plan = mod.plan()

    def test_four_dual_wan_links(self):
        self.assertEqual(len(self.plan), 4)
        self.assertEqual({v["nic"] for v in self.plan}, {"s1p", "s1b", "s2p", "s2b"})
        self.assertEqual(sum(v["branch"] == "R-S1" for v in self.plan), 2)
        self.assertEqual(sum(v["branch"] == "R-S2" for v in self.plan), 2)

    def test_endpoints_and_prefixes(self):
        expected = {
            "s1p": ("10.78.0.1/30", "10.78.0.2/30"),
            "s1b": ("10.78.0.5/30", "10.78.0.6/30"),
            "s2p": ("10.78.0.9/30", "10.78.0.10/30"),
            "s2b": ("10.78.0.13/30", "10.78.0.14/30"),
        }
        for v in self.plan:
            self.assertEqual((v["hq_ip"], v["branch_ip"]), expected[v["nic"]])

    def test_unique_temporary_host_interfaces(self):
        names = [n for v in self.plan
                 for n in (v["temporary_hq"], v["temporary_branch"])]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(len(n) < 16 for n in names))

    def test_no_management_interface_in_links(self):
        for v in self.plan:
            self.assertNotEqual(v["nic"], "ens33")
            self.assertNotIn("192.168.47", v["hq_ip"] + v["branch_ip"])


if __name__ == "__main__":
    unittest.main()
