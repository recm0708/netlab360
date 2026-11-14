"""S05: prueba offline del despliegue LACP HQ sobre bridge existente."""
from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/laboratorio/s05-lacp-hq-integracion.py"
spec = importlib.util.spec_from_file_location("s05_lacp_hq", SCRIPT)
assert spec and spec.loader
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class TestS05LacpHQ(unittest.TestCase):
    def test_plan_displays_only_hq_and_protected_interfaces(self):
        with redirect_stdout(io.StringIO()) as stream:
            lab.plan()
        msg = stream.getvalue()
        self.assertIn("SW:nl360-s02-sw-hq", msg)
        self.assertIn("VLAN:120", msg)
        self.assertIn("10.70.20.40/24", msg)
        self.assertIn("S05_LACP_HQ_PLAN=OK_SIN_CAMBIOS", msg)
        self.assertNotIn("S05_LACP_HQ_DESPLIEGUE=OK", msg)

    def test_requires_explicit_confirmation_for_up_and_down(self):
        for action in ("up", "down"):
            p = subprocess.run(
                [sys.executable, str(SCRIPT), action],
                capture_output=True, text=True, timeout=10
            )
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("--confirm-isolated", p.stderr)

    def test_namespaces_and_devices_are_distinct_from_s02_and_ha(self):
        self.assertEqual(lab.CLIENT, "nl360-s05-lacp-hq")
        self.assertEqual(lab.SW, "nl360-s02-sw-hq")
        self.assertEqual(lab.SW_BOND, "s5bond0")
        self.assertEqual(lab.CLIENT_BOND, "bond0")
        self.assertEqual(len(lab.SW_SLAVES), 2)
        self.assertEqual(len(lab.CLIENT_SLAVES), 2)
        self.assertTrue(set(lab.SW_SLAVES).isdisjoint(lab.PROTECTED))
        for name in ("ens33", "br0", "tr-sw", "ha-hq21", "ha-hq23"):
            self.assertTrue(name == "ens33" or name in lab.PROTECTED)

    def test_no_host_network_or_container_mutation(self):
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("docker compose", src)
        self.assertNotIn("systemctl restart", src)
        self.assertNotIn('"link", "delete", "dev", "br0"', src)
        self.assertNotIn('"link", "delete", "dev", "tr-sw"', src)
        self.assertIn('"link", "set", SW_BOND, "master", "br0"', src)
        self.assertIn('"bridge", "vlan", "add", "dev", SW_BOND', src)
        self.assertIn('"mode", "802.3ad"', src)
        self.assertIn('"xmit_hash_policy", "layer3+4"', src)
        self.assertIn("S05_LACP_HQ_ERROR_ROLLBACK_SELECTIVO", src.replace(
            'S05_LACP_HQ_DESPLIEGUE=ERROR_ROLLBACK_SELECTIVO',
            'S05_LACP_HQ_ERROR_ROLLBACK_SELECTIVO'
        ))
        self.assertIn("STATE.unlink()", src)

    def test_up_checks_precheck_before_creating_resources(self):
        with mock.patch.object(lab, "precheck", side_effect=RuntimeError("freno")):
            with mock.patch.object(lab, "write_state") as write:
                with mock.patch.object(lab, "cmd") as cmd:
                    with self.assertRaisesRegex(RuntimeError, "freno"):
                        lab.up()
                    write.assert_not_called()
                    cmd.assert_not_called()

    def test_cleanup_refuses_unknown_resource_before_any_delete(self):
        record = {
            "status": "active", "alias": "S05_HQ_0123456789abcdef",
            "before": {"mgmt": {"ens33": "x", "routes": "y"},
                       "switch": {"ports": {}, "vlans": {}}},
        }
        with mock.patch.object(lab, "management", return_value=record["before"]["mgmt"]), \
             mock.patch.object(lab, "assert_protected"), \
             mock.patch.object(lab, "netns", return_value={lab.CLIENT, lab.SW}), \
             mock.patch.object(lab, "cmd", return_value=""), \
             mock.patch.object(lab, "assert_owned", side_effect=RuntimeError("alias no validado")), \
             mock.patch.object(lab, "ip_ns") as netcmd:
            with self.assertRaisesRegex(RuntimeError, "alias no validado"):
                lab.cleanup(record)
            netcmd.assert_not_called()

    def test_cleanup_allows_only_bridge_mac_drift(self):
        expected = {"ports": {
            "br0": {"ifindex": 1, "mac": "06:01", "master": None},
            "tr-sw": {"ifindex": 2, "mac": "08:02", "master": 1},
        }, "vlans": {"br0": ["1 PVID Egress Untagged"],
                     "tr-sw": ["120"]}}
        bridge_mac_only = {"ports": {
            "br0": {"ifindex": 1, "mac": "fe:10", "master": None},
            "tr-sw": {"ifindex": 2, "mac": "08:02", "master": 1},
        }, "vlans": expected["vlans"]}
        with mock.patch.object(lab, "protected_snapshot", return_value=bridge_mac_only):
            lab.assert_protected(expected, before_cleanup=True)
            with self.assertRaises(RuntimeError):
                lab.assert_protected(expected)
        bridge_mac_only["vlans"] = {"br0": ["1"], "tr-sw": ["120"]}
        with mock.patch.object(lab, "protected_snapshot", return_value=bridge_mac_only):
            with self.assertRaises(RuntimeError):
                lab.assert_protected(expected, before_cleanup=True)

    def test_ping_verificado_recupera_timeout_y_registra_intento(self):
        timed_out = subprocess.TimeoutExpired(
            cmd=["sudo", "ip", "netns", "exec", lab.CLIENT, "ping"], timeout=15
        )
        with mock.patch.object(lab, "ns_exec", side_effect=[timed_out, ""]) as cmd, \
             mock.patch.object(lab.time, "sleep") as sleep, \
             redirect_stdout(io.StringIO()) as output:
            lab.ping_verified(lab.CLIENT, "10.72.20.20", attempts=2)
        self.assertEqual(cmd.call_count, 2)
        sleep.assert_called_once_with(1)
        self.assertIn("TIMEOUT_PROCESO", output.getvalue())
        self.assertIn("S05_LACP_HQ_PING_10.72.20.20=OK", output.getvalue())

    def test_ping_verificado_no_declarar_ok_si_todo_falla(self):
        timed_out = subprocess.TimeoutExpired(cmd=["ping"], timeout=15)
        with mock.patch.object(lab, "ns_exec", side_effect=timed_out) as cmd, \
             mock.patch.object(lab.time, "sleep"), \
             redirect_stdout(io.StringIO()) as output:
            with self.assertRaisesRegex(RuntimeError, "NO_VALIDADO"):
                lab.ping_verified(lab.CLIENT, "10.72.20.20", attempts=3)
        self.assertEqual(cmd.call_count, 3)
        self.assertNotIn("=OK", output.getvalue())

    def test_protected_port_set_includes_existing_bridge_and_ha(self):
        self.assertEqual(set(lab.PROTECTED), {
            "br0", "tr-sw", "a110", "a120", "a130", "ha-hq21", "ha-hq23"
        })
        self.assertEqual(lab.IP, "10.70.20.40/24")
        self.assertEqual(lab.GW, "10.70.20.1")
        self.assertEqual(lab.VID, 120)


if __name__ == "__main__":
    unittest.main()
