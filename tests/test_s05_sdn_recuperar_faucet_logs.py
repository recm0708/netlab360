"""Tests sin sudo del rescate selectivo de Faucet existente."""
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
PATH = ROOT / "scripts/laboratorio/s05_sdn_recuperar_faucet_logs.py"
spec = importlib.util.spec_from_file_location("s05_recover_faucet_logs", PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestFaucetLogRecovery(unittest.TestCase):
    def test_recover_requiere_confirmacion(self):
        result = subprocess.run([sys.executable, str(PATH), "recover"],
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--confirm-recovery", result.stderr)

    def test_preflight_no_toca_recursos_si_estado_no_es_parcial(self):
        with mock.patch.object(module.lab, "state_read",
                               return_value={"status": "active"}), \
             mock.patch.object(module.lab, "root") as root:
            with self.assertRaisesRegex(RuntimeError, "needs_inspection"):
                module.preflight()
        root.assert_not_called()

    def test_preflight_no_toca_contenedor_de_otro_propietario(self):
        with mock.patch.object(module.lab, "state_read", return_value={
                    "status": "needs_inspection", "image": module.lab.IMAGE
                }), \
             mock.patch.object(module.lab, "owned_bridge", return_value=True), \
             mock.patch.object(module.lab, "owned_controller", return_value=False), \
             mock.patch.object(module.lab, "root") as root:
            with self.assertRaisesRegex(RuntimeError, "Propiedad SDN"):
                module.preflight()
        root.assert_not_called()

    def test_recover_solo_chown_chmod_docker_start_sobre_contenedor_existente(self):
        state = {"owner": module.lab.OWNER, "bridge": module.lab.BRIDGE,
                 "status": "needs_inspection", "error": "old"}
        container = {"State": {"Running": False}}
        with mock.patch.object(module, "preflight", return_value=(state, container)), \
             mock.patch.object(module.lab, "root") as root, \
             mock.patch.object(module.lab, "ovs", return_value="true"), \
             mock.patch.object(module.lab, "status") as status, \
             mock.patch.object(module.lab, "state_write") as save, \
             redirect_stdout(io.StringIO()) as out:
            module.recover()
        actions = [call.args[:2] for call in root.call_args_list]
        self.assertEqual(actions, [("chown", f"0:{module.os.getgid()}"),
                                   ("chmod", "0750"),
                                   ("docker", "start")])
        self.assertEqual(root.call_args_list[2].args[2], module.lab.CONTROLLER)
        status.assert_called_once_with(allow_recovery=True)
        save.assert_called_once()
        self.assertEqual(state["status"], "active")
        self.assertNotIn("error", state)
        self.assertEqual(state["recovery"]["previous_error"], "old")
        self.assertIn("S05_SDN_RECOVERY=OK_SIN_RECREAR_RECURSOS",
                      out.getvalue())

    def test_no_declarar_active_si_falla_openflow(self):
        state = {"status": "needs_inspection"}
        with mock.patch.object(module, "preflight",
                               return_value=(state, {"State": {"Running": True}})), \
             mock.patch.object(module.lab, "root") as root, \
             mock.patch.object(module.lab, "ovs", return_value="false"), \
             mock.patch.object(module.time, "sleep"), \
             mock.patch.object(module.lab, "state_write") as save:
            with self.assertRaisesRegex(RuntimeError, "no conectó"):
                module.recover()
        self.assertEqual(state["status"], "needs_inspection")
        save.assert_not_called()
        self.assertFalse(any(c.args[:2] == ("docker", "start")
                             for c in root.call_args_list))

    def test_no_declarar_active_si_no_pasan_pings_o_fib(self):
        state = {"status": "needs_inspection"}
        with mock.patch.object(module, "preflight",
                               return_value=(state, {"State": {"Running": True}})), \
             mock.patch.object(module.lab, "root"), \
             mock.patch.object(module.lab, "ovs", return_value="true"), \
             mock.patch.object(module.lab, "status",
                               side_effect=RuntimeError("aislamiento fallido")) as status, \
             mock.patch.object(module.time, "sleep"), \
             mock.patch.object(module.lab, "state_write") as save:
            with self.assertRaisesRegex(RuntimeError, "NO validado"):
                module.recover()
        self.assertEqual(status.call_count, 3)
        self.assertEqual(state["status"], "needs_inspection")
        save.assert_not_called()

    def test_status_normal_sigue_rechazando_estado_parcial(self):
        with mock.patch.object(module.lab, "state_read",
                               return_value={"status": "needs_inspection"}), \
             mock.patch.object(module.lab, "owned_bridge") as owned:
            with self.assertRaisesRegex(RuntimeError, "parcial"):
                module.lab.status()
        owned.assert_not_called()

    def test_codigo_no_elimina_ni_recrea_red(self):
        content = PATH.read_text(encoding="utf-8")
        for prohibited in ('"docker", "rm"', '"docker", "restart"',
                           '"add-br"', '"del-br"', '"netns", "delete"',
                           '"ip", "link", "delete"', '"systemctl", "restart"'):
            self.assertNotIn(prohibited, content)
        self.assertIn("Permission denied: '/var/log/faucet/faucet.log'", content)
        self.assertIn('lab.status(allow_recovery=True)', content)


if __name__ == "__main__":
    unittest.main()
