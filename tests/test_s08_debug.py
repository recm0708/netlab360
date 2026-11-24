"""Pruebas offline del explorador técnico sin consultas externas."""
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi", "httpx", "pydantic", "uvicorn"))
if AVAILABLE:
    from fastapi.testclient import TestClient
    package = ROOT / "servicios/consola-s08/api"
    spec = importlib.util.spec_from_file_location(
        "netlab360_s08_debug", package / "__init__.py",
        submodule_search_locations=[str(package)])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from netlab360_s08_debug import storage, security, sessions, readers
    from netlab360_s08_debug.main import create_app

BASE = "/api/v1/debug"


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0, "API con dependencias y sin root")
class DebugTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / "estado"
        storage.initialize(self.directory)
        storage.migrate(self.directory)
        for name, role in (("viewer", "VIEWER"), ("operator", "OPERATOR")):
            security.create_user(self.directory, name, "synthetic test phrase only", role)
        self.client = TestClient(create_app(self.directory), base_url="http://127.0.0.1:9140")
        self.addCleanup(self.client.close)

    def login(self, name="operator"):
        self.client.cookies.set("netlab360_session", sessions.issue(self.directory, name)["token"])

    def test_anonymous_and_viewer_denied(self):
        for path in ("/catalog", "/probe/health"):
            self.assertEqual(self.client.get(BASE+path).status_code,401)
        self.login("viewer")
        for path in ("/catalog", "/probe/health"):
            self.assertEqual(self.client.get(BASE+path).status_code,403)

    def test_catalog_fixed(self):
        self.login()
        data = self.client.get(BASE+"/catalog").json()
        self.assertEqual(len(data["endpoints"]),6)
        self.assertEqual({x["id"] for x in data["endpoints"]},
                         {"health","capabilities","sources","metrics","diagnostics","advisory"})
        self.assertTrue(all(x["method"]=="GET" and x["role"]=="OPERATOR" for x in data["endpoints"]))
        self.assertFalse(data["network_mutations_authorized"])

    def test_arbitrary_parameters_and_writes_denied(self):
        self.login()
        with patch.object(readers,"collect") as collector:
            self.assertEqual(self.client.get(BASE+"/probe/unknown").status_code,404)
            self.assertEqual(self.client.get(BASE+"/probe/sources?url=other").status_code,400)
            self.assertEqual(self.client.get(BASE+"/catalog?url=other").status_code,400)
            self.assertEqual(self.client.post(BASE+"/probe/sources").status_code,405)
            collector.assert_not_called()

    def test_projection_and_rate_limit(self):
        self.login()
        stamp = readers.now_utc()
        row = readers.observation("EXPORTER_S04","MULTISEDE","ROUTER_EXISTENCE_ONLY",
                                  stamp,"OK",stamp,details={"private":"sensitive example"})
        with patch.object(readers,"collect",return_value=[row]) as collector:
            r = self.client.get(BASE+"/probe/sources")
            self.assertEqual(r.status_code,200)
            data = r.json()
            self.assertEqual(data["records"][0]["source"],"Exportador")
            self.assertEqual(data["records"][0]["quality"],"VALID")
            self.assertNotIn("sensitive example",r.text)
            self.assertNotIn("EXPORTER_S04",r.text)
            self.assertFalse(data["network_mutations_authorized"])
            self.assertEqual(self.client.get(BASE+"/probe/sources").status_code,429)
            collector.assert_called_once()

    def test_metadata_and_bootstrap(self):
        self.login()
        response = self.client.get(BASE+"/probe/health")
        self.assertEqual(response.status_code,200)
        self.assertTrue(response.json()["summary"]["healthy"])
        self.assertEqual(response.json()["summary"]["infrastructure_state"],"UNKNOWN")
        self.assertNotIn("netlab360-s08-console", response.text)
        with TestClient(create_app(),base_url="http://127.0.0.1:9140") as client:
            self.assertEqual(client.get(BASE+"/catalog").status_code,404)

    def test_internal_error_is_sanitized(self):
        self.login()
        with patch.object(readers,"collect",side_effect=RuntimeError("private path")):
            r = self.client.get(BASE+"/probe/sources")
            self.assertEqual(r.status_code,503)
            self.assertNotIn("private path",r.text)

    def test_record_limit(self):
        self.login()
        stamp = readers.now_utc()
        row = readers.observation("EXPORTER_S04","MULTISEDE","ROUTER_EXISTENCE_ONLY",
                                  stamp,"OK",stamp)
        with patch.object(readers,"collect",return_value=[row]*129):
            self.assertEqual(self.client.get(BASE+"/probe/sources").status_code,503)


if __name__ == "__main__":
    unittest.main()
