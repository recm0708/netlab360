"""Pruebas de transiciones del ensayo real, con backend falso sin red."""
from copy import deepcopy
from pathlib import Path
from uuid import uuid4
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from ospf_trial import Trial,TARGET,BASE,DRIFT,unit,REQUEST_TTL,WATCHDOG_TTL

class Backend:
    def __init__(self):
        self.state={"costs":{TARGET:BASE,"HQ/s1p":10},"identity":{"S1":"session"},"boot_id":"boot"}
        self.timer=False
        self.writes=[]
    def snapshot(self): return deepcopy(self.state)
    def cost(self,expected):
        if self.state["identity"]!=expected["identity"]: raise ValueError("TARGET_SESSION_CHANGED")
        return self.state["costs"][TARGET]
    def change(self,expected,before,after):
        if self.cost(expected)!=before: raise ValueError("EXPECTED_COST_CHANGED")
        self.state["costs"][TARGET]=after
        self.writes.append(after)
    def arm(self,rid): self.timer=True; return True
    def timer_active(self,rid): return self.timer

class TrialTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.b=Backend()
        self.now=1000
        self.rid=uuid4().hex
        self.t=Trial(Path(self.temp.name),self.rid,self.b,lambda:self.now)
        self.t.request(1000,deepcopy(self.b.state["costs"]))
    def start(self): return self.t.start("APROBAR ENSAYO "+self.rid)
    def restore(self): return self.t.restore("APROBAR RESTAURACION "+self.rid)
    def test_approved_cycle(self):
        self.start()
        self.assertEqual(self.restore()["status"],"VERIFIED")
        self.assertEqual(self.b.writes,[150,100])
    def test_wrong_confirmation(self):
        with self.assertRaisesRegex(ValueError,"APPROVAL_DENIED"): self.t.start("yes")
        self.assertEqual(self.b.writes,[])
    def test_expired(self):
        self.now+=REQUEST_TTL
        with self.assertRaisesRegex(ValueError,"RFC_EXPIRED"): self.start()
        self.assertEqual(self.b.writes,[])
    def test_state_changed(self):
        self.b.state["costs"]["HQ/s1p"]=20
        with self.assertRaisesRegex(ValueError,"EXPECTED_STATE_CHANGED"): self.start()
        self.assertEqual(self.b.writes,[])
    def test_timer_not_armed(self):
        self.b.arm=lambda _:False
        with self.assertRaisesRegex(ValueError,"WATCHDOG_NOT_READY"): self.start()
        self.assertEqual(self.b.writes,[])
    def test_timer_lost(self):
        self.b.timer_active=lambda _:False
        with self.assertRaisesRegex(ValueError,"WATCHDOG_NOT_READY"): self.start()
        self.assertEqual(self.b.writes,[])
    def test_watchdog(self):
        self.start()
        self.now+=WATCHDOG_TTL
        self.assertEqual(self.t.recover("WATCHDOG")["status"],"VERIFIED")
        self.assertEqual(self.b.writes,[150,100])
    def test_restore_without_start(self):
        with self.assertRaisesRegex(ValueError,"RESTORATION_APPROVAL_DENIED"): self.restore()
    def test_restore_expiring(self):
        self.start()
        self.now+=WATCHDOG_TTL
        with self.assertRaisesRegex(ValueError,"WATCHDOG_DEADLINE_NEAR"): self.restore()
        self.t.recover("WATCHDOG")
        self.assertEqual(self.b.writes,[150,100])
    def test_replay(self):
        self.start()
        self.restore()
        with self.assertRaisesRegex(ValueError,"APPROVAL_DENIED"): self.start()
        self.t.recover("WATCHDOG")
        self.assertEqual(self.b.writes,[150,100])
    def test_unexpected_cost(self):
        self.start()
        self.b.state["costs"][TARGET]=200
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_TARGET_COST"): self.t.recover("WATCHDOG")
        self.assertEqual(self.t.load()["status"],"ESCALATION_REQUIRED")
        self.assertEqual(self.b.writes,[150])
    def test_wrong_session(self):
        self.start()
        self.b.state["identity"]["S1"]="other"
        with self.assertRaisesRegex(ValueError,"TARGET_SESSION_CHANGED"): self.t.recover("WATCHDOG")
        self.assertEqual(self.b.writes,[150])
    def test_partial_recovery(self):
        self.start()
        self.b.state["costs"]["HQ/s1p"]=20
        with self.assertRaisesRegex(ValueError,"POSTCONDITION_NOT_MET"): self.t.recover("WATCHDOG")
        self.assertEqual(self.b.state["costs"][TARGET],100)
        self.assertEqual(self.t.load()["status"],"RESTORED_UNVERIFIED")
    def test_unowned_drift(self):
        self.t.event(self.t.load(),"ARMED")
        self.b.state["costs"][TARGET]=150
        for _ in range(2):
            with self.assertRaisesRegex(ValueError,"UNOWNED_DRIFT"): self.t.recover("WATCHDOG")
        self.assertEqual(self.b.writes,[])
    def test_bad_id(self):
        with self.assertRaisesRegex(ValueError,"INVALID_RFC_ID"): unit("../x")

if __name__=="__main__": unittest.main()
