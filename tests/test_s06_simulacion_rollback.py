"""Pruebas de seguridad S06-037: sin sudo, tc, systemd ni trafico."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PATH = Path(__file__).resolve().parents[1] / "scripts/s06/simular_rollback.py"
SPEC = importlib.util.spec_from_file_location("s06_simulacion_rollback", PATH)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class SimulatedRollbackTests(unittest.TestCase):
    def test_catalogo_de_estados(self):
        self.assertEqual(len(mod.CASES), 14)
        self.assertEqual(mod.TARGET["device"], "eth0")
        self.assertEqual(mod.TARGET["namespace"], "nl360-s02-h-hq-120")
        self.assertNotEqual(mod.TARGET["ip"], mod.MANAGEMENT["ip"])

    def test_todos_los_escenarios_reproducibles(self):
        for name in mod.CASES:
            with self.subTest(name=name):
                result = mod.run_case(name)
                self.assertEqual(result["outcome"], result["expected_outcome"])
                self.assertFalse(result["network_changes_executed"])
                self.assertFalse(result["real_rollback_implemented"])
                self.assertEqual(result["ground_truth_label"], "UNKNOWN")
                self.assertFalse(result["ground_truth_verified"])

    def test_watchdog_simulado_vencimiento(self):
        r = mod.run_case("expired_ttl")
        self.assertEqual(r["virtual_seconds"], 31)
        self.assertEqual(r["outcome"], "RESTORED")
        events = [e["event"] for e in r["events"]]
        self.assertIn("watchdog_deadline_reached", events)
        self.assertIn("owned_qdisc_restored_simulated", events)

    def test_caida_del_controlador_no_impide_rollback_logico(self):
        r = mod.run_case("controller_crash")
        self.assertEqual(r["outcome"], "RESTORED")
        self.assertIn("controller_crash_simulated",
                      [x["event"] for x in r["events"]])

    def test_ajeno_no_se_borra_ni_libera_lock(self):
        r = mod.run_case("foreign_owner")
        self.assertEqual(r["outcome"], "ESCALATED")
        self.assertEqual(r["qdisc_simulated"]["owner"], "another")
        self.assertIsNotNone(r["slot_owned"])
        self.assertIn("foreign_qdisc_not_deleted",
                      [x["event"] for x in r["events"]])

    def test_rollback_fallido_escalado(self):
        r = mod.run_case("rollback_failure")
        self.assertEqual(r["outcome"], "ESCALATED")
        self.assertTrue(r["slot_owned"])
        self.assertIn("rollback_failed_escalated",
                      [x["event"] for x in r["events"]])

    def test_tarea_sin_aprobacion_no_adquiere_lock(self):
        r = mod.run_case("no_approval")
        self.assertEqual(r["outcome"], "NEW")
        self.assertEqual(r["refusal"], "human_approval_required")
        self.assertIsNone(r["slot_owned"])

    def test_qdisc_inicial_ajena_rechazada(self):
        r = mod.run_case("wrong_qdisc")
        self.assertEqual(r["refusal"], "preexisting_qdisc_not_owned")

    def test_dispositivo_ens33_rechazado(self):
        r = mod.run_case("wrong_target")
        self.assertEqual(r["refusal"], "target_not_allowlisted")

    def test_gateway_gestion_diferente_rechazado(self):
        r = mod.run_case("wrong_management")
        self.assertEqual(r["refusal"], "management_not_in_reference")

    def test_ttl_3600_rechazado(self):
        r = mod.run_case("bad_ttl")
        self.assertEqual(r["refusal"], "ttl_out_of_policy")

    def test_no_puede_aplicar_sin_armar_watchdog(self):
        r = mod.run_case("watchdog_missing")
        self.assertEqual(r["refusal"], "must_arm_watchdog_before_apply")
        self.assertEqual(r["qdisc_simulated"]["kind"], "noqueue")

    def test_no_puede_ejecutar_dos_experimentos(self):
        r = mod.run_case("concurrency")
        self.assertEqual(r["refusal"], "active_operation_exists")

    def test_falla_de_aplicacion_aborta_y_libera(self):
        r = mod.run_case("apply_failure")
        self.assertEqual(r["outcome"], "ABORTED")
        self.assertEqual(r["qdisc_simulated"]["kind"], "noqueue")
        self.assertIsNone(r["slot_owned"])

    def test_rollback_idempotente(self):
        r = mod.run_case("double_restore")
        self.assertEqual(r["outcome"], "RESTORED")
        self.assertEqual(
            [x["event"] for x in r["events"]].count("owned_qdisc_restored_simulated"), 1
        )

    def test_armado_fallido_impide_cambio(self):
        obj = mod.Trial()
        obj.approve()
        obj.arm_watchdog(success=False)
        self.assertEqual(obj.state, "ABORTED")
        self.assertEqual(obj.effective_qdisc["kind"], "noqueue")
        self.assertIsNone(obj.slot.owner)

    def test_antes_del_ttl_no_restaura(self):
        obj = mod.Trial()
        obj.approve(ttl=30)
        obj.arm_watchdog()
        obj.apply()
        obj.advance(29)
        self.assertEqual(obj.state, "ACTIVE")
        obj.advance(1)
        self.assertEqual(obj.state, "RESTORED")

    def test_reject_negativo_reloj_virtual(self):
        obj = mod.Trial()
        with self.assertRaises(ValueError):
            obj.advance(-1)

    def test_rechaza_resultado_no_etiquetado_como_ground_truth(self):
        r = mod.run_case("success")
        self.assertFalse(r["ground_truth_verified"])
        self.assertEqual(r["ground_truth_label"], "UNKNOWN")

    def test_seguridad_sin_subprocess_o_red_en_programa(self):
        source = PATH.read_text()
        for phrase in ("subprocess.run(", "os.system(", "shell=True",
                       "qdisc add", "qdisc del", "qdisc replace"):
            self.assertNotIn(phrase, source)

    def test_reporte_serializable_y_privado(self):
        with tempfile.TemporaryDirectory() as directory:
            r = mod.run_case("expired_ttl")
            out = Path(directory) / "report.json"
            out.write_text(json.dumps(r))
            data = json.loads(out.read_text())
            self.assertFalse(data["real_rollback_implemented"])
            self.assertEqual(data["outcome"], "RESTORED")


if __name__ == "__main__":
    unittest.main()
