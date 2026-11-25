"""Pruebas HTTP y estructura documental de la interfaz base S08."""
from html.parser import HTMLParser
import importlib.util
from pathlib import Path
import os
import re
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
        self.assertEqual(set(parser.resources), {"/ui/static/styles.css", "/ui/static/app.js", "/ui/static/history.js"})
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue({"main", "refresh", "notice", "api-state", "capabilities", "observed"} <= set(parser.ids))
        self.assertFalse(parser.inline)

    def test_separate_login_resources(self):
        parser = PageParser()
        html = (UI / "login.html").read_text(encoding="utf-8")
        parser.feed(html)
        self.assertEqual(set(parser.resources),{"/ui/static/styles.css","/ui/static/app.js","/ui/static/login.js"})
        self.assertEqual(len(parser.ids),len(set(parser.ids)))
        self.assertFalse(parser.inline)
        self.assertNotIn("data-view=",html)
        self.assertNotIn('id="login-form"',(UI / "index.html").read_text(encoding="utf-8"))
        js = (UI / "static/login.js").read_text(encoding="utf-8")
        self.assertIn('location.replace("/home")',js)
        for value in ("localStorage","sessionStorage","document.cookie","innerHTML"):
            self.assertNotIn(value,js)

    def test_no_arbitrary_fetch_or_secret_storage(self):
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        for value in ("innerHTML",
                      "document.cookie", "eval(", "new Function("):
            self.assertNotIn(value, js)
        self.assertIn('credentials: "omit"', js)

    def test_dashboard_structure_and_read_only_polling(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        for key in ("coverage", "routers", "wan", "vlan", "ha", "lacp", "sdn", "inference", "advisory"):
            self.assertIn(f'id="dash-{key}"', html)
        self.assertIn('id="dashboard-auto" type="checkbox" checked', html)
        self.assertIn('id="dashboard-rows"', html)
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertIn("dashboardBatch(key,data,started)", js)
        self.assertIn("dashboardEpoch++", js)
        self.assertIn("dashboardAuto.checked&&!document.hidden&&dashboardAllowed()", js)
        self.assertIn("},15000);", js)
        self.assertIn("await debugRead(path)", js)
        self.assertIn("clearDashboard();", js)

    def test_debug_structure_and_exports(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="debug-view" hidden', html)
        for name in ("debug-run", "debug-copy", "debug-json", "debug-csv"):
            self.assertIn(f'id="{name}"', html)
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertIn('debugPaths.has(debugSelect.value)', js)
        self.assertIn('debugRead("/api/v1/debug/probe/" + key)', js)
        self.assertIn('maxBytes = 262144', js)
        self.assertIn('size > maxBytes', js)
        self.assertIn('debugEpoch++', js)
        self.assertIn('URL.revokeObjectURL(url)', js)
        self.assertIn('csvCell', js)
        self.assertIn('debugOutput.textContent = JSON.stringify(data, null, 2)', js)

    def test_vector_icons_and_scroll_layout(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('<svg class="nav-symbol"'), 15)
        self.assertEqual(html.count('class="nav-text"'), 15)
        self.assertIn('title="Diagnóstico técnico"', html)
        self.assertNotIn('<span class="nav-symbol"', html)
        css = (UI / "static/styles.css").read_text(encoding="utf-8")
        for rule in ("scrollbar-color:", "--scroll-thumb", "height: 100dvh",
                     "overflow-y: auto", "overscroll-behavior: contain",
                     "width: 24px; height: 24px",
                     ".menu-collapsed .nav-symbol { width: 24px; height: 24px; flex-basis: 24px; }"):
            self.assertIn(rule, css)

    def test_presentation_storage_is_limited(self):
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertEqual(js.count("sessionStorage."), 2)
        self.assertIn("sessionStorage.getItem(presentationKey)", js)
        self.assertIn("sessionStorage.setItem(presentationKey, JSON.stringify(presentation))", js)
        self.assertIn('const clean = {collapsed: false, menu: {expanded: 0, collapsed: 0}, pages: {}}', js)
        self.assertIn("for (const path of allowedPages)", js)
        self.assertIn('window.addEventListener("pagehide", savePresentation)', js)
        self.assertIn("restorePresentation()", js)

    def test_shared_theme_and_hamburger(self):
        for name in ("index.html", "login.html"):
            html = (UI / name).read_text(encoding="utf-8")
            self.assertEqual(html.count('id="theme-select"'), 1)
            for value in ("auto", "light", "dark"):
                self.assertIn(f'value="{value}"', html)
            self.assertIn('<script src="/ui/static/app.js"></script>', html)
        html = (UI / "index.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('class="menu-line'), 3)
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertIn('if (document.getElementById("console-shell")) initializeConsole()', js)
        css = (UI / "static/styles.css").read_text(encoding="utf-8")
        self.assertIn(':root[data-theme="light"]', css)
        self.assertIn(':root:not([data-theme])', css)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn("animation: selected-icon", css)

    def test_theme_storage_is_enum_only(self):
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertEqual(js.count("localStorage."), 2)
        self.assertIn('const themeKey = "netlab360.theme.v1"', js)
        self.assertIn('const themes = ["auto", "light", "dark"]', js)
        self.assertIn("themePreference = validTheme(value)", js)
        self.assertIn("localStorage.setItem(themeKey, themePreference)", js)
        self.assertIn("localStorage.getItem(themeKey)", js)
        self.assertIn('systemTheme.addEventListener("change"', js)

    def test_semantic_palette_contrast(self):
        css = (UI / "static/styles.css").read_text(encoding="utf-8")

        def palette(selector):
            match = re.search(re.escape(selector) + r"\s*\{([^}]+)\}", css)
            self.assertIsNotNone(match)
            return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{3,6})", match.group(1)))

        def luminance(color):
            value = color.lstrip("#")
            if len(value) == 3:
                value = "".join(channel * 2 for channel in value)
            channels = [int(value[i:i+2], 16) / 255 for i in (0, 2, 4)]
            linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                      for v in channels]
            return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))

        def contrast(first, second):
            low, high = sorted((luminance(first), luminance(second)))
            return (high + 0.05) / (low + 0.05)

        for selector in (":root", ':root[data-theme="light"]', ":root:not([data-theme])"):
            colors = palette(selector)
            for state in ("ok", "warn", "fault", "recovery", "unknown", "text", "muted"):
                for background in ("bg", "surface", "sidebar"):
                    with self.subTest(theme=selector, state=state, background=background):
                        self.assertGreaterEqual(contrast(colors[state], colors[background]), 4.5)
            self.assertGreaterEqual(contrast(colors["button-text"], colors["accent"]), 4.5)
            self.assertGreaterEqual(contrast(colors["accent"], colors["sidebar"]), 3)

    def test_solid_current_navigation(self):
        css = (UI / "static/styles.css").read_text(encoding="utf-8")
        self.assertNotIn("border-left:", css)
        self.assertNotIn("border-left-color:", css)
        self.assertIn('#navigation a.current, #navigation a[aria-current="page"]', css)
        self.assertIn("background: var(--accent);\n  color: var(--button-text);", css)
        self.assertIn("width: 48px; height: 48px;", css)
        self.assertIn('[data-state="unknown"] { color: var(--unknown); }', css)
        self.assertIn('[data-state="fault"] { color: var(--fault); }', css)

    def test_login_structure(self):
        html = (UI / "login.html").read_text(encoding="utf-8")
        for fragment in ('id="login-form" method="post"', 'id="login-fields" disabled',
                         'type="password"', 'autocomplete="current-password"',
                         'id="login-button" type="submit"'):
            self.assertIn(fragment, html)

    def test_product_labels_and_clock(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html.lower(), r"\bfase\s*\d+|\bs0[1-9]\b|laboratorio académico")
        self.assertIn("CENTRO DE OPERACIONES DE RED", html)
        self.assertIn("<dt>Fecha y hora</dt>", html)
        self.assertIn("Vencimiento de la sesión por inactividad o límite máximo.", html)
        self.assertNotIn("Expiración (Panamá)", html)
        self.assertEqual(html.count("data-view="), 15)
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertIn('timeZone: "America/Panama"', js)
        self.assertIn('hourCycle: "h12"', js)
        self.assertIn('parts.month + "/" + parts.day + "/" + parts.year', js)
        self.assertIn('parts.second + " " + parts.dayPeriod', js)
        self.assertIn("formatPanama(stamp)", js)
        self.assertIn("formatPanama(new Date(session.expiresAt * 1000))", js)

    def test_auth_client_fixed_routes(self):
        js = (UI / "static/app.js").read_text(encoding="utf-8") + (UI / "static/login.js").read_text(encoding="utf-8")
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
    from netlab360_s08_ui import storage, security, sessions
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
        r = self.client.get("/login")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers["content-type"])
        self.assertIn("NETLAB360", r.text)
        self.assertNotIn("console-shell", r.text)
        csp = r.headers["content-security-policy"]
        for part in ("script-src 'self'", "style-src 'self'", "connect-src 'self'",
                     "form-action 'none'", "frame-ancestors 'none'"):
            self.assertIn(part, csp)
        self.assertNotIn("unsafe-inline", csp)
        self.assertEqual(r.headers["cache-control"], "no-store")

    def test_assets(self):
        for path, mime in (("/ui/static/styles.css", "text/css"),
                           ("/ui/static/app.js", "text/javascript"),
                           ("/ui/static/login.js", "text/javascript")):
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

    def test_navigation_guards_and_logout(self):
        from netlab360_s08_ui.ui_http import PAGES
        self.assertEqual(len(PAGES), 15)
        for path in ("/", *PAGES):
            r = self.client.get(path, follow_redirects=False)
            self.assertEqual((r.status_code,r.headers["location"]),(303,"/login"))
        security.create_user(self.directory, "viewer", "synthetic test phrase only", "VIEWER")
        issued = sessions.issue(self.directory,"viewer")
        self.client.cookies.set("netlab360_session",issued["token"])
        for path in ("/","/login"):
            r = self.client.get(path,follow_redirects=False)
            self.assertEqual((r.status_code,r.headers["location"]),(303,"/home"))
        for path in PAGES:
            r = self.client.get(path,follow_redirects=False)
            if path == "/debug":
                self.assertEqual(r.status_code,403)
                continue
            self.assertEqual(r.status_code,200)
            self.assertIn('href="/home"',r.text)
            self.assertNotIn('id="login-form"',r.text)
            self.assertIn('id="logout"',r.text)
        self.assertEqual(self.client.get("/unknown-module").status_code,404)
        self.assertEqual(self.client.post("/api/v1/auth/logout",
            headers={"Origin":"http://127.0.0.1:9140","X-CSRF-Token":issued["csrf_token"]}).status_code,200)
        self.assertEqual(self.client.get("/home",follow_redirects=False).status_code,303)

    def test_debug_reserved_to_operator(self):
        security.create_user(self.directory, "operator", "synthetic test phrase only", "OPERATOR")
        issued = sessions.issue(self.directory, "operator")
        self.client.cookies.set("netlab360_session", issued["token"])
        for path in ("/debug", "/administration"):
            r = self.client.get(path, follow_redirects=False)
            self.assertEqual(r.status_code, 200)
            self.assertIn("Función no disponible", r.text)
            self.assertEqual(self.client.post(path).status_code, 405)

    def test_expired_session_redirects(self):
        security.create_user(self.directory,"viewer","synthetic test phrase only","VIEWER")
        issued = sessions.issue(self.directory,"viewer",now=100)
        self.client.cookies.set("netlab360_session",issued["token"])
        self.assertEqual(self.client.get("/topology",follow_redirects=False).headers["location"],"/login")

    def test_bootstrap_no_ui(self):
        with TestClient(create_app(), base_url="http://127.0.0.1:9140") as client:
            self.assertEqual(client.get("/").status_code, 404)
            self.assertEqual(client.get("/ui/static/app.js").status_code, 404)
            self.assertIs(client.get("/api/v1/capabilities").json()["frontend_enabled"], False)


if __name__ == "__main__":
    unittest.main()
