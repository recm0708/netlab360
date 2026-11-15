"""Contrato offline de extracción P1 hacia directorio nuevo sin sobrescritura."""
from __future__ import annotations

import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
import unittest

SRC = Path(__file__).resolve().parents[1] / "scripts/validacion/s05-recuperar-p1-tar-historico.py"
spec = importlib.util.spec_from_file_location("s05_p1_recover", SRC)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestS05Recovery(unittest.TestCase):
    def test_tar_matching_content(self):
        raw = b'{"run":"historic"}'
        expected = {"01_un_flujo.json": hashlib.sha256(raw).hexdigest()}
        with TemporaryDirectory() as t:
            tar_path = Path(t) / "a.tar.gz"
            with tarfile.open(tar_path, "w:gz") as obj:
                info = tarfile.TarInfo("lacp-p1/01_un_flujo.json")
                info.size = len(raw)
                obj.addfile(info, io.BytesIO(raw))
            self.assertEqual(m.verified_members(tar_path, expected), {"01_un_flujo.json": raw})
            self.assertFalse((Path(t) / "lacp-p1").exists())

    def test_disagreeing_hash_fails(self):
        with TemporaryDirectory() as t:
            tar_path = Path(t) / "a.tar.gz"
            raw = b"bad"
            with tarfile.open(tar_path, "w:gz") as obj:
                info = tarfile.TarInfo("01_un_flujo.json")
                info.size = len(raw)
                obj.addfile(info, io.BytesIO(raw))
            with self.assertRaisesRegex(RuntimeError, "SHA no coincide"):
                m.verified_members(tar_path, {"01_un_flujo.json": "0" * 64})

    def test_destination_already_exists_is_preserved(self):
        with TemporaryDirectory() as t:
            d = Path(t) / "existing"
            d.mkdir()
            existing = d / "data.txt"
            existing.write_text("preservar")
            with self.assertRaisesRegex(RuntimeError, "ya existe"):
                m.recover({}, d)
            self.assertEqual(existing.read_text(), "preservar")

    def test_unsafe_symlink_member_is_rejected(self):
        with TemporaryDirectory() as t:
            tar_path = Path(t) / "a.tar.gz"
            with tarfile.open(tar_path, "w:gz") as obj:
                info = tarfile.TarInfo("01_un_flujo.json")
                info.type = tarfile.SYMTYPE
                info.linkname = "../../secret"
                obj.addfile(info)
            with self.assertRaisesRegex(RuntimeError, "inseguro"):
                m.verified_members(tar_path, {"01_un_flujo.json": "a" * 64})


if __name__ == "__main__":
    unittest.main()
