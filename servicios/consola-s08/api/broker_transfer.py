"""Supervisión protegida de transferencias con procesos propios y perfiles cerrados."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
import signal
import subprocess
import tempfile
import time

from . import content_executor as content, transfer_executor as perf
from .probe_executor import ENV, verify_identity


def drop(uid, gid):
    """Eliminar capacidades y grupos antes de ejecutar el proceso de datos."""
    if type(uid) is not int or type(gid) is not int or min(uid, gid) <= 0:
        raise ValueError("INVALID_WORKER_IDENTITY")
    return ["/usr/bin/setpriv", "--reuid", str(uid), "--regid", str(gid),
            "--clear-groups", "--no-new-privs", "--bounding-set=-all",
            "--inh-caps=-all", "--ambient-caps=-all"]


def argv(namespace, args, seconds):
    return ["/usr/sbin/ip", "netns", "exec", namespace, "/usr/bin/env", "-i",
            "PATH=/usr/sbin:/usr/bin", "LC_ALL=C", "/usr/bin/timeout",
            "--foreground", "--kill-after=2", str(seconds), *args]


@contextmanager
def managed(namespace, args, seconds):
    """Conservar archivos de salida pequeños y terminar solo nuestro grupo."""
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        process = subprocess.Popen(argv(namespace, args, seconds),
                                   stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                   env=ENV, start_new_session=True)
        try:
            yield process, out, err
        finally:
            if process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.wait(timeout=5)


def read_output(handle):
    handle.seek(0)
    data = handle.read(perf.MAX_JSON + 1)
    if len(data) > perf.MAX_JSON:
        raise ValueError("TRANSFER_OUTPUT_LIMIT")
    return data.decode("utf-8", "strict")


def invoke(namespace, args, seconds):
    """Limitar captura en memoria; el servicio acota también archivos de salida."""
    with managed(namespace, args, seconds) as (process, out, err):
        rc = process.wait(timeout=seconds + 5)
        return subprocess.CompletedProcess(args, rc, read_output(out), read_output(err))


def plan(selection, uid, gid):
    """Derivar ambos procesos del catálogo, sin aceptar argv desde el cliente."""
    prefix = drop(uid, gid)
    if selection.action == "test.content.tcp":
        src, dst, client, server, timeout = content.commands(selection.profile, selection.route, uid, gid)
        return src, dst, server, client, timeout, timeout + 10, content.PORT
    src, dst, server, client, ct, st = perf.commands(selection.profile, selection.route)
    if selection.action != "test.iperf." + perf.PROFILES[selection.profile][0].lower():
        raise ValueError("PROFILE_PROTOCOL_MISMATCH")
    return src, dst, prefix + server, prefix + client, ct, st, perf.IPERF_PORT


def listener(endpoint, port):
    reply = invoke(endpoint.namespace, ["/usr/bin/ss", "-H", "-lntu",
                                       "sport", "=", f":{port}"], 5)
    if reply.returncode:
        raise ValueError("PORT_CHECK_FAILED")
    return reply.stdout.strip()


def execute(selection, uid, gid):
    """Ejecutar una transferencia y devolver la medición solo después de limpiar."""
    src, dst, server, client, ct, st, port = plan(selection, uid, gid)
    is_content = selection.action == "test.content.tcp"
    result = {"schema": "NETLAB360_S08_CONTENT_V1" if is_content else "NETLAB360_S08_TRANSFER_V1",
              "profile": selection.profile, "route": selection.route,
              "origin": src.address, "destination": dst.address,
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "transport": "ERROR", "measurement": None, "error": None}
    started = time.monotonic()
    try:
        verify_identity(src, dst, invoke)
        verify_identity(dst, src, invoke)
        if listener(src, port) or listener(dst, port):
            raise ValueError("PORT_NOT_FREE")
        try:
            with managed(dst.namespace, server, st) as (receiver, out, _):
                for _ in range(30):
                    if receiver.poll() is not None:
                        raise ValueError("RECEIVER_FAILED")
                    if f"{dst.address}:{port}" in listener(dst, port):
                        break
                    time.sleep(0.2)
                else:
                    raise ValueError("RECEIVER_NOT_READY")
                reply = invoke(src.namespace, client, ct)
                if reply.returncode in (124, 137):
                    raise subprocess.TimeoutExpired(client, ct)
                if reply.returncode:
                    raise ValueError("SENDER_FAILED")
                if receiver.wait(timeout=max(5, st - (time.monotonic() - started) + 15)):
                    raise ValueError("RECEIVER_FAILED")
                tx, rx = json.loads(reply.stdout), json.loads(read_output(out))
                measurement = (content.reconcile(selection.profile, selection.route, tx, rx, uid)
                               if is_content else perf.parse_results(selection.profile, selection.route, tx, rx))
        finally:
            if listener(src, port) or listener(dst, port):
                raise ValueError("PORT_NOT_RELEASED")
        result.update(transport="OK", measurement=measurement)
    except subprocess.TimeoutExpired:
        result.update(transport="TIMEOUT", error="TRANSFER_TIMEOUT")
    except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
        code = str(exc)
        result["error"] = code if code.isupper() and code.replace("_", "").isalnum() else "INVALID_TRANSFER_OUTPUT"
    result["elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
    return result
