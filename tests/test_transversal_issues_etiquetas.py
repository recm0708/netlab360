"""Pruebas de normalización de issues/etiquetas NETLAB360, sin llamadas reales."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

SOURCE = (Path(__file__).resolve().parents[1] /
          "scripts/operacion/normalizar_issues_etiquetas.py")
spec = importlib.util.spec_from_file_location("netlab360_issues_es", SOURCE)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def make_item(n):
    phase=m.phase_for(n)
    state="closed" if n in m.EXPECTED_CLOSED else "open"
    return {
        "number":n,
        "title":f"[S{phase:02d}] Descripción adecuada para la issue {n}",
        "milestone":{"number":phase},
        "state":state,
        "body":"- [x] Criterio correcto" if state=="closed"
               else "- [ ] Criterio todavía no realizado",
        "labels":[{"name":lab} for lab in m.labels_for(n)],
    }


class IssuesSpanishTests(unittest.TestCase):
    def test_all_53_issues_exactly_once(self):
        ids=[i for s in m.PHASES.values() for i in s]
        self.assertEqual(len(ids),53)
        self.assertEqual(len(set(ids)),53)

    def test_all_53_issues_one_theme(self):
        for n in m.ALL_IDS:
            with self.subTest(issue=n):
                self.assertEqual(sum(n in nums for nums in m.THEMES.values()),1)

    def test_titles_only_phase_prefix(self):
        issues=[make_item(n) for n in m.ALL_IDS]
        self.assertEqual(len(m.check_baseline(issues)),53)

    def test_status_not_embedded_in_title(self):
        issues=[make_item(n) for n in m.ALL_IDS]
        issues[0]["title"]+=" — CERRADA"
        with self.assertRaisesRegex(ValueError,"nonuniform_title"):
            m.check_baseline(issues)

    def test_reject_missing_issue(self):
        issues=[make_item(n) for n in m.ALL_IDS if n!=5]
        with self.assertRaisesRegex(ValueError,"inventory_changed"):
            m.check_baseline(issues)

    def test_reject_extra_issue(self):
        issues=[make_item(n) for n in m.ALL_IDS]
        issues.append(make_item(1)|{"number":999})
        with self.assertRaisesRegex(ValueError,"inventory_changed"):
            m.check_baseline(issues)

    def test_reject_closed_unchecked(self):
        issues=[make_item(n) for n in m.ALL_IDS]
        issue=next(x for x in issues if x["number"]==5)
        issue["body"]="- [ ] Pendiente desconocido"
        with self.assertRaisesRegex(ValueError,"closed_with_1_unchecked"):
            m.check_baseline(issues)

    def test_reject_open_without_pending(self):
        issues=[make_item(n) for n in m.ALL_IDS]
        issue=next(x for x in issues if x["number"]==8)
        issue["body"]="- [x] Todo completo"
        with self.assertRaisesRegex(ValueError,"open_without_pending"):
            m.check_baseline(issues)

    def test_reject_wrong_milestone(self):
        issues=[make_item(n) for n in m.ALL_IDS]
        next(x for x in issues if x["number"]==24)["milestone"]={"number":5}
        with self.assertRaisesRegex(ValueError,"wrong_milestone"):
            m.check_baseline(issues)

    def test_preserve_open_optional(self):
        for n in (17,24,29):
            self.assertIn("alcance:opcional",m.labels_for(n))
            self.assertNotIn("prioridad:alta",m.labels_for(n))

    def test_core_open_high_priority(self):
        for n in (6,7,8,25,26,27,43,44,45,106):
            self.assertIn("prioridad:alta",m.labels_for(n))

    def test_completed_issue_has_no_priority_padding(self):
        self.assertEqual(m.labels_for(32),
                         ["fase:05","tipo:disponibilidad"])
        self.assertEqual(m.labels_for(153),
                         ["fase:06","tipo:pruebas"])

    def test_one_type_per_issue(self):
        for n in m.ALL_IDS:
            result=m.labels_for(n)
            self.assertEqual(sum(label.startswith("tipo:") for label in result),1)
            self.assertEqual(sum(label.startswith("fase:") for label in result),1)
            self.assertEqual(len(result),len(set(result)))

    def test_all_descriptions_in_spanish(self):
        self.assertEqual(m.DEFINITIONS["tipo:documentación"][1][:10],
                         "Documentos")
        for name,(color,description) in m.DEFINITIONS.items():
            self.assertRegex(color,r"^[0-9A-F]{6}$")
            self.assertTrue(description.endswith("."))
            self.assertTrue(description)
            self.assertLessEqual(len(description), 100, name)

    def test_reject_overlong_description_before_api_call(self):
        color, _ = m.DEFINITIONS["estado:bloqueado"]
        with mock.patch.dict(m.DEFINITIONS, {
            "estado:bloqueado": (color, "x" * 101)
        }):
            with mock.patch.object(m, "gh") as gh:
                with self.assertRaisesRegex(ValueError,
                                            "label_description_invalid_estado:bloqueado"):
                    m.run(True)
                gh.assert_not_called()

    def test_no_unknown_labels_in_pure_catalogue(self):
        rows=[make_item(n) for n in m.ALL_IDS]
        labels={name:{"name":name,"color":color,"description":description}
                for name,(color,description) in m.DEFINITIONS.items()}
        findings=m.inspect(rows,labels)
        self.assertEqual(findings["issue_label_mismatch"],[])
        self.assertEqual(findings["canonical_labels_missing"],[])
        self.assertEqual(findings["legacy_labels"],[])
        self.assertEqual(findings["unknown_labels"],[])
        self.assertEqual(findings["canonical_descriptions_outdated"],[])

    def test_unknown_label_detected(self):
        labels={"foo-en": {"name":"foo-en","description":"legacy","color":"ffffff"}}
        summary=m.inspect([make_item(n) for n in m.ALL_IDS],labels)
        self.assertEqual(summary["unknown_labels"],["foo-en"])

    def test_pr_excluded_from_issue_validation(self):
        rows=[make_item(n) for n in m.ALL_IDS]
        rows.append({"number":181,"pull_request":{"url":"..."}})
        self.assertEqual(len(m.check_baseline(rows)),53)

    def test_accessibility_and_bloqueado_explicit(self):
        self.assertEqual(m.ALIASES["accessibility"], "tipo:accesibilidad")
        self.assertIn("estado:bloqueado", m.DEFINITIONS)
        self.assertIn("dependencia", m.DEFINITIONS["estado:bloqueado"][1])
        labels={
            name:{"name":name,"color":color,"description":description}
            for name,(color,description) in m.DEFINITIONS.items()
        }
        labels["accessibility"]={
            "name":"accessibility","color":"e4e4e4","description":"Accessibility"
        }
        # Etiqueta heredada conocida, no equivale a un nombre desconocido.
        result=m.inspect([make_item(n) for n in m.ALL_IDS],labels)
        self.assertEqual(result["unknown_labels"],[])
        self.assertIn("accessibility",result["legacy_labels"])

    def test_legacy_alias_mapped(self):
        self.assertEqual(m.ALIASES["semana:05"],"fase:05")
        self.assertEqual(m.ALIASES["tipo:docs"],"tipo:documentación")
        self.assertEqual(m.ALIASES["bug"],"tipo:error")

    def test_dry_run_no_api_writes(self):
        rows=[make_item(n) for n in m.ALL_IDS]
        labels={name:{"name":name,"color":color,"description":description}
                for name,(color,description) in m.DEFINITIONS.items()}
        with (mock.patch.object(m,"all_items",return_value=rows),
              mock.patch.object(m,"label_inventory",return_value=labels),
              mock.patch.object(m,"gh") as gh):
            m.run(False)
            gh.assert_not_called()

    def test_status_reason_conserved_by_label_update(self):
        rows=[make_item(28)]
        with mock.patch.object(m,"gh") as gh:
            m.set_issue_assignments(rows)
            gh.assert_not_called()

    def test_label_write_only_if_mismatched(self):
        row=make_item(5)
        row["labels"]=[{"name":"semana:05"}]
        with mock.patch.object(m,"gh",return_value=[]) as gh:
            m.set_issue_assignments([row])
            gh.assert_called_once_with(
                f"{m.ROOT}/issues/5/labels","PUT",
                {"labels":["fase:05","tipo:infraestructura"]})


if __name__=="__main__":
    unittest.main()
