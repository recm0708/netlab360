"""Perfiles privados y permisos funcionales sin administración de terceros."""
from contextlib import closing
from datetime import datetime, timezone
import json
import re
import unicodedata

from . import security, storage

# ADMIN queda reservado hasta que exista autenticación multifactor obligatoria.
PERMISSIONS = {
    "VIEWER": frozenset({"profile:read:self", "profile:write:self", "network:read"}),
    "OPERATOR": frozenset({"profile:read:self", "profile:write:self", "network:read",
                           "debug:read"}),
}


def permits(role: str, permission: str) -> bool:
    """Denegar por defecto; ningún rol actual administra cuentas o interviene la red."""
    return permission in PERMISSIONS.get(role, frozenset())


def _identity(db, username, permission):
    security.validate_username(username)
    row = db.execute("SELECT role FROM users WHERE username=? AND enabled=1",
                     (username,)).fetchone()
    if row is None or not permits(row[0], permission):
        raise PermissionError("PROFILE_FORBIDDEN")
    return row[0]


def _path(directory):
    path = security._path(directory)
    with closing(storage._connect(path, readonly=True)) as db:
        if db.execute("PRAGMA user_version").fetchone()[0] != 3:
            raise ValueError("PROFILE_SCHEMA_REQUIRED")
    return path


def _validated(display_name, email):
    for value, limit in ((display_name, 100), (email, 254)):
        if (not isinstance(value, str) or len(value) > limit
                or any(unicodedata.category(c).startswith("C") for c in value)):
            raise ValueError("INVALID_PROFILE")
    name, address = display_name.strip(), email.strip()
    if address and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", address):
        raise ValueError("INVALID_PROFILE")
    return name, address


def _read(db, username, role):
    row = db.execute("SELECT display_name,email,updated_at_utc FROM profiles WHERE username=?",
                     (username,)).fetchone()
    if row is None:
        raise ValueError("PROFILE_MISSING")
    return {"username": username, "role": role, "display_name": row[0],
            "email": row[1], "updated_at_utc": row[2],
            "network_mutations_authorized": False}


def read_self(directory, actor):
    """El actor debe proceder de la identidad autenticada, nunca del cuerpo HTTP."""
    with closing(storage._connect(_path(directory), readonly=True)) as db:
        db.execute("BEGIN")
        return _read(db, actor, _identity(db, actor, "profile:read:self"))


def update_self(directory, actor, *, display_name, email):
    """Actualizar exclusivamente el perfil del actor; auditar sin datos personales."""
    name, address = _validated(display_name, email)
    with closing(storage._connect(_path(directory), readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            role = _identity(db, actor, "profile:write:self")
            current = _read(db, actor, role)
            if (current["display_name"], current["email"]) != (name, address):
                stamp = datetime.now(timezone.utc).isoformat()
                db.execute("UPDATE profiles SET display_name=?,email=?,updated_at_utc=? WHERE username=?",
                           (name, address, stamp, actor))
                db.execute(
                    "INSERT INTO audit_events(event_type,observed_at_utc,details_json) VALUES (?,?,?)",
                    ("PROFILE_UPDATED", stamp, json.dumps({"username": actor})))
            result = _read(db, actor, role)
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return result
