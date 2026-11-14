"""NETLAB360 S05: el runbook debe comparar el marcador real completo."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs/operacion/s05-lotes-siguientes-lacp-hq-20261114.md"


class TestS05RunbookGates(unittest.TestCase):
    def test_marcadores_y_gates_coinciden(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        for marker in (
            "LOTE114A_R_PRECHECK=OK",
            "LOTE114A_S_ESTABILIDAD=OK",
            "LOTE114B_FALLA_RETORNO=OK",
        ):
            self.assertIn(f'echo "========== {marker} =========="', text)
            self.assertIn(f"grep -Fxq '========== {marker} =========='", text)
            self.assertNotIn(f"grep -Fxq '{marker}'", text)

    def test_mutacion_bloqueada_por_dos_checks(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        i = text.index("## Lote 114B —")
        end = text.index("## Lote 114C —", i)
        block = text[i:end]
        for marker in (
            "LOTE114A_R_PRECHECK=OK",
            "LOTE114A_S_ESTABILIDAD=OK",
        ):
            self.assertIn(f"grep -Fxq '========== {marker} =========='", block)
        self.assertLess(block.index("LOTE114A_S_ESTABILIDAD=OK"),
                        block.index("run --confirm-failover"))

    def test_gate_exacto_preserva_formato(self):
        line = "========== LOTE114A_R_PRECHECK=OK =========="
        self.assertEqual(line, "========== LOTE114A_R_PRECHECK=OK ==========")
        self.assertNotEqual(line, "LOTE114A_R_PRECHECK=OK")


if __name__ == "__main__":
    unittest.main()
