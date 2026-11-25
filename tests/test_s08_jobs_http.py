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


    def test_history_isolation(self):
        headers = self.login()
        first = self.client.post(BASE, json=SELECTION, headers=headers).json()
        history = self.client.get(BASE).json()["jobs"]
        self.assertEqual([row["job_id"] for row in history], [first["job_id"]])
        self.assertNotIn("result", history[0])
        self.login("other")
        self.assertEqual(self.client.get(BASE).json()["jobs"], [])

    def test_stream_samples_and_final(self):
        selection = {"action":"test.content.tcp","route":"HQ_A_S1","profile":"content-100mb"}
        def transport(payload, emit, cancelled):
            self.assertEqual(payload, selection)
            self.assertFalse(cancelled())
            emit({"role":"sender","bytes":10000000,"elapsed_s":1.0})
            emit({"role":"receiver","bytes":9000000,"elapsed_s":1.0})
            emit({"role":"receiver","bytes":19000000,"elapsed_s":2.0})
            return {"kind":"final","status":"OK","cleanup_verified":True,
                    "result":{"schema":"NETLAB360_S08_CONTENT_V1","route":selection["route"],
                              "profile":selection["profile"],"transport":"OK","measurement":{"status":"OK"}}}
        with TestClient(create_app(self.directory, job_transport=self.transport, job_stream=transport),
                        base_url=ORIGIN) as client:
            self.client = client
            headers = self.login()
            rows = client.get(BASE+"/catalog").json()["selections"]
            self.assertEqual(sum(row["live_progress"] for row in rows),10)
            job = client.post(BASE,json=selection,headers=headers).json()
            result = client.get(BASE+"/"+job["job_id"]).json()
            self.assertEqual(result["status"],"SUCCEEDED")
            self.assertEqual([row["mbps"] for row in result["data"]["progress"]],[80.0,72.0,80.0])

    def test_stream_cancellation_requires_confirmation(self):
        selection = {"action":"test.content.tcp","route":"HQ_A_S1","profile":"content-100mb"}
        job = jobs.enqueue(self.directory,"operator",selection,stream_enabled=True)
        identifier = job["job_id"]
        jobs.claim(self.directory,identifier)
        self.login("other")
        # Consultar con el otro operador no revela el trabajo.
        self.assertEqual(self.client.get(BASE+"/"+identifier).status_code,404)
        headers = self.login()
        response = self.client.post(BASE+"/"+identifier+"/cancel",headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()["status"],"RUNNING")
        self.assertTrue(jobs.cancellation_requested(self.directory,identifier))
        with self.assertRaises(ValueError):
            jobs.finish_cancelled(self.directory,identifier,cleanup_verified=False)
        self.assertEqual(jobs.finish_cancelled(self.directory,identifier,cleanup_verified=True)["status"],"CANCELLED")

    def test_progress_rejects_regression(self):
        selection = {"action":"test.content.tcp","route":"HQ_A_S1","profile":"content-100mb"}
        job = jobs.enqueue(self.directory,"operator",selection,stream_enabled=True)
        identifier = job["job_id"]
        jobs.claim(self.directory,identifier)
        jobs.append_progress(self.directory,identifier,{"role":"sender","bytes":100,"elapsed_s":1})
        for event in ({"role":"sender","bytes":99,"elapsed_s":2},
                      {"role":"receiver","bytes":100000001,"elapsed_s":2},
                      {"role":"sender","bytes":200,"elapsed_s":1}):
            with self.assertRaises(ValueError):
                jobs.append_progress(self.directory,identifier,event)
        self.assertEqual(len(jobs.get(self.directory,"operator",identifier)["data"]["progress"]),1)

    def test_restart_retains_running_reservation(self):
        job = jobs.enqueue(self.directory,"operator",SELECTION)
        jobs.claim(self.directory,job["job_id"])
        self.assertEqual(jobs.recover_interrupted(self.directory),["RUNNING"])
        self.assertEqual(jobs.get(self.directory,"operator",job["job_id"])["data"]["execution_quality"],"UNCERTAIN")
        with self.assertRaises(ValueError):
            jobs.enqueue(self.directory,"operator",SELECTION)

    def test_restart_cancels_abandoned_queue(self):
        job = jobs.enqueue(self.directory,"operator",SELECTION)
        self.assertEqual(jobs.recover_interrupted(self.directory),["CANCELLED"])
        self.assertEqual(jobs.get(self.directory,"operator",job["job_id"])["status"],"CANCELLED")
        self.assertEqual(jobs.enqueue(self.directory,"operator",SELECTION)["status"],"QUEUED")

    def test_pilot_origin(self):
        with TestClient(create_app(self.directory,job_transport=self.transport,console_port=9145),
                        base_url="http://127.0.0.1:9145") as client:
            result = client.post("/api/v1/auth/login",json={"username":"operator","password":"synthetic test phrase only"},
                                 headers={"Origin":"http://127.0.0.1:9145"})
            self.assertEqual(result.status_code,200)
            self.assertEqual(client.get("/healthz").json()["mode"],"AUTHENTICATED_JOBS")
            self.assertEqual(client.get("/ui/static/jobs.js").status_code,200)
            self.assertIn('id="jobs-view"',client.get("/diagnostics").text)


if __name__ == "__main__":
    unittest.main()
