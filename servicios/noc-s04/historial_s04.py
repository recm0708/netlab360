"""Historial S04 de transiciones reales de Prometheus, almacenamiento local SQLite.

No backfill automatico ni supuestos sobre eventos no observados por este NOC.
"""
from __future__ import annotations

from contextlib import closing
import csv
import hashlib
from io import StringIO
import json
from pathlib import Path
import sqlite3

DEFAULT_DB = Path.home() / "netlab360-bootstrap/s04/historial/incidentes.sqlite3"
SITES = ("HQ", "S1", "S2")


def initialize(path: Path = DEFAULT_DB) -> None:
    if path.parent.is_symlink() or path.is_symlink():
        raise RuntimeError("Ruta simbolica de historial prohibida")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    if path.exists() and not path.is_file():
        raise RuntimeError("Base de datos invalida")
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.execute("PRAGMA journal_mode=WAL")
        with db:
            db.execute("""
              CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fingerprint TEXT NOT NULL,
                observed_at_utc TEXT NOT NULL,
                active_at_utc TEXT,
                alertname TEXT NOT NULL,
                site TEXT NOT NULL,
                resource TEXT NOT NULL,
                severity TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('pending','firing','resolved')),
                source TEXT NOT NULL
              )
            """)
            db.execute("""
              CREATE TABLE IF NOT EXISTS active(
                fingerprint TEXT PRIMARY KEY,
                active_at_utc TEXT NOT NULL,
                labels_json TEXT NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('pending','firing'))
              )
            """)
    path.chmod(0o600)


def record(overview: dict, path: Path = DEFAULT_DB) -> int:
    prom = overview.get("prometheus", {})
    if prom.get("available") is not True or prom.get("alerts_known") is not True:
        return 0
    items = prom.get("alerts", [])
    if not isinstance(items, list):
        return 0
    now = overview.get("collected_at_utc")
    if not isinstance(now, str) or not now:
        raise ValueError("Marca temporal no disponible")
    seen = {}
    for item in items:
        labels = item.get("labels", {})
        state = item.get("state")
        if not isinstance(labels, dict) or not labels.get("alertname") or state not in ("pending", "firing"):
            continue
        label_json = json.dumps(labels, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        fp = hashlib.sha256(label_json.encode("utf-8")).hexdigest()
        seen[fp] = (str(item.get("activeAt") or ""), label_json, state)

    reliable = (prom.get("scrape") == "up"
                and overview.get("telemetry", {}).get("source_ok") is True
                and overview.get("telemetry", {}).get("fresh") is True)
    changes = 0
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.row_factory = sqlite3.Row
        with db:
            old = {row["fingerprint"]: row for row in db.execute(
                "SELECT fingerprint,active_at_utc,labels_json,state FROM active"
            )}

            def append(fp, labels, active_at, state):
                nonlocal changes
                db.execute("""
                  INSERT INTO events(fingerprint,observed_at_utc,active_at_utc,
                    alertname,site,resource,severity,state,source)
                  VALUES (?,?,?,?,?,?,?,?,?)
                """, (fp, now, active_at,
                      str(labels["alertname"])[:128], str(labels.get("site", "GLOBAL"))[:32],
                      str(labels.get("interface", labels.get("vlan", "-")))[:64],
                      str(labels.get("severity", "unknown"))[:32], state,
                      "prometheus_active_alerts"))
                changes += 1

            for fp, (active_at, label_json, state) in seen.items():
                previous = old.get(fp)
                if previous and previous["state"] == state and previous["active_at_utc"] == active_at:
                    continue
                append(fp, json.loads(label_json), active_at, state)
                db.execute("""
                  INSERT INTO active(fingerprint,active_at_utc,labels_json,state)
                    VALUES (?,?,?,?)
                  ON CONFLICT(fingerprint) DO UPDATE SET
                    active_at_utc=excluded.active_at_utc,
                    labels_json=excluded.labels_json,
                    state=excluded.state
                """, (fp, active_at, label_json, state))

            # No inferir "resolved" de ausencia durante falla de observacion.
            # El NOC expone como maximo 50 alertas; no asumir que el resto no existe.
            if reliable and len(items) < 50:
                for fp, previous in old.items():
                    if fp in seen:
                        continue
                    append(fp, json.loads(previous["labels_json"]),
                           previous["active_at_utc"], "resolved")
                    db.execute("DELETE FROM active WHERE fingerprint=?", (fp,))
    return changes


def events(site: str = "ALL", limit: int = 100, path: Path = DEFAULT_DB) -> list[dict]:
    if site not in ("ALL", *SITES):
        raise ValueError("Sede desconocida")
    if not isinstance(limit, int) or not 1 <= limit <= 200:
        raise ValueError("Limite fuera de rango")
    sql = ("SELECT id,observed_at_utc,active_at_utc,alertname,site,"
           "resource,severity,state,source FROM events")
    args = []
    if site != "ALL":
        sql += " WHERE site=? OR site='GLOBAL'"
        args.append(site)
    sql += " ORDER BY id DESC LIMIT ?"
    args.append(limit)
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute(sql, args)]


def as_csv(records: list[dict]) -> bytes:
    fields = ("id", "observed_at_utc", "active_at_utc", "alertname",
              "site", "resource", "severity", "state", "source")
    buf = StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for record in records:
        w.writerow({key: record.get(key, "") for key in fields})
    return buf.getvalue().encode("utf-8")
