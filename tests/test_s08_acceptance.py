"""Aceptación del inventario de capacidades y aislamiento entre lectores S08."""
import asyncio
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from threading import Event

ROOT = Path(__file__).resolve().parents[1]
AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi","httpx","pydantic","uvicorn"))
if AVAILABLE:
    import httpx
    package = ROOT / "servicios/consola-s08/api"
    spec = importlib.util.spec_from_file_location(
        "netlab360_s08_acceptance", package / "__init__.py",
        submodule_search_locations=[str(package)])
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from netlab360_s08_acceptance import storage, security, sessions, readers, prometheus_reader
    from netlab360_s08_acceptance.main import create_app

ORIGIN = "http://127.0.0.1:9140"
ROUTES = ("/api/v1/sources", "/api/v1/metrics", "/api/v1/diagnostics", "/api/v1/advisory")


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0,"API S08 con dependencias y sin root")
class AcceptanceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        directory = Path(temp.name)/"estado"
        storage.initialize(directory)
        storage.migrate(directory)
        security.create_user(directory,"viewer","synthetic test phrase only","VIEWER")
        self.token = sessions.issue(directory,"viewer")["token"]
        self.app = create_app(directory)
        self.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url=ORIGIN)
        self.addAsyncCleanup(self.client.aclose)

    async def test_capabilities_match_routes(self):
        caps = (await self.client.get("/api/v1/capabilities")).json()
        for key in ("source_readers_enabled","diagnostics_enabled","advisory_enabled",
                    "authentication_enabled","persistence_enabled"):
            self.assertIs(caps[key],True)
        self.assertIs(caps["network_mutations_authorized"],False)
        self.assertIs(caps["frontend_enabled"],True)
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=create_app()),
                                     base_url=ORIGIN) as bootstrap:
            caps = (await bootstrap.get("/api/v1/capabilities")).json()
            for key in ("source_readers_enabled","diagnostics_enabled","advisory_enabled","frontend_enabled"):
                self.assertIs(caps[key],False)
            for path in ROUTES:
                self.assertEqual((await bootstrap.get(path)).status_code,404)

    async def test_every_reader_requires_session(self):
        for path in ROUTES:
            self.assertEqual((await self.client.get(path)).status_code,401)
        self.client.cookies.set("netlab360_session",self.token)
        for path in ROUTES:
            self.assertEqual((await self.client.get(path+"?url=other")).status_code,400)
            self.assertEqual((await self.client.post(path)).status_code,405)

    async def test_independent_acquisition_limits(self):
        self.client.cookies.set("netlab360_session",self.token)
        entered, release = Event(), Event()
        def slow():
            entered.set()
            if not release.wait(5):
                raise RuntimeError("TEST_TIMEOUT")
            return []
        with patch.object(readers,"collect",side_effect=slow), \
                patch.object(prometheus_reader,"collect",return_value=[]) as metric:
            task = asyncio.create_task(self.client.get(ROUTES[0]))
            try:
                self.assertTrue(await asyncio.to_thread(entered.wait,2))
                self.assertEqual((await self.client.get(ROUTES[0])).status_code,429)
                other = await asyncio.wait_for(self.client.get(ROUTES[1]),2)
                self.assertEqual(other.status_code,200)
                metric.assert_called_once()
            finally:
                release.set()
                response = await task
            self.assertEqual(response.status_code,200)


if __name__ == "__main__":
    unittest.main()
