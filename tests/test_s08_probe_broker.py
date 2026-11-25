"""Pruebas de frontera Unix sin root, sin namespaces y sin tráfico real."""
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import Mock

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_broker_test", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_broker_test import probe_broker as B

PAYLOAD = {"action": "test.ping.short", "route": "HQ_A_S1", "profile": "default"}


@contextmanager
def available():
    yield


@contextmanager
def busy():
    raise BlockingIOError()
    yield


def measurement(selection):
    return {"schema": "NETLAB360_S08_PROBE_V1", "action": selection.action,
            "route": selection.route, "transport": "OK", "measurement": {"status": "OK"}}


class BrokerTests(unittest.TestCase):
    def test_valid_frame(self):
        self.assertEqual(B.decode_request(json.dumps(PAYLOAD).encode() + b"\n").action,
                         PAYLOAD["action"])

    def test_reject_invalid_frames(self):
        for raw in (b"", b"{}", b"{}\n{}\n", b"\xff\n", b"x" * 4097 + b"\n",
                    b'{"action":"x","action":"y"}\n'):
            with self.subTest(raw=raw[:32]), self.assertRaises(ValueError):
                B.decode_request(raw)

    def test_reject_extra_parameters(self):
        with self.assertRaises(ValueError):
            B.decode_request(json.dumps(dict(PAYLOAD, command="id")).encode() + b"\n")

    def test_kernel_peer(self):
        left, right = socket.socketpair()
        with left, right:
            self.assertEqual(B.peer_uid(right), os.getuid())

    def call(self, payload, uid=None, lock=available, executor=None):
        executor = executor or Mock(side_effect=measurement)
        left, right = socket.socketpair()
        with left, right:
            left.sendall(json.dumps(payload).encode() + b"\n")
            result = B.handle(right, os.getuid() if uid is None else uid, lock, executor)
        return result, executor

    @unittest.skipIf(os.getuid() == 0, "El cliente autorizado no puede ser root")
    def test_dispatch(self):
        result, executor = self.call(PAYLOAD)
        self.assertEqual(result["status"], "OK")
        executor.assert_called_once()

    def test_wrong_uid(self):
        result, executor = self.call(PAYLOAD, uid=os.getuid() + 1)
        self.assertEqual(result["status"], "DENIED")
        executor.assert_not_called()

    @unittest.skipIf(os.getuid() == 0, "El cliente autorizado no puede ser root")
    def test_disabled_transfer(self):
        result, executor = self.call(
            {"action": "test.iperf.tcp", "route": "HQ_A_S1", "profile": "tcp-5gb"})
        self.assertEqual(result["status"], "NOT_ENABLED")
        executor.assert_not_called()

    @unittest.skipIf(os.getuid() == 0, "El cliente autorizado no puede ser root")
    def test_busy(self):
        result, executor = self.call(PAYLOAD, lock=busy)
        self.assertEqual(result["status"], "BUSY")
        executor.assert_not_called()

    @unittest.skipIf(os.getuid() == 0, "El cliente autorizado no puede ser root")
    def test_invalid_result(self):
        result, _ = self.call(PAYLOAD, executor=Mock(return_value={"schema": "wrong"}))
        self.assertEqual(result["status"], "INVALID_RESULT")

    def test_lock_exclusion(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "active.lock"
            with B.global_lock(path):
                with self.assertRaises(BlockingIOError):
                    with B.global_lock(path):
                        self.fail("Se admitió una segunda ejecución")
            with B.global_lock(path):
                self.assertTrue(path.is_file())

    def test_unsafe_lock(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "active.lock"
            path.symlink_to(Path(folder) / "other")
            with self.assertRaises(OSError):
                with B.global_lock(path):
                    self.fail("Se siguió un enlace simbólico")


if __name__ == "__main__":
    unittest.main()
