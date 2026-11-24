"""Comprobaciones de presentación y enlaces de la documentación técnica."""
from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
BASE_WEB = "https://github.com/recm0708/netlab360/blob/main/"
FASES = {1: 83, 2: 9, 3: 8, 4: 22, 5: 71, 6: 11, 7: 49}
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
            if not re.search(r"(?m)^# \S", texto):
                fallos.append(f"Falta título: {relativos}")
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
