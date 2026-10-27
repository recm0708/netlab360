#!/usr/bin/env python3
"""NETLAB360 S04 — NOC central y por sede, sin escribir en la infraestructura.

Solo agrega API local de exporter 9110 y Prometheus 9091. El panel no genera
estados sintéticos, no modifica Docker/FRR/Tofu y nunca publica en VMnet8.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import subprocess
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

EXPORTER = "http://127.0.0.1:9110"
PROMETHEUS = "http://127.0.0.1:9091"
EXPECTED_SITES = ("HQ", "S1", "S2")
JOB = "netlab360-s04-multisede"
FRESHNESS_MAX_SECONDS = 15.0
ADMIN_IP = "192.168.47.40/24"
ADMIN_GATEWAY = "default via 192.168.47.2 dev ens33"

PAGE = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NETLAB360 | Centro de operaciones de red</title>
<style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#081523;color:#e7eef7}
*{box-sizing:border-box}body{margin:0}header{padding:24px clamp(20px,5vw,58px);background:#10243b;border-bottom:1px solid #24405e;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}
h1{margin:0;font-size:1.7rem;letter-spacing:.02em}h2{font-size:1.18rem;margin:8px 0 12px}h3{font-size:1rem;margin:2px 0 12px}
.sub{color:#9bb1ca;font-size:.91rem;margin-top:4px}.small{color:#9bb1ca;font-size:.82rem}
main{max-width:1350px;margin:auto;padding:25px clamp(16px,4vw,48px)}
nav{display:flex;gap:8px;margin:14px 0 22px;flex-wrap:wrap}
button{background:#172d45;border:1px solid #34506e;color:#e7eef7;padding:10px 18px;border-radius:11px;cursor:pointer;font:inherit}
button[aria-pressed=true]{background:#245c7d;border-color:#69b8db}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(185px,1fr));gap:12px;margin-bottom:24px}
.card{border:1px solid #2b455e;border-radius:15px;background:#12243a;padding:17px;min-width:0}
.big{font-size:1.35rem;font-weight:700;margin:8px 0}.tag{display:inline-flex;align-items:center;border-radius:30px;padding:4px 10px;font-size:.8rem;font-weight:600;background:#314157;color:#e9f0fa}
.active{background:#154b42;color:#a1f4d3}.offline{background:#455161;color:#eef2f6}.partial{background:#644a20;color:#ffe1a4}
.unknown{background:#673241;color:#ffc7d2}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(265px,1fr));gap:14px}
.data{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;font-size:.86rem}
.data span{border:1px solid #2a3f56;border-radius:7px;padding:7px;overflow-wrap:anywhere}
.section{margin-top:30px}.alert{padding:11px 13px;border:1px solid #536278;border-radius:9px;margin:8px 0;background:#182f46}
footer{border-top:1px solid #29445b;margin-top:32px;padding-top:16px;color:#9ab2ca;line-height:1.6;font-size:.85rem}
</style>
</head><body>
<header>
<div><h1>NETLAB360 <span class="small">/ NOC</span></h1><div class="sub">Observabilidad multisede · datos reales de Ubuntu / Docker / Prometheus</div></div>
<div class="small" id="stamp">Consultando fuentes…</div></header>
<main>
<nav aria-label="Vistas del laboratorio">
<button data-site="ALL" aria-pressed="true">Vista central</button>
<button data-site="HQ" aria-pressed="false">Sede HQ</button>
<button data-site="S1" aria-pressed="false">Sucursal S1</button>
<button data-site="S2" aria-pressed="false">Sucursal S2</button>
</nav>
<div class="metrics" id="metrics"></div>
<section class="section"><h2 id="place-title">Vista central de las tres sedes</h2><div class="grid" id="sites"></div></section>
<section class="section"><h2>Alertas de Prometheus S04</h2><p class="small">Los datos provienen de /api/v1/alerts. Sin Alertmanager ni notificaciones externas verificadas.</p><div id="alerts"></div></section>
<footer>La presencia de un contenedor no certifica OSPF Full ni HTTP. OFFLINE indica topología intencionalmente desmontada cuando la fuente es fiable. UNKNOWN significa que la observación no es confiable; no implica falla física. Las interfaces con estado −1 no representan una caída WAN. Actualización cada 3 segundos, exclusivamente en localhost.</footer>
</main>
<script>
"use strict";
let selection="ALL";
let last=null;
const $=id=>document.getElementById(id);
const esc=x=>String(x===null||x===undefined?"—":x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const tag=(text,cls)=>'<span class="tag '+esc(cls)+'">'+esc(text)+'</span>';
const statusClass=s=>(["active","offline","partial","unknown"].includes(s)?s:"unknown");
function slot(title,value,small,cls){
return '<div class="card"><div class="small">'+esc(title)+'</div><div class="big">'+(cls?tag(value,cls):esc(value))+'</div><div class="small">'+esc(small)+'</div></div>';
}
function wanValue(n){return n===1?"UP admin":n===0?"DOWN admin":"Sin observación";}
function render(data){
last=data;
const t=data.telemetry||{},p=data.prometheus||{};
const reliable=t.available&&t.fresh&&t.source_ok;
const state=reliable?t.topology:"unknown";
$("stamp").textContent="Última consulta: "+(data.collected_at_utc||"—")+" · Auto-refresh 3 s";
const siteIds=selection==="ALL"?["HQ","S1","S2"]:[selection];
$("place-title").textContent=selection==="ALL"?"Vista central de las tres sedes":"Vista de "+selection;
const sites=t.sites||{};
let cards="";
for(const site of siteIds){
const s=reliable?sites[site]:null;
const links=s&&s.wan||{},vlans=s&&s.vlans||{};
const any=s!==null&&s!==undefined;
const run=any?(s.running===1?"Contenedor activo":"Contenedor detenido"):"Dato no disponible";
const ls=Object.keys(links).sort().map(n=>'<span>'+esc(n)+": "+esc(wanValue(links[n].admin_up))+'</span>').join("");
const vs=Object.keys(vlans).sort().map(n=>'<span>VLAN '+esc(n)+": "+esc(wanValue(vlans[n].admin_up))+'</span>').join("");
cards+='<article class="card"><h3>'+esc(site)+'</h3>'+tag(run,(!any?"unknown":s.running===1?"active":"offline"))+
'<p class="small">Interfaces WAN</p><div class="data">'+(ls||'<span>Sin datos WAN</span>')+
'</div><p class="small">Subinterfaces VLAN</p><div class="data">'+(vs||'<span>Sin datos VLAN</span>')+'</div></article>';
}
$("sites").innerHTML=cards;
const alertsKnown=p.available===true&&p.alerts_known===true;
const rawAlerts=alertsKnown?(p.alerts||[]):[];
const alerts=rawAlerts.filter(a=>{
if(selection==="ALL")return true;
const labels=a.labels||{};
return !labels.site||labels.site===selection;
});
$("metrics").innerHTML=
slot("Topología",reliable?state.toUpperCase():"UNKNOWN",reliable?"Fuente fiable":"No confundir con enlace caído",statusClass(state))+
slot("Muestreo exporter",t.fresh&&t.source_ok?"FRESCO":"NO FIABLE",t.age_seconds===null?"Edad no disponible":"Antigüedad "+t.age_seconds+" s",(t.fresh&&t.source_ok)?"active":"unknown")+
slot("Prometheus",p.available===true?"DISPONIBLE":"NO DISPONIBLE","Scrape "+(p.scrape||"unknown"),p.available===true&&p.scrape==="up"?"active":"unknown")+
slot("Alertas vigentes",alertsKnown?String(alerts.length):"DESCONOCIDAS",alertsKnown?"Estado consultado":"No se pudo consultar /api/v1/alerts",alertsKnown?(alerts.length>0?"partial":"active"):"unknown");
if(!alertsKnown){
$("alerts").innerHTML='<div class="alert">Estado de alertas desconocido: '+esc(p.error||"Sin respuesta confirmada")+'</div>';
}else if(!alerts.length){
$("alerts").innerHTML='<div class="alert">Sin alertas activas registradas por Prometheus para esta vista.</div>';
}else{
$("alerts").innerHTML=alerts.map(a=>'<div class="alert">'+tag(a.state||"active","partial")+" "+esc(a.labels&&a.labels.alertname||"Alerta")+
' · '+esc(a.annotations&&a.annotations.summary||"Sin resumen")+
'<div class="small">Inicio: '+esc(a.activeAt||"—")+'</div></div>').join("");
}
}
async function refresh(){
try{
const r=await fetch("/api/v1/overview",{cache:"no-store"});
if(!r.ok)throw Error("HTTP "+r.status);
render(await r.json());
}catch(e){
$("stamp").textContent="Panel no puede consultar su API: "+e.message;
$("metrics").innerHTML=slot("NOC", "UNKNOWN", "API local sin respuesta", "unknown");
$("sites").textContent="No es posible afirmar el estado de las sedes.";
$("alerts").textContent="Estado de alertas desconocido.";
}
}
document.querySelectorAll("button[data-site]").forEach(b=>b.addEventListener("click",()=>{
selection=b.dataset.site;
document.querySelectorAll("button[data-site]").forEach(x=>x.setAttribute("aria-pressed",String(x===b)));
if(last)render(last);
}));
refresh();
setInterval(refresh,3000);
</script></body></html>"""


