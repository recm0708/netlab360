"""Sesiones opacas S08: persistencia de verificadores, expiración y revocación."""
from __future__ import annotations

from contextlib import closing
import hashlib
import hmac
import re
import secrets
import time

from . import security, storage

TTL = 1800
TOKEN = re.compile(r"[A-Za-z0-9_-]{43}\Z")


def digest(token: str | None) -> bytes | None:
    """Aceptar únicamente tokens opacos de 256 bits codificados sin relleno."""
    if not isinstance(token, str) or not TOKEN.fullmatch(token):
        return None
    return hashlib.sha256(token.encode("ascii")).digest()


def issue(directory, username: str, *, now: int | None = None) -> dict:
    """Emitir una sesión por cuenta activa, revocando la sesión previa."""
    timestamp = int(time.time()) if now is None else now
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
    path = security._path(directory)
    with closing(storage._connect(path, readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            row = db.execute("SELECT role FROM users WHERE username=? AND enabled=1",
                             (username,)).fetchone()
            if not row or row[0] not in security.ROLES:
                raise ValueError("ACCOUNT_UNAVAILABLE")
            db.execute("DELETE FROM sessions WHERE expires_at<=? OR username=?",
                       (timestamp, username))
            db.execute("INSERT INTO sessions VALUES (?,?,?,?,?)",
                       (digest(token), username, digest(csrf), timestamp, timestamp+TTL))
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return {"token": token, "csrf_token": csrf, "expires_at": timestamp+TTL,
            "username": username, "role": row[0], "network_mutations_authorized": False}


def resolve(directory, token: str | None, *, csrf: str | None = None,
            require_csrf: bool = False, now: int | None = None) -> dict | None:
    """Consultar identidad vigente y validar CSRF cuando corresponde."""
    key = digest(token)
    if key is None:
        return None
    timestamp = int(time.time()) if now is None else now
    with closing(storage._connect(security._path(directory), readonly=True)) as db:
        row = db.execute(
            "SELECT u.username,u.role,s.csrf_digest FROM sessions s JOIN users u "
            "ON s.username=u.username WHERE s.token_digest=? AND u.enabled=1 "
            "AND s.created_at<=? AND s.expires_at>?", (key,timestamp,timestamp)).fetchone()
    if not row or row[1] not in security.ROLES:
        return None
    if require_csrf:
        candidate = digest(csrf)
        if candidate is None or not hmac.compare_digest(candidate,row[2]):
            return None
    return {"username":row[0],"role":row[1],"network_mutations_authorized":False}


def revoke(directory, token: str | None, csrf: str | None) -> bool:
    """Revocar únicamente una sesión vigente con su comprobante CSRF."""
    if resolve(directory,token,csrf=csrf,require_csrf=True) is None:
        return False
    with closing(storage._connect(security._path(directory), readonly=False)) as db:
        result = db.execute("DELETE FROM sessions WHERE token_digest=? AND csrf_digest=?",
                            (digest(token),digest(csrf)))
        return result.rowcount == 1
