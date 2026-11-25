"""Frontera Unix del broker S08; solo diagnósticos cortos en esta revisión."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import stat
import struct
import subprocess

from . import probe_executor
from .job_contract import select

MAX_REQUEST = 4096
MAX_RESPONSE = 262144
LOCK_PATH = Path("/run/netlab360-s08-broker/active.lock")


def unique_object(pairs):
    """Rechazar claves repetidas, incluso si tienen el mismo valor."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_KEY")
        result[key] = value
    return result


def decode_request(raw):
    """Aceptar una solicitud de una línea, sin comandos ni parámetros libres."""
    if not raw or len(raw) > MAX_REQUEST or not raw.endswith(b"\n") or raw.count(b"\n") != 1:
        raise ValueError("INVALID_FRAME")
    try:
        return select(json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object))
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ValueError("INVALID_SELECTION") from None


def read_request(conn):
    """Limitar bytes y tiempo de lectura; no procesar una segunda solicitud."""
    conn.settimeout(3)
    data = bytearray()
    while len(data) <= MAX_REQUEST:
        block = conn.recv(min(1024, MAX_REQUEST + 1 - len(data)))
        if not block:
            break
        data.extend(block)
        if b"\n" in data:
            break
    return decode_request(bytes(data))


def peer_uid(conn):
    """Obtener identidad del kernel, nunca de un campo proporcionado por el cliente."""
    if conn.family != socket.AF_UNIX:
        raise ValueError("UNIX_SOCKET_REQUIRED")
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    _, uid, _ = struct.unpack("3i", raw)
    return uid


@contextmanager
def global_lock(path=LOCK_PATH):
    """Serializar instancias del broker mediante un archivo no editable por clientes."""
    parent = path.parent
    info = parent.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o022:
        raise ValueError("UNSAFE_LOCK_DIRECTORY")
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, "rb+") as lock:
        info = os.fstat(lock.fileno())
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid()
                or stat.S_IMODE(info.st_mode) != 0o600 or info.st_nlink != 1):
            raise ValueError("UNSAFE_LOCK_FILE")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def root_runner(namespace, args, seconds):
    """Invocar únicamente los argv construidos internamente por probe_executor."""
    argv = ["/usr/sbin/ip", "netns", "exec", namespace, "/usr/bin/env", "-i",
            "PATH=/usr/sbin:/usr/bin", "LC_ALL=C", "/usr/bin/timeout",
            "--foreground", "--kill-after=1", str(seconds), *args]
    with subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, env=probe_executor.ENV,
                          start_new_session=True) as process:
        try:
            out, err = process.communicate(timeout=seconds + 5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.communicate()
            raise
    if len(out) + len(err) > probe_executor.LIMIT:
        raise ValueError("OUTPUT_LIMIT")
    return subprocess.CompletedProcess(argv, process.returncode,
                                       out.decode("utf-8", "replace"), err.decode("utf-8", "replace"))


def run_probe(selection):
    return probe_executor.execute(selection.action, selection.route, runner=root_runner)


def response(status, result=None):
    return {"schema": "NETLAB360_S08_BROKER_V1", "status": status, "result": result}


def handle(conn, allowed_uid, lock_factory=global_lock, executor=run_probe):
    """Autorizar al par y reservar la plaza antes de llamar al ejecutor."""
    try:
        if type(allowed_uid) is not int or allowed_uid <= 0 or peer_uid(conn) != allowed_uid:
            return response("DENIED")
        selection = read_request(conn)
        if selection.action not in probe_executor.ACTIONS:
            return response("NOT_ENABLED")
        with lock_factory():
            result = executor(selection)
            if (type(result) is not dict or result.get("schema") != "NETLAB360_S08_PROBE_V1"
                    or result.get("action") != selection.action or result.get("route") != selection.route
                    or result.get("transport") not in ("OK", "ERROR", "TIMEOUT")):
                return response("INVALID_RESULT")
            return response("OK", result)
    except BlockingIOError:
        return response("BUSY")
    except (ValueError, OSError, TimeoutError):
        return response("REJECTED")


def serve(conn, allowed_uid):
    """Una conexión, una respuesta acotada; sin acceso a SQLite ni shell."""
    result = handle(conn, allowed_uid)
    raw = (json.dumps(result, allow_nan=False, ensure_ascii=True) + "\n").encode()
    if len(raw) > MAX_RESPONSE:
        raw = (json.dumps(response("INVALID_RESULT")) + "\n").encode()
    conn.settimeout(3)
    conn.sendall(raw)
