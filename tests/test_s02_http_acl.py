"""Pruebas sin red: control sudo/session y verificacion HTTP/ACL S02."""
from __future__ import annotations

import importlib.util
import inspect
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/laboratorio/s02_http_acl_demo.py"
SPEC = importlib.util.spec_from_file_location("s02_http", SCRIPT)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class TestS02HTTP(unittest.TestCase):
    def test_four_service_endpoints_unique(self):
        self.assertEqual(len(mod.SERVICES), 4)
        self.assertEqual(len({(s, port) for s, _, _, port in mod.SERVICES}), 4)

    def test_no_new_session_for_sudo_children(self):
        # Es la regresion que evita: sudo: interactive authentication is required
        self.assertIn("start_new_session=False", inspect.getsource(mod.main))
        self.assertNotIn("os.killpg(", inspect.getsource(mod.cleanup_http_processes))

    def test_http_readiness_confirms_body(self):
        with TemporaryDirectory() as tmp:
            log = Path(tmp) / "server.log"
            process = SimpleNamespace(poll=lambda: None)
            with patch.object(mod, "curl", return_value="NETLAB360_S02_HTTP_S1_8080_OK"):
                mod.wait_http_ready(process, "nl360-s02-h-s1-220",
                                    "10.71.20.20", 8080, log)

    def test_http_readiness_rejects_immediate_exit(self):
        with TemporaryDirectory() as tmp:
            log = Path(tmp) / "server.log"
            log.write_text("sudo: interactive authentication is required")
            proc = SimpleNamespace(poll=lambda: 1)
            with self.assertRaisesRegex(RuntimeError, "interactive authentication"):
                mod.wait_http_ready(proc, "ns", "10.71.20.20", 8080, log)

    def test_curl_refuses_failed_connection(self):
        fake = SimpleNamespace(returncode=7, stdout="", stderr="connection refused")
        with patch.object(subprocess, "run", return_value=fake):
            with self.assertRaisesRegex(RuntimeError, "HTTP falla"):
                mod.curl("ns", "http://10.71.20.20:8080/")

    def test_acl_negative_result_must_not_be_http_200(self):
        fake = SimpleNamespace(returncode=0, stdout="NETLAB360_S02_HTTP_S1_8081_OK", stderr="")
        with patch.object(subprocess, "run", return_value=fake):
            with self.assertRaisesRegex(RuntimeError, "ACL no bloqueo"):
                mod.curl("ns", "http://10.71.20.20:8081/", success=False)


if __name__ == "__main__":
    unittest.main()
