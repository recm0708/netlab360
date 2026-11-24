"""Pruebas del lector Prometheus S08 y compatibilidad con el contrato S07."""
from datetime import datetime
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location(
    "netlab360_s08_metrics", package / "__init__.py", submodule_search_locations=[str(package)])
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_metrics import prometheus_reader as m

NOW = "2026-01-01T00:00:10+00:00"
T = datetime.fromisoformat(NOW).timestamp() - 5


def fixture():
    rows = []
    for key in sorted(m.adapter.expected_keys()):
        labels = dict(key)
        value = "0" if labels.get("mode") not in (None,"active") else "1"
        rows.append({"metric": labels, "values": [[T-2,value],[T,value]]})
    return {"status":"success","data":{"resultType":"matrix","result":rows}}


def series(payload,name,**labels):
    return next(row for row in payload["data"]["result"]
                if row["metric"]["__name__"] == name
                and all(row["metric"].get(k)==v for k,v in labels.items()))


def by_id(rows, resource):
    return next(row for row in rows if row["resource"]==resource)


class MetricsTests(unittest.TestCase):
    def test_inventory_and_scope(self):
        rows = m.project(fixture(),NOW,"OK")
        self.assertEqual(len(rows),23)
        self.assertTrue(all(row["quality"]=="VALID" for row in rows))
        self.assertEqual(sum(row["state"]=="NORMAL" for row in rows),2)
        self.assertEqual(by_id(rows,"VLAN-110")["state"],"UNKNOWN")
        self.assertTrue(all(row["network_mutations_authorized"] is False for row in rows))

    def test_scrape_timestamp(self):
        rows = m.project(fixture(),NOW,"OK")
        self.assertTrue(all(row["age_seconds"]==5 for row in rows))

    def test_failed_scrape(self):
        p = fixture()
        series(p,"up")["values"][-1][1] = "0"
        rows = m.project(p,NOW,"OK")
        self.assertEqual(by_id(rows,"S04-EXPORTER")["state"],"FAULT")
        self.assertEqual(by_id(rows,"VLAN-110")["quality"],"MISSING")

    def test_stale_and_future(self):
        for stamp, quality in ((T-90,"STALE"),(T+10,"FUTURE")):
            p = fixture()
            for row in p["data"]["result"]:
                row["values"] = [[stamp,row["values"][-1][1]]]
            rows = m.project(p,NOW,"OK")
            self.assertTrue(all(r["quality"]==quality and r["details"]=={} for r in rows))

    def test_invalid_envelope(self):
        for payload in ({},dict(fixture(),warnings=["partial"])):
            self.assertTrue(all(r["quality"]=="INVALID" for r in m.project(payload,NOW,"OK")))

    def test_unavailable(self):
        rows = m.project(None,NOW,"UNAVAILABLE")
        self.assertEqual(len(rows),23)
        self.assertTrue(all(r["quality"]=="MISSING" and r["details"]=={} for r in rows))

    def test_duplicate_and_mismatched_scrape(self):
        p = fixture()
        p["data"]["result"].append(series(p,"up"))
        self.assertTrue(all(r["quality"]=="MISSING" for r in m.project(p,NOW,"OK")))
        p = fixture()
        series(p,m.adapter.PREFIX+"vlan_admin_up",site="HQ",vlan="110")["values"].pop()
        self.assertEqual(by_id(m.project(p,NOW,"OK"),"VLAN-110")["quality"],"MISSING")

    def test_fixed_query(self):
        with patch.object(m.readers,"_fetch_fixed",return_value=(fixture(),NOW,"OK")) as fetch:
            self.assertEqual(len(m.collect()),23)
            fetch.assert_called_once_with(9091,m.PATH,m.adapter.MAX_BYTES)
        self.assertIn("query=",m.PATH)
        self.assertEqual(m.adapter.MAX_BYTES,524288)


AVAILABLE = all(importlib.util.find_spec(name) is not None for name in ("fastapi","httpx","pydantic"))
if AVAILABLE:
    from fastapi.testclient import TestClient
    from netlab360_s08_metrics import storage, security, sessions
    from netlab360_s08_metrics.main import create_app


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0,"API S08 con dependencias y sin root")
class MetricsHttpTests(unittest.TestCase):
    def test_protected_metrics_and_json_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)/"estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory,"viewer","synthetic test phrase only","VIEWER")
            token = sessions.issue(directory,"viewer")["token"]
            with TestClient(create_app(directory),base_url="http://127.0.0.1:9140") as client:
                with patch.object(m,"collect",return_value=m.project(fixture(),NOW,"OK")) as collect:
                    self.assertEqual(client.get("/api/v1/metrics").status_code,401)
                    collect.assert_not_called()
                    client.cookies.set("netlab360_session",token)
                    self.assertEqual(client.get("/api/v1/metrics?query=up").status_code,400)
                    collect.assert_not_called()
                    response = client.get("/api/v1/metrics")
                    self.assertEqual(response.status_code,200)
                    rows = response.json()["observations"]
                    self.assertEqual(len(rows),23)
                    self.assertEqual(rows[0]["schema"],"NETLAB360_S08_SOURCE_V1")
                    self.assertNotIn("schema_id",rows[0])
                    self.assertEqual(client.post("/api/v1/metrics").status_code,405)
                    collect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
