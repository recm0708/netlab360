"""Pruebas offline del colector S04. No requieren Docker ni red administrada."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "s04_exporter", ROOT / "servicios/observabilidad/s04_exporter_multisede.py"
)
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def sot_fixture():
    devices = {}
    ids = {"HQ": (110, 120, 130), "S1": (210, 220, 230), "S2": (310, 320, 330)}
    wans = {"HQ": ("s1p", "s1b", "s2p", "s2b"),
            "S1": ("s1p", "s1b"), "S2": ("s2p", "s2b")}
    for site in ("HQ", "S1", "S2"):
        devices["R-" + site] = {
            "container": "nl360-s02-r-" + site.lower(),
            "vlans": [{"id": x, "interface": "trunk0." + str(x)} for x in ids[site]],
            "wan": [{"interface": x, "address": "10.78.0.1/30"} for x in wans[site]],
        }
    return {"project": "NETLAB360", "source_status": "candidate", "devices": devices}


def cp(argv, code=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(argv, code, stdout, stderr)


def docker_obj(name, up=True, label=mod.DOCKER_PROJECT):
    return [{"Name": "/" + name,
             "HostConfig": {"NetworkMode": "none"},
             "Config": {"Labels": {"com.docker.compose.project": label}},
             "State": {"Running": up, "Pid": 1234 if up else 0}}]


class S04Tests(unittest.TestCase):
    def setUp(self):
        self.sot = sot_fixture()

    def test_valid_sot(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sot.json"
            path.write_text(json.dumps(self.sot))
            self.assertEqual(set(mod.load_sot(path)["devices"]), set(mod.EXPECTED))

    def test_invalid_cardinality_fails_closed(self):
        self.sot["devices"]["R-HQ"]["wan"].pop()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sot.json"
            path.write_text(json.dumps(self.sot))
            with self.assertRaises(mod.ObserveError):
                mod.load_sot(path)

    def test_guard_checks_address_and_gateway(self):
        def runner(argv):
            if argv[-2:] == ["show", "ens33"]:
                return cp(argv, stdout="ens33 UP 192.168.47.40/24")
            return cp(argv, stdout=mod.ADMIN_ROUTE)
        mod.management_guard(runner, hostname="netlab360-lab")
        with self.assertRaises(mod.ObserveError):
            mod.management_guard(runner, hostname="another-host")

    def test_absent_routers_offline_not_failure(self):
        def runner(argv):
            if argv[-2:] == ["show", "ens33"]:
                return cp(argv, stdout="ens33 UP 192.168.47.40/24")
            if argv[-2:] == ["show", "default"]:
                return cp(argv, stdout=mod.ADMIN_ROUTE)
            if argv[0] == "sudo":
                return cp(argv, code=1, stderr="Error: No such object")
            raise AssertionError(argv)
        state = mod.collect(self.sot, runner, hostname="netlab360-lab")
        self.assertTrue(state["source_ok"])
        self.assertEqual(state["topology"], "offline")
        self.assertEqual(state["routers"], {"R-HQ": 0, "R-S1": 0, "R-S2": 0})
        self.assertIn('netlab360_s04_topology_mode{mode="offline"} 1',
                      mod.prometheus_metrics(state))

    def test_permission_failure_is_unknown_not_offline(self):
        def runner(argv):
            if argv[-2:] == ["show", "ens33"]:
                return cp(argv, stdout="ens33 UP 192.168.47.40/24")
            if argv[-2:] == ["show", "default"]:
                return cp(argv, stdout=mod.ADMIN_ROUTE)
            return cp(argv, code=1, stderr="sudo: a password is required")
        state = mod.collect(self.sot, runner, hostname="netlab360-lab")
        self.assertFalse(state["source_ok"])
        self.assertEqual(state["topology"], "unknown")
        self.assertIn('netlab360_s04_router_running{router="R-HQ"} -1',
                      mod.prometheus_metrics(state))

    def test_project_fence(self):
        cname = "nl360-s02-r-hq"
        def runner(argv):
            return cp(argv, stdout=json.dumps(
                docker_obj(cname, label="some-other-project")))
        with self.assertRaises(mod.ObserveError):
            mod.inspect_router(cname, runner)

    def test_running_routers_and_vlan_wan_status(self):
        def runner(argv):
            if argv[-2:] == ["show", "ens33"]:
                return cp(argv, stdout="ens33 UP 192.168.47.40/24")
            if argv[-2:] == ["show", "default"]:
                return cp(argv, stdout=mod.ADMIN_ROUTE)
            if argv[:3] == ["sudo", "-n", "docker"]:
                return cp(argv, stdout=json.dumps(docker_obj(argv[-1])))
            if argv[:3] == ["sudo", "-n", "nsenter"]:
                links = [{"ifname": name, "flags": ["UP", "LOWER_UP"]}
                         for name in ("s1p", "s1b", "s2p", "s2b",
                                      "trunk0.110", "trunk0.120", "trunk0.130",
                                      "trunk0.210", "trunk0.220", "trunk0.230",
                                      "trunk0.310", "trunk0.320", "trunk0.330")]
                return cp(argv, stdout=json.dumps(links))
            raise AssertionError(argv)
        state = mod.collect(self.sot, runner, hostname="netlab360-lab")
        self.assertTrue(state["source_ok"])
        self.assertEqual(state["topology"], "active")
        self.assertEqual(state["sites"]["HQ"]["wan"]["s1p"]["admin_up"], 1)
        self.assertEqual(state["sites"]["S2"]["vlans"]["320"]["admin_up"], 1)
        self.assertEqual(sum(len(x["wan"]) for x in state["sites"].values()), 8)
        self.assertEqual(sum(len(x["vlans"]) for x in state["sites"].values()), 9)
        self.assertIn('netlab360_s04_wan_admin_up{site="S1",interface="s1b"} 1',
                      mod.prometheus_metrics(state))

    def test_partially_running_does_not_claim_full(self):
        def runner(argv):
            if argv[-2:] == ["show", "ens33"]:
                return cp(argv, stdout="ens33 UP 192.168.47.40/24")
            if argv[-2:] == ["show", "default"]:
                return cp(argv, stdout=mod.ADMIN_ROUTE)
            if argv[:3] == ["sudo", "-n", "docker"]:
                return cp(argv, stdout=json.dumps(
                    docker_obj(argv[-1], up=argv[-1].endswith("-hq"))))
            if argv[:3] == ["sudo", "-n", "nsenter"]:
                return cp(argv, stdout=json.dumps([]))
            raise AssertionError(argv)
        state = mod.collect(self.sot, runner, hostname="netlab360-lab")
        self.assertEqual(state["topology"], "partial")
        self.assertEqual(state["sites"]["HQ"]["wan"]["s1p"]["admin_up"], -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
