"""S06 V2: pruebas sin red de scoring congelado y cronología de eventos."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "scripts/s06/evaluar_v2_congelado.py"
spec = importlib.util.spec_from_file_location("s06_v2_frozen_scoring", SRC)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class DummyForest:
    def predict(self, rows):
        return [1 if row[0] < 10 else -1 for row in rows]


class DummyLogistic:
    def predict(self, rows):
        return [0 if row[0] < 10 else 1 for row in rows]


class FrozenScoringTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.study = self.root / "estudio-uniforme-v2"
        self.study.mkdir()
        self.experiments = self.root / "experimentos"
        self.experiments.mkdir()
        self.batch_dir = self.experiments / "S06_043_20261123T160000Z_abcdef"
        self.batch_dir.mkdir()
        self.source = self.batch_dir / "manifest.json"
        self.normal = "S06_WINDOW_NORMAL_20261123T155900Z_abcdef"
        self.d = ["S06_WINDOW_DEGRADED_20261123T160001Z_abcdef",
                  "S06_WINDOW_DEGRADED_20261123T160201Z_abcdef"]
        self.r = ["S06_WINDOW_RECOVERY_20261123T160100Z_abcdef",
                  "S06_WINDOW_RECOVERY_20261123T160300Z_abcdef"]
        self.tokens = ["0000000000000001", "0000000000000002"]
        self.train_n = ["S06_WINDOW_NORMAL_20261123T150000Z_abcdef"]
        self.train_d = ["S06_WINDOW_DEGRADED_20261123T151000Z_abcdef"]
        self.train_r = ["S06_WINDOW_RECOVERY_20261123T151100Z_abcdef"]
        self.frozen = {
            "frozen_at_utc": "2026-11-23T15:30:00+00:00",
            "training": {
                "normal_sessions": self.train_n,
                "degraded_sessions": self.train_d,
                "recovery_sessions": self.train_r,
                "event_tokens": ["00000000000000ff"],
            },
            "p95_cutoffs_ms": {route: .5 for route in m.PROBES},
        }
        for key, val in [("BASE", self.root), ("STUDY", self.study)]:
            p = mock.patch.object(m, key, val)
            p.start()
            self.addCleanup(p.stop)
        self.manifest_file = self.study / "VALIDATION_Manifest.json"
        self.stage = {
            "schema": m.SCHEMA_STAGE["validation"], "status": "VALIDATION_VERIFIED",
            "packets_per_window": 3, "models_retrained": False,
            "normal_session": self.normal, "degraded_sessions": self.d,
            "recovery_sessions": self.r, "event_tokens": list(self.tokens),
            "source_manifest": str(self.source),
        }
        self.batch = {
            "schema": "NETLAB360_S06_043_REAL_HQ_BATCH_V1",
            "status": "complete", "complete_cycles": 2, "planned_cycles": 2,
            "packets_per_degraded_window": 3, "target": m.TARGET,
            "management_interface_mutated": False,
            "new_namespaces_created": False, "new_interfaces_created": False,
            "cycles": [
                {"number": i, "status": "complete", "token": self.tokens[i-1],
                 "degraded": {"session_id": self.d[i-1]},
                 "recovery": {"session_id": self.r[i-1]}}
                for i in (1, 2)
            ],
        }
        for index, token in enumerate(self.tokens, 1):
            (self.batch_dir / f"ciclo_{index:02d}_watchdog.json").write_text(
                json.dumps({"token": token, "state": "RESTORED",
                            "qdisc": "BASELINE", "restoration_trigger": "WATCHDOG",
                            "final_qdisc_state": "BASELINE"}))
        self.save()

    def save(self):
        self.manifest_file.write_text(json.dumps(self.stage))
        self.source.write_text(json.dumps(self.batch))

    def test_validation_manifest_accepted(self):
        got, batch = m.parse_manifest("validation", self.frozen)
        self.assertEqual(got["normal_session"], self.normal)
        self.assertEqual(len(batch["cycles"]), 2)

    def test_reject_reused_train_session(self):
        self.stage["normal_session"] = self.train_n[0]
        self.save()
        with self.assertRaisesRegex(ValueError, "reuses_training"):
            m.parse_manifest("validation", self.frozen)

    def test_reject_reused_token(self):
        self.stage["event_tokens"][1] = "00000000000000ff"
        self.save()
        with self.assertRaisesRegex(ValueError, "reuses_training"):
            m.parse_manifest("validation", self.frozen)

    def test_reject_session_before_freeze(self):
        self.stage["normal_session"] = "S06_WINDOW_NORMAL_20261123T150000Z_aaaaaa"
        self.save()
        with self.assertRaisesRegex(ValueError, "before_freeze"):
            m.parse_manifest("validation", self.frozen)

    def test_reject_nondisjoint(self):
        self.stage["recovery_sessions"][0] = self.d[0]
        self.save()
        with self.assertRaisesRegex(ValueError, "manifest_invalid"):
            m.parse_manifest("validation", self.frozen)

    def test_reject_wrong_sampling(self):
        self.stage["packets_per_window"] = 2
        self.save()
        with self.assertRaisesRegex(ValueError, "manifest_invalid"):
            m.parse_manifest("validation", self.frozen)

    def test_reject_controller_change(self):
        self.batch["management_interface_mutated"] = True
        self.save()
        with self.assertRaisesRegex(ValueError, "batch_invalid"):
            m.parse_manifest("validation", self.frozen)

    def test_reject_no_watchdog_recovery(self):
        p = self.batch_dir / "ciclo_02_watchdog.json"
        d = json.loads(p.read_text())
        d["state"] = "ESCALATED"
        p.write_text(json.dumps(d))
        with self.assertRaisesRegex(ValueError, "watchdog_not"):
            m.parse_manifest("validation", self.frozen)

    def test_reject_stage_not_allowed(self):
        with self.assertRaisesRegex(ValueError, "stage_not_allowed"):
            m.parse_manifest("train", self.frozen)

    def test_reject_test_before_validation(self):
        test = dict(self.stage)
        test["schema"] = m.SCHEMA_STAGE["test"]
        test["status"] = "TEST_VERIFIED"
        test["normal_session"] = "S06_WINDOW_NORMAL_20261123T154000Z_aabbcc"
        (self.study / "TEST_Manifest.json").write_text(json.dumps(test))
        with self.assertRaisesRegex(ValueError, "test_not_after_validation"):
            m.parse_manifest("test", self.frozen)

    def test_reject_test_reuses_validation_token(self):
        test = dict(self.stage)
        test["schema"] = m.SCHEMA_STAGE["test"]
        test["status"] = "TEST_VERIFIED"
        test["normal_session"] = "S06_WINDOW_NORMAL_20261123T170000Z_aabbcc"
        (self.study / "TEST_Manifest.json").write_text(json.dumps(test))
        with self.assertRaisesRegex(ValueError, "test_not_after_validation"):
            m.parse_manifest("test", self.frozen)

    def test_route_metrics_for_scoped_40ms_event(self):
        normal = [(0.1, .15, .03, 0.)] * 20
        degraded = [(40.5, 41., .04, 0.)] * 4
        recovery = [(0.09, .12, .02, 0.)] * 6
        tables = {
            "NORMAL": {"N": {p: normal for p in m.PROBES}},
            "DEGRADED": {"D1": {p: degraded for p in m.PROBES},
                         "D2": {p: degraded for p in m.PROBES}},
            "RECOVERY": {"R1": {p: recovery for p in m.PROBES},
                         "R2": {p: recovery for p in m.PROBES}},
        }
        result = m.route_metrics(m.PROBES[0], tables, self.frozen, {
            "iforest": DummyForest(), "logistic": DummyLogistic(),
        })
        for name in m.METHODS:
            stats = result["methods"][name]
            self.assertEqual((stats["tp"], stats["fp"], stats["tn"], stats["fn"]),
                             (8, 0, 20, 0))
            self.assertEqual(stats["positive_events_with_any_detection"], 2)
            self.assertEqual(stats["per_event_detected_windows"], [4, 4])
            self.assertEqual(stats["recovery_false_alarms"], 0)

    def test_route_metrics_reject_bad_count(self):
        tables = {
            "NORMAL": {"N": {p: [(.1, .1, 0., 0.)] * 19 for p in m.PROBES}},
            "DEGRADED": {"D1": {p: [(40.,41.,.1,0.)]*4 for p in m.PROBES},
                         "D2": {p: [(40.,41.,.1,0.)]*4 for p in m.PROBES}},
            "RECOVERY": {"R1": {p: [(.1,.2,.02,0.)]*6 for p in m.PROBES},
                         "R2": {p: [(.1,.2,.02,0.)]*6 for p in m.PROBES}},
        }
        with self.assertRaisesRegex(ValueError, "window_count_invalid"):
            m.route_metrics(m.PROBES[0], tables, self.frozen, {
                "iforest": DummyForest(), "logistic": DummyLogistic(),
            })

    def test_source_no_mutation_or_training(self):
        source = SRC.read_text()
        for forbidden in ("subprocess.", "tc qdisc add", "ip netns add",
                          "docker run", "sudo ", "systemd-run", ".fit(", "joblib.dump"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
