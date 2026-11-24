"""Aceptación de SDN: alcance del controlador, sin inferir puerto."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from ensayos_wan_sdn_s07 import assess,BACKUP

class ScopeTests(unittest.TestCase):
    def fixture(self):
        a={"window":{"temporal_gate":True,"rows":[{"event_id":"E","eligibility":"ELIGIBLE"}]},
           "batch":{"events":[{"event_id":"E","source":"NOC_S05","resource_id":"FAUCET","quality":"VALID",
              "observed_at_utc":"2026-11-24T05:00:00+00:00","state":"NORMAL","details":{"connected":True}}]}}
        r={"temporal_gate":True,"hypotheses":[],"network_mutations_authorized":False}
        rec={"approval_granted":False,"network_mutations_authorized":False}
        return a,r,rec
    def test_sdn_port_fault_not_controller_failure(self):
        self.assertEqual(assess("SDN","FAULT",*self.fixture()),(True,"MATCH"))
    def test_sdn_false_attribution(self):
        a,r,rec=self.fixture()
        r["hypotheses"]=[{"rule":"SDN_CONTROLLER_DEVIATION"}]
        self.assertEqual(assess("SDN","FAULT",a,r,rec)[1],"FALSE_CONTROLLER_ATTRIBUTION")
    def test_stale(self):
        self.assertEqual(assess("SDN","FAULT",*self.fixture(),"2026-11-24T05:00:01+00:00")[1],"CONTROLLER_NOT_VERIFIED_CONNECTED")
    def test_abstention(self):
        a,r,rec=self.fixture()
        r["temporal_gate"]=False
        self.assertEqual(assess("SDN","FAULT",a,r,rec)[1],"WINDOW_NOT_USABLE")
    def test_no_approval(self):
        a,r,rec=self.fixture()
        rec["approval_granted"]=True
        with self.assertRaisesRegex(ValueError,"ADVISORY_SCOPE_VIOLATED"):
            assess("SDN","FAULT",a,r,rec)
    def test_wan_missing_evidence(self):
        self.assertEqual(assess("WAN","FAULT",*self.fixture())[1],"WAN_ADMIN_NOT_MATCHED")
    def test_wan_expected_first_hops(self):
        self.assertEqual(BACKUP,{"FIB-HQ-S1","FIB-S1-HQ","FIB-S1-S2"})

if __name__=="__main__": unittest.main()
