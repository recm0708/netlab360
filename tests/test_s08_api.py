"""Pruebas del arranque HTTP S08 sin infraestructura ni privilegios."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi", "pydantic", "httpx", "uvicorn"))

if AVAILABLE:
    from fastapi.testclient import TestClient
    from pydantic import ValidationError
    # Importar el paquete con un nombre exclusivo para no alterar sys.path.
    package = ROOT / "servicios/consola-s08/api"
    spec = importlib.util.spec_from_file_location(
        "netlab360_s08_api", package / "__init__.py",
        submodule_search_locations=[str(package)])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from netlab360_s08_api.main import create_app, main
    from netlab360_s08_api.models import Capabilities, Health


@unittest.skipUnless(AVAILABLE, "Ejecutar API en el job S08 con dependencias científicas")
class BootstrapApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app, base_url="http://127.0.0.1:9140")
        self.addCleanup(self.client.close)

    def test_health(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["service"], "netlab360-s08-console")
        self.assertIs(body["healthy"], True)
        self.assertEqual(body["infrastructure_state"], "UNKNOWN")
        self.assertIs(body["network_mutations_authorized"], False)

    def test_health_timestamp(self):
        body = self.client.get("/healthz").json()
        stamp = datetime.fromisoformat(body["generated_at_utc"])
        self.assertEqual(stamp.utcoffset().total_seconds(), 0)
        self.assertLess(abs((datetime.now(timezone.utc) - stamp).total_seconds()), 10)

    def test_capabilities(self):
        response = self.client.get("/api/v1/capabilities")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIs(body["health_available"], True)
        self.assertEqual(body["mode"], "BOOTSTRAP_READ_ONLY")
        for key in ("source_readers_enabled", "persistence_enabled",
                    "authentication_enabled", "frontend_enabled",
                    "diagnostics_enabled", "network_mutations_authorized"):
            self.assertIs(body[key], False)

    def test_public_routes_only(self):
        self.assertEqual({(r.path, frozenset(r.methods)) for r in self.app.routes},
                         {("/healthz", frozenset({"GET"})),
                          ("/api/v1/capabilities", frozenset({"GET"}))})

    def test_mutating_methods_denied(self):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            for path in ("/healthz", "/api/v1/capabilities"):
                with self.subTest(method=method, path=path):
                    r = self.client.request(method, path, json={"command": "denied"})
                    self.assertEqual(r.status_code, 405)
                    self.assertEqual(r.json()["error"], "METHOD_NOT_ALLOWED")
                    self.assertIs(r.json()["network_mutations_authorized"], False)

    def test_unimplemented_routes(self):
        for path in ("/", "/docs", "/redoc", "/openapi.json", "/api/v1/sources",
                     "/api/v1/rfcs", "/api/v1/jobs"):
            with self.subTest(path=path):
                r = self.client.get(path)
                self.assertEqual(r.status_code, 404)
                self.assertEqual(r.json()["error"], "NOT_FOUND")

    def test_host_rejected(self):
        r = self.client.get("/healthz", headers={"Host": "untrusted.invalid"})
        self.assertEqual(r.status_code, 400)

    def test_localhost_allowed(self):
        r = self.client.get("/healthz", headers={"Host": "localhost:9140"})
        self.assertEqual(r.status_code, 200)

    def test_no_cors(self):
        r = self.client.get("/healthz", headers={"Origin": "https://untrusted.invalid"})
        self.assertNotIn("access-control-allow-origin", r.headers)

    def test_no_cache_and_security_headers(self):
        r = self.client.get("/healthz")
        self.assertEqual(r.headers["cache-control"], "no-store")
        self.assertEqual(r.headers["x-content-type-options"], "nosniff")
        self.assertEqual(r.headers["referrer-policy"], "no-referrer")
        self.assertIn("frame-ancestors 'none'", r.headers["content-security-policy"])

    def test_error_does_not_echo_path(self):
        r = self.client.get("/private-example")
        self.assertEqual(r.status_code, 404)
        self.assertNotIn("private-example", r.text)

    def test_strict_models(self):
        with self.assertRaises(ValidationError):
            Health(generated_at_utc=datetime.now(timezone.utc), infrastructure_state="NORMAL")
        with self.assertRaises(ValidationError):
            Capabilities(network_mutations_authorized=True)
        with self.assertRaises(ValidationError):
            Capabilities(command="arbitrary")

    def test_root_refused(self):
        with patch("netlab360_s08_api.main.os.geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "S08_ROOT_FORBIDDEN"):
                create_app()

    def test_launcher_fixed_loopback(self):
        with patch("uvicorn.run") as run:
            main()
        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args.kwargs["host"], "127.0.0.1")
        self.assertEqual(run.call_args.kwargs["port"], 9140)
        self.assertIs(run.call_args.kwargs["proxy_headers"], False)
        self.assertIs(run.call_args.kwargs["reload"], False)


if __name__ == "__main__":
    unittest.main()
