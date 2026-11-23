"""S06-045: pruebas offline del replay HQ, integridad y UNKNOWN."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SRC = (Path(__file__).resolve().parents[1] /
       "scripts/s06/inferencia_hq_readonly.py")
spec = importlib.util.spec_from_file_location("s06_045_inference", SRC)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class FakeEstimator:
    def __init__(self, kind):
        self.kind = kind

    def predict(self, rows):
        value = rows[0][0]
        is_degraded = value > 1
        if self.kind == "iforest":
            return [-1 if is_degraded else 1]
        return [1 if is_degraded else 0]


def report():
    return {
        "schema": m.EVAL_SCHEMA,
        "features": list(m.FEATURES),
        "target": "nl360-s02-h-hq-120/eth0",
        "evaluation_exploratory": True,
        "production_deployment_authorized": False,
        "s07_mutating_actions_authorized": False,
        "globally_chronological_holdout": False,
        "recovery_not_used_for_binary_training": True,
        "metrics_by_probe": {
            route: {
                "p95_training_rtt_ms": .1,
                "methods": {
                    name: {"fp": 0, "fn": 0, "recovery_false_alarms": 0}
                    for name in m.MODEL_NAMES
                },
            } for route in m.PROBES
        },
    }


class S06045Tests(unittest.TestCase):
    def setUp(self):
        self.models = {
            "IsolationForest": FakeEstimator("iforest"),
            "LogisticRegression": FakeEstimator("logistic"),
        }

    def test_features_contract(self):
        self.assertEqual(m.FEATURES,
                         ("rtt_avg_ms", "rtt_p95_ms", "rtt_mdev_ms", "loss_pct"))
        self.assertEqual(m.PROBES, ("HQ_A_S1", "HQ_A_S2"))

    def test_features_reject_bad_values(self):
        for bad in (None, -1, float("inf"), float("nan"), True, "1"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                m._features([bad, 1, .1, 0])

    def test_features_reject_loss_above_100(self):
        with self.assertRaisesRegex(ValueError, "loss_out_of_range"):
            m._features([1, 2, 1, 101])

    def test_features_valid(self):
        self.assertEqual(m._features((1, 2, .3, 0)), (1., 2., .3, 0.))

    def test_invalid_route_is_unknown_no_model(self):
        with mock.patch.object(m, "_load_models") as loader:
            data = m.infer("UNTRUSTED", "NORMAL", 1)
            self.assertEqual(data["operational_state"], "UNKNOWN")
            self.assertEqual(data["reason"], "UNSUPPORTED_ROUTE_OR_SCENARIO")
            loader.assert_not_called()

    def test_invalid_window_unknown(self):
        for bad in (0, 21, -1, "1", True):
            with self.subTest(value=bad):
                self.assertEqual(m.infer("HQ_A_S1", "NORMAL", bad)["reason"],
                                 "INVALID_WINDOW_INDEX")

    def _call(self, scenario, row):
        with (mock.patch.object(m, "verified_report", return_value=report()),
              mock.patch.object(m, "_historical_rows", return_value=[row]),
              mock.patch.object(m, "_load_models", return_value=self.models)):
            return m.infer("HQ_A_S1", scenario, 1)

    def test_normal_consensus(self):
        got = self._call("NORMAL", (.05, .06, .01, 0))
        self.assertEqual(got["operational_state"], "NORMAL")
        self.assertEqual(got["binary_consensus"], "NORMAL")
        self.assertFalse(got["production_deployment_authorized"])
        self.assertFalse(got["network_mutations_authorized"])
        self.assertFalse(got["new_independent_validation"])

    def test_degraded_consensus(self):
        got = self._call("DEGRADED", (40., 41., .5, 0))
        self.assertEqual(got["operational_state"], "DEGRADED")
        self.assertTrue(all(v == "DEGRADED" for v in got["predictions"].values()))

    def test_recovery_not_three_class_ml(self):
        got = self._call("RECOVERY", (.05, .06, .01, 0))
        self.assertEqual(got["binary_consensus"], "NORMAL")
        self.assertEqual(got["operational_state"], "UNKNOWN")
        self.assertEqual(got["reason"], "RECOVERY_NOT_DISTINGUISHABLE_FROM_NORMAL")

    def test_disagreement_is_unknown(self):
        got = self._call("NORMAL", (.2, .3, .01, 0))
        self.assertEqual(got["operational_state"], "UNKNOWN")
        self.assertEqual(got["reason"], "MODEL_DISAGREEMENT")

    def test_missing_dataset_unknown(self):
        with (mock.patch.object(m, "verified_report", return_value=report()),
              mock.patch.object(m, "_historical_rows",
                                side_effect=ValueError("missing"))):
            got = m.infer("HQ_A_S1", "NORMAL", 1)
        self.assertEqual(got["operational_state"], "UNKNOWN")
        self.assertIsNone(got["predictions"])

    def test_missing_model_unknown(self):
        with (mock.patch.object(m, "verified_report", return_value=report()),
              mock.patch.object(m, "_historical_rows",
                                return_value=[(.05, .06, .01, 0)]),
              mock.patch.object(m, "_load_models",
                                side_effect=ValueError("unverified"))):
            got = m.infer("HQ_A_S1", "NORMAL", 1)
        self.assertEqual(got["reason"], "UNVERIFIED_DATA_OR_MODEL")

    def test_verified_report_and_hash(self):
        with tempfile.TemporaryDirectory() as name:
            d = Path(name)
            r = report()
            r["model_files_sha256"] = {}
            for route in m.PROBES:
                for typ in ("iforest", "logistic"):
                    fname = f"{route.lower()}_{typ}.joblib"
                    raw = fname.encode()
                    (d / fname).write_bytes(raw)
                    r["model_files_sha256"][fname] = hashlib.sha256(raw).hexdigest()
            (d / "evaluacion.json").write_text(json.dumps(r))
            with mock.patch.object(m, "EVAL_DIR", d), mock.patch.object(
                m, "REPORT", d / "evaluacion.json"
            ):
                self.assertEqual(m.verified_report()["schema"], m.EVAL_SCHEMA)
                (d / "hq_a_s1_iforest.joblib").write_bytes(b"tampered")
                with self.assertRaisesRegex(ValueError, "digest"):
                    m.verified_report()

    def test_symlink_model_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            d = Path(name)
            r = report()
            r["model_files_sha256"] = {}
            for route in m.PROBES:
                for typ in ("iforest", "logistic"):
                    fname = f"{route.lower()}_{typ}.joblib"
                    raw = fname.encode()
                    (d / fname).write_bytes(raw)
                    r["model_files_sha256"][fname] = hashlib.sha256(raw).hexdigest()
            f = d / "hq_a_s2_logistic.joblib"
            target = d / "original"
            f.rename(target)
            f.symlink_to(target)
            (d / "evaluacion.json").write_text(json.dumps(r))
            with mock.patch.object(m, "EVAL_DIR", d), mock.patch.object(
                m, "REPORT", d / "evaluacion.json"
            ):
                with self.assertRaisesRegex(ValueError, "digest"):
                    m.verified_report()

    def test_replay_uses_last_verified_cycle(self):
        cycle = {"degraded": {"session_id": "DEG"},
                 "recovery": {"session_id": "REC"}}
        with (mock.patch.object(m, "read_event_batches",
                                return_value=[{}, {}, cycle]) as batch,
              mock.patch.object(m, "read_controlled",
                                return_value=({}, {"HQ_A_S1": [
                                    (40., 41., .1, 0)], "HQ_A_S2": [
                                    (40., 41., .1, 0)]})) as reader):
            rows = m._historical_rows("HQ_A_S1", "DEGRADED")
        self.assertEqual(len(rows), 1)
        batch.assert_called_once_with(m.SOURCE_MANIFEST)
        reader.assert_called_once_with("DEG", "DEGRADED")

    def test_replay_normal_uses_heldout_normal(self):
        with mock.patch.object(
            m, "read_normal",
            return_value={"HQ_A_S1": [(.1, .2, .01, 0)],
                          "HQ_A_S2": [(.1, .2, .01, 0)]}
        ) as reader:
            rows = m._historical_rows("HQ_A_S1", "NORMAL")
        self.assertEqual(len(rows), 1)
        reader.assert_called_once_with(m.NORMAL_TEST)

    def test_audit_matches_saved_metrics(self):
        def rows(route, scenario):
            count = {"NORMAL": 20, "DEGRADED": 4, "RECOVERY": 6}[scenario]
            val = 40. if scenario == "DEGRADED" else .05
            return [(val, val + .01, .001, 0)] * count
        with (mock.patch.object(m, "verified_report", return_value=report()),
              mock.patch.object(m, "_load_models", return_value=self.models),
              mock.patch.object(m, "_historical_rows", side_effect=rows)):
            audited = m.audit_errors()
        self.assertTrue(audited["derived_from_existing_test"])
        self.assertEqual(audited["routes"]["HQ_A_S1"]["P95_RTT"][
            "false_positive_normal_windows"], [])
        self.assertFalse(audited["changes_to_network"])

    def test_audit_detects_metric_mismatch(self):
        r = report()
        r["metrics_by_probe"]["HQ_A_S1"]["methods"]["P95_RTT"]["fp"] = 1
        def rows(route, scenario):
            count = {"NORMAL": 20, "DEGRADED": 4, "RECOVERY": 6}[scenario]
            val = 40. if scenario == "DEGRADED" else .05
            return [(val, val+.01, .001, 0)] * count
        with (mock.patch.object(m, "verified_report", return_value=r),
              mock.patch.object(m, "_load_models", return_value=self.models),
              mock.patch.object(m, "_historical_rows", side_effect=rows)):
            with self.assertRaisesRegex(ValueError, "stored_metrics"):
                m.audit_errors()

    def test_api_routes_when_fastapi_available(self):
        try:
            import fastapi  # noqa: F401
        except ImportError:
            self.skipTest("FastAPI solo instalado en VM cientifica")
        app = m.make_app()
        paths = {route.path for route in app.routes}
        self.assertTrue({"/healthz", "/api/v1/s06/live",
                         "/api/v1/s06/replay",
                         "/api/v1/s06/error-audit"}.issubset(paths))
        self.assertFalse(any("POST" in x.methods for x in app.routes))

    def test_source_has_no_network_mutators(self):
        text = SRC.read_text(encoding="utf-8")
        for forbidden in ("subprocess.", "os.system(", "shell=True",
                          "tc qdisc add", "ip netns add", "docker run",
                          "sudo ", "systemd-run"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
