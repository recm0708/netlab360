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
const invalid=fixture();invalid.nodes[0]={...invalid.nodes[0],id:"FAUCET"};assert(!m.valid(invalid));
assert.throws(()=>m.view(d,"summary"));
assert.equal(m.view(d).nodes.length,18);
assert.equal(m.view(d).links.length,21);
assert.equal(m.view(d).nodes.filter(n=>n.type==="server").length,3);
assert.equal(m.view(d).links.filter(l=>l.type==="wan").length,4);
d.nodes[0].detail="Inventario de prueba";
const stale=m.aged(d,60);
assert.equal(stale.nodes[0].status,"unknown");
assert.equal(stale.nodes[0].detail,"Inventario de prueba");
assert(m.details(stale.nodes[0]).some(row=>row[0]==="Identificador"&&row[1]==="R-HQ"));
assert(m.details(stale.nodes[0]).some(row=>row[0]==="Vigencia"&&row[1]==="Sin observación vigente"));
const partial=fixture();partial.http={...partial.http,age_seconds:59};
assert.equal(m.aged(partial,2).nodes.find(n=>n.id==="FRONTAL_HQ").status,"unknown");
assert.equal(m.aged(partial,2).nodes[0].status,"running");
assert.equal(m.aged(partial,0,true).nodes[0].status,"unknown");
const svg=new Element("svg"),calls=[];
const choose=id=>calls.push(id);
m.render(svg,d,"R-HQ",choose,"detailed");
const first=svg.children.find(e=>e.attrs["data-resource"]==="R-HQ");
assert(first);assert(first.classes.has("selected"));
m.render(svg,stale,"R-HQ",choose,"detailed");
assert.equal(svg.children.find(e=>e.attrs["data-resource"]==="R-HQ"),first);
assert.equal(first.attrs["data-state"],"unknown");
assert.equal(first.attrs["aria-pressed"],"true");
first.handlers.click();assert.equal(calls[0],"R-HQ");
m.render(svg,d,null,choose,"detailed");assert(!first.classes.has("selected"));
m.render(svg,d,null,choose,"detailed");
assert.equal(svg.children.filter(e=>e.attrs["data-resource"]).length,39);
const byId=id=>d.links.find(l=>l.id===id);
assert.equal(m.edgePath(byId("S05-HA-HTTP-PRINCIPAL"),"detailed"),"M276 590 H174");
assert.equal(m.edgePath(byId("S05-HA-HTTP-RESPALDO"),"detailed"),"M330 613 V690 H905 V360 H1136");
assert.equal(m.edgePath(byId("S05-HA-ACCESO-FRONTAL"),"detailed"),"M284 390 H439 V590 H384");
assert.equal(m.viewport("detailed").join(" "),"0 0 1440 1250");
assert.equal(m.viewport("detailed","SDN").join(" "),"10 965 1410 270");
assert.equal(m.viewport("detailed","S1").join(" "),"970 5 450 440");
assert.throws(()=>m.viewport("detailed","external"));
let box=m.moveViewport("detailed",m.viewport("detailed"),0.8);
assert(box[2]<1440);assert(box[3]<1250);
box=m.moveViewport("detailed",box,1,99,99);
assert(box[0]+box[2]<=1440);assert(box[1]+box[3]<=1250);
const rows=[
  {source:"NOC_S05",resource:"LACP-HQ",quality:"VALID",state:"NORMAL",details:{switch_members:2,client_members:2}},
  {source:"NOC_S05",resource:"LACP-S1",quality:"VALID",state:"DEGRADED",details:{switch_members:2,client_members:1}},
  {source:"NOC_S05",resource:"LACP-S2",quality:"STALE",state:"NORMAL",details:{switch_members:2,client_members:2}},
  {source:"NOC_S05",resource:"FAUCET",quality:"VALID",state:"NORMAL",details:{connected:true,flow_count:27}}
];
const full=m.augment(d,rows),find=id=>full.nodes.find(n=>n.id===id);
assert.equal(full.nodes.length,26);assert.equal(full.links.length,28);
assert.equal(find("LACP-HQ").status,"bond-normal");
assert.equal(find("LACP-S1").status,"bond-degraded");
assert.equal(find("LACP-S2").status,"unknown");
assert.equal(find("OVS").flow_count,27);
assert.equal(find("SDN-A").status,"unknown");
assert.equal(full.links.filter(l=>l.type==="lacp").length,3);
assert(m.details(find("LACP-HQ")).some(r=>r[0]==="Miembros switch"&&r[1]==="2 / 2"));
assert(m.details(find("OVS")).some(r=>r[0]==="Flujos observados"&&r[1]==="27"));
assert(m.details(find("SDN-A")).some(r=>r[0]==="Estado observado"&&r[1]==="Sin verificar"));
assert.equal(m.geometry("detailed").layout.FAUCET[1]-23-1005,22);
assert(full.links.filter(l=>l.type==="sdn-access").every(l=>l.status==="unknown"));
assert.equal(m.augment(d,[]).nodes.find(n=>n.id==="FAUCET").status,"unknown");
m.render(svg,full,"LACP-HQ",choose);
assert.equal(svg.children.filter(e=>e.attrs["data-resource"]).length,54);
const bond=svg.children.find(e=>e.attrs["data-resource"]==="BOND-HQ");
assert.equal(Number(bond.children.find(e=>e.textContent==="802.3ad").attrs.x),m.geometry("detailed").layout["LACP-HQ"][0]-84);
for(const [id,pattern] of [["SDN-CONTROL","control"],["S05-HA-HTTP-PRINCIPAL","service"]]){
  assert(svg.children.find(e=>e.attrs["data-resource"]===id).children.some(e=>e.attrs.class==="topology-edge "+pattern));
}
assert.equal(svg.children.find(e=>e.attrs["data-resource"]==="LACP-S1").attrs["data-state"],"warn");
assert.equal(svg.children.find(e=>e.attrs["data-resource"]==="SDN-A").attrs["data-state"],"unknown");
m.render(svg,m.augment(d,[]),"LACP-HQ",choose);
assert.equal(svg.children.find(e=>e.attrs["data-resource"]==="LACP-HQ").attrs["data-state"],"unknown");
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
        self.assertNotIn('href="/topology?view=detailed"', html)
        self.assertNotIn('href="/topology?view=detailed" target="_blank"', html)
        self.assertIn('id="topology-workspace"', html)
        self.assertIn("topologyWorkspace.requestFullscreen()", js)
        self.assertIn("document.exitFullscreen()", js)
        self.assertIn('id="topology-site"', html)
        self.assertIn("applyTopologyBox();", js)
        self.assertIn("Todas las zonas", html)
        self.assertIn('aria-label="Convenciones del diagrama"', html)
        for state in ("ok", "recovery", "warn", "fault", "unknown"):
            self.assertIn(f'<strong data-state="{state}">', html)
        self.assertIn("moveViewport(topologyMode", js)
        self.assertIn('if(status===429)', js)
        self.assertIn("refreshCurrent", js)
        self.assertNotIn("scheduleTopology(", js)
        self.assertIn('await debugRead("/api/v1/topology")', js)
        self.assertIn('await debugRead("/api/v1/sources")', js)
        self.assertIn('model.augment(model.aged', js)
        css = (UI / "static/styles.css").read_text(encoding="utf-8")
        self.assertIn(".dashboard-table-wrap { max-height: 60vh; overflow: auto; overscroll-behavior: auto; }", css)

    def test_fullscreen_width_and_inspector_hierarchy(self):
        css = (UI / "static/styles.css").read_text(encoding="utf-8")
        self.assertIn("#topology-workspace:fullscreen #topology-map { width:100%; height:auto; max-height:none; }", css)
        self.assertNotIn("max-height:calc(100vh - 185px)", css)
        self.assertIn(".topology-inspector dt { color:var(--muted); font-size:.79rem; font-weight:700;", css)
        self.assertIn(".topology-inspector dd { color:var(--text); font-size:.94rem;", css)
        self.assertIn("#topology-selection { color:var(--text); font-size:1rem; font-weight:700;", css)
