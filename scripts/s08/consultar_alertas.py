#!/usr/bin/env python3
"""Canal Unix de lectura delimitada del registro privado de Alertmanager."""
import json
import os
from pathlib import Path
import pwd
import runpy
import socket
import struct
import time

ROOT = Path(__file__).resolve().parent
DATABASE = Path("/var/lib/netlab360/s08-alertas/notificaciones.sqlite3")
MAX_RESPONSE = 2 * 1024 * 1024
SCOPES = {b"operational\n": "operational", b"validation\n": "validation"}


def serve(conn, uid, inspect):
    """Autorizar el proceso cliente, nunca una identidad declarada por el mensaje."""
    conn.settimeout(3)
    credentials = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    if uid <= 0 or struct.unpack("3i", credentials)[1] != uid:
        return
    deadline = time.monotonic() + 3
    raw = bytearray()
    while len(raw) <= 16:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        conn.settimeout(remaining)
        chunk = conn.recv(17 - len(raw))
        if not chunk:
            break
        raw.extend(chunk)
    scope = SCOPES.get(bytes(raw))
    if scope is None:
        return
    try:
        result = inspect(DATABASE, scope)
        frame = json.dumps({"schema": "NETLAB360_S08_NOTIFICATIONS_V1",
                            "status": "OK", "result": result},
                           ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode() + b"\n"
        if len(frame) > MAX_RESPONSE:
            raise ValueError("RESPONSE_LIMIT")
    except Exception:
        frame = b'{"schema":"NETLAB360_S08_NOTIFICATIONS_V1","status":"UNAVAILABLE","result":null}\n'
    conn.settimeout(3)
    conn.sendall(frame)


def main():
    account = pwd.getpwnam("netlab360-s08-alerts")
    if account.pw_uid <= 0 or os.geteuid() != account.pw_uid:
        raise ValueError("NOTIFICATION_SERVER_IDENTITY")
    inspect = runpy.run_path(str(ROOT / "recibir_alertas.py"))["inspect"]
    with socket.socket(fileno=0) as conn:
        serve(conn, pwd.getpwnam("netlab360-s08-api").pw_uid, inspect)


if __name__ == "__main__":
    main()
