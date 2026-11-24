"""Pruebas offline para el lector de procedencia P1; no toca datos ni red."""
import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts/validacion/s05_auditar_origen_p1.py"
spec = importlib.util.spec_from_file_location("s05_p1_origen", SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestP1Origen(unittest.TestCase):
    def test_hash_matches_expected_documented_sha_format(self):
        self.assertEqual(set(m.EXPECTED), {
            "S05_P1_20261110-110047.log",
            "01_un_flujo.json",
            "02_ocho_flujos.json",
            "03_falla_retorno.json",
        })
        self.assertTrue(all(len(x) == 64 for x in m.EXPECTED.values()))

    def test_reader_inspects_bytes_without_extracting_files(self):
        data = b'{"test": "ok"}'
        expected = {"01_un_flujo.json": hashlib.sha256(data).hexdigest()}
        with TemporaryDirectory() as temp:
            path = Path(temp) / "ejemplo-P1.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                info = tarfile.TarInfo("rutas/lacp-p1/01_un_flujo.json")
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            found = m.archive_matches(path, expected)
            self.assertEqual(found["01_un_flujo.json"], [expected["01_un_flujo.json"]])
            self.assertFalse((Path(temp) / "rutas").exists())

    def test_reader_skips_symlink_members(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "ejemplo-P1.tar"
            with tarfile.open(path, "w") as archive:
                info = tarfile.TarInfo("01_un_flujo.json")
                info.type = tarfile.SYMTYPE
                info.linkname = "/etc/passwd"
                archive.addfile(info)
            found = m.archive_matches(path, {"01_un_flujo.json": "x" * 64})
            self.assertEqual(found["01_un_flujo.json"], [])

    def test_actual_file_hash_is_read_only(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "un_flujo.json"
            path.write_bytes(b"abc")
            self.assertEqual(m.file_digest(path), hashlib.sha256(b"abc").hexdigest())
            self.assertEqual(path.read_bytes(), b"abc")


if __name__ == "__main__":
    unittest.main()
