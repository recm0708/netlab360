"""Sesiones opacas con vencimiento absoluto, inactividad y reanudación segura."""
from __future__ import annotations

import base64
from contextlib import closing
import hashlib
import hmac
import re
import secrets
import time

from . import security, storage

TTL = 8 * 3600
IDLE = 300
GRACE = 60
TOKEN = re.compile(r"[A-Za-z0-9_-]{43}\Z")


def digest(token: str | None) -> bytes | None:
    """Aceptar exclusivamente tokens opacos de 256 bits."""
    if not isinstance(token, str) or not TOKEN.fullmatch(token):
        return None
    return hashlib.sha256(token.encode("ascii")).digest()


def csrf_for(token: str) -> str:
    """Derivar un comprobante separado sin persistir secretos recuperables."""
    value = hmac.digest(token.encode("ascii"), b"NETLAB360/session-csrf/v2", "sha256")
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _now(now):
    return int(time.time()) if now is None else now


def _lookup(db, token, now):
    key = digest(token)
    if key is None:
        return None
    row = db.execute(
        "SELECT u.username,u.role,s.csrf_digest,s.created_at,s.expires_at "
        "FROM sessions s JOIN users u ON s.username=u.username "
        "WHERE s.token_digest=? AND u.enabled=1 AND s.created_at<=? AND s.expires_at>?",
        (key, now, now)).fetchone()
    # Los comprobantes aleatorios de la política anterior no son recuperables;
    # se rechazan sin ampliar sus plazos ni modificar las cuentas.
    if (not row or row[1] not in security.ROLES or row[4] > row[3]+TTL
            or not hmac.compare_digest(digest(csrf_for(token)), row[2])):
        return None
    return row


def _identity(row):
    return {"username": row[0], "role": row[1], "network_mutations_authorized": False}


def _snapshot(row, token, now):
    return {**_identity(row), "csrf_token": csrf_for(token), "expires_at": row[4],
            "warning_at": max(row[3], row[4]-GRACE),
            "absolute_expires_at": row[3]+TTL, "server_now": now}


def issue(directory, username: str, *, now: int | None = None) -> dict:
    """Emitir una sesión por cuenta; el plazo inicial incluye el aviso."""
    timestamp = _now(now)
    token = secrets.token_urlsafe(32)
    csrf = csrf_for(token)
    expiry = timestamp+IDLE+GRACE
    with closing(storage._connect(security._path(directory), readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            user = db.execute("SELECT role FROM users WHERE username=? AND enabled=1",
                              (username,)).fetchone()
            if not user or user[0] not in security.ROLES:
                raise ValueError("ACCOUNT_UNAVAILABLE")
            db.execute("DELETE FROM sessions WHERE expires_at<=? OR username=?",
                       (timestamp, username))
            db.execute("INSERT INTO sessions VALUES (?,?,?,?,?)",
                       (digest(token), username, digest(csrf), timestamp, expiry))
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return {"token": token, **_snapshot((username,user[0],digest(csrf),timestamp,expiry),
                                         token,timestamp)}


def resolve(directory, token: str | None, *, csrf: str | None = None,
            require_csrf: bool = False, now: int | None = None) -> dict | None:
    """Validar plazos sin extenderlos por consultas ni sondeos automáticos."""
    timestamp = _now(now)
    with closing(storage._connect(security._path(directory), readonly=True)) as db:
        row = _lookup(db, token, timestamp)
    if not row:
        return None
    if require_csrf:
        candidate = digest(csrf)
        if candidate is None or not hmac.compare_digest(candidate,row[2]):
            return None
    return _identity(row)


def resume(directory, token, *, now=None):
    """Recuperar identidad y CSRF de la cookie vigente, sin renovar actividad."""
    timestamp = _now(now)
    with closing(storage._connect(security._path(directory), readonly=True)) as db:
        row = _lookup(db, token, timestamp)
    return _snapshot(row, token, timestamp) if row else None


def touch(directory, token, csrf, *, confirmed=False, now=None):
    """Actualizar actividad autenticada; durante el aviso exigimos confirmación."""
    timestamp = _now(now)
    with closing(storage._connect(security._path(directory), readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            row = _lookup(db, token, timestamp)
            candidate = digest(csrf)
            if not row or candidate is None or not hmac.compare_digest(candidate,row[2]):
                db.execute("ROLLBACK")
                return None
            if confirmed or timestamp < row[4]-GRACE:
                expiry = min(row[3]+TTL, max(row[4], timestamp+IDLE+GRACE))
                db.execute("UPDATE sessions SET expires_at=? WHERE token_digest=?",
                           (expiry,digest(token)))
                row = (*row[:4],expiry)
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
    return _snapshot(row,token,timestamp)


def revoke(directory, token: str | None, csrf: str | None) -> bool:
    """Revocar una sesión vigente y su comprobante de forma transaccional."""
    with closing(storage._connect(security._path(directory), readonly=False)) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            row = _lookup(db, token, _now(None))
            candidate = digest(csrf)
            if not row or candidate is None or not hmac.compare_digest(candidate,row[2]):
                db.execute("ROLLBACK")
                return False
            result = db.execute("DELETE FROM sessions WHERE token_digest=?",
                                (digest(token),))
            db.execute("COMMIT")
            return result.rowcount == 1
        except BaseException:
            db.execute("ROLLBACK")
            raise
