"""Offline: OpenTofu S03 plan gate sin aplicar state."""
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
  "plan_gate",ROOT/"scripts/validacion/s03-tofu-plan.py")
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

def plan_fixture():
    addrs=(["terraform_data.management_guard"]
           +[f'terraform_data.site["{k}"]' for k in ("HQ","S1","S2")]
           +[f'terraform_data.wan["WAN-{k}"]' for k in range(4)]
           +[f'terraform_data.vlan["V-{k}"]' for k in range(9)])
    rows=[]
    for addr in addrs:
        part=addr.split(".")[1].split("[")[0]
        rows.append({"address":addr,"type":"terraform_data","name":part,
                     "provider_name":"terraform.io/builtin/terraform",
                     "change":{"actions":["create"]}})
    return {"resource_changes":rows}

class TestS03PlanGate(unittest.TestCase):
    def test_allow_only_seventeen_creates(self):
        self.assertEqual(m.verify_plan(plan_fixture()),
                         {"management_guard":1,"site":3,"wan":4,"vlan":9})

    def test_block_delete(self):
        p=plan_fixture()
        p["resource_changes"][0]["change"]["actions"]=["delete"]
        with self.assertRaisesRegex(ValueError,"no es creación"):
            m.verify_plan(p)

    def test_block_external_provider(self):
        p=plan_fixture()
        p["resource_changes"][2]["provider_name"]="registry.opentofu.org/hashicorp/aws"
        with self.assertRaisesRegex(ValueError,"Provider"):
            m.verify_plan(p)

    def test_block_unknown_resource(self):
        p=plan_fixture()
        p["resource_changes"][3]["type"]="docker_container"
        with self.assertRaisesRegex(ValueError,"tipo ajeno"):
            m.verify_plan(p)

    def test_block_missing_vlan(self):
        p=plan_fixture()
        p["resource_changes"].pop()
        with self.assertRaisesRegex(ValueError,"17 recursos"):
            m.verify_plan(p)

if __name__=="__main__":
    unittest.main()
