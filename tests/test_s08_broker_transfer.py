"""Pruebas offline de selección, despacho y supervisión de transferencias protegidas."""
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import Mock, patch

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_broker_transfer_test", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_broker_transfer_test import broker_transfer as T, probe_broker as B
from netlab360_s08_broker_transfer_test.job_contract import select, catalog


@contextmanager
def available():
    yield


class BrokerTransferTests(unittest.TestCase):
    def test_all_transfer_plans(self):
        rows = [row for row in catalog() if row["profile"] != "default"]
        self.assertEqual(len(rows), 24)
        for row in rows:
            selection = select({key: row[key] for key in ("action", "route", "profile")})
            src, dst, server, client, ct, st, port = T.plan(selection, 997, 972)
            self.assertEqual(src.address, "10.70.20.20")
            self.assertNotEqual(src.namespace, dst.namespace)
            self.assertIn(port, (5201, 5202))
            self.assertLess(ct, st)
            self.assertLess(st, selection.deadline_s)
            for args in (client, server):
                self.assertEqual(args[0], "/usr/bin/setpriv")
                self.assertIn("--bounding-set=-all", args)
                self.assertIn("--no-new-privs", args)
                self.assertIn("--clear-groups", args)
                self.assertNotIn("/usr/bin/sudo", T.argv(src.namespace, args, ct))

    def test_root_identity_rejected(self):
        for uid, gid in ((0, 972), (997, 0), (True, 972)):
            with self.assertRaises(ValueError):
                T.drop(uid, gid)

    def test_protocol_mismatch(self):
        with self.assertRaises(ValueError):
            select({"action": "test.iperf.udp", "route": "HQ_A_S1", "profile": "tcp-5gb"})

    def test_managed_cleanup(self):
        process = Mock()
        process.poll.return_value = None
        process.pid = 12345
        with patch.object(T.subprocess, "Popen", return_value=process), patch.object(T.os, "killpg") as kill:
            with self.assertRaisesRegex(ValueError, "test"):
                with T.managed("fixed", ["/usr/bin/true"], 2):
                    raise ValueError("test")
            kill.assert_called_once_with(12345, T.signal.SIGKILL)
            process.wait.assert_called_once_with(timeout=5)

    def test_managed_completed(self):
        process = Mock()
        process.poll.return_value = 0
        with patch.object(T.subprocess, "Popen", return_value=process), patch.object(T.os, "killpg") as kill:
            with T.managed("fixed", ["/usr/bin/true"], 2):
                pass
            kill.assert_not_called()

    def dispatch(self, action, profile, schema, *, wrong=False, locked=False):
        payload = {"action": action, "route": "HQ_A_S1", "profile": profile}
        executor = Mock(return_value={"schema": schema, "profile": "wrong" if wrong else profile,
                                      "route": "HQ_A_S1", "transport": "OK", "measurement": {"status": "OK"}})
        @contextmanager
        def busy():
            raise BlockingIOError()
            yield
        left, right = socket.socketpair()
        with left, right, patch.object(B, "peer_uid", return_value=997):
            left.sendall(json.dumps(payload).encode() + b"\n")
            result = B.handle(right, 997, lock_factory=busy if locked else available, transfer=executor)
        return result, executor

    def test_transfer_dispatch(self):
        for action, profile, schema in (
            ("test.iperf.tcp", "tcp-5gb", "NETLAB360_S08_TRANSFER_V1"),
            ("test.iperf.udp", "udp-10s", "NETLAB360_S08_TRANSFER_V1"),
            ("test.content.tcp", "content-5gb", "NETLAB360_S08_CONTENT_V1"),
        ):
            result, executor = self.dispatch(action, profile, schema)
            self.assertEqual(result["status"], "OK")
            executor.assert_called_once()

    def test_wrong_result_profile(self):
        result, _ = self.dispatch("test.iperf.tcp", "tcp-10s", "NETLAB360_S08_TRANSFER_V1", wrong=True)
        self.assertEqual(result["status"], "INVALID_RESULT")

    def test_transfer_busy(self):
        result, executor = self.dispatch("test.content.tcp", "content-5gb", "NETLAB360_S08_CONTENT_V1", locked=True)
        self.assertEqual(result["status"], "BUSY")
        executor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
