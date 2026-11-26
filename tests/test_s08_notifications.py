"""Pruebas de alcance, integridad y autorización de la lectura de notificaciones."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import socket
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location("netlab360_s08_notifications", PACKAGE / "__init__.py",
                                             submodule_search_locations=[str(PACKAGE)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_notifications import notification_reader as N
S = runpy.run_path(str(ROOT / "scripts/s08/consultar_alertas.py"))
AVAILABLE = all(importlib.util.find_spec(n) is not None for n in ("fastapi", "httpx", "pydantic", "uvicorn"))


def frame(scope="operational"):
    labels = {"alertname": "NETLAB360S08ProbeFailed", "phase": "s08",
              "probe_id": "hq-s1-icmp", "laboratory": "netlab360-lab"}
    if scope == "validation":
        labels = {"alertname": "NETLAB360S08Validation", "phase": "validation",
                  "synthetic": "true", "run_id": "1234567890abcdef"}
    raw = json.dumps(labels, sort_keys=True, separators=(",", ":"))
    row = {"id": 1, "scope": scope, "fingerprint": hashlib.sha256(raw.encode()).hexdigest(),
           "alertname": labels["alertname"], "labels_json": raw, "status": "firing",
           "starts_at_utc": "2026-01-01T00:00:00+00:00", "ends_at_utc": None,
           "received_at_utc": "2026-01-01T00:00:01+00:00"}
    return {"schema": "NETLAB360_S08_NOTIFICATIONS_V1", "status": "OK",
            "result": {"source": "alertmanager_webhook", "scope": scope, "total": 1,
                       "records": [row]}}


class ReaderTests(unittest.TestCase):
    def test_scope_and_fingerprint(self):
        for scope in N.SCOPES:
            data = frame(scope)
            row = N.project(json.dumps(data).encode(), scope)["records"][0]
            self.assertEqual(row["scope"], scope)
            self.assertNotIn("labels_json", row)
            data["result"]["records"][0]["fingerprint"] = "wrong"
            with self.assertRaises(ValueError):
                N.project(json.dumps(data).encode(), scope)
        with self.assertRaises(ValueError):
            N.project(json.dumps(frame("validation")).encode(), "operational")

    def test_empty_is_distinct_from_unavailable(self):
        data = frame()
        data["result"].update(total=0, records=[])
        self.assertEqual(N.project(json.dumps(data).encode(), "operational")["total"], 0)
        with patch.object(N, "identity", side_effect=FileNotFoundError):
            result = N.collect("operational")
        self.assertEqual(result["transport"], "UNAVAILABLE")
        self.assertIsNone(result["total"])

    def test_invalid_scope_rejected(self):
        with self.assertRaises(ValueError):
            N.collect("other")

    def test_duplicate_ids_and_inconsistent_resolution(self):
        data = frame()
        data["result"]["records"] *= 2
        data["result"]["total"] = 2
        with self.assertRaises(ValueError):
            N.project(json.dumps(data).encode(), "operational")
        data = frame()
        data["result"]["records"][0]["status"] = "resolved"
        with self.assertRaises(ValueError):
            N.project(json.dumps(data).encode(), "operational")

    @unittest.skipIf(os.getuid() == 0, "El servidor exige cliente no root")
    def test_socket_scope_and_peer(self):
        for request, uid, accepted in (
                (b"operational\n", os.getuid(), True),
                (b"validation\n", os.getuid(), True),
                (b"operational\n", os.getuid() + 1, False),
                (b"operational\nx", os.getuid(), False)):
            inspect = Mock(return_value={"source": "test"})
            left, right = socket.socketpair()
            with left, right:
                left.sendall(request)
                left.shutdown(socket.SHUT_WR)
                S["serve"](right, uid, inspect)
                right.shutdown(socket.SHUT_WR)
                result = left.recv(4096)
            self.assertEqual(bool(result), accepted)
            self.assertEqual(inspect.call_count, int(accepted))


@unittest.skipUnless(AVAILABLE and os.geteuid() != 0, "API con dependencias y usuario sin root")
class HttpTests(unittest.TestCase):
    def test_roles(self):
        from fastapi.testclient import TestClient
        from netlab360_s08_notifications import security, sessions, storage
        from netlab360_s08_notifications.main import create_app
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "estado"
            storage.initialize(directory)
            storage.migrate(directory)
            for user, role in (("viewer", "VIEWER"), ("operator", "OPERATOR")):
                security.create_user(directory, user, "synthetic test phrase only", role)
            with TestClient(create_app(directory), base_url="http://127.0.0.1:9140") as client:
                path = "/api/v1/alerts/notifications/"
                self.assertEqual(client.get(path + "operational").status_code, 401)
                client.cookies.set("netlab360_session", sessions.issue(directory, "viewer")["token"])
                with patch.object(N, "collect", return_value={"transport": "OK"}) as collect:
                    self.assertEqual(client.get(path + "validation").status_code, 403)
                    self.assertEqual(client.get(path + "other").status_code, 400)
                    self.assertEqual(client.get(path + "operational?x=1").status_code, 400)
                    self.assertEqual(client.get(path + "operational").status_code, 200)
                    collect.assert_called_once_with("operational")
                client.cookies.set("netlab360_session", sessions.issue(directory, "operator")["token"])
                with patch.object(N, "collect", return_value={"transport": "OK"}) as collect:
                    self.assertEqual(client.get(path + "validation").status_code, 429)
                    collect.assert_not_called()


if __name__ == "__main__":
    unittest.main()
