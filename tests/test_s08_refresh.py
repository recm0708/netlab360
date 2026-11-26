"""Verificamos preferencias y temporizador global con reloj controlado."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "servicios/consola-s08/ui/static/app.js"

SCRIPT = r"""
const fs=require("node:fs"),vm=require("node:vm"),assert=require("node:assert/strict");
const js=fs.readFileSync(process.argv[1],"utf8");
const start=js.indexOf("function observationSite(");
const end=js.indexOf("/* Fin de preferencias de actualización. */");
assert(start>=0&&end>start);
const ctx=vm.createContext({});
vm.runInContext(js.slice(start,end)+"\nthis.model={parseRefresh,refreshValue,refreshScheduler,automaticPage,observationSite,siteInventory};",ctx);
const m=ctx.model;
for(const p of ["/home","/topology","/wan","/lan","/services","/lacp","/sdn","/intelligence","/observability"])assert(m.automaticPage(p));
for(const p of ["/debug","/diagnostics","/administration","/unknown"])assert(!m.automaticPage(p));
assert.equal(m.observationSite({resource:"VLAN-230"}),"S1");
assert.equal(m.observationSite({resource:"WAN-END-HQ-s1p"}),"HQ");
assert.equal(m.observationSite({resource:"FAUCET"}),null);
const rows=[{resource:"R-HQ",quality:"VALID",details:{running:1}},{resource:"WAN-END-HQ-s1p",quality:"VALID",details:{admin_up:1}},{resource:"WAN-END-HQ-s1b",quality:"STALE",details:{admin_up:1}}];
assert.equal(m.siteInventory(rows,"HQ").running,1);
assert.equal(m.siteInventory(rows,"HQ").wan.up,1);
assert.equal(m.siteInventory(rows,"HQ").wan.known,1);
assert.equal(m.siteInventory(rows,"HQ").wan.total,2);
const clockStart=js.indexOf("  const panamaClock =");
const clockEnd=js.indexOf("  const fields = [",clockStart);
assert(clockStart>=0&&clockEnd>clockStart);
vm.runInContext(js.slice(clockStart,clockEnd)+"\nthis.formatPanama=formatPanama;",ctx);
assert.equal(ctx.formatPanama(new Date("2026-11-26T08:02:49Z")),"11/26/2026 · 03:02:49");
assert.equal(ctx.formatPanama(new Date("2026-11-26T05:00:00Z")),"11/26/2026 · 00:00:00");
assert.equal(ctx.formatPanama(new Date("2026-11-26T04:59:59Z")),"11/25/2026 · 23:59:59");
assert.equal(m.parseRefresh(null).seconds,5);
assert.equal(m.parseRefresh(null).auto,true);
for(const seconds of [5,10,15,30,60,300]){
  const value=m.refreshValue(false,seconds);
  assert.equal(m.parseRefresh(value).seconds,seconds);
  assert.equal(m.parseRefresh(value).auto,false);
}
for(const invalid of ["on:1","off:999","on:5:secret","x",{},null]){
  assert.equal(m.parseRefresh(invalid).seconds,5);
  assert.equal(m.parseRefresh(invalid).auto,true);
}
let count=0,seq=0;
const timers=new Map();
const clock={setInterval(fn,ms){const id=++seq;timers.set(id,{fn,ms});return id;},clearInterval(id){timers.delete(id);}};
const scheduler=m.refreshScheduler(reason=>{assert.equal(reason,"auto");count++;},clock);
scheduler.configure(m.parseRefresh("on:5"));
assert.equal(timers.size,1);
assert.equal([...timers.values()][0].ms,5000);
[...timers.values()][0].fn();assert.equal(count,1);
scheduler.configure(m.parseRefresh("on:30"));
assert.equal(timers.size,1);assert.equal([...timers.values()][0].ms,30000);
scheduler.configure(m.parseRefresh("off:30"));
assert.equal(timers.size,0);assert.equal(count,1);
scheduler.configure(m.parseRefresh("on:300"));
assert.equal([...timers.values()][0].ms,300000);
scheduler.stop();assert.equal(timers.size,0);
"""


class RefreshSchedulerTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Node requerido para temporizador")
    def test_preference_and_clock(self):
        result = subprocess.run(
            ["node", "-e", SCRIPT, str(APP)],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