def utc_now():
    return datetime.now(timezone.utc)


def local_guard(runner=subprocess.run, hostname=None) -> None:
    if (hostname or socket.gethostname()) != "netlab360-lab":
        raise RuntimeError("hostname administrativo inesperado")
    for argv, required in (
        (["ip", "-4", "-br", "address", "show", "ens33"], ADMIN_IP),
        (["ip", "-4", "route", "show", "default"], ADMIN_GATEWAY),
    ):
        result = runner(argv, capture_output=True, text=True, timeout=4, check=False)
        if result.returncode or required not in result.stdout:
            raise RuntimeError("proteccion administrativa: " + argv[-1])


def get_json(url: str, timeout=3) -> dict:
    if not url.startswith((EXPORTER + "/", PROMETHEUS + "/")):
        raise ValueError("fuente HTTP no autorizada")
    with urlopen(url, timeout=timeout) as r:
        return json.load(r)


def normalize_telemetry(snapshot: dict | None, now: datetime | None = None) -> dict:
    base = {"available": False, "source_ok": False, "fresh": False,
            "age_seconds": None, "topology": "unknown", "sites": {}, "error": ""}
    if not isinstance(snapshot, dict):
        base["error"] = "API exporter sin respuesta valida"
        return base
    base["available"] = True
    base["source_ok"] = snapshot.get("source_ok") is True
    timestamp = snapshot.get("observed_at_utc")
    try:
        when = datetime.fromisoformat(str(timestamp))
        if when.tzinfo is None:
            raise ValueError("sin zona horaria")
        age = ((now or utc_now()) - when).total_seconds()
        base["age_seconds"] = round(age, 2)
        base["fresh"] = 0 <= age <= FRESHNESS_MAX_SECONDS
    except (ValueError, TypeError, OverflowError):
        base["error"] = "marca temporal invalida"
    mode = snapshot.get("topology")
    if base["source_ok"] and base["fresh"] and mode in ("offline", "partial", "active"):
        sites = snapshot.get("sites")
        if (isinstance(sites, dict)
                and set(sites) == set(EXPECTED_SITES)
                and all(isinstance(sites[s], dict) for s in EXPECTED_SITES)):
            base["topology"] = mode
            base["sites"] = sites
        else:
            base["error"] = "sedes del exporter incompletas"
    elif not base["error"]:
        base["error"] = "fuente no fiable, sin datos actuales o sin disponibilidad"
    return base


