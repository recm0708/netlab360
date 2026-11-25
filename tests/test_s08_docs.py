"""Validamos documentación real, autorización y recursos locales."""
import base64
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_docs", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_docs import swagger_assets


class AssetTests(unittest.TestCase):
    def test_verified_members_only(self):
        out = io.BytesIO()
        with tarfile.open(fileobj=out, mode="w:gz") as archive:
            for name in swagger_assets.ASSETS:
                content = name.encode()
                member = tarfile.TarInfo("package/" + name)
                member.size = len(content)
                archive.addfile(member, io.BytesIO(content))
        raw = out.getvalue()
        digest = "sha512-" + base64.b64encode(hashlib.sha512(raw).digest()).decode()
        self.assertEqual(set(swagger_assets.extract(raw, digest)), set(swagger_assets.ASSETS))
        with self.assertRaises(ValueError):
            swagger_assets.extract(raw, "sha512-invalid")

    def test_no_arbitrary_destination(self):
        with self.assertRaises(ValueError):
            swagger_assets.download("https://example.invalid/file", 10)


@unittest.skipUnless(all(importlib.util.find_spec(x) for x in ("fastapi", "httpx", "pydantic"))
                     and os.geteuid() != 0, "API autenticada sin root")
class DocsTests(unittest.TestCase):
    def test_operator_only_and_actual_routes(self):
        from fastapi.testclient import TestClient
        from netlab360_s08_docs import storage, security, sessions
        from netlab360_s08_docs.main import create_app
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory, "viewer", "synthetic test phrase only", "VIEWER")
            security.create_user(directory, "operator", "synthetic test phrase only", "OPERATOR")
            app = create_app(directory)
            routes = ("/docs", "/openapi.json", "/docs/init.js", "/docs/assets/swagger-ui.css")
            with TestClient(app, base_url="http://127.0.0.1:9140") as client:
                for route in routes:
                    self.assertEqual(client.get(route).status_code, 401)
                client.cookies.set("netlab360_session", sessions.issue(directory, "viewer")["token"])
                for route in routes:
                    self.assertEqual(client.get(route).status_code, 403)
                client.cookies.set("netlab360_session", sessions.issue(directory, "operator")["token"])
                self.assertEqual(client.get("/docs").status_code, 503)
                schema = client.get("/openapi.json").json()
                self.assertIn("get", schema["paths"]["/api/v1/alerts"])
                self.assertIn("post", schema["paths"]["/api/v1/auth/login"])
                self.assertNotIn("delete", schema["paths"]["/api/v1/alerts"])
                self.assertNotIn("/docs", schema["paths"])
                self.assertNotIn("/debug", schema["paths"])
                self.assertEqual(schema["servers"], [{"url": "/"}])
                self.assertEqual(schema["paths"]["/api/v1/alerts"]["get"]["security"], [{"SessionCookie": []}])
                self.assertNotIn("security", schema["paths"]["/healthz"]["get"])
                self.assertIn("no ejecutable", schema["paths"]["/api/v1/auth/login"]["post"]["description"])
                init = client.get("/docs/init.js").text
                self.assertIn('supportedSubmitMethods: ["get"]', init)
                self.assertIn("validatorUrl: null", init)
                self.assertIn("url.origin !== location.origin", init)
                self.assertEqual(client.get("/docs/assets/unknown").status_code, 404)
                with patch.object(swagger_assets, "asset", return_value=b"local"):
                    response = client.get("/docs")
                    self.assertEqual(response.status_code, 200)
                    self.assertIn("swagger-ui-bundle.js", response.text)
                    self.assertNotIn("https://", response.text)
                    self.assertIn("connect-src 'self'", response.headers["content-security-policy"])
                    self.assertEqual(client.get("/docs/assets/swagger-ui.css").content, b"local")
                self.assertEqual(client.post("/api/v1/alerts").status_code, 405)
