"""Pruebas offline de conciliación histórica de tareas de PR."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "scripts/operacion/normalizar_tareas_prs.py"
SPEC = importlib.util.spec_from_file_location("normalizar_tareas_prs", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class HistoricalTasksTests(unittest.TestCase):
    def setUp(self):
        self.pr = dict(body="Alcance original", state="MERGED", mergedAt="2026-11-25",
                       changedFiles=2, baseRefName="main")
        self.files = [dict(filename="tests/test_demo.py", status="added"),
                      dict(filename="docs/demo.md", status="modified")]

    def test_preserves_description_and_records_only_integration(self):
        result = MOD.historical_body(self.pr, self.files)
        self.assertTrue(result.startswith("Alcance original"))
        self.assertIn("- [x]", result)
        self.assertIn("tests/test_demo.py", result)
        self.assertIn("docs/demo.md", result)
        self.assertIn("no una nueva ejecución de CI", result)

    def test_existing_tasks_and_open_pr_unchanged(self):
        self.assertIsNone(MOD.historical_body(dict(self.pr, body="- [ ] Pendiente"), self.files))
        self.assertIsNone(MOD.historical_body(dict(self.pr, state="OPEN"), self.files))

    def test_incomplete_files_rejected(self):
        with self.assertRaises(ValueError):
            MOD.historical_body(self.pr, self.files[:1])

    def test_idempotence(self):
        first = MOD.historical_body(self.pr, self.files)
        self.assertIsNone(MOD.historical_body(dict(self.pr, body=first), self.files))


if __name__ == "__main__":
    unittest.main()
