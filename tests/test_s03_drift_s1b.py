"""NETLAB360 S03: tests OFFLINE del experimento de drift, sin Docker/FRR."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
import yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"scripts/laboratorio/s03_drift_s1b.py"
SPEC=importlib.util.spec_from_file_location("s03drift",SOURCE)
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class TestS03Drift(unittest.TestCase):
    def test_one_safe_backup_target(self):
        self.assertEqual(m.TARGET_ROUTER,"R-S1")
        self.assertEqual(m.TARGET_INTERFACE,"s1b")
        self.assertEqual(m.INJECTED_COST,150)
        self.assertEqual(m.EXPECTED_FULL,{"R-HQ":4,"R-S1":2,"R-S2":2})

    def test_eight_costs_normal_expected(self):
        wanted={"R-HQ":{"s1p":10,"s1b":100,"s2p":10,"s2b":100},
                "R-S1":{"s1p":10,"s1b":100},
                "R-S2":{"s2p":10,"s2b":100}}
        with patch.object(m,"print",create=True):
            m.validate_costs(wanted,wanted,100)

    def test_cost_validator_allows_only_target_drift(self):
        wanted={"R-HQ":{"s1p":10,"s1b":100,"s2p":10,"s2b":100},
                "R-S1":{"s1p":10,"s1b":100},
                "R-S2":{"s2p":10,"s2b":100}}
        observed={k:v.copy() for k,v in wanted.items()}
        observed["R-S1"]["s1b"]=150
        m.validate_costs(wanted,observed,150)
        observed["R-HQ"]["s1p"]=20
        with self.assertRaisesRegex(RuntimeError,"Costo no esperado"):
            m.validate_costs(wanted,observed,150)

    def test_vtysh_rejects_unapproved_cost(self):
        with self.assertRaisesRegex(RuntimeError,"fuera del escenario"):
            m.vtysh_set_cost({},200)

    def test_vtysh_command_targets_only_s1b(self):
        current={"R-S1":{"name":"nl360-s02-r-s1"}}
        with patch.object(m,"run",return_value="") as fake:
            m.vtysh_set_cost(current,150)
            self.assertEqual(fake.call_args.args,
                ("docker","exec","nl360-s02-r-s1","vtysh",
                 "-c","configure terminal","-c","interface s1b",
                 "-c","ip ospf cost 150","-c","end"))

    def test_ansible_playbook_limits_router_and_become(self):
        p=yaml.safe_load((ROOT/"ansible/s03/control-drift-s1b.yml").read_text())[0]
        self.assertEqual(p["hosts"],"R-S1")
        self.assertEqual(p["connection"],"local")
        self.assertFalse(p.get("become",False))
        tasks=[x for x in p["tasks"] if x.get("become",False)]
        self.assertEqual(len(tasks),1)
        self.assertEqual(tasks[0]["vars"]["ansible_become_exe"],"/usr/bin/sudo.ws")
        self.assertEqual(tasks[0]["changed_when"],
                         "'S03_CONFIG_CHANGED=1' in s03_control.stdout")

    def test_detector_does_not_apply_config(self):
        p=yaml.safe_load((ROOT/"ansible/s03/detectar-drift-s1b.yml").read_text())[0]
        self.assertEqual(p["hosts"],"R-S1")
        tasks=p["tasks"]
        command_tasks=[t for t in tasks if "ansible.builtin.command" in t]
        self.assertEqual(len(command_tasks),1)
        self.assertFalse(command_tasks[0]["changed_when"])
        self.assertEqual(command_tasks[0]["failed_when"],
                         "s03_drifts.rc not in [0,2]")


if __name__=="__main__":
    unittest.main()
