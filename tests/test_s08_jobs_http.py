"""Rutas de trabajos con transporte sintético y bases temporales, sin tráfico."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi", "pydantic", "httpx", "uvicorn"))
if AVAILABLE:
    from fastapi.testclient import TestClient
    package = ROOT / "servicios/consola-s08/api"
    spec = importlib.util.spec_from_file_location("netlab360_s08_jobs_http", package / "__init__.py",
                                                 submodule_search_locations=[str(package)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from netlab360_s08_jobs_http import broker_client, jobs, security, sessions, storage
    from netlab360_s08_jobs_http.main import create_app

ORIGIN = "http://127.0.0.1:9140"
BASE = "/api/v1/jobs"
SELECTION = {"action": "test.ping.short", "route": "HQ_A_S1", "profile": "default"}


def reply(selection):
    return {"schema": "NETLAB360_S08_BROKER_V1", "status": "OK",
            "result": {"schema": "NETLAB360_S08_PROBE_V1", "action": selection["action"],
                       "route": selection["route"], "transport": "OK", "measurement": {"status": "NO_REPLY"}}}


@unittest.skipUnless(AVAILABLE and os.geteuid() != 0, "API S08 con dependencias y usuario sin root")
class JobHttpTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / "estado"
        storage.initialize(self.directory)
        storage.migrate(self.directory)
        storage.migrate_v3(self.directory)
        for username, role in (("operator", "OPERATOR"), ("other", "OPERATOR"), ("viewer", "VIEWER")):
            security.create_user(self.directory, username, "synthetic test phrase only", role)
        self.transport = Mock(side_effect=reply)
        self.client = TestClient(create_app(self.directory, job_transport=self.transport), base_url=ORIGIN)
        self.addCleanup(self.client.close)

    def login(self, user="operator"):
        issued = sessions.issue(self.directory, user)
        self.client.cookies.set("netlab360_session", issued["token"])
        return {"Origin": ORIGIN, "X-CSRF-Token": issued["csrf_token"]}

    def test_default_disabled(self):
        with TestClient(create_app(self.directory), base_url=ORIGIN) as client:
            self.assertEqual(client.post(BASE, json=SELECTION).status_code, 404)

    def test_requires_session_and_role(self):
        self.assertEqual(self.client.get(BASE + "/catalog").status_code, 401)
        self.assertEqual(self.client.post(BASE, json=SELECTION).status_code, 401)
        headers = self.login("viewer")
        self.assertEqual(self.client.get(BASE + "/catalog").status_code, 403)
        self.assertEqual(self.client.post(BASE, json=SELECTION, headers=headers).status_code, 403)
        self.transport.assert_not_called()

    def test_csrf_origin(self):
        headers = self.login()
        for invalid in ({}, {"Origin": ORIGIN}, {"X-CSRF-Token": headers["X-CSRF-Token"]},
                        dict(headers, Origin="https://evil.invalid")):
            self.assertEqual(self.client.post(BASE, json=SELECTION, headers=invalid).status_code, 403)
        self.transport.assert_not_called()

    def test_reject_payload(self):
        headers = self.login()
        for invalid in (dict(SELECTION, actor="other"), dict(SELECTION, route="192.168.47.2"),
                        dict(SELECTION, action="id")):
            self.assertEqual(self.client.post(BASE, json=invalid, headers=headers).status_code, 400)
        headers["Content-Type"] = "application/json"
        self.assertEqual(self.client.post(BASE, content=b"x" * 4097, headers=headers).status_code, 413)
        self.assertEqual(self.client.post(BASE, content=b'{"action":"x","action":"y"}', headers=headers).status_code, 400)
        self.transport.assert_not_called()

    def test_submit_result_and_owner(self):
        headers = self.login()
        catalog = self.client.get(BASE + "/catalog").json()
        self.assertEqual(len(catalog["selections"]), 34)
        created = self.client.post(BASE, json=SELECTION, headers=headers)
        self.assertEqual(created.status_code, 202)
        self.assertEqual(created.json()["status"], "QUEUED")
        url = BASE + "/" + created.json()["job_id"]
        data = self.client.get(url).json()
        self.assertEqual(data["status"], "SUCCEEDED")
        self.assertEqual(data["data"]["result"]["measurement"]["status"], "NO_REPLY")
        self.transport.assert_called_once_with(SELECTION)
        self.login("other")
        self.assertEqual(self.client.get(url).status_code, 404)

    def test_queued_cancel_and_busy(self):
        headers = self.login()
        job = jobs.enqueue(self.directory, "operator", SELECTION)
        self.assertEqual(self.client.post(BASE, json=SELECTION, headers=headers).status_code, 409)
        url = BASE + "/" + job["job_id"] + "/cancel"
        self.assertEqual(self.client.post(url, headers=headers).json()["status"], "CANCELLED")
        self.transport.assert_not_called()

    def test_transport_disconnect_retains_reservation(self):
        headers = self.login()
        self.transport.side_effect = OSError("synthetic disconnect")
        created = self.client.post(BASE, json=SELECTION, headers=headers).json()
        data = self.client.get(BASE + "/" + created["job_id"]).json()
        self.assertEqual(data["status"], "RUNNING")
        self.assertEqual(data["data"]["execution_quality"], "UNCERTAIN")
        self.assertEqual(self.client.post(BASE, json=SELECTION, headers=headers).status_code, 409)

    def test_invalid_result_retains_reservation(self):
        headers = self.login()
        self.transport.side_effect = lambda selection: reply(dict(selection, route="HQ_A_S2"))
        created = self.client.post(BASE, json=SELECTION, headers=headers).json()
        data = self.client.get(BASE + "/" + created["job_id"]).json()
        self.assertEqual(data["status"], "RUNNING")
        self.assertEqual(data["data"]["execution_quality"], "UNCERTAIN")
        self.assertEqual(self.client.post(BASE + "/" + created["job_id"] + "/cancel", headers=headers).status_code, 409)

    def test_client_response_frame(self):
        good = json.dumps(reply(SELECTION)).encode() + b"\n"
        self.assertEqual(broker_client.decode(good)["status"], "OK")
        for raw in (b"", good + good, good[:-1], b"x" * 262145 + b"\n",
                    b'{"schema":"x","schema":"y"}\n'):
            with self.assertRaises(ValueError):
                broker_client.decode(raw)

    def test_broker_rejection_uncertain(self):
        headers = self.login()
        self.transport.side_effect = None
        self.transport.return_value = {"schema": "NETLAB360_S08_BROKER_V1", "status": "BUSY", "result": None}
        job = self.client.post(BASE, json=SELECTION, headers=headers).json()
        data = self.client.get(BASE + "/" + job["job_id"]).json()
        self.assertEqual(data["status"], "RUNNING")
        self.assertEqual(data["data"]["uncertainty_reason"], "BROKER_UNCONFIRMED")


if __name__ == "__main__":
    unittest.main()
