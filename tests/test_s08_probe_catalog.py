"""Validar catálogo y límites sin iniciar procesos ni tocar la red."""
import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api/probe_catalog.py"
SPEC = importlib.util.spec_from_file_location("netlab360_probe_catalog", PATH)
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


class ProbeCatalogTests(unittest.TestCase):
    def test_verified_endpoints(self):
        self.assertEqual(set(MOD.ENDPOINTS), {"HQ", "S1", "S2", "FRONTAL_HQ"})
        self.assertEqual({e.address for e in MOD.ENDPOINTS.values()},
                         {"10.70.20.20", "10.71.20.20", "10.72.20.20", "10.70.20.23"})
        self.assertTrue(all(e.interface == "eth0" for e in MOD.ENDPOINTS.values()))

    def test_limits(self):
        self.assertEqual(MOD.PROFILES["test.ping.short"].packets, 4)
        self.assertEqual(MOD.PROFILES["test.ping.long"].packets, 20)
        self.assertEqual(MOD.PROFILES["test.traceroute"].hops, 12)
        self.assertEqual(MOD.PROFILES["test.http"].timeout_s, 5)
        for action in ("test.iperf.tcp", "test.iperf.udp"):
            profile = MOD.PROFILES[action]
            self.assertEqual(profile.duration_s, 10)
            self.assertEqual(profile.bitrate_bps, 20_000_000)
        self.assertEqual(MOD.MAX_CONCURRENT_ACTIVE_TESTS, 1)

    def test_allowed_combinations(self):
        rows = MOD.catalog()
        self.assertEqual(len(rows), 14)
        self.assertTrue(all(r["execution_enabled"] is False for r in rows))
        source, destination, _ = MOD.resolve("test.http", "S2_A_FRONTAL_HQ")
        self.assertEqual(source.address, "10.72.20.20")
        self.assertEqual(destination.address, "10.70.20.23")
        self.assertEqual(MOD.HTTP_PORT, 8080)
        self.assertEqual(MOD.IPERF_PORT, 5201)

    def test_invalid_input(self):
        for action, route in [
            ("test.ping.short", "192.168.47.2"), ("test.http", "HQ_A_S1"),
            ("test.iperf.tcp", "S2_A_FRONTAL_HQ"), ("test.iperf.udp", "S2_A_FRONTAL_HQ"),
            ("test.ping.short; id", "HQ_A_S1"), ("test.http", "http://example.org"),
            (None, "HQ_A_S1"), ("test.ping.short", []),
        ]:
            with self.subTest(action=action, route=route):
                with self.assertRaises(ValueError):
                    MOD.resolve(action, route)

    def test_projection_is_independent(self):
        rows = MOD.catalog()
        rows[0]["source"]["address"] = "192.168.47.40"
        self.assertEqual(MOD.catalog()[0]["source"]["address"], "10.70.20.20")


if __name__ == "__main__":
    unittest.main()
