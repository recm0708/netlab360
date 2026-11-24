"""Pruebas de Intent Assurance y RFC de simulación, sin privilegios."""
from pathlib import Path
from copy import deepcopy
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from intent_assurance import evaluate
from rfc_simulacion import Ledger,ACTION
from adaptador_frr import LINKS
from test_s07_contexto_rca import acquisition
from test_s07_adquisicion_integrada import baseline
from test_s07_diagnostico_rca import change,ospf

STAMP="2026-11-24T03:00:02Z"
NOW="2026-11-24T03:00:03Z"
ARGS={"site":"S1","interface":"s1b","cost":100}
REQ="TEST_REQUESTER"
APP="TEST_APPROVER"


def audit(drift=False):
    rows=[]
    for site,links in LINKS.items():
        for i in links:
            cost=10 if i.endswith("p") else 100
            got=150 if drift and (site,i)==("S1","s1b") else cost
            rows.append({"site":site,"interface":i,"expected":cost,"observed":got,
                         "status":"COMPLIANT" if cost==got else "NON_COMPLIANT","observed_at_utc":STAMP})
    return {"schema":"NETLAB360_S07_CONFIG_AUDIT_V1","reference":"S03_CANDIDATE_SOT_MATCHED_S02_COST_PROFILE",
            "started_at_utc":STAMP,"ended_at_utc":STAMP,"rows":rows,
            "network_mutations_authorized":False,"historical_rca_causal_link":False}


def fixture(drift=True,b=None):
    return evaluate(acquisition(b),audit(drift))


def requested():
    l=Ledger()
    return l,l.request(REQ,ACTION,ARGS,fixture(),NOW)


class IntentTests(unittest.TestCase):
    def test_baseline(self):
        r=fixture(False)
        self.assertEqual(r["configuration_compliance"],"MET")
        self.assertEqual(r["preferred_route_intent"],"MET")
        self.assertEqual(r["http_observed_availability"],"MET")
        self.assertEqual(r["end_to_end_availability"],"NOT_MEASURED")
        self.assertTrue(r["temporally_aligned"])

    def test_drift_but_available(self):
        r=fixture()
        self.assertEqual(r["configuration_compliance"],"NOT_MET")
        self.assertEqual(r["preferred_route_intent"],"MET")
        self.assertEqual(r["http_observed_availability"],"MET")

    def test_operational_failure_compliant(self):
        r=fixture(False,ospf(baseline(),"OSPF-HQ-s1p"))
        self.assertEqual(r["configuration_compliance"],"MET")
        self.assertEqual(r["ospf_adjacency_intent"],"NOT_MET")

    def test_valid_configuration_intent_not_met(self):
        b=baseline()
        e=next(e for e in b["events"] if e["resource_id"]=="FIB-HQ-S1")
        change(b,"FRR_S02","FIB-HQ-S1",state="DEGRADED",details=dict(e["details"],interface="s1b",gateway="10.78.0.6",selection="BACKUP"))
        r=fixture(False,b)
        self.assertEqual(r["configuration_compliance"],"MET")
        self.assertEqual(r["preferred_route_intent"],"NOT_MET")

    def test_unknown_cost(self):
        a=audit()
        a["rows"][0].update(observed=None,status="UNKNOWN")
        self.assertEqual(evaluate(acquisition(),a)["configuration_compliance"],"UNKNOWN")

    def test_forged_status(self):
        a=audit()
        a["rows"][0]["status"]="NON_COMPLIANT"
        with self.assertRaises(ValueError): evaluate(acquisition(),a)

    def test_duplicate_cost(self):
        a=audit()
        a["rows"].append(a["rows"][0])
        with self.assertRaises(ValueError): evaluate(acquisition(),a)


class RfcTests(unittest.TestCase):
    def test_full_simulated_cycle(self):
        l,r=requested()
        l.approve(APP,r,NOW)
        result=l.consume_preview(REQ,r,fixture(),NOW)
        self.assertEqual(result["status"],"SIMULATED_NOOP")
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(len(l.snapshot()["audit"]),3)

    def test_self_approval(self):
        l,r=requested()
        with self.assertRaises(ValueError): l.approve(REQ,r,NOW)

    def test_unrecognized_actor(self):
        with self.assertRaises(ValueError): Ledger().request("guest",ACTION,ARGS,fixture(),NOW)

    def test_no_drift(self):
        with self.assertRaises(ValueError): Ledger().request(REQ,ACTION,ARGS,fixture(False),NOW)

    def test_operational_fault_blocks(self):
        with self.assertRaises(ValueError): Ledger().request(REQ,ACTION,ARGS,fixture(True,ospf(baseline(),"OSPF-HQ-s1p")),NOW)

    def test_expired(self):
        l,r=requested()
        with self.assertRaises(ValueError): l.approve(APP,r,"2026-11-24T03:01:03Z")

    def test_altered(self):
        l,r=requested()
        r["arguments"]["cost"]=10
        with self.assertRaises(ValueError): l.approve(APP,r,NOW)

    def test_unapproved(self):
        l,r=requested()
        with self.assertRaises(ValueError): l.consume_preview(REQ,r,fixture(),NOW)

    def test_replay(self):
        l,r=requested()
        l.approve(APP,r,NOW)
        l.consume_preview(REQ,r,fixture(),NOW)
        with self.assertRaises(ValueError): l.consume_preview(REQ,r,fixture(),NOW)

    def test_cancel(self):
        l,r=requested()
        l.approve(APP,r,NOW)
        l.cancel(REQ,r,NOW)
        self.assertEqual(l.snapshot()["records"][0]["status"],"CANCELLED")
        with self.assertRaises(ValueError): l.consume_preview(REQ,r,fixture(),NOW)

    def test_expected_state_changed(self):
        l,r=requested()
        l.approve(APP,r,NOW)
        a=audit(True)
        next(x for x in a["rows"] if (x["site"],x["interface"])==("S1","s1b"))["observed"]=160
        with self.assertRaises(ValueError): l.consume_preview(REQ,r,evaluate(acquisition(),a),NOW)

    def test_stale_evidence(self):
        with self.assertRaises(ValueError): Ledger().request(REQ,ACTION,ARGS,fixture(),"2026-11-24T03:00:40Z")

    def test_scope_management(self):
        with self.assertRaises(ValueError): Ledger().request(REQ,ACTION,{"site":"HQ","interface":"ens33","cost":10},fixture(),NOW)

    def test_unknown_action(self):
        with self.assertRaises(ValueError): Ledger().request(REQ,"shell",{},fixture(),NOW)


if __name__=="__main__":
    unittest.main()
