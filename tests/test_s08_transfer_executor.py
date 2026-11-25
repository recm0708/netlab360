"""Validación offline de perfiles, métricas y límites de transferencia."""
import importlib.util
from pathlib import Path
import sys
import unittest

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_transfer", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_transfer import transfer_executor as M


def fixture(protocol="TCP", volume=25000000):
    """Modelo mínimo del contrato JSON de ambos extremos de iPerf3."""
    def side(local, remote):
        return {"start": {"test_start": {"protocol": protocol},
                          "connected": [{"local_host": local, "remote_host": remote}]},
                "intervals": [{"sum": {"start": 0, "end": 10, "bytes": volume,
                                        "bits_per_second": 20000000}}]}
    tx = side("10.70.20.20", "10.71.20.20")
    rx = side("10.71.20.20", "10.70.20.20")
    tx["end"] = {
        "sum_sent": {"bytes": volume, "bits_per_second": 20000000, "retransmits": 0},
        "sum_received": {"bytes": volume, "bits_per_second": 20000000, "seconds": 10,
                         "lost_packets": 0, "packets": 1000, "lost_percent": 0, "jitter_ms": 0.3}}
    rx["end"] = {"sum_received": dict(tx["end"]["sum_received"])}
    return tx, rx


class TransferTests(unittest.TestCase):
    def test_duration_profiles(self):
        for profile in ("tcp-10s", "udp-10s"):
            _, _, server, client, ct, st = M.commands(profile, "HQ_A_S1")
            self.assertIn("-1", server)
            self.assertEqual(client[client.index("-t") + 1], "10")
            self.assertEqual(client[client.index("-b") + 1], "20000000")
            self.assertEqual(client[client.index("-P") + 1], "1")
            self.assertLess(ct, st)
            self.assertEqual("-u" in client, profile.startswith("udp"))

    def test_volume_profile(self):
        _, _, _, client, ct, st = M.commands("tcp-100mb", "HQ_A_S2")
        self.assertEqual(client[client.index("-n") + 1], "100000000")
        self.assertNotIn("-t", client)
        self.assertEqual((ct, st), (60, 70))

    def test_extended_volume_profiles(self):
        for name, size in (("tcp-500mb", 500000000), ("tcp-1gb", 1000000000),
                           ("tcp-2gb", 2000000000), ("tcp-5gb", 5000000000)):
            _, _, server, client, ct, st = M.commands(name, "HQ_A_S2")
            self.assertEqual(client[client.index("-n") + 1], str(size))
            self.assertEqual(client[client.index("-b") + 1], "100000000")
            self.assertEqual(client[client.index("-i") + 1], server[server.index("-i") + 1])
            self.assertLessEqual(ct / int(client[client.index("-i") + 1]), 80)
            self.assertGreater(st, ct)

    def test_invalid_choices(self):
        for profile, route in [("tcp-10gb", "HQ_A_S1"), ("tcp-10s", "192.168.47.2"),
                               ("udp-10s", "S2_A_FRONTAL_HQ"), ("tcp-10s;id", "HQ_A_S2")]:
            with self.assertRaises(ValueError):
                M.commands(profile, route)

    def test_tcp_metrics(self):
        a, b = fixture()
        result = M.parse_results("tcp-10s", "HQ_A_S1", a, b)
        self.assertEqual(result["bytes_received"], 25000000)
        self.assertEqual(result["retransmissions"], 0)
        self.assertIsNone(result["loss_pct"])
        self.assertFalse(result["content_integrity_verified"])

    def test_udp_loss(self):
        a, b = fixture("UDP")
        for document in (a, b):
            document["end"]["sum_received"].update(lost_packets=10, lost_percent=1)
        result = M.parse_results("udp-10s", "HQ_A_S1", a, b)
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["jitter_ms"], 0.3)
        self.assertIsNone(result["retransmissions"])

    def test_volume_incomplete(self):
        a, b = fixture(volume=90000000)
        self.assertEqual(M.parse_results("tcp-100mb", "HQ_A_S1", a, b)["status"], "INCOMPLETE")

    def test_volume_complete(self):
        a, b = fixture(volume=100000000)
        result = M.parse_results("tcp-100mb", "HQ_A_S1", a, b)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["volume_status"], "EXACT")
        self.assertTrue(result["volume_target_met"])

    def test_volume_overshoot_observed(self):
        a, b = fixture(volume=500020000)
        result = M.parse_results("tcp-500mb", "HQ_A_S1", a, b)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["volume_status"], "EXCEEDED")
        self.assertEqual(result["volume_excess_bytes"], 20000)
        self.assertEqual(result["volume_shortfall_bytes"], 0)
        self.assertFalse(result["content_integrity_verified"])

    def test_volume_shortfall_reported(self):
        a, b = fixture(volume=499990000)
        result = M.parse_results("tcp-500mb", "HQ_A_S1", a, b)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["volume_status"], "SHORT")
        self.assertEqual(result["volume_shortfall_bytes"], 10000)
        self.assertFalse(result["volume_target_met"])

    def test_volume_exceeded_with_unequal_endpoints(self):
        a, b = fixture(volume=500020000)
        a["end"]["sum_sent"]["bytes"] += 10000
        result = M.parse_results("tcp-500mb", "HQ_A_S1", a, b)
        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertEqual(result["volume_status"], "EXCEEDED")

    def test_reject_wrong_identity(self):
        a, b = fixture()
        b["start"]["connected"][0]["remote_host"] = "192.168.47.40"
        with self.assertRaises(ValueError):
            M.parse_results("tcp-10s", "HQ_A_S1", a, b)

    def test_receiver_mismatch(self):
        a, b = fixture()
        b["intervals"][0]["sum"]["bytes"] -= 1
        result = M.parse_results("tcp-10s", "HQ_A_S1", a, b)
        self.assertEqual(result["interval_accounting"]["status"], "DISCREPANT")
        self.assertEqual(result["interval_accounting"]["receiver_delta_bytes"], -1)
        self.assertEqual(result["bytes_received"], 25000000)

    def test_udp_observed_interval_discrepancy(self):
        a, b = fixture("UDP", volume=25000800)
        for document in (a, b):
            document["end"]["sum_received"].update(packets=20834, jitter_ms=0.0496088985908028)
        b["intervals"][0]["sum"]["bytes"] = 24999600
        result = M.parse_results("udp-10s", "HQ_A_S1", a, b)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["bytes_received"], 25000800)
        self.assertEqual(result["lost_packets"], 0)
        self.assertEqual(result["receiver_packets"], 20834)
        self.assertEqual(result["interval_accounting"]["receiver_delta_bytes"], -1200)
        self.assertEqual(result["interval_accounting"]["status"], "DISCREPANT")
        self.assertEqual(result["receiver_intervals"][0]["bytes"], 24999600)

    def test_receiver_summaries_mismatch(self):
        a, b = fixture()
        b["end"]["sum_received"]["bytes"] -= 1
        with self.assertRaisesRegex(ValueError, "RECEIVER_SUMMARIES_MISMATCH"):
            M.parse_results("tcp-10s", "HQ_A_S1", a, b)

    def test_udp_summary_packet_mismatch(self):
        a, b = fixture("UDP")
        b["end"]["sum_received"]["packets"] += 1
        with self.assertRaisesRegex(ValueError, "UDP_SUMMARIES_MISMATCH"):
            M.parse_results("udp-10s", "HQ_A_S1", a, b)

    def test_sender_interval_discrepancy(self):
        a, b = fixture()
        a["intervals"][0]["sum"]["bytes"] -= 1
        result = M.parse_results("tcp-10s", "HQ_A_S1", a, b)
        self.assertEqual(result["interval_accounting"]["sender_delta_bytes"], -1)
        self.assertEqual(result["interval_accounting"]["receiver_delta_bytes"], 0)
        self.assertEqual(result["interval_accounting"]["status"], "DISCREPANT")

    def test_invalid_metrics(self):
        for value in (float("nan"), -1, True, None):
            with self.assertRaises(ValueError):
                M.number(value)

    def test_invalid_intervals(self):
        a, _ = fixture()
        a["intervals"][0]["sum"]["end"] = 0
        with self.assertRaises(ValueError):
            M.intervals(a)

    def test_udp_inconsistent_loss(self):
        a, b = fixture("UDP")
        for document in (a, b):
            document["end"]["sum_received"].update(lost_packets=1001, lost_percent=1)
        with self.assertRaises(ValueError):
            M.parse_results("udp-10s", "HQ_A_S1", a, b)


if __name__ == "__main__":
    unittest.main()
