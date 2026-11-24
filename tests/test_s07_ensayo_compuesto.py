"""Pruebas de aceptación conjunta, sin mutaciones de red."""
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
import ensayo_compuesto_s07 as c

class JointTests(unittest.TestCase):
    def fixture(self):
        return {},{"network_mutations_authorized":False},{"approval_granted":False,"network_mutations_authorized":False}
    def test_shared_window(self):
        args=self.fixture()
        with mock.patch.object(c,"assess_wan",return_value=(True,"MATCH")) as w, mock.patch.object(c,"assess_service",return_value=(True,"MATCH")) as h:
            self.assertEqual(c.assess_joint("FAULT",*args,"stamp"),(True,"MATCH"))
            w.assert_called_once_with("WAN","FAULT",*args,"stamp")
            h.assert_called_once_with("HTTP","FAULT",*args,"stamp")
    def test_wan_not_matched(self):
        with mock.patch.object(c,"assess_wan",return_value=(False,"FIB_NOT_MATCHED")), mock.patch.object(c,"assess_service") as h:
            self.assertEqual(c.assess_joint("FAULT",*self.fixture())[1],"WAN:FIB_NOT_MATCHED")
            h.assert_not_called()
    def test_http_not_matched(self):
        with mock.patch.object(c,"assess_wan",return_value=(True,"MATCH")), mock.patch.object(c,"assess_service",return_value=(False,"TARGET_UNKNOWN")):
            self.assertEqual(c.assess_joint("FAULT",*self.fixture())[1],"HTTP:TARGET_UNKNOWN")
    def test_invalid_stage(self):
        with self.assertRaisesRegex(ValueError,"STAGE_INVALID"): c.assess_joint("OTHER",*self.fixture())
    def test_autonomous_approval_denied(self):
        a,r,rec=self.fixture(); rec["approval_granted"]=True
        with self.assertRaisesRegex(ValueError,"ADVISORY_SCOPE_VIOLATED"): c.assess_joint("FAULT",a,r,rec)
if __name__=="__main__": unittest.main()
