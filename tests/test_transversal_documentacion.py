"""Comprobaciones de presentación y enlaces de la documentación técnica."""
from __future__ import annotations

import re
import sys
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
BASE_WEB = "https://github.com/recm0708/netlab360/blob/main/"
FASES = {1: 83, 2: 9, 3: 8, 4: 22, 5: 71, 6: 11, 7: 49}
sys.path.insert(0, str(ROOT / "scripts/validacion"))
from auditar_repositorio import markdown_lines, proposed_name

ENLACE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def documentos_tecnicos():
    """Retorna los documentos incluidos en el proyecto."""
    for documento in ROOT.rglob("*.md"):
        yield documento


class DocumentacionProyectoTests(unittest.TestCase):
    """Preserva las convenciones editoriales sin intervenir los servicios."""

    def test_titulos_y_referencias(self):
        fallos = []
        for doc in documentos_tecnicos():
            texto = doc.read_text(encoding="utf-8")
            relativos = doc.relative_to(ROOT).as_posix()
            if sum(bool(re.match(r"^#\s+\S", linea)) for _, linea in markdown_lines(texto)) != 1:
                fallos.append(f"Título H1 no único: {relativos}")
            if re.search(r"sha[-_ ]?256|\.sha256|evidencias/manifiestos|\bmanifiestos?\b",
                         texto, flags=re.IGNORECASE):
                fallos.append(f"Referencia administrativa: {relativos}")

            for enlazado in ENLACE.findall(texto):
                destino = unquote(enlazado.split("#", 1)[0].strip())
                if not destino:
                    continue
                if destino.startswith(BASE_WEB):
                    ruta = ROOT / destino.removeprefix(BASE_WEB)
                elif "://" in destino or destino.startswith(("mailto:", "#")):
                    continue
                else:
                    ruta = doc.parent / destino
                if not ruta.exists():
                    fallos.append(f"Enlace ausente: {relativos} → {destino}")
        self.assertEqual(fallos, [])

    def test_nomenclatura_versionada(self):
        rutas = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        errores = []
        for ruta in filter(None, rutas):
            nombre = Path(ruta).name
            if proposed_name(ruta) != ruta:
                errores.append(ruta)
            elif ruta.endswith(".py") and not re.fullmatch(r"[a-z][a-z0-9_]*\.py", nombre):
                errores.append(ruta)
            elif ruta.startswith("tests/") and ruta.endswith(".py") and not re.fullmatch(r"test_(s\d{2}|transversal)_[a-z0-9_]+\.py", nombre):
                errores.append(ruta)
            elif ruta.startswith("docs/") and ruta.endswith(".md") and nombre != "README.md" and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.md", nombre):
                errores.append(ruta)
        self.assertEqual(errores, [])

    def test_catalogos_de_capturas(self):
        carpeta = ROOT / "evidencias/capturas"
        for fase, cantidad in FASES.items():
            actual = carpeta / f"fase{fase}"
            documentos = sorted(item.name for item in actual.glob("*.md"))
            self.assertEqual(documentos, ["README.md"], actual)
            self.assertEqual(len(list(actual.glob("*.png"))), cantidad, actual)

    def test_sin_archivos_de_control_grafico(self):
        self.assertEqual(list(ROOT.rglob("*.sha256")), [])
        self.assertFalse((ROOT / "evidencias/manifiestos").exists())


if __name__ == "__main__":
    unittest.main()
