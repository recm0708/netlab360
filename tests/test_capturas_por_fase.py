"""Pruebas del catálogo gráfico y de la inspección básica de PNG."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validacion/validar-capturas-unificadas.py"
spec = importlib.util.spec_from_file_location("netlab_capturas", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class CatalogoCapturasTests(unittest.TestCase):
    """Comprueba las fases terminadas y el formato de las imágenes."""

    def test_inventario_de_fases(self):
        conteos = module.validar_catalogo()
        self.assertEqual(
            [conteos[i] for i in range(1, 9)],
            [83, 9, 8, 22, 71, 11, 0, 0],
        )

    def test_cabecera_invalida(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directorio:
            archivo = Path(directorio) / "prueba.png"
            archivo.write_bytes(b"incorrecto")
            with self.assertRaises(ValueError):
                module.inspeccionar_png(archivo)


if __name__ == "__main__":
    unittest.main()
