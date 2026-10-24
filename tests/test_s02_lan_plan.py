"""Test offline para el inventario LAN/VLAN S02; no crea interfaces."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import ipaddress
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("s02_lan", ROOT/"scripts/laboratorio/s02-lan-vlan.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestS02Lan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with contextlib.redirect_stdout(io.StringIO()):
            cls.result = mod.plan()

    def test_three_sites_nine_vlan(self):
        self.assertEqual(set(self.result), {"HQ", "S1", "S2"})
        self.assertEqual(sum(len(v["vlans"]) for v in self.result.values()), 9)

    def test_addresses_are_inside_subnets(self):
        for site, row in self.result.items():
            for vlan in row["vlans"]:
                net = ipaddress.ip_network(vlan["subnet"])
                gw = ipaddress.ip_address(vlan["gateway"])
                host = ipaddress.ip_interface(vlan["host_ip"])
                self.assertIn(gw, net)
                self.assertIn(host.ip, net)
                self.assertNotEqual(gw, host.ip)
                self.assertEqual(host.network, net)

    def test_all_namespaces_unique_and_separate(self):
        names = []
        for site, row in self.result.items():
            names.append(row["switch"])
            names.extend(v["host"] for v in row["vlans"])
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(n.startswith("nl360-s02-") for n in names))
        self.assertEqual(len(names), 12)

    def test_preserves_management_network(self):
        for site, row in self.result.items():
            for vlan in row["vlans"]:
                self.assertNotIn("192.168.47", vlan["host_ip"])
                self.assertNotEqual(vlan["host"], "ens33")


if __name__ == "__main__":
    unittest.main()
