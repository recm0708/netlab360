"""Validamos los intervalos reales, muestras ausentes y límites de históricos."""
import importlib.util
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location(
    "netlab360_s08_history", package / "__init__.py",
    submodule_search_locations=[str(package)])
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_history import history_reader as h

END = 1795550400


def fixture(group):
    keys = {key for _, _, key in h.GROUPS[group]} | {h.UP, h.COLLECTOR}
    return {"status":"success","data":{"resultType":"matrix","result":[
        {"metric":dict(key),"values":[[END-4,"1"],[END-2,"1"]]}
        for key in sorted(keys)]}}


def row(payload, key):
    return next(r for r in payload["data"]["result"] if r["metric"]==dict(key))


class HistoryTests(unittest.TestCase):
    def test_catalog_and_fixed_query(self):
        for group, size in (("collection",2),("routers",3),("wan",8),("vlan",9)):
            self.assertEqual(len(h.GROUPS[group]),size)
            for window in h.WINDOWS:
                parsed = urlsplit(h.query_path(group,window,END))
                self.assertEqual(parsed.path,"/api/v1/query")
                args = parse_qs(parsed.query)
                self.assertEqual(args["time"],[str(END)])
                self.assertTrue(args["query"][0].endswith("["+window+"]"))
                self.assertIn(h.adapter.JOB,args["query"][0])
        for group, window in (("arbitrary","5m"),("wan","99d")):
            with self.assertRaises(ValueError):
                h.query_path(group,window,END)

    def test_real_timestamps_and_scope(self):
        data = h.project("vlan","5m",END,fixture("vlan"),"OK")
        self.assertEqual(data["start_epoch"],END-300)
        self.assertEqual(data["end_epoch"],END)
        self.assertFalse(data["network_mutations_authorized"])
        self.assertEqual(len(data["series"]),9)
        for series in data["series"]:
            self.assertEqual(series["scope"],"ADMIN_STATE_ONLY")
            self.assertEqual(series["points"],[[END-4,1],[END-2,1]])

    def test_failed_scrape_and_negative_sample(self):
        p = fixture("wan")
        row(p,h.UP)["values"][0][1]="0"
        target=h.GROUPS["wan"][0][2]
        row(p,target)["values"][1][1]="-1"
        data=h.project("wan","5m",END,p,"OK")
        self.assertEqual(data["series"][0]["points"],[[END-4,None],[END-2,None]])
        self.assertEqual(data["series"][1]["points"],[[END-4,None],[END-2,1]])

    def test_missing_series_and_gap(self):
        p=fixture("routers")
        target=h.GROUPS["routers"][0][2]
        p["data"]["result"].remove(row(p,target))
        row(p,h.COLLECTOR)["values"].pop()
        data=h.project("routers","5m",END,p,"OK")
        self.assertEqual(data["series"][0]["points"],[])
        self.assertEqual(data["series"][1]["points"],[[END-4,1],[END-2,None]])

    def test_zero_not_missing(self):
        p=fixture("collection")
        row(p,h.UP)["values"][0][1]="0"
        data=h.project("collection","5m",END,p,"OK")
        self.assertEqual(data["series"][0]["points"][0],[END-4,0])
        self.assertEqual(data["series"][1]["points"][0],[END-4,None])

    def test_invalid_envelopes(self):
        for change in (
            lambda p:p.update(warnings=["partial"]),
            lambda p:p["data"]["result"].append(row(p,h.UP)),
            lambda p:row(p,h.UP)["metric"].update(instance="other"),
            lambda p:row(p,h.UP)["values"].append([END+1,"1"]),
            lambda p:row(p,h.UP)["values"].append([END-2,"1"]),
            lambda p:row(p,h.UP)["values"].append([END,"NaN"]),
            lambda p:row(p,h.UP).update(values=[[END-1,"1"]]*(h.MAX_POINTS+1)),
        ):
            with self.subTest(change=change):
                p=fixture("collection")
                change(p)
                result=h.project("collection","5m",END,p,"OK")
                self.assertEqual(result["transport"],"INVALID")
                self.assertTrue(all(not s["points"] for s in result["series"]))

    def test_unavailable_and_fixed_transport(self):
        with patch.object(h.readers,"_fetch_fixed",return_value=(None,"","UNAVAILABLE")) as fetch:
            data=h.collect("collection","15m")
            self.assertEqual(data["transport"],"UNAVAILABLE")
            fetch.assert_called_once_with(9091,h.query_path("collection","15m",data["end_epoch"]),h.MAX_BYTES)
        self.assertTrue(all(not s["points"] for s in data["series"]))


AVAILABLE = all(importlib.util.find_spec(name) is not None
                for name in ("fastapi","httpx","pydantic","uvicorn"))
if AVAILABLE:
    from fastapi.testclient import TestClient
    from netlab360_s08_history import storage, security, sessions
    from netlab360_s08_history.main import create_app


@unittest.skipUnless(AVAILABLE and os.geteuid()!=0,"API S08 sin root")
class HistoryHttpTests(unittest.TestCase):
    def test_auth_selection_rate_and_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            directory=Path(temp)/"estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory,"viewer","synthetic test phrase only","VIEWER")
            token=sessions.issue(directory,"viewer")["token"]
            with TestClient(create_app(directory),base_url="http://127.0.0.1:9140") as client:
                path="/api/v1/history/collection/5m"
                with patch.object(h,"collect",return_value=h.project("collection","5m",END,fixture("collection"),"OK")) as collect:
                    self.assertEqual(client.get(path).status_code,401)
                    client.cookies.set("netlab360_session",token)
                    self.assertEqual(client.get(path+"?query=other").status_code,400)
                    self.assertEqual(client.get("/api/v1/history/other/5m").status_code,400)
                    self.assertEqual(client.get("/api/v1/history/collection/999d").status_code,400)
                    self.assertEqual(client.post(path).status_code,405)
                    collect.assert_not_called()
                    result=client.get(path)
                    self.assertEqual(result.status_code,200)
                    self.assertFalse(result.json()["network_mutations_authorized"])
                    self.assertEqual(client.get(path).status_code,429)
                    collect.assert_called_once_with("collection","5m")


if __name__ == "__main__":
    unittest.main()
