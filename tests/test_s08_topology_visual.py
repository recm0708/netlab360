"""Validamos vistas SVG, geometría, vigencia y selección estable sin navegador."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "servicios/consola-s08/ui"

SCRIPT = r"""
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
class Element {
  constructor(tag){this.tag=tag;this.attrs={};this.children=[];this.handlers={};this.textContent="";
    this.classes=new Set();this.classList={toggle:(name,on)=>on?this.classes.add(name):this.classes.delete(name)};}
  setAttribute(k,v){this.attrs[k]=String(v);}
  getAttribute(k){return this.attrs[k]??null;}
  append(...items){this.children.push(...items);}
  prepend(item){this.children.unshift(item);}
  replaceChildren(){this.children=[];}
  get firstChild(){return this.children[0];}
  addEventListener(k,f){this.handlers[k]=f;}
}
const ctx=vm.createContext({document:{createElementNS:(_,tag)=>new Element(tag)}});
vm.runInContext(fs.readFileSync(process.argv[1],"utf8"),ctx);
const m=ctx.NetlabTopology;
function fixture(){
  const meta={quality:"VALID",age_seconds:2,max_age_seconds:60};
  const nodes=[],links=[];
  for(const [i,site] of ["HQ","S1","S2"].entries()){
    nodes.push({id:"R-"+site,type:"router",label:"R-"+site,status:"running",scope:"CONTAINER_ONLY"},
      {id:"SW-"+site,type:"switch",label:"SW-"+site,status:"namespace-present",scope:"NAMESPACE_ONLY"});
    links.push({id:"TRUNK-"+site,type:"lan",from:"R-"+site,to:"SW-"+site,status:"unknown",role:"trunk",scope:"INVENTORY_ONLY"});
    for(const suffix of [10,20,30]){
      const vlan=(i+1)*100+suffix,id="H-"+site+"-"+vlan;
      nodes.push({id,type:"host",label:id,vlan,gateway:"10.0.0.1",status:"namespace-present",vlan_admin:"admin-up",scope:"NAMESPACE_ONLY"});
      links.push({id:"ACCESS-"+site+"-"+vlan,type:"access",from:"SW-"+site,to:id,status:"unknown",role:"access",scope:"INVENTORY_ONLY"});
    }
  }
  for(const site of ["S1","S2"])for(const role of ["primary","backup"])
    links.push({id:"WAN-"+(role==="primary"?"PRIMARIA":"RESPALDO")+"-HQ-"+site,type:"wan",from:"R-HQ",to:"R-"+site,role,
      route_selection:role==="primary"?"selected":"standby",status:"admin-up",a:"10.78.0.1/30",b:"10.78.0.2/30",scope:"ADMIN_STATE_ONLY"});
  for(const [id,site] of [["BACKEND_HQ","HQ"],["FRONTAL_HQ","HQ"],["BACKEND_S1","S1"]])
    nodes.push({id,type:"server",site,label:id,status:"running",scope:"HTTP_FROM_S2",application_selection:"selected"});
  for(const [id,from,to,type] of [
    ["S05-HA-ACCESO-HQ","SW-HQ","BACKEND_HQ","access"],
    ["S05-HA-ACCESO-FRONTAL","SW-HQ","FRONTAL_HQ","access"],
    ["S05-HA-ACCESO-S1","SW-S1","BACKEND_S1","access"],
    ["S05-HA-HTTP-PRINCIPAL","FRONTAL_HQ","BACKEND_HQ","redundancy"],
    ["S05-HA-HTTP-RESPALDO","FRONTAL_HQ","BACKEND_S1","redundancy"]])
    links.push({id,from,to,type,role:"http",scope:type==="redundancy"?"HTTP_FROM_S2":"INVENTORY_ONLY",status:"unknown"});
  return {project:"NETLAB360",schema_version:1,source:"NOC",network_mutations_authorized:false,
    traffic_measured:false,graph:meta,telemetry:meta,http:meta,nodes,links};
}
const d=fixture();
assert(m.valid(d));
assert.equal(m.view(d,"summary").nodes.length,15);
assert.equal(m.view(d,"summary").links.length,14);
assert.equal(m.view(d,"detailed").nodes.length,18);
assert.equal(m.view(d,"detailed").links.length,21);
const logical=m.view(d,"summary").links.find(l=>l.type==="wan-group");
assert.equal(m.logicalState(logical),"ok");
logical.members[1].status="admin-down";
assert.equal(m.logicalState(logical),"warn");
logical.members[0].status="admin-down";logical.members[0].route_selection="unavailable";
assert.equal(m.logicalState(logical),"fault");
logical.members[1].status="admin-up";logical.members[1].route_selection="selected";
assert.equal(m.logicalState(logical),"recovery");
const stale=m.aged(d,60);
assert.equal(stale.nodes[0].status,"unknown");
assert.equal(m.logicalState(m.view(stale,"summary").links.find(l=>l.type==="wan-group")),"unknown");
const partial=fixture();partial.http={...partial.http,age_seconds:59};
assert.equal(m.aged(partial,2).nodes.find(n=>n.id==="FRONTAL_HQ").status,"unknown");
assert.equal(m.aged(partial,2).nodes[0].status,"running");
assert.equal(m.aged(partial,0,true).nodes[0].status,"unknown");
const svg=new Element("svg"),calls=[];
const choose=id=>calls.push(id);
m.render(svg,d,"R-HQ",choose,"summary");
const first=svg.children.find(e=>e.attrs["data-resource"]==="R-HQ");
assert(first);assert(first.classes.has("selected"));
m.render(svg,stale,"R-HQ",choose,"summary");
assert.equal(svg.children.find(e=>e.attrs["data-resource"]==="R-HQ"),first);
assert.equal(first.attrs["data-state"],"unknown");
assert.equal(first.attrs["aria-pressed"],"true");
first.handlers.click();assert.equal(calls[0],"R-HQ");
m.render(svg,d,null,choose,"summary");assert(!first.classes.has("selected"));
m.render(svg,d,null,choose,"detailed");
assert.equal(svg.children.filter(e=>e.attrs["data-resource"]).length,39);
const byId=id=>d.links.find(l=>l.id===id);
assert.equal(m.edgePath(byId("S05-HA-HTTP-PRINCIPAL"),"detailed"),"M276 590 H174");
assert.equal(m.edgePath(byId("S05-HA-HTTP-RESPALDO"),"detailed"),"M330 613 V690 H905 V360 H1136");
assert.equal(m.edgePath(byId("S05-HA-ACCESO-FRONTAL"),"detailed"),"M284 390 H439 V590 H384");
assert.equal(m.viewport("summary").join(" "),"0 0 1250 620");
assert.equal(m.viewport("detailed","S1").join(" "),"970 5 450 440");
assert.throws(()=>m.viewport("summary","external"));
let box=m.moveViewport("summary",m.viewport("summary"),0.8);
assert(box[2]<1250);assert(box[3]<620);
box=m.moveViewport("summary",box,1,99,99);
assert(box[0]+box[2]<=1250);assert(box[1]+box[3]<=620);
m.reset(svg);assert.equal(svg.children.length,0);
"""


class TopologyVisualTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node requerido para SVG")
    def test_views_geometry_and_stable_elements(self):
        result = subprocess.run(
            ["node", "-e", SCRIPT, str(UI / "static/topology.js")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_controller_and_fullscreen(self):
        html = (UI / "index.html").read_text(encoding="utf-8")
        js = (UI / "static/app.js").read_text(encoding="utf-8")
        self.assertIn('href="/topology?view=detailed">Vista detallada', html)
        self.assertNotIn('href="/topology?view=detailed" target="_blank"', html)
        self.assertIn('id="topology-workspace"', html)
        self.assertIn("topologyWorkspace.requestFullscreen()", js)
        self.assertIn("document.exitFullscreen()", js)
        self.assertIn('id="topology-site"', html)
        self.assertIn("applyTopologyBox();", js)
        self.assertIn("moveViewport(topologyMode", js)
        self.assertIn('if(status===429)', js)
        self.assertIn("refreshCurrent", js)
        self.assertNotIn("scheduleTopology(", js)
        self.assertIn('await debugRead("/api/v1/topology")', js)
