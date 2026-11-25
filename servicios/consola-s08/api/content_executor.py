"""Supervisar transferencias de contenido sin conceder privilegios a Python."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from .content_worker import BITRATE, PORT, VOLUMES
from .probe_catalog import resolve
from .probe_executor import ENV, invoke, verify_identity
from .transfer_executor import ROUTES, count, manual_lock, number, read_json, server_argv

PROFILES = dict(zip(("content-100mb", "content-500mb", "content-1gb",
                     "content-2gb", "content-5gb"), VOLUMES))


def commands(profile, route, uid, gid):
    """Construir comandos cerrados y abandonar privilegios antes de cargar Python."""
    if profile not in PROFILES or route not in ROUTES or uid <= 0 or gid <= 0:
        raise ValueError("INVALID_CONTENT_SELECTION")
    src, dst, _ = resolve("test.iperf.tcp", route)
    volume = PROFILES[profile]
    worker = str(Path(__file__).with_name("content_worker.py").resolve())
    base = ["/usr/bin/setpriv", "--reuid", str(uid), "--regid", str(gid),
            "--clear-groups", "--no-new-privs", "--bounding-set=-all",
            "--inh-caps=-all", "--ambient-caps=-all", "/usr/bin/python3", "-I", "-B", worker]
    tail = ["--site", dst.address, "--volume", str(volume)]
    deadline = int(volume * 8 / BITRATE * 1.5) + 20
    return src, dst, base + ["--role", "sender"] + tail, base + ["--role", "receiver"] + tail, deadline


def reconcile(profile, route, sender, receiver, uid):
    """Exigir identidades, tamaños exactos y hashes calculados independientemente."""
    _, dst, _ = resolve("test.iperf.tcp", route)
    volume = PROFILES[profile]
    for doc, role in ((sender, "sender"), (receiver, "receiver")):
        if doc["role"] != role or doc["site"] != dst.address or doc["uid"] != uid:
            raise ValueError("CONTENT_IDENTITY_MISMATCH")
        if count(doc["target_bytes"]) != volume or count(doc["bytes"]) != volume:
            raise ValueError("CONTENT_SIZE_MISMATCH")
        if not re.fullmatch(r"[0-9a-f]{64}", doc["sha256"]) or number(doc["duration_s"]) <= 0:
            raise ValueError("CONTENT_METRIC_INVALID")
    match = sender["sha256"] == receiver["sha256"]
    return {"status": "OK" if match else "CONTENT_MISMATCH",
            "target_bytes": volume, "bytes_sent": sender["bytes"], "bytes_received": receiver["bytes"],
            "sender_sha256": sender["sha256"], "receiver_sha256": receiver["sha256"],
            "content_integrity_verified": match, "target_bitrate_bps": BITRATE,
            "sender_duration_s": sender["duration_s"], "receiver_duration_s": receiver["duration_s"],
            "sender_mbps": round(volume * 8 / sender["duration_s"] / 1e6, 3),
            "receiver_mbps": round(volume * 8 / receiver["duration_s"] / 1e6, 3)}


def listener(endpoint):
    reply = invoke(endpoint.namespace, ["/usr/bin/ss", "-H", "-lntu", "sport", "=", f":{PORT}"], 5)
    if reply.returncode:
        raise ValueError("PORT_CHECK_FAILED")
    return reply.stdout.strip()


def execute(profile, route):
    """Acotar duración, supervisar ambos extremos y confirmar liberación de puertos."""
    uid, gid = os.getuid(), os.getgid()
    src, dst, tx, rx, deadline = commands(profile, route, uid, gid)
    result = {"schema": "NETLAB360_S08_CONTENT_V1", "profile": profile, "route": route,
              "origin": src.address, "destination": dst.address,
              "observed_at_utc": datetime.now(timezone.utc).isoformat(),
              "transport": "ERROR", "measurement": None, "error": None}
    try:
        verify_identity(src, dst, invoke)
        if listener(src) or listener(dst):
            raise ValueError("PORT_NOT_FREE")
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            process = subprocess.Popen(server_argv(dst.namespace, rx, deadline + 10),
                                       stdout=out, stderr=err, env=ENV)
            try:
                for _ in range(30):
                    if process.poll() is not None:
                        raise ValueError("RECEIVER_FAILED")
                    if f"{dst.address}:{PORT}" in listener(dst):
                        break
                    time.sleep(0.2)
                else:
                    raise ValueError("RECEIVER_NOT_READY")
                reply = invoke(src.namespace, tx, deadline)
                if reply.returncode in (124, 137):
                    raise subprocess.TimeoutExpired(tx, deadline)
                if reply.returncode:
                    raise ValueError("SENDER_FAILED")
                if process.wait(timeout=deadline + 15):
                    raise ValueError("RECEIVER_FAILED")
                result.update(transport="OK", measurement=reconcile(
                    profile, route, json.loads(reply.stdout), read_json(out), uid))
            finally:
                # El receptor tiene timeout propio incluso si se interrumpe el supervisor.
                process.wait(timeout=deadline + 15)
        if listener(src) or listener(dst):
            raise ValueError("PORT_NOT_RELEASED")
    except subprocess.TimeoutExpired:
        result.update(transport="TIMEOUT", measurement=None, error="CONTENT_TIMEOUT")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        code = str(exc)
        result.update(transport="ERROR", measurement=None,
                      error=code if re.fullmatch(r"[A-Z_]+", code) else "INVALID_CONTENT_OUTPUT")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(PROFILES), required=True)
    parser.add_argument("--route", choices=ROUTES, required=True)
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error("ROOT_FORBIDDEN")
    with manual_lock():
        result = execute(args.profile, args.route)
        print(json.dumps(result, allow_nan=False))
    return 0 if result["transport"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
