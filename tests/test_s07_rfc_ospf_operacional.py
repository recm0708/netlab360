"""Pruebas del broker operacional con backend aislado."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import ospf_trial as trial
from rfc_ospf_operacional import Broker,ACTIONS
from test_s07_ospf_trial import Backend

class OperationalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.b=Backend();self.now=1000;self.log=[]
        self.broker=Broker(trial,Path(self.tmp.name),self.b,deepcopy(self.b.state["costs"]),1000,
            lambda *args:self.log.append(args),lambda:self.now,protected=False)
        self.patch=mock.patch.object(trial,"boot_id",return_value="boot");self.patch.start();self.addCleanup(self.patch.stop)
    def request(self,uid=1000):
        action,args=ACTIONS["EXPERIMENT"]
        return self.broker.handle(uid,{"op":"request","action_id":action,"arguments":args})
    def approve(self,d,stage="EXPERIMENT",uid=0,alter=False):
        body=deepcopy(d["approvals"][stage]["binding"])
        if alter: body["arguments"]["site"]="HQ"
        return self.broker.handle(uid,{"op":"approve","rfc_id":d["rfc_id"],"binding":body,
                "confirmation":"APROBAR RFC "+body["approval_id"]})
    def cancel(self,d,stage="EXPERIMENT"):
        return self.broker.handle(1000,{"op":"cancel","rfc_id":d["rfc_id"],"binding":d["approvals"][stage]["binding"]})
    def restore_request(self,d):
        return self.broker.handle(1000,{"op":"request_restore","rfc_id":d["rfc_id"]})
    def test_complete_cycle(self):
        a=self.request();self.assertTrue(a["ok"])
        d=self.approve(a);self.assertEqual(d["status"],"DRIFT_VERIFIED")
        r=self.restore_request(d);self.assertTrue(r["ok"])
        f=self.approve(r,"RESTORE");self.assertEqual(f["status"],"VERIFIED")
        self.assertEqual(self.b.writes,[150,100])
        self.assertEqual(f["approvals"]["RESTORE"]["approver_uid"],0)
    def test_self_approval(self):
        self.assertEqual(self.approve(self.request(),uid=1000)["reason"],"ROLE_DENIED")
        self.assertEqual(self.b.writes,[])
    def test_root_request_denied(self):
        self.assertEqual(self.request(0)["reason"],"ROLE_DENIED")
    def test_tampering(self):
        self.assertEqual(self.approve(self.request(),alter=True)["reason"],"RFC_BINDING_MISMATCH")
        self.assertEqual(self.b.writes,[])
    def test_cancel(self):
        a=self.request();self.assertEqual(self.cancel(a)["status"],"CANCELLED")
        self.assertEqual(self.approve(a)["reason"],"RFC_STATE_DENIED")
        self.assertEqual(self.b.writes,[])
    def test_expiry(self):
        a=self.request();self.now+=trial.REQUEST_TTL
        self.assertEqual(self.approve(a)["reason"],"RFC_EXPIRED")
    def test_replay(self):
        a=self.request();self.approve(a)
        self.assertEqual(self.approve(a)["reason"],"RFC_STATE_DENIED")
        self.assertEqual(self.b.writes,[150])
    def test_restore_cancel_keeps_timer(self):
        a=self.approve(self.request());r=self.restore_request(a)
        self.assertEqual(self.cancel(r,"RESTORE")["approvals"]["RESTORE"]["status"],"CANCELLED")
        self.assertTrue(self.b.timer)
        self.assertEqual(self.approve(r,"RESTORE")["reason"],"RFC_STATE_DENIED")
        self.broker.trial(a["rfc_id"]).recover("WATCHDOG")
        self.assertEqual(self.b.writes,[150,100])
    def test_state_changed(self):
        a=self.request();self.b.state["costs"]["HQ/s1p"]=20
        self.assertEqual(self.approve(a)["reason"],"EXPECTED_STATE_CHANGED")
        self.assertEqual(self.b.writes,[])
    def test_request_restore_before_drift(self):
        self.assertEqual(self.restore_request(self.request())["reason"],"RFC_STATE_DENIED")
    def test_unknown_action(self):
        self.assertEqual(self.broker.handle(1000,{"op":"request","action_id":"shell","arguments":{}})["reason"],"ACTION_OR_ARGUMENT_DENIED")
    def test_client_evidence_denied(self):
        action,args=ACTIONS["EXPERIMENT"]
        self.assertEqual(self.broker.handle(1000,{"op":"request","action_id":action,"arguments":args,"evidence":{}})["reason"],"ACTION_OR_ARGUMENT_DENIED")
    def test_concurrent_transaction_denied(self):
        self.request();self.assertEqual(self.request()["reason"],"UNRESOLVED_TRANSACTION")
    def test_approval_audit(self):
        a=self.request();self.approve(a)
        self.assertTrue(any(x[0]==0 and x[2]=="APPROVAL_CONSUMED" for x in self.log))
    def test_restore_expiry(self):
        r=self.restore_request(self.approve(self.request()));self.now+=trial.WATCHDOG_TTL
        self.assertEqual(self.approve(r,"RESTORE")["reason"],"RFC_EXPIRED")
        self.assertEqual(self.b.writes,[150])
if __name__=="__main__": unittest.main()
