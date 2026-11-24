"""Pruebas de persistencia y política preview sin privilegios."""
import concurrent.futures
import io
import json
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from rfc_protegido_preview import Store,ACTION,ARGS,TTL
import rfc_protegido_preview as broker

class ProtectedPreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"ledger.sqlite"
        self.now=1000
        self.uid=1234
        self.s=Store(self.path,self.uid,lambda:self.now)
    def request(self):
        r=self.s.handle(self.uid,{"op":"request","action_id":ACTION,"arguments":ARGS})
        self.assertTrue(r["ok"])
        return r["request"]
    def op(self,uid,op,b,**extra):
        return self.s.handle(uid,{"op":op,"rfc_id":b["rfc_id"],"body":b,**extra})
    def approve(self,b):
        return self.op(0,"approve",b,confirmation="APROBAR PREVIEW "+b["rfc_id"])
    def test_restart_and_consume(self):
        b=self.request()
        self.assertTrue(self.approve(b)["ok"])
        self.s=Store(self.path,self.uid,lambda:self.now)
        r=self.op(self.uid,"consume",b)
        self.assertEqual(r["result"],"PROTECTED_NOOP")
        self.assertFalse(r["execution_authorized"])
        self.assertFalse(self.op(self.uid,"consume",b)["ok"])
    def test_unknown_peer(self):
        self.assertFalse(self.s.handle(5678,{"op":"request","action_id":ACTION,"arguments":ARGS})["ok"])
    def test_self_approve(self):
        b=self.request()
        self.assertFalse(self.op(self.uid,"approve",b,confirmation="APROBAR PREVIEW "+b["rfc_id"])["ok"])
    def test_confirmation(self):
        self.assertFalse(self.op(0,"approve",self.request(),confirmation="yes")["ok"])
    def test_expiry(self):
        b=self.request()
        self.now+=TTL
        self.assertFalse(self.approve(b)["ok"])
    def test_modified(self):
        b=self.request()
        b["arguments"]["cost"]=150
        self.assertFalse(self.approve(b)["ok"])
    def test_cancel(self):
        b=self.request()
        self.approve(b)
        self.assertTrue(self.op(self.uid,"cancel",b)["ok"])
        self.assertFalse(self.op(self.uid,"consume",b)["ok"])
    def test_no_approval(self):
        self.assertFalse(self.op(self.uid,"consume",self.request())["ok"])
    def test_arbitrary_action(self):
        self.assertFalse(self.s.handle(self.uid,{"op":"request","action_id":"shell","arguments":{}})["ok"])
    def test_injection(self):
        self.assertFalse(self.s.handle(self.uid,{"op":"request","action_id":ACTION,"arguments":dict(ARGS,interface="ens33")})["ok"])
    def test_concurrent_consumption(self):
        b=self.request()
        self.approve(b)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            results=list(ex.map(lambda _:self.op(self.uid,"consume",b),range(2)))
        self.assertEqual(sum(r["ok"] for r in results),1)
    def test_audit_denial(self):
        b=self.request()
        self.op(self.uid,"consume",b)
        with self.s.connect() as c:
            self.assertEqual(c.execute("SELECT count(*) FROM audit WHERE event='DENIED'").fetchone()[0],1)
    def test_root_not_requester(self):
        self.assertFalse(self.s.handle(0,{"op":"request","action_id":ACTION,"arguments":ARGS})["ok"])
    def test_root_not_consumer(self):
        b=self.request()
        self.approve(b)
        self.assertFalse(self.op(0,"consume",b)["ok"])

    def test_cli_confirmation_json_stdout(self):
        body=self.request()
        rid=body["rfc_id"]
        out,err=io.StringIO(),io.StringIO()
        def route(msg):
            return self.s.handle(0,msg)
        with patch.object(sys,"argv",["broker","approve",rid]), patch.object(sys.stdin,"isatty",return_value=True), patch.object(broker.os,"geteuid",return_value=0), patch.object(broker,"call",side_effect=route), patch("builtins.input",return_value="APROBAR PREVIEW "+rid) as typed, redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as exc:
                broker.main()
        self.assertEqual(exc.exception.code,0)
        typed.assert_called_once_with()
        self.assertEqual(json.loads(out.getvalue())["status"],"APPROVED_PREVIEW")
        self.assertIn("Escriba APROBAR PREVIEW "+rid,err.getvalue())

    def test_cli_rejection_json_stdout(self):
        body=self.request()
        rid=body["rfc_id"]
        out,err=io.StringIO(),io.StringIO()
        with patch.object(sys,"argv",["broker","approve",rid]), patch.object(sys.stdin,"isatty",return_value=True), patch.object(broker.os,"geteuid",return_value=0), patch.object(broker,"call",side_effect=lambda msg:self.s.handle(0,msg)), patch("builtins.input",return_value="incorrecto"), redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as exc:
                broker.main()
        self.assertEqual(exc.exception.code,3)
        self.assertEqual(json.loads(out.getvalue())["reason"],"CONFIRMATION_REQUIRED")

if __name__=="__main__":
    unittest.main()
