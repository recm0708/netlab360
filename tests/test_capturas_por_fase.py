"""Prueba offline de evidencia S01 organizada sin bytes modificados."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestCapturasPorFase(unittest.TestCase):
    def test_shas_y_carpetas(self):
        cmd = [sys.executable, str(ROOT / "scripts/validacion/validar-capturas-unificadas.py")]
        completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("S01_SHA256_Y_GIT_BLOB_CONSERVADOS=86/86", completed.stdout)
        self.assertIn("AUDITORIA_CAPTURAS_POR_FASE=OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
