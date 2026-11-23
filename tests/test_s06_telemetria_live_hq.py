"""S06-046: validacion offline de freshness/quality y API solo lectura."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts/s06"
COLLECTOR = SCRIPTS / "telemetria_hq_live.py"
API = SCRIPTS / "inferencia_hq_readonly.py"


def import_source(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = import_source("s06_046_collector", COLLECTOR)
api = import_source("s06_046_inference", API)


class FakeEstimator:
    def __init__(self, name):
        self.name = name

    def predict(self, rows):
        degraded = rows[0][0] > 1
        if self.name == "iforest":
            return [-1 if degraded else 1]
        return [1 if degraded else 0]


def fake_report():
    return {
        "metrics_by_probe": {
            route: {"p95_training_rtt_ms": 0.1}
            for route in api.PROBES
        }
    }


def sample(*, timestamp=None):
    now = timestamp or datetime.now(timezone.utc)
    t = now.isoformat()
    boundary = {
        "snapshot_valid": True,
        "qdisc_state": "CANDIDATE_NOQUEUE",
        "noc_healthy": True,
        "routes_ok": {"HQ_A_S1": True, "HQ_A_S2": True},
    }
    guard = {
        "schema": "NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1",
        "state": "NONE", "qdisc": "BASELINE",
        "target": "nl360-s02-h-hq-120/eth0",
    }
    records = []
    for route, source in m.PROBE_TARGETS.items():
        records.append({
            "probe_id": route,
            "source_namespace": source["namespace"],
            "destination_ip": source["ip"],
            "kind": "icmp",
            "requested_packets": 3,
            "recorded_at_utc": t,
            "result": {
                "measurement_valid": True,
                "sent": 3, "received": 3,
                "rtt_avg_ms": 0.05, "rtt_p95_ms": 0.06,
                "rtt_mdev_ms": 0.01, "loss_pct": 0,
            },
        })
    return {
        "schema": m.SCHEMA,
        "source": m.SOURCE, "target": m.TARGET,
        "started_at_utc": t, "collected_at_utc": t,
        "packets_per_probe": 3,
        "before": boundary, "after": boundary.copy(),
        "guard_before": guard, "guard_after": guard.copy(),
        "measurements": records,
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "network_mutations_executed": False,
    }


class FreshTelemetryTests(unittest.TestCase):
    def test_snapshot_valid_two_real_probe_ids(self):
        d = m.validate_snapshot(sample())
        self.assertEqual(set(d["features_by_route"]), {"HQ_A_S1", "HQ_A_S2"})
        self.assertEqual(d["features_by_route"]["HQ_A_S1"], (.05, .06, .01, 0.))

    def test_stale_snapshot_rejected(self):
        d = sample(timestamp=datetime.now(timezone.utc)-timedelta(seconds=31))
        with self.assertRaisesRegex(ValueError, "stale"):
            m.validate_snapshot(d)

    def test_future_snapshot_rejected(self):
        d = sample(timestamp=datetime.now(timezone.utc)+timedelta(seconds=4))
        with self.assertRaisesRegex(ValueError, "future"):
            m.validate_snapshot(d)

    def test_bad_times_rejected(self):
        d = sample()
        d["collected_at_utc"] = "2026-11-23T00:00:00"
        with self.assertRaisesRegex(ValueError, "timezone"):
            m.validate_snapshot(d)

    def test_wrong_target_rejected(self):
        d = sample()
        d["target"] = "ens33"
        with self.assertRaisesRegex(ValueError, "contract"):
            m.validate_snapshot(d)

    def test_unknown_ground_truth_must_remain_unknown(self):
        d = sample()
        d["ground_truth_label"] = "NORMAL"
        with self.assertRaisesRegex(ValueError, "contract"):
            m.validate_snapshot(d)

    def test_baseline_mutations_rejected(self):
        d = sample()
        d["network_mutations_executed"] = True
        with self.assertRaisesRegex(ValueError, "contract"):
            m.validate_snapshot(d)

    def test_guard_active_rejected(self):
        d = sample()
        d["guard_after"]["state"] = "APPLIED"
        with self.assertRaisesRegex(ValueError, "boundaries"):
            m.validate_snapshot(d)

    def test_boundary_unhealthy_rejected(self):
        d = sample()
        d["before"]["noc_healthy"] = False
        with self.assertRaisesRegex(ValueError, "boundaries"):
            m.validate_snapshot(d)

    def test_missing_or_replaced_probe_rejected(self):
        d = sample()
        d["measurements"][1]["probe_id"] = "HQ_A_S1"
        with self.assertRaisesRegex(ValueError, "probe"):
            m.validate_snapshot(d)

    def test_ip_source_changed_rejected(self):
        d = sample()
        d["measurements"][0]["destination_ip"] = "8.8.8.8"
        with self.assertRaisesRegex(ValueError, "allowlisted"):
            m.validate_snapshot(d)

    def test_packet_loss_and_invalid_measurement_unknown(self):
        d = sample()
        d["measurements"][0]["result"]["received"] = 2
        with self.assertRaisesRegex(ValueError, "packet_loss"):
            m.validate_snapshot(d)
        d = sample()
        d["measurements"][0]["result"]["measurement_valid"] = False
        with self.assertRaisesRegex(ValueError, "incomplete"):
            m.validate_snapshot(d)

    def test_nonfinite_rejected(self):
        d = sample()
        d["measurements"][0]["result"]["rtt_p95_ms"] = float("nan")
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            m.validate_snapshot(d)

    def test_read_latest_missing_and_symlink(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            latest = folder / "latest.json"
            with mock.patch.object(m, "LATEST", latest):
                with self.assertRaisesRegex(ValueError, "missing"):
                    m.read_latest()
                other = folder / "target.json"
                other.write_text(json.dumps(sample()))
                latest.symlink_to(other)
                with self.assertRaisesRegex(ValueError, "missing"):
                    m.read_latest()

    def test_read_latest_valid_private_file(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name) / "latest.json"
            p.write_text(json.dumps(sample()))
            p.chmod(0o600)
            with mock.patch.object(m, "LATEST", p):
                self.assertEqual(len(m.read_latest()["features_by_route"]), 2)

    def test_capture_preconditions_before_ping(self):
        with (mock.patch.object(m, "preflight"),
              mock.patch.object(m, "evidence_snapshot",
                                return_value={}) as snap,
              mock.patch.object(m, "read_guard", return_value={}),
              mock.patch.object(m, "measure_ping") as ping):
            with self.assertRaisesRegex(RuntimeError, "precondition"):
                m.capture_once()
            snap.assert_called_once()
            ping.assert_not_called()

    def test_live_missing_returns_unknown(self):
        with mock.patch.object(api, "read_latest",
                               side_effect=ValueError("stale")):
            result = api.infer_live("HQ_A_S1")
        self.assertEqual(result["operational_state"], "UNKNOWN")
        self.assertFalse(result["fresh_telemetry_verified"])
        self.assertFalse(result["production_deployment_authorized"])

    def test_live_invalid_route_returns_unknown_before_model(self):
        with mock.patch.object(api, "read_latest") as read:
            result = api.infer_live("ANY")
            self.assertEqual(result["reason"], "UNSUPPORTED_ROUTE")
            read.assert_not_called()

    def _fresh(self):
        return {
            "features_by_route": {"HQ_A_S1": (.05, .06, .01, 0),
                                  "HQ_A_S2": (.05, .06, .01, 0)},
            "collected_at_utc": datetime.now(timezone.utc).isoformat(),
            "age_seconds": 1.2, "source": m.SOURCE, "target": m.TARGET,
        }

    def test_live_normal_uses_models_without_training(self):
        with (mock.patch.object(api, "read_latest", return_value=self._fresh()),
              mock.patch.object(api, "verified_report", return_value=fake_report()),
              mock.patch.object(api, "_load_models", return_value={
                  "IsolationForest": FakeEstimator("iforest"),
                  "LogisticRegression": FakeEstimator("logistic"),
              })):
            r = api.infer_live("HQ_A_S1")
        self.assertEqual(r["operational_state"], "NORMAL")
        self.assertEqual(r["binary_consensus"], "NORMAL")
        self.assertTrue(r["fresh_telemetry_verified"])
        self.assertEqual(r["ground_truth_label"], "UNKNOWN")
        self.assertFalse(r["model_generalization_demonstrated"])
        self.assertFalse(r["network_mutations_authorized"])

    def test_live_anomaly_requires_independent_confirmation(self):
        d = self._fresh()
        d["features_by_route"]["HQ_A_S1"] = (40, 41, .5, 0)
        with (mock.patch.object(api, "read_latest", return_value=d),
              mock.patch.object(api, "verified_report", return_value=fake_report()),
              mock.patch.object(api, "_load_models", return_value={
                  "IsolationForest": FakeEstimator("iforest"),
                  "LogisticRegression": FakeEstimator("logistic"),
              })):
            r = api.infer_live("HQ_A_S1")
        self.assertEqual(r["binary_consensus"], "DEGRADED")
        self.assertEqual(r["operational_state"], "UNKNOWN")
        self.assertEqual(r["reason"], "DEGRADATION_INDICATION_UNCONFIRMED")

    def test_code_has_no_state_mutators(self):
        text = COLLECTOR.read_text()
        for bad in ("shell=True", "tc qdisc add", "ip netns add",
                    "docker run", "systemd-run", "sudo -v"):
            self.assertNotIn(bad, text)


if __name__ == "__main__":
    unittest.main()
