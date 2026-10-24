"""Pruebas offline manifest/guard OpenTofu S03, sin tofu apply o Docker."""
from __future__ import annotations
import hashlib
import importlib.util
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"inventario/ipam/topologia-s02.yaml"
HCL=ROOT/"iac/s03/main.tf"
SPEC=importlib.util.spec_from_file_location(
    "s03_manifest_validator", ROOT/"scripts/validacion/s03-tofu-manifest.py")
assert SPEC and SPEC.loader
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestS03OpenTofu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=yaml.safe_load(SRC.read_text())
        cls.sha=hashlib.sha256(SRC.read_bytes()).hexdigest()
        cls.fixture={
            "scope":"metadata_only_no_live_network_apply",
            "status":"candidate_manifest",
            "source_sha256":cls.sha,
            "management":cls.source["management_host"],
            "sites":{name:dict(site,site_id=name)
                     for name,site in cls.source["sites"].items()},
            "wan_links":{w["id"]:w for w in cls.source["wan_links"]},
            "vlans":{f"{name}-{v['id']}":dict(v,site=name)
                     for name,site in cls.source["sites"].items()
                     for v in site["vlans"]},
        }

    def test_seventeen_records_match_source(self):
        result=mod.validate_manifest(self.fixture,self.source,self.sha)
        self.assertEqual(result,{"sites":3,"links":4,"vlans":9,"records":17})

    def test_reject_modified_wan_cost(self):
        import copy
        fixture=copy.deepcopy(self.fixture)
        fixture["wan_links"]["WAN-RESPALDO-HQ-S1"]["ospf_cost"]=250
        with self.assertRaisesRegex(ValueError,"WAN no coincide"):
            mod.validate_manifest(fixture,self.source,self.sha)

    def test_reject_modified_management(self):
        import copy
        fixture=copy.deepcopy(self.fixture)
        fixture["management"]["host_ip"]="192.168.47.41"
        with self.assertRaisesRegex(ValueError,"Guarda VMnet8"):
            mod.validate_manifest(fixture,self.source,self.sha)

    def test_reject_wrong_sot_hash(self):
        import copy
        fixture=copy.deepcopy(self.fixture)
        fixture["source_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"SHA"):
            mod.validate_manifest(fixture,self.source,self.sha)

    def test_hcl_has_no_external_or_mutating_provisioners(self):
        code=HCL.read_text()
        self.assertEqual(code.count('resource "terraform_data"'),4)
        self.assertNotIn('provisioner "',code)
        self.assertNotIn('resource "docker_',code)
        self.assertNotIn('resource "local_file"',code)
        self.assertNotIn("required_providers",code)
        self.assertIn("locked == true",code)
        self.assertIn('status        = "candidate_manifest"',code)


if __name__=="__main__":
    unittest.main()
