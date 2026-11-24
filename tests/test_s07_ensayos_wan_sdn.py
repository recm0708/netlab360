"""Aceptación de SDN: alcance del controlador, sin inferir puerto."""
import sys
import json
import tempfile
import subprocess
from pathlib import Path
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/s07"))
from ensayos_wan_sdn_s07 import assess,BACKUP
import wan_trial_guard as guard
import ensayos_wan_sdn_s07 as supervisor

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

class WanTests(unittest.TestCase):
    def fixture(self,fault):
        rows=[]; events=[]
        def add(src,res,details):
            i=res
            rows.append({"event_id":i,"eligibility":"ELIGIBLE"})
            events.append({"event_id":i,"source":src,"resource_id":res,
                           "quality":"VALID","observed_at_utc":"2026-11-24T05:00:00+00:00","details":details})
        add("NOC_S05","WAN-PRIMARIA-HQ-S1",{"admin_state":"admin-down" if fault else "admin-up"})
        for site in ("HQ","S1","S2"):
            for peer in ("HQ","S1","S2"):
                if site==peer: continue
                key=f"FIB-{site}-{peer}"
                add("FRR_S02",key,{"selection":"BACKUP" if fault and key in BACKUP else "PRIMARY"})
        for site,ifaces in {"HQ":["s1p","s1b","s2p","s2b"],"S1":["s1p","s1b"],"S2":["s2p","s2b"]}.items():
            for iface in ifaces:
                if fault and site in ("HQ","S1") and iface=="s1p": continue
                add("FRR_S02",f"OSPF-{site}-{iface}",{"neighbor_state":"Full"})
        hs=[]; items=[]
        if fault:
            for i,(rule,context,action) in enumerate([
                ("WAN_ADMIN_DEVIATION","WAN-HQ-S1-PRIMARY","S07_READ_WAN_V1"),
                ("FIB_BACKUP_SELECTED","ROUTE-HQ-S1","S07_READ_FIB_V1"),
                ("FIB_BACKUP_SELECTED","ROUTE-S1-HQ","S07_READ_FIB_V1")]):
                hs.append({"rule":rule,"context_id":context,"hypothesis_id":str(i)})
                items.append({"hypothesis_id":str(i),"suggested_read_only_actions":[{"action_id":action}]})
        return ({"window":{"temporal_gate":True,"rows":rows},"batch":{"events":events}},
                {"temporal_gate":True,"network_mutations_authorized":False,"hypotheses":hs},
                {"approval_granted":False,"network_mutations_authorized":False,"recommendations":items})
    def test_complete_wan_phases(self):
        for stage in ("BASELINE","FAULT","RECOVERY"):
            self.assertEqual(assess("WAN",stage,*self.fixture(stage=="FAULT")),(True,"MATCH"))
    def test_unrelated_fib_rejected(self):
        a,r,rec=self.fixture(True)
        next(e for e in a["batch"]["events"] if e["resource_id"]=="FIB-HQ-S2")["details"]["selection"]="BACKUP"
        self.assertEqual(assess("WAN","FAULT",a,r,rec)[1],"FIB_NOT_MATCHED")
    def test_missing_runbook_rejected(self):
        a,r,rec=self.fixture(True)
        rec["recommendations"]=[]
        self.assertEqual(assess("WAN","FAULT",a,r,rec)[1],"TARGET_RUNBOOK_MISSING")

class GuardTests(unittest.TestCase):
    def test_bad_id(self):
        with self.assertRaisesRegex(ValueError,"BAD_ID"): guard.unit("../host")
    def test_target_changed_no_write(self):
        with mock.patch.object(guard,"identity",return_value=({"pid":99},False)),mock.patch.object(guard,"run") as run:
            with self.assertRaisesRegex(ValueError,"TARGET_SESSION_CHANGED"):
                guard.set_link(None,{},{"pid":10},True)
            run.assert_not_called()
    def test_restore_only_fixed_interface(self):
        expected={"pid":100}
        with mock.patch.object(guard,"identity",side_effect=[(expected,False),(expected,True)]),mock.patch.object(guard,"run") as run:
            guard.set_link(None,{},expected,True)
            run.assert_called_once_with("/usr/bin/nsenter","-t","100","-n","/usr/sbin/ip","link","set","dev","s1p","up")
    def test_restore_already_up_no_write(self):
        expected={"pid":100}
        with mock.patch.object(guard,"identity",return_value=(expected,True)),mock.patch.object(guard,"run") as run:
            guard.set_link(None,{},expected,True)
            run.assert_not_called()
    def test_postcondition_failed(self):
        expected={"pid":100}
        with mock.patch.object(guard,"identity",return_value=(expected,False)),mock.patch.object(guard,"run"):
            with self.assertRaisesRegex(ValueError,"LINK_POSTCONDITION_FAILED"):
                guard.set_link(None,{},expected,True)

class GuardResponseTests(unittest.TestCase):
    def test_denial_preserves_json(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            result=subprocess.CompletedProcess([],3,'{"ok":false,"reason":"PIN_MISMATCH"}','')
            with mock.patch.object(supervisor.subprocess,"run",return_value=result),mock.patch("sys.stderr"):
                with self.assertRaisesRegex(RuntimeError,"PIN_MISMATCH"):
                    supervisor.guard("start",directory=p)
            files=list(p.glob("wan-guard-error-start-*.json"))
            self.assertEqual(len(files),1)
            self.assertEqual(json.loads(files[0].read_text())["response"]["reason"],"PIN_MISMATCH")
    def test_non_json_failure(self):
        result=subprocess.CompletedProcess([],1,"","sudo denied")
        with mock.patch.object(supervisor.subprocess,"run",return_value=result),mock.patch("sys.stderr"):
            with self.assertRaisesRegex(RuntimeError,"INVALID_RESPONSE"): supervisor.guard("start")
    def test_success(self):
        result=subprocess.CompletedProcess([],0,'{"ok":true,"id":"test"}',"")
        with mock.patch.object(supervisor.subprocess,"run",return_value=result):
            self.assertEqual(supervisor.guard("start")["id"],"test")

if __name__=="__main__": unittest.main()
