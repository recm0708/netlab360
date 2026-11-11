"""Contrato offline: observadores de solo lectura aislados de sesiones SSH."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/operacion/s05-observador-privilegiado.py"
S04 = ROOT / "servicios/observabilidad/s04_exporter_multisede.py"
NOC = ROOT / "servicios/topologia-s05/app.py"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


helper = load(HELPER, "s05_privileged")
s04 = load(S04, "s05_s04")
noc = load(NOC, "s05_noc")


class ReadOnlyHelperTests(unittest.TestCase):
    def test_fixed_containers_and_routes_no_arbitrary_args(self):
        self.assertEqual(set(helper.NAMES), {"R-HQ", "R-S1", "R-S2"})
        self.assertEqual(helper.TARGETS, {"S1": "10.79.0.2", "S2": "10.79.0.3"})
        source = HELPER.read_text(encoding="utf-8")
        self.assertIn('sys.argv != [sys.argv[0], "snapshot"]', source)
        for forbidden in ('subprocess.Popen', '"ip", "link", "set"',
                          '"route", "add"', '"docker", "exec"',
                          '"docker", "stop"', "shell=True"):
            self.assertNotIn(forbidden, source)

    def test_route_rejects_unexpected_next_hop(self):
        packet = json.dumps([{"dev": "s1b", "gateway": "1.2.3.4"}])
        with patch.object(helper, "run", return_value=packet):
            self.assertIsNone(helper.fib(1234, "S1", "10.79.0.2"))
        valid = json.dumps([{"dev": "s1b", "gateway": "10.78.0.6"}])
        with patch.object(helper, "run", return_value=valid):
            self.assertEqual(helper.fib(1234, "S1", "10.79.0.2")["dev"], "s1b")

    def test_sudoers_is_fixed_one_action_and_web_units_unprivileged(self):
        for name in ("netlab360-s04-exporter", "netlab360-s05-noc"):
            path = ROOT / "servicios/systemd" / f"{name}.service"
            content = path.read_text(encoding="utf-8")
            self.assertIn("User=rc-aa-ec", content)
            self.assertIn("ProtectSystem=strict", content)
            self.assertIn("ProtectHome=read-only", content)
            self.assertIn("Environment=NETLAB360_PRIV_OBSERVER=/usr/local/libexec/netlab360-observer", content)
            self.assertIn("Restart=on-failure", content)
            self.assertNotIn("User=root", content)
            self.assertNotIn("ExecStart=/usr/bin/sudo", content)


class IntegratedSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.sample = {
            "project": "NETLAB360",
            "owner": "NETLAB360_S02_WAN_LINKS_V1",
            "routers": {
                key: {
                    "id": "a" * 64,
                    "running": True,
                    "pid": 100,
                    "links": {
                        "s1p": {"flags": ["UP"]},
                        "s1b": {"flags": ["UP"]},
                        "trunk0.110": {"flags": ["UP"]},
                    },
                }
                for key in ("R-HQ", "R-S1", "R-S2")
            },
            "routes": {
                "S1": {"dev": "s1b", "gateway": "10.78.0.6",
                       "target": "10.79.0.2", "origin": "Linux FIB R-HQ"},
                "S2": {"dev": "s2p", "gateway": "10.78.0.10",
                       "target": "10.79.0.3", "origin": "Linux FIB R-HQ"}
            },
        }

    def test_s04_trusted_snapshot_without_docker_calls(self):
        invoked = []
        def runner(argv):
            invoked.append(argv)
            return subprocess.CompletedProcess(argv, 0, json.dumps(self.sample), "")
        with patch.dict("os.environ", {"NETLAB360_PRIV_OBSERVER": s04.PRIV_HELPER}):
            snapshot = s04.trusted_snapshot(runner)
        self.assertEqual(snapshot["routers"]["R-HQ"]["links"]["s1p"]["flags"], ["UP"])
        self.assertEqual(invoked, [["sudo", "-n", s04.PRIV_HELPER, "snapshot"]])

    def test_noc_trusted_fib_without_direct_nsenter(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "wan.json"
            state.write_text(json.dumps(
                {"owner": "NETLAB360_S02_WAN_LINKS_V1",
                 "ids": {"R-HQ": "a" * 64}}), encoding="utf-8")
            output = subprocess.CompletedProcess([], 0, json.dumps(self.sample), "")
            with patch.object(noc, "WAN_STATE", state), \
                 patch.dict("os.environ", {"NETLAB360_PRIV_OBSERVER": noc.PRIV_HELPER}), \
                 patch.object(noc, "command", return_value=output) as runner:
                routes, warn = noc.fib_routes()
        self.assertEqual(warn, "")
        self.assertEqual(routes["S1"]["dev"], "s1b")
        self.assertEqual(routes["S2"]["dev"], "s2p")
        self.assertEqual(runner.call_args_list[0].args[:3],
                         ("sudo", "-n", noc.PRIV_HELPER))

    def test_noc_rejects_invalid_route(self):
        import tempfile
        self.sample["routes"]["S1"]["gateway"] = "8.8.8.8"
        with tempfile.TemporaryDirectory() as d:
            state = Path(d) / "wan.json"
            state.write_text(json.dumps(
                {"owner": "NETLAB360_S02_WAN_LINKS_V1",
                 "ids": {"R-HQ": "a" * 64}}), encoding="utf-8")
            output = subprocess.CompletedProcess([], 0, json.dumps(self.sample), "")
            with patch.object(noc, "WAN_STATE", state), \
                 patch.dict("os.environ", {"NETLAB360_PRIV_OBSERVER": noc.PRIV_HELPER}), \
                 patch.object(noc, "command", return_value=output):
                routes, _ = noc.fib_routes()
        self.assertIsNone(routes)


if __name__ == "__main__":
    unittest.main()
