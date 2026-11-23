"""Pruebas offline de las sondas de rendimiento S06, sin sudo ni trafico."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts/s06/medir_rendimiento.py"
SPEC = importlib.util.spec_from_file_location("s06_rendimiento", TARGET)
assert SPEC is not None and SPEC.loader is not None
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

PING = """PING 10.71.20.20 (10.71.20.20) 56(84) bytes of data.
64 bytes from 10.71.20.20: icmp_seq=1 ttl=62 time=1.000 ms
64 bytes from 10.71.20.20: icmp_seq=2 ttl=62 time=2.000 ms
64 bytes from 10.71.20.20: icmp_seq=3 ttl=62 time=3.000 ms
64 bytes from 10.71.20.20: icmp_seq=4 ttl=62 time=4.000 ms
64 bytes from 10.71.20.20: icmp_seq=5 ttl=62 time=5.000 ms

--- 10.71.20.20 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 1000ms
rtt min/avg/max/mdev = 1.000/3.000/5.000/1.414 ms
"""

PING_LOSS = """PING 10.72.20.20 (10.72.20.20)
64 bytes from 10.72.20.20: icmp_seq=1 ttl=62 time=1.2 ms
64 bytes from 10.72.20.20: icmp_seq=3 ttl=62 time=3.2 ms

--- 10.72.20.20 ping statistics ---
5 packets transmitted, 2 received, 60% packet loss, time 1000ms
rtt min/avg/max/mdev = 1.200/2.200/3.200/1.000 ms
"""

PING_ZERO = """PING 10.72.20.20 (10.72.20.20)

