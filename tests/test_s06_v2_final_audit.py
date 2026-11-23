"""S06-V2 final: pruebas offline de deriva y oportunidad de detección."""
from __future__ import annotations
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1] / "scripts/s06/auditar_resultados_v2_finales.py"
spec = importlib.util.spec_from_file_location("s06_v2_final_audit", SOURCE)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MockIF:
    def predict(self, rows):
        return [-1 if x[0] > 10 else 1 for x in rows]


class MockLR:
    def predict(self, rows):
        return [1 if x[0] > 10 else 0 for x in rows]


def vectors(length):
    return {r: [(0.1,.15,.02,0.)] * length for r in m.PROBES}


def tables(n):
    return {"S": vectors(n)}


class FinalAuditTests(unittest.TestCase):
    def test_ks_identical(self):
        self.assertEqual(m.ks([1.,2.,3.],[1.,2.,3.]),0)

    def test_ks_disjoint(self):
        self.assertEqual(m.ks([1.,1.],[2.,2.]),1)

    def test_ks_partial(self):
        self.assertEqual(m.ks([1.,2.],[2.,3.]), .5)

    def test_ks_rejects_one_sample(self):
        with self.assertRaisesRegex(ValueError,"requires|invalid"):
            m.ks([1.],[1.,2.])

    def test_ks_rejects_invalid(self):
        with self.assertRaisesRegex(ValueError,"invalid"):
            m.ks([float("nan"),1],[1,2])

    def test_datetime_utc_normal(self):
        d=m.utc("2026-11-23T15:35:35.200+00:00")
        self.assertEqual(d.tzinfo,timezone.utc)

    def test_datetime_z_supported(self):
        self.assertEqual(m.utc("2026-11-23T15:35:35Z").second,35)

    def test_datetime_offset_rejected(self):
        with self.assertRaisesRegex(ValueError,"not_utc"):
            m.utc("2026-11-23T10:35:35-05:00")

    def test_datetime_naive_rejected(self):
        with self.assertRaisesRegex(ValueError,"not_utc"):
            m.utc("2026-11-23T15:35:35")

    def test_drift_four_features_and_correct_sizes(self):
        result=m.drift(tables(40),tables(20),tables(20),m.PROBES[0])
        self.assertEqual(set(result),set(m.FEATURES))
        self.assertEqual(result["rtt_avg_ms"]["sample_sizes"],[40,20,20])
        self.assertEqual(result["rtt_avg_ms"]["ks_train_test"],0)
        self.assertEqual(result["rtt_avg_ms"]["inference"],
                         "DESCRIPTIVE_ONLY_NO_SIGNIFICANCE_CLAIM")

    def test_drift_wrong_counts_rejected(self):
        with self.assertRaisesRegex(ValueError,"split_sizes"):
            m.drift(tables(39),tables(20),tables(20),m.PROBES[0])

    def test_predictors_consistent(self):
        rows=[(.1,.2,.01,0.),(40.,40.5,.01,0.)]
        models={"iforest":MockIF(),"logistic":MockLR()}
        for name in m.METHODS:
            self.assertEqual(m.predicted(rows,name,1.,models),[0,1])

    def test_predictor_invalid_method(self):
        with self.assertRaisesRegex(ValueError,"unknown_method"):
            m.predicted([(.1,.2,.01,0.)],"TRAIN",1.,
                        {"iforest":MockIF(),"logistic":MockLR()})

    def test_event_latency_offline_not_online(self):
        sid="S06_WINDOW_DEGRADED_20261123T153534Z_abcdef"
        events=[]
        for i in range(1,5):
            events.append({
                "session_id":sid, "window_index":i,
                "ground_truth_label":"DEGRADED",
                "ground_truth_verified":True,
                "before":{"guard":{
                    "token":"0000000000000001",
                    "state":"APPLIED",
                    "applied_at_utc":"2026-11-23T15:35:34.000+00:00"}},
                "recorded_at_utc":(
                    "2026-11-23T15:35:34."
                    +f"{i*100:03d}"+ "+00:00"),
            })
        raw=("\n".join(json.dumps(x) for x in events)+"\n").encode()
        by={"DEGRADED":{sid:{route:[(40.,40.5,.1,0.)]*4
                               for route in m.PROBES}}}
        score={"metrics_by_route":{
            route:{"methods":{name:{"per_event_detected_windows":[4]}
                               for name in m.METHODS}}
            for route in m.PROBES}}
        with mock.patch.object(m,"read_regular",return_value=raw):
            result=m.event_opportunities(
                "test",m.PROBES[0],
                {"iforest":MockIF(),"logistic":MockLR()},1.,by,score)
        for name in m.METHODS:
            self.assertEqual(result[name][0]["first_detected_window"],1)
            self.assertEqual(result[name][0]["retrospective_detection_opportunity_ms"],100.)
            self.assertFalse(result[name][0]["true_online_alert_time_measured"])

    def test_event_not_premature(self):
        sid="S06_WINDOW_DEGRADED_20261123T153534Z_abcdef"
        event={
            "session_id":sid, "window_index":1,
            "ground_truth_label":"DEGRADED",
            "ground_truth_verified":True,
            "before":{"guard":{"token":"0"*16,"state":"APPLIED",
                "applied_at_utc":"2026-11-23T16:00:00+00:00"}},
            "recorded_at_utc":"2026-11-23T15:00:00+00:00"}
        raw=("\n".join(json.dumps(dict(event,window_index=i))
                       for i in range(1,5))+"\n").encode()
        rows={"DEGRADED":{sid:{r:[(40.,40.,.1,0.)]*4 for r in m.PROBES}}}
        with mock.patch.object(m,"read_regular",return_value=raw):
            with self.assertRaisesRegex(ValueError,"timestamps"):
                m.event_opportunities("test",m.PROBES[0],
                                     {"iforest":MockIF(),"logistic":MockLR()},
                                     1.,rows,{"metrics_by_route":{}})

    def test_code_no_mutation_or_fit(self):
        source=SOURCE.read_text()
        for forbidden in ("subprocess.", "systemctl restart", "tc qdisc add",
                          "sudo ", ".fit(", "docker run", "ip netns add",
                          "joblib.dump", "network_changes=True"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,source)


if __name__ == "__main__":
    unittest.main()
