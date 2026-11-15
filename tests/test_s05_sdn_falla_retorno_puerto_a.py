"""Pruebas offline del ensayo SDN de enlace A sin tocar redes reales."""
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
SCRIPT = ROOT / "scripts/laboratorio/s05-sdn-falla-retorno-puerto-a.py"
spec = importlib.util.spec_from_file_location("s05_sdn_fault_a", SCRIPT)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestS05SDNLinkFault(unittest.TestCase):
    def test_only_sdna0_is_target(self):
        self.assertEqual(mod.PORT, "sdna0")
        self.assertEqual(mod.lab.BRIDGE, "br-s05-sdn")
        self.assertEqual(mod.RESCUE_SECONDS, 120)
        self.assertEqual(set(mod.SERVICES), {
            "netlab360-s04-exporter", "netlab360-s05-noc",
            "netlab360-s05-ha-backend-hq", "netlab360-s05-ha-backend-s1",
            "netlab360-s05-ha-frontal-hq", "netlab360-s05-ha-monitor-s2"})

    def test_run_exige_confirmacion(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "run"],
                           text=True, capture_output=True, timeout=12)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--confirm-fault", p.stderr)

    def test_precheck_frena_estado_parcial_antes_de_mutar(self):
        with mock.patch.object(mod.lab, "state_read",
                               return_value={"status": "needs_inspection"}), \
             mock.patch.object(mod.lab, "root") as root:
            with self.assertRaisesRegex(RuntimeError, "no esta activo"):
                mod.precheck()
        root.assert_not_called()

    def test_precheck_frena_puertos_ajenos(self):
        with mock.patch.object(mod.lab, "state_read",
                               return_value={"status": "active"}), \
             mock.patch.object(mod.lab, "owned_bridge", return_value=True), \
             mock.patch.object(mod.lab, "owned_controller", return_value=True), \
             mock.patch.object(mod.lab, "ovs", return_value="sdna0\nsdnb0\nsdnc0\nens33"), \
             mock.patch.object(mod.lab, "root") as root:
            with self.assertRaisesRegex(RuntimeError, "Puertos OVS ajenos"):
                mod.precheck()
        root.assert_not_called()

    def test_precheck_estado_correcto_solo_consultas(self):
        baseline = {"status": "active", "before": {"management": {},
                    "docker": [], "namespaces": []}}
        with mock.patch.object(mod.lab, "state_read", return_value=baseline), \
             mock.patch.object(mod.lab, "owned_bridge", return_value=True), \
             mock.patch.object(mod.lab, "owned_controller", return_value=True), \
             mock.patch.object(mod.lab, "ovs",
                               side_effect=["sdna0\nsdnb0\nsdnc0", "1"]), \
             mock.patch.object(mod, "device_up", return_value=True), \
             mock.patch.object(mod.shutil, "which", return_value="/usr/bin/ip"), \
             mock.patch.object(mod.lab, "root",
                               return_value=mock.Mock(stdout="")) as root, \
             mock.patch.object(mod.lab, "status") as status, \
             mock.patch.object(mod, "protected_services") as services, \
             redirect_stdout(io.StringIO()) as out:
            result = mod.precheck()
        self.assertIs(result, baseline)
        status.assert_called_once()
        services.assert_called_once_with(baseline)
        self.assertIn("S05_SDN_FAULT_PRECHECK=OK", out.getvalue())
        self.assertEqual(root.call_args.args[:2], ("systemctl", "list-timers"))

    def test_arm_restore_only_timer(self):
        with mock.patch.object(mod.shutil, "which", return_value="/usr/sbin/ip"), \
             mock.patch.object(mod.secrets, "token_hex", return_value="abc123"), \
             mock.patch.object(mod.lab, "root") as root:
            name = mod.failsafe_arm()
        self.assertEqual(name, mod.RESCUE_PREFIX + "abc123")
        command = root.call_args.args
        self.assertEqual(command[:2], ("systemd-run", "--unit"))
        self.assertIn("--on-active=120s", command)
        self.assertEqual(command[-6:], ("/usr/sbin/ip", "link", "set", "dev", "sdna0", "up"))

    def test_no_muta_si_precheck_falla(self):
        with mock.patch.object(mod, "precheck", side_effect=RuntimeError("frenar")), \
             mock.patch.object(mod.lab, "root") as root:
            with self.assertRaisesRegex(RuntimeError, "frenar"):
                mod.run_fault()
        root.assert_not_called()

    def test_error_en_falla_restaura_puerto_y_conserva_watchdog_si_postcheck_falla(self):
        data = {"status": "active", "before": {}}
        with mock.patch.object(mod, "precheck", return_value=data), \
             mock.patch.object(mod, "failsafe_arm", return_value="rescue"), \
             mock.patch.object(mod, "device_up", side_effect=[True, False, True]), \
             mock.patch.object(mod.lab, "owned_bridge", return_value=True), \
             mock.patch.object(mod.lab, "ovs", return_value="sdna0\nsdnb0\nsdnc0"), \
             mock.patch.object(mod.lab, "root") as root, \
             mock.patch.object(mod.icmp, "measure", side_effect=RuntimeError("sin respuesta")), \
             mock.patch.object(mod.lab, "status", side_effect=RuntimeError("pipeline aun no recobra")), \
             mock.patch.object(mod.time, "sleep"), \
             mock.patch.object(mod, "failsafe_cancel") as cancel, \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "incompleta"):
                mod.run_fault()
        directions = [c.args[-1] for c in root.call_args_list]
        self.assertEqual(directions, ["down", "up"])
        cancel.assert_not_called()

    def test_script_no_reinstala_o_elimina_recursos(self):
        src = SCRIPT.read_text()
        for forbidden in ('"docker", "restart"', '"docker", "stop"',
                          '"docker", "rm"', '"docker", "run"',
                          '"ovs", "del-br"', '"ovs", "add-br"',
                          '"netns", "delete"', '"ens33", "down"'):
            self.assertNotIn(forbidden, src)
        self.assertIn("lab.status()", src)
        self.assertIn("failsafe_arm()", src)
        self.assertIn("failsafe_cancel(rescue)", src)


if __name__ == "__main__":
    unittest.main()
