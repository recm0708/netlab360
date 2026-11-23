"""S06-044: integridad/partición y métricas offline, sin sklearn ni red."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SRC = Path(__file__).resolve().parents[1] / "scripts/s06/evaluar_deteccion_binaria.py"
SPEC = importlib.util.spec_from_file_location("s06_binary_eval", SRC)
assert SPEC and SPEC.loader
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class BinaryEvaluationTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.temp = Path(t.name)
        raw = self.temp / "datasets/raw"
        raw.mkdir(parents=True)
        out = self.temp / "evaluaciones"
        manifest = self.temp / "experimentos/S06_043_20261123T073108Z_344e1e/manifest.json"
        manifest.parent.mkdir(parents=True)
        p = mock.patch.multiple(m, BASE=self.temp, RAW=raw,
                                OUT=out, SOURCE_MANIFEST=manifest)
        p.start()
        self.addCleanup(p.stop)

    def session(self, kind="DEGRADED", session=None, token="0123456789abcdef",
                corrupt=None, windows=4):
        if session is None:
            session=f"S06_WINDOW_{kind}_20261123T073344Z_abcdef"
        folder = m.RAW / session
        folder.mkdir()
        rows=[]
        for i in range(1,windows + 1):
            state = "APPLIED" if kind=="DEGRADED" else "RESTORED"
            qs = "OWN_NETEM" if kind=="DEGRADED" else "BASELINE"
            guard = {
                "state":state,"qdisc":qs,"token":token,
                "target":m.TARGET,"human_approval":True,
                "ground_truth_degraded_verified":True,
                "applied_at_utc":"2026-11-23T07:00:00+00:00",
                "expired_at_utc":"2026-11-23T07:00:35+00:00",
            }
            row = {
                "schema":m.WINDOW_SCHEMA,"session_id":session,
                "window_index":i,"ground_truth_label":kind,
                "ground_truth_verified":True,
                "label_scope":"HQ_CLIENT_EGRESS_NETWORK_STATE",
                "network_changes_by_collector":False,
                "before":{"routes_verified":True,"guard":dict(guard)},
                "after":{"routes_verified":True,"guard":dict(guard)},
                "measurements":[
                    {"probe_id":p, "result":{
                        "measurement_valid":True,"rtt_avg_ms":40.,
                        "rtt_p95_ms":40.5,"rtt_mdev_ms":.2,"loss_pct":0.
                    }} for p in m.PROBES
                ]
            }
            if i==1 and corrupt:
                corrupt(row)
            rows.append(row)
        raw = "".join(json.dumps(row)+"\n" for row in rows).encode()
        (folder/"ventanas.jsonl").write_bytes(raw)
        meta={
            "schema":m.WINDOW_SCHEMA, "session_id":session,
            "expected_class":kind,"controller_token":token,
            "status":"complete","training_ready":False,
            "network_changes_by_collector":False,
            "label_scope":"HQ_CLIENT_EGRESS_NETWORK_STATE",
            "samples_recorded":windows,"verified":windows,
            "unknown":0,"data_digest_sha256":hashlib.sha256(raw).hexdigest()
        }
        (folder/"metadata.json").write_text(json.dumps(meta))
        return session

    def test_features_solo_trafico(self):
        self.assertEqual(m.FEATURES,
            ("rtt_avg_ms","rtt_p95_ms","rtt_mdev_ms","loss_pct"))
        src = SRC.read_text()
        self.assertIn('"globally_chronological_holdout": False', src)
        self.assertIn('"production_deployment_authorized": False', src)

    def test_feature_row_valid(self):
        v={"measurement_valid":True,"rtt_avg_ms":10,
           "rtt_p95_ms":11,"rtt_mdev_ms":0.4,"loss_pct":0}
        self.assertEqual(m.feature_row(v),(10.,11.,.4,0.))

    def test_feature_row_no_admite_nan_inf_ni_negative(self):
        for x in (float("nan"),float("inf"),-1.,None,True):
            v={"measurement_valid":True,"rtt_avg_ms":x,
               "rtt_p95_ms":1,"rtt_mdev_ms":1,"loss_pct":0}
            with self.subTest(x=x),self.assertRaises(ValueError):
                m.feature_row(v)

    def test_controlled_valido(self):
        s=self.session()
        meta,v=m.read_controlled(s,"DEGRADED")
        self.assertEqual(meta["controller_token"],"0123456789abcdef")
        self.assertEqual(len(v["HQ_A_S1"]),4)

    def test_controlled_recovery_valido(self):
        s=self.session("RECOVERY",windows=6)
        _,v=m.read_controlled(s,"RECOVERY")
        self.assertEqual(len(v["HQ_A_S2"]),6)

    def test_invalid_name_rechazado(self):
        for x in ("../../etc/passwd","", "S06_WINDOW_UNKNOWN_X"):
            with self.subTest(x=x),self.assertRaises(ValueError):
                m.read_controlled(x,"DEGRADED")

    def test_unknown_rechazado(self):
        s=self.session(corrupt=lambda row: row.update(
            ground_truth_label="UNKNOWN",ground_truth_verified=False))
        with self.assertRaisesRegex(ValueError,"unverified"):
            m.read_controlled(s,"DEGRADED")

    def test_qdisc_foreign_rechazado(self):
        def corrupt(r):r["before"]["guard"]["qdisc"]="FOREIGN"
        s=self.session(corrupt=corrupt)
        with self.assertRaisesRegex(ValueError,"boundary"):
            m.read_controlled(s,"DEGRADED")

    def test_sin_human_approval_rechazado(self):
        def corrupt(r):r["after"]["guard"]["human_approval"]=False
        s=self.session(corrupt=corrupt)
        with self.assertRaisesRegex(ValueError,"boundary"):
            m.read_controlled(s,"DEGRADED")

    def test_etiqueta_no_basada_rtt(self):
        def corrupt(r):
            for x in r["measurements"]:
                x["result"]["rtt_avg_ms"]=0.001
        s=self.session(corrupt=corrupt)
        _,rows=m.read_controlled(s,"DEGRADED")
        self.assertEqual(rows["HQ_A_S1"][0][0],0.001)

    def test_alteracion_despues_de_checksum_rechazada(self):
        s=self.session()
        with (m.RAW/s/"ventanas.jsonl").open("a") as f:f.write(" ")
        with self.assertRaisesRegex(ValueError,"metadata"):
            m.read_controlled(s,"DEGRADED")

    def test_symlink_fuente_rechazado(self):
        s=self.session()
        f=m.RAW/s/"ventanas.jsonl"
        other=m.RAW/s/"other"
        f.rename(other)
        f.symlink_to(other)
        with self.assertRaisesRegex(ValueError,"symlink"):
            m.read_controlled(s,"DEGRADED")

    def test_token_invalido_rechazado(self):
        s=self.session(token="NOT_A_REAL_TOKEN")
        with self.assertRaisesRegex(ValueError,"token"):
            m.read_controlled(s,"DEGRADED")

    def test_indices_duplicados_rechazados(self):
        s=self.session(corrupt=lambda r:r.update(window_index=2))
        with self.assertRaises(ValueError):
            m.read_controlled(s,"DEGRADED")

    def test_confusion_counts_and_metrics(self):
        v=m.confusion([0,0,0,1,1],[0,1,0,1,0])
        self.assertEqual((v["tp"],v["fp"],v["tn"],v["fn"]), (1,1,2,1))
        self.assertAlmostEqual(v["precision"],0.5)
        self.assertAlmostEqual(v["recall"],0.5)
        self.assertAlmostEqual(v["f1"],0.5)

    def test_recall_0_no_divide(self):
        x=m.confusion([0,1],[0,0])
        self.assertEqual(x["f1"],0.0)

    def test_confusion_requires_both_classes(self):
        with self.assertRaises(ValueError):
            m.confusion([0,0],[0,0])

    def test_p95_from_train_only(self):
        self.assertAlmostEqual(m.p95([(float(x),0,0,0) for x in range(1,6)]),4.8)

    def test_split_reject_session_leakage(self):
        with self.assertRaisesRegex(ValueError,"overlap"):
            m.validate_split((m.NORMAL_A,m.NORMAL_TEST),
                             (m.DEGRADED_INITIAL,),m.NORMAL_TEST,
                             "S06_WINDOW_DEGRADED_20261123T080000Z_abcdef")

    def test_split_valido(self):
        m.validate_split((m.NORMAL_A,m.NORMAL_B),
                         (m.DEGRADED_INITIAL,),
                         m.NORMAL_TEST,
                         "S06_WINDOW_DEGRADED_20261123T080000Z_abcdef")

    def test_manifest_foreign_path_rechazado(self):
        foreign=self.temp/"manifest.json"
        foreign.write_text("{}")
        with self.assertRaisesRegex(ValueError,"pinned"):
            m.read_event_batches(foreign)

    def test_output_captura_delimitado(self):
        sample={"metrics_by_probe":{
            p:{"methods":{
                model:{"tp":4,"fp":0,"tn":20,"fn":0,
                       "precision":1., "recall":1., "f1":1.,
                       "recovery_false_alarms":0}
                for model in ("P95_RTT","IsolationForest","LogisticRegression")
            }} for p in m.PROBES
        }}
        t=m.capture_text(sample)
        self.assertTrue(t.startswith("========== INICIO CAPTURA S06_F06"))
        self.assertIn("FIN CAPTURA S06_F06",t)
        self.assertIn("GLOBAL_TIME_HOLDOUT=NO",t)
        self.assertIn("TEST_POSITIVOS=4_POR_RUTA",t)

    def test_no_red_mutation_code(self):
        s=SRC.read_text()
        for unsafe in ('"netns", "add"','"netns", "del"',
                       '"tc", "qdisc", "add"', "shell=True",
                       "subprocess.Popen(", "systemd-run"):
            self.assertNotIn(unsafe,s)


if __name__=="__main__":
    unittest.main()
