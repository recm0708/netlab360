"""Pruebas offline del diario NOC S04: no alteran Docker, WAN, ni servicios."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "servicios/noc-s04/historial_s04.py"
spec = importlib.util.spec_from_file_location("nl360hist_test", SRC)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def state(alerts=(), good=True, scrape="up", stamp="2026-10-27T08:00:00Z"):
    return {
        "collected_at_utc": stamp,
        "telemetry": {"source_ok": good, "fresh": good},
        "prometheus": {"available": True, "alerts_known": True,
                       "scrape": scrape, "alerts": list(alerts)},
    }


def alarm(mode):
    return {"state": mode, "activeAt": "2026-10-27T07:59:00Z",
            "labels": {"alertname": "NETLAB360S04WANAdminDown", "site": "HQ",
                       "interface": "s1p", "severity": "warning"}}


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "historial" / "incidentes.sqlite3"
        mod.initialize(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_pending_firing_resolved_and_dedup(self):
        self.assertEqual(mod.record(state([alarm("pending")]), self.path), 1)
        self.assertEqual(mod.record(state([alarm("pending")]), self.path), 0)
        self.assertEqual(mod.record(state([alarm("firing")]), self.path), 1)
        self.assertEqual(mod.record(state([]), self.path), 1)
        got = mod.events("HQ", path=self.path)
        self.assertEqual([x["state"] for x in got], ["resolved", "firing", "pending"])
        self.assertTrue(all(x["source"] == "prometheus_active_alerts" for x in got))

    def test_unknown_does_not_fake_resolved(self):
        mod.record(state([alarm("firing")]), self.path)
        bad = state([], good=False, scrape="down")
        self.assertEqual(mod.record(bad, self.path), 0)
        self.assertEqual(mod.events("HQ", path=self.path)[0]["state"], "firing")
        self.assertEqual(mod.record(state([]), self.path), 1)
        self.assertEqual(mod.events("HQ", path=self.path)[0]["state"], "resolved")

    def test_prometheus_unavailable_does_not_change_history(self):
        mod.record(state([alarm("pending")]), self.path)
        bad = state()
        bad["prometheus"]["available"] = False
        bad["prometheus"]["alerts_known"] = False
        self.assertEqual(mod.record(bad, self.path), 0)
        self.assertEqual(len(mod.events(path=self.path)), 1)

    def test_db_is_durable_without_duplicate(self):
        mod.record(state([alarm("firing")]), self.path)
        mod.initialize(self.path)
        self.assertEqual(mod.record(state([alarm("firing")]), self.path), 0)
        self.assertEqual(len(mod.events(path=self.path)), 1)

    def test_site_filters_and_csv(self):
        mod.record(state([alarm("firing")]), self.path)
        self.assertEqual(len(mod.events("S1", path=self.path)), 0)
        records = mod.events("HQ", path=self.path)
        exported = mod.as_csv(records).decode("utf-8")
        self.assertIn("NETLAB360S04WANAdminDown", exported)
        self.assertIn("observed_at_utc", exported)
        self.assertIn("prometheus_active_alerts", exported)

    def test_invalid_filters(self):
        for site in ("S4", "HQ' OR 1=1", ""):
            with self.assertRaises(ValueError):
                mod.events(site=site, path=self.path)
        with self.assertRaises(ValueError):
            mod.events(limit=500, path=self.path)

    def test_unverified_g3_log_refused(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            mod.parse_verified_g3(b"S04_G3_RESULTADO=OK")

    def test_nonexistent_original_g3_log_refused(self):
        with self.assertRaises(ValueError):
            mod.import_g3(path=Path(self.temp.name) / "not-there.log", db_path=self.path)


if __name__ == "__main__":
    unittest.main()
