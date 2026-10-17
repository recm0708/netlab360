#!/usr/bin/env python3
"""Tests unitarios offline del validador IPAM S02. No modifican redes."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import ipaddress
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "scripts/validacion/validar-ipam-s02.py"
SPEC = importlib.util.spec_from_file_location("netlab360_s02_ipam_validator", FILE)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class S02IpamValidationTests(unittest.TestCase):
    def quiet_static(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return validator.check_static()

    def test_static_inventory_is_isolated_from_b1(self):
        networks = self.quiet_static()
        self.assertEqual(len(networks), 16)  # 3 loopbacks, 9 VLAN, 4 WAN
        self.assertEqual(len({str(n) for _, n in networks}), 16)
        self.assertIn("10.78.0.8/30", [str(n) for _, n in networks])
        self.assertIn("10.78.0.12/30", [str(n) for _, n in networks])

    def test_null_docker_configs_not_interpreted_as_iterables(self):
        def fake_command(args):
            if args[:2] == ["ip", "-j"]:
                return json.dumps([{"dst": "192.168.47.0/24", "dev": "ens33"}])
            if "ls" in args:
                return "bridge\nhost\nnone\n"
            name = args[-1]
            if name == "bridge":
                config = [{"Subnet": "172.17.0.0/16"}]
            else:
                config = None
            return json.dumps([{"IPAM": {"Config": config}}])
        with patch.object(validator, "checked", side_effect=fake_command):
            with contextlib.redirect_stdout(io.StringIO()) as result:
                validator.check_live(self.quiet_static())
        self.assertIn("S02_COLISIONES_HOST_DOCKER=0", result.getvalue())

    def test_overlapping_host_route_blocks_candidate(self):
        def fake_command(args):
            if args[:2] == ["ip", "-j"]:
                return json.dumps([{"dst": "10.78.0.8/30", "dev": "tunX"}])
            if "ls" in args:
                return "none\n"
            return json.dumps([{"IPAM": {"Config": None}}])
        with patch.object(validator, "checked", side_effect=fake_command):
            with self.assertRaisesRegex(ValueError, "colisiones"):
                with contextlib.redirect_stdout(io.StringIO()):
                    validator.check_live(self.quiet_static())

    def test_duplicate_subnets_not_accepted(self):
        with self.assertRaises(ValueError):
            validator.require(False, "SOLAPAMIENTO_INTERNO=prueba")


if __name__ == "__main__":
    unittest.main()
