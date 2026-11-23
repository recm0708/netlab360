"""S06-041B: procedencia y train/test sin filtraciones, offline sin sklearn."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

FILE=Path(__file__).resolve().parents[1]/"scripts/s06/entrenar_baseline_anomalias.py"
SPEC=importlib.util.spec_from_file_location("s06_iforest_baseline",FILE)
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class BaselineMLTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        patch=mock.patch.object(m,"RAW",Path(self.temp.name))
        patch.start()
        self.addCleanup(patch.stop)

    def session(self, n=12, session="S06_WINDOW_NORMAL_20261123T070000Z_abc123",
                mutate=None):
        folder=m.RAW/session
        folder.mkdir(mode=0o700)
        lines=[]
        for j in range(1,n+1):
            r={
                "schema":m.SCHEMA,"session_id":session,
                "window_index":j,"recorded_at_utc":"2026-11-23T07:00:00+00:00",
                "ground_truth_label":"NORMAL","ground_truth_verified":True,
                "label_scope":"HQ_CLIENT_EGRESS_NETWORK_STATE",
                "qdisc_intervention_executed":False,
                "before":{"snapshot_valid":True},
                "after":{"snapshot_valid":True},
                "measurements":[
                    {"probe_id":name,"result":{
                        "measurement_valid":True,
                        "rtt_avg_ms":0.2,"rtt_p95_ms":0.3,
                        "rtt_mdev_ms":0.04,"loss_pct":0.0
                    }} for name in m.PROBES
                ]
            }
            if mutate and j==2:
                mutate(r)
            lines.append(r)
        raw="".join(json.dumps(x)+"\n" for x in lines)
        (folder/"ventanas.jsonl").write_text(raw)
        meta={
            "schema":m.SCHEMA,"session_id":session,"status":"complete",
            "samples_recorded":n,"verified":n,"stimulus":"NONE",
            "mutating_action_executed":False,
            "label_scope":"HQ_CLIENT_EGRESS_NETWORK_STATE",
            "training_ready":False,
            "data_digest_sha256":hashlib.sha256(raw.encode()).hexdigest()
        }
        (folder/"metadata.json").write_text(json.dumps(meta))
        return session

    def test_catalogo_no_contiene_ground_truth_como_feature(self):
        self.assertEqual(m.FEATURES,(
            "rtt_avg_ms","rtt_p95_ms","rtt_mdev_ms","loss_pct"))
        self.assertNotIn("qdisc_state",m.FEATURES)
        self.assertNotIn("ground_truth_label",m.FEATURES)

    def test_read_session_valida(self):
        id=self.session()
        rows=m.read_session(id)
        self.assertEqual(len(rows["HQ_A_S1"]),12)
        self.assertEqual(rows["HQ_A_S1"][0],(0.2,0.3,0.04,0.0))

    def test_hash_falso_bloquea(self):
        id=self.session()
        with (m.RAW/id/"ventanas.jsonl").open("a") as f:
            f.write("\n")
        with self.assertRaisesRegex(ValueError,"integra"):
            m.read_session(id)

    def test_ruta_ids_maliciosos_bloquea(self):
        for bad in ("../../root","", "S06_PERF_20261123T070000Z_abc123"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                m.read_session(bad)

    def test_symlink_rechazado(self):
        id=self.session()
        f=m.RAW/id/"ventanas.jsonl"
        real=m.RAW/id/"real.jsonl"
        f.rename(real)
        f.symlink_to(real)
        with self.assertRaisesRegex(ValueError,"symlink"):
            m.read_session(id)

    def test_unknown_no_se_entrena(self):
        id=self.session(mutate=lambda r:r.update(
            ground_truth_label="UNKNOWN",ground_truth_verified=False
        ))
        with self.assertRaisesRegex(ValueError,"no verificada"):
            m.read_session(id)

    def test_cambio_produccion_en_row_rechazado(self):
        id=self.session(mutate=lambda r:r.update(qdisc_intervention_executed=True))
        with self.assertRaises(ValueError):
            m.read_session(id)

    def test_snapshot_no_verificado_rechazado(self):
        id=self.session(mutate=lambda r:r["before"].update(snapshot_valid=False))
        with self.assertRaises(ValueError):
            m.read_session(id)

    def test_rtt_infinito_rechazado(self):
        id=self.session(mutate=lambda r:r["measurements"][0]["result"].update(
            rtt_avg_ms=float("inf")
        ))
        with self.assertRaisesRegex(ValueError,"Feature"):
            m.read_session(id)

    def test_sonda_ajena_rechazada(self):
        id=self.session(mutate=lambda r:r["measurements"][0].update(probe_id="EXTERNAL"))
        with self.assertRaises(ValueError):
            m.read_session(id)

    def test_indices_duplicados_rechazados(self):
        id=self.session(mutate=lambda r:r.update(window_index=1))
        with self.assertRaisesRegex(ValueError,"Ventana"):
            m.read_session(id)

    def test_menos_de_diez_ventanas_bloquea(self):
        id=self.session(n=5)
        with self.assertRaisesRegex(ValueError,"diez"):
            m.read_session(id)

    def test_percentile_95(self):
        value=m.percentile([1.0,2.0,3.0,4.0,5.0],95)
        self.assertAlmostEqual(value,4.8)

    def test_regla_p95_contabiliza_falsos_positivos(self):
        threshold,n=m.predict_threshold([(i,0,0,0) for i in (1.,2.,3.,4.,5.)],
                                        [(2,0,0,0),(8,0,0,0)])
        self.assertAlmostEqual(threshold,4.8)
        self.assertEqual(n,1)

    def test_train_test_misma_sesion_bloquea_antes_import_ml(self):
        id=self.session()
        with self.assertRaisesRegex(ValueError,"distintas"):
            m.analyze(id,id,id)

    def test_solo_clase_normal_no_hay_f1(self):
        s=FILE.read_text()
        self.assertIn('"recall_degraded": None',s)
        self.assertIn('"f1_degraded": None',s)
        self.assertIn('"training_ready_for_binary_classifier": False',s)


if __name__=="__main__":
    unittest.main()
