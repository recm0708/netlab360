"""Comprobamos la proyección JavaScript real con observaciones sintéticas delimitadas."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "servicios/consola-s08/ui/static/app.js"

# Ejecutamos las funciones puras del mismo recurso servido por FastAPI.
SCRIPT = r"""
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const source = fs.readFileSync(process.argv[1], "utf8");
const start = source.indexOf("const NetlabNumbers =");
const end = source.indexOf("/* Fin de la proyección pura del dashboard. */");
assert(start >= 0 && end > start);
const model = vm.runInNewContext(source.slice(start,end) +
  "\n({NetlabNumbers,dashboardInventory,dashboardBatch,dashboardRows,dashboardSummary,dashboardDetail});");
const {dashboardInventory: inventory, dashboardBatch: batch,
       dashboardRows: rows, dashboardSummary: summary, dashboardDetail: detail} = model;
const stamp = "2026-11-24T23:00:00Z";

function scope(source, resource) {
  if (resource==="FRONTAL_HQ") return "HTTP_FROM_S2";
  if (resource==="FAUCET") return "CONTROLLER_ONLY";
  if (resource.startsWith("LACP-")) return "BOND_MEMBER_STATE";
  if (resource.startsWith("WAN-END-")||resource.startsWith("VLAN-")) return "ADMIN_STATE_ONLY";
  if (source==="EXPORTER_S04") return "ROUTER_EXISTENCE_ONLY";
  if (source==="NOC_S05") return "TOPOLOGY_OBSERVATION";
  if (resource==="S04-EXPORTER") return "SCRAPE_AVAILABILITY";
  if (resource==="S04-COLLECTOR") return "COLLECTOR_READ";
  if (source==="PROMETHEUS_S04") return resource==="MULTISEDE"?"ROUTER_EXISTENCE_ONLY":"CONTAINER_RUNNING_ONLY";
  return source==="IA_S06"?"HQ_CLIENT_EGRESS_NETWORK_STATE":"HISTORICAL";
}

function payload(key) {
  return {project:"NETLAB360",schema_version:1,infrastructure_state:"UNKNOWN",
    network_mutations_authorized:false,observations:inventory[key].map(([source,resource,,,max]) => {
      const record={schema:"NETLAB360_S08_SOURCE_V1",source,resource,
        scope:scope(source,resource),
        kind:key==="diagnostics"?"INFERENCE":key==="advisory"?"ADVISORY_SNAPSHOT":"OBSERVATION",
        transport:"OK",quality:"VALID",state:"UNKNOWN",age_seconds:1,
        observed_at_utc:stamp,max_age_seconds:max,network_mutations_authorized:false,details:{}};
      if (source==="EXPORTER_S04") record.details={"R-HQ":1,"R-S1":1,"R-S2":1};
      if (resource.startsWith("LACP-")) {record.state="NORMAL";record.details={switch_members:2,client_members:2};}
      if (resource==="FRONTAL_HQ") {record.state="NORMAL";record.details={active_backend:"BACKEND_HQ"};}
      if (resource==="FAUCET") {record.state="NORMAL";record.details={connected:true,flow_count:26};}
      if (resource.startsWith("WAN-END-")||resource.startsWith("VLAN-")) record.details={admin_up:1};
      return record;
    })};
}

function all() {
  return Object.fromEntries(Object.keys(inventory).map(key=>[key,{rows:batch(key,payload(key),1000)}]));
}

