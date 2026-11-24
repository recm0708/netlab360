"""Pruebas HTTP y estructura documental de la interfaz base S08."""
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "servicios/consola-s08/ui"
AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi", "httpx", "pydantic", "uvicorn"))


class PageParser(HTMLParser):
    """Inventario de recursos, identificadores y contenido ejecutable inline."""
    def __init__(self):
        super().__init__()
        self.ids = []
        self.resources = []
        self.inline = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "script":
            self.resources.append(attrs.get("src"))
        if tag == "link":
            self.resources.append(attrs.get("href"))
        if tag == "style" or "style" in attrs or any(k.startswith("on") for k in attrs):
            self.inline.append(tag)


class StructureTests(unittest.TestCase):
    def test_local_resources_and_unique_ids(self):
        parser = PageParser()
        parser.feed((UI / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(set(parser.resources), {"/ui/static/styles.css", "/ui/static/app.js"})
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue({"main", "refresh", "notice", "api-state", "capabilities", "observed"} <= set(parser.ids))
        self.assertFalse(parser.inline)

    def test_no_operational_fetch_or_browser_storage(self):
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        for value in ("localStorage", "sessionStorage", "innerHTML",
                      "/api/v1/sources", "/api/v1/metrics", "/api/v1/advisory"):
            self.assertNotIn(value, js)
        self.assertIn('credentials: "omit"', js)

    def test_login_structure(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        for fragment in ('id="login-form" method="post"', 'id="login-fields" disabled',
                         'type="password"', 'autocomplete="current-password"',
                         'id="session-panel" hidden', 'id="logout" type="button" disabled'):
            self.assertIn(fragment, html)

    def test_product_labels_and_clock(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html.lower(), r"\bfase\s*\d+|\bs0[1-9]\b|laboratorio académico")
        self.assertIn("Supervisión multisede", html)
        self.assertIn("<dt>Fecha y hora</dt>", html)
        self.assertIn("Vencimiento de la sesión por inactividad o límite máximo.", html)
        self.assertNotIn("Expiración (Panamá)", html)
        self.assertEqual(html.count('aria-disabled="true"'), 12)
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertIn('timeZone: "America/Panama"', js)
        self.assertIn('hourCycle: "h12"', js)
        self.assertIn('parts.month + "/" + parts.day + "/" + parts.year', js)
        self.assertIn('parts.second + " " + parts.dayPeriod', js)
        self.assertIn("formatPanama(stamp)", js)
        self.assertIn("formatPanama(new Date(session.expiresAt * 1000))", js)

    def test_auth_client_fixed_routes(self):
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        for route in ("/api/v1/auth/login", "/api/v1/auth/resume", "/api/v1/auth/logout",
                      "/api/v1/auth/activity", "/api/v1/auth/continue"):
            self.assertIn(route, js)
        self.assertIn('"X-CSRF-Token": session.csrf', js)
        self.assertIn('credentials: "same-origin"', js)
        self.assertNotIn("document.cookie", js)
        self.assertNotIn("console.log", js)
        self.assertNotIn("/api/v1/actions", js)

    def test_idle_dialog_and_resume(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        self.assertIn('<dialog id="idle-dialog"', html)
        self.assertIn('id="idle-continue"', html)
        self.assertIn('id="idle-logout"', html)
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertIn('"X-Netlab360-Resume": "1"', js)
        self.assertIn("event.isTrusted", js)
        self.assertIn("performance.now()", js)
        self.assertIn("setInterval(tick, 1000)", js)


if AVAILABLE:
    from fastapi.testclient import TestClient
    package = ROOT / "servicios/consola-s08/api"
    spec = importlib.util.spec_from_file_location(
        "netlab360_s08_ui", package / "__init__.py", submodule_search_locations=[str(package)])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from netlab360_s08_ui import storage, security
    from netlab360_s08_ui.main import create_app


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0, "API S08 con dependencias y sin root")
class UIHttpTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        directory = Path(tmp.name) / "estado"
        storage.initialize(directory)
        storage.migrate(directory)
        self.directory = directory
        self.client = TestClient(create_app(directory), base_url="http://127.0.0.1:9140")
        self.addCleanup(self.client.close)

    def test_html_and_csp(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers["content-type"])
        self.assertIn("NETLAB360", r.text)
        self.assertIn("UNKNOWN", r.text)
        csp = r.headers["content-security-policy"]
        for part in ("script-src 'self'", "style-src 'self'", "connect-src 'self'",
                     "form-action 'none'", "frame-ancestors 'none'"):
            self.assertIn(part, csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertEqual(r.headers["cache-control"], "no-store")

    def test_assets(self):
        for path, mime in (("/ui/static/styles.css", "text/css"),
                           ("/ui/static/app.js", "text/javascript")):
            r = self.client.get(path)
            self.assertEqual(r.status_code, 200)
            self.assertIn(mime, r.headers["content-type"])
            self.assertEqual(r.headers["x-content-type-options"], "nosniff")
            self.assertEqual(self.client.post(path).status_code, 405)

    def test_no_directory_exposure(self):
        for path in ("/ui/", "/ui/static/", "/ui/static/main.py", "/ui/index.html",
                     "/ui/static/%2e%2e/%2e%2e/api/security.py", "/.git/config"):
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_private_api_stays_protected(self):
        self.assertEqual(self.client.get("/api/v1/sources").status_code, 401)
        r = self.client.get("/healthz")
        self.assertEqual(r.headers["content-security-policy"],
                         "default-src 'none'; frame-ancestors 'none'")
        self.assertIs(self.client.get("/api/v1/capabilities").json()["frontend_enabled"], True)

    def test_login_logout_in_same_origin(self):
        security.create_user(self.directory, "viewer", "synthetic test phrase only", "VIEWER")
        origin = {"Origin": "http://127.0.0.1:9140"}
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 401)
        result = self.client.post("/api/v1/auth/login", headers=origin,
                                  json={"username": "viewer", "password": "synthetic test phrase only"})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["role"], "VIEWER")
        self.assertIn("HttpOnly", result.headers["set-cookie"])
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/logout", headers=origin).status_code, 403)
        self.assertEqual(self.client.post("/api/v1/auth/logout",
                         headers={**origin, "X-CSRF-Token": result.json()["csrf_token"]}).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/auth/me").status_code, 401)

    def test_bootstrap_no_ui(self):
        with TestClient(create_app(), base_url="http://127.0.0.1:9140") as client:
            self.assertEqual(client.get("/").status_code, 404)
            self.assertEqual(client.get("/ui/static/app.js").status_code, 404)
            self.assertIs(client.get("/api/v1/capabilities").json()["frontend_enabled"], False)


if __name__ == "__main__":
    unittest.main()
