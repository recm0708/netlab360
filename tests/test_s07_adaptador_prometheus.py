"""Fixtures sintéticos de series Prometheus; no consultas reales en CI."""
from datetime import datetime
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/s07"))
import adaptador_prometheus as m

NOW = "2026-11-24T03:00:00Z"
T = datetime.fromisoformat(NOW).timestamp()-5


def fixture():
    rows = []
    for key in sorted(m.expected_keys()):
        labels = dict(key)
        value = "1"
        if labels.get("mode") not in (None, "active"):
            value = "0"
        rows.append({"metric": {**labels, "context": "s04", "laboratory": "netlab360-lab"},
                     "values": [[T-2, value], [T, value]]})
    return {"status": "success", "data": {"resultType": "matrix", "result": rows}}


def series(payload, name, **labels):
    return next(row for row in payload["data"]["result"]
                if row["metric"]["__name__"] == name and
                all(row["metric"].get(k)==v for k,v in labels.items()))


def by_id(payload, resource):
    return next(e for e in m.project(payload, NOW) if e["resource_id"] == resource)


class PrometheusAdapterTests(unittest.TestCase):
    def test_inventory(self):
        events = m.project(fixture(), NOW)
        self.assertEqual(len(events), 23)
        self.assertTrue(all(e["quality"] == "VALID" for e in events))
        self.assertEqual(sum(e["state"] == "NORMAL" for e in events), 2)
        self.assertTrue(all(not e["network_mutations_authorized"] for e in events))

    def test_real_scrape_timestamp(self):
        self.assertEqual(by_id(fixture(), "S04-EXPORTER")["age_seconds"], 5)

    def test_no_operational_claim_from_admin(self):
        e = by_id(fixture(), "WAN-END-HQ-s1p")
        self.assertEqual(e["state"], "UNKNOWN")
        self.assertEqual(e["details"]["admin_up"], 1)
        self.assertEqual(e["details"]["timestamp_scope"], "PROMETHEUS_SCRAPE")

    def test_failed_scrape_blocks_older_metrics(self):
        p = fixture()
        series(p, "up")["values"][-1][1] = "0"
        self.assertEqual(by_id(p, "S04-EXPORTER")["state"], "FAULT")
        self.assertEqual(by_id(p, "S04-COLLECTOR")["quality"], "MISSING")
        self.assertEqual(by_id(p, "VLAN-110")["quality"], "MISSING")

    def test_collector_failure(self):
        p = fixture()
        series(p, m.PREFIX+"source_up")["values"][-1][1] = "0"
        self.assertEqual(by_id(p, "S04-COLLECTOR")["state"], "UNKNOWN")
        self.assertEqual(by_id(p, "S04-COLLECTOR")["quality"], "VALID")
        self.assertEqual(by_id(p, "MULTISEDE")["quality"], "MISSING")

    def test_mismatched_scrape(self):
        p = fixture()
        series(p, m.PREFIX+"vlan_admin_up", site="HQ", vlan="110")["values"].pop()
        self.assertEqual(by_id(p, "VLAN-110")["quality"], "MISSING")

    def test_duplicate_series(self):
        p = fixture()
        p["data"]["result"].append(series(p, "up"))
        self.assertTrue(all(e["quality"] == "MISSING" for e in m.project(p, NOW)))

    def test_stale_scrape(self):
        p = fixture()
        for row in p["data"]["result"]:
            row["values"] = [[T-90, row["values"][-1][1]]]
        self.assertTrue(all(e["quality"] == "STALE" for e in m.project(p, NOW)))

    def test_future_scrape(self):
        p = fixture()
        for row in p["data"]["result"]:
            row["values"] = [[T+10, row["values"][-1][1]]]
        self.assertTrue(all(e["quality"] == "FUTURE" for e in m.project(p, NOW)))

    def test_unknown_admin_value_preserved(self):
        p = fixture()
        series(p, m.PREFIX+"wan_admin_up", site="HQ", interface="s1p")["values"][-1][1] = "-1"
        e = by_id(p, "WAN-END-HQ-s1p")
        self.assertEqual((e["quality"], e["state"], e["details"]["admin_up"]), ("VALID", "UNKNOWN", -1))

    def test_topology_inconsistent(self):
        p = fixture()
        series(p, m.PREFIX+"topology_mode", mode="partial")["values"][-1][1] = "1"
        self.assertEqual(by_id(p, "MULTISEDE")["quality"], "MISSING")

    def test_wrong_target(self):
        p = fixture()
        series(p, "up")["metric"]["instance"] = "other"
        self.assertTrue(all(e["quality"] == "MISSING" for e in m.project(p, NOW)))

    def test_invalid_samples(self):
        for pair in ([T, "NaN"], [T, "2"], [True, "1"], [T-10, "1"]):
            p = fixture()
            series(p, "up")["values"][-1] = pair
            self.assertEqual(by_id(p, "S04-EXPORTER")["quality"], "MISSING")

    def test_unavailable_or_warning(self):
        for p in (None, {}, dict(fixture(), warnings=["partial"])):
            self.assertTrue(all(e["quality"] == "MISSING" for e in m.project(p, NOW)))

    def test_fixed_query_and_batch(self):
        self.assertIn('instance="127.0.0.1:9110"', m.QUERY)
        with patch.object(m, "read_prometheus", return_value=(fixture(), NOW, "HTTP_OK")):
            b = m.collect()
        self.assertEqual(len(b["events"]), 23)
        self.assertFalse(b["network_mutations_authorized"])


if __name__ == "__main__":
    unittest.main()
