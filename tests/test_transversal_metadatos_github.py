"""Regresión offline del plan de metadatos sin peticiones ni escrituras."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "scripts/operacion/auditar_metadatos_github.py"
SPEC = importlib.util.spec_from_file_location("auditar_metadatos_github", PATH)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class MetadataPlanTests(unittest.TestCase):
    def setUp(self):
        self.types = {"task": "Task", "feature": "Feature", "bug": "Bug"}
        self.milestones = {5, 8}
        self.issue = {"number": 206, "title": "[S08] Diagnóstico",
                      "labels": [{"name": "tipo:pruebas"}], "assignees": []}

    def test_missing_issue_fields(self):
        changes, review = MOD.plan(self.issue, self.types, self.milestones)
        self.assertEqual(changes, {"assignees": ["recm0708"], "milestone": 8,
                                   "type": "Feature"})
        self.assertFalse(review)

    def test_preserve_existing_fields(self):
        issue = dict(self.issue, type={"name": "Task"},
                     assignees=[{"login": "other"}], milestone={"number": 5})
        self.assertEqual(MOD.plan(issue, self.types, self.milestones), ({}, []))

    def test_pr_transversal(self):
        pr = dict(self.issue, title="[GESTIÓN] Política común", pull_request={},
                  assignees=[{"login": "recm0708"}])
        self.assertEqual(MOD.plan(pr, self.types, self.milestones), ({}, []))

    def test_unresolved_labels_and_milestone(self):
        pr = dict(self.issue, pull_request={}, labels=[])
        changes, review = MOD.plan(pr, self.types, self.milestones)
        self.assertEqual(changes, {"assignees": ["recm0708"]})
        self.assertEqual(review, ["LABELS_AUSENTES", "MILESTONE_PR_REVISAR_ALCANCE"])

    def test_type_unavailable(self):
        changes, review = MOD.plan(self.issue, {}, self.milestones)
        self.assertNotIn("type", changes)
        self.assertIn("TYPE_NO_DISPONIBLE_FEATURE", review)

    def test_bug_and_task(self):
        issue = dict(self.issue, number=10)
        self.assertEqual(MOD.plan(issue, self.types, self.milestones)[0]["type"], "Task")
        issue["labels"] = [{"name": "tipo:error"}]
        self.assertEqual(MOD.plan(issue, self.types, self.milestones)[0]["type"], "Bug")


if __name__ == "__main__":
    unittest.main()
