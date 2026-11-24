"""Persistencia privada S08: inicialización explícita y comprobación solo lectura."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import stat

APPLICATION_ID = 0x4E4C5338
SCHEMA_VERSION = 1
LATEST_SCHEMA_VERSION = 3
DB_NAME = "consola.sqlite3"
TABLES = frozenset({"schema_migrations", "jobs", "audit_events"})
TABLES_V2 = TABLES | {"users", "sessions"}
TABLES_V3 = TABLES_V2 | {"profiles"}

# Los trabajos se reservan para una fase posterior: no se crean
# registros de ejecución ficticios ni se interpretan como RFC S07.
DDL = (
    """CREATE TABLE schema_migrations (
        version INTEGER PRIMARY KEY CHECK(version = 1),
        applied_at_utc TEXT NOT NULL
    )""",
    """CREATE TABLE jobs (
        job_id TEXT PRIMARY KEY NOT NULL,
        action_id TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        created_at_utc TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN
            ('QUEUED','RUNNING','SUCCEEDED','FAILED','CANCELLED')),
        finished_at_utc TEXT,
        result_json TEXT
    )""",
    """CREATE TABLE audit_events (
        event_id INTEGER PRIMARY KEY,
        event_type TEXT NOT NULL,
        observed_at_utc TEXT NOT NULL,
        details_json TEXT NOT NULL
    )""",
)


def default_dir() -> Path:
    """Ruta de desarrollo privada, independiente de las bases S06/S07."""
    return Path.home() / "netlab360-bootstrap/s08/estado"


def _owned_directory(path: Path, *, private: bool) -> None:
    """Rechazar enlaces y directorios con permisos o propietario inseguros."""
    info = path.lstat()
    mode = stat.S_IMODE(info.st_mode)
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid()
            or (mode != 0o700 if private else bool(mode & 0o022))):
        raise ValueError("UNSAFE_STORAGE_DIRECTORY")


def _directory(directory: Path, *, create: bool) -> Path:
    if os.geteuid() == 0:
        raise RuntimeError("S08_ROOT_FORBIDDEN")
    if not directory.is_absolute() or ".." in directory.parts:
        raise ValueError("INVALID_STORAGE_PATH")
    _owned_directory(directory.parent, private=False)
    if create:
        try:
            directory.mkdir(mode=0o700)
        except FileExistsError:
            pass
    _owned_directory(directory, private=True)
    return directory / DB_NAME


def _owned_database(path: Path) -> None:
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1):
        raise ValueError("UNSAFE_STORAGE_DATABASE")


def _connect(path: Path, *, readonly: bool) -> sqlite3.Connection:
    _owned_database(path)
    mode = "ro" if readonly else "rw"
    connection = sqlite3.connect(path.as_uri() + "?mode=" + mode,
                                 uri=True, timeout=5, isolation_level=None)
    try:
        connection.execute("PRAGMA foreign_keys=ON")
        if readonly:
            connection.execute("PRAGMA query_only=ON")
    except BaseException:
        connection.close()
        raise
    return connection


def inspect(directory: Path) -> dict:
    """Comprobar identidad, versión, integridad y cantidades sin escribir."""
    path = _directory(directory, create=False)
    with closing(_connect(path, readonly=True)) as db:
        app_id = db.execute("PRAGMA application_id").fetchone()[0]
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if app_id != APPLICATION_ID or version not in (1, 2, LATEST_SCHEMA_VERSION):
            raise ValueError("UNSUPPORTED_STORAGE_SCHEMA")
        tables = {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if tables != {1: TABLES, 2: TABLES_V2, 3: TABLES_V3}[version]:
            raise ValueError("UNEXPECTED_STORAGE_TABLES")
        if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise ValueError("STORAGE_INTEGRITY_ERROR")
        migrations = db.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
        if migrations != [(v,) for v in range(1, version + 1)]:
            raise ValueError("INVALID_MIGRATION_HISTORY")
        jobs = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        events = db.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0]
    return {
        "schema": f"NETLAB360_S08_STORAGE_V{version}",
        "schema_version": version,
        "integrity": "OK",
        "jobs": jobs,
        "audit_events": events,
        "network_mutations_authorized": False,
    }


def initialize(directory: Path) -> dict:
    """Crear una base nueva; nunca migrar ni sobrescribir una base desconocida."""
    path = _directory(directory, create=True)
    try:
        # El descriptor exclusivo impide sustituir bases existentes o enlaces.
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except FileExistsError:
        return inspect(directory)
    try:
        os.fchmod(fd, 0o600)
    finally:
        os.close(fd)

    # La transacción incluye DDL, versión y evidencia de inicialización.
    # Ante una interrupción conservamos la base para diagnóstico; no la borramos.
    with closing(_connect(path, readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            for statement in DDL:
                db.execute(statement)
            stamp = datetime.now(timezone.utc).isoformat()
            db.execute("INSERT INTO schema_migrations VALUES (?, ?)",
                       (SCHEMA_VERSION, stamp))
            db.execute(
                "INSERT INTO audit_events(event_type, observed_at_utc, details_json) VALUES (?, ?, ?)",
                ("STORAGE_INITIALIZED", stamp,
                 json.dumps({"schema_version": SCHEMA_VERSION}, separators=(",", ":"))))
            db.execute(f"PRAGMA application_id={APPLICATION_ID}")
            db.execute(f"PRAGMA user_version={SCHEMA_VERSION}")
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return inspect(directory)


# La migración v2 amplía el historial sin alterar las filas de trabajos.
DDL_V2 = (
    "ALTER TABLE schema_migrations RENAME TO schema_migrations_v1",
    """CREATE TABLE schema_migrations (
        version INTEGER PRIMARY KEY CHECK(version BETWEEN 1 AND 2),
        applied_at_utc TEXT NOT NULL
    )""",
    "INSERT INTO schema_migrations SELECT version, applied_at_utc FROM schema_migrations_v1",
    "DROP TABLE schema_migrations_v1",
    """CREATE TABLE users (
        username TEXT PRIMARY KEY NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('VIEWER','OPERATOR')),
        password_salt BLOB NOT NULL CHECK(length(password_salt)=16),
        password_digest BLOB NOT NULL CHECK(length(password_digest)=32),
        enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),
        created_at_utc TEXT NOT NULL
    )""",
    """CREATE TABLE sessions (
        token_digest BLOB PRIMARY KEY NOT NULL CHECK(length(token_digest)=32),
        username TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
        csrf_digest BLOB NOT NULL CHECK(length(csrf_digest)=32),
        created_at INTEGER NOT NULL,
        expires_at INTEGER NOT NULL CHECK(expires_at > created_at)
    )""",
)


def migrate(directory: Path) -> dict:
    """Ampliar una base v1 verificada de forma transaccional y explícita."""
    before = inspect(directory)
    if before["schema_version"] >= 2:
        return before
    path = _directory(directory, create=False)
    with closing(_connect(path, readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            if db.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID:
                raise ValueError("UNSUPPORTED_STORAGE_SCHEMA")
            if db.execute("PRAGMA user_version").fetchone()[0] != 1:
                raise ValueError("CONCURRENT_SCHEMA_CHANGE")
            for statement in DDL_V2:
                db.execute(statement)
            stamp = datetime.now(timezone.utc).isoformat()
            db.execute("INSERT INTO schema_migrations VALUES (?, ?)", (2, stamp))
            db.execute(
                "INSERT INTO audit_events(event_type, observed_at_utc, details_json) VALUES (?, ?, ?)",
                ("STORAGE_MIGRATED", stamp, '{"schema_version":2}'))
            db.execute("PRAGMA user_version=2")
            if db.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("STORAGE_FOREIGN_KEY_ERROR")
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return inspect(directory)


# Conservamos usuarios, verificadores y sesiones existentes. La administración
# de terceros no se activa por la mera migración de almacenamiento.
DDL_V3 = (
    "ALTER TABLE schema_migrations RENAME TO schema_migrations_v2",
    """CREATE TABLE schema_migrations (
        version INTEGER PRIMARY KEY CHECK(version BETWEEN 1 AND 3),
        applied_at_utc TEXT NOT NULL
    )""",
    "INSERT INTO schema_migrations SELECT version, applied_at_utc FROM schema_migrations_v2",
    "DROP TABLE schema_migrations_v2",
    """CREATE TABLE profiles (
        username TEXT PRIMARY KEY NOT NULL REFERENCES users(username) ON DELETE CASCADE,
        display_name TEXT NOT NULL DEFAULT '' CHECK(length(display_name)<=100),
        email TEXT NOT NULL DEFAULT '' CHECK(length(email)<=254),
        updated_at_utc TEXT NOT NULL
    )""",
    """INSERT INTO profiles(username, updated_at_utc)
        SELECT username, created_at_utc FROM users""",
    """CREATE TRIGGER profile_after_user_insert AFTER INSERT ON users
        BEGIN
            INSERT INTO profiles(username, updated_at_utc)
            VALUES (NEW.username, NEW.created_at_utc);
        END""",
)


def migrate_v3(directory: Path) -> dict:
    """Ampliar explícitamente v2, sin promover usuarios ni modificar sesiones."""
    before = inspect(directory)
    if before["schema_version"] == 3:
        return before
    if before["schema_version"] != 2:
        raise ValueError("STORAGE_V2_REQUIRED")
    path = _directory(directory, create=False)
    with closing(_connect(path, readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            if (db.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID
                    or db.execute("PRAGMA user_version").fetchone()[0] != 2):
                raise ValueError("CONCURRENT_SCHEMA_CHANGE")
            for statement in DDL_V3:
                db.execute(statement)
            stamp = datetime.now(timezone.utc).isoformat()
            db.execute("INSERT INTO schema_migrations VALUES (?, ?)", (3, stamp))
            db.execute(
                "INSERT INTO audit_events(event_type,observed_at_utc,details_json) VALUES (?,?,?)",
                ("STORAGE_MIGRATED", stamp, '{"schema_version":3}'))
            db.execute("PRAGMA user_version=3")
            if db.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("STORAGE_FOREIGN_KEY_ERROR")
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return inspect(directory)


def main() -> None:
    """CLI local de administración de almacenamiento, sin opciones de ruta web."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("init", "check", "migrate", "migrate-v3"))
    args = parser.parse_args()
    action = {"init": initialize, "check": inspect, "migrate": migrate,
              "migrate-v3": migrate_v3}[args.operation]
    print(json.dumps(action(default_dir()), sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
