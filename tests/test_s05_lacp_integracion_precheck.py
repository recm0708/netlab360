"""Regresión offline del contrato S05 LACP plan/precheck (no muta redes)."""
from __future__ import annotations

import importlib.util
import io
import contextlib
from pathlib import Path
import unittest
from unittest import mock
import subprocess

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

    def test_plan_selectivo_s1_s2_no_marca_hq_libre(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            module.inventory(["S1", "S2"])
        value = out.getvalue()
        self.assertNotIn("S05_LACP_PLAN_HQ=", value)
        self.assertIn("S05_LACP_PLAN_S1=", value)
        self.assertIn("S05_LACP_PLAN_S2=", value)
        self.assertIn("S05_LACP_PLAN_SEDES_SOLICITADAS=S1,S2", value)
        self.assertIn("ALCANCE_SELECTIVO", value)

    def test_rechaza_sedes_duplicadas_y_desconocidas(self):
        for selected in (["HQ", "HQ"], ["S3"]):
            with self.assertRaises(ValueError):
                module.inventory(selected)

    def test_cli_accepts_selected_sites(self):
        import subprocess
        import sys
        process = subprocess.run(
            [sys.executable, str(PATH), "plan", "--sites", "S1", "S2"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn("S05_LACP_PLAN_SEDES_SOLICITADAS=S1,S2", process.stdout)
        self.assertNotIn("S05_LACP_PLAN_HQ=", process.stdout)

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

    def test_bridge_vlan_timeout_transitorio_se_recupera(self):
        timed = subprocess.TimeoutExpired(cmd=("ip", "netns", "exec"), timeout=30)
        with mock.patch.object(module, "privileged",
                               side_effect=[timed, mock.Mock(stdout="tr-sw 320\\n")]) as call, \
             mock.patch.object(module.time, "sleep") as sleep, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            value = module.read_bridge_vlans("nl360-s02-sw-s2")
        self.assertEqual(value, "tr-sw 320\\n")
        self.assertEqual(call.call_count, 2)
        self.assertEqual(call.call_args.kwargs["timeout"], 30)
        sleep.assert_called_once_with(1)
        self.assertIn("TIMEOUT_INTENTO_1", output.getvalue())
        self.assertIn("OK_INTENTO_2", output.getvalue())

    def test_bridge_vlan_falla_si_ambas_lecturas_expiran(self):
        timed = subprocess.TimeoutExpired(cmd=("ip", "netns", "exec"), timeout=30)
        with mock.patch.object(module, "privileged", side_effect=timed) as call, \
             mock.patch.object(module.time, "sleep"), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaisesRegex(RuntimeError, "Consulta VLAN no validada"):
                module.read_bridge_vlans("nl360-s02-sw-s2")
        self.assertEqual(call.call_count, 2)
        self.assertNotIn("OK_INTENTO", output.getvalue())

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
