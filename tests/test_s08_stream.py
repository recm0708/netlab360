"""Pruebas offline del canal de progreso y cancelación, sin red ni privilegios."""
from contextlib import contextmanager
import importlib.util
import json
from pathlib import Path
import socket
import struct
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, Mock, patch

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_stream_test", PACKAGE / "__init__.py", submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_stream_test import broker_stream as S, broker_client as C, probe_broker as B
from netlab360_s08_stream_test.job_contract import select
from netlab360_s08_stream_test.stream_protocol import sample

PAYLOAD = {"action": "test.content.tcp", "route": "HQ_A_S1", "profile": "content-100mb"}
EVENT = {"role": "sender", "bytes": 10000000, "elapsed_s": 1.0}


@contextmanager
def available():
    yield


class StreamTests(unittest.TestCase):
    def test_sample_and_interval_rate(self):
        first = sample(EVENT, PAYLOAD["profile"])
        second = sample(dict(EVENT, bytes=18000000, elapsed_s=2), PAYLOAD["profile"], first)
        self.assertEqual(first["mbps"], 80)
        self.assertEqual(second["mbps"], 64)

    def test_invalid_sample(self):
        for value in (dict(EVENT, bytes=True), dict(EVENT, elapsed_s=float("nan")),
                      dict(EVENT, bytes=100000001), dict(EVENT, role="other"), dict(EVENT, uid=0)):
            with self.assertRaises(ValueError):
                sample(value, PAYLOAD["profile"])

    def test_partial_line_and_independent_progress(self):
        emit = Mock()
        progress = S.Progress("sender", PAYLOAD["profile"], emit)
        line = b"NL360_PROGRESS " + json.dumps(EVENT).encode() + b"\n"
        with tempfile.TemporaryFile() as handle:
            handle.write(line[:20])
            handle.flush()
            progress.poll(handle)
            emit.assert_not_called()
            handle.write(line[20:])
            handle.flush()
            progress.poll(handle)
            progress.poll(handle)
        emit.assert_called_once_with(EVENT)

    def test_cancel_from_same_connection(self):
        left, right = socket.socketpair()
        with left, right:
            control = S.Control(right)
            control.check()
            left.sendall(b"CAN")
            control.check()
            left.sendall(b"CEL\n")
            with self.assertRaises(S.CancelRequested):
                control.check()

    def test_disconnection_requests_cleanup(self):
        left, right = socket.socketpair()
        with right:
            left.close()
            with self.assertRaises(S.CancelRequested):
                S.Control(right).check()

    def test_broker_stream_dispatch(self):
        left, right = socket.socketpair()
        with left, right, patch.object(B, "peer_uid", return_value=997), \
                patch.object(B, "global_lock", available), patch.object(S, "run", return_value=S.final("CANCELLED", cleanup=True)) as run:
            left.sendall(json.dumps(dict(PAYLOAD, stream=True)).encode() + b"\n")
            B.serve(right, 997, worker=(994, 971))
            with left.makefile("rb") as stream:
                self.assertEqual(json.loads(stream.readline()), {"kind":"accepted"})
                self.assertEqual(json.loads(stream.readline()), S.final("CANCELLED", cleanup=True))
            self.assertEqual(run.call_args.args[1], select(PAYLOAD))
            self.assertEqual(run.call_args.args[2:], (994, 971))

    def test_cancel_before_workers_still_checks_ports(self):
        left, right = socket.socketpair()
        selection = select(PAYLOAD)
        with left, right, patch.object(S, "verify_identity"), \
                patch.object(S.T, "listener", return_value="") as listener, patch.object(S.T, "managed") as managed:
            left.sendall(b"CANCEL\n")
            result = S.run(right, selection, 994, 971)
            self.assertEqual(result, S.final("CANCELLED", cleanup=True))
            self.assertEqual(listener.call_count, 4)
            managed.assert_not_called()

    def test_client_stream_and_cancel(self):
        conn = MagicMock()
        conn.__enter__.return_value = conn
        conn.getsockopt.return_value = struct.pack("3i", 1, 0, 0)
        frames = (json.dumps({"kind":"progress","sample":EVENT}) + "\n"
                  + json.dumps(S.final("CANCELLED", cleanup=True)) + "\n").encode()
        conn.recv.side_effect = [b'{"kind":"accepted"}\n', frames[:17], frames[17:]]
        emit = Mock()
        with patch.object(C, "check_identity"), patch.object(C.socket, "socket", return_value=conn):
            result = C.request_stream(PAYLOAD, emit, lambda: True)
        self.assertEqual(result["status"],"CANCELLED")
        emit.assert_called_once_with(EVENT)
        self.assertEqual(conn.sendall.call_args_list[-1].args[0], b"CANCEL\n")

    def test_client_rejects_unrequested_cancel(self):
        conn = MagicMock()
        conn.__enter__.return_value = conn
        conn.getsockopt.return_value = struct.pack("3i", 1, 0, 0)
        conn.recv.side_effect = [b'{"kind":"accepted"}\n', (json.dumps(S.final("CANCELLED", cleanup=True))+"\n").encode()]
        with patch.object(C,"check_identity"), patch.object(C.socket,"socket",return_value=conn):
            with self.assertRaisesRegex(ValueError,"STREAM_UNREQUESTED_CANCEL"):
                C.request_stream(PAYLOAD,Mock(),lambda:False)


if __name__ == "__main__":
    unittest.main()
