"""Pruebas offline NOC S04: fuentes verdaderas, estado stale y fallos explícitos."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "s04noc", ROOT / "servicios/noc-s04/app.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

NOW = datetime(2026, 10, 27, 3, 15, tzinfo=timezone.utc)


def snapshot(age=1, source_ok=True, topology="offline"):
    return {"source_ok": source_ok, "topology": topology,
            "observed_at_utc": (NOW - timedelta(seconds=age)).isoformat(),
            "sites": {s: {"running": 0, "wan": {}, "vlans": {}} for s in mod.EXPECTED_SITES}}


def targets(health="up"):
    return {"status": "success", "data": {"activeTargets": [
        {"health": health, "labels": {"job": mod.JOB}}
    ]}}


def alerts(items=None):
    return {"status": "success", "data": {"alerts": [] if items is None else items}}


class NocOfflineTests(unittest.TestCase):
    def test_fresh_offline_topology_is_not_a_fault(self):
        r = mod.normalize_telemetry(snapshot(), NOW)
        self.assertTrue(r["available"] and r["source_ok"] and r["fresh"])
        self.assertEqual(r["topology"], "offline")
        self.assertEqual(len(r["sites"]), 3)

    def test_stale_source_is_unknown_and_hides_old_sites(self):
        r = mod.normalize_telemetry(snapshot(age=200), NOW)
        self.assertFalse(r["fresh"])
        self.assertEqual(r["topology"], "unknown")
        self.assertFalse(r["sites"])

    def test_bad_timestamp_is_not_live(self):
        sample = snapshot()
        sample["observed_at_utc"] = "not a timestamp"
        r = mod.normalize_telemetry(sample, NOW)
        self.assertFalse(r["fresh"])
        self.assertEqual(r["topology"], "unknown")

    def test_unavailable_source_is_unknown(self):
        r = mod.normalize_telemetry(None, NOW)
        self.assertFalse(r["available"])
        self.assertEqual(r["topology"], "unknown")

    def test_partial_sot_not_presented_as_healthy(self):
        sample = snapshot()
        del sample["sites"]["S2"]
        r = mod.normalize_telemetry(sample, NOW)
        self.assertEqual(r["topology"], "unknown")
        self.assertEqual(r["sites"], {})

    def test_no_alerts_when_prometheus_confirms_empty(self):
        p = mod.normalize_prometheus(targets(), alerts())
        self.assertTrue(p["available"] and p["alerts_known"])
        self.assertEqual(p["scrape"], "up")
        self.assertEqual(p["alerts"], [])

    def test_prometheus_failure_is_unknown_not_zero_alerts(self):
        p = mod.normalize_prometheus(None, None, "ConnectionRefused")
        self.assertFalse(p["available"] or p["alerts_known"])
        self.assertEqual(p["scrape"], "unknown")

    def test_prometheus_alert_is_visible_with_timestamp(self):
        event = {"state": "firing",
                 "labels": {"alertname": "NETLAB360S04WANAdminDown", "site": "HQ"},
                 "activeAt": "2026-10-27T03:14:00Z"}
        p = mod.normalize_prometheus(targets(), alerts([event]))
        self.assertEqual(p["alerts"][0]["activeAt"], event["activeAt"])

    def test_aggregated_overview_uses_two_local_sources_only(self):
        urls = []
        def reader(url):
            urls.append(url)
            if url == mod.EXPORTER + "/api/v1/state":
                return snapshot()
            if url == mod.PROMETHEUS + "/api/v1/targets":
                return targets()
            if url == mod.PROMETHEUS + "/api/v1/alerts":
                return alerts()
            raise AssertionError(url)
        out = mod.overview(reader, NOW)
        self.assertEqual(out["telemetry"]["topology"], "offline")
        self.assertEqual(out["prometheus"]["scrape"], "up")
        self.assertEqual(len(urls), 3)
        self.assertTrue(all(url.startswith("http://127.0.0.1:") for url in urls))

    def test_one_source_failure_does_not_falsify_other(self):
        def reader(url):
            if url.startswith(mod.EXPORTER):
                return snapshot()
            raise ConnectionRefusedError("prometheus disconnected")
        out = mod.overview(reader, NOW)
        self.assertEqual(out["telemetry"]["topology"], "offline")
        self.assertFalse(out["prometheus"]["alerts_known"])

    def test_management_guard(self):
        def runner(argv, **kwargs):
            value = "ens33 UP 192.168.47.40/24" if argv[-1] == "ens33" \
                else "default via 192.168.47.2 dev ens33"
            return subprocess.CompletedProcess(argv, 0, value, "")
        mod.local_guard(runner, hostname="netlab360-lab")
        with self.assertRaises(RuntimeError):
            mod.local_guard(runner, hostname="not-our-host")

    def test_dashboard_has_central_and_three_site_views(self):
        for label in ('data-site="ALL"', 'data-site="HQ"',
                      'data-site="S1"', 'data-site="S2"'):
            self.assertIn(label, mod.PAGE)
        self.assertIn("/api/v1/overview", mod.PAGE)
        self.assertIn("UNKNOWN", mod.PAGE)


if __name__ == "__main__":
    unittest.main()
