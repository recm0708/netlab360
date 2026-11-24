"""Validamos perfiles privados y migración explícita con datos sintéticos."""
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
    "netlab360_s08_profiles", package / "__init__.py",
    submodule_search_locations=[str(package)])
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_profiles import profiles, security, sessions, storage


@unittest.skipIf(os.geteuid() == 0, "La persistencia exige usuario sin root")
class ProfileTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / "estado"
        storage.initialize(self.directory)
        storage.migrate(self.directory)
        self.path = self.directory / storage.DB_NAME
        for user, role in (("viewer", "VIEWER"), ("operator", "OPERATOR")):
            security.create_user(self.directory, user, "synthetic test phrase only", role)

    def rows(self, query):
        with closing(sqlite3.connect(self.path)) as db:
            return db.execute(query).fetchall()

    def test_migration_preserves_users_sessions_history(self):
        issued = sessions.issue(self.directory, "viewer")
        before = [self.rows("SELECT * FROM " + table + " ORDER BY 1")
                  for table in ("users", "sessions", "jobs", "audit_events")]
        result = storage.migrate_v3(self.directory)
        self.assertEqual(result["schema_version"], 3)
        for table, expected in zip(("users", "sessions", "jobs", "audit_events"), before):
            self.assertEqual(self.rows("SELECT * FROM " + table + " ORDER BY 1")[:len(expected)], expected)
        self.assertEqual(sessions.resolve(self.directory, issued["token"])["username"], "viewer")
        self.assertEqual(self.rows("SELECT username FROM profiles ORDER BY username"),
                         [("operator",), ("viewer",)])
        self.assertEqual(security.authenticate(self.directory, "viewer", "synthetic test phrase only")["role"], "VIEWER")

    def test_idempotence(self):
        first = storage.migrate_v3(self.directory)
        before = self.path.read_bytes()
        self.assertEqual(storage.migrate_v3(self.directory), first)
        self.assertEqual(storage.migrate(self.directory), first)
        self.assertEqual(self.path.read_bytes(), before)

    def test_rollback(self):
        with patch.object(storage, "DDL_V3", (storage.DDL_V3[0], "INVALID SQL")):
            with self.assertRaises(sqlite3.OperationalError):
                storage.migrate_v3(self.directory)
        self.assertEqual(storage.inspect(self.directory)["schema_version"], 2)

    def test_v2_refuses_profile(self):
        with self.assertRaisesRegex(ValueError, "PROFILE_SCHEMA_REQUIRED"):
            profiles.read_self(self.directory, "viewer")

    def test_profile_isolation_and_audit(self):
        storage.migrate_v3(self.directory)
        other = profiles.read_self(self.directory, "operator")
        result = profiles.update_self(self.directory, "viewer", display_name="Persona de prueba",
                                      email="example@example.invalid")
        self.assertEqual(result["display_name"], "Persona de prueba")
        self.assertEqual(profiles.read_self(self.directory, "operator"), other)
        self.assertFalse(result["network_mutations_authorized"])
        audit = str(self.rows("SELECT details_json FROM audit_events"))
        self.assertNotIn("example@example.invalid", audit)
        self.assertNotIn("Persona de prueba", audit)

    def test_invalid_and_disabled(self):
        storage.migrate_v3(self.directory)
        for name, email in (("x"*101, ""), ("x\n", ""), ("x", "invalid")):
            with self.assertRaisesRegex(ValueError, "INVALID_PROFILE"):
                profiles.update_self(self.directory, "viewer", display_name=name, email=email)
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("UPDATE users SET enabled=0 WHERE username='viewer'")
            db.commit()
        with self.assertRaises(PermissionError):
            profiles.read_self(self.directory, "viewer")
        with self.assertRaises(PermissionError):
            profiles.update_self(self.directory, "viewer", display_name="", email="")

    def test_new_account_profile_and_no_admin(self):
        storage.migrate_v3(self.directory)
        security.create_user(self.directory, "new-user", "synthetic test phrase only", "VIEWER")
        self.assertEqual(profiles.read_self(self.directory, "new-user")["display_name"], "")
        with self.assertRaisesRegex(ValueError, "INVALID_ROLE"):
            security.create_user(self.directory, "admin", "synthetic test phrase only", "ADMIN")

    def test_permissions_default_deny(self):
        for role in ("VIEWER", "OPERATOR"):
            self.assertTrue(profiles.permits(role, "profile:write:self"))
            self.assertFalse(profiles.permits(role, "users:write"))
            self.assertFalse(profiles.permits(role, "network:mutate"))
        self.assertTrue(profiles.permits("OPERATOR", "debug:read"))
        self.assertFalse(profiles.permits("VIEWER", "debug:read"))
        self.assertFalse(profiles.permits("ADMIN", "users:write"))


if __name__ == "__main__":
    unittest.main()
