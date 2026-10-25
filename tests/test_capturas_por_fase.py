"""Auditoría offline de capturas reales por fase, con huellas históricas."""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LOTE = ROOT / "evidencias/manifiestos/MANIFIESTO_SHA256_CAPTURAS_2026-10-25.csv"


class TestCapturasPorFase(unittest.TestCase):
    def test_shas_y_carpetas(self):
        cmd = [sys.executable, str(ROOT / "scripts/validacion/validar-capturas-unificadas.py")]
        completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        for comprobacion in (
            "S01_SHA256_Y_GIT_BLOB_CONSERVADOS=86/86",
            "LOTE_20261025_SHA256_Y_BLOB=21/21",
            "FASE_2_PNG_VERSIONADOS=9",
            "FASE_3_PNG_VERSIONADOS=8",
            "AUDITORIA_CAPTURAS_POR_FASE=OK",
        ):
            self.assertIn(comprobacion, completed.stdout)

    def test_lote_21_solo_evidencias_aprobadas(self):
        with LOTE.open(encoding="utf-8", newline="") as f:
            registros = list(csv.DictReader(f))
        self.assertEqual(len(registros), 21)
        self.assertEqual(
            [sum(r["ruta_actual"].startswith(f"evidencias/capturas/fase{i}/")
                 for r in registros) for i in (1, 2, 3)],
            [4, 9, 8],
        )
        self.assertEqual(len({r["ruta_actual"] for r in registros}), 21)
        self.assertTrue(all(r["clasificacion"] in ("COMPLEMENTARIA", "PRINCIPAL")
                            for r in registros))


if __name__ == "__main__":
    unittest.main()
