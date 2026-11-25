"""Pruebas offline de transferencia de contenido y descenso de privilegios."""
import hashlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_content", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_content import content_executor as M
from netlab360_s08_content import content_worker as W


class MemorySocket:
    def __init__(self, data=b""):
        self.data = io.BytesIO(data)
        self.closed_write = False

    def sendall(self, data):
        self.data.write(data)

    def recv(self, size):
        return self.data.read(size)

    def shutdown(self, how):
        self.closed_write = True


class ContentTests(unittest.TestCase):
    def test_profiles(self):
        self.assertEqual(tuple(M.PROFILES.values()), W.VOLUMES)
        for profile in M.PROFILES:
            for route in M.ROUTES:
                src, dst, tx, rx, deadline = M.commands(profile, route, 1000, 1000)
                self.assertEqual(tx[0], "/usr/bin/setpriv")
                self.assertIn("--no-new-privs", tx)
                self.assertIn("--bounding-set=-all", rx)
                self.assertIn("-I", rx)
                self.assertEqual(tx[tx.index("--site") + 1], dst.address)
                self.assertGreater(deadline, M.PROFILES[profile] * 8 / W.BITRATE)
                self.assertEqual(src.address, W.HQ)

    def test_invalid_selection(self):
        for args in (("content-10gb", "HQ_A_S1", 1000, 1000),
                     ("content-100mb", "192.168.47.2", 1000, 1000),
                     ("content-100mb", "HQ_A_S1", 0, 1000)):
            with self.assertRaises(ValueError):
                M.commands(*args)

    def test_stream_exact_and_reproducible(self):
        size = W.BLOCK * 2 + 7
        sock = MemorySocket()
        sent = W.send_stream(sock, size, 100_000_000, pause=lambda _: None)
        data = sock.data.getvalue()
        self.assertEqual(len(data), size)
        self.assertTrue(sock.closed_write)
        received = W.receive_stream(MemorySocket(data), size)
        self.assertEqual(sent["sha256"], received["sha256"])
        self.assertEqual(received["sha256"], hashlib.sha256(data).hexdigest())
        another = MemorySocket()
        W.send_stream(another, size, 100_000_000, pause=lambda _: None)
        self.assertEqual(another.data.getvalue(), data)

    def test_short_stream(self):
        with self.assertRaisesRegex(ValueError, "PREMATURE_EOF"):
            W.receive_stream(MemorySocket(b"abc"), 4)

    def test_excess_stream(self):
        with self.assertRaisesRegex(ValueError, "EXCESS_CONTENT"):
            W.receive_stream(MemorySocket(b"abcd"), 3)

    def pair(self):
        base = {"site": "10.71.20.20", "uid": 1000, "target_bytes": 100000000,
                "bytes": 100000000, "sha256": "a" * 64, "duration_s": 8}
        return dict(base, role="sender"), dict(base, role="receiver")

    def test_reconcile_match(self):
        tx, rx = self.pair()
        result = M.reconcile("content-100mb", "HQ_A_S1", tx, rx, 1000)
        self.assertTrue(result["content_integrity_verified"])
        self.assertEqual(result["receiver_mbps"], 100)

    def test_reconcile_corruption(self):
        tx, rx = self.pair()
        rx["sha256"] = "b" * 64
        result = M.reconcile("content-100mb", "HQ_A_S1", tx, rx, 1000)
        self.assertFalse(result["content_integrity_verified"])
        self.assertEqual(result["status"], "CONTENT_MISMATCH")

    def test_reconcile_size_or_identity(self):
        for key, value in (("bytes", 99999999), ("uid", 0), ("site", "10.72.20.20"),
                           ("sha256", "wrong"), ("duration_s", 0)):
            tx, rx = self.pair()
            rx[key] = value
            with self.assertRaises(ValueError):
                M.reconcile("content-100mb", "HQ_A_S1", tx, rx, 1000)


if __name__ == "__main__":
    unittest.main()
