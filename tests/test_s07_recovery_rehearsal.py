"""Ensayos unitarios del watchdog y estados; sin operaciones de red."""
from pathlib import Path
from uuid import uuid4
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from recovery_rehearsal import Trial,plan,save,TTL,BASE,DRIFT,unit_name

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.clock=1000.0
        self.rid=uuid4().hex
        self.t=Trial(self.root,self.rid,"boot-a",lambda:self.clock)
        self.t.prepare()
    def test_plan(self):
        p=plan()
        self.assertEqual(p["arguments"],{"site":"S1","interface":"s1b","cost":100})
        self.assertFalse(p["network_executor_enabled"])
        self.assertFalse(p["network_mutations_authorized"])
    def test_full_cycle(self):
        self.t.arm(True)
        self.t.apply(True)
        self.assertEqual(self.t.value(),DRIFT)
        self.clock+=TTL
        recovered=Trial(self.root,self.rid,"boot-a",lambda:self.clock)
        recovered.recover()
        self.assertEqual(recovered.value(),BASE)
        self.assertEqual(recovered.load()["status"],"RECOVERED")
    def test_apply_before_arm(self):
        with self.assertRaisesRegex(ValueError,"WATCHDOG_NOT_READY"): self.t.apply(True)
        self.assertEqual(self.t.value(),BASE)
    def test_timer_inactive(self):
        with self.assertRaisesRegex(ValueError,"WATCHDOG_NOT_READY"): self.t.arm(False)
    def test_timer_lost(self):
        self.t.arm(True)
        with self.assertRaisesRegex(ValueError,"WATCHDOG_NOT_READY"): self.t.apply(False)
    def test_deadline(self):
        self.t.arm(True)
        self.clock+=TTL
        with self.assertRaisesRegex(ValueError,"WATCHDOG_NOT_READY"): self.t.apply(True)
    def test_interrupted_apply(self):
        self.t.arm(True)
        d=self.t.load()
        self.t.event(d,"APPLYING")
        save(self.t.fixture,{"run_id":self.rid,"cost":DRIFT})
        self.t.recover()
        self.assertEqual(self.t.value(),BASE)
    def test_interrupted_recovery(self):
        self.t.arm(True)
        self.t.apply(True)
        self.t.event(self.t.load(),"RECOVERING")
        save(self.t.fixture,{"run_id":self.rid,"cost":BASE})
        self.t.recover()
        self.assertEqual(self.t.load()["status"],"RECOVERED")
    def test_noop_restore(self):
        self.t.arm(True)
        self.t.recover()
        self.assertEqual(self.t.value(),BASE)
    def test_repeated_recovery(self):
        self.t.arm(True)
        self.t.apply(True)
        d=self.t.recover()
        self.assertEqual(self.t.recover(),d)
    def test_unexpected_cost(self):
        self.t.arm(True)
        save(self.t.fixture,{"run_id":self.rid,"cost":200})
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_STATE"): self.t.recover()
        self.assertEqual(self.t.load()["status"],"ESCALATION_REQUIRED")
    def test_wrong_boot(self):
        with self.assertRaisesRegex(ValueError,"TRANSACTION_BINDING_INVALID"):
            Trial(self.root,self.rid,"boot-b",lambda:self.clock).recover()
    def test_wrong_fixture(self):
        self.t.arm(True)
        save(self.t.fixture,{"run_id":"other","cost":DRIFT})
        with self.assertRaisesRegex(ValueError,"FIXTURE_BINDING_INVALID"): self.t.recover()
    def test_bad_run_id(self):
        with self.assertRaisesRegex(ValueError,"INVALID_RUN_ID"): unit_name("../other")

if __name__=="__main__":
    unittest.main()
