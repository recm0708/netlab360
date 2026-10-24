"""Pruebas offline de normalizacion/SoT de observabilidad S03."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s03obs", ROOT/"scripts/validacion/s03-estado-observado.py"
)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestObservedS03(unittest.TestCase):
    def test_ipv4_address_normalization(self):
        raw = [
            {"ifname": "lo", "addr_info": [
                {"family": "inet", "local": "127.0.0.1", "prefixlen": 8},
                {"family": "inet", "local": "10.79.0.1", "prefixlen": 32},
            ]},
            {"ifname": "trunk0.110", "addr_info": [
                {"family": "inet", "local": "10.70.10.1", "prefixlen": 24},
            ]},
        ]
        d = mod.addr_map(raw)
        self.assertIn("10.79.0.1/32", d["lo"])
        self.assertEqual(d["trunk0.110"], {"10.70.10.1/24"})

    def test_expected_ips_from_desired_state(self):
        desired = {
            "loopback": "10.79.0.2/32",
            "vlans": [{"interface": "trunk0.210",
                       "subnet": "10.71.10.0/24", "gateway": "10.71.10.1"}],
            "wan": [{"interface": "s1p", "address": "10.78.0.2/30"}],
        }
        d = mod.expected_ips(desired)
        self.assertEqual(d["lo"], {"10.79.0.2/32"})
        self.assertEqual(d["trunk0.210"], {"10.71.10.1/24"})
        self.assertEqual(d["s1p"], {"10.78.0.2/30"})

    def test_absent_ipv4_interface_detectable(self):
        actual = mod.addr_map([{"ifname": "lo", "addr_info": []}])
        desired = mod.expected_ips({
            "loopback": "10.79.0.1/32", "vlans": [], "wan": []
        })
        self.assertFalse(desired["lo"].issubset(actual["lo"]))


if __name__ == "__main__":
    unittest.main()
