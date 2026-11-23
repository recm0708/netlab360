"""S06-051: no alteración de datos, paquete real vs metadata y confusión."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "scripts/s06/auditar_muestreo_historico.py"
spec = importlib.util.spec_from_file_location("s06_051_audit", SRC)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def inventory(normal=(2, 2, 2), degraded=(3, 3, 3, 3),
              recovery=(3, 3, 3, 3)):
    rows = []
    for index, size in enumerate(normal):
        rows.append({"class": "NORMAL",
                     "split_role": "TRAIN" if index < 2 else "TEST",
                     "packets_per_window": size, "windows_per_route": 20})
    for index, size in enumerate(degraded):
        rows.append({"class": "DEGRADED",
                     "split_role": "TRAIN" if index < 3 else "TEST",
                     "packets_per_window": size, "windows_per_route": 4})
    for index, size in enumerate(recovery):
        rows.append({"class": "RECOVERY",
                     "split_role": "RECOVERY_ANALYSIS" if index == 3 else "HISTORICAL_OTHER",
                     "packets_per_window": size, "windows_per_route": 6})
    return rows


class S06051AuditTests(unittest.TestCase):
    def test_summarize_class_separation(self):
        d = m.summarize(inventory())
        self.assertTrue(d["class_packet_sizes_disjoint"])
        self.assertEqual(d["potential_protocol_class_confound"],
                         "HIGH_IF_PACKET_SIZES_DISJOINT")
        self.assertEqual(d["windows_by_class_and_packet_size"]["NORMAL"], {"2": 60})
        self.assertEqual(d["windows_by_class_and_packet_size"]["DEGRADED"], {"3": 16})
        self.assertEqual(d["windows_by_class_and_packet_size"]["RECOVERY"], {"3": 24})
        self.assertEqual(d["methodological_decision"], "KEEP_PREREGISTRATION_BLOCKED")

    def test_summarize_partial_mix(self):
        d = m.summarize(inventory(normal=(2, 2, 3)))
        self.assertFalse(d["class_packet_sizes_disjoint"])
        self.assertEqual(d["potential_protocol_class_confound"],
                         "POSSIBLE_SAMPLING_BIAS_REQUIRES_CONTROL")
        self.assertEqual(d["windows_by_class_and_packet_size"]["NORMAL"],
                         {"2": 40, "3": 20})

    def test_summarize_no_new_test_claim(self):
        d = m.summarize(inventory())
        self.assertFalse(d["new_test_performed"])
        self.assertFalse(d["existing_models_rescored"])
        self.assertFalse(d["models_retrained"])
        self.assertFalse(d["network_mutations_executed"])

    def test_wrong_total_rejected(self):
        data = inventory()
        data[0]["windows_per_route"] = 19
        with self.assertRaisesRegex(ValueError, "window_inventory"):
            m.summarize(data)

    def test_wrong_number_of_sessions_rejected(self):
        with self.assertRaisesRegex(ValueError, "count"):
            m.summarize(inventory()[:9])

    def test_bad_packet_size_rejected(self):
        data = inventory()
        data[1]["packets_per_window"] = 0
        with self.assertRaisesRegex(ValueError, "invalid_aggregate"):
            m.summarize(data)

    def test_unexpected_frozen_packet_sizes_rejected(self):
        with self.assertRaisesRegex(ValueError, "frozen_packet_protocol"):
            m.summarize(inventory(normal=(3,3,3)))

    def test_catalog_11_sessions_and_roles(self):
        report = {
            "train_normal_sessions": [m.NORMAL_A, m.NORMAL_B],
            "test_normal_sessions": [m.NORMAL_TEST],
            "train_degraded_sessions": [m.DEGRADED_INITIAL, "D1", "D2"],
            "test_degraded_sessions": ["D3"],
            "test_recovery_sessions": ["R3"],
        }
        cycles = [
            {"degraded": {"session_id": "D1"}, "recovery": {"session_id": "R1"}},
            {"degraded": {"session_id": "D2"}, "recovery": {"session_id": "R2"}},
            {"degraded": {"session_id": "D3"}, "recovery": {"session_id": "R3"}},
        ]
        out = m.session_catalog(report, cycles)
        self.assertEqual(len(out), 11)
        self.assertEqual(sum(r == "TRAIN" for _, _, r in out), 5)
        self.assertEqual(sum(r == "TEST" for _, _, r in out), 2)
        self.assertEqual(sum(r == "RECOVERY_ANALYSIS" for _, _, r in out), 1)

    def test_catalog_rejects_untracked_test(self):
        report = {"train_normal_sessions": [m.NORMAL_A, m.NORMAL_B],
                  "test_normal_sessions": ["NOT_ORIGINAL"],
                  "train_degraded_sessions": [], "test_degraded_sessions": [],
                  "test_recovery_sessions": []}
        with self.assertRaisesRegex(ValueError, "unrecognized_normal_test"):
            m.session_catalog(report, [])

    def test_frozen_gate_rejects_changed_protocol(self):
        d = {
            "schema": m.FREEZE_SCHEMA,
            "status": "PLAN_READY",
            "historical_packet_counts": [2, 3],
            "models_retrained": False,
            "new_prospective_test_completed": False,
        }
        with (patch.object(m, "read_regular", return_value=json.dumps(d).encode()),
              patch.object(m, "compare_frozen"),
              patch.object(m, "current_freeze", return_value=d)):
            with self.assertRaisesRegex(ValueError, "frozen_gate"):
                m.verified_freeze()

    def _write_session(self, folder, requested=2, sent=2):
        folder.mkdir()
        name = folder.name
        metadata = {
            "session_id": name, "status": "complete",
            "packet_count_per_probe": requested
        }
        (folder / "metadata.json").write_text(json.dumps(metadata))
        measurements = [{
            "kind": "icmp", "probe_id": probe,
            "requested_packets": requested,
            "result": {
                "measurement_valid": True, "sent": sent, "received": sent,
            },
        } for probe in m.PROBES]
        rows = [{
            "session_id": name, "window_index": i,
            "ground_truth_label": "NORMAL",
            "ground_truth_verified": True, "measurements": measurements,
        } for i in (1, 2)]
        (folder / "ventanas.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n")
        return name

    def test_requested_equals_sent(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            s = self._write_session(root / "S06_WINDOW_NORMAL_20261123T000000Z_abcdef")
            with (patch.object(m, "RAW", root),
                  patch.object(m, "read_normal",
                               return_value={probe: [(1,2,3,0)] * 2
                                             for probe in m.PROBES})):
                result = m.inspect_session(s, "NORMAL", "TRAIN")
                self.assertEqual(result["packets_per_window"], 2)
                self.assertTrue(result["packets_metadata_matches_actual"])

    def test_mismatched_packet_transmission_rejected(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            s = self._write_session(root / "S06_WINDOW_NORMAL_20261123T000000Z_abcdef",
                                    requested=2, sent=3)
            with (patch.object(m, "RAW", root),
                  patch.object(m, "read_normal",
                               return_value={probe: [(1,2,3,0)] * 2
                                             for probe in m.PROBES})):
                with self.assertRaisesRegex(ValueError, "actual_packets"):
                    m.inspect_session(s, "NORMAL", "TRAIN")

    def test_source_no_network_or_learning_mutators(self):
        text = SRC.read_text()
        for word in ("subprocess.", "tc qdisc add", "docker run",
                     "ip netns add", ".fit(", "joblib.dump", "sudo "):
            with self.subTest(word=word):
                self.assertNotIn(word, text)


if __name__ == "__main__":
    unittest.main()
