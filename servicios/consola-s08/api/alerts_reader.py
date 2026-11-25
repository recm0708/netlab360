"""Migración de alertas: lectura activa y copia explícita de transiciones observadas."""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import tempfile

from . import readers, storage

RULES = {
    "NETLAB360S04ExporterUnavailable": "Exportador no disponible",
    "NETLAB360S04CollectorUnknown": "Colector sin observación",
    "NETLAB360S04WANAdminDown": "WAN administrativamente inactiva",
    "NETLAB360S04VLANAdminDown": "VLAN administrativamente inactiva",
}
SITES = ("HQ", "S1", "S2", "GLOBAL")
SNAPSHOT = "alertas-historicas.json"
MAX_EVENTS = 200
MAX_BYTES = 262144
FIELDS = ("id", "observed_at_utc", "active_at_utc", "alertname", "site",
          "resource", "severity", "state", "source")


def timestamp(value, optional=False):
    if optional and value in (None, ""):
        return None
    if not isinstance(value, str) or len(value) > 64:
        raise ValueError("INVALID_TIMESTAMP")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("INVALID_TIMESTAMP")
    return dt.astimezone(timezone.utc).isoformat()


def label(value, length=64):
    if not isinstance(value, str) or not value or len(value) > length or any(ord(c) < 32 for c in value):
        raise ValueError("INVALID_LABEL")
    return value


def transition(row):
    if (type(row["id"]) is not int or row["id"] < 1 or row["alertname"] not in RULES
            or row["site"] not in SITES or row["state"] not in ("pending", "firing", "resolved")
            or row["source"] not in ("verified_G3_terminal_log", "prometheus_active_alerts")):
        raise ValueError("INVALID_EVENT")
    stamp = timestamp(row["observed_at_utc"])
    active = timestamp(row["active_at_utc"], optional=True)
    if active is not None and datetime.fromisoformat(active) > datetime.fromisoformat(stamp):
        raise ValueError("INVALID_EVENT_ORDER")
    return {"id": row["id"], "observed_at_utc": stamp, "active_at_utc": active,
            "alertname": row["alertname"], "site": row["site"],
            "resource": label(row["resource"]), "severity": label(row["severity"], 32),
            "state": row["state"], "source": row["source"]}


def snapshot_data(payload):
    if (payload["schema"] != "NETLAB360_ALERT_HISTORY_V1"
            or type(payload["total"]) is not int or payload["total"] < 0
            or not isinstance(payload["records"], list)
            or len(payload["records"]) != min(payload["total"], MAX_EVENTS)):
        raise ValueError("INVALID_SNAPSHOT")
    records = [transition(row) for row in payload["records"]]
    ids = [row["id"] for row in records]
    if ids != sorted(set(ids), reverse=True):
        raise ValueError("INVALID_EVENT_IDS")
    return {"schema": payload["schema"], "captured_at_utc": timestamp(payload["captured_at_utc"]),
            "total": payload["total"], "records": records}


def export_snapshot(directory, source):
    """Importamos una copia delimitada sin modificar la SQLite histórica."""
    storage.inspect(directory)
    storage._owned_database(source)
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True, timeout=5)) as db:
        db.execute("PRAGMA query_only=ON")
        db.row_factory = sqlite3.Row
        db.execute("BEGIN")
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("INVALID_HISTORY_DATABASE")
        total = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        records = [dict(row) for row in db.execute(
            "SELECT " + ",".join(FIELDS) + " FROM events ORDER BY id DESC LIMIT ?", (MAX_EVENTS,))]
        db.rollback()
    payload = snapshot_data({"schema": "NETLAB360_ALERT_HISTORY_V1",
                             "captured_at_utc": readers.now_utc(), "total": total, "records": records})
    raw = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode()
    if len(raw) > MAX_BYTES:
        raise ValueError("HISTORY_TOO_LARGE")
    target = directory / SNAPSHOT
    if target.exists() or target.is_symlink():
        storage._owned_database(target)
    fd, name = tempfile.mkstemp(prefix=".alerts-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, target)
    finally:
        Path(name).unlink(missing_ok=True)
    return payload


def history(directory):
    try:
        path = directory / SNAPSHOT
        storage._owned_database(path)
        with path.open("rb") as handle:
            payload = snapshot_data(readers.decode(handle.read(MAX_BYTES + 1), MAX_BYTES))
        return {"transport": "OK", **payload}
    except FileNotFoundError:
        return {"transport": "NOT_STARTED", "records": [], "total": None, "captured_at_utc": None}
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return {"transport": "INVALID", "records": [], "total": None, "captured_at_utc": None}


def active_alerts(payload, received, transport):
    """Distinguimos una consulta vacía confirmada de una fuente ausente."""
    result = {"transport": transport, "queried_at_utc": received, "records": [], "truncated": False}
    if transport != "OK":
        return result
    try:
        incoming = payload["data"]["alerts"]
        if payload["status"] != "success" or not isinstance(incoming, list) or len(incoming) > 1000:
            raise ValueError("INVALID_ALERTS")
        rows = []
        for item in incoming:
            labels = item["labels"]
            name = labels["alertname"]
            if name not in RULES:
                continue
            site, state = labels.get("site", "GLOBAL"), item["state"]
            if site not in SITES or state not in ("pending", "firing"):
                raise ValueError("INVALID_ALERT")
            rows.append({"alertname": name, "site": site, "state": state,
                         "resource": label(labels.get("interface", labels.get("vlan", "-"))),
                         "severity": label(labels.get("severity", "unknown"), 32),
                         "active_at_utc": timestamp(item["activeAt"])})
        result.update(records=rows[:50], truncated=len(rows) > 50)
    except (ValueError, TypeError, KeyError, AttributeError):
        result.update(transport="INVALID", records=[], truncated=False)
    return result


def collect(directory):
    current = active_alerts(*readers._fetch_fixed(9091, "/api/v1/alerts", MAX_BYTES))
    return {"project": "NETLAB360", "schema_version": 1, "current": current,
            "history": history(directory), "network_mutations_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("export",))
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    source = Path.home() / "netlab360-bootstrap/s04/historial/incidentes.sqlite3"
    payload = export_snapshot(args.directory, source)
    print(json.dumps({"total": payload["total"], "exported": len(payload["records"]),
                      "source_modified": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
