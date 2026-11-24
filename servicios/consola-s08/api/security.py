"""Identidades locales S08; derivación scrypt y roles sin autoridad de red."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import getpass
import hashlib
import hmac
import re
import secrets
import sys
import warnings

from . import storage

ROLES = frozenset({"VIEWER", "OPERATOR"})
USERNAME = re.compile(r"[a-z][a-z0-9_-]{2,31}\Z")
# Parámetros fijos de scrypt; cada derivación usa aproximadamente 128 MiB.
N, R, P = 2**17, 8, 1
MAXMEM = 256 * 1024 * 1024


def validate_username(username: str) -> None:
    """Restringir identificadores locales sin aceptar rutas o espacios."""
    if not isinstance(username, str) or not USERNAME.fullmatch(username):
        raise ValueError("INVALID_USERNAME")


def _password_bytes(password: str, *, enrollment: bool) -> bytes:
    if not isinstance(password, str):
        raise ValueError("INVALID_PASSWORD")
    data = password.encode("utf-8")
    if not 1 <= len(data) <= 256 or (enrollment and len(password) < 15):
        raise ValueError("INVALID_PASSWORD")
    return data


def derive(password: str, salt: bytes, *, enrollment: bool = False) -> bytes:
    """Derivar un verificador sin guardar ni registrar la contraseña."""
    if not isinstance(salt, bytes) or len(salt) != 16:
        raise ValueError("INVALID_SALT")
    return hashlib.scrypt(_password_bytes(password, enrollment=enrollment),
                          salt=salt, n=N, r=R, p=P, maxmem=MAXMEM, dklen=32)


def _path(directory):
    path = storage._directory(directory, create=False)
    with closing(storage._connect(path, readonly=True)) as db:
        if (db.execute("PRAGMA application_id").fetchone()[0] != storage.APPLICATION_ID
                or db.execute("PRAGMA user_version").fetchone()[0] not in (2, 3)):
            raise ValueError("SECURITY_SCHEMA_REQUIRED")
    return path


def create_user(directory, username: str, password: str, role: str) -> dict:
    """Alta local explícita; no sobrescribir cuentas existentes ni elevar roles."""
    validate_username(username)
    if not isinstance(role, str) or role not in ROLES:
        raise ValueError("INVALID_ROLE")
    path = _path(directory)
    salt = secrets.token_bytes(16)
    digest = derive(password, salt, enrollment=True)
    stamp = datetime.now(timezone.utc).isoformat()
    with closing(storage._connect(path, readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            if db.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
                raise ValueError("USER_EXISTS")
            db.execute(
                "INSERT INTO users(username,role,password_salt,password_digest,created_at_utc) VALUES (?,?,?,?,?)",
                (username, role, salt, digest, stamp))
            # El evento contiene únicamente el identificador y el rol, nunca secretos.
            import json
            db.execute(
                "INSERT INTO audit_events(event_type,observed_at_utc,details_json) VALUES (?,?,?)",
                ("USER_CREATED", stamp, json.dumps({"username": username, "role": role})))
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return {"username": username, "role": role, "network_mutations_authorized": False}


def authenticate(directory, username: str, password: str) -> dict | None:
    """Verificar credenciales; devolver identidad limitada o ninguna."""
    try:
        validate_username(username)
        _password_bytes(password, enrollment=False)
    except (ValueError, UnicodeError):
        return None
    path = _path(directory)
    with closing(storage._connect(path, readonly=True)) as db:
        row = db.execute(
            "SELECT role,password_salt,password_digest,enabled FROM users WHERE username=?",
            (username,)).fetchone()
    # Ejecutar una derivación incluso si la cuenta válida sintácticamente no existe.
    salt, expected = (row[1], row[2]) if row else (b"\x00"*16, b"\x00"*32)
    matches = hmac.compare_digest(derive(password, salt), expected)
    if not row or not matches or row[3] != 1 or row[0] not in ROLES:
        return None
    return {"username": username, "role": row[0], "network_mutations_authorized": False}


def main() -> None:
    """Administración local por terminal; la contraseña se lee sin eco."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("create-user",))
    parser.add_argument("username")
    parser.add_argument("role", choices=sorted(ROLES))
    args = parser.parse_args()
    if not sys.stdin.isatty():
        raise SystemExit("INTERACTIVE_TERMINAL_REQUIRED")
    warnings.simplefilter("error", getpass.GetPassWarning)
    password = getpass.getpass("Contraseña local: ")
    confirm = getpass.getpass("Confirmar contraseña: ")
    if password != confirm:
        raise SystemExit("PASSWORD_MISMATCH")
    result = create_user(storage.default_dir(), args.username, password, args.role)
    print("USUARIO_CREADO=" + result["username"] + " ROL=" + result["role"])


if __name__ == "__main__":
    main()
