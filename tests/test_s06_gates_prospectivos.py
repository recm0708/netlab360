"""S06-049: pruebas offline del gate de cronología y suficiencia."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

SOURCE = (Path(__file__).resolve().parents[1] /
          "scripts/s06/auditar_gates_prospectivos.py")
spec = importlib.util.spec_from_file_location("s06_049_audit", SOURCE)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

N_A = "S06_WINDOW_NORMAL_20261123T063314Z_c84c9d"
N_T = "S06_WINDOW_NORMAL_20261123T063414Z_2b5732"
D_TRAIN = "S06_WINDOW_DEGRADED_20261123T070344Z_984563"
D_FUTURE = "S06_WINDOW_DEGRADED_20261123T080000Z_abcdef"

def fake_report():
    return {
        "globally_chronological_holdout": False,
        "recovery_not_used_for_binary_training": True,
        "production_deployment_authorized": False,
        "metrics_by_probe": {"HQ_A_S1": {}, "HQ_A_S2": {}},
        "train_normal_sessions": [N_A],
        "train_degraded_sessions": [D_TRAIN],
        "test_normal_sessions": [N_T],
        "test_degraded_sessions": [D_FUTURE],
    }


class ProspectiveAuditTests(unittest.TestCase):
    def test_session_timestamp_exact(self):
        self.assertEqual(m.session_time(N_A).isoformat(),
                         "2026-11-23T06:33:14+00:00")

    def test_reject_invalid_session_identifier(self):
        for bad in (None, "", "../../etc/passwd", "S06_WINDOW_NORMAL_foo",
                    "S06_WINDOW_FAULT_20261123T060000Z_abcdef"):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                m.session_time(bad)

    def test_disjoint_not_same_as_chronological(self):
        got = m.chronology([N_A, D_TRAIN], [N_T, D_FUTURE])
        self.assertTrue(got["disjoint_session_ids"])
        self.assertFalse(got["global_chronological_holdout"])

    def test_true_chronological_session_order(self):
        got = m.chronology([N_A, N_T], [D_TRAIN, D_FUTURE])
        self.assertTrue(got["global_chronological_holdout"])

    def test_leakage_rejected(self):
        with self.assertRaisesRegex(ValueError, "disjoint"):
            m.chronology([N_A], [N_A])
        with self.assertRaisesRegex(ValueError, "disjoint"):
            m.chronology([N_A, N_A], [D_FUTURE])

    def test_bad_counts_rejected(self):
        for counts in ({}, {"NORMAL": 60, "DEGRADED": 16, "RECOVERY": 23},
                       {"NORMAL": 60, "DEGRADED": 16, "RECOVERY": True}):
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                m.validate_counts(counts)

    def test_audit_flags_real_limitation_not_success(self):
        found = m.findings(fake_report(), m.EXPECTED_COUNTS.copy())
        self.assertFalse(found["chronology"]["global_chronological_holdout"])
        self.assertFalse(found["second_independent_future_labeled_test_present"])
        self.assertFalse(found["horizon_target_defined"])
        self.assertEqual(found["verified_unique_windows_per_route"]["FAULT"], 0)
        self.assertEqual(found["gate"], "PENDING_NEW_PROSPECTIVE_EVIDENCE")
        self.assertFalse(found["models_retrained"])
        self.assertFalse(found["networks_modified"])
        self.assertFalse(found["production_deployment_authorized"])

    def test_invalid_legacy_report_rejected(self):
        old = fake_report()
        old["globally_chronological_holdout"] = True
        with self.assertRaisesRegex(ValueError, "legacy_report"):
            m.findings(old, m.EXPECTED_COUNTS.copy())

    def test_count_originals_uses_only_permitted_original_sessions(self):
        def normal(_id):
            return {r: [(0.1, 0.2, 0.03, 0.0)] * 20 for r in m.PROBES}
        d = [(.2, .3, .1, 0.)] * 4
        recovery = [(.1, .2, .01, 0.)] * 6
        cycles = []
        for n in range(3):
            cycles.append({
                "degraded": {"session_id": f"S06_WINDOW_DEGRADED_20261123T070{n+4}00Z_abcdef"},
                "recovery": {"session_id": f"S06_WINDOW_RECOVERY_20261123T070{n+4}35Z_abcdef"},
            })
        def controlled(session, kind):
            rows = d if kind == "DEGRADED" else recovery
            return ({"controller_token": "known_event"}, {r: rows for r in m.PROBES})
        with (patch.object(m, "read_normal", side_effect=normal) as rn,
              patch.object(m, "read_event_batches", return_value=cycles) as ev,
              patch.object(m, "read_controlled", side_effect=controlled) as co):
            counts = m.count_originals()
        self.assertEqual(counts, m.EXPECTED_COUNTS)
        self.assertEqual(rn.call_count, 3)
        self.assertEqual(co.call_count, 8)
        ev.assert_called_once_with(m.SOURCE_MANIFEST)

    def test_mismatched_token_rejected(self):
        with (patch.object(m, "read_normal",
                           return_value={r: [(.1, .2, .01, 0)] * 20 for r in m.PROBES}),
              patch.object(m, "read_event_batches", return_value=[{
                  "degraded": {"session_id": "A"},
                  "recovery": {"session_id": "B"}}] * 3),
              patch.object(m, "read_controlled", side_effect=[
                  ({"controller_token": "x"}, {r: [(1,2,1,0)]*4 for r in m.PROBES}),
                  ({"controller_token": "y"}, {r: [(.1,.2,.1,0)]*6 for r in m.PROBES}),
              ])):
            with self.assertRaisesRegex(ValueError, "provenance"):
                m.count_originals()

    def test_source_only_reads(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in ("subprocess.", "os.system(", "tc qdisc add",
                          "ip netns add", "docker run", "sudo ", "joblib.dump",
                          ".fit(", ".fit_predict("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
