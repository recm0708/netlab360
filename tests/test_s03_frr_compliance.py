"""Tests offline de parseo FRRouting OSPF S03 (no sudo, sin red)."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "s03costs",ROOT/"scripts/validacion/s03-frr-compliance.py")
assert SPEC and SPEC.loader
m=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

SAMPLE="""Building configuration...

Current configuration:
!
interface lo
 ip ospf area 0
!
interface s1p
 description primaria
 ip ospf area 0
 ip ospf network point-to-point
 ip ospf cost 10
!
interface s1b
 description respaldo
 ip ospf cost 100
!
router ospf
 ospf router-id 10.79.0.1
!
"""

class TestS03CostParser(unittest.TestCase):
    def test_interface_costs(self):
        result=m.parse_frr_costs(SAMPLE)
        self.assertEqual(result["s1p"],10)
        self.assertEqual(result["s1b"],100)

    def test_ignore_cost_outside_interface(self):
        result=m.parse_frr_costs(SAMPLE+"ip ospf cost 66\n")
        self.assertEqual(result,{"s1p":10,"s1b":100})

    def test_detect_drift(self):
        desired={"s1p":10,"s1b":100}
        observed={"s1p":10,"s1b":150}
        errors=m.compare_costs(desired,observed)
        self.assertEqual(errors,["s1b esperado=100 observado=150"])

    def test_detect_absent_interface(self):
        self.assertEqual(
            m.compare_costs({"s2b":100},{}),
            ["s2b esperado=100 observado=AUSENTE"]
        )

    def test_reject_duplicate_ospf_cost(self):
        text="interface s1b\n ip ospf cost 10\n ip ospf cost 100\n!"
        with self.assertRaisesRegex(ValueError,"duplicado"):
            m.parse_frr_costs(text)

if __name__=="__main__":
    unittest.main()
