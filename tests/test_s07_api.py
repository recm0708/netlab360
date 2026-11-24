"""Contrato API, idempotencia y autorización sin red real."""
from contextlib import nullcontext
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from api_s07 import API,Replay,response

class APITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.b=Mock();self.b.uid=1000
        self.b.handle.return_value={"ok":True,"status":"PENDING"}
        self.r=Replay(Path(self.tmp.name)/"idem.db")
        self.api=API(self.b,self.r,{"observed_at_utc":"test","incidents":[],"hypotheses":[],"runbooks":{}},lambda:[],nullcontext)
        self.path="/api/v1/rfcs";self.body={"action_id":"fixed","arguments":{}}
        self.key="test_key_00000001";self.rid="a"*32
    def test_peer(self):
        self.assertEqual(self.api.dispatch(1001,"GET","/api/v1/health")[0],403)
    def test_advisory_untrusted(self):
        self.assertFalse(self.api.dispatch(1000,"GET","/api/v1/incidents")[1]["result"]["authorization_evidence"])
    def test_unknown_route(self):
        self.assertEqual(self.api.dispatch(1000,"GET","/api/v1/shell")[0],404)
    def test_method(self):
        self.assertEqual(self.api.dispatch(1000,"DELETE",self.path)[0],405)
    def test_role_approve(self):
        self.assertEqual(self.api.dispatch(1000,"POST",self.path+"/"+self.rid+"/approve-execute",{"binding":{},"confirmation":"x"},self.key)[0],403)
        self.b.handle.assert_not_called()
    def test_root_request(self):
        self.assertEqual(self.api.dispatch(0,"POST",self.path,self.body,self.key)[0],403)
    def test_schema(self):
        self.assertEqual(self.api.dispatch(1000,"POST",self.path,{**self.body,"shell":"x"},self.key)[0],400)
    def test_key_required(self):
        self.assertEqual(self.api.dispatch(1000,"POST",self.path,self.body)[0],400)
    def test_replay(self):
        a=self.api.dispatch(1000,"POST",self.path,self.body,self.key)
        self.assertEqual(a,self.api.dispatch(1000,"POST",self.path,self.body,self.key))
        self.b.handle.assert_called_once()
    def test_conflict(self):
        self.api.dispatch(1000,"POST",self.path,self.body,self.key)
        self.assertEqual(self.api.dispatch(1000,"POST",self.path,{"action_id":"other","arguments":{}},self.key)[1]["reason"],"IDEMPOTENCY_CONFLICT")
        self.b.handle.assert_called_once()
    def test_persisted(self):
        a=self.api.dispatch(1000,"POST",self.path,self.body,self.key)
        self.api.replay=Replay(self.r.path)
        self.assertEqual(a,self.api.dispatch(1000,"POST",self.path,self.body,self.key))
        self.b.handle.assert_called_once()
    def test_uncertain(self):
        def fail(): raise RuntimeError("interrupted")
        with self.assertRaises(RuntimeError): self.r.apply(1000,self.path,self.key,self.body,fail)
        self.assertEqual(self.r.apply(1000,self.path,self.key,self.body,lambda:response(200,ok=True))[1]["reason"],"OUTCOME_UNCERTAIN_RECONCILE")
    def test_no_free_execution(self):
        self.assertEqual(self.api.dispatch(0,"POST",self.path+"/"+self.rid+"/execute",{},self.key)[0],404)
    def test_broker_denial(self):
        self.b.handle.return_value={"ok":False,"reason":"ACTION_OR_ARGUMENT_DENIED"}
        self.assertEqual(self.api.dispatch(1000,"POST",self.path,self.body,self.key)[0],409)
if __name__=="__main__": unittest.main()
