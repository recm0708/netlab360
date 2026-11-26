"""Cliente de lectura de notificaciones; sin acceso al SQLite ni credenciales AM."""
import hashlib
import json
import os
from pathlib import Path
import pwd
import socket
import stat
import struct
import time

from . import readers, alerts_reader, slo_contract

SOCKET = Path("/run/netlab360-s08-alert-read/control.sock")
MAX_RESPONSE = 2 * 1024 * 1024
SCOPES = ("operational", "validation")
S08 = {"NETLAB360S08ProbeFailed", "NETLAB360S08ProbeAcquisitionFailed", "NETLAB360S08ProbeMetricMissing"}


def identity():
    uid = pwd.getpwnam("netlab360-s08-api").pw_uid
    if uid <= 0 or os.getuid() != uid or os.geteuid() != uid:
        raise ValueError("NOTIFICATION_CLIENT_IDENTITY")
    parent, target = SOCKET.parent.lstat(), SOCKET.lstat()
    if (not stat.S_ISDIR(parent.st_mode) or parent.st_uid != 0 or parent.st_mode & 0o022
            or not stat.S_ISSOCK(target.st_mode) or target.st_uid != uid
            or stat.S_IMODE(target.st_mode) != 0o600):
        raise ValueError("NOTIFICATION_SOCKET_IDENTITY")


def project(raw, scope):
    frame = readers.decode(raw, MAX_RESPONSE)
    if (set(frame) != {"schema", "status", "result"}
            or frame["schema"] != "NETLAB360_S08_NOTIFICATIONS_V1"):
        raise ValueError("NOTIFICATION_FRAME")
    if frame["status"] == "UNAVAILABLE" and frame["result"] is None:
        raise OSError("NOTIFICATION_SOURCE_UNAVAILABLE")
    if frame["status"] != "OK":
        raise ValueError("NOTIFICATION_STATUS")
    result = frame["result"]
    if (result["source"] != "alertmanager_webhook" or result["scope"] != scope
            or type(result["total"]) is not int or result["total"] < 0
            or not isinstance(result["records"], list)
            or len(result["records"]) != min(result["total"], 200)):
        raise ValueError("NOTIFICATION_RESULT")
    rows = []
    for row in result["records"]:
        if (type(row["id"]) is not int or row["id"] <= 0 or row["scope"] != scope
                or row["status"] not in ("firing", "resolved")):
            raise ValueError("NOTIFICATION_ROW")
        labels = readers.decode(row["labels_json"].encode(), 32768)
        canonical = json.dumps(labels, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if hashlib.sha256(canonical.encode()).hexdigest() != row["fingerprint"]:
            raise ValueError("NOTIFICATION_FINGERPRINT")
        name = row["alertname"]
        if labels.get("alertname") != name:
            raise ValueError("NOTIFICATION_NAME")
        if scope == "operational":
            if "synthetic" in labels or not (
                name in alerts_reader.RULES and labels.get("phase") == "s04"
                or name in S08 and labels.get("phase") == "s08"
                and labels.get("probe_id") in slo_contract.PROBES
                and labels.get("laboratory") == "netlab360-lab"
            ):
                raise ValueError("NOTIFICATION_SCOPE")
        elif (name != "NETLAB360S08Validation" or labels.get("phase") != "validation"
              or labels.get("synthetic") != "true"):
            raise ValueError("NOTIFICATION_SCOPE")
        start = alerts_reader.timestamp(row["starts_at_utc"])
        end = alerts_reader.timestamp(row["ends_at_utc"], optional=True)
        received = alerts_reader.timestamp(row["received_at_utc"])
        if ((row["status"] == "resolved") != (end is not None)
                or end is not None and end < start):
            raise ValueError("NOTIFICATION_ORDER")
        rows.append({"id": row["id"], "scope": scope, "fingerprint": row["fingerprint"],
                     "alertname": name, "status": row["status"], "starts_at_utc": start,
                     "ends_at_utc": end, "received_at_utc": received, "labels": labels})
    ids = [row["id"] for row in rows]
    if ids != sorted(set(ids), reverse=True):
        raise ValueError("NOTIFICATION_IDS")
    return {"total": result["total"], "records": rows, "truncated": result["total"] > len(rows)}


def collect(scope):
    if scope not in SCOPES:
        raise ValueError("INVALID_NOTIFICATION_SCOPE")
    result = {"source": "ALERTMANAGER_WEBHOOK", "scope": scope,
              "transport": "UNKNOWN", "total": None, "records": [], "truncated": False}
    try:
        identity()
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
            conn.settimeout(3)
            conn.connect(str(SOCKET))
            credentials = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
            if struct.unpack("3i", credentials)[1] != 0:
                raise ValueError("NOTIFICATION_SERVER_IDENTITY")
            conn.sendall(scope.encode() + b"\n")
            conn.shutdown(socket.SHUT_WR)
            deadline = time.monotonic() + 12
            raw = bytearray()
            while len(raw) <= MAX_RESPONSE:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("NOTIFICATION_DEADLINE")
                conn.settimeout(remaining)
                chunk = conn.recv(min(65536, MAX_RESPONSE + 1 - len(raw)))
                if not chunk:
                    break
                raw.extend(chunk)
            if len(raw) > MAX_RESPONSE or raw.count(b"\n") != 1 or not raw.endswith(b"\n"):
                raise ValueError("NOTIFICATION_RESPONSE_FRAME")
            result.update(project(bytes(raw), scope), transport="OK")
    except (OSError, KeyError) as error:
        result["transport"] = "INVALID" if isinstance(error, KeyError) else "UNAVAILABLE"
    except (ValueError, TypeError, AttributeError, OverflowError, RecursionError):
        result["transport"] = "INVALID"
    result["queried_at_utc"] = readers.now_utc()
    return result
