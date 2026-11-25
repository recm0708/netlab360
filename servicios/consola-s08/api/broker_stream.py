"""Canal de progreso y cancelación de contenido; conserva el protocolo V1."""
import json
import os
import select as io_select
import time
from datetime import datetime, timezone

from . import broker_transfer as T, content_executor as C
from .probe_executor import verify_identity
from .stream_protocol import MAX_EVENTS, MAX_FRAME, sample


class CancelRequested(Exception):
    """Terminación cooperativa de la transferencia de esta conexión."""


def frame(conn, value):
    raw = (json.dumps(value, allow_nan=False, separators=(",", ":")) + "\n").encode()
    if len(raw) > MAX_FRAME:
        raise ValueError("STREAM_FRAME_LIMIT")
    conn.settimeout(3)
    conn.sendall(raw)


def final(status, result=None, cleanup=False):
    return {"kind": "final", "status": status, "result": result, "cleanup_verified": cleanup}


class Control:
    """Solo acepta CANCEL en el mismo canal que inició el trabajo."""
    def __init__(self, conn):
        self.conn = conn
        self.buffer = bytearray()

    def check(self):
        if io_select.select([self.conn], [], [], 0)[0]:
            data = self.conn.recv(32)
            if not data:
                raise CancelRequested()
            self.buffer.extend(data)
            if self.buffer == b"CANCEL\n":
                raise CancelRequested()
            if not b"CANCEL\n".startswith(self.buffer):
                raise CancelRequested()


class Progress:
    """Leer únicamente líneas completas del stderr privado de cada worker."""
    def __init__(self, role, profile, emit):
        self.role, self.profile, self.emit = role, profile, emit
        self.offset = 0
        self.pending = b""
        self.previous = None
        self.count = 0

    def poll(self, handle):
        chunk = os.pread(handle.fileno(), 65536, self.offset)
        self.offset += len(chunk)
        self.pending += chunk
        lines = self.pending.split(b"\n")
        self.pending = lines.pop()
        if self.offset > 65536 or len(self.pending) > 4096:
            raise ValueError("PROGRESS_OUTPUT_LIMIT")
        for line in lines:
            if not line.startswith(b"NL360_PROGRESS "):
                continue
            raw = json.loads(line[len(b"NL360_PROGRESS "):])
            measured = sample(raw, self.profile, self.previous)
            if measured["role"] != self.role or self.count >= MAX_EVENTS // 2:
                raise ValueError("PROGRESS_IDENTITY_OR_LIMIT")
            self.previous = measured
            self.count += 1
            self.emit(raw)


def run(conn, selection, uid, gid):
    """Supervisar ambos workers, comprobar liberación antes de confirmar cancelación."""
    if selection.action != "test.content.tcp":
        return final("NOT_ENABLED")
    src, dst, server, client, ct, st, port = T.plan(selection, uid, gid)
    control = Control(conn)
    started = time.monotonic()
    stamp = datetime.now(timezone.utc).isoformat()
    def emit(raw):
        frame(conn, {"kind": "progress", "sample": raw})
    tx = Progress("sender", selection.profile, emit)
    rx = Progress("receiver", selection.profile, emit)
    cancelled = False
    try:
        verify_identity(src, dst, T.invoke)
        verify_identity(dst, src, T.invoke)
        if T.listener(src, port) or T.listener(dst, port):
            return final("UNCERTAIN")
        try:
            control.check()
            with T.managed(dst.namespace, server + ["--progress"], st) as (receiver, out_rx, err_rx):
                for _ in range(30):
                    control.check()
                    if receiver.poll() is not None:
                        raise ValueError("RECEIVER_FAILED")
                    if f"{dst.address}:{port}" in T.listener(dst, port):
                        break
                    time.sleep(0.2)
                else:
                    raise ValueError("RECEIVER_NOT_READY")
                control.check()
                with T.managed(src.namespace, client + ["--progress"], ct) as (sender, out_tx, err_tx):
                    deadline = time.monotonic() + ct + 5
                    while sender.poll() is None or receiver.poll() is None:
                        control.check()
                        tx.poll(err_tx)
                        rx.poll(err_rx)
                        if time.monotonic() >= deadline:
                            raise TimeoutError("TRANSFER_DEADLINE")
                        if sender.poll() not in (None, 0) or receiver.poll() not in (None, 0):
                            raise ValueError("WORKER_FAILED")
                        time.sleep(0.15)
                    control.check()
                    tx.poll(err_tx)
                    rx.poll(err_rx)
                    if sender.returncode or receiver.returncode:
                        raise ValueError("WORKER_FAILED")
                    measurement = C.reconcile(selection.profile, selection.route,
                        json.loads(T.read_output(out_tx)), json.loads(T.read_output(out_rx)), uid)
        except CancelRequested:
            cancelled = True
        finally:
            if T.listener(src, port) or T.listener(dst, port):
                raise ValueError("PORT_NOT_RELEASED")
        if cancelled:
            return final("CANCELLED", cleanup=True)
        return final("OK", {"schema": "NETLAB360_S08_CONTENT_V1", "profile": selection.profile,
                     "route": selection.route, "origin": src.address, "destination": dst.address,
                     "observed_at_utc": stamp, "transport": "OK", "measurement": measurement,
                     "error": None, "elapsed_ms": round((time.monotonic() - started) * 1000, 3)}, True)
    except (ValueError, OSError, KeyError, TypeError, TimeoutError):
        return final("UNCERTAIN")
