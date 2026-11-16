"""Pruebas del contrato importacion S04 LOTE03 usando PNG real ya versionada."""
import csv
import importlib.util
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validacion/importar-s04-lote03.py"
spec = importlib.util.spec_from_file_location("nl360_s04_import_lote3", SCRIPT)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
REAL = ROOT / "evidencias/capturas/fase4/S04_11_Recuperacion_WAN_Alerta_Resuelta.png"


class ImporterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.repo = self.home / "repo"
        (self.repo / "evidencias/capturas/fase4").mkdir(parents=True)
        (self.repo / "evidencias/manifiestos").mkdir(parents=True)
        self.zip = self.home / "lot3.zip"
        self.data = REAL.read_bytes()

    def make_zip(self, bad_hash=False, extra=False):
        buf = io.StringIO(newline="")
        w = csv.DictWriter(buf, fieldnames=("Name", "SHA256", "Length"),
                           lineterminator="\r\n")
        w.writeheader()
        digest = hashlib.sha256(self.data).hexdigest()
        with ZipFile(self.zip, "w", ZIP_DEFLATED) as z:
            for idx, name in enumerate(m.NAMES):
                z.writestr(name, self.data)
                w.writerow({"Name": name, "SHA256": "0" * 64 if bad_hash and idx == 0
                            else digest, "Length": len(self.data)})
            z.writestr(m.ORIGIN, buf.getvalue())
            if extra:
                z.writestr("unwanted.txt", "not allowed")

    def test_valid_real_png_generates_unix_lf_manifest(self):
        self.make_zip()
        checked, origin = m.check_zip(self.zip, repo=self.repo)
        self.assertEqual(len(checked), 8)
        self.assertEqual(len(origin) > 0, True)
        self.assertEqual(len([x for x in checked if x[0].suffix == ".png"]), 7)
        manifest = checked[-1][1]
        self.assertNotIn(b"\r\n", manifest)
        self.assertEqual(len(list(csv.DictReader(io.StringIO(manifest.decode())))), 7)

    def test_source_sha_mismatch_rejected(self):
        self.make_zip(bad_hash=True)
        with self.assertRaisesRegex(ValueError, "SHA256"):
            m.check_zip(self.zip, repo=self.repo)

    def test_unexpected_zip_files_rejected(self):
        self.make_zip(extra=True)
        with self.assertRaisesRegex(ValueError, "siete PNG"):
            m.check_zip(self.zip, repo=self.repo)

    def test_existing_original_is_never_overwritten(self):
        self.make_zip()
        (self.repo / "evidencias/capturas/fase4" / m.NAMES[0]).write_bytes(self.data)
        with self.assertRaisesRegex(ValueError, "ya publicada"):
            m.check_zip(self.zip, repo=self.repo)

    def test_missing_archive_refused(self):
        with self.assertRaisesRegex(ValueError, "ZIP ausente"):
            m.check_zip(self.home / "no-such.zip", repo=self.repo)


if __name__ == "__main__":
    unittest.main()
