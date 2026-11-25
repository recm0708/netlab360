"""Cliente Unix sin sudo: identidad dedicada, selección cerrada y respuesta acotada."""
import json
import os
from pathlib import Path
import pwd
import socket
import stat
import struct
import time

from .job_contract import select
from .probe_broker import MAX_RESPONSE, unique_object

SOCKET = Path("/run/netlab360-s08-broker/control.sock")
ACCOUNT = "netlab360-s08-api"


def check_identity():
    """No conceder acceso al operador interactivo ni a procesos root."""
    uid = pwd.getpwnam(ACCOUNT).pw_uid
    if uid <= 0 or os.geteuid() != uid or os.getuid() != uid:
        raise ValueError("BROKER_CLIENT_IDENTITY")
    parent = SOCKET.parent.lstat()
    target = SOCKET.lstat()
    if (not stat.S_ISDIR(parent.st_mode) or parent.st_uid != 0 or parent.st_mode & 0o022
            or not stat.S_ISSOCK(target.st_mode) or target.st_uid != uid
            or stat.S_IMODE(target.st_mode) != 0o600):
        raise ValueError("BROKER_SOCKET_UNSAFE")


def decode(raw):
    if not raw or len(raw) > MAX_RESPONSE or raw.count(b"\n") != 1 or not raw.endswith(b"\n"):
        raise ValueError("BROKER_RESPONSE_FRAME")
    result = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object)
    if (type(result) is not dict or set(result) != {"schema", "status", "result"}
            or result["schema"] != "NETLAB360_S08_BROKER_V1"
            or result["status"] not in ("OK", "BUSY", "DENIED", "REJECTED", "NOT_ENABLED", "INVALID_RESULT")
            or (result["status"] == "OK" and type(result["result"]) is not dict)
            or (result["status"] != "OK" and result["result"] is not None)):
        raise ValueError("BROKER_RESPONSE_INVALID")
    return result


def request(payload):
    """Solicitar una ejecución sin pasar comandos, rutas de archivos ni identidad libre."""
    selection = select(payload)
    check_identity()
    deadline = time.monotonic() + min(710, selection.deadline_s + 45)
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(3)
        conn.connect(str(SOCKET))
        credentials = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
        if struct.unpack("3i", credentials)[1] != 0:
            raise ValueError("BROKER_SERVER_IDENTITY")
        conn.sendall(json.dumps(selection.parameters(), separators=(",", ":")).encode() + b"\n")
        data = bytearray()
        while len(data) <= MAX_RESPONSE:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("BROKER_RESPONSE_DEADLINE")
            conn.settimeout(remaining)
            chunk = conn.recv(min(8192, MAX_RESPONSE + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
            if b"\n" in data:
                break
        return decode(bytes(data))
