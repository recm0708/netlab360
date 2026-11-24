"""Pruebas del comparador histórico; fixtures sintéticos."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from comparar_ciclos_ospf import compare,evaluate,PROFILE,PREFIX,SUFFIX

def record(source):
    b={"costs":dict(PROFILE),"identity":dict.fromkeys(("HQ","S1","S2"),"fixture"),
       "neighbors":list(range(8)),"routes":list(range(6)),"icmp":list(range(6)),
       "http":{"status":"available","backend":"BACKEND_HQ"}}
    d=deepcopy(b)
    d["costs"]["S1/s1b"]=150
    states=PREFIX+(["APPROVED_RESTORE"] if source=="HUMAN_APPROVED" else [])+SUFFIX
    events=[]
    for i,state in enumerate(states):
        e={"state":state,"monotonic":float(i)}
        if state.startswith("APPROVED"): e["approver_uid"]=0
        if state in SUFFIX: e["source"]=source
        if state in ("DRIFT_APPLIED","RESTORING"): e["observed"]=150
        if state in ("RESTORED_UNVERIFIED","VERIFIED"): e["observed"]=100
        events.append(e)
    return {"ok":True,"transaction":{"schema":"NETLAB360_S07_OSPF_TRIAL_V1",
        "status":"VERIFIED","rfc_id":source,"target":"S1/s1b","baseline_cost":100,
        "drift_cost":150,"action_id":"S07_RESTORE_OSPF_COST_V1",
        "arguments":{"site":"S1","interface":"s1b","cost":100},"baseline":b,
        "drift_observation":d,"final_observation":deepcopy(b),"events":events}}

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.a=record("WATCHDOG")
        self.b=record("HUMAN_APPROVED")
    def test_valid_comparison(self):
        r=compare(self.a,self.b)
        self.assertFalse(r["statistical_generalization"])
        self.assertIsNone(r["results"][0]["decision_and_revalidation_s"])
        self.assertEqual(r["results"][1]["decision_and_revalidation_s"],1)
    def test_source_mismatch(self):
        with self.assertRaises(ValueError): evaluate(self.a,"HUMAN_APPROVED")
    def test_wrong_scope(self):
        self.a["transaction"]["drift_observation"]["costs"]["S1/s1p"]=20
        with self.assertRaisesRegex(ValueError,"DRIFT_OUTSIDE_SCOPE"): compare(self.a,self.b)
    def test_not_restored(self):
        self.b["transaction"]["final_observation"]["costs"]["S1/s1b"]=150
        with self.assertRaisesRegex(ValueError,"BASELINE_NOT_RESTORED"): compare(self.a,self.b)
    def test_order(self):
        self.a["transaction"]["events"][4]["monotonic"]=-1
        with self.assertRaisesRegex(ValueError,"CLOCK_INVALID"): compare(self.a,self.b)
    def test_duplicate(self):
        self.b["transaction"]["rfc_id"]=self.a["transaction"]["rfc_id"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_RFC"): compare(self.a,self.b)
    def test_missing_approval(self):
        self.b["transaction"]["events"].pop(6)
        with self.assertRaisesRegex(ValueError,"SEQUENCE_INVALID"): compare(self.a,self.b)
    def test_wrong_role(self):
        self.b["transaction"]["events"][6]["approver_uid"]=1000
        with self.assertRaisesRegex(ValueError,"RESTORE_NOT_APPROVED"): compare(self.a,self.b)
    def test_missing_http(self):
        self.a["transaction"]["baseline"]["http"]["status"]="offline"
        self.a["transaction"]["drift_observation"]["http"]["status"]="offline"
        self.a["transaction"]["final_observation"]["http"]["status"]="offline"
        with self.assertRaisesRegex(ValueError,"POSTCONDITIONS_INCOMPLETE"): compare(self.a,self.b)

if __name__=="__main__": unittest.main()
