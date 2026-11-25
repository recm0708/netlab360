"""Pruebas de contrato y persistencia aislada de trabajos de diagnóstico."""
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_jobs", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_jobs import job_contract as C, jobs as J, storage, security

PAYLOAD = {"action": "test.ping.short", "route": "HQ_A_S1", "profile": "default"}


class ContractTests(unittest.TestCase):
    def test_catalog(self):
        rows = C.catalog()
        self.assertEqual(len(rows), 34)
        self.assertEqual(len({(r["action"], r["route"], r["profile"]) for r in rows}), 34)
        self.assertTrue(all(not r["execution_enabled"] and 0 < r["deadline_s"] <= 665 for r in rows))

    def test_extended(self):
        selection = C.select({"action": "test.content.tcp", "route": "HQ_A_S2", "profile": "content-5gb"})
        self.assertEqual(selection.deadline_s, 665)

    def test_reject_parameters(self):
        for payload in (dict(PAYLOAD, address="192.168.47.2"), dict(PAYLOAD, route="192.168.47.2"),
                        dict(PAYLOAD, action="test.ping.short;id"), dict(PAYLOAD, profile=[]),
                        dict(PAYLOAD, action="test.http"), dict(PAYLOAD, action="test.iperf.udp", profile="tcp-10s")):
            with self.assertRaises(ValueError):
                C.select(payload)


@unittest.skipIf(os.geteuid() == 0, "La persistencia exige usuario sin root")
class JobTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / "estado"
        storage.initialize(self.directory)
        storage.migrate(self.directory)
        storage.migrate_v3(self.directory)
        for user, role in (("operator", "OPERATOR"), ("other", "OPERATOR"), ("viewer", "VIEWER")):
            security.create_user(self.directory, user, "synthetic test phrase only", role)

    def enqueue(self):
        return J.enqueue(self.directory, "operator", PAYLOAD)

    def result(self, transport="OK"):
        return {"schema": "NETLAB360_S08_PROBE_V1", "action": PAYLOAD["action"],
                "route": PAYLOAD["route"], "transport": transport,
                "measurement": {"status": "NO_REPLY"} if transport == "OK" else None}

    def test_enqueue_and_read(self):
        job = self.enqueue()
        self.assertEqual(job["status"], "QUEUED")
        self.assertEqual(J.get(self.directory, "operator", job["job_id"]), job)

    def test_viewer_denied(self):
        with self.assertRaisesRegex(ValueError, "OPERATOR_REQUIRED"):
            J.enqueue(self.directory, "viewer", PAYLOAD)

    def test_exclusion(self):
        job = self.enqueue()
        for status in ("QUEUED", "RUNNING"):
            if status == "RUNNING":
                J.claim(self.directory, job["job_id"])
            with self.assertRaisesRegex(ValueError, "JOB_BUSY"):
                J.enqueue(self.directory, "other", PAYLOAD)

    def test_owner(self):
        job = self.enqueue()
        for method in (J.get, J.cancel_queued):
            with self.assertRaisesRegex(ValueError, "JOB_NOT_FOUND"):
                method(self.directory, "other", job["job_id"])

    def test_cancel(self):
        job = self.enqueue()
        cancelled = J.cancel_queued(self.directory, "operator", job["job_id"])
        self.assertEqual(cancelled["status"], "CANCELLED")
        self.assertIsNotNone(cancelled["finished_at_utc"])
        self.assertEqual(self.enqueue()["status"], "QUEUED")

    def test_lifecycle(self):
        job = self.enqueue()
        identifier = job["job_id"]
        self.assertEqual(J.claim(self.directory, identifier)["status"], "RUNNING")
        with self.assertRaisesRegex(ValueError, "INVALID_JOB_TRANSITION"):
            J.cancel_queued(self.directory, "operator", identifier)
        with self.assertRaisesRegex(ValueError, "CLEANUP_NOT_VERIFIED"):
            J.finish(self.directory, identifier, self.result(), cleanup_verified=False)
        result = J.finish(self.directory, identifier, self.result(), cleanup_verified=True)
        self.assertEqual(result["status"], "SUCCEEDED")
        self.assertEqual(result["data"]["result"]["measurement"]["status"], "NO_REPLY")
        with self.assertRaisesRegex(ValueError, "INVALID_JOB_TRANSITION"):
            J.finish(self.directory, identifier, self.result(), cleanup_verified=True)
        self.assertEqual(self.enqueue()["status"], "QUEUED")

    def test_result_identity(self):
        identifier = self.enqueue()["job_id"]
        J.claim(self.directory, identifier)
        with self.assertRaisesRegex(ValueError, "JOB_RESULT_SELECTION_MISMATCH"):
            J.finish(self.directory, identifier, dict(self.result(), route="HQ_A_S2"), cleanup_verified=True)
        self.assertEqual(J.get(self.directory, "operator", identifier)["status"], "RUNNING")

    def test_failure(self):
        identifier = self.enqueue()["job_id"]
        J.claim(self.directory, identifier)
        result = J.finish(self.directory, identifier, self.result("TIMEOUT"), cleanup_verified=True)
        self.assertEqual(result["status"], "FAILED")

    def test_audit(self):
        before = storage.inspect(self.directory)["audit_events"]
        identifier = self.enqueue()["job_id"]
        J.claim(self.directory, identifier)
        J.finish(self.directory, identifier, self.result(), cleanup_verified=True)
        self.assertEqual(storage.inspect(self.directory)["audit_events"], before + 3)


if __name__ == "__main__":
    unittest.main()
