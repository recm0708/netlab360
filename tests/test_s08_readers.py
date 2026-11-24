"""Contratos S04/S05, fallos de transporte y consulta HTTP protegida."""
from contextlib import closing
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location(
    "netlab360_s08_readers", package / "__init__.py", submodule_search_locations=[str(package)])
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_readers import readers

STAMP = "2026-01-01T00:00:00+00:00"
NOW = "2026-01-01T00:00:10+00:00"


def sample_exporter():
    return {"project":"NETLAB360","phase":"S04","source_ok":True,
            "observed_at_utc":STAMP,"topology":"active",
            "routers":{"R-HQ":1,"R-S1":1,"R-S2":1}}


def sample_noc():
    return {"project":"NETLAB360","phase":"S05","schema_version":1,
            "telemetry":{"available":True,"topology":"active","last_sample_utc":STAMP},
            "lacp":{"status":"observed","observed_at_utc":STAMP,"sites":{
                site:{"switch_members":2,"client_members":2,"status":"up"} for site in readers.SITES}},
            "sdn":{"available":True,"connected":True,"status":"connected",
                   "flow_count":26,"observed_at_utc":STAMP},
            "ha_service":{"available":True,"status":"running","active_backend":"BACKEND_HQ",
                          "selected_path":"PRINCIPAL","observed_at_utc":STAMP}}


class ReaderTests(unittest.TestCase):
    def test_exporter_scope(self):
        r = readers.exporter(sample_exporter(),NOW,"OK")[0]
        self.assertEqual((r["quality"],r["state"]),("VALID","UNKNOWN"))
        self.assertEqual(r["details"]["R-HQ"],1)

    def test_exporter_bad_identity(self):
        p = sample_exporter()
        p["project"] = "OTHER"
        self.assertEqual(readers.exporter(p,NOW,"OK")[0]["quality"],"INVALID")

    def test_exporter_mismatch(self):
        p = sample_exporter()
        p["routers"]["R-HQ"] = 0
        self.assertEqual(readers.exporter(p,NOW,"OK")[0]["quality"],"INVALID")

    def test_exporter_source_failure(self):
        p = sample_exporter()
        p["source_ok"] = False
        r = readers.exporter(p,NOW,"OK")[0]
        self.assertEqual((r["quality"],r["state"],r["details"]),("MISSING","UNKNOWN",{}))

    def test_noc_scopes(self):
        rows = readers.noc(sample_noc(),NOW,"OK")
        self.assertEqual(len(rows),6)
        self.assertEqual(rows[0]["state"],"UNKNOWN")
        self.assertTrue(all(r["quality"]=="VALID" for r in rows))
        self.assertTrue(all(r["state"]=="NORMAL" for r in rows[1:]))

    def test_noc_uses_individual_times(self):
        p = sample_noc()
        p["observed_at_utc"] = NOW
        p["lacp"]["observed_at_utc"] = "2025-12-31T23:58:00+00:00"
        rows = readers.noc(p,NOW,"OK")
        self.assertEqual([r["quality"] for r in rows],["VALID","STALE","STALE","STALE","VALID","VALID"])
        self.assertTrue(all(r["state"]=="UNKNOWN" and r["details"]=={} for r in rows[1:4]))

    def test_future_and_missing(self):
        p = sample_noc()
        p["sdn"]["observed_at_utc"] = "2026-01-01T00:01:00+00:00"
        del p["ha_service"]["observed_at_utc"]
        rows = readers.noc(p,NOW,"OK")
        self.assertEqual((rows[-2]["quality"],rows[-1]["quality"]),("FUTURE","MISSING"))
        self.assertEqual(rows[-2]["details"],{})

    def test_noc_inconsistent_lacp(self):
        p = sample_noc()
        p["lacp"]["sites"]["HQ"]["client_members"] = 1
        self.assertEqual(readers.noc(p,NOW,"OK")[1]["state"],"UNKNOWN")

    def test_noc_degradation_scoped(self):
        p = sample_noc()
        p["lacp"]["sites"]["HQ"].update(client_members=1,status="degraded")
        p["ha_service"].update(active_backend="BACKEND_S1",selected_path="RESPALDO")
        rows = readers.noc(p,NOW,"OK")
        self.assertEqual((rows[1]["state"],rows[-1]["state"]),("DEGRADED","DEGRADED"))

    def test_invalid_json(self):
        for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b'{"a":1e999}',b'[]',b'x'*(readers.MAX_BYTES+1)):
            with self.subTest(length=len(raw)):
                with self.assertRaises(ValueError):
                    readers.decode(raw)

    def test_no_arbitrary_destination(self):
        with patch.object(readers.http.client,"HTTPConnection") as connection:
            with self.assertRaises(ValueError):
                readers.fetch("http://example.invalid")
            connection.assert_not_called()

    def test_no_redirect_and_fixed_get(self):
        with patch.object(readers.http.client,"HTTPConnection") as factory:
            response = MagicMock(status=302)
            factory.return_value.getresponse.return_value.__enter__.return_value = response
            self.assertEqual(readers.fetch("NOC_S05")[2],"INVALID")
            factory.assert_called_once_with("127.0.0.1",9130,timeout=3)
            self.assertEqual(factory.return_value.request.call_args.args[:2],("GET","/api/v1/graph"))
            factory.return_value.request.assert_called_once()

    def test_transport_failure_independent(self):
        with patch.object(readers,"fetch",side_effect=[
            (None,NOW,"UNAVAILABLE"),(sample_noc(),NOW,"OK")]):
            rows = readers.collect()
        self.assertEqual(len(rows),7)
        self.assertEqual(rows[0]["quality"],"MISSING")
        self.assertTrue(all(r["quality"]=="VALID" for r in rows[1:]))
        self.assertTrue(all(r["network_mutations_authorized"] is False for r in rows))


AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("fastapi","httpx","pydantic"))
if AVAILABLE:
    from fastapi.testclient import TestClient
    from netlab360_s08_readers import storage, security, sessions
    from netlab360_s08_readers.main import create_app


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0,"API S08 sin root y con dependencias")
class ReaderHttpTests(unittest.TestCase):
    def test_protected_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)/"estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory,"viewer","synthetic test phrase only","VIEWER")
            token = sessions.issue(directory,"viewer")["token"]
            with TestClient(create_app(directory),base_url="http://127.0.0.1:9140") as client:
                with patch.object(readers,"collect",return_value=readers.noc(sample_noc(),NOW,"OK")) as collect:
                    self.assertEqual(client.get("/api/v1/sources").status_code,401)
                    collect.assert_not_called()
                    client.cookies.set("netlab360_session",token)
                    self.assertEqual(client.get("/api/v1/sources?url=x").status_code,400)
                    collect.assert_not_called()
                    response = client.get("/api/v1/sources")
                    self.assertEqual(response.status_code,200)
                    self.assertEqual(len(response.json()["observations"]),6)
                    self.assertEqual(response.json()["observations"][0]["schema"],"NETLAB360_S08_SOURCE_V1")
                    self.assertEqual(response.json()["infrastructure_state"],"UNKNOWN")
                    self.assertEqual(client.post("/api/v1/sources").status_code,405)
                    collect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
