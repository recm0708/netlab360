"""Contratos offline del dominio SDN S05. Ningún test requiere sudo ni instala puentes."""
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
PATH = ROOT / "scripts/laboratorio/s05_sdn_ovs_faucet_aislado.py"
spec = importlib.util.spec_from_file_location("s05_sdn_isolated", PATH)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestS05SDNIsolated(unittest.TestCase):
    def test_identidad_y_recursos_estrictos(self):
        self.assertEqual(module.BRIDGE, "br-s05-sdn")
        self.assertEqual(module.DPID, "0000000000000505")
        self.assertEqual(module.CONTROL_PORT, 16653)
        self.assertEqual(module.OWNER, "NETLAB360_S05_SDN_V1")
        self.assertEqual(set(module.NS), {"a", "b", "c"})
        self.assertEqual(
            {row[2] for row in module.HOSTS.values()}, {1, 2, 3})
        self.assertEqual(
            {row[3] for row in module.HOSTS.values()},
            {"198.18.41.11/24", "198.18.41.12/24", "198.18.41.13/24"})
        self.assertTrue(module.IMAGE.startswith("faucet/faucet@sha256:"))

    def test_plan_es_solo_lectura(self):
        with mock.patch.object(module, "run") as process, redirect_stdout(io.StringIO()) as out:
            module.plan()
        process.assert_not_called()
        self.assertIn("S05_SDN_PLAN=NO_MODIFICAR_ENS33_FRR_WAN_LACP_HA", out.getvalue())

    def test_cualquier_mutacion_requiere_confirmacion(self):
        for action in ("up", "down"):
            with self.subTest(action=action):
                result = subprocess.run([sys.executable, str(PATH), action],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("--confirm-isolated", result.stderr)

    def test_precheck_sin_recursos_ajenos(self):
        before = {"management": {"ens33": "UP", "route": "via"},
                  "docker": sorted(module.FRR), "namespaces": []}
        with mock.patch.object(module, "STATE",
                               mock.Mock(exists=lambda: False, is_symlink=lambda: False)), \
             mock.patch.object(module, "CONFIG",
                               mock.Mock(is_file=lambda: True, is_symlink=lambda: False)), \
             mock.patch.object(module, "LOGDIR",
                               mock.Mock(is_dir=lambda: True, is_symlink=lambda: False)), \
             mock.patch.object(module, "check_image"), \
             mock.patch.object(module, "baseline", return_value=before), \
             mock.patch.object(module, "ovs", return_value=""), \
             mock.patch.object(module, "link_names", return_value=set()), \
             mock.patch.object(module, "namespaces", return_value=set()), \
             mock.patch.object(module, "docker_all_names", return_value=set()), \
             mock.patch.object(module, "root", return_value=mock.Mock(stdout="")), \
             redirect_stdout(io.StringIO()) as out:
            got = module.precheck()
        self.assertIs(got, before)
        self.assertIn("S05_SDN_PRECHECK=OK_SIN_CAMBIOS", out.getvalue())

    def test_precheck_rechaza_estado_preexistente(self):
        with mock.patch.object(module, "STATE",
                               mock.Mock(exists=lambda: True, is_symlink=lambda: False)), \
             mock.patch.object(module, "root") as privileged:
            with self.assertRaisesRegex(RuntimeError, "Ya existe estado"):
                module.precheck()
        privileged.assert_not_called()

    def test_precheck_rechaza_puerto_sdn_ya_ocupado(self):
        before = {"management": {}, "docker": sorted(module.FRR), "namespaces": []}
        with mock.patch.object(module, "STATE",
                               mock.Mock(exists=lambda: False, is_symlink=lambda: False)), \
             mock.patch.object(module, "CONFIG",
                               mock.Mock(is_file=lambda: True, is_symlink=lambda: False)), \
             mock.patch.object(module, "LOGDIR",
                               mock.Mock(is_dir=lambda: True, is_symlink=lambda: False)), \
             mock.patch.object(module, "check_image"), \
             mock.patch.object(module, "baseline", return_value=before), \
             mock.patch.object(module, "ovs", return_value=""), \
             mock.patch.object(module, "link_names", return_value={"sdna0"}), \
             mock.patch.object(module, "root") as privileged:
            with self.assertRaisesRegex(RuntimeError, "Dispositivos ocupados"):
                module.precheck()
        privileged.assert_not_called()

    def test_up_escribe_estado_antes_de_crear_contenedor(self):
        before = {"management": {"ens33": "UP"}, "docker": [], "namespaces": []}
        with mock.patch.object(module, "precheck", return_value=before), \
             mock.patch.object(module, "state_write") as write, \
             mock.patch.object(module, "root", side_effect=RuntimeError("bloqueado")) as root:
            with self.assertRaisesRegex(RuntimeError, "bloqueado"):
                module.up()
        self.assertEqual(write.call_count, 2)
        self.assertTrue(write.call_args_list[0].kwargs["exclusive"])
        self.assertEqual(write.call_args_list[0].args[0]["owner"], module.OWNER)
        self.assertEqual(write.call_args_list[-1].args[0]["status"],
                         "needs_inspection")
        root.assert_called_once()

    def test_status_parcial_rechaza_aceptacion(self):
        with mock.patch.object(module, "state_read",
                               return_value={"status": "needs_inspection"}), \
             mock.patch.object(module, "root") as privileged:
            with self.assertRaisesRegex(RuntimeError, "parcial"):
                module.status()
        privileged.assert_not_called()

    def test_ping_aislado_solo_acepta_rc_uno(self):
        with mock.patch.object(module, "root",
                               return_value=mock.Mock(returncode=1)) as privileged, \
             redirect_stdout(io.StringIO()) as out:
            module.ping("a", "198.18.41.13", expect_success=False)
        privileged.assert_called_once()
        self.assertIn("=BLOQUEADO", out.getvalue())

    def test_ping_aislado_rechaza_rc_dos(self):
        with mock.patch.object(module, "root",
                               return_value=mock.Mock(returncode=2)) as privileged, \
             mock.patch.object(module.time, "sleep"), \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "no validada"):
                module.ping("a", "198.18.41.13", expect_success=False)
        self.assertEqual(privileged.call_count, 2)

    def test_borrado_rechaza_bridge_ajeno(self):
        with mock.patch.object(module, "state_read",
                               return_value={"owner": module.OWNER, "before": {}}), \
             mock.patch.object(module, "owned_bridge",
                               side_effect=RuntimeError("otro propietario")), \
             mock.patch.object(module, "root") as privileged:
            with self.assertRaisesRegex(RuntimeError, "otro propietario"):
                module.down()
        privileged.assert_not_called()

    def test_codigo_no_menciona_interfaces_gestion_para_bajarlas(self):
        text = PATH.read_text(encoding="utf-8")
        self.assertNotIn('link", "set", "ens33"', text)
        self.assertNotIn('"systemctl", "restart"', text)
        self.assertNotIn('"docker", "restart"', text)
        self.assertNotIn('"ovs", "del-br", "br0"', text)
        self.assertIn('"fail_mode=secure"', text)
        self.assertIn('"protocols=OpenFlow13"', text)
        self.assertIn('"external_ids:netlab360-owner=" + OWNER', text)


if __name__ == "__main__":
    unittest.main()
