"""Monitor y NOC HA: solo una muestra S2 fresca autoriza estado activo."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(file: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


monitor = load(ROOT / "servicios/ha-s05/monitor_http_s2.py", "ha_s05_monitor")
noc = load(ROOT / "servicios/topologia-s05/app.py", "ha_s05_noc")


class HAMonitorTests(unittest.TestCase):
    def test_only_three_fixed_endpoints_without_proxy(self):
        self.assertEqual(set(monitor.TARGETS), {"BACKEND_HQ", "BACKEND_S1", "FRONTAL_HQ"})
        self.assertEqual(monitor.TARGETS["BACKEND_HQ"]["ip"], "10.70.20.21")
        self.assertEqual(monitor.TARGETS["BACKEND_S1"]["ip"], "10.71.20.21")
        self.assertEqual(monitor.TARGETS["FRONTAL_HQ"]["ip"], "10.70.20.23")
        src = (ROOT / "servicios/ha-s05/monitor_http_s2.py").read_text()
        self.assertIn("ProxyHandler({})", src)
        self.assertIn('os.stat("/proc/self/ns/net").st_ino', src)
        self.assertNotIn("sudo", src)
        self.assertNotIn("docker", src.lower().split('def ensure_network_namespace')[1])

    def test_valid_healthcheck_and_frontend_selection(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self, n): return json.dumps({
                "service": monitor.SERVICE, "id": "FRONTAL_HQ",
                "role": "frontend", "status": "available",
                "active_backend": "BACKEND_S1", "selected_path": "RESPALDO"
            }).encode()
        with patch.object(monitor.OPENER, "open", return_value=Response()):
            row = monitor.probe("FRONTAL_HQ")
        self.assertEqual(row["status"], "running")
        self.assertEqual(row["active_backend"], "BACKEND_S1")

    def test_unexpected_http_id_is_unknown(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *_): return False
            def read(self, n): return json.dumps({
                "service": monitor.SERVICE, "id": "BACKEND_S1",
                "role": "backend", "site": "S1", "status": "healthy"
            }).encode()
        with patch.object(monitor.OPENER, "open", return_value=Response()):
            self.assertEqual(monitor.probe("BACKEND_HQ")["status"], "unknown")

    def test_snapshot_contains_ownership_and_utc(self):
        fake = [{"status": "running", "site": m["site"], "ip": m["ip"]}
                for m in monitor.TARGETS.values()]
        with patch.object(monitor, "probe", side_effect=fake):
            result = monitor.observe()
        self.assertEqual(result["owner"], monitor.OWNER)
        self.assertEqual(result["source_netns"], monitor.SOURCE)
        self.assertEqual(set(result["services"]), set(monitor.TARGETS))
        self.assertTrue(result["observed_at_utc"].endswith("+00:00"))


class NOCServiceObservationTests(unittest.TestCase):
    def sample(self, seconds_ago=0):
        return {
            "owner": noc.HA_OWNER,
            "source_netns": noc.HA_SOURCE,
            "observed_at_utc": (datetime.now(timezone.utc) -
                                timedelta(seconds=seconds_ago)).isoformat(),
            "services": {
                "BACKEND_HQ": {"site": "HQ", "ip": "10.70.20.21",
                               "status": "running"},
                "BACKEND_S1": {"site": "S1", "ip": "10.71.20.21",
                               "status": "running"},
                "FRONTAL_HQ": {"site": "HQ", "ip": "10.70.20.23",
                               "status": "running", "active_backend": "BACKEND_S1",
                               "selected_path": "RESPALDO"},
            },
        }

    def test_fresh_snapshot_is_observed(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "status.json"
            path.write_text(json.dumps(self.sample()))
            data, warning = noc.ha_observation(path)
        self.assertEqual(warning, "")
        self.assertEqual(data["services"]["FRONTAL_HQ"]["active_backend"], "BACKEND_S1")

    def test_stale_snapshot_never_claims_running(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "status.json"
            path.write_text(json.dumps(self.sample(seconds_ago=30)))
            data, warning = noc.ha_observation(path)
        self.assertIsNone(data)
        self.assertIn("obsoleta", warning)

    def test_wrong_source_or_identity_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "status.json"
            row = self.sample()
            row["services"]["BACKEND_HQ"]["ip"] = "8.8.8.8"
            path.write_text(json.dumps(row))
            data, _ = noc.ha_observation(path)
        self.assertIsNone(data)

    def test_graph_realized_nodes_status_and_app_selected(self):
        ext = noc.extensions()
        self.assertEqual(len(ext["nodes"]), 3)
        self.assertEqual(len(ext["links"]), 5)
        data = noc.graph(noc.inventory(), None, None, ext, ha=self.sample())
        nodes = {x["id"]: x for x in data["nodes"]}
        self.assertEqual(data["counts"]["extensions"], 3)
        self.assertEqual(nodes["BACKEND_HQ"]["application_selection"], "standby")
        self.assertEqual(nodes["BACKEND_S1"]["application_selection"], "selected")
        self.assertEqual(nodes["FRONTAL_HQ"]["status"], "running")
        links = {x["id"]: x for x in data["links"]}
        self.assertEqual(links["S05-HA-HTTP-RESPALDO"]["application_selection"], "selected")
        self.assertEqual(links["S05-HA-HTTP-PRINCIPAL"]["application_selection"], "standby")
        self.assertEqual(data["ha_service"]["selected_path"], "RESPALDO")
        self.assertEqual(len([x for x in data["links"] if x["type"] == "wan"]), 4)

    def test_without_monitor_all_nodes_unknown(self):
        ext = noc.extensions()
        data = noc.graph(noc.inventory(), None, None, ext)
        statuses = [x["status"] for x in data["nodes"]
                    if x["id"] in noc.HA_SERVICES]
        self.assertEqual(statuses, ["unknown"] * 3)
        self.assertFalse(data["ha_service"]["available"])

    def test_systemd_monitor_is_only_s2_without_host_changes(self):
        unit = (ROOT / "servicios/systemd" /
                "netlab360-s05-ha-monitor-s2.service").read_text()
        self.assertIn("NetworkNamespacePath=/run/netns/nl360-s02-h-s2-320", unit)
        self.assertIn("User=rc-aa-ec", unit)
        self.assertIn("NoNewPrivileges=yes", unit)
        self.assertIn("ReadWritePaths=/home/rc-aa-ec/netlab360-bootstrap/s05/ha", unit)
        self.assertNotIn("User=root", unit)


if __name__ == "__main__":
    unittest.main()
