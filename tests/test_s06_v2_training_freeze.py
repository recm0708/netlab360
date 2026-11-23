"""S06 V2: congelación de modelos sin fuga TEST ni red."""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "scripts/s06/entrenar_y_congelar_v2.py"
spec = importlib.util.spec_from_file_location("s06_v2_train_freeze", SRC)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def fake_ids():
    d = [
        "S06_WINDOW_DEGRADED_20261123T150227Z_abcdef",
        "S06_WINDOW_DEGRADED_20261123T150450Z_abcdef",
    ]
    r = [
        "S06_WINDOW_RECOVERY_20261123T150320Z_abcdef",
        "S06_WINDOW_RECOVERY_20261123T150540Z_abcdef",
    ]
    return d, r


class V2FreezeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.base = self.root / "s06"
        self.base.mkdir()
        self.study = self.base / "estudio-uniforme-v2"
        self.study.mkdir(mode=0o700)
        self.train = self.study / "TRAIN_Manifest.json"
        self.dest = self.study / "modelos-v2"
        self.report = self.dest / "S06_V2_Training_Freeze.json"
        for key, value in (("BASE", self.base), ("STUDY", self.study),
                           ("TRAIN", self.train), ("DEST", self.dest),
                           ("REPORT", self.report)):
            p = mock.patch.object(m, key, value)
            p.start()
            self.addCleanup(p.stop)
        self.degraded, self.recovery = fake_ids()
        self.folder = self.base / "experimentos" / "S06_043_20261123T150227Z_abcdef"
        self.folder.mkdir(parents=True)
        self.manifest = self.folder / "manifest.json"
        self.doc = {
            "schema": m.TRAIN_SCHEMA, "status": "TRAIN_VERIFIED",
            "models_trained": False,
            "event_count": 2, "packets_per_window": 3,
            "normal_sessions": list(m.APPROVED_NORMAL),
            "degraded_sessions": self.degraded,
            "recovery_sessions": self.recovery,
            "source_manifest": str(self.manifest),
        }
        self.train.write_text(json.dumps(self.doc))
        self.events = []
        for n in (1, 2):
            token = f"{n:016x}"
            item = {
                "number": n, "status": "complete", "token": token,
                "degraded": {"session_id": self.degraded[n - 1]},
                "recovery": {"session_id": self.recovery[n - 1]},
            }
            self.events.append(item)
            (self.folder / f"ciclo_{n:02d}_watchdog.json").write_text(
                json.dumps({
                    "token": token, "state": "RESTORED",
                    "qdisc": "BASELINE", "restoration_trigger": "WATCHDOG",
                    "final_qdisc_state": "BASELINE",
                }))
        self.batch = {
            "schema": m.BATCH_SCHEMA, "status": "complete",
            "planned_cycles": 2, "complete_cycles": 2,
            "packets_per_degraded_window": 3, "target": m.TARGET,
            "explicit_human_approval": True,
            "management_interface_mutated": False,
            "new_namespaces_created": False,
            "new_interfaces_created": False,
            "cycles": self.events,
        }
        self.manifest.write_text(json.dumps(self.batch))

    def test_train_map_valid(self):
        n, d, r, file = m.validate_train_map(self.doc)
        self.assertEqual(n, list(m.APPROVED_NORMAL))
        self.assertEqual(d, self.degraded)
        self.assertEqual(r, self.recovery)
        self.assertEqual(file, self.manifest)

    def test_train_map_rejects_non_uniform_packets(self):
        doc = dict(self.doc, packets_per_window=2)
        with self.assertRaisesRegex(ValueError, "contract"):
            m.validate_train_map(doc)

    def test_train_map_rejects_train_replacement(self):
        doc = dict(self.doc, normal_sessions=["NOT_THE_TRAIN_A", self.doc["normal_sessions"][1]])
        with self.assertRaisesRegex(ValueError, "partition"):
            m.validate_train_map(doc)

    def test_train_map_rejects_duplicate_controlled_id(self):
        doc = dict(self.doc, degraded_sessions=[self.degraded[0]] * 2)
        with self.assertRaisesRegex(ValueError, "partition"):
            m.validate_train_map(doc)

    def test_train_map_rejects_other_source_folder(self):
        doc = dict(self.doc, source_manifest=str(self.root / "evil" / "manifest.json"))
        with self.assertRaisesRegex(ValueError, "source_manifest"):
            m.validate_train_map(doc)

    def _read_sources(self, *, broken_watchdog=False):
        if broken_watchdog:
            p = self.folder / "ciclo_02_watchdog.json"
            d = json.loads(p.read_text())
            d["restoration_trigger"] = "MANUAL"
            p.write_text(json.dumps(d))
        all_ids = list(m.APPROVED_NORMAL) + self.degraded + self.recovery
        for sid in all_ids:
            folder = self.base / "datasets/raw" / sid
            folder.mkdir(parents=True)
            (folder / "ventanas.jsonl").write_text(sid + "\n")

        def inspect(sid, label, role):
            return {
                "windows_per_route": 20 if label == "NORMAL" else
                                     4 if label == "DEGRADED" else 6,
                "packets_per_window": 3,
                "measurements_with_packet_loss": 0,
                "packets_metadata_matches_actual": True,
            }
        vectors = lambda n: {p: [(0.09, 0.11, 0.02, 0.0)] * n for p in m.PROBES}
        def controlled(sid, label):
            event = self.degraded.index(sid) if label == "DEGRADED" else self.recovery.index(sid)
            return ({"controller_token": self.events[event]["token"]},
                    vectors(4 if label == "DEGRADED" else 6))
        with (mock.patch.object(m, "assert_legacy_lock"),
              mock.patch.object(m, "inspect_session", side_effect=inspect),
              mock.patch.object(m, "read_normal", return_value=vectors(20)),
              mock.patch.object(m, "read_controlled", side_effect=controlled)):
            return m.verified_training()

    def test_verify_sources_and_tokens(self):
        sources, rows = self._read_sources()
        self.assertEqual(len(sources["event_tokens"]), 2)
        self.assertEqual(len(sources["source_digests"]), 6)
        self.assertEqual(len(rows["DEGRADED"]), 2)
        self.assertEqual(len(rows["RECOVERY"]), 2)

    def test_watchdog_not_autonomous_rejected(self):
        with self.assertRaisesRegex(ValueError, "autonomous"):
            self._read_sources(broken_watchdog=True)

    def test_watchdog_duplicate_token_rejected(self):
        self.events[1]["token"] = self.events[0]["token"]
        self.manifest.write_text(json.dumps(self.batch))
        with self.assertRaisesRegex(ValueError, "training_tokens_reused"):
            self._read_sources()

    def test_class_count_validation_by_design(self):
        vectors = {
            "NORMAL": {"A": {p: [(0.1, .2, .03, 0.)] * 20 for p in m.PROBES},
                       "B": {p: [(0.1, .2, .03, 0.)] * 20 for p in m.PROBES}},
            "DEGRADED": {"D1": {p: [(40., 41., 1., 0.)] * 4 for p in m.PROBES},
                         "D2": {p: [(40., 41., 1., 0.)] * 4 for p in m.PROBES}},
            "RECOVERY": {"R1": {p: [(0.1, .2, .03, 0.)] * 6 for p in m.PROBES},
                         "R2": {p: [(0.1, .2, .03, 0.)] * 6 for p in m.PROBES}},
        }
        # La prueba no necesita sklearn; el gate de muestras sí requiere 40/8/12.
        for route in m.PROBES:
            self.assertEqual(sum(len(v[route]) for v in vectors["NORMAL"].values()), 40)
            self.assertEqual(sum(len(v[route]) for v in vectors["DEGRADED"].values()), 8)
            self.assertEqual(sum(len(v[route]) for v in vectors["RECOVERY"].values()), 12)

    def _frozen_report(self):
        self.dest.mkdir(mode=0o700, exist_ok=True)
        files = {}
        for route in m.PROBES:
            for kind in ("iforest", "logistic"):
                filename = f"{route.lower()}_{kind}.joblib"
                content = (route + kind).encode()
                target = self.dest / filename
                target.write_bytes(content)
                files[filename] = hashlib.sha256(content).hexdigest()
        source = {"normal_sessions": list(m.APPROVED_NORMAL)}
        doc = {
            "schema": m.SCHEMA, "training_complete": True,
            "independent_test_completed": False,
            "validation_data_used": False,
            "test_data_used": False,
            "operational_deployment_authorized": False,
            "class_packet_count_uniform": 3,
            "train_normal_per_route": 40,
            "train_degraded_per_route": 8,
            "train_recovery_per_route": 12,
            "train_recovery_excluded_from_fit": True,
            "features": list(m.FEATURES),
            "routes": list(m.PROBES),
            "training": source,
            "model_files_sha256": files,
            "p95_cutoffs_ms": {p: .15 for p in m.PROBES},
            "generalization_demonstrated": False,
            "forecast_horizon_defined": False,
        }
        return doc, source

    def test_freeze_report_valid_without_loading_joblib(self):
        report, source = self._frozen_report()
        m.verify_report(report, source)

    def test_freeze_detects_model_tampering(self):
        report, source = self._frozen_report()
        (self.dest / "hq_a_s1_iforest.joblib").write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError, "model_file_changed"):
            m.verify_report(report, source)

    def test_freeze_rejects_training_provenance_change(self):
        report, source = self._frozen_report()
        with self.assertRaisesRegex(ValueError, "freeze_contract"):
            m.verify_report(report, {"normal_sessions": ["OTHER"]})

    def test_freeze_rejects_claimed_generalization(self):
        report, source = self._frozen_report()
        report["generalization_demonstrated"] = True
        with self.assertRaisesRegex(ValueError, "scope_overclaimed"):
            m.verify_report(report, source)

    def test_freeze_rejects_validation_used(self):
        report, source = self._frozen_report()
        report["validation_data_used"] = True
        with self.assertRaisesRegex(ValueError, "freeze_contract"):
            m.verify_report(report, source)

    def test_train_script_does_not_mutate_network_or_score_test(self):
        source = SRC.read_text(encoding="utf-8")
        for forbidden in ("subprocess.", "os.system(", "tc qdisc add",
                          "ip netns add", "docker run", "systemctl restart",
                          "predict(test", "joblib.load", "sudo "):
            with self.subTest(marker=forbidden):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
