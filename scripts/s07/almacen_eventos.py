"""Persistencia histórica S07: SQLite, sin adquisición ni acciones de red."""
from __future__ import annotations

from collections import Counter
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from contrato_eventos import make_event, utc

VERSION = 1
BATCH_SCHEMA = "NETLAB360_S07_EVENT_BATCH_V1"
MAX_EVENTS = 10000
DDL = """
CREATE TABLE IF NOT EXISTS events (
    sequence INTEGER PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    stream TEXT NOT NULL,
    source TEXT NOT NULL,
    subject TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    observed_utc TEXT,
    received_utc TEXT NOT NULL,
    quality TEXT NOT NULL,
    state TEXT NOT NULL,
    late INTEGER NOT NULL CHECK(late IN (0,1)),
    payload TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS events_stream_time
    ON events(stream, observed_utc);
CREATE INDEX IF NOT EXISTS events_source ON events(source);
"""


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def stamp(value):
    return utc(value).isoformat(timespec="microseconds")


def checked_event(event):
    """Revalidar contrato e identidad determinista antes de persistir."""
    if not isinstance(event, dict):
        raise ValueError("EVENT_NOT_OBJECT")
    try:
        quality = event["quality"]
        observed = event["observed_at_utc"]
        if quality == "INVALID":
            # El contrato descarta el timestamp inválido original.
            observed = "invalid"
        rebuilt = make_event(
            source=event["source"], subject=event["subject"],
            resource_id=event["resource_id"], site=event["site"],
            peer_site=event["peer_site"], observed_at_utc=observed,
            received_at_utc=event["received_at_utc"], state=event["state"],
            available=quality != "MISSING", details=event["details"],
        )
        if canonical(event) != canonical(rebuilt):
            raise ValueError("EVENT_CONTRACT_MISMATCH")
        return rebuilt
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError("INVALID_EVENT_CONTRACT") from exc


def stream_key(e):
    return canonical([e[k] for k in
                      ("source", "subject", "resource_id", "site", "peer_site")])


def identity_content(e):
    excluded = {"received_at_utc", "age_seconds"}
    if e["observed_at_utc"] is None:
        excluded.remove("received_at_utc")
    return canonical({k: v for k, v in e.items() if k not in excluded})


def open_store(path):
    path = Path(path)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("INVALID_STORE_PATH")
    conn = sqlite3.connect(path, timeout=5)
    try:
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, VERSION):
            raise ValueError("UNSUPPORTED_STORE_VERSION")
        if version == 0:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if tables:
                raise ValueError("UNRECOGNIZED_DATABASE")
            conn.executescript("BEGIN IMMEDIATE;\n"+DDL+
                               f"\nPRAGMA user_version={VERSION};\nCOMMIT;")
        else:
            conn.execute("SELECT sequence,event_id,payload FROM events LIMIT 0")
        return conn
    except Exception:
        conn.close()
        raise


def import_batch(conn, batch):
    """Importación atómica. No modificar observaciones históricas existentes."""
    if (not isinstance(batch, dict) or batch.get("schema") != BATCH_SCHEMA
            or batch.get("network_mutations_authorized") is not False
            or batch.get("mode") != "READ_ONLY"
            or not isinstance(batch.get("events"), list)
            or len(batch["events"]) > MAX_EVENTS):
        raise ValueError("INVALID_BATCH")
    events = [checked_event(e) for e in batch["events"]]
    stats = {"received": len(events), "inserted": 0, "duplicates": 0, "late": 0}
    try:
        conn.execute("BEGIN IMMEDIATE")
        for e in events:
            key = e["event_id"]
            existing = conn.execute("SELECT payload FROM events WHERE event_id=?", (key,)).fetchone()
            if existing:
                if identity_content(json.loads(existing[0])) != identity_content(e):
                    raise ValueError("EVENT_ID_CONFLICT")
                stats["duplicates"] += 1
                continue
            stream = stream_key(e)
            observed = stamp(e["observed_at_utc"]) if e["observed_at_utc"] else None
            late = 0
            # Un timestamp futuro o inválido no avanza la frontera temporal.
            if observed is not None and e["quality"] in ("VALID", "STALE"):
                high = conn.execute(
                    "SELECT MAX(observed_utc) FROM events WHERE stream=? AND quality IN ('VALID','STALE')",
                    (stream,)).fetchone()[0]
                late = int(high is not None and observed < high)
            conn.execute(
                "INSERT INTO events(event_id,stream,source,subject,resource_id,observed_utc,"
                "received_utc,quality,state,late,payload) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (key, stream, e["source"], e["subject"], e["resource_id"], observed,
                 stamp(e["received_at_utc"]), e["quality"], e["state"], late, canonical(e)))
            stats["inserted"] += 1
            stats["late"] += late
        conn.commit()
        return stats
    except Exception:
        conn.rollback()
        raise


def history(conn):
    """Orden cronológico de observación, con ausentes al final."""
    rows = conn.execute("SELECT payload FROM events ORDER BY observed_utc IS NULL,"
                        "observed_utc,received_utc,event_id")
    return [json.loads(row[0]) for row in rows]


def summary(conn):
    events = history(conn)
    return {
        "schema": "NETLAB360_S07_HISTORY_V1",
        "mode": "HISTORICAL_NOT_LIVE",
        "total": len(events),
        "by_source": dict(Counter(e["source"] for e in events)),
        "by_quality_at_reception": dict(Counter(e["quality"] for e in events)),
        "by_state_at_reception": dict(Counter(e["state"] for e in events)),
        "late": conn.execute("SELECT COUNT(*) FROM events WHERE late=1").fetchone()[0],
        "integrity": conn.execute("PRAGMA quick_check").fetchone()[0],
        "network_mutations_authorized": False,
    }