def normalize_prometheus(targets: dict | None, alerts: dict | None,
                         error: str = "") -> dict:
    p = {"available": False, "scrape": "unknown", "alerts_known": False,
         "alerts": [], "error": error}
    if not (isinstance(targets, dict) and isinstance(alerts, dict)):
        if not p["error"]:
            p["error"] = "Prometheus /targets o /alerts no disponible"
        return p
    if targets.get("status") != "success" or alerts.get("status") != "success":
        p["error"] = "API Prometheus reporto fallo"
        return p
    matches = [t for t in targets.get("data", {}).get("activeTargets", [])
               if t.get("labels", {}).get("job") == JOB]
    p["scrape"] = matches[0].get("health", "unknown") if len(matches) == 1 else "unknown"
    p["scrape"] = p["scrape"] if p["scrape"] in ("up", "down") else "unknown"
    incoming = alerts.get("data", {}).get("alerts")
    if not isinstance(incoming, list):
        p["error"] = "Prometheus devolvio lista de alertas invalida"
        return p
    p["available"] = True
    p["alerts_known"] = True
    p["alerts"] = incoming[:50]
    return p


def overview(reader=get_json, now=None) -> dict:
    response = {"project": "NETLAB360", "phase": "S04",
                "collected_at_utc": (now or utc_now()).isoformat(timespec="seconds"),
                "telemetry": {}, "prometheus": {}}
    try:
        observation = reader(EXPORTER + "/api/v1/state")
    except (OSError, ValueError, TimeoutError, KeyError) as exc:
        response["telemetry"] = normalize_telemetry(None)
        response["telemetry"]["error"] = type(exc).__name__
    else:
        response["telemetry"] = normalize_telemetry(observation, now)
    try:
        targets = reader(PROMETHEUS + "/api/v1/targets")
        alerts = reader(PROMETHEUS + "/api/v1/alerts")
    except (OSError, ValueError, TimeoutError, KeyError) as exc:
        response["prometheus"] = normalize_prometheus(None, None, type(exc).__name__)
    else:
        response["prometheus"] = normalize_prometheus(targets, alerts)
    return response


