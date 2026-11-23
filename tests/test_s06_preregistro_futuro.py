"""S06-050: pre-registro frozen, strict time and no redeployment."""
from __future__ import annotations
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "scripts/s06/prerregistrar_estudio_futuro.py"
spec = importlib.util.spec_from_file_location("s06_050_freeze", SOURCE)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def original_report():
    return {
        "production_deployment_authorized": False,
        "evaluation_exploratory": True,
        "globally_chronological_holdout": False,
        "train_normal_sessions": [m.NORMAL_A, m.NORMAL_B],
        "train_degraded_sessions": [m.DEGRADED_INITIAL],
        "test_normal_sessions": [m.NORMAL_TEST],
        "test_degraded_sessions": [],
        "test_recovery_sessions": [],
        "features": ["rtt_avg_ms", "rtt_p95_ms", "rtt_mdev_ms", "loss_pct"],
        "model_files_sha256": {"a.joblib": "a" * 64, "b.joblib": "b" * 64,
                               "c.joblib": "c" * 64, "d.joblib": "d" * 64},
    }


def original_audit():
    return {
        "schema": "NETLAB360_S06_049_READINESS_AUDIT_V1",
        "gate": "PENDING_NEW_PROSPECTIVE_EVIDENCE",
        "audit_only": True,
        "chronology": {"global_chronological_holdout": False},
        "verified_unique_windows_per_route":
            {"NORMAL": 60, "DEGRADED": 16, "RECOVERY": 24, "FAULT": 0},
    }


def cycles():
    return [{
        "degraded": {"session_id": "S06_WINDOW_DEGRADED_20261123T080000Z_abcdef"},
        "recovery": {"session_id": "S06_WINDOW_RECOVERY_20261123T080010Z_abcdef"},
    }]


class FrozenStudyTests(unittest.TestCase):
    def plan(self, packet=2, at=datetime(2026, 11, 24, tzinfo=timezone.utc)):
        def fetch(path, limit=150000):
            if path == m.AUDIT:
                return json.dumps(original_audit()).encode()
            if path == m.REPORT:
                return b"original evaluation"
            raise AssertionError(path)
        with (mock.patch.object(m, "verified_report", return_value=original_report()),
              mock.patch.object(m, "read_regular", side_effect=fetch),
              mock.patch.object(m, "packet_count", return_value=packet),
              mock.patch.object(m, "read_event_batches", return_value=cycles())):
            return m.build(now=at)

    def test_frozen_plan_excludes_historical_ids(self):
        d = self.plan()
        self.assertTrue(d["future_plan"]["new_sessions_after_freeze_only"])
        self.assertEqual(d["status"], "PLAN_READY")
        self.assertIn(m.NORMAL_A, d["historical_ids_excluded_from_future_test"])
        self.assertEqual(d["frozen_at_utc"], "2026-11-24T00:00:00+00:00")
        self.assertFalse(d["network_mutations_executed"])

    def test_locked_methods_are_not_forecast(self):
        d = self.plan()
        self.assertEqual(len(d["model_file_hashes"]), 4)
        self.assertEqual(len(d["methods"]), 3)
        self.assertFalse(d["models_retrained"])
        self.assertFalse(d["new_prospective_test_completed"])
        self.assertEqual(d["future_plan"]["forecast_horizon"],
                         "NOT_DEFINED_NO_PREDICTION_CLAIM")

    def test_freeze_timestamp_before_existing_fails(self):
        with self.assertRaisesRegex(ValueError, "clock"):
            self.plan(at=datetime(2026, 11, 22, tzinfo=timezone.utc))

    def test_freeze_must_be_aware(self):
        with self.assertRaisesRegex(ValueError, "clock"):
            self.plan(at=datetime(2026, 11, 24))

    def test_identical_frozen_plan_is_accepted(self):
        d = self.plan()
        later = self.plan(at=datetime(2026, 11, 25, tzinfo=timezone.utc))
        m.compare_frozen(d, later)

    def test_reject_model_change_after_freezing(self):
        d = self.plan()
        later = self.plan(at=datetime(2026, 11, 25, tzinfo=timezone.utc))
        later["model_file_hashes"]["a.joblib"] = "x" * 64
        with self.assertRaisesRegex(ValueError, "changed"):
            m.compare_frozen(d, later)

    def test_reject_rewritten_protocol(self):
        d = self.plan()
        later = self.plan()
        later["future_plan"]["positive_independent_event_tokens_min"] = 1
        with self.assertRaisesRegex(ValueError, "changed"):
            m.compare_frozen(d, later)

    def test_reject_freeze_timestamp_before_baseline(self):
        d = self.plan()
        d["frozen_at_utc"] = "2020-01-01T00:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "timestamp"):
            m.compare_frozen(d, self.plan())

    def test_no_frozen_creation_overwrites(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            file = root / "freeze.json"
            file.write_text("original")
            with mock.patch.object(m, "ROOT", root), mock.patch.object(m, "FREEZE", file):
                with self.assertRaises(FileExistsError):
                    with file.open("x") as stream:
                        stream.write("tampered")
            self.assertEqual(file.read_text(), "original")

    def test_private_source_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            source = root / "source.json"
            link = root / "link.json"
            source.write_text("{}")
            link.symlink_to(source)
            with self.assertRaisesRegex(ValueError, "regular"):
                m.read_regular(link)

    def test_bad_metadata_packet_count(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home)
            folder = root / m.NORMAL_A
            folder.mkdir()
            (folder / "metadata.json").write_text(json.dumps({
                "session_id": m.NORMAL_A, "status": "complete",
                "stimulus": "NONE", "mutating_action_executed": False,
                "packet_count_per_probe": 0,
            }))
            with mock.patch.object(m, "RAW", root):
                with self.assertRaisesRegex(ValueError, "packet_count"):
                    m.packet_count(m.NORMAL_A, False)

    def test_full_source_has_no_network_mutators(self):
        text = SOURCE.read_text(encoding="utf-8")
        for forbidden in ("subprocess.", "tc qdisc add", "docker run", "ip netns add",
                          ".fit(", "joblib.dump", "sudo ", "systemd-run"):
            with self.subTest(bad=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
