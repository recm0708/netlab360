"""Pruebas offline del ejecutor manual; no requieren sudo ni namespaces."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock

PACKAGE = Path(__file__).resolve().parents[1] / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_probe_executor", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_probe_executor import probe_executor as M

PING = """64 bytes from 10.71.20.20: icmp_seq=1 ttl=62 time=0.072 ms
64 bytes from 10.71.20.20: icmp_seq=2 ttl=62 time=0.095 ms
64 bytes from 10.71.20.20: icmp_seq=3 ttl=62 time=0.094 ms
64 bytes from 10.71.20.20: icmp_seq=4 ttl=62 time=0.109 ms
4 packets transmitted, 4 received, 0% packet loss, time 3062ms
rtt min/avg/max/mdev = 0.072/0.092/0.109/0.013 ms
"""
TRACE = """traceroute to 10.71.20.20 (10.71.20.20), 12 hops max, 60 byte packets
 1  10.70.20.1  0.124 ms
 2  10.78.0.2  0.055 ms
 3  10.71.20.20  0.013 ms
"""
HTTP = ('{"id":"FRONTAL_HQ","service":"netlab360-s05-ha","status":"available",'
        '"active_backend":"BACKEND_HQ","active_site":"HQ","selected_path":"PRINCIPAL",'
        '"backend_status":"healthy"}\nHTTP_STATUS=200\nHTTP_TOTAL_S=0.001602\n')


class ExecutorTests(unittest.TestCase):
    def test_commands(self):
        _, dst, profile, args = M.command("test.ping.short", "HQ_A_S1")
        self.assertEqual(args[-1], dst.address)
        self.assertEqual(args[args.index("-c") + 1], "4")
        self.assertEqual(profile.timeout_s, 10)
        _, _, _, args = M.command("test.ping.long", "HQ_A_S2")
        self.assertEqual(args[args.index("-c") + 1], "20")
        _, _, _, args = M.command("test.traceroute", "HQ_A_S1")
        self.assertEqual(args[args.index("-m") + 1], "12")
        _, _, _, args = M.command("test.http", "S2_A_FRONTAL_HQ")
        self.assertEqual(args[-1], "http://10.70.20.23:8080/api/v1/service")
        self.assertNotIn("-L", args)

    def test_reject_arbitrary_and_iperf(self):
        for action, route in [("test.ping.short", "192.168.47.2"),
                              ("test.http", "HQ_A_S1"), ("test.iperf.tcp", "HQ_A_S1"),
                              ("test.ping.short;id", "HQ_A_S1")]:
            with self.assertRaises(ValueError):
                M.command(action, route)

    def test_ping_real_format(self):
        result = M.parse_ping(PING, 4, 0)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["received"], 4)
        self.assertEqual(result["rtt_p95_ms"], 0.107)

    def test_ping_no_reply(self):
        result = M.parse_ping("4 packets transmitted, 0 received, 100% packet loss", 4, 1)
        self.assertEqual(result["status"], "NO_REPLY")
        self.assertIsNone(result["rtt_p95_ms"])

    def test_ping_partial(self):
        raw = ("icmp_seq=1 ttl=62 time=0.100 ms\n"
               "4 packets transmitted, 1 received, 75% packet loss\n"
               "rtt min/avg/max/mdev = 0.100/0.100/0.100/0.000 ms")
        self.assertEqual(M.parse_ping(raw, 4, 1)["status"], "PARTIAL")

    def test_ping_inconsistent(self):
        for raw, rc in [(PING.replace("0%", "100%"), 0), (PING, 2),
                        (PING.replace("icmp_seq=4", "icmp_seq=3"), 0)]:
            with self.assertRaises(ValueError):
                M.parse_ping(raw, 4, rc)

    def test_trace(self):
        result = M.parse_trace(TRACE, "10.71.20.20", 12, 0)
        self.assertTrue(result["reached"])
        self.assertEqual(len(result["hops"]), 3)
        result = M.parse_trace("1  *\n2  10.78.0.2  0.1 ms !H", "10.71.20.20", 12, 0)
        self.assertFalse(result["reached"])
        self.assertIsNone(result["hops"][0]["rtt_ms"])

    def test_trace_malformed(self):
        with self.assertRaises(ValueError):
            M.parse_trace("2  *", "10.71.20.20", 12, 0)

    def test_http_real_format(self):
        result = M.parse_http(HTTP, 0)
        self.assertEqual(result["elapsed_ms"], 1.602)
        self.assertEqual(result["active_backend"], "BACKEND_HQ")
        self.assertEqual(result["status"], "OK")

    def test_http_failure_and_identity(self):
        self.assertEqual(M.parse_http("Unavailable\nHTTP_STATUS=503\nHTTP_TOTAL_S=0.001\n", 0)["status"],
                         "HTTP_ERROR")
        with self.assertRaises(ValueError):
            M.parse_http(HTTP.replace("FRONTAL_HQ", "OTHER"), 0)
        with self.assertRaises(ValueError):
            M.parse_http(HTTP, 7)

    @staticmethod
    def fake_reply(ns, args, seconds):
        src, dst, _, _ = M.command("test.ping.short", "HQ_A_S1")
        if args[:4] == ["/usr/sbin/ip", "-j", "-4", "addr"]:
            ep = src if ns == src.namespace else dst
            output = json.dumps([{"ifname": "eth0", "addr_info": [
                {"family": "inet", "local": ep.address, "prefixlen": 24}]}])
        elif args[:4] == ["/usr/sbin/ip", "-j", "-4", "route"]:
            output = json.dumps([{"dst": dst.address, "gateway": src.gateway,
                                  "dev": "eth0", "prefsrc": src.address}])
        else:
            output = PING
        return subprocess.CompletedProcess(args, 0, stdout=output, stderr="")

    def test_execute_valid(self):
        runner = Mock(side_effect=self.fake_reply)
        result = M.execute("test.ping.short", "HQ_A_S1", runner=runner)
        self.assertEqual(result["transport"], "OK")
        self.assertEqual(result["measurement"]["received"], 4)
        self.assertEqual(runner.call_count, 4)

    def test_identity_fails_closed(self):
        runner = Mock(return_value=subprocess.CompletedProcess([], 0, stdout="[]", stderr=""))
        result = M.execute("test.ping.short", "HQ_A_S1", runner=runner)
        self.assertEqual(result["transport"], "ERROR")
        self.assertIsNone(result["measurement"])
        self.assertEqual(runner.call_count, 1)

    def test_timeout(self):
        def reply(ns, args, seconds):
            if args[0] == "/usr/bin/ping":
                return subprocess.CompletedProcess(args, 124, stdout="", stderr="")
            return self.fake_reply(ns, args, seconds)
        result = M.execute("test.ping.short", "HQ_A_S1", runner=reply)
        self.assertEqual(result["transport"], "TIMEOUT")
        self.assertIsNone(result["measurement"])


if __name__ == "__main__":
    unittest.main()
