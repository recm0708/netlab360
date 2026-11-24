"""Regresión offline de los metadatos obligatorios de PR."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/operacion"))
from auditar_metadatos_prs import audit


class MetadatosPRTests(unittest.TestCase):
    def setUp(self):
        self.pr = {"number": 1, "title": "[GESTIÓN] Consolidar documentación técnica",
                   "state": "closed", "milestone": {"title": "S08"},
                   "labels": [{"name": "fase:08"}, {"name": "tipo:documentación"}],
                   "assignees": [{"login": "operador"}]}

    def test_valido(self):
        self.assertEqual(audit([self.pr])["defects"], [])

    def test_cada_campo(self):
        for field, value, reason in [
            ("milestone", {"title": "S09"}, "MILESTONE_INVALIDO"), ("assignees", [], "ASSIGNEE"),
            ("labels", [{"name": "tipo:documentación"}], "ETIQUETA_FASE_MILESTONE"),
            ("labels", [{"name": "fase:08"}], "ETIQUETA_TEMATICA"),
            ("title", "Título sin fase", "TITULO"),
        ]:
            with self.subTest(field=field, reason=reason):
                pr = copy.deepcopy(self.pr)
                pr[field] = value
                self.assertIn(reason, audit([pr])["defects"][0]["reasons"])

    def test_transversal_con_fase_adicional(self):
        self.pr["labels"].append({"name": "fase:02"})
        self.assertEqual(audit([self.pr])["defects"], [])

    def test_transversal_sin_milestone(self):
        self.pr["milestone"] = None
        self.pr["labels"].append({"name": "fase:02"})
        report = audit([self.pr])
        self.assertEqual(report["defects"], [])
        self.assertEqual(report["without_milestone"], [1])

    def test_gestion_general_sin_fase_ni_milestone(self):
        self.pr["milestone"] = None
        self.pr["labels"] = [{"name": "tipo:documentación"}]
        self.assertEqual(audit([self.pr])["defects"], [])

    def test_titulo_de_fase_exige_etiqueta_aun_sin_milestone(self):
        self.pr["title"] = "[S02] Consolidar documentación técnica"
        self.pr["milestone"] = None
        self.assertIn("ETIQUETA_FASE_TITULO", audit([self.pr])["defects"][0]["reasons"])

    def test_milestone_transversal_requiere_revision_no_es_defecto(self):
        self.pr["labels"].append({"name": "fase:02"})
        report = audit([self.pr])
        self.assertEqual(report["defects"], [])
        self.assertEqual(report["review_milestone"], [1])

    def test_inventario_duplicado_o_vacio(self):
        for rows in ([], [self.pr, self.pr]):
            with self.assertRaises(ValueError):
                audit(rows)
