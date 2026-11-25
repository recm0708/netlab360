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

    def test_invalid_choices(self):
        for profile, route in [("tcp-5gb", "HQ_A_S1"), ("tcp-10s", "192.168.47.2"),
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
        a["end"]["sum_received"].update(lost_packets=10, lost_percent=1)
        result = M.parse_results("udp-10s", "HQ_A_S1", a, b)
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["jitter_ms"], 0.3)
        self.assertIsNone(result["retransmissions"])

    def test_volume_incomplete(self):
        a, b = fixture(volume=90000000)
        self.assertEqual(M.parse_results("tcp-100mb", "HQ_A_S1", a, b)["status"], "INCOMPLETE")

    def test_volume_complete(self):
        a, b = fixture(volume=100000000)
        self.assertEqual(M.parse_results("tcp-100mb", "HQ_A_S1", a, b)["status"], "OK")

    def test_reject_wrong_identity(self):
        a, b = fixture()
        b["start"]["connected"][0]["remote_host"] = "192.168.47.40"
        with self.assertRaises(ValueError):
            M.parse_results("tcp-10s", "HQ_A_S1", a, b)

    def test_receiver_mismatch(self):
        a, b = fixture()
        b["intervals"][0]["sum"]["bytes"] -= 1
        with self.assertRaises(ValueError):
            M.parse_results("tcp-10s", "HQ_A_S1", a, b)

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
        a["end"]["sum_received"].update(lost_packets=1001, lost_percent=1)
        with self.assertRaises(ValueError):
            M.parse_results("udp-10s", "HQ_A_S1", a, b)


if __name__ == "__main__":
    unittest.main()
