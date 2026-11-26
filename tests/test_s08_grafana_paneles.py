"""Pruebas del contrato de ejecución de paneles y contraste de data frames."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/s08"))
import ejecutar_paneles_grafana as G


def frame(stamps, values, probe="hq-s1-icmp"):
    return {"schema": {"fields": [
        {"type": "time"}, {"type": "number", "labels": {
            "job": "netlab360-s08-blackbox", "probe_id": probe}}]},
        "data": {"values": [stamps, values]}}


class PanelTests(unittest.TestCase):
    def test_frames(self):
        actual = G.frame_points({"frames": [frame([10000, 20000], [1, 0])]})
        self.assertEqual(actual, {("hq-s1-icmp", 10): 1, ("hq-s1-icmp", 20): 0})

    def test_vector(self):
        actual = G.prom_points({"status": "success", "data": {
            "resultType": "vector", "result": [{"metric": {
                "job": "netlab360-s08-blackbox", "probe_id": "hq-s1-icmp"},
                "value": [10, "1"]}]}}, True)
        self.assertEqual(actual, {("hq-s1-icmp", 10): 1})

    def test_duplicate(self):
        with self.assertRaises(AssertionError):
            G.frame_points({"frames": [frame([10000, 10000], [1, 1])]})

    def test_invalid_values(self):
        for value in (None, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(AssertionError):
                G.frame_points({"frames": [frame([10000], [value])]})

    def test_unknown_probe(self):
        with self.assertRaises(ValueError):
            G.frame_points({"frames": [frame([10000], [1], "unknown")]})

    def test_missing_and_mismatched_points(self):
        expected = {("hq-s1-icmp", 10): 1}
        G.compare_points(expected, expected, ["hq-s1-icmp"], [10])
        for actual in ({}, {("hq-s1-icmp", 10): 0}, {("hq-s1-icmp", 20): 1}):
            with self.assertRaises(AssertionError):
                G.compare_points(actual, expected, ["hq-s1-icmp"], [10])


if __name__ == "__main__":
    unittest.main()
