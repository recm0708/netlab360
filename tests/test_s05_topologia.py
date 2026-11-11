"""S05 topology: offline graph contract and truthful status tests."""
from __future__ import annotations

import importlib.util
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

APP = Path(__file__).resolve().parents[1] / "servicios/topologia-s05/app.py"
spec = importlib.util.spec_from_file_location("netlab360_s05_graph", APP)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TopologyGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = module.inventory()
        cls.extensions = {"schema_version": 1, "nodes": [], "links": []}

    def build(self, snapshot=None, ns=None, ext=None):
        return module.graph(
            self.inventory, snapshot, ns, self.extensions if ext is None else ext
        )

    @staticmethod
    def active_snapshot():
        return {
            "topology": "active",
            "observed_at_utc": "2026-11-10T16:00:00+00:00",
            "source_ok": True,
            "sites": {
                site: {
                    "running": 1,
                    "wan": {name: {"admin_up": 1} for name in ("s1p", "s1b", "s2p", "s2b")},
                    "vlans": {
                        str(v): {"admin_up": 1}
                        for v in (
                            {"HQ": (110, 120, 130), "S1": (210, 220, 230),
                             "S2": (310, 320, 330)}[site]
                        )
                    },
                }
                for site in ("HQ", "S1", "S2")
            },
        }

    def test_three_sites_full_inventory_not_invented(self):
        result = self.build()
        self.assertEqual(result["counts"]["sites"], 3)
        self.assertEqual(result["counts"]["routers"], 3)
        self.assertEqual(result["counts"]["switches"], 3)
        self.assertEqual(result["counts"]["hosts"], 9)
        self.assertEqual(result["counts"]["wan"], 4)
        self.assertEqual(len(result["nodes"]), 15)
        self.assertEqual(len(result["links"]), 16)
        self.assertTrue(all(n["status"] == "unknown" for n in result["nodes"]))
        self.assertTrue(all(l["status"] == "unknown" for l in result["links"]))

    def test_observed_offline(self):
        snapshot = self.active_snapshot()
        snapshot["topology"] = "offline"
        for site in snapshot["sites"].values():
            site["running"] = 0
        out = self.build(snapshot, set())
        self.assertEqual({n["status"] for n in out["nodes"]}, {"offline"})
        self.assertTrue(all(
            link["status"] == "offline"
            for link in out["links"] if link["type"] == "wan"
        ))

    def test_wan_requires_both_ends_up(self):
        snap = self.active_snapshot()
        snap["sites"]["HQ"]["wan"]["s1p"]["admin_up"] = 0
        out = self.build(snap, set())
        wan = {l["id"]: l for l in out["links"] if l["type"] == "wan"}
        self.assertEqual(wan["WAN-PRIMARIA-HQ-S1"]["status"], "admin-down")
        self.assertEqual(wan["WAN-RESPALDO-HQ-S1"]["status"], "admin-up")
        self.assertEqual(wan["WAN-PRIMARIA-HQ-S2"]["status"], "admin-up")
        self.assertNotIn("active", {l["status"] for l in wan.values()})

    def test_one_end_not_observed_is_unknown(self):
        snap = self.active_snapshot()
        snap["sites"]["S1"]["wan"]["s1p"]["admin_up"] = -1
        wan = [l for l in self.build(snap)["links"]
               if l["id"] == "WAN-PRIMARIA-HQ-S1"][0]
        self.assertEqual(wan["status"], "unknown")

    def test_namespace_is_not_assumed_alive(self):
        snap = self.active_snapshot()
        result = self.build(snap, {"nl360-s02-sw-hq", "nl360-s02-h-hq-110"})
        hosts = {n["id"]: n for n in result["nodes"]}
        self.assertEqual(hosts["SW-HQ"]["status"], "namespace-present")
        self.assertEqual(hosts["H-HQ-110"]["status"], "namespace-present")
        self.assertEqual(hosts["H-HQ-120"]["status"], "offline")
        self.assertEqual(hosts["H-HQ-110"]["vlan_admin"], "admin-up")
        self.assertNotIn("server", {n["type"] for n in result["nodes"]})

    def test_extension_only_realized_and_valid(self):
        ext = {"schema_version": 1, "nodes": [
            {"id": "HA-HQ-A", "site": "HQ", "type": "server", "label": "HA verificado",
             "realized": True, "evidence": "issue con pruebas"},
            {"id": "FUTURO-S1", "site": "S1", "type": "server", "realized": False}
        ], "links": []}
        out = self.build(ext=ext)
        self.assertEqual(out["counts"]["extensions"], 1)
        self.assertEqual(out["nodes"][-1]["status"], "unknown")
        ext["nodes"][0]["id"] = "R-HQ"
        with self.assertRaises(ValueError):
            self.build(ext=ext)


    def test_fib_primary_selected_and_backup_standby(self):
        snap = self.active_snapshot()
        fib = {
            "S1": {"dev": "s1p", "gateway": "10.78.0.2", "target": "10.79.0.2"},
            "S2": {"dev": "s2p", "gateway": "10.78.0.10", "target": "10.79.0.3"},
        }
        out = module.graph(self.inventory, snap, set(), self.extensions, fib=fib)
        wan = {l["id"]: l for l in out["links"] if l["type"] == "wan"}
        self.assertTrue(out["routing"]["available"])
        self.assertFalse(out["routing"]["traffic_measured"])
        for site in ("S1", "S2"):
            self.assertEqual(wan[f"WAN-PRIMARIA-HQ-{site}"]["route_selection"],
                             "selected")
            self.assertEqual(wan[f"WAN-RESPALDO-HQ-{site}"]["route_selection"],
                             "standby")

    def test_fib_selected_backup_when_primary_down(self):
        snap = self.active_snapshot()
        snap["sites"]["HQ"]["wan"]["s1p"]["admin_up"] = 0
        fib = {
            "S1": {"dev": "s1b", "gateway": "10.78.0.6", "target": "10.79.0.2"},
            "S2": {"dev": "s2p", "gateway": "10.78.0.10", "target": "10.79.0.3"},
        }
        out = module.graph(self.inventory, snap, set(), self.extensions, fib=fib)
        wan = {l["id"]: l for l in out["links"] if l["type"] == "wan"}
        self.assertEqual(wan["WAN-PRIMARIA-HQ-S1"]["route_selection"],
                         "unavailable")
        self.assertEqual(wan["WAN-RESPALDO-HQ-S1"]["route_selection"],
                         "selected")
        self.assertEqual(wan["WAN-PRIMARIA-HQ-S2"]["route_selection"],
                         "selected")
        self.assertEqual(wan["WAN-RESPALDO-HQ-S2"]["route_selection"],
                         "standby")

    def test_fib_unknown_without_observation_or_admin_source(self):
        snap = self.active_snapshot()
        self.assertTrue(all(
            l["route_selection"] == "unknown"
            for l in self.build(snap)["links"] if l["type"] == "wan"
        ))
        snap["sites"]["S1"]["wan"]["s1p"]["admin_up"] = -1
        fib = {"S1": {"dev": "s1p", "gateway": "10.78.0.2"}}
        out = module.graph(self.inventory, snap, set(), self.extensions, fib=fib)
        links = {l["id"]: l for l in out["links"] if l["type"] == "wan"}
        self.assertEqual(links["WAN-PRIMARIA-HQ-S1"]["route_selection"],
                         "unknown")
        self.assertEqual(links["WAN-PRIMARIA-HQ-S2"]["route_selection"],
                         "unknown")

    def test_fib_observer_checks_identity_and_reads_only(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "wan-state.json"
            path.write_text(json.dumps({
                "owner": "NETLAB360_S02_WAN_LINKS_V1",
                "ids": {"R-HQ": "b" * 64}
            }))
            info = {"Id": "b" * 64, "Name": "/nl360-s02-r-hq",
                    "State": {"Running": True, "Pid": 12345},
                    "HostConfig": {"NetworkMode": "none"},
                    "Config": {"Labels": {
                        "com.docker.compose.project": "netlab360-s02-wan"
                    }}}
            returns = [
                subprocess.CompletedProcess([], 0, json.dumps([info]), ""),
                subprocess.CompletedProcess([], 0, json.dumps([
                    {"dev": "s1p", "gateway": "10.78.0.2"}
                ]), ""),
                subprocess.CompletedProcess([], 0, json.dumps([
                    {"dev": "s2b", "gateway": "10.78.0.14"}
                ]), ""),
            ]
            with patch.object(module, "WAN_STATE", path), patch.object(
                module, "command", side_effect=returns
            ) as call:
                routes, warn = module.fib_routes()
            self.assertEqual(warn, "")
            self.assertEqual(routes["S1"]["dev"], "s1p")
            self.assertEqual(routes["S2"]["dev"], "s2b")
            self.assertEqual(call.call_count, 3)
            for called in call.call_args_list:
                argv = called.args
                self.assertEqual(argv[:2], ("sudo", "-n"))
                self.assertNotIn("set", argv)
                self.assertNotIn("add", argv)
                self.assertNotIn("delete", argv)

    def test_fib_observer_never_fabricates_when_unavailable(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing.json"
            with patch.object(module, "WAN_STATE", path), patch.object(
                module, "command"
            ) as call:
                routes, warn = module.fib_routes()
            self.assertIsNone(routes)
            self.assertIn("sin estado", warn)
            call.assert_not_called()

    def test_vm_clock_uses_panama_zone_and_keeps_utc(self):
        d = self.build()
        clock = d["vm_clock"]
        self.assertEqual(clock["timezone"], "America/Panama")
        self.assertEqual(clock["source"], "system_clock_vm")
        instant_utc = datetime.fromisoformat(clock["utc"])
        instant_local = datetime.fromisoformat(clock["panama"])
        self.assertEqual(instant_local.utcoffset(), timedelta(hours=-5))
        self.assertEqual(instant_utc.utcoffset(), timedelta(0))
        self.assertEqual(
            instant_utc.astimezone(timezone.utc),
            instant_local.astimezone(timezone.utc),
        )
        self.assertEqual(d["observed_at_utc"], clock["utc"])


    def test_namespaces_prefers_read_only_without_sudo(self):
        result = subprocess.CompletedProcess(
            ("ip", "netns", "list"), 0, "nl360-s02-sw-hq (id: 0)\n"
        )
        with patch.object(module, "command", return_value=result) as runner:
            names, warning = module.namespaces()
        self.assertEqual(names, {"nl360-s02-sw-hq"})
        self.assertEqual(warning, "")
        self.assertEqual(runner.call_args.args, ("ip", "netns", "list"))

    def test_namespaces_falls_back_only_if_needed(self):
        rejected = subprocess.CompletedProcess(("ip", "netns", "list"), 1, "")
        accepted = subprocess.CompletedProcess(
            ("sudo", "-n", "ip", "netns", "list"), 0, ""
        )
        with patch.object(module, "command", side_effect=(rejected, accepted)) as runner:
            names, warning = module.namespaces()
        self.assertEqual(names, set())
        self.assertEqual(warning, "")
        self.assertEqual(runner.call_count, 2)



if __name__ == "__main__":
    unittest.main()
