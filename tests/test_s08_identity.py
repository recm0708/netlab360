"""Pruebas de migración e identidades S08 con credenciales exclusivamente sintéticas."""
from contextlib import closing
import importlib.util
from pathlib import Path
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location(
    "netlab360_s08_identity", package / "__init__.py",
    submodule_search_locations=[str(package)])
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_identity import security as s, storage as db

PASSWORD = "synthetic test phrase only"


@unittest.skipIf(os.geteuid() == 0, "La persistencia exige usuario sin root")
class IdentityTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name) / "estado"
        db.initialize(self.directory)
        self.path = self.directory / db.DB_NAME

    def rows(self, query):
        with closing(sqlite3.connect(self.path)) as conn:
            return conn.execute(query).fetchall()

    def test_migration_preserves_history(self):
        history = self.rows("SELECT * FROM audit_events")
        version = self.rows("SELECT * FROM schema_migrations")
        result = db.migrate(self.directory)
        self.assertEqual((result["schema_version"], result["jobs"], result["audit_events"]), (2,0,2))
        self.assertEqual(self.rows("SELECT * FROM audit_events ORDER BY event_id")[:1], history)
        self.assertEqual(self.rows("SELECT * FROM schema_migrations ORDER BY version")[:1], version)
        self.assertEqual(self.rows("SELECT * FROM users"), [])
        self.assertEqual(self.rows("SELECT * FROM sessions"), [])

    def test_migration_idempotent(self):
        first = db.migrate(self.directory)
        before = self.path.read_bytes()
        self.assertEqual(db.migrate(self.directory), first)
        self.assertEqual(self.path.read_bytes(), before)

    def test_migration_rollback(self):
        with patch.object(db, "DDL_V2", (db.DDL_V2[0], "INVALID SQL")):
            with self.assertRaises(sqlite3.OperationalError):
                db.migrate(self.directory)
        self.assertEqual(db.inspect(self.directory)["schema_version"], 1)
        self.assertEqual(self.rows("SELECT COUNT(*) FROM audit_events"), [(1,)])

    def test_old_schema_rejected_for_accounts(self):
        with self.assertRaisesRegex(ValueError, "SECURITY_SCHEMA_REQUIRED"):
            s.create_user(self.directory, "viewer", PASSWORD, "VIEWER")

    def test_password_policy(self):
        for password in ("short", "", "x"*257):
            with self.subTest(password_length=len(password)):
                with self.assertRaisesRegex(ValueError, "INVALID_PASSWORD"):
                    s.derive(password, b"x"*16, enrollment=True)

    def test_scrypt_parameters_and_salt(self):
        self.assertEqual((s.N,s.R,s.P), (131072,8,1))
        self.assertNotEqual(s.derive(PASSWORD,b"x"*16),s.derive(PASSWORD,b"y"*16))

    def test_role_and_username_validation(self):
        db.migrate(self.directory)
        with self.assertRaisesRegex(ValueError,"INVALID_ROLE"):
            s.create_user(self.directory,"viewer",PASSWORD,"ROOT")
        with self.assertRaisesRegex(ValueError,"INVALID_USERNAME"):
            s.create_user(self.directory,"../viewer",PASSWORD,"VIEWER")

    def test_create_and_authenticate(self):
        db.migrate(self.directory)
        result = s.create_user(self.directory,"viewer",PASSWORD,"VIEWER")
        self.assertEqual(s.authenticate(self.directory,"viewer",PASSWORD),result)
        self.assertIs(result["network_mutations_authorized"],False)
        self.assertNotIn(PASSWORD.encode(),self.path.read_bytes())
        self.assertEqual(self.rows("SELECT length(password_salt),length(password_digest) FROM users"),[(16,32)])

    def test_wrong_and_unknown_password(self):
        db.migrate(self.directory)
        s.create_user(self.directory,"viewer",PASSWORD,"VIEWER")
        self.assertIsNone(s.authenticate(self.directory,"viewer","wrong"))
        self.assertIsNone(s.authenticate(self.directory,"unknown",PASSWORD))

    def test_duplicate_does_not_replace(self):
        db.migrate(self.directory)
        s.create_user(self.directory,"viewer",PASSWORD,"VIEWER")
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError,"USER_EXISTS"):
            s.create_user(self.directory,"viewer",PASSWORD,"OPERATOR")
        self.assertEqual(self.path.read_bytes(),before)

    def test_operator_has_no_mutation_authority(self):
        db.migrate(self.directory)
        result = s.create_user(self.directory,"operator",PASSWORD,"OPERATOR")
        self.assertEqual(result["role"],"OPERATOR")
        self.assertIs(result["network_mutations_authorized"],False)

    def test_disabled_account(self):
        db.migrate(self.directory)
        s.create_user(self.directory,"viewer",PASSWORD,"VIEWER")
        with closing(sqlite3.connect(self.path)) as conn:
            conn.execute("UPDATE users SET enabled=0 WHERE username=?",("viewer",))
            conn.commit()
        self.assertIsNone(s.authenticate(self.directory,"viewer",PASSWORD))


if __name__ == "__main__":
    unittest.main()
