"""Validamos lectura de alertas y migración sin modificar la fuente."""
import importlib.util
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_alerts", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_alerts import alerts_reader as reader, storage

STAMP = "2026-11-24T22:00:00+00:00"
RULE = "NETLAB360S04WANAdminDown"


class AlertsTests(unittest.TestCase):
    def test_active_empty_unavailable_and_valid(self):
        self.assertEqual(reader.active_alerts({"status":"success","data":{"alerts":[]}},STAMP,"OK")["records"],[])
        self.assertEqual(reader.active_alerts(None,STAMP,"UNAVAILABLE")["transport"],"UNAVAILABLE")
        data = {"status":"success","data":{"alerts":[{"labels":{"alertname":RULE,"site":"HQ","interface":"s1p"},
                                                        "state":"firing","activeAt":STAMP}]}}
        self.assertEqual(reader.active_alerts(data,STAMP,"OK")["records"][0]["state"],"firing")
        data["data"]["alerts"][0]["state"] = "resolved"
        self.assertEqual(reader.active_alerts(data,STAMP,"OK")["transport"],"INVALID")

    @unittest.skipIf(os.geteuid()==0,"Persistencia sin root")
    def test_snapshot_and_missing(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)
            directory = folder / "estado"
            storage.initialize(directory)
            source = folder / "incidentes.sqlite3"
            with sqlite3.connect(source) as db:
                db.execute("CREATE TABLE events(id INTEGER PRIMARY KEY, observed_at_utc TEXT, active_at_utc TEXT, alertname TEXT, site TEXT, resource TEXT, severity TEXT, state TEXT, source TEXT)")
                db.execute("INSERT INTO events VALUES(1,?,?,?,?,?,?,?,?)",
                           (STAMP,STAMP,RULE,"HQ","s1p","warning","resolved","verified_G3_terminal_log"))
            source.chmod(0o600)
            before = source.read_bytes()
            self.assertEqual(reader.history(directory)["transport"],"NOT_STARTED")
            exported = reader.export_snapshot(directory,source)
            self.assertEqual(exported["total"],1)
            self.assertEqual(reader.history(directory)["records"][0]["state"],"resolved")
            self.assertEqual(source.read_bytes(),before)
            self.assertEqual((directory/reader.SNAPSHOT).stat().st_mode & 0o777,0o600)
            (directory/reader.SNAPSHOT).unlink()
            (directory/reader.SNAPSHOT).symlink_to(source)
            self.assertEqual(reader.history(directory)["transport"],"INVALID")

    def test_snapshot_rejects_invalid_records(self):
        payload = {"schema":"NETLAB360_ALERT_HISTORY_V1","captured_at_utc":STAMP,"total":1,"records":[]}
        with self.assertRaises(ValueError):
            reader.snapshot_data(payload)

    @unittest.skipUnless(all(importlib.util.find_spec(x) for x in ("fastapi","httpx","pydantic"))
                         and os.geteuid()!=0,"API autenticada sin root")
    def test_http_permissions(self):
        from fastapi.testclient import TestClient
        from netlab360_s08_alerts import security, sessions
        from netlab360_s08_alerts.main import create_app
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root)/"estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory,"viewer","synthetic test phrase only","VIEWER")
            token = sessions.issue(directory,"viewer")["token"]
            with TestClient(create_app(directory),base_url="http://127.0.0.1:9140") as client:
                self.assertEqual(client.get("/api/v1/alerts").status_code,401)
                client.cookies.set("netlab360_session",token)
                self.assertEqual(client.get("/api/v1/alerts?url=other").status_code,400)
                self.assertEqual(client.post("/api/v1/alerts").status_code,405)
                with patch.object(reader,"collect",return_value={"network_mutations_authorized":False}):
                    self.assertEqual(client.get("/api/v1/alerts").status_code,200)
                    self.assertEqual(client.get("/api/v1/alerts").status_code,429)
