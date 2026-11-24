"""Pruebas sintéticas de clasificación y correlación, sin red."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import correlacion_evidencias as m
from test_s07_contexto_rca import acquisition
from test_s07_adquisicion_integrada import baseline, NOW
from contrato_eventos import make_event


def replace(b,source,resource,**changes):
    old=next(e for e in b["events"] if e["source"]==source and e["resource_id"]==resource)
    args={k:old[k] for k in ("source","subject","resource_id","site","peer_site","observed_at_utc","received_at_utc","state","details")}
    args["available"]=True
    args.update(changes)
    b["events"]=[make_event(**args) if e is old else e for e in b["events"]]
    return b


def evidence(r,source,resource):
    return next(e for e in r["evidence"] if e["source"]==source and e["resource_id"]==resource)


class EvidenceTests(unittest.TestCase):
    def test_baseline(self):
        r=m.correlate(acquisition())
        self.assertEqual(len(r["evidence"]),58)
        self.assertEqual(len(r["groups"]),18)
        self.assertTrue(all(e["usable"] for e in r["evidence"]))
        self.assertEqual(r["by_classification"]["OSPF_FULL"],8)
        self.assertEqual(r["by_classification"]["FIB_PRIMARY"],6)
        self.assertEqual(r["by_classification"]["ADMIN_UP"],30)
        self.assertIsNone(r["root_cause"])
        self.assertFalse(r["network_mutations_authorized"])

    def test_admin_not_operational(self):
        r=m.correlate(acquisition())
        e=evidence(r,"NOC_S05","WAN-PRIMARIA-HQ-S1")
        self.assertEqual((e["classification"],e["nature"]),("ADMIN_UP","ADMINISTRATIVE"))

    def test_missing_ia(self):
        b=baseline()
        for route in ("HQ_A_S1","HQ_A_S2"):
            replace(b,"IA_S06",route,available=False)
        r=m.correlate(acquisition(b))
        self.assertEqual(r["by_classification"]["UNAVAILABLE"],2)
        ids={e["event_id"] for e in r["evidence"] if not e["usable"]}
        self.assertTrue(all(not ids.intersection(p["event_ids"]) for p in r["pairs"]))

    def test_inconsistent_state(self):
        b=replace(baseline(),"FRR_S02","OSPF-HQ-s1p",state="DEGRADED")
        r=m.correlate(acquisition(b))
        e=evidence(r,"FRR_S02","OSPF-HQ-s1p")
        self.assertEqual(e["classification"],"INCONSISTENT")
        self.assertFalse(e["usable"])

    def test_admin_down_is_observation(self):
        b=replace(baseline(),"NOC_S05","WAN-PRIMARIA-HQ-S1",
                  details={"scope":"ADMIN_STATE_ONLY","admin_state":"admin-down"})
        self.assertEqual(evidence(m.correlate(acquisition(b)),"NOC_S05","WAN-PRIMARIA-HQ-S1")["classification"],"ADMIN_DOWN")

    def test_no_pairs_outside_limit(self):
        b=replace(baseline(),"FRR_S02","OSPF-HQ-s1p",observed_at_utc="2026-11-24T02:59:30Z")
        r=m.correlate(acquisition(b))
        e=evidence(r,"FRR_S02","OSPF-HQ-s1p")
        self.assertTrue(e["usable"])
        self.assertFalse(any(e["event_id"] in p["event_ids"] for p in r["pairs"]))

    def test_pairs_unique_and_scoped(self):
        r=m.correlate(acquisition())
        pairs={p["pair_id"]:p for p in r["pairs"]}
        self.assertEqual(len(pairs),len(r["pairs"]))
        for g in r["groups"]:
            for key in g["pair_ids"]:
                self.assertTrue(set(pairs[key]["event_ids"])<=set(g["event_ids"]))

    def test_shared_collector(self):
        r=m.correlate(acquisition())
        self.assertGreater(r["by_dependence"]["POTENTIALLY_SHARED_COLLECTOR"],0)
        self.assertNotIn("INDEPENDENT",r["by_dependence"])

    def test_bad_window_abstains(self):
        r=m.correlate(acquisition(end="2026-11-24T03:00:40Z",elapsed=41))
        self.assertEqual(r["pairs"],[])
        self.assertEqual(r["by_classification"],{"UNAVAILABLE":58})

    def test_fib_inconsistent_gateway(self):
        b=baseline()
        old=next(e for e in b["events"] if e["resource_id"]=="FIB-HQ-S1")
        replace(b,"FRR_S02","FIB-HQ-S1",details=dict(old["details"],gateway="10.78.0.99"))
        self.assertFalse(evidence(m.correlate(acquisition(b)),"FRR_S02","FIB-HQ-S1")["usable"])

    def test_http_backup_not_offline(self):
        b=replace(baseline(),"NOC_S05","FRONTAL_HQ",state="DEGRADED",
                  details={"scope":"HTTP_FROM_S2","status":"running","active_backend":"BACKEND_S1","selected_path":"RESPALDO"})
        self.assertEqual(evidence(m.correlate(acquisition(b)),"NOC_S05","FRONTAL_HQ")["classification"],"HTTP_BACKUP")

    def test_ia_inference_not_observation(self):
        e=evidence(m.correlate(acquisition()),"IA_S06","HQ_A_S1")
        self.assertEqual(e["nature"],"INFERENCE")


if __name__=="__main__":
    unittest.main()
