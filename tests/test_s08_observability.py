"""Pruebas de procedencia, cobertura y acceso del lector integrado."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location("netlab360_s08_observation", PACKAGE / "__init__.py",
                                             submodule_search_locations=[str(PACKAGE)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_observation import observability_reader as R, slo_contract as S

END = 10000.0
AVAILABLE = all(importlib.util.find_spec(n) is not None for n in ("fastapi", "httpx", "pydantic", "uvicorn"))


def payload(metric, key="hq-s1-icmp", values=None):
    probe = S.probe(key)
    return {"status": "success", "data": {"resultType": "matrix", "result": [
        {"metric": {"__name__": metric, "job": R.JOB, "probe_id": key,
                    "instance": "127.0.0.1:9116", "laboratory": "netlab360-lab",
                    "origin": probe["origin"], "module": probe["module"]},
         "values": values if values is not None else [[END, "1"]]}]}}


def sources(metric, end):
    if metric == "probe_http_status_code":
        return "OK", {"s2-hq-http": {int(end * 1000): 200}}
    value = .001 if metric == "probe_duration_seconds" else 1
    return "OK", {key: {int((end - i * 10) * 1000): value for i in range(360)}
                  for key in S.PROBES}


class ReaderTests(unittest.TestCase):
    def test_full_windows(self):
        with patch.object(R, "fetch", side_effect=sources) as fetch:
            result = R.collect(END)
        self.assertEqual(fetch.call_count, 4)
        self.assertEqual(len(result["probes"]), 5)
        for row in result["probes"]:
            self.assertEqual(row["quality"], "VALID")
            self.assertEqual([w["probe_count"] for w in row["windows"]], [30, 90, 360])
            self.assertTrue(all(w["meets_observed_target"] is True for w in row["windows"]))
            self.assertEqual(len(row["samples"]), 360)

    def test_missing_not_healthy(self):
        with patch.object(R, "fetch", return_value=("OK", {})):
            result = R.collect(END)
        for row in result["probes"]:
            self.assertEqual(row["quality"], "ABSENT")
            self.assertIsNone(row["latest"])
            self.assertTrue(all(w["observed_availability_pct"] is None for w in row["windows"]))

    def test_transport_failure_not_zero(self):
        def fail(metric, end):
            return ("UNAVAILABLE", {}) if metric == "up" else sources(metric, end)
        with patch.object(R, "fetch", side_effect=fail):
            result = R.collect(END)
        self.assertEqual(result["transport"]["up"], "UNAVAILABLE")
        self.assertTrue(all(row["windows"] == [] and row["quality"] == "UNKNOWN"
                            for row in result["probes"]))

    def test_optional_failure_preserves_sli(self):
        def fail(metric, end):
            return ("INVALID", {}) if metric == "probe_duration_seconds" else sources(metric, end)
        with patch.object(R, "fetch", side_effect=fail):
            result = R.collect(END)
        self.assertEqual(result["probes"][0]["windows"][0]["probe_count"], 30)
        self.assertIsNone(result["probes"][0]["latest"]["duration_seconds"])

    def test_identity_and_duplicates(self):
        row = payload("up")
        self.assertEqual(R.series(row, "up", END), {"hq-s1-icmp": {10000000: 1}})
        row["data"]["result"].append(row["data"]["result"][0])
        with self.assertRaises(ValueError):
            R.series(row, "up", END)
        row = payload("up")
        row["data"]["result"][0]["metric"]["origin"] = "S2"
        with self.assertRaises(ValueError):
            R.series(row, "up", END)

    def test_invalid_duration_and_query(self):
        for raw in ("NaN", "-1", "6"):
            with self.assertRaises(ValueError):
                R.series(payload("probe_duration_seconds", values=[[END, raw]]),
                         "probe_duration_seconds", END)
        with self.assertRaises(ValueError):
            R.expression("arbitrary")

    def test_failed_scrape_and_unpaired(self):
        def data(metric, end):
            if metric == "up":
                return "OK", {"hq-s1-icmp": {10000000: 0}}
            if metric == "probe_success":
                return "OK", {}
            return "OK", {}
        with patch.object(R, "fetch", side_effect=data):
            row = R.collect(END)["probes"][0]
        self.assertEqual(row["quality"], "UNKNOWN")
        self.assertIsNone(row["latest"]["probe_success"])
        self.assertEqual(row["windows"][0]["probe_fail"], 0)
        def unpaired(metric, end):
            return ("OK", {"hq-s1-icmp": {10000000: 1}}) if metric == "probe_success" else data(metric, end)
        with patch.object(R, "fetch", side_effect=unpaired):
            self.assertEqual(R.collect(END)["probes"][0]["quality"], "INVALID")


@unittest.skipUnless(AVAILABLE and os.geteuid() != 0, "API con dependencias y usuario sin root")
class HttpTests(unittest.TestCase):
    def test_session_and_fixed_selection(self):
        from fastapi.testclient import TestClient
        from netlab360_s08_observation import security, sessions, storage
        from netlab360_s08_observation.main import create_app
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory, "viewer", "synthetic test phrase only", "VIEWER")
            with TestClient(create_app(directory), base_url="http://127.0.0.1:9140") as client:
                path = "/api/v1/observability/probes"
                self.assertEqual(client.get(path).status_code, 401)
                issued = sessions.issue(directory, "viewer")
                client.cookies.set("netlab360_session", issued["token"])
                with patch.object(R, "collect", return_value={"source": "SYNTHETIC_TEST"}) as collect:
                    self.assertEqual(client.get(path + "?query=up").status_code, 400)
                    self.assertEqual(client.get(path).json(), {"source": "SYNTHETIC_TEST"})
                    self.assertEqual(client.get(path).status_code, 429)
                    collect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
