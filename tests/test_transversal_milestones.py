"""Comprueba la gestión de hitos sin modificar GitHub."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts/operacion/reconciliar_milestones_netlab360.py"
)

spec = importlib.util.spec_from_file_location("milestones", PATH)
assert spec and spec.loader

m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def milestone(n, title=None, state=None):
    return {
        "number": n,
        "title": title or f"Fase {n}",
        "state": state or ("closed" if n <= 7 else "open"),
        "open_issues": 0,
        "closed_issues": 10,
        "due_on": None,
        "description": m.DESCRIPTIONS[n].strip()
    }


def entries7():
    return [
        {
            "number": n,
            "state": "closed",
            "milestone": {"number": 7}
        }
        for n in [7, *range(190, 198)]
    ] + [{
        "number": 202,
        "state": "closed",
        "milestone": {"number": 7},
        "pull_request": {}
    }]


class MilestoneTests(unittest.TestCase):

    def test_description_sections(self):
        self.assertEqual(set(m.DESCRIPTIONS), set(range(1, 11)))

        for description in m.DESCRIPTIONS.values():
            for label in (
                "Propósito", "Alcance y entregables",
                "Criterio de aceptación", "Estado"
            ):
                self.assertIn(f"**{label}:**", description)

    def test_expected_states(self):
        for n in range(1, 8):
            self.assertEqual(m.EXPECTED_STATES[n], "closed")

        for n in (8, 9, 10):
            self.assertEqual(m.EXPECTED_STATES[n], "open")

    def test_legacy_and_current_identity(self):
        for n in range(1, 11):
            for title in (f"S{n:02d}", f"Fase {n}"):
                with patch.object(
                    m, "gh", return_value=milestone(n, title)
                ):
                    self.assertEqual(m.milestone(n)["title"], title)

    def test_invalid_identity(self):
        with patch.object(
            m, "gh", return_value=milestone(7, "Fase 6")
        ):
            with self.assertRaisesRegex(RuntimeError, "identity"):
                m.milestone(7)

    def test_unexpected_open_state(self):
        with patch.object(
            m, "gh", return_value=milestone(7, state="open")
        ):
            with self.assertRaisesRegex(RuntimeError, "state"):
                m.milestone(7)

    def test_phase7_includes_merged_pr(self):
        with patch.object(
            m, "gh", side_effect=[
                entries7(),
                {"state": "closed", "merged": True}
            ]
        ):
            observed = m.inventory(7)

        self.assertEqual(observed["closed"], 10)
        self.assertEqual(observed["open"], 0)

    def test_open_pr_rejected(self):
        rows = entries7()
        rows[-1]["state"] = "open"

        with patch.object(m, "gh", return_value=rows):
            with self.assertRaisesRegex(RuntimeError, "open_items"):
                m.inventory(7)

    def test_missing_issue_rejected(self):
        with patch.object(m, "gh", return_value=entries7()[1:]):
            with self.assertRaisesRegex(RuntimeError, "inventory_changed"):
                m.inventory(7)

    def test_unmerged_pr_rejected(self):
        with patch.object(
            m, "gh", side_effect=[
                entries7(),
                {"state": "closed", "merged": False}
            ]
        ):
            with self.assertRaisesRegex(RuntimeError, "not_merged"):
                m.inventory(7)

    def test_duplicate_rejected(self):
        rows = entries7()
        rows.append(rows[0])

        with patch.object(m, "gh", return_value=rows):
            with self.assertRaisesRegex(RuntimeError, "invalid_inventory"):
                m.inventory(7)

    def test_wrong_membership_rejected(self):
        rows = entries7()
        rows[0]["milestone"] = {"number": 8}

        with patch.object(m, "gh", return_value=rows):
            with self.assertRaisesRegex(RuntimeError, "inventory_changed"):
                m.inventory(7)

    def test_global_inventory_filters_other_phases(self):
        rows = entries7() + [{
            "number": 204,
            "state": "open",
            "milestone": {"number": 8}
        }]

        with patch.object(
            m, "gh", side_effect=[
                rows, {"state": "closed", "merged": True}
            ]
        ) as api:
            result = m.inventory(7)

        self.assertEqual(result["closed"], 10)
        self.assertNotIn(204, result["items"])
        self.assertIn(
            "/issues?state=all",
            api.call_args_list[0].args[0]
        )

    def test_phase10_inventory(self):
        rows = [{
            "number": 218,
            "state": "open",
            "milestone": {"number": 10}
        }]

        with patch.object(m, "gh", return_value=rows):
            result = m.inventory(10)

        self.assertEqual(result["open"], 1)
        self.assertEqual(result["closed"], 0)

    def test_stale_counter_detected(self):
        observed = {"open": 0, "closed": 10}
        current = milestone(7)
        current["open_issues"] = 1
        current["closed_issues"] = 9

        self.assertFalse(m.counts_ok(current, observed))
        self.assertTrue(m.counts_ok(milestone(7), observed))

    def test_check_does_not_mutate(self):
        observed = {"open": 0, "closed": 10, "items": {}}

        with (
            patch.object(m, "milestone", side_effect=milestone),
            patch.object(m, "all_inventories", return_value={n: observed for n in range(1, 11)}),
            patch.object(m, "gh") as api
        ):
            m.run(False)
            api.assert_not_called()

    def test_apply_only_updates_metadata(self):
        observed = {"open": 0, "closed": 10, "items": {}}

        with (
            patch.object(
                m, "milestone",
                side_effect=[
                    milestone(n, f"S{n:02d}") for n in range(1, 11)
                ] + [
                    milestone(n) for n in range(1, 11)
                ]
            ),
            patch.object(m, "all_inventories", return_value={n: observed for n in range(1, 11)}),
            patch.object(m, "gh") as api
        ):
            m.run(True)

        self.assertEqual(api.call_count, 10)

        for call in api.call_args_list:
            self.assertEqual(
                set(call.args[1]),
                {"title", "description"}
            )

    def test_s06_scientific_limits_preserved(self):
        self.assertIn(
            "pronóstico/horizonte MAE no evaluables",
            m.DESCRIPTIONS[6]
        )

    def test_s07_acceptance_preserved(self):
        self.assertIn("CERRADA", m.DESCRIPTIONS[7])
        self.assertIn("1258", m.DESCRIPTIONS[7])


if __name__ == "__main__":
    unittest.main()
