"""Pruebas offline de persistencia S08 en directorios temporales privados."""
from contextlib import closing
import importlib.util
from pathlib import Path
import os
import sqlite3
import stat
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "s08_storage", ROOT / "servicios/consola-s08/api/storage.py")
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@unittest.skipIf(os.geteuid() == 0, "La persistencia exige usuario sin root")
class StorageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.parent = Path(tmp.name)
        self.directory = self.parent / "estado"
        self.db = self.directory / m.DB_NAME

    def test_initialize(self):
        r = m.initialize(self.directory)
        self.assertEqual((r["integrity"], r["schema_version"], r["jobs"],
                          r["audit_events"]), ("OK", 1, 0, 1))
        self.assertIs(r["network_mutations_authorized"], False)

    def test_permissions(self):
        m.initialize(self.directory)
        self.assertEqual(stat.S_IMODE(self.directory.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE(self.db.stat().st_mode), 0o600)

    def test_repeat_is_idempotent(self):
        first = m.initialize(self.directory)
        data = self.db.read_bytes()
        self.assertEqual(m.initialize(self.directory), first)
        self.assertEqual(self.db.read_bytes(), data)

    def test_check_read_only(self):
        m.initialize(self.directory)
        before = self.db.stat().st_mtime_ns, self.db.read_bytes()
        self.assertEqual(m.inspect(self.directory)["integrity"], "OK")
        self.assertEqual((self.db.stat().st_mtime_ns, self.db.read_bytes()), before)

    def test_check_missing_does_not_create(self):
        with self.assertRaises(FileNotFoundError):
            m.inspect(self.directory)
        self.assertFalse(self.directory.exists())

    def test_foreign_database_not_overwritten(self):
        self.directory.mkdir(mode=0o700)
        self.db.write_bytes(b"")
        self.db.chmod(0o600)
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("CREATE TABLE foreign_data(value TEXT)")
            db.execute("INSERT INTO foreign_data VALUES (?)", ("preserve",))
            db.commit()
        before = self.db.read_bytes()
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_STORAGE_SCHEMA"):
            m.initialize(self.directory)
        self.assertEqual(self.db.read_bytes(), before)

    def test_future_version_refused(self):
        m.initialize(self.directory)
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("PRAGMA user_version=4")
        before = self.db.read_bytes()
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_STORAGE_SCHEMA"):
            m.initialize(self.directory)
        self.assertEqual(self.db.read_bytes(), before)

    def test_directory_symlink_refused(self):
        target = self.parent / "target"
        target.mkdir(mode=0o700)
        self.directory.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "UNSAFE_STORAGE_DIRECTORY"):
            m.initialize(self.directory)
        self.assertEqual(list(target.iterdir()), [])

    def test_database_symlink_refused(self):
        self.directory.mkdir(mode=0o700)
        target = self.parent / "target"
        target.write_bytes(b"preserve")
        self.db.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "UNSAFE_STORAGE_DATABASE"):
            m.initialize(self.directory)
        self.assertEqual(target.read_bytes(), b"preserve")

    def test_hardlink_refused(self):
        m.initialize(self.directory)
        os.link(self.db, self.parent / "alias")
        with self.assertRaisesRegex(ValueError, "UNSAFE_STORAGE_DATABASE"):
            m.inspect(self.directory)

    def test_unsafe_permissions_refused(self):
        m.initialize(self.directory)
        self.db.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "UNSAFE_STORAGE_DATABASE"):
            m.inspect(self.directory)
        self.db.chmod(0o600)
        self.directory.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "UNSAFE_STORAGE_DIRECTORY"):
            m.inspect(self.directory)

    def test_parent_writable_refused(self):
        self.parent.chmod(0o777)
        self.addCleanup(self.parent.chmod, 0o700)
        with self.assertRaisesRegex(ValueError, "UNSAFE_STORAGE_DIRECTORY"):
            m.initialize(self.directory)

    def test_migration_rollback(self):
        with patch.object(m, "DDL", (m.DDL[0], "INVALID SQL")):
            with self.assertRaises(sqlite3.OperationalError):
                m.initialize(self.directory)
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [])
        with self.assertRaisesRegex(ValueError, "UNSUPPORTED_STORAGE_SCHEMA"):
            m.initialize(self.directory)

    def test_root_refused(self):
        with patch.object(m.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "S08_ROOT_FORBIDDEN"):
                m.initialize(self.directory)
        self.assertFalse(self.directory.exists())


if __name__ == "__main__":
    unittest.main()
