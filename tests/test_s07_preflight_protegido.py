"""Pruebas de preflight sin Docker ni operaciones de red."""
from pathlib import Path
from unittest.mock import patch
import tempfile
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import preflight_protegido as p

class PreflightTests(unittest.TestCase):
    def test_profile(self):
        self.assertEqual(sum(map(len,p.profile().values())),8)
        self.assertEqual(p.profile()["S1"]["s1b"],100)
        self.assertNotIn("ens33",p.profile()["HQ"])
    def test_pin(self):
        pin={"schema":"NETLAB360_S07_ROUTER_PIN_V1","ids":{"HQ":"a"*64,"S1":"b"*64,"S2":"c"*64},"profile":p.profile()}
        self.assertEqual(len(p.pin_ids(pin)),3)
        pin["ids"]["S1"]=pin["ids"]["HQ"]
        with self.assertRaisesRegex(ValueError,"PIN_INVALID"): p.pin_ids(pin)
    def test_cost_parser(self):
        self.assertEqual(p.parse_frr_costs("interface s1b\n ip ospf cost 100\n!\n"),{"s1b":100})
    def test_duplicate_cost(self):
        with self.assertRaises(ValueError): p.parse_frr_costs("interface s1b\n ip ospf cost 100\n ip ospf cost 150\n")
    def test_lock_contention(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"lock"
            with p.exclusive(path):
                with self.assertRaisesRegex(ValueError,"RESOURCE_BUSY"):
                    with p.exclusive(path): pass
            with p.exclusive(path): pass
    def test_lock_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"lock"
            path.symlink_to(Path(d)/"other")
            with self.assertRaises(OSError):
                with p.exclusive(path): pass
    def test_mismatched_identity(self):
        with patch.object(p,"management",return_value={}),patch.object(p,"load_gate",return_value={}),patch.object(p,"inspect",return_value={"id":"b"*64,"pid":123}):
            with self.assertRaisesRegex(ValueError,"PIN_MISMATCH"): p.observe({"HQ":"a"*64})
    def test_load_gate(self):
        with patch.object(p.os,"getloadavg",return_value=(100000,0,0)):
            with self.assertRaisesRegex(ValueError,"HOST_LOAD_LIMIT"): p.load_gate()
    def test_management_wrong_host(self):
        with patch.object(p.socket,"gethostname",return_value="other"):
            with self.assertRaisesRegex(ValueError,"HOSTNAME"): p.management()

if __name__=="__main__":
    unittest.main()
