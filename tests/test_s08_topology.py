"""Verificamos límites, inventario y vigencia del grafo integrado."""
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import os
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "servicios/consola-s08/api"
SPEC = importlib.util.spec_from_file_location(
    "netlab360_s08_topology", PACKAGE / "__init__.py",
    submodule_search_locations=[str(PACKAGE)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from netlab360_s08_topology import topology_reader as reader

NOW = "2026-11-24T23:00:00+00:00"


def fixture():
    nodes = []
    for key, (site, kind) in reader.NODES.items():
        row = dict(id=key, site=site, type=kind, label=key, detail="Inventario",
                   status="running" if kind in ("router", "server") else "namespace-present")
        if kind == "host":
            row.update(vlan=int(key.rsplit("-", 1)[1]), gateway="10.70.10.1", vlan_admin="admin-up")
        if kind == "server":
            row["application_selection"] = "unknown"
        nodes.append(row)
    links = []
    for key, (a, b, kind) in reader.LINKS.items():
        row = dict(id=key, type=kind, role="trunk", detail="Inventario",
                   status="unknown", **{"from": a, "to": b})
        if kind == "wan":
            row.update(status="admin-up", role="primary" if "PRIMARIA" in key else "backup",
                       a="10.78.0.1/30", b="10.78.0.2/30", route_selection="standby")
        if kind == "redundancy":
            row["application_selection"] = "unknown"
        links.append(row)
    return dict(project="NETLAB360", phase="S05", schema_version=1,
                observed_at_utc=NOW, nodes=nodes, links=links, source_warnings=[],
                namespaces_observable=True,
                telemetry=dict(available=True, last_sample_utc=NOW),
                routing=dict(available=True, traffic_measured=False),
                ha_service=dict(available=True, observed_at_utc=NOW))


class TopologyTests(unittest.TestCase):
    def test_inventory_and_scope(self):
        result = reader.project(fixture(), NOW, "OK")
        self.assertEqual(len(result["nodes"]), 18)
        self.assertEqual(len(result["links"]), 21)
        self.assertEqual(result["graph"]["quality"], "VALID")
        self.assertIs(result["network_mutations_authorized"], False)
        self.assertIs(result["traffic_measured"], False)
        self.assertIs(result["routing_available"], True)

    def test_stale_telemetry_independent_http(self):
        data = fixture()
        data["telemetry"]["last_sample_utc"] = "2026-11-24T22:58:00+00:00"
        result = reader.project(data, NOW, "OK")
        self.assertEqual(result["telemetry"]["quality"], "STALE")
        self.assertIs(result["routing_available"], False)
        self.assertEqual(next(x for x in result["nodes"] if x["id"] == "R-HQ")["status"], "unknown")
        self.assertEqual(next(x for x in result["nodes"] if x["id"] == "FRONTAL_HQ")["status"], "running")

    def test_stale_generation(self):
        data = fixture()
        data["observed_at_utc"] = "2026-11-24T22:58:00+00:00"
        result = reader.project(data, NOW, "OK")
        self.assertTrue(all(row["status"] == "unknown" for row in result["nodes"] + result["links"]))

    def test_invalid_link_and_duplicate(self):
        for change in ("link", "duplicate"):
            data = fixture()
            if change == "link":
                data["links"][0]["to"] = "R-S1"
            else:
                data["nodes"][1] = data["nodes"][0]
            result = reader.project(data, NOW, "OK")
            self.assertEqual(result["nodes"], [])
            self.assertEqual(result["graph"]["quality"], "INVALID")

    def test_fib_gateway(self):
        data = fixture()
        row = next(x for x in data["links"] if x["id"] == "WAN-PRIMARIA-HQ-S1")
        row.update(route_selection="selected", route_gateway="10.78.0.2")
        result = reader.project(data, NOW, "OK")
        self.assertEqual(next(x for x in result["links"] if x["id"] == row["id"])["route_selection"], "selected")
        row["route_gateway"] = "10.78.0.6"
        self.assertEqual(reader.project(data, NOW, "OK")["graph"]["quality"], "INVALID")

    def test_inconsistent_role_rejected(self):
        data = fixture()
        row = next(x for x in data["links"] if x["id"] == "WAN-PRIMARIA-HQ-S1")
        row["role"] = "backup"
        self.assertEqual(reader.project(data, NOW, "OK")["graph"]["quality"], "INVALID")

    def test_fixed_source(self):
        with patch.object(reader.readers, "fetch", return_value=(None, NOW, "UNAVAILABLE")) as fetch:
            result = reader.collect()
            fetch.assert_called_once_with("NOC_S05")
            self.assertEqual(result["graph"]["quality"], "MISSING")


AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi", "httpx", "pydantic", "uvicorn"))


@unittest.skipUnless(AVAILABLE and os.geteuid() != 0, "API sin root")
class TopologyHttpTests(unittest.TestCase):
    def test_auth_and_fixed_read(self):
        from fastapi.testclient import TestClient
        from netlab360_s08_topology import storage, security, sessions
        from netlab360_s08_topology.main import create_app
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory, "viewer", "synthetic test phrase only", "VIEWER")
            with TestClient(create_app(directory), base_url="http://127.0.0.1:9140") as client:
                route = "/api/v1/topology"
                self.assertEqual(client.get(route).status_code, 401)
                client.cookies.set("netlab360_session", sessions.issue(directory, "viewer")["token"])
                self.assertEqual(client.get(route+"?url=other").status_code, 400)
                self.assertEqual(client.post(route).status_code, 405)
                with patch.object(reader, "collect", return_value=reader.project(fixture(), NOW, "OK")):
                    self.assertEqual(len(client.get(route).json()["nodes"]), 18)
                    self.assertEqual(client.get(route).status_code, 429)
                self.assertEqual(client.get("/topology").status_code, 200)
                self.assertEqual(client.get("/ui/static/topology.js").status_code, 200)
