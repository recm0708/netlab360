"""Escenarios RCA sintéticos: no se escriben registros ni se toca la red."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from diagnostico_rca import diagnose
from auditoria_costos_rca import compare,desired
from adaptador_frr import SITES,LINKS,NAMES
from adaptadores_noc import METHODS
from test_s07_contexto_rca import acquisition
from test_s07_adquisicion_integrada import baseline
from test_s07_correlacion_evidencias import replace


def change(b,source,res,**kw):
    return replace(b,source,res,**kw)


def ospf(b,res):
    e=next(e for e in b["events"] if e["resource_id"]==res)
    return change(b,"FRR_S02",res,state="DEGRADED",details=dict(e["details"],neighbor_state="Init"))


def rules(b):
    return diagnose(acquisition(b))


def one(result,rule):
    return next(h for h in result["hypotheses"] if h["rule"]==rule)


class RcaTests(unittest.TestCase):
    def test_baseline(self):
        r=rules(baseline())
        self.assertEqual(r["status"],"NO_CANDIDATE")
        self.assertEqual(r["hypotheses"],[])
        self.assertIsNone(r["root_cause"])

    def test_missing_ia_not_fault(self):
        b=baseline()
        for route in ("HQ_A_S1","HQ_A_S2"):
            change(b,"IA_S06",route,available=False)
        r=rules(b)
        self.assertEqual(r["status"],"NO_CANDIDATE_WITH_GAPS")
        self.assertEqual(len(r["coverage_gaps"]),2)

    def test_ospf_nonfull_ambiguous(self):
        r=rules(ospf(baseline(),"OSPF-HQ-s1p"))
        h=one(r,"OSPF_ADJACENCY_DEVIATION")
        self.assertEqual(h["uncertainty"],"AMBIGUOUS")
        self.assertEqual(len(h["against_event_ids"]),1)
        self.assertEqual(h["context_id"],"WAN-HQ-S1-PRIMARY")

    def test_admin_down_and_ospf_deviation(self):
        b=ospf(baseline(),"OSPF-HQ-s1p")
        change(b,"NOC_S05","WAN-PRIMARIA-HQ-S1",details={"scope":"ADMIN_STATE_ONLY","admin_state":"admin-down"})
        h=one(rules(b),"WAN_ADMIN_DEVIATION")
        self.assertEqual(len(h["support_event_ids"]),2)
        self.assertTrue(h["against_event_ids"])

    def test_fib_backup_scoped(self):
        b=baseline()
        e=next(e for e in b["events"] if e["resource_id"]=="FIB-HQ-S1")
        change(b,"FRR_S02","FIB-HQ-S1",state="DEGRADED",details=dict(e["details"],interface="s1b",gateway="10.78.0.6",selection="BACKUP"))
        r=rules(b)
        self.assertEqual([h["rule"] for h in r["hypotheses"]],["FIB_BACKUP_SELECTED"])
        self.assertEqual(r["hypotheses"][0]["against_event_ids"],[])

    def test_http_backup(self):
        b=change(baseline(),"NOC_S05","FRONTAL_HQ",state="DEGRADED",details={"scope":"HTTP_FROM_S2","status":"running","active_backend":"BACKEND_S1","selected_path":"RESPALDO"})
        self.assertEqual([h["rule"] for h in rules(b)["hypotheses"]],["HTTP_BACKUP_SELECTED"])

    def test_http_offline(self):
        b=change(baseline(),"NOC_S05","FRONTAL_HQ",state="FAULT",details={"scope":"HTTP_FROM_S2","status":"offline","active_backend":None,"selected_path":None})
        self.assertEqual([h["rule"] for h in rules(b)["hypotheses"]],["HTTP_SERVICE_OFFLINE"])

    def test_lacp(self):
        b=change(baseline(),"NOC_S05","LACP-S1",state="DEGRADED",details={"scope":"BOND_MEMBER_STATE","switch_members":1,"client_members":2})
        self.assertEqual(one(rules(b),"LACP_MEMBER_DEVIATION")["context_id"],"SITE-S1")

    def test_sdn(self):
        b=change(baseline(),"NOC_S05","FAUCET",state="FAULT",details={"scope":"CONTROLLER_ONLY","connected":False,"flow_count":None})
        self.assertEqual([h["rule"] for h in rules(b)["hypotheses"]],["SDN_CONTROLLER_DEVIATION"])

    def test_ia_degraded(self):
        b=change(baseline(),"IA_S06","HQ_A_S1",state="UNKNOWN",details={"scope":"HQ_CLIENT_EGRESS_NETWORK_STATE","consensus":"DEGRADED",**{k:"DEGRADED" for k in METHODS}})
        self.assertEqual(one(rules(b),"ICMP_DEGRADATION_INDICATION")["uncertainty"],"LIMITED")

    def test_vlan_conflict(self):
        b=change(baseline(),"NOC_S05","VLAN-110",details={"scope":"ADMIN_STATE_ONLY","admin_state":"admin-down","vlan":110})
        h=one(rules(b),"VLAN_ADMIN_DEVIATION")
        self.assertEqual(h["uncertainty"],"AMBIGUOUS")
        self.assertEqual(len(h["against_event_ids"]),1)

    def test_distant_opposition_not_counted(self):
        b=ospf(baseline(),"OSPF-HQ-s1p")
        change(b,"FRR_S02","OSPF-S1-s1p",observed_at_utc="2026-11-24T02:59:30Z")
        h=one(rules(b),"OSPF_ADJACENCY_DEVIATION")
        self.assertEqual(h["against_event_ids"],[])

    def test_inconsistent_excluded(self):
        b=change(baseline(),"FRR_S02","OSPF-HQ-s1p",state="DEGRADED")
        self.assertEqual(rules(b)["hypotheses"],[])

    def test_window_abstention(self):
        r=diagnose(acquisition(ospf(baseline(),"OSPF-HQ-s1p"),end="2026-11-24T03:00:40Z",elapsed=41))
        self.assertEqual(r["status"],"ABSTAIN_WINDOW")
        self.assertEqual(r["hypotheses"],[])

    def test_composite_deterministic_no_mutations(self):
        b=ospf(baseline(),"OSPF-HQ-s1p")
        change(b,"NOC_S05","LACP-S1",state="DEGRADED",details={"scope":"BOND_MEMBER_STATE","switch_members":1,"client_members":1})
        change(b,"NOC_S05","FAUCET",state="FAULT",details={"scope":"CONTROLLER_ONLY","connected":False,"flow_count":None})
        r=rules(b)
        self.assertEqual(r,rules(b))
        self.assertEqual(len(r["hypotheses"]),3)
        self.assertEqual([h["rank"] for h in r["hypotheses"]],[1,2,3])
        self.assertTrue(all(not h["confirmed"] and not h["network_mutations_authorized"] for h in r["hypotheses"]))
        self.assertFalse(r["network_mutations_authorized"])

    def test_telemetry_not_network_fault(self):
        b=change(baseline(),"PROMETHEUS_S04","S04-EXPORTER",state="FAULT",details={"scope":"SCRAPE_AVAILABILITY","timestamp_scope":"PROMETHEUS_SCRAPE","up":0})
        self.assertEqual([h["rule"] for h in rules(b)["hypotheses"]],["TELEMETRY_ACQUISITION_DEVIATION"])

    def test_cost_compliant_and_drift(self):
        rows=compare("HQ",{"s1p":10,"s1b":100},{"s1p":10,"s1b":150},"2026-11-24T03:00:00Z")
        self.assertEqual({r["interface"]:r["status"] for r in rows},{"s1p":"COMPLIANT","s1b":"NON_COMPLIANT"})

    def test_missing_cost_unknown(self):
        self.assertEqual(compare("HQ",{"s1p":10},{} ,None)[0]["status"],"UNKNOWN")

    def test_sot_profile(self):
        s={"source_status":"candidate","devices":{"R-"+site:{"container":NAMES[site],"wan":[{"interface":i,"ospf_cost":10 if i.endswith("p") else 100} for i in LINKS[site]]} for site in SITES}}
        self.assertEqual(sum(len(v) for v in desired(s).values()),8)
        s["devices"]["R-HQ"]["wan"][0]["ospf_cost"]=999
        with self.assertRaises(ValueError):
            desired(s)


if __name__=="__main__":
    unittest.main()
