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
            routes = ("/docs", "/docs?embedded=1", "/openapi.json", "/docs/init.js",
                      "/docs/theme.css", "/docs/assets/swagger-ui.css")
            with TestClient(app, base_url="http://127.0.0.1:9140") as client:
                for route in routes:
                    self.assertEqual(client.get(route).status_code, 401)
                client.cookies.set("netlab360_session", sessions.issue(directory, "viewer")["token"])
                for route in routes:
                    self.assertEqual(client.get(route).status_code, 403)
                client.cookies.set("netlab360_session", sessions.issue(directory, "operator")["token"])
                entry = client.get("/docs", follow_redirects=False)
                self.assertEqual((entry.status_code, entry.headers["location"]), (303, "/debug?tab=docs"))
                self.assertEqual(client.get("/docs?embedded=1").status_code, 503)
                self.assertEqual(client.get("/docs?embedded=other").status_code, 400)
                shell = client.get("/debug?tab=docs")
                self.assertEqual(shell.status_code, 200)
                self.assertIn('id="swagger-host"', shell.text)
                self.assertIn("frame-src 'self'", shell.headers["content-security-policy"])
                self.assertNotIn("frame-src", client.get("/home").headers["content-security-policy"])
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
                params = schema["paths"]["/api/v1/history/{group}/{window}"]["get"]["parameters"]
                options = {item["name"]: item["schema"]["enum"] for item in params}
                self.assertEqual(set(options["group"]), {"collection", "routers", "wan", "vlan"})
                self.assertEqual(set(options["window"]), {"5m", "15m", "1h"})
                self.assertEqual(schema["paths"]["/api/v1/alerts"]["get"]["tags"], ["Observabilidad"])
                init = client.get("/docs/init.js").text
                self.assertIn('supportedSubmitMethods: ["get"]', init)
                self.assertIn("validatorUrl: null", init)
                self.assertIn("url.origin !== location.origin", init)
                self.assertEqual(client.get("/docs/assets/unknown").status_code, 404)
                with patch.object(swagger_assets, "asset", return_value=b"local"):
                    response = client.get("/docs?embedded=1")
                    self.assertEqual(response.status_code, 200)
                    self.assertIn("swagger-ui-bundle.js", response.text)
                    self.assertNotIn("https://", response.text)
                    self.assertIn("connect-src 'self'", response.headers["content-security-policy"])
                    self.assertIn("frame-ancestors 'self'", response.headers["content-security-policy"])
                    theme = client.get("/docs/theme.css")
                    self.assertEqual(theme.status_code, 200)
                    self.assertIn(".authorization__btn", theme.text)
                    self.assertIn("var(--text)", theme.text)
                    self.assertEqual(client.get("/docs/assets/swagger-ui.css").content, b"local")
                self.assertEqual(client.post("/api/v1/alerts").status_code, 405)
                self.assertEqual(client.get("/api/v1/auth/me").json()["role"], "OPERATOR")
                self.assertEqual(client.get("/healthz").status_code, 200)
                self.assertEqual(client.get("/api/v1/history/not-allowed/5m").status_code, 400)
