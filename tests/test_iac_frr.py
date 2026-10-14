#!/usr/bin/env python3
"""Regresion local del comparador FRR (sin OpenTofu/Ansible ni Docker)."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDADOR = ROOT / "scripts/validacion/validar-iac-frr.py"
BASE = ROOT / "topologias/b2-frr/configs"


class TestIacFrrCompliance(unittest.TestCase):
    def test_baseline_is_compliant(self):
        with tempfile.TemporaryDirectory(prefix="netlab360-iac-") as folder:
            target = Path(folder)
            for router in ("R-HQ", "R-S1"):
                (target / f"{router}.frr.conf").write_bytes((BASE / f"{router}.frr.conf").read_bytes())
            result = subprocess.run(
                [sys.executable, str(VALIDADOR), str(target)],
                capture_output=True, text=True, cwd=ROOT
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("IAC_CONFIG_FIEL_A_B2=SI", result.stdout)

    def test_controlled_drift_detected(self):
        with tempfile.TemporaryDirectory(prefix="netlab360-iac-drift-") as folder:
            target = Path(folder)
            for router in ("R-HQ", "R-S1"):
                text = (BASE / f"{router}.frr.conf").read_text(encoding="utf-8")
                if router == "R-HQ":
                    text = text.replace(" ip ospf cost 10", " ip ospf cost 50", 1)
                (target / f"{router}.frr.conf").write_text(text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(VALIDADOR), str(target)],
                capture_output=True, text=True, cwd=ROOT
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("NON_COMPLIANT", result.stderr)


if __name__ == "__main__":
    unittest.main()
