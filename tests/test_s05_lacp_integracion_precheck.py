"""Regresión offline del contrato S05 LACP plan/precheck (no muta redes)."""
from __future__ import annotations

import importlib.util
import io
import contextlib
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/validacion/s05-lacp-integracion-precheck.py"
spec = importlib.util.spec_from_file_location("lacp_precheck", PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestS05LACPIntegrationPrecheck(unittest.TestCase):
    def test_plan_three_sites_and_fixed_existing_service_vlans(self):
        self.assertEqual(set(module.SITES), {"HQ", "S1", "S2"})
        self.assertEqual({x["vlan"] for x in module.SITES.values()},
                         {120, 220, 320})
        self.assertEqual(len({x["new_ns"] for x in module.SITES.values()}), 3)
        self.assertTrue(all(x["new_ns"].startswith("nl360-s05-lacp-")
                            for x in module.SITES.values()))
        with contextlib.redirect_stdout(io.StringIO()) as out:
            module.inventory()
        self.assertIn("S05_LACP_PLAN=3_SEDES", out.getvalue())

    def test_bridge_vlan_multiline_parser(self):
        text = (
            "port              vlan-id\n"
            "br0               1 PVID Egress Untagged\n"
            "tr-sw             110\n"
            "                  120\n"
            "                  130\n"
            "a120              120 PVID Egress Untagged\n"
            "ha-hq21           120 PVID Egress Untagged\n"
        )
        actual = module.parse_vlan_map(text)
        self.assertEqual(actual["tr-sw"], {110, 120, 130})
        self.assertEqual(actual["a120"], {120})
        self.assertEqual(actual["ha-hq21"], {120})

    def test_address_reader_only_ipv4_locals(self):
        data = '[{"ifname":"eth0","addr_info":[{"family":"inet","local":"10.70.20.21"},{"family":"inet6","local":"fe80::1"}]}]'
        self.assertEqual(module.ip_set(data), {"10.70.20.21"})

    def test_no_mutating_actions_offered(self):
        src = PATH.read_text(encoding="utf-8")
        self.assertIn('choices=("plan", "precheck")', src)
        self.assertNotIn('ip netns add', src)
        self.assertNotIn('link set master', src)
        self.assertNotIn('systemctl restart', src)
        self.assertNotIn('docker compose up', src)
        self.assertIn('ping', src)
        self.assertIn("S05_LACP_PRECHECK=OK_SIN_CAMBIOS_DE_CONFIGURACION", src)
        self.assertIn("S05_LACP_ADVERTENCIA=PING_SIN_RESPUESTA", src)

    def test_name_guards_and_ownership(self):
        self.assertIn("tr-sw", module.PROTECTED)
        self.assertIn("ens33", module.PROTECTED)
        self.assertIn("ha-hq21", module.PROTECTED)
        self.assertIn("ha-hq23", module.PROTECTED)
        self.assertIn("ha-s121", module.PROTECTED)
        self.assertEqual(len(module.SERVICES), 6)
        self.assertEqual(len(module.NEW_NAMES), 3)


if __name__ == "__main__":
    unittest.main()