def serve(port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def send_body(self, code: int, body: bytes, content_type: str):
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                self.send_body(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            elif path == "/healthz":
                value = {"service": "netlab360-s04-noc", "healthy": True,
                         "note": "salud API NOC, no disponibilidad de infraestructura"}
                self.send_body(200, json.dumps(value).encode(), "application/json")
            elif path == "/api/v1/overview":
                self.send_body(200, json.dumps(overview(), ensure_ascii=False).encode(),
                               "application/json; charset=utf-8")
            else:
                self.send_body(404, b"not found\n", "text/plain")

        def do_POST(self):
            self.send_body(405, b"method not allowed\n", "text/plain")

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"S04_NOC_URL=http://127.0.0.1:{port}/", flush=True)
    print("S04_NOC_SOLO_LECTURA=SI", flush=True)
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("S04_NOC_DETENIDO=SI", flush=True)


def main() -> None:
    cli = argparse.ArgumentParser(description="NETLAB360 S04: panel local de tres sedes")
    group = cli.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--once", action="store_true")
    group.add_argument("--serve", action="store_true")
    cli.add_argument("--port", type=int, default=9120)
    args = cli.parse_args()
    if not 1024 <= args.port <= 65535:
        cli.error("puerto no valido")
    local_guard()
    if args.check:
        print("S04_NOC_PREFLIGHT=OK")
        print("S04_NOC_NO_CAMBIOS=SI")
    elif args.once:
        print(json.dumps(overview(), indent=2, ensure_ascii=False, sort_keys=True))
    else:
        serve(args.port)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError) as exc:
        print("S04_NOC_ERROR=" + str(exc))
        raise SystemExit(2)