--- 10.72.20.20 ping statistics ---
5 packets transmitted, 0 received, 100% packet loss, time 1000ms
"""

HTTP = {
    "http_status": 200, "elapsed_ms": 12.123,
    "service": "netlab360-s05-ha", "role": "frontend",
    "availability": "available", "active_backend": "BACKEND_HQ",
    "selected_path": "local_backend",
}


class PerformanceObservationalTests(unittest.TestCase):
    def test_catalogo_permitido(self):
        self.assertEqual(len(mod.PROBES), 3)
        self.assertEqual(mod.HTTP_NS, "nl360-s02-h-s2-320")
        self.assertEqual(mod.HTTP_ENDPOINT,
                         "http://10.70.20.23:8080/api/v1/service")
        self.assertFalse(any("ens33" in str(x) for x in mod.PROBES))

    def test_ping_sano_y_p95(self):
        result = mod.parse_ping(PING, 5, 0)
        self.assertEqual((result["sent"], result["received"]), (5, 5))
        self.assertEqual(result["loss_pct"], 0)
        self.assertAlmostEqual(result["rtt_p95_ms"], 4.8, places=3)
        self.assertTrue(result["measurement_valid"])

    def test_ping_perdidas_reales_no_errores_de_parseo(self):
        result = mod.parse_ping(PING_LOSS, 5, 1)
        self.assertEqual(result["loss_pct"], 60)
        self.assertEqual(result["received"], 2)
        self.assertEqual(result["rtt_p95_ms"], 3.1)

    def test_ping_cero_respuestas_es_valor_observado(self):
        result = mod.parse_ping(PING_ZERO, 5, 1)
        self.assertEqual(result["loss_pct"], 100)
        self.assertIsNone(result["rtt_p95_ms"])
        self.assertIsNone(result["rtt_avg_ms"])
        self.assertTrue(result["measurement_valid"])

    def test_ping_sin_resumen_rechazado(self):
        with self.assertRaisesRegex(ValueError, "resumen"):
            mod.parse_ping("timeout", 5, 1)

    def test_ping_exitcode_anormal_rechazado(self):
        with self.assertRaisesRegex(ValueError, "completar"):
            mod.parse_ping(PING, 5, 2)

    def test_ping_contador_alterado_rechazado(self):
        with self.assertRaisesRegex(ValueError, "inconsistencia"):
            mod.parse_ping(PING.replace("5 packets transmitted", "6 packets transmitted"), 5, 0)

    def test_ping_sin_muestras_rtt_rechazado(self):
        with self.assertRaisesRegex(ValueError, "RTT por paquete"):
            mod.parse_ping(PING.replace("icmp_seq=3", "icmp_n=3"), 5, 0)

    def test_http_contrato_valido(self):
        result = mod.parse_http(json.dumps(HTTP))
        self.assertEqual(result["active_backend"], "BACKEND_HQ")
        self.assertEqual(result["elapsed_ms"], 12.123)

    def test_http_rechaza_servicio_ajeno(self):
        invalid = dict(HTTP, service="otro-servicio")
        with self.assertRaisesRegex(ValueError, "contrato"):
            mod.parse_http(json.dumps(invalid))

    def test_http_rechaza_duracion_numerica_no_finita(self):
        invalid = dict(HTTP, elapsed_ms=float("inf"))
        with self.assertRaisesRegex(ValueError, "Tiempo"):
            mod.parse_http(json.dumps(invalid))

    def test_limites_acotados(self):
        mod.validate_limits(3, 5, 1)
        for args in ((0, 5, 1), (9, 5, 1), (3, 1, 1), (3, 11, 1),
                     (3, 5, -1), (3, 5, 11)):
            with self.subTest(params=args):
                with self.assertRaises(ValueError):
                    mod.validate_limits(*args)

    def test_medicion_no_asigna_etiqueta_supervisada(self):
        result = subprocess.CompletedProcess(["ping"], 0, stdout=PING, stderr="")
        with mock.patch.object(mod, "run", return_value=result):
            obs = mod.measure_ping(mod.PROBES[0], 5)
        self.assertTrue(obs["result"]["measurement_valid"])
        self.assertEqual(obs["ground_truth_label"], "UNKNOWN")
        self.assertFalse(obs["ground_truth_verified"])

    def test_medicion_con_perdida_no_infiere_causa(self):
        result = subprocess.CompletedProcess(["ping"], 1, stdout=PING_LOSS, stderr="")
        with mock.patch.object(mod, "run", return_value=result):
            obs = mod.measure_ping(mod.PROBES[0], 5)
        self.assertTrue(obs["result"]["measurement_valid"])
        self.assertIn("observed_packet_loss_not_ground_truth",
                      obs["quality_warnings"])
        self.assertEqual(obs["ground_truth_label"], "UNKNOWN")

    def test_http_medicion_observacional(self):
        result = subprocess.CompletedProcess(["python3"], 0, stdout=json.dumps(HTTP), stderr="")
        with mock.patch.object(mod, "run", return_value=result):
            obs = mod.measure_http()
        self.assertTrue(obs["result"]["measurement_valid"])
        self.assertEqual(obs["ground_truth_label"], "UNKNOWN")
        self.assertFalse(obs["ground_truth_verified"])

    def test_http_caido_es_fuente_no_disponible(self):
        result = subprocess.CompletedProcess(["python3"], 1, stdout="", stderr="timeout")
        with mock.patch.object(mod, "run", return_value=result):
            obs = mod.measure_http()
        self.assertFalse(obs["result"]["measurement_valid"])
        self.assertEqual(obs["quality_warnings"], ["http_measurement_unavailable"])
        self.assertEqual(obs["ground_truth_label"], "UNKNOWN")

    def test_sesion_referencia_sin_inventar_ground_truth(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            session = "S06_BASELINE_20261123T043741Z_39a268"
            directory = base / "raw" / session
            directory.mkdir(parents=True)
            (directory / "metadata.json").write_text(json.dumps({
                "session_id": session,
                "status": "complete",
                "schema": "NETLAB360_S06_OBSERVATIONAL_V1",
                "ground_truth_verified": False,
            }))
            with mock.patch.object(mod, "BASE", base):
                reference = mod.validate_reference(session)
            self.assertEqual(reference["session_id"], session)

    def test_sesion_referencia_invalida(self):
        with self.assertRaises(ValueError):
            mod.validate_reference("../../etc/passwd")

    def test_write_metadata_atomically(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "metadata.json"
            mod.store(target, {"training_ready": False})
            self.assertEqual(json.loads(target.read_text()),
                             {"training_ready": False})
            self.assertFalse((Path(d) / "metadata.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
