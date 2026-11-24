"""Validación de aceptación de ventanas; fixtures aislados."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from ensayos_servicios_s07 import assess,CASES

class AcceptanceTests(unittest.TestCase):
    def fixture(self,case,stage):
        subject,resource,rule,ctx,action=CASES[case]
        fault=stage=="FAULT"
        details=({"status":"running","active_backend":"BACKEND_S1" if fault else "BACKEND_HQ",
                  "selected_path":"RESPALDO" if fault else "PRINCIPAL"} if case=="HTTP"
                 else {"switch_members":1 if fault else 2,"client_members":1 if fault else 2})
        e={"source":"NOC_S05","subject":subject,"resource_id":resource,"event_id":"E",
           "quality":"VALID","observed_at_utc":"2026-11-24T04:00:00+00:00",
           "state":"DEGRADED" if fault else "NORMAL","details":details}
        a={"batch":{"events":[e]},"window":{"temporal_gate":True,"rows":[{"event_id":"E","eligibility":"ELIGIBLE"}]}}
        r={"temporal_gate":True,"network_mutations_authorized":False,"hypotheses":[
            {"rule":rule,"context_id":ctx,"anchor_event_ids":["E"],"hypothesis_id":"H"}] if fault else []}
        rec={"approval_granted":False,"network_mutations_authorized":False,"recommendations":[
            {"hypothesis_id":"H","suggested_read_only_actions":[{"action_id":action}]}] if fault else []}
        return a,r,rec
    def test_six_phases(self):
        for c in CASES:
            for s in ("BASELINE","FAULT","RECOVERY"):
                self.assertEqual(assess(c,s,*self.fixture(c,s)),(True,"MATCH"))
    def test_old_observation(self):
        self.assertEqual(assess("HTTP","FAULT",*self.fixture("HTTP","FAULT"),
            "2026-11-24T04:00:01+00:00")[1],"TARGET_SAMPLE_PRECEDES_PHASE")
    def test_missing_signal(self):
        a,r,rec=self.fixture("LACP","FAULT")
        a["window"]["rows"][0]["eligibility"]="MISSING"
        self.assertEqual(assess("LACP","FAULT",a,r,rec)[1],"TARGET_UNKNOWN")
    def test_wrong_members(self):
        a,r,rec=self.fixture("LACP","FAULT")
        a["batch"]["events"][0]["details"]["client_members"]=2
        self.assertEqual(assess("LACP","FAULT",a,r,rec)[1],"LACP_STATE_NOT_MATCHED")
    def test_no_hypothesis(self):
        a,r,rec=self.fixture("HTTP","FAULT")
        r["hypotheses"]=[]
        self.assertEqual(assess("HTTP","FAULT",a,r,rec)[1],"TARGET_HYPOTHESIS_MISSING")
    def test_no_runbook(self):
        a,r,rec=self.fixture("HTTP","FAULT")
        rec["recommendations"]=[]
        self.assertEqual(assess("HTTP","FAULT",a,r,rec)[1],"TARGET_RUNBOOK_MISSING")
    def test_false_positive(self):
        a,r,rec=self.fixture("HTTP","BASELINE")
        r["hypotheses"]=self.fixture("HTTP","FAULT")[1]["hypotheses"]
        self.assertEqual(assess("HTTP","BASELINE",a,r,rec)[1],"TARGET_FALSE_POSITIVE")
    def test_mutation_denied(self):
        a,r,rec=self.fixture("HTTP","FAULT")
        rec["approval_granted"]=True
        with self.assertRaisesRegex(ValueError,"ADVISORY_SCOPE_VIOLATED"):
            assess("HTTP","FAULT",a,r,rec)

if __name__=="__main__": unittest.main()
