"""Pruebas offline: títulos de PR NETLAB360."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[1]/"scripts/operacion/auditar_titulos_prs.py"
spec=importlib.util.spec_from_file_location("pr_es_check",SOURCE)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def make(count=129):
    return [
        {"number":i+1,
         "title":f"[S05] Documentar la comprobación del lote {i+1}",
         "state":"closed",
         "merged_at":"2026-11-23T00:00:00Z"}
        for i in range(count)
    ]


class PullRequestTitleTests(unittest.TestCase):
    def test_accept_all_129_merged(self):
        data=m.check(make())
        self.assertEqual((data["total"],data["merged"],data["open"]),(129,129,0))

    def test_accept_open_future_pr(self):
        items=make()
        items[0]["state"]="open"
        items[0]["merged_at"]=None
        self.assertEqual(m.check(items)["open"],1)

    def test_management_prefix(self):
        items=make()
        items[0]["title"]="[GESTIÓN] Auditar las milestones del proyecto"
        self.assertEqual(m.check(items)["normalized"],129)

    def test_reject_conventional_commit_prefix(self):
        items=make()
        items[0]["title"]="feat(S06): nuevo experimento"
        with self.assertRaisesRegex(ValueError,"non_normalized"):
            m.check(items)

    def test_reject_status_suffix(self):
        items=make()
        items[0]["title"]="[S05] Validar el enlace — CERRADO"
        with self.assertRaisesRegex(ValueError,"non_normalized"):
            m.check(items)

    def test_reject_too_small_inventory(self):
        with self.assertRaisesRegex(ValueError,"short"):
            m.check(make(127))

    def test_reject_duplicate(self):
        items=make()
        items[1]["number"]=1
        with self.assertRaisesRegex(ValueError,"duplicate"):
            m.check(items)

    def test_preserve_technical_words(self):
        items=make()
        items[0]["title"]="[S06] Probar el watchdog systemd con ICMP y OpenFlow"
        self.assertEqual(m.check(items)["normalized"],129)


    def test_new_phase_prefixes(self):
        for phase in (9, 10):
            rows = make()
            rows[0]["title"] = (
                f"[S{phase:02d}] Validar capacidad planificada"
            )
            self.assertEqual(m.check(rows)["normalized"], 129)

    def test_reject_unapproved_phase(self):
        rows = make()
        rows[0]["title"] = "[S11] Capacidad no planificada"
        with self.assertRaisesRegex(ValueError, "non_normalized"):
            m.check(rows)

if __name__=="__main__":
    unittest.main()
