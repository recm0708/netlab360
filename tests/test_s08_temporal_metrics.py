"""Pruebas de contratos temporales; los fixtures no constituyen mediciones reales."""
import importlib.util
from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_temporal_test", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_temporal_test import iperf_native as I, slo_window as W


class NativeTests(unittest.TestCase):
    def stream(self):
        stream = I.NativeStream("tcp-10s", "HQ_A_S1", "sender")
        stream.feed({"event": "start", "data": {"test_start": {"protocol": "TCP"},
                     "connected": [{"local_host": "10.70.20.20", "remote_host": "10.71.20.20"}]}})
        return stream

    def interval(self, start, end, size):
        return {"event": "interval", "data": {"sum": {"start": start, "end": end,
                "bytes": size, "bits_per_second": size * 8 / (end - start)}}}

    def test_observed_progress(self):
        s = self.stream()
        self.assertEqual(s.feed(self.interval(0, 1, 100))["bytes"], 100)
        row = s.feed(self.interval(1, 2, 0))
        self.assertEqual(row["bytes"], 100)
        self.assertEqual(row["mbps"], 0)
        s.feed({"event": "end", "data": {}})
        self.assertEqual(len(s.finish()["intervals"]), 2)

    def test_reject_incomplete(self):
        s = self.stream()
        s.feed(self.interval(0, 1, 100))
        with self.assertRaises(ValueError):
            s.finish()

    def test_reject_overlapping(self):
        s = self.stream()
        s.feed(self.interval(0, 1, 100))
        with self.assertRaises(ValueError):
            s.feed(self.interval(0.5, 1.5, 100))

    def test_reject_wrong_peer(self):
        s = I.NativeStream("tcp-10s", "HQ_A_S1", "receiver")
        with self.assertRaises(ValueError):
            s.feed({"event": "start", "data": {"test_start": {"protocol": "TCP"},
                    "connected": [{"local_host": "10.70.20.20", "remote_host": "10.71.20.20"}]}})

    def test_reject_post_end(self):
        s = self.stream()
        s.feed(self.interval(0, 1, 100))
        s.feed({"event": "end", "data": {}})
        with self.assertRaises(ValueError):
            s.feed(self.interval(1, 2, 100))


class WindowTests(unittest.TestCase):
    def setUp(self):
        self.end = 10000
        self.up = [[self.end - i * 10, "1"] for i in range(30)]

    def evaluate(self, up, probes):
        return W.evaluate("hq-s1-icmp", 5, self.end, up, probes)

    def test_full(self):
        r = self.evaluate(self.up, self.up)
        self.assertEqual(r["quality"], "OBSERVED")
        self.assertTrue(r["meets_observed_target"])

    def test_equal_count_with_gap(self):
        values = self.up[1:] + [[self.end - 11, "1"]]
        r = self.evaluate(values, values)
        self.assertEqual(r["quality"], "PARTIAL")
        self.assertEqual(r["missing_slots"], 1)
        self.assertEqual(r["duplicate_slots"], 1)
        self.assertIsNone(r["meets_observed_target"])

    def test_unpaired(self):
        with self.assertRaises(ValueError):
            self.evaluate(self.up[1:], self.up)

    def test_failed_scrape_is_not_probe_failure(self):
        up = [[self.end, "0"], *self.up[1:]]
        r = self.evaluate(up, self.up[1:])
        self.assertEqual(r["probe_fail"], 0)
        self.assertEqual(r["unobserved_scrapes"], 1)
        self.assertIsNone(r["meets_observed_target"])

    def test_measured_probe_failure(self):
        probe = [[self.end, "0"], *self.up[1:]]
        r = self.evaluate(self.up, probe)
        self.assertEqual(r["probe_fail"], 1)
        self.assertFalse(r["meets_observed_target"])

    def test_absent_and_duplicates(self):
        self.assertEqual(self.evaluate([], [])["quality"], "ABSENT")
        with self.assertRaises(ValueError):
            self.evaluate(self.up + [self.up[0]], self.up)


if __name__ == "__main__":
    unittest.main()
