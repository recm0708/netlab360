"""Pruebas sintéticas de ventana y candidato; no acceden a la red."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import adquisicion_integrada as m
from contrato_incidentes import candidate,candidates
from contrato_eventos import make_event,normalize_batch
from test_s07_adaptadores_noc import graph,ia
from test_s07_adaptador_prometheus import fixture
from test_s07_adaptador_frr import record

START="2026-11-24T02:59:59Z"
END="2026-11-24T03:00:01Z"
NOW="2026-11-24T03:00:00Z"


def baseline():
    events=m.noc.graph_events(graph(),NOW)+m.noc.ia_events(ia(),NOW)
    events+=m.prom.project(fixture(),NOW)
    events += [e for site in m.frr.SITES for e in m.frr.project_site(site,record(site))]
    batch=normalize_batch(events)
    batch["mode"]="READ_ONLY"
    return batch


def signal(**changes):
    args=dict(source="FRR_S02",subject="OSPF",resource_id="OSPF-HQ-s1p",
              site="HQ",peer_site="S1",observed_at_utc="2026-11-24T02:59:59Z",
              received_at_utc=NOW,available=True,state="DEGRADED",
              details={"neighbor_state":"Init"})
    args.update(changes)
    return make_event(**args)


class WindowTests(unittest.TestCase):
    def test_inventory_and_baseline(self):
        b=baseline()
        w=m.evaluate_window(b,START,END,2)
        self.assertTrue(w["temporal_gate"])
        self.assertEqual(w["by_eligibility"],{"ELIGIBLE":58})
        self.assertFalse(w["simultaneous_measurement"])
        self.assertEqual(candidates({"batch":b,"window":w}),[])

    def test_missing_ia_not_global_fault(self):
        b=baseline()
        b["events"]=[e for e in b["events"] if e["source"]!="IA_S06"]+m.noc.ia_events(None,NOW)
        w=m.evaluate_window(b,START,END,2)
        self.assertEqual(w["by_eligibility"],{"ELIGIBLE":56,"MISSING":2})
        self.assertEqual(candidates({"batch":b,"window":w}),[])

    def test_long_window_not_eligible_for_rca(self):
        w=m.evaluate_window(baseline(),START,"2026-11-24T03:00:40Z",41)
        self.assertFalse(w["temporal_gate"])

    def test_clock_disagreement(self):
        with self.assertRaisesRegex(ValueError,"CLOCK"):
            m.evaluate_window(baseline(),START,END,100)

    def test_reception_outside_window(self):
        with self.assertRaisesRegex(ValueError,"RECEPTION"):
            m.evaluate_window(baseline(),"2026-11-24T03:00:00.5Z",END,.5)

    def test_incomplete_inventory(self):
        b=baseline()
        b["events"].pop()
        with self.assertRaisesRegex(ValueError,"INVENTORY"):
            m.evaluate_window(b,START,END,2)

    def test_duplicate_stream(self):
        b=baseline()
        b["events"]=[e for e in b["events"] if e["resource_id"]!="OSPF-HQ-s1b"]
        b["events"].append(signal())
        with self.assertRaisesRegex(ValueError,"INVENTORY"):
            m.evaluate_window(b,START,END,2)

    def test_quality_at_end_not_rewritten(self):
        e=signal()
        self.assertEqual(m.assess(e,"2026-11-24T03:01:01Z")[0],"STALE")
        self.assertEqual(e["quality"],"VALID")

    def test_tampered_window_rejected(self):
        b=baseline()
        w=m.evaluate_window(b,START,END,2)
        w["temporal_gate"]=False
        with self.assertRaisesRegex(ValueError,"MISMATCH"):
            candidates({"batch":b,"window":w})

    def test_candidate_observed_deviation(self):
        e=signal()
        c=candidate(e,END)
        self.assertEqual(c["status"],"CANDIDATE")
        self.assertFalse(c["confirmed"])
        self.assertEqual(c["evidence_event_ids"],[e["event_id"]])
        self.assertIsNone(c["root_cause"])
        self.assertFalse(c["network_mutations_authorized"])

    def test_candidate_id_stable(self):
        self.assertEqual(candidate(signal(),END)["incident_id"],
                         candidate(signal(),"2026-11-24T03:00:02Z")["incident_id"])

    def test_missing_normal_stale_not_candidate(self):
        self.assertIsNone(candidate(signal(available=False),END))
        self.assertIsNone(candidate(signal(state="NORMAL"),END))
        self.assertIsNone(candidate(signal(),"2026-11-24T03:02:00Z"))

    def test_unconfirmed_ia_candidate(self):
        e=signal(source="IA_S06",subject="ICMP_DIAGNOSIS",resource_id="HQ_A_S1",
                 state="UNKNOWN",details={"consensus":"DEGRADED"})
        c=candidate(e,END)
        self.assertEqual(c["reason"],"UNCONFIRMED_INFERENCE")
        self.assertFalse(c["confirmed"])

    def test_tampered_event_rejected(self):
        e=signal()
        e["network_mutations_authorized"]=True
        with self.assertRaises(ValueError):
            candidate(e,END)

    def test_failed_window_with_deviation_abstains(self):
        b=baseline()
        b["events"]=[signal() if e["resource_id"]=="OSPF-HQ-s1p" else e
                     for e in b["events"]]
        w=m.evaluate_window(b,START,"2026-11-24T03:00:40Z",41)
        self.assertEqual(candidates({"batch":b,"window":w}),[])


if __name__=="__main__":
    unittest.main()
