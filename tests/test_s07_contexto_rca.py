"""Pruebas de contexto RCA con fixtures sintéticos; sin acceso a red."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import contexto_rca as m
from adquisicion_integrada import evaluate_window
from contrato_eventos import make_event
from test_s07_adquisicion_integrada import baseline,START,END,NOW


def acquisition(batch=None,end=END,elapsed=2):
    b=baseline() if batch is None else batch
    return {"batch":b,"window":evaluate_window(b,START,end,elapsed)}


class ContextTests(unittest.TestCase):
    def test_inventory(self):
        rows,groups=m.inventory()
        self.assertEqual(len(rows),58)
        self.assertEqual(len(groups),18)
        self.assertEqual({k for g in groups.values() for k in g["references"]},set(rows))

    def test_baseline(self):
        result=m.build_context(acquisition())
        self.assertEqual(result["unique_signals"],58)
        self.assertEqual(len(result["groups"]),18)
        self.assertTrue(all(g["eligible"]==g["total"] for g in result["groups"]))
        self.assertIsNone(result["root_cause"])
        self.assertFalse(result["network_mutations_authorized"])

    def test_wan_scope(self):
        r=m.build_context(acquisition())
        g=next(g for g in r["groups"] if g["context_id"]=="WAN-HQ-S1-PRIMARY")
        self.assertEqual(g["total"],5)
        self.assertEqual({x["resource_id"] for x in g["references"]},
                         {"WAN-PRIMARIA-HQ-S1","WAN-END-HQ-s1p","WAN-END-S1-s1p","OSPF-HQ-s1p","OSPF-S1-s1p"})

    def test_route_scope(self):
        g=next(g for g in m.build_context(acquisition())["groups"]
               if g["context_id"]=="ROUTE-S1-S2")
        self.assertEqual(g["total"],11)
        self.assertNotIn("OSPF-HQ-s2p",{x["resource_id"] for x in g["references"]})

    def test_separate_service_scopes(self):
        groups={g["context_id"]:g for g in m.build_context(acquisition())["groups"]}
        self.assertEqual(groups["HTTP-HA"]["total"],1)
        self.assertEqual(groups["SDN-FAUCET"]["total"],1)

    def test_unknown_source_identity_rejected(self):
        b=baseline()
        old=next(e for e in b["events"] if e["resource_id"]=="LACP-HQ")
        new=make_event(source=old["source"],subject=old["subject"],resource_id="LACP-OTHER",
                       site=old["site"],observed_at_utc=old["observed_at_utc"],
                       received_at_utc=old["received_at_utc"],state="NORMAL",available=True)
        b["events"]=[new if e is old else e for e in b["events"]]
        with self.assertRaisesRegex(ValueError,"RESOURCE_MISMATCH"):
            m.build_context(acquisition(b))

    def test_wrong_site_rejected(self):
        b=baseline()
        old=next(e for e in b["events"] if e["resource_id"]=="LACP-HQ")
        new=make_event(source=old["source"],subject=old["subject"],resource_id=old["resource_id"],
                       site="S2",observed_at_utc=old["observed_at_utc"],
                       received_at_utc=old["received_at_utc"],state="NORMAL",available=True)
        b["events"]=[new if e is old else e for e in b["events"]]
        with self.assertRaisesRegex(ValueError,"RESOURCE_MISMATCH"):
            m.build_context(acquisition(b))

    def test_bad_window_disables_all_refs(self):
        r=m.build_context(acquisition(end="2026-11-24T03:00:40Z",elapsed=41))
        self.assertFalse(r["temporal_gate"])
        self.assertTrue(all(g["eligible"]==0 for g in r["groups"]))
        self.assertTrue(all(x["state"]=="UNKNOWN" for g in r["groups"] for x in g["references"]))

    def test_missing_ia_retained(self):
        from adaptadores_noc import ia_events
        b=baseline()
        b["events"]=[e for e in b["events"] if e["source"]!="IA_S06"]+ia_events(None,NOW)
        r=m.build_context(acquisition(b))
        self.assertEqual(r["unique_signals"],58)
        self.assertTrue(all(g["eligible"]==0 for g in r["groups"] if g["kind"]=="ICMP_INFERENCE"))

    def test_tampered_window_rejected(self):
        a=acquisition()
        a["window"]["temporal_gate"]=False
        with self.assertRaisesRegex(ValueError,"WINDOW_CONTRACT"):
            m.build_context(a)


if __name__=="__main__":
    unittest.main()
