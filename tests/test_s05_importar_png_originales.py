"""Verificación ZIP de PNG y manifiesto sin tocar originales."""
import csv
import hashlib
import importlib.util
from pathlib import Path
import zipfile
from tempfile import TemporaryDirectory
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts/validacion/s05-importar-png-originales.py"
spec = importlib.util.spec_from_file_location("png_import", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestPngImport(unittest.TestCase):
    def test_csv_zip_valid(self):
        data = m.PNG_MAGIC + b"datos_png"
        digest = hashlib.sha256(data).hexdigest()
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            csvpath = root / "manifest.csv"
            with csvpath.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Archivo", "Bytes", "SHA256", "Ruta"])
                writer.writerow(["S05_01_evidencia.png", len(data), digest, "C:/dummy"])
            zipped = root / "evidencias.zip"
            with zipfile.ZipFile(zipped, "w") as f:
                f.writestr("S05_01_evidencia.png", data)
            records = m.read_csv(csvpath, expected_count=1)
            items = m.verify_zip(zipped, records)
            self.assertEqual(items["S05_01_evidencia.png"], data)

    def test_zip_sha_mismatch_aborts(self):
        data = m.PNG_MAGIC + b"abc"
        with TemporaryDirectory() as tmp:
            zipped = Path(tmp) / "evidencias.zip"
            with zipfile.ZipFile(zipped, "w") as f:
                f.writestr("S05_01_evidencia.png", data)
            with self.assertRaisesRegex(RuntimeError, "SHA256"):
                m.verify_zip(zipped, {"S05_01_evidencia.png": (len(data), "0"*64)})

    def test_import_cannot_overwrite_existing(self):
        data = m.PNG_MAGIC + b"123"
        digest = hashlib.sha256(data).hexdigest()
        with TemporaryDirectory() as tmp:
            d = Path(tmp)
            name = "S05_01_evidencia.png"
            (d / name).write_bytes(data)
            with self.assertRaisesRegex(RuntimeError, "no sobrescribir"):
                m.import_png({name: data}, {name: (len(data), digest)}, d)
            self.assertEqual((d / name).read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
