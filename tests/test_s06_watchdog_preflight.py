"""S06-036: pruebas offline del temporizador protegido, sin llamar systemd."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

TARGET = Path(__file__).resolve().parents[1] / "scripts/s06/verificar_watchdog.py"
SPEC = importlib.util.spec_from_file_location("s06_watchdog_preflight", TARGET)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

UNIT = "netlab360-s06-wd-probe-1234abcd"


class WatchdogPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.patch_base = mock.patch.object(mod, "BASE", self.base)
        self.patch_base.start()
        self.addCleanup(self.patch_base.stop)
        (self.base / "watchdog-tests").mkdir()

    def marker(self, name="wd_1234abcd.ready"):
        return self.base / "watchdog-tests" / name

    def test_timer_usa_solo_touch(self):
        args = mod.build_timer_args(UNIT, self.marker())
        self.assertEqual(args[:3], ["sudo", "-n", "systemd-run"])
        self.assertEqual(args[-2:], ["/usr/bin/touch", str(self.marker())])
        self.assertIn("--on-active=3s", args)
        self.assertIn("--timer-property=AccuracySec=1s", args)
        self.assertNotIn("bash", args)
        self.assertNotIn("tc", args)

    def test_unidad_de_arbitraje_rechaza_texto_arbitrario(self):
        with self.assertRaises(ValueError):
            mod.build_timer_args("../../../malicious", self.marker())

    def test_unidad_rechaza_opciones_inyectadas(self):
        with self.assertRaises(ValueError):
            mod.build_timer_args("--exec=/bin/sh", self.marker())

    def test_marcador_fuera_de_raiz_rechazado(self):
        with self.assertRaises(ValueError):
            mod.build_timer_args(UNIT, self.base / "wd_1234abcd.ready")

    def test_marcador_con_slash_rechazado(self):
        with self.assertRaises(ValueError):
            mod.build_timer_args(UNIT, self.marker("../wd_1234abcd.ready"))

    def test_marcador_existente_rechazado(self):
        self.marker().touch()
        with self.assertRaisesRegex(ValueError, "preexistente"):
            mod.build_timer_args(UNIT, self.marker())

    def test_marcador_symlink_rechazado(self):
        self.marker().symlink_to(self.base / "archivo_ajeno")
        with self.assertRaises(ValueError):
            mod.build_timer_args(UNIT, self.marker())

    def test_noqueue_candidato(self):
        self.assertEqual(mod.classify_qdisc([{
            "kind": "noqueue", "root": True, "handle": "0:"
        }]), "CANDIDATE_NOQUEUE")

    def test_netem_previo_bloquea(self):
        self.assertEqual(mod.classify_qdisc([{
            "kind": "netem", "root": True
        }]), "BLOCKED_NETEM_PRESENT")

    def test_qdisc_ajena_bloquea(self):
        self.assertEqual(mod.classify_qdisc([{
            "kind": "fq_codel", "root": True
        }]), "BLOCKED_QDISC_NOT_NOQUEUE")

    def test_qdisc_invalido_rechazado(self):
        with self.assertRaises(ValueError):
            mod.classify_qdisc({})

    def test_qdisc_root_ambiguo_rechazado(self):
        self.assertEqual(mod.classify_qdisc([
            {"kind": "noqueue", "root": True},
            {"kind": "noqueue", "root": True}
        ]), "BLOCKED_QDISC_NOT_NOQUEUE")

    def test_reporte_no_agrega_ordenes_mutantes(self):
        folder = self.base / "report"
        folder.mkdir()
        mod.write_report(folder, {
            "timer_fired": True,
            "qdisc_mutation_allowed": False,
            "network_change_executed": False,
        })
        saved = json.loads(
            (folder / "S06_036_Resultado_Watchdog.json").read_text()
        )
        self.assertFalse(saved["network_change_executed"])

    def test_consulta_falla_si_gestion_alterada(self):
        values = {
            "git": "",
            "addr": "2: ens33 inet 192.168.47.41/24",
            "route": "default via 192.168.47.2 dev ens33",
        }
        def fake(args):
            if args[0] == "git":
                return values["git"]
            if args[:3] == ["ip", "-4", "-o"]:
                return values["addr"]
            if args[:4] == ["ip", "-4", "route", "show"]:
                return values["route"]
            raise AssertionError("Consulta adicional inesperada")
        with mock.patch.object(mod, "get_output", side_effect=fake):
            with mock.patch.object(mod.os, "geteuid", return_value=1000):
                with self.assertRaisesRegex(RuntimeError, "administrativa"):
                    mod.check_read_only()

    def test_timer_real_no_se_ejecuta_al_importar(self):
        # La importacion y los tests no deben lanzar systemd ni tc.
        self.assertTrue(callable(mod.main))
        self.assertEqual(mod.NS, "nl360-s02-h-hq-120")
        self.assertEqual(mod.DEVICE, "eth0")

    def test_run_no_usa_shell(self):
        with mock.patch.object(mod.subprocess, "run",
                               return_value=subprocess.CompletedProcess([], 0, "ok", "")) as runner:
            response = mod.run(["echo", "ok"])
        self.assertEqual(response.returncode, 0)
        self.assertFalse(runner.call_args.kwargs.get("shell", False))


if __name__ == "__main__":
    unittest.main()
