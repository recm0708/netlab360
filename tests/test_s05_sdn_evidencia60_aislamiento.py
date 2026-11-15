"""Evidencia 60: el aislamiento solo se acredita si ping sale RC=1 con 100% de pérdida."""
from __future__ import annotations
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/validacion/s05-sdn-evidencia60-aislamiento.py"
spec = importlib.util.spec_from_file_location("s05_evidencia60", PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fake(rc, received):
    return subprocess.CompletedProcess(["ping"], rc,
            f"--- x ping statistics ---\n2 packets transmitted, {received} received, " +
            ("0" if received == 2 else "100") + "% packet loss, time 1000ms\n", "")


class TestS05SDNEvidencia60(unittest.TestCase):
    def test_negativa_real_rc1_y_100porciento(self):
        with mock.patch.object(module.subprocess, "run", return_value=fake(1, 0)) as run, \
             redirect_stdout(io.StringIO()) as out:
            module.measure("a", "198.18.41.13", allowed=False)
        self.assertIn("DENEGADO_RC_1", out.getvalue())
        self.assertIn("-w", run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs["timeout"], 20)
        self.assertNotIn("timeout", run.call_args.args[0])

    def test_iputils_reporta_diez_intentos_y_diez_errores_arp(self):
        real = subprocess.CompletedProcess(
            ["ping"], 1,
            "--- 198.18.41.13 ping statistics ---\n"
            "10 packets transmitted, 0 received, +10 errors, 100% packet loss, time 3088ms\n"
            "pipe 10\n", "")
        with mock.patch.object(module.subprocess, "run", return_value=real), \
             redirect_stdout(io.StringIO()) as out:
            module.measure("a", "198.18.41.13", allowed=False)
        self.assertIn("RESUMEN=10 transmitidos, 0 recibidos, 100% pérdida; RC=1", out.getvalue())
        self.assertIn("DENEGADO_RC_1", out.getvalue())

    def test_iputils_errores_arp_no_permiten_aceptar_rc124(self):
        bad = subprocess.CompletedProcess(
            ["ping"], 124,
            "10 packets transmitted, 0 received, +10 errors, 100% packet loss, time 3000ms\n", "")
        with mock.patch.object(module.subprocess, "run", return_value=bad), \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "Aislamiento NO acreditado"):
                module.measure("a", "198.18.41.13", allowed=False)

    def test_dos_intentos_minimos_requeridos_en_denegacion(self):
        bad = subprocess.CompletedProcess(
            ["ping"], 1,
            "1 packets transmitted, 0 received, 100% packet loss, time 100ms\n", "")
        with mock.patch.object(module.subprocess, "run", return_value=bad), \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "fuera de rango"):
                module.measure("a", "198.18.41.13", allowed=False)

    def test_rc124_no_es_evidencia_de_denegacion(self):
        with mock.patch.object(module.subprocess, "run", return_value=fake(124, 0)), \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "Aislamiento NO acreditado"):
                module.measure("a", "198.18.41.13", allowed=False)

    def test_rc2_no_es_evidencia_de_denegacion(self):
        with mock.patch.object(module.subprocess, "run", return_value=fake(2, 0)), \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "Aislamiento NO acreditado"):
                module.measure("c", "198.18.41.11", allowed=False)

    def test_rc1_no_basta_si_tiene_respuestas(self):
        with mock.patch.object(module.subprocess, "run", return_value=fake(1, 2)), \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "Aislamiento NO acreditado"):
                module.measure("c", "198.18.41.11", allowed=False)

    def test_permitida_exige_2_de_2(self):
        with mock.patch.object(module.subprocess, "run", return_value=fake(0, 2)), \
             redirect_stdout(io.StringIO()) as out:
            module.measure("a", "198.18.41.12", allowed=True)
        self.assertIn("PERMITIDO_RC_0", out.getvalue())

    def test_timeout_de_python_falla_cerrado(self):
        with mock.patch.object(module.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired(["ping"], 20)), \
             redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "NO aceptar bloqueo"):
                module.measure("a", "198.18.41.13", allowed=False)

    def test_todos_los_destinos_son_del_dominio(self):
        with mock.patch.object(module.subprocess, "run") as run:
            with self.assertRaisesRegex(ValueError, "Objetivo no pertenece"):
                module.measure("a", "192.168.47.40", allowed=True)
        run.assert_not_called()

    def test_main_bloquea_estado_no_activo(self):
        with mock.patch.object(module.lab, "state_read",
                               return_value={"status": "needs_inspection"}), \
             mock.patch.object(module, "measure") as ping:
            with self.assertRaisesRegex(RuntimeError, "no está activo"):
                module.main()
        ping.assert_not_called()

    def test_main_marca_ok_solo_con_tres_pings_verificados(self):
        with mock.patch.object(module.lab, "state_read",
                               return_value={"status": "active"}), \
             mock.patch.object(module.lab, "owned_bridge", return_value=True), \
             mock.patch.object(module.lab, "owned_controller", return_value=True), \
             mock.patch.object(module.lab, "status") as status, \
             mock.patch.object(module, "measure") as measure, \
             redirect_stdout(io.StringIO()) as out:
            module.main()
        self.assertEqual(status.call_count, 2)
        self.assertEqual(measure.call_count, 3)
        self.assertEqual(measure.call_args_list[0].args,
                         ("a", "198.18.41.12"))
        self.assertIn("FIN_CAPTURA_S05_60", out.getvalue())
        self.assertIn("S05_SDN_CAPTURA60=OK", out.getvalue())

    def test_main_interrumpe_sin_marcador_fin_si_prueba_falla(self):
        with mock.patch.object(module.lab, "state_read",
                               return_value={"status": "active"}), \
             mock.patch.object(module.lab, "owned_bridge", return_value=True), \
             mock.patch.object(module.lab, "owned_controller", return_value=True), \
             mock.patch.object(module.lab, "status"), \
             mock.patch.object(module, "measure",
                               side_effect=[None, RuntimeError("unreachable")]), \
             redirect_stdout(io.StringIO()) as out:
            with self.assertRaisesRegex(RuntimeError, "unreachable"):
                module.main()
        self.assertNotIn("FIN_CAPTURA_S05_60", out.getvalue())
        self.assertNotIn("S05_SDN_CAPTURA60=OK", out.getvalue())


if __name__ == "__main__":
    unittest.main()
