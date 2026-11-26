"""Pruebas de procedencia, cobertura y acceso del lector integrado."""
import importlib.util
import json
import shutil
import subprocess
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "servicios/consola-s08/api"
spec = importlib.util.spec_from_file_location("netlab360_s08_observation", PACKAGE / "__init__.py",
                                             submodule_search_locations=[str(PACKAGE)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from netlab360_s08_observation import observability_reader as R, slo_contract as S

END = 10000.0
AVAILABLE = all(importlib.util.find_spec(n) is not None for n in ("fastapi", "httpx", "pydantic", "uvicorn"))


def payload(metric, key="hq-s1-icmp", values=None):
    probe = S.probe(key)
    return {"status": "success", "data": {"resultType": "matrix", "result": [
        {"metric": {"__name__": metric, "job": R.JOB, "probe_id": key,
                    "instance": "127.0.0.1:9116", "laboratory": "netlab360-lab",
                    "origin": probe["origin"], "module": probe["module"]},
         "values": values if values is not None else [[END, "1"]]}]}}


def sources(metric, end):
    if metric == "probe_http_status_code":
        return "OK", {"s2-hq-http": {int(end * 1000): 200}}
    value = .001 if metric == "probe_duration_seconds" else 1
    return "OK", {key: {int((end - i * 10) * 1000): value for i in range(360)}
                  for key in S.PROBES}


class ReaderTests(unittest.TestCase):
    def test_full_windows(self):
        with patch.object(R, "fetch", side_effect=sources) as fetch:
            result = R.collect(END)
        self.assertEqual(fetch.call_count, 4)
        self.assertEqual(len(result["probes"]), 5)
        for row in result["probes"]:
            self.assertEqual(row["quality"], "VALID")
            self.assertEqual([w["probe_count"] for w in row["windows"]], [30, 90, 360])
            self.assertTrue(all(w["meets_observed_target"] is True for w in row["windows"]))
            self.assertEqual(len(row["samples"]), 360)

    def test_missing_not_healthy(self):
        with patch.object(R, "fetch", return_value=("OK", {})):
            result = R.collect(END)
        for row in result["probes"]:
            self.assertEqual(row["quality"], "ABSENT")
            self.assertIsNone(row["latest"])
            self.assertTrue(all(w["observed_availability_pct"] is None for w in row["windows"]))

    def test_transport_failure_not_zero(self):
        def fail(metric, end):
            return ("UNAVAILABLE", {}) if metric == "up" else sources(metric, end)
        with patch.object(R, "fetch", side_effect=fail):
            result = R.collect(END)
        self.assertEqual(result["transport"]["up"], "UNAVAILABLE")
        self.assertTrue(all(row["windows"] == [] and row["quality"] == "UNKNOWN"
                            for row in result["probes"]))

    def test_optional_failure_preserves_sli(self):
        def fail(metric, end):
            return ("INVALID", {}) if metric == "probe_duration_seconds" else sources(metric, end)
        with patch.object(R, "fetch", side_effect=fail):
            result = R.collect(END)
        self.assertEqual(result["probes"][0]["windows"][0]["probe_count"], 30)
        self.assertIsNone(result["probes"][0]["latest"]["duration_seconds"])

    def test_identity_and_duplicates(self):
        row = payload("up")
        self.assertEqual(R.series(row, "up", END), {"hq-s1-icmp": {10000000: 1}})
        row["data"]["result"].append(row["data"]["result"][0])
        with self.assertRaises(ValueError):
            R.series(row, "up", END)
        row = payload("up")
        row["data"]["result"][0]["metric"]["origin"] = "S2"
        with self.assertRaises(ValueError):
            R.series(row, "up", END)

    def test_invalid_duration_and_query(self):
        for raw in ("NaN", "-1", "6"):
            with self.assertRaises(ValueError):
                R.series(payload("probe_duration_seconds", values=[[END, raw]]),
                         "probe_duration_seconds", END)
        with self.assertRaises(ValueError):
            R.expression("arbitrary")

    def test_failed_scrape_and_unpaired(self):
        def data(metric, end):
            if metric == "up":
                return "OK", {"hq-s1-icmp": {10000000: 0}}
            if metric == "probe_success":
                return "OK", {}
            return "OK", {}
        with patch.object(R, "fetch", side_effect=data):
            row = R.collect(END)["probes"][0]
        self.assertEqual(row["quality"], "UNKNOWN")
        self.assertIsNone(row["latest"]["probe_success"])
        self.assertEqual(row["windows"][0]["probe_fail"], 0)
        def unpaired(metric, end):
            return ("OK", {"hq-s1-icmp": {10000000: 1}}) if metric == "probe_success" else data(metric, end)
        with patch.object(R, "fetch", side_effect=unpaired):
            self.assertEqual(R.collect(END)["probes"][0]["quality"], "INVALID")


@unittest.skipUnless(shutil.which("node"), "Node para comprobar la proyección visual")
class ProjectionTests(unittest.TestCase):
    """Contrastar la presentación con el contrato Python y casos de ausencia."""

    def run_node(self, program, payload):
        script = ROOT / "servicios/consola-s08/ui/static/observation.js"
        subprocess.run(["node", "-e", program, str(script)],
                       input=json.dumps(payload), text=True, check=True, capture_output=True)

    def test_real_contract_shape_and_plot(self):
        with patch.object(R, "fetch", side_effect=sources):
            data = R.collect(END)
        self.run_node("""
const assert=require("node:assert/strict");
require(process.argv[1]);
const M=globalThis.NetlabObservation, d=JSON.parse(require("node:fs").readFileSync(0,"utf8"));
assert.equal(M.validate(d),d);
const colors={surface:"#fff",text:"#111",line:"#777",ok:"#004400",fault:"#990000",light:true};
const fmt=x=>x.toISOString();
for(const metric of ["scrape_up","probe_success","duration_seconds"]){
  const f=M.figure(d,metric,fmt,colors,5);
  assert.equal(f.traces.length,5);
  for(const t of f.traces){
    assert.equal(t.x.length,30);
    if(metric==="duration_seconds"){
      assert.equal(t.connectgaps,false); assert(t.y.every(n=>n===1));
    }
  }
}
assert.equal(M.httpLabel(200),"200 OK");
assert.equal(M.httpLabel(0),"0 · Sin respuesta");
assert.equal(M.httpLabel(null),"Sin datos");
assert.equal(M.httpLabel(503),"503");
assert.equal(M.httpState(503),"fault");
d.probes[0].windows[0].probe_ok--;
assert.throws(()=>M.validate(d));
""", data)

    def test_partial_and_absence_not_success(self):
        def partial(metric, end):
            status, rows = sources(metric, end)
            for points in rows.values():
                points.pop(int((end - 20) * 1000), None)
            return status, rows
        with patch.object(R, "fetch", side_effect=partial):
            data = R.collect(END)
        with patch.object(R, "fetch", return_value=("OK", {})):
            absent = R.collect(END)
        self.run_node("""
const assert=require("node:assert/strict");
require(process.argv[1]);
const M=globalThis.NetlabObservation, [d,empty]=JSON.parse(require("node:fs").readFileSync(0,"utf8"));
M.validate(d); M.validate(empty);
assert.equal(d.probes[0].windows[0].meets_observed_target,null);
assert.equal(empty.probes[0].windows[0].observed_availability_pct,null);
const f=M.figure(d,"duration_seconds",x=>x.toISOString(),{light:false},5);
assert(f.traces.every(t=>t.y.includes(null)));
assert(M.figure(empty,"probe_success",x=>x.toISOString(),{},5).traces.every(t=>t.x.length===0));
""", [data, absent])

    def test_overview_preserves_quality_and_counts(self):
        with patch.object(R, "fetch", side_effect=sources):
            full = R.collect(END)
        with patch.object(R, "fetch", return_value=("OK", {})):
            empty = R.collect(END)
        self.run_node("""
const assert=require("node:assert/strict");
require(process.argv[1]);
const M=globalThis.NetlabObservation, [full,empty]=JSON.parse(require("node:fs").readFileSync(0,"utf8"));
assert.deepEqual(M.overview(full),{fresh:5,acquired:5,measured:5,passed:5,complete:15});
assert.deepEqual(M.overview(empty),{fresh:0,acquired:0,measured:0,passed:0,complete:0});
full.probes[0].quality="STALE";
assert.deepEqual(M.overview(full),{fresh:4,acquired:4,measured:4,passed:4,complete:15});
for(const span of [5,15,60]){
  const stats=M.durationStats(full,span);
  assert.equal(stats.length,5);
  for(const s of stats)assert.deepEqual([s.count,s.last,s.mean,s.max],[span*6,1,1,1]);
  for(const s of M.durationStats(empty,span))assert.deepEqual([s.count,s.last,s.mean,s.max],[0,null,null,null]);
}
""", [full, empty])

    def test_http_distribution_exact_codes_and_interval(self):
        def mixed(metric, end):
            if metric == "probe_http_status_code":
                return "OK", {"s2-hq-http": {
                    int(end * 1000): 200, int((end-10)*1000): 503,
                    int((end-20)*1000): 0, int((end-310)*1000): 302}}
            return sources(metric, end)
        with patch.object(R, "fetch", side_effect=mixed):
            result = R.collect(END)
        self.run_node("""
const assert=require("node:assert/strict");
require(process.argv[1]);
const M=globalThis.NetlabObservation,d=JSON.parse(require("node:fs").readFileSync(0,"utf8"));
M.validate(d);
const h=M.httpHistory(d,5);
assert.equal(h.rows.length,30);
assert.deepEqual(h.counts,[[0,1],[200,1],[503,1],[null,27]]);
assert.deepEqual(h.rows.slice(0,3).map(s=>s.http_status_code),[200,503,0]);
assert.equal(h.latest.http_status_code,200);
assert.deepEqual(M.httpHistory(d,15).counts,[[0,1],[200,1],[302,1],[503,1],[null,86]]);
assert.equal(M.httpHistory(d,60).rows.length,360);
assert.equal(M.httpHistory(d,60).counts.reduce((n,r)=>n+r[1],0),360);
""", result)

    def test_notification_scope(self):
        self.run_node("""
const assert=require("node:assert/strict");
require(process.argv[1]);
const M=globalThis.NetlabObservation;
const empty={source:"ALERTMANAGER_WEBHOOK",scope:"operational",transport:"OK",total:0,records:[],truncated:false};
assert.equal(M.validateNotifications(empty,"operational").total,0);
assert.throws(()=>M.validateNotifications(empty,"validation"));
assert.throws(()=>M.validateNotifications({...empty,transport:"UNAVAILABLE"},"operational"));
assert.equal(M.validateNotifications({...empty,transport:"UNAVAILABLE",total:null},"operational").total,null);
""", None)

    def test_static_safety(self):
        ui = ROOT / "servicios/consola-s08/ui"
        js = (ui / "static/observation.js").read_text()
        for forbidden in ("innerHTML", "document.cookie", "localStorage", "sessionStorage", "eval("):
            self.assertNotIn(forbidden, js)
        self.assertIn('read("/api/v1/observability/probes",1048576)', js)
        self.assertIn('read("/api/v1/alerts/notifications/"+selected,2097152)', js)
        self.assertIn('context().role!=="OPERATOR"', js)
        self.assertIn("observationView.clear();", (ui / "static/app.js").read_text())
        self.assertIn('rel="noopener noreferrer">Abrir Grafana', (ui / "index.html").read_text())


@unittest.skipUnless(AVAILABLE and os.geteuid() != 0, "API con dependencias y usuario sin root")
class HttpTests(unittest.TestCase):
    def test_session_and_fixed_selection(self):
        from fastapi.testclient import TestClient
        from netlab360_s08_observation import security, sessions, storage
        from netlab360_s08_observation.main import create_app
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "estado"
            storage.initialize(directory)
            storage.migrate(directory)
            security.create_user(directory, "viewer", "synthetic test phrase only", "VIEWER")
            with TestClient(create_app(directory), base_url="http://127.0.0.1:9140") as client:
                path = "/api/v1/observability/probes"
                self.assertEqual(client.get(path).status_code, 401)
                issued = sessions.issue(directory, "viewer")
                client.cookies.set("netlab360_session", issued["token"])
                with patch.object(R, "collect", return_value={"source": "SYNTHETIC_TEST"}) as collect:
                    self.assertEqual(client.get(path + "?query=up").status_code, 400)
                    self.assertEqual(client.get(path).json(), {"source": "SYNTHETIC_TEST"})
                    self.assertEqual(client.get(path).status_code, 429)
                    collect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