const fmt=model.NetlabNumbers.format;
assert.equal(fmt(25003200,"bytes"),"25,003,200");
assert.equal(fmt(20,"rate"),"20.000");
assert.equal(fmt(0.02684290293371846,"jitter"),"0.0268");
assert.equal(fmt(0,"loss"),"0.000");
assert.equal(fmt(99.95,"percentage"),"99.95");
assert.equal(fmt(0.000001,"jitter"),"<0.0001");
assert.equal(fmt(-0.000001,"jitter"),">-0.0001");
assert.equal(fmt(null,"rate"),"—");
assert.equal(fmt(NaN,"rate"),"—");
assert.equal(fmt("123","count"),"—");
assert.equal(fmt(12.5,"count"),"—");
assert.equal(fmt(1000.1234,"volume"),"1,000.12");
assert.equal(fmt(0.97851,"probability"),"0.9785");
assert.equal(fmt(45.24,"temperature"),"45.2");
assert.equal(model.NetlabNumbers.axis("jitter"),",.4f");
assert.throws(()=>fmt(1,"unknown"),{name:"RangeError"});
const scenario=process.argv[2];
if(scenario==="inventory") {
  const r=rows(all(),1000), s=summary(r);
  assert.equal(r.length,35);
  assert.equal(s.coverage.text,"30 / 30");
  assert.equal(s.routers.text,"3 / 3");
  assert.equal(s.wan.text,"8 / 8 activas");
  assert.equal(s.vlan.text,"9 / 9 activas");
  assert.equal(s.lacp.text,"3 / 3 normales");
  assert.equal(s.ha.detail,"HQ · principal · desde S2");
  assert.equal(s.sdn.text,"Conectado");
}
if(scenario==="expiry") {
  const data=all(), fresh=rows(data,1000), stale=rows(data,62000);
  assert.equal(fresh.filter(r=>r.quality==="VALID").length,35);
  assert.equal(stale.filter(r=>r.quality==="STALE").length,35);
  assert.equal(summary(stale).coverage.text,"0 / 30");
  assert.equal(summary(stale).ha.state,"unknown");
  assert.equal(summary(stale).routers.text,"Sin datos");
  assert.equal(detail(stale.find(r=>r.resource==="FAUCET")),"—");
}
if(scenario==="partial") {
  const data=all(); data.metrics={error:"LIMITED"};
  const r=rows(data,1000), s=summary(r);
  assert.equal(r.filter(x=>x.quality==="LIMITED").length,23);
  assert.equal(s.coverage.text,"7 / 30");
  assert.equal(s.wan.text,"Sin datos");
  assert.equal(s.lacp.state,"normal");
  assert.equal(s.ha.state,"normal");
}
if(scenario==="scope") {
  const p=payload("metrics");
  const admin=p.observations.find(r=>r.resource.startsWith("WAN-END-"));
  admin.state="NORMAL";
  const r=batch("metrics",p,1000).find(r=>r.resource===admin.resource);
  assert.equal(r.state,"UNKNOWN");
  assert.equal(detail(r),"Admin. activa");
  admin.scope="HTTP_FROM_S2";
  assert.throws(()=>batch("metrics",p,1000),/INVALID_SCOPE/);
  const a=payload("advisory");a.observations[0].state="FAULT";
  assert.equal(batch("advisory",a,1000)[0].state,"UNKNOWN");
  const i=payload("diagnostics");i.observations[0].state="FAULT";
  assert.equal(batch("diagnostics",i,1000)[0].state,"UNKNOWN");
}
if(scenario==="malformed") {
  for(const change of [
    p=>p.network_mutations_authorized=true,
    p=>p.observations.pop(),
    p=>p.observations[0]=p.observations[1],
    p=>p.observations[0].age_seconds=-1,
    p=>p.observations[0].observed_at_utc="invalid",
    p=>p.observations[0].transport="UNAVAILABLE",
    p=>p.observations[0].max_age_seconds=600
  ]) {
    const p=payload("sources");change(p);
    assert.throws(()=>batch("sources",p,1000));
  }
}
if(scenario==="fault") {
  const data=all(), p=payload("sources");
  const h=p.observations.find(r=>r.resource==="FRONTAL_HQ");
  h.state="DEGRADED";h.details={active_backend:"BACKEND_S1"};
  const l=p.observations.find(r=>r.resource==="LACP-HQ");
  l.state="FAULT";l.details={switch_members:0,client_members:0};
  data.sources={rows:batch("sources",p,1000)};
  const s=summary(rows(data,1000));
  assert.equal(s.ha.state,"degraded");
  assert.equal(s.ha.detail,"S1 · respaldo · desde S2");
  assert.equal(s.lacp.state,"fault");
}
if(scenario==="missing") {
  const data=all(), p=payload("sources");
  const h=p.observations.find(r=>r.resource==="FRONTAL_HQ");
  h.quality="MISSING";h.transport="UNAVAILABLE";h.age_seconds=null;
  data.sources={rows:batch("sources",p,1000)};
  const r=rows(data,1000), s=summary(r);
  assert.equal(s.ha.text,"Sin datos");
  assert.equal(s.ha.state,"unknown");
  assert.equal(s.coverage.text,"29 / 30");
  assert.equal(detail(r.find(x=>x.resource==="FRONTAL_HQ")),"—");
}
"""


@unittest.skipUnless(shutil.which("node"), "Node requerido para la proyección visual")
class DashboardTests(unittest.TestCase):
    def run_case(self, scenario):
        result = subprocess.run(
            ["node", "-e", SCRIPT, str(JS), scenario],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_inventory_and_indicators(self):
        self.run_case("inventory")

    def test_expiry_between_queries(self):
        self.run_case("expiry")

    def test_independent_source_failure(self):
        self.run_case("partial")

    def test_scope_and_no_global_inference(self):
        self.run_case("scope")

    def test_malformed_and_duplicate_rejected(self):
        self.run_case("malformed")

    def test_scoped_fault_and_backup(self):
        self.run_case("fault")

    def test_missing_data_not_healthy(self):
        self.run_case("missing")


if __name__ == "__main__":
    unittest.main()
