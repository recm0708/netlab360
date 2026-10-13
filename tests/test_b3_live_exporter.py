#!/usr/bin/env python3
"""Regression tests for Docker inspect CLI error handling (no Docker required)."""
import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

TARGET = Path(__file__).resolve().parents[1] / "servicios/observabilidad/live_exporter.py"
spec = importlib.util.spec_from_file_location("netlab360_live_exporter", TARGET)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class DockerInspectionTests(unittest.TestCase):
    def test_absent_container_lowercase(self):
        result = subprocess.CompletedProcess(["docker"], 1, "", "error: no such object: nl360-b2-r-hq")
        with patch.object(module, "sudo_run", return_value=result):
            self.assertEqual(module.inspect_router(module.HQ), {"running": False, "pid": None})

    def test_absent_container_uppercase(self):
        result = subprocess.CompletedProcess(["docker"], 1, "", "Error: No such object: nl360-b2-r-hq")
        with patch.object(module, "sudo_run", return_value=result):
            self.assertEqual(module.inspect_router(module.HQ), {"running": False, "pid": None})

    def test_permission_denied_is_not_offline(self):
        result = subprocess.CompletedProcess(["docker"], 1, "", "permission denied while trying to connect")
        with patch.object(module, "sudo_run", return_value=result):
            with self.assertRaises(RuntimeError):
                module.inspect_router(module.HQ)

    def test_running_container(self):
        result = subprocess.CompletedProcess(["docker"], 0, "true 23456\n", "")
        with patch.object(module, "sudo_run", return_value=result):
            self.assertEqual(module.inspect_router(module.HQ), {"running": True, "pid": 23456})

    def test_stopped_container(self):
        result = subprocess.CompletedProcess(["docker"], 0, "false 0\n", "")
        with patch.object(module, "sudo_run", return_value=result):
            self.assertEqual(module.inspect_router(module.HQ), {"running": False, "pid": None})

if __name__ == "__main__":
    unittest.main(verbosity=2)
