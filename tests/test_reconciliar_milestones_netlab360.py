"""Pruebas sin GitHub real para la reconciliación segura S01–S08."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[1] / "scripts/operacion/reconciliar_milestones_netlab360.py"
spec = importlib.util.spec_from_file_location("netlab360_milestones", PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def ms(n, open_count=0, closed_count=0, description="antigua"):
    return {"number": n, "title": f"S{n:02d}",
            "state": "closed" if n <= 6 else "open",
            "open_issues": open_count, "closed_issues": closed_count,
            "description": description}


class MilestoneReconcileTests(unittest.TestCase):
    def test_all_descriptions_present(self):
        self.assertEqual(set(m.DESCRIPTIONS), set(range(1,9)))

    def test_descriptions_uniform_sections(self):
        for n, d in m.DESCRIPTIONS.items():
            with self.subTest(phase=n):
                for tag in ("**Propósito:**", "**Alcance y entregables:**",
                            "**Criterio de aceptación:**", "**Estado:**"):
                    self.assertIn(tag, d)

    def test_s05_is_six_completed_no_fourth_site(self):
        d = m.DESCRIPTIONS[5]
        self.assertIn("seis issues", d)
        self.assertIn("No incluye HA física", d)
        self.assertIn("WireGuard", d)

    def test_s06_closed_with_experimental_limits(self):
        self.assertEqual(m.EXPECTED_STATES[6], "closed")
        self.assertIn("CERRADA", m.DESCRIPTIONS[6])
        self.assertIn("FAULT HTTP HQ independiente", m.DESCRIPTIONS[6])
        self.assertIn("pronóstico/horizonte MAE no evaluables", m.DESCRIPTIONS[6])
        self.assertNotIn("90 %", m.DESCRIPTIONS[6])

    def test_s06_milestone_identity_and_closed_state(self):
        with patch.object(m, "gh", return_value=ms(6)):
            self.assertEqual(m.milestone(6)["state"], "closed")

    def test_s06_rejects_unexpected_open_state(self):
        with patch.object(m, "gh", return_value=ms(6) | {"state": "open"}):
            with self.assertRaisesRegex(RuntimeError, "unexpected_state"):
                m.milestone(6)

    def test_s07_s08_stay_open(self):
        self.assertEqual(m.EXPECTED_STATES[7], "open")
        self.assertEqual(m.EXPECTED_STATES[8], "open")
        self.assertIn("issue #24", m.DESCRIPTIONS[5])

    def test_inventory_rejects_unfinished_issue(self):
        issues = [{"number": n, "state": "closed"} for n in sorted(m.S05_EXPECTED)]
        issues[2]["state"] = "open"
        with patch.object(m, "gh", return_value=issues):
            with self.assertRaisesRegex(RuntimeError, "issue_open"):
                m.s05_inventory()

    def test_inventory_rejects_spurious_issue(self):
        issues = [{"number": n, "state": "closed"} for n in sorted(m.S05_EXPECTED)]
        issues.append({"number": 999, "state": "closed"})
        with patch.object(m, "gh", return_value=issues):
            with self.assertRaisesRegex(RuntimeError, "inventory_changed"):
                m.s05_inventory()

    def test_inventory_rejects_pull_request(self):
        issues = [{"number": n, "state": "closed"} for n in sorted(m.S05_EXPECTED)]
        issues[0]["pull_request"] = {"url": "a"}
        with patch.object(m, "gh", return_value=issues):
            with self.assertRaisesRegex(RuntimeError, "pull_request"):
                m.s05_inventory()

    def test_inventory_valid(self):
        issues = [{"number": n, "state": "closed"} for n in sorted(m.S05_EXPECTED)]
        with patch.object(m, "gh", return_value=issues):
            self.assertEqual(m.s05_inventory()["closed"],6)

    def test_milestone_identity_fail_closed(self):
        with patch.object(m, "gh", return_value=ms(1) | {"title": "OTHER"}):
            with self.assertRaisesRegex(RuntimeError, "identity"):
                m.milestone(1)

    def test_milestone_status_fail_closed(self):
        with patch.object(m, "gh", return_value=ms(5) | {"state": "open"}):
            with self.assertRaisesRegex(RuntimeError, "unexpected_state"):
                m.milestone(5)

    def test_optional_issue_relocation(self):
        with patch.object(m,"gh", return_value={"state":"open","milestone":{"number":8}}):
            m.optional_issue_scope()

    def test_optional_issue_wrong_milestone_rejected(self):
        with patch.object(m,"gh", return_value={"state":"open","milestone":{"number":5}}):
            with self.assertRaisesRegex(RuntimeError,"not_reassigned"):
                m.optional_issue_scope()

    def test_count_comparison(self):
        inv={"open":0,"closed":6}
        self.assertTrue(m.counts_ok(ms(5,0,6),inv))
        self.assertFalse(m.counts_ok(ms(5,6,1),inv))

    def test_dry_run_makes_no_patch(self):
        inventory = {"closed":6,"open":0,"total":6,
                     "numbers":sorted(m.S05_EXPECTED)}
        with (patch.object(m,"s05_inventory",return_value=inventory),
              patch.object(m,"optional_issue_scope"),
              patch.object(m,"milestone",side_effect=lambda n: ms(n,0,6) if n==5 else ms(n)),
              patch.object(m,"gh") as api):
            m.run(False)
            api.assert_not_called()

    def test_recount_leaves_completed_issue_closed(self):
        inventory={"closed":6,"open":0}
        states=[
            ms(5,6,1),
            ms(5,0,6)
        ]
        with (patch.object(m,"milestone",side_effect=states),
              patch.object(m,"s05_inventory",return_value=inventory),
              patch.object(m,"gh",side_effect=[
                  {"state":"closed","milestone":{"number":5}},
                  {"state":"closed","milestone":None},
                  {"state":"closed","milestone":{"number":5}},
                  {"state":"closed","milestone":{"number":5}},
              ]) as gh):
            m.refresh_s05_once(inventory)
            self.assertEqual([x.args[1] for x in gh.call_args_list if len(x.args)>1],
                             [{"milestone":None},{"milestone":5}])


if __name__=="__main__":
    unittest.main()
