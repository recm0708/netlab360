"""S06: pruebas offline de normalizacion, integridad y procedencia."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
FILE = REPO / "scripts/s06/normalizar_sesiones.py"
SPEC = importlib.util.spec_from_file_location("s06_normalizacion", FILE)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

BASE_ID = "S06_BASELINE_20261123T043741Z_39a268"
PERF_ID = "S06_PERF_20261123T044532Z_cea2dc"
T0 = datetime(2026, 11, 23, 4, 45, tzinfo=timezone.utc)
SOURCES = ("HQ_A_S1", "HQ_A_S2", "S2_A_FRONTAL_HQ", "S2_A_FRONTAL_HQ_HTTP")


def dt(i):
    return (T0 + timedelta(seconds=i * 2)).isoformat(timespec="milliseconds")


def sample_baseline(i):
    at = (T0 + timedelta(seconds=i * 2)).timestamp()
    return {
        "schema": "NETLAB360_S06_OBSERVATIONAL_V1",
        "recorded_at_utc": dt(i), "sample_index": i + 1,
        "session_id": BASE_ID, "observed_healthy": True,
        "quality_warnings": [], "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "metric_samples": [
            {"name": key, "labels": {"__name__": key}, "value": 1.0,
             "timestamp_unix": at}
            for key in sorted(m.S04_NAMES)
        ],
    }


def sample_perf(i):
    probe = SOURCES[i % 4]
    icmp = probe != "S2_A_FRONTAL_HQ_HTTP"
    result = ({
        "sent": 5, "received": 5, "loss_pct": 0,
        "rtt_min_ms": 0.05, "rtt_avg_ms": 0.08,
        "rtt_max_ms": 0.11, "rtt_mdev_ms": 0.02,
        "rtt_p95_ms": 0.1, "measurement_valid": True,
    } if icmp else {
        "elapsed_ms": 7.594, "http_status": 200,
        "active_backend": "BACKEND_HQ",
        "measurement_valid": True,
    })
    return {
        "schema": "NETLAB360_S06_PERFORMANCE_OBSERVATIONAL_V1",
        "recorded_at_utc": dt(i + 20), "sample_index": i + 1,
        "session_id": PERF_ID,
        "kind": "icmp" if icmp else "http",
        "round": i // 4 + 1,
        "probe_id": probe,
        "source_namespace": "nl360-s02-h-hq-120" if icmp else "nl360-s02-h-s2-320",
        "destination_ip": "10.71.20.20" if icmp else None,
        "destination_url": "http://10.70.20.23:8080/api/v1/service" if not icmp else None,
        "result": result, "quality_warnings": [],
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
    }


def create_data(root):
    data = [(BASE_ID, "observaciones.jsonl", "observations_sha256",
             [sample_baseline(i) for i in range(12)],
             "NETLAB360_S06_OBSERVATIONAL_V1"),
            (PERF_ID, "mediciones.jsonl", "data_digest_sha256",
             [sample_perf(i) for i in range(12)],
             "NETLAB360_S06_PERFORMANCE_OBSERVATIONAL_V1")]
    for session, filename, key, rows, schema in data:
        folder = root / "raw" / session
        folder.mkdir(parents=True)
        serialized = "".join(json.dumps(x) + "\n" for x in rows).encode()
        (folder / filename).write_bytes(serialized)
        metadata = {
            "schema": schema, "session_id": session,
            "status": "complete", "ground_truth_label": "UNKNOWN",
            "ground_truth_verified": False,
            "samples_complete" if session == BASE_ID else "samples_recorded": 12,
            key: hashlib.sha256(serialized).hexdigest(),
        }
        if session == PERF_ID:
            metadata["reference_session"] = BASE_ID
        (folder / "metadata.json").write_text(json.dumps(metadata))


class NormalizacionS06Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        create_data(self.root)
        self.patch = mock.patch.object(m, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_sesiones_validas_y_filas_normalizadas(self):
        rows, quality = m.analyze(BASE_ID, PERF_ID)
        self.assertEqual(len(rows), 60 + 9 * 8 + 3)
        self.assertEqual(quality["record_counts"]["raw_baseline"], 12)
        self.assertEqual(quality["record_counts"]["raw_performance"], 12)
        self.assertEqual(quality["record_counts"]["missing_numeric_values"], 0)
        self.assertEqual(quality["ground_truth_labels_available"], 0)
        self.assertFalse(quality["training_ready"])
        self.assertFalse(quality["time_split_ready"])
        self.assertTrue(all(row["ground_truth_label"] == "UNKNOWN" for row in rows))

    def test_unidades_y_fuentes_no_mezcladas(self):
        rows, quality = m.analyze(BASE_ID, PERF_ID)
        self.assertEqual(quality["record_counts"]["by_source"], {
            "http_s05": 3, "icmp_s02": 72, "prometheus_s04": 60,
        })
        self.assertEqual({x["unit"] for x in rows if x["source"] == "prometheus_s04"},
                         {"state"})
        self.assertEqual({x["unit"] for x in rows if x["signal"] == "loss_pct"},
                         {"percent"})
        self.assertEqual({x["unit"] for x in rows if x["signal"] == "elapsed_ms"},
                         {"ms"})

    def test_timestamps_utc_completos(self):
        rows, quality = m.analyze(BASE_ID, PERF_ID)
        self.assertEqual(rows[0]["observed_at_utc"], dt(0))
        self.assertEqual(quality["period_utc"]["last"], dt(31))

    def test_no_permite_id_malicioso(self):
        with self.assertRaisesRegex(ValueError, "Identificador"):
            m.safe_dir("../x", m.BASE_ID)

    def test_no_permite_ground_truth_falso(self):
        path = self.root / "raw" / BASE_ID / "metadata.json"
        meta = json.loads(path.read_text())
        meta["ground_truth_label"] = "NORMAL"
        path.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError, "Metadatos"):
            m.analyze(BASE_ID, PERF_ID)

    def test_rechaza_checksum_falso(self):
        path = self.root / "raw" / BASE_ID / "observaciones.jsonl"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Checksum"):
            m.analyze(BASE_ID, PERF_ID)

    def test_rechaza_referencia_diferente(self):
        path = self.root / "raw" / PERF_ID / "metadata.json"
        meta = json.loads(path.read_text())
        meta["reference_session"] = "S06_BASELINE_20261123T043741Z_000000"
        path.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError, "enlazadas"):
            m.analyze(BASE_ID, PERF_ID)

    def test_rechaza_serie_sintetica_fuera_del_catalogo(self):
        samples = [sample_baseline(0)]
        samples[0]["metric_samples"][0]["name"] = "artificial"
        with self.assertRaisesRegex(ValueError, "Familia S04"):
            m.transform_baseline(BASE_ID, samples)

    def test_rechaza_timestamp_obsoleto(self):
        samples = [sample_baseline(0)]
        samples[0]["metric_samples"][0]["timestamp_unix"] -= 600
        with self.assertRaisesRegex(ValueError, "obsoleta"):
            m.transform_baseline(BASE_ID, samples)

    def test_rechaza_interfaz_ajena(self):
        samples = [sample_perf(i) for i in range(12)]
        samples[0]["probe_id"] = "INTERFAZ_AJENA"
        with self.assertRaisesRegex(ValueError, "catalogo"):
            m.transform_perf(PERF_ID, samples)

    def test_rechaza_perdida_incoherente(self):
        samples = [sample_perf(i) for i in range(12)]
        samples[0]["result"]["loss_pct"] = 100
        with self.assertRaisesRegex(ValueError, "inconsistente"):
            m.transform_perf(PERF_ID, samples)

    def test_null_rtt_no_es_cero(self):
        samples = [sample_perf(i) for i in range(12)]
        for key in ("rtt_min_ms", "rtt_avg_ms", "rtt_max_ms", "rtt_mdev_ms", "rtt_p95_ms"):
            samples[0]["result"][key] = None
        samples[0]["result"]["received"] = 0
        samples[0]["result"]["loss_pct"] = 100
        rows, report = m.transform_perf(PERF_ID, samples)
        missing = [x for x in rows if x["value"] is None]
        self.assertEqual(len(missing), 5)
        self.assertEqual(sum(report["missing_values"].values()), 5)

    def test_detecta_scrape_repetido_sin_ocultarlo(self):
        samples = [sample_baseline(i) for i in range(12)]
        for idx in (1, 2):
            for metric in samples[idx]["metric_samples"]:
                metric["timestamp_unix"] = samples[0]["metric_samples"][0]["timestamp_unix"]
        _, quality = m.transform_baseline(BASE_ID, samples)
        self.assertEqual(quality["prometheus_repeated_scrape_samples"], 10)

    def test_no_hace_truncamiento_y_rechaza_nans(self):
        with self.assertRaisesRegex(ValueError, "finito"):
            m.as_number(float("nan"))
        with self.assertRaisesRegex(ValueError, "numerico"):
            m.as_number(True)

    def test_rechaza_zona_horaria_distinta_utc(self):
        with self.assertRaisesRegex(ValueError, "no UTC"):
            m.parse_utc("2026-11-22T23:45:00-05:00")

    def test_sin_symlink_malicioso(self):
        folder = self.root / "raw" / BASE_ID
        sample_path = folder / "observaciones.jsonl"
        sample_path.unlink()
        sample_path.symlink_to(self.root / "no_such_file")
        with self.assertRaisesRegex(ValueError, "ausentes/symlink"):
            m.analyze(BASE_ID, PERF_ID)


if __name__ == "__main__":
    unittest.main()
