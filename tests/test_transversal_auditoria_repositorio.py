"""Pruebas de nomenclatura y referencias para auditoría documental."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts/validacion"))
from auditar_repositorio import anchors, markdown_lines, proposed_name, resolve_link

class AuditoriaRepositorioTests(unittest.TestCase):
    def test_documento(self):
        self.assertEqual(proposed_name("docs/decisiones/ADR-001-vmware-vm-sin-iso.md"),"docs/decisiones/adr-001-entorno-virtualizacion.md")
    def test_test_transversal(self):
        self.assertEqual(proposed_name("tests/test_capturas_por_fase.py"),"tests/test_transversal_capturas.py")
    def test_modulo_python(self):
        self.assertEqual(proposed_name("scripts/laboratorio/s02-failover-wan.py"),"scripts/laboratorio/s02_failover_wan.py")
    def test_convenciones_reservadas(self):
        for path in ("README.md","CITATION.cff","iac/s03/main.tf","topologias/s02-frr/docker-compose.yml","evidencias/capturas/fase7/S07_F01_Observaciones_Reales_NOC_IA.png"):
            self.assertEqual(proposed_name(path),path)
    def test_enlace_relativo(self):
        self.assertEqual(resolve_link("docs/diseno/x.md","../gestion/a.md#estado"),("docs/gestion/a.md","estado"))
    def test_enlace_historico(self):
        self.assertIsNone(resolve_link("README.md","https://github.com/recm0708/netlab360/blob/abcdef/docs/a.md"))
    def test_anchor(self):
        self.assertEqual(anchors("# Título\n## Validación\n## Validación\n"),{"título","validación","validación-1"})
    def test_fences(self):
        self.assertEqual(list(markdown_lines("# Título\n"+chr(96)*3+"python\n# No es título\n"+chr(96)*3+"\n## Validación")),[(1,"# Título"),(5,"## Validación")])
if __name__=="__main__":
    unittest.main()
