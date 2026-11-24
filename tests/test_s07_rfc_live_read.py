"""Pruebas de RFC live-read: observador simulado únicamente en pruebas."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from rfc_live_read import Store,ACTION,ARGS,RESTORE,RESTORE_ARGS,TTL

class LiveReadTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"rfc.sqlite3"
        self.now=1000.0
        self.observed_offset=0
        self.state={"costs":{"S1/s1b":100},"boot_id":"test-boot"}
        self.s=Store(self.path,1000,lambda:self.now,self.observe)
    def observe(self):
        return {"observed_at_utc":datetime.fromtimestamp(self.now+self.observed_offset,timezone.utc).isoformat(),
                "state":deepcopy(self.state),"source":"ROOT_OWNED_PREFLIGHT"}
    def request(self):
        r=self.s.handle(1000,{"op":"request","action_id":ACTION,"arguments":ARGS})
        self.assertTrue(r["ok"],r)
        return r["request"]
    def op(self,uid,op,b,**extra):
        return self.s.handle(uid,{"op":op,"rfc_id":b["rfc_id"],"body":b,**extra})
    def approve(self,b,uid=0):
        return self.op(uid,"approve",b,confirmation="APROBAR AUDITORIA "+b["rfc_id"])
    def test_cycle_live_read_contract(self):
        b=self.request()
        self.now+=1
        self.assertTrue(self.approve(b)["ok"])
        self.now+=1
        self.s=Store(self.path,1000,lambda:self.now,self.observe)
        r=self.op(1000,"consume",b)
        self.assertEqual(r["result"],"LIVE_AUDIT_VERIFIED")
        self.assertFalse(r["execution_authorized"])
        with self.s.connect() as c:
            self.assertEqual([x[0] for x in c.execute("SELECT stage FROM evidence ORDER BY seq")],["REQUEST","APPROVE","CONSUME"])
    def test_no_drift(self):
        self.assertEqual(self.s.handle(1000,{"op":"request","action_id":RESTORE,"arguments":RESTORE_ARGS})["reason"],"NO_VERIFIED_DRIFT")
    def test_drift_gate_closed(self):
        self.state["costs"]["S1/s1b"]=150
        self.assertEqual(self.s.handle(1000,{"op":"request","action_id":RESTORE,"arguments":RESTORE_ARGS})["reason"],"MUTATION_GATE_CLOSED")
    def test_stale(self):
        self.observed_offset=-11
        self.assertEqual(self.s.handle(1000,{"op":"request","action_id":ACTION,"arguments":ARGS})["reason"],"EVIDENCE_NOT_FRESH")
    def test_future(self):
        self.observed_offset=1
        self.assertEqual(self.s.handle(1000,{"op":"request","action_id":ACTION,"arguments":ARGS})["reason"],"EVIDENCE_NOT_FRESH")
    def test_stale_at_approval(self):
        b=self.request()
        self.observed_offset=-11
        self.assertEqual(self.approve(b)["reason"],"EVIDENCE_NOT_FRESH")
    def test_changed_at_approval(self):
        b=self.request()
        self.state["costs"]["S1/s1b"]=150
        self.assertEqual(self.approve(b)["reason"],"EXPECTED_STATE_CHANGED")
    def test_changed_at_consume(self):
        b=self.request()
        self.approve(b)
        self.state["boot_id"]="different"
        self.assertEqual(self.op(1000,"consume",b)["reason"],"EXPECTED_STATE_CHANGED")
    def test_expiry(self):
        b=self.request()
        self.now+=TTL
        self.assertEqual(self.approve(b)["reason"],"RFC_EXPIRED_OR_FUTURE")
    def test_self_approval(self):
        self.assertEqual(self.approve(self.request(),1000)["reason"],"ROLE_DENIED")
    def test_replay(self):
        b=self.request()
        self.approve(b)
        self.assertTrue(self.op(1000,"consume",b)["ok"])
        self.assertEqual(self.op(1000,"consume",b)["reason"],"RFC_STATE_DENIED")
    def test_client_evidence(self):
        self.assertEqual(self.s.handle(1000,{"op":"request","action_id":ACTION,"arguments":ARGS,"evidence":self.observe()})["reason"],"ACTION_OR_ARGUMENT_DENIED")
    def test_tampering(self):
        b=self.request()
        b["expected_state"]["costs"]["S1/s1b"]=150
        self.assertEqual(self.approve(b)["reason"],"RFC_BINDING_MISMATCH")
    def test_cancel(self):
        b=self.request()
        self.approve(b)
        self.assertTrue(self.op(1000,"cancel",b)["ok"])
        self.assertEqual(self.op(1000,"consume",b)["reason"],"RFC_STATE_DENIED")
    def test_no_approval(self):
        b=self.request()
        self.assertEqual(self.op(1000,"consume",b)["reason"],"RFC_STATE_DENIED")
    def test_preview_not_recognized(self):
        self.assertEqual(self.s.handle(1000,{"op":"show","rfc_id":"00000000-0000-0000-0000-000000000000"})["reason"],"RFC_UNKNOWN")
    def test_preflight_failure(self):
        def unavailable(): raise OSError("offline")
        self.s.observer=unavailable
        self.assertEqual(self.s.handle(1000,{"op":"request","action_id":ACTION,"arguments":ARGS})["reason"],"PREFLIGHT_UNAVAILABLE")

if __name__=="__main__":
    unittest.main()
