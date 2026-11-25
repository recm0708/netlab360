#!/usr/bin/env python3
"""Recepción de notificaciones Alertmanager con registro idempotente y alcance cerrado."""
import argparse
import base64
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import re
import sqlite3

MAX_BODY = 131072
S04 = {"NETLAB360S04ExporterUnavailable", "NETLAB360S04CollectorUnknown",
       "NETLAB360S04WANAdminDown", "NETLAB360S04VLANAdminDown"}
S08 = {"NETLAB360S08ProbeFailed", "NETLAB360S08ProbeAcquisitionFailed",
       "NETLAB360S08ProbeMetricMissing"}
PROBES = {"hq-s1-icmp", "hq-s2-icmp", "s2-hq-icmp", "s2-hq-tcp", "s2-hq-http"}


def utc(value):
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("INVALID_TIMESTAMP")
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("INVALID_TIMESTAMP")
    return stamp.astimezone(timezone.utc).isoformat(timespec="microseconds")


def normalize(payload):
    """Validar todos los eventos antes de abrir una transacción."""
    if (not isinstance(payload, dict) or payload.get("receiver") != "netlab360-local"
            or payload.get("version") != "4" or payload.get("truncatedAlerts") != 0
            or payload.get("status") not in ("firing", "resolved")):
        raise ValueError("INVALID_NOTIFICATION")
    alerts = payload.get("alerts")
    if not isinstance(alerts, list) or not 1 <= len(alerts) <= 64:
        raise ValueError("INVALID_ALERT_COUNT")
    records = []
    for item in alerts:
        if not isinstance(item, dict):
            raise ValueError("INVALID_ALERT")
        labels = item["labels"]
        if not isinstance(labels, dict) or len(labels) > 24 or not all(
                isinstance(k, str) and 0 < len(k) <= 64 and isinstance(v, str)
                and 0 < len(v) <= 256 and all(ord(c) >= 32 for c in v)
                for k, v in labels.items()):
            raise ValueError("INVALID_LABELS")
        name, phase = labels.get("alertname"), labels.get("phase")
        scope = "operational"
        if name in S04 and phase == "s04" and "synthetic" not in labels:
            pass
        elif (name in S08 and phase == "s08" and labels.get("probe_id") in PROBES
              and labels.get("laboratory") == "netlab360-lab" and "synthetic" not in labels):
            pass
        elif (name == "NETLAB360S08Validation" and phase == "validation"
              and labels.get("synthetic") == "true"
              and re.fullmatch("[0-9a-f]{16}", labels.get("run_id", ""))):
            scope = "validation"
        else:
            raise ValueError("UNKNOWN_ALERT_SCOPE")
        state = item["status"]
        if state not in ("firing", "resolved"):
            raise ValueError("INVALID_ALERT_STATUS")
        start = utc(item["startsAt"])
        end = utc(item["endsAt"]) if state == "resolved" else None
        if end is not None and end < start:
            raise ValueError("INVALID_ALERT_ORDER")
        canonical = json.dumps(labels, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
        records.append((scope, fingerprint, start, state, end, name, canonical))
    return records


def initialize(path):
    if path.is_symlink() or not path.parent.is_dir() or path.parent.is_symlink():
        raise ValueError("INVALID_HISTORY_PATH")
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.execute("PRAGMA journal_mode=WAL")
        with db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY,
                    scope TEXT NOT NULL CHECK(scope IN ('operational','validation')),
                    fingerprint TEXT NOT NULL,
                    starts_at_utc TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('firing','resolved')),
                    ends_at_utc TEXT,
                    alertname TEXT NOT NULL,
                    labels_json TEXT NOT NULL,
                    received_at_utc TEXT NOT NULL,
                    UNIQUE(scope,fingerprint,starts_at_utc,status)
                )
            """)
    path.chmod(0o600)


def record(path, payload):
    rows = normalize(payload)
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    with closing(sqlite3.connect(path, timeout=5)) as db:
        with db:
            before = db.total_changes
            db.executemany("""
                INSERT INTO notifications(scope,fingerprint,starts_at_utc,status,
                    ends_at_utc,alertname,labels_json,received_at_utc)
                VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(scope,fingerprint,starts_at_utc,status) DO NOTHING
            """, [(*row, now) for row in rows])
            return db.total_changes - before


def inspect(path, scope):
    if scope not in ("operational", "validation"):
        raise ValueError("INVALID_SCOPE")
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=5)) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("HISTORY_INTEGRITY")
        total = db.execute("SELECT count(*) FROM notifications WHERE scope=?", (scope,)).fetchone()[0]
        rows = [dict(row) for row in db.execute(
            "SELECT * FROM notifications WHERE scope=? ORDER BY id DESC LIMIT 200", (scope,))]
        return {"source": "alertmanager_webhook", "scope": scope, "total": total, "records": rows}


class Receiver(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, *_):
        # No registrar cabeceras de autenticación ni cuerpos.
        pass

    def do_GET(self):
        if self.path != "/healthz":
            self.send_error(404)
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK\n")

    def do_POST(self):
        if self.path != "/receive":
            self.send_error(404)
            return
        if not hmac.compare_digest(self.headers.get("Authorization", "").encode(),
                                   self.server.authorization):
            self.send_error(401)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY or self.headers.get("Transfer-Encoding"):
                raise ValueError("BODY_LENGTH")
            raw = self.rfile.read(size)
            if len(raw) != size:
                raise ValueError("BODY_TRUNCATED")
            record(self.server.database, json.loads(raw))
        except (ValueError, TypeError, KeyError, UnicodeError):
            self.send_error(400)
            return
        except (sqlite3.Error, OSError):
            self.send_error(503)
            return
        self.send_response(200)
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("serve", "operational", "validation"))
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--secret", type=Path)
    args = parser.parse_args()
    if args.mode != "serve":
        print(json.dumps(inspect(args.database, args.mode), ensure_ascii=False))
        return
    initialize(args.database)
    secret = args.secret.read_text().strip()
    if not re.fullmatch("[A-Za-z0-9_-]{32,128}", secret):
        raise ValueError("INVALID_WEBHOOK_SECRET")
    with HTTPServer(("127.0.0.1", 9193), Receiver) as server:
        server.database = args.database
        server.authorization = b"Basic " + base64.b64encode(("webhook:" + secret).encode())
        server.serve_forever()


if __name__ == "__main__":
    main()
