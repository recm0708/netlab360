"""Pruebas offline: S1/S2 sin cambios fuera de namespaces de su sede."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SITES = {
    "S1": ("nl360-s02-sw-s1", "nl360-s05-lacp-s1",
           "10.71.20.40/24", "10.71.20.1", 220,
           {"br0", "tr-sw", "a210", "a220", "a230", "ha-s121"}),
    "S2": ("nl360-s02-sw-s2", "nl360-s05-lacp-s2",
           "10.72.20.40/24", "10.72.20.1", 320,
           {"br0", "tr-sw", "a310", "a320", "a330"}),
}


def load(site):
    path = ROOT / f"scripts/laboratorio/s05-lacp-{site.lower()}-integracion.py"
    spec = importlib.util.spec_from_file_location(f"s05_lacp_{site}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestS05SucursalesLACP(unittest.TestCase):
    def test_identidad_de_sede_y_no_colision_con_hq(self):
        for site, (sw, client, ip, gw, vlan, protected) in SITES.items():
            with self.subTest(site=site):
                m = load(site)
                self.assertEqual(m.SW, sw)
                self.assertEqual(m.CLIENT, client)
                self.assertEqual(m.IP, ip)
                self.assertEqual(m.GW, gw)
                self.assertEqual(m.VID, vlan)
                self.assertEqual(set(m.PROTECTED), protected)
                self.assertEqual(m.SITE, site)
                self.assertEqual(m.OWNER, f"NETLAB360_S05_LACP_{site}_V1")
                self.assertEqual(m.STATE.name, f"state-{site.lower()}.json")
                self.assertEqual(m.SW_BOND, "s5bond0")
                self.assertEqual(m.CLIENT_BOND, "bond0")
                self.assertTrue(set(m.SW_SLAVES).isdisjoint(protected))
                self.assertNotEqual(m.CLIENT, "nl360-s05-lacp-hq")

    def test_plan_no_crea_recursos(self):
        for site in SITES:
            with self.subTest(site=site):
                m = load(site)
                with redirect_stdout(io.StringIO()) as stream:
                    m.plan()
                t = stream.getvalue()
                self.assertIn(f"S05_LACP_{site}_PLAN=OK_SIN_CAMBIOS", t)
                self.assertIn(m.IP, t)
                self.assertIn("NO_MODIFICAR=WAN_FRR", t)

    def test_precheck_limitado_a_la_sede(self):
        for site in SITES:
            with self.subTest(site=site):
                m = load(site)
                baseline = {"mgmt": {"x": 1}, "switch": {"ports": {}, "vlans": {}}}
                with mock.patch.object(m, "identity"), \
                     mock.patch.object(m.STATE, "exists", return_value=False), \
                     mock.patch.object(m.STATE, "is_symlink", return_value=False), \
                     mock.patch.object(m, "cmd", return_value="S05_LACP_PRECHECK=OK_SIN_CAMBIOS_DE_CONFIGURACION\n") as cmd, \
                     mock.patch.object(m, "netns", return_value={m.SW}), \
                     mock.patch.object(m, "links", return_value={}), \
                     mock.patch.object(m, "management", return_value=baseline["mgmt"]), \
                     mock.patch.object(m, "protected_snapshot", return_value=baseline["switch"]), \
                     mock.patch.object(m, "assert_services"):
                    with redirect_stdout(io.StringIO()):
                        got = m.precheck()
                self.assertEqual(got, baseline)
                self.assertEqual(cmd.call_args.args[:4],
                                 (sys.executable, str(m.VALIDATOR), "precheck", "--sites"))
                self.assertEqual(cmd.call_args.args[4], site)

    def test_no_repetir_despliegue_y_no_aceptar_recursos_ajenos(self):
        for site in SITES:
            with self.subTest(site=site):
                m = load(site)
                with mock.patch.object(m, "identity"), \
                     mock.patch.object(m.STATE, "exists", return_value=True), \
                     mock.patch.object(m.STATE, "is_symlink", return_value=False):
                    with self.assertRaisesRegex(RuntimeError, "ya existe"):
                        m.precheck()
                with mock.patch.object(m, "precheck", side_effect=RuntimeError("guard")), \
                     mock.patch.object(m, "write_state") as write, \
                     mock.patch.object(m, "cmd") as cmd:
                    with self.assertRaisesRegex(RuntimeError, "guard"):
                        m.up()
                    write.assert_not_called()
                    cmd.assert_not_called()

    def test_acciones_mutantes_exigen_confirmacion(self):
        for site in SITES:
            script = ROOT / f"scripts/laboratorio/s05-lacp-{site.lower()}-integracion.py"
            for action in ("up", "down"):
                with self.subTest(site=site, action=action):
                    p = subprocess.run([sys.executable, str(script), action],
                                       capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(p.returncode, 0)
                    self.assertIn("--confirm-isolated", p.stderr)

    def test_puertos_y_vlan_aislados_en_codigo(self):
        for site in SITES:
            with self.subTest(site=site):
                script = ROOT / f"scripts/laboratorio/s05-lacp-{site.lower()}-integracion.py"
                t = script.read_text(encoding="utf-8")
                self.assertIn('"mode", "802.3ad"', t)
                self.assertIn('"xmit_hash_policy", "layer3+4"', t)
                self.assertIn('"link", "set", SW_BOND, "master", "br0"', t)
                self.assertIn('"bridge", "vlan", "add", "dev", SW_BOND', t)
                self.assertIn('set_alias(SW, sw_dev, data)', t)
                self.assertIn('set_alias(CLIENT, client_dev, data)', t)
                self.assertIn('STATE.unlink()', t)
                self.assertNotIn('"docker", "restart"', t)
                self.assertNotIn('"systemctl", "restart"', t)
                self.assertNotIn('"link", "delete", "dev", "tr-sw"', t)
                self.assertNotIn('"ens33", "down"', t)

    def test_status_valida_ip_y_no_omite_check_services(self):
        for site in SITES:
            with self.subTest(site=site):
                m = load(site)
                data = {"status": "active", "alias": f"S05_{site}_abcdef0123456789",
                        "before": {"mgmt": {"x": 1}, "switch": {"ports": {}, "vlans": {}}}}
                with mock.patch.object(m, "netns", return_value={m.CLIENT}), \
                     mock.patch.object(m, "alias_of", return_value=data["alias"]), \
                     mock.patch.object(m, "ns_exec", return_value=f"{m.VID} PVID Egress Untagged"), \
                     mock.patch.object(m, "ip_ns", side_effect=[m.IP, f"default via {m.GW} dev bond0"]), \
                     mock.patch.object(m, "bond_ports") as bonds, \
                     mock.patch.object(m, "ping_verified") as ping, \
                     mock.patch.object(m, "management", return_value=data["before"]["mgmt"]), \
                     mock.patch.object(m, "assert_protected") as prot, \
                     mock.patch.object(m, "assert_services") as services, \
                     redirect_stdout(io.StringIO()):
                    m.status(data)
                self.assertEqual(bonds.call_count, 2)
                self.assertEqual(ping.call_count, 4)
                prot.assert_called_once()
                services.assert_called_once()


if __name__ == "__main__":
    unittest.main()
