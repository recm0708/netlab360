"""Validamos el modelo visual y los recursos locales de históricos."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "servicios/consola-s08/ui"

SCRIPT = r"""
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const ctx=vm.createContext({});
vm.runInContext(fs.readFileSync(process.argv[1],"utf8"),ctx);
const h=ctx.NetlabHistory;
const p={project:"NETLAB360",schema_version:1,source:"PROMETHEUS_S04",
 group:"collection",window:"5m",transport:"OK",start_epoch:1000,end_epoch:1300,
 scrape_interval_seconds:2,network_mutations_authorized:false,series:[
 {id:"exporter",scope:"SCRAPE_AVAILABILITY",points:[[1002,1],[1004,null],[1010,0]]},
 {id:"collector",scope:"COLLECTOR_READ",points:[]}]};
assert.equal(h.allowed("collection","5m"),true);
assert.equal(h.allowed("toString","5m"),false);
assert.equal(h.validate(p,"collection","5m"),p);
assert.equal(h.counts(p).valid,2);
assert.equal(h.counts(p).missing,1);
assert.equal(h.counts(p).series,1);
const fig=h.figure(p,d=>d.toISOString(),{ok:"#00aa00",fault:"#ff0000",surface:"#fff",text:"#111",line:"#aaa"});
assert.equal(fig.traces.length,2);
assert.equal(fig.traces[0].mode,"markers");
assert.equal(fig.traces[0].x.length,2);
assert.equal(fig.traces[0].x[1],1010);
assert.equal(fig.traces[0].y[1],3);
assert.equal(fig.traces[1].x.length,0);
assert.notEqual(fig.traces[0].marker.color,fig.traces[1].marker.color);
assert.equal(fig.traces[0].marker.symbol[0],"circle");
assert.equal(fig.traces[0].marker.symbol[1],"x");
assert.equal(fig.traces[0].customdata[0][1],"1 · Scrape disponible");
assert.equal(fig.traces[0].customdata[1][1],"0 · Scrape no disponible");
assert.equal(fig.layout.legend.x,0.5);
assert.equal(fig.layout.legend.xanchor,"center");
assert.equal(fig.layout.xaxis.title,undefined);
assert.equal(fig.layout.margin.b,78);
assert.equal(fig.layout.legend.y*(fig.layout.height-90),-36);
for(const n of [2,3,8,9]){
 const q={...p,group:({2:"collection",3:"routers",8:"wan",9:"vlan"})[n]};
 const ids= n===2?["exporter","collector"]:n===3?["R-HQ","R-S1","R-S2"]:n===8?["WAN-END-HQ-s1p","WAN-END-HQ-s1b","WAN-END-HQ-s2p","WAN-END-HQ-s2b","WAN-END-S1-s1p","WAN-END-S1-s1b","WAN-END-S2-s2p","WAN-END-S2-s2b"]:[110,120,130,210,220,230,310,320,330].map(v=>"VLAN-"+v);
 q.series=ids.map(id=>({id,points:[]}));
 const f=h.figure(q,d=>d.toISOString(),{surface:"#fff",text:"#111",line:"#aaa"});
 assert.equal(f.layout.xaxis.title,undefined);
 assert.equal(f.layout.margin.b,78);
 assert(Math.abs(f.layout.legend.y*(f.layout.height-90)+36)<1e-9);
}
const light=h.figure(p,d=>d.toISOString(),{theme:"light",surface:"#fff",text:"#111",line:"#aaa"});
assert.notEqual(light.traces[0].marker.color,fig.traces[0].marker.color);
assert.equal(light.traces[0].marker.size,7);
assert.equal(fig.traces[0].marker.size,5);
assert.equal(light.traces[0].marker.symbol[1],"x");
for(const change of [
 q=>q.network_mutations_authorized=true,q=>q.series[0].scope="ADMIN_STATE_ONLY",
 q=>q.series[0].points.push([1301,1]),q=>q.series[0].points.push([1002,1]),
 q=>q.series[0].points[0][1]=2,q=>q.series[1]=q.series[0]
]) {
 const q=JSON.parse(JSON.stringify(p));change(q);
 assert.throws(()=>h.validate(q,"collection","5m"));
}
"""


class HistoryVisualTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node requerido para modelo visual")
    def test_real_marker_projection(self):
        result = subprocess.run(
            ["node","-e",SCRIPT,str(UI/"static/history.js")],
            capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_structure_and_fixed_read(self):
        html=(UI/"index.html").read_text(encoding="utf-8")
        js=(UI/"static/app.js").read_text(encoding="utf-8")
        for name in ("history-view","history-group","history-window","history-plot"):
            self.assertIn(f'id="{name}"',html)
        self.assertIn('script.src="/ui/static/plotly.js"',js)
        self.assertIn('debugRead("/api/v1/history/"+group+"/"+span,1048576)',js)
        self.assertIn("historyEpoch++",js)
        self.assertIn("window.Plotly.purge(historyPlot)",js)
        self.assertNotIn("https://",html)
        self.assertIn("history-state-key",html)
        self.assertIn("El color identifica el recurso",html)
