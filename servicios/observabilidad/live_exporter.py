#!/usr/bin/env python3
"""NETLAB360 B3: telemetria ACTUAL de dos routers FRR aislados (solo lectura).
Exclusivamente en 127.0.0.1. Sin Docker SDK, sin rutas del host modificadas.
No instala ni simula Prometheus. Permisos sudo -n solo para inspeccion.
"""
import argparse
import html
import json
import re
import socket
import subprocess
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path.home() / "netlab360-bootstrap/evidencias/b3-live"
HQ = "nl360-b2-r-hq"
S1 = "nl360-b2-r-s1"
SRC = "10.70.10.1"
DST = "10.71.10.1"
GUARD_IP = "192.168.47.40/24"
GUARD_GW = "default via 192.168.47.2 dev ens33"
LOCK = threading.RLock()
DATA = {"snapshot": None, "events": [], "counters": {
    "wan_down": 0, "wan_restored": 0, "route_changed": 0
}}
STOP = threading.Event()


def now():
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def command(argv, timeout=4):
    return subprocess.run(argv, capture_output=True, text=True,
                          timeout=timeout, check=False)


def management_guard():
    ip = command(["ip", "-4", "-br", "addr", "show", "ens33"])
    route = command(["ip", "-4", "route", "show", "default"])
    return (ip.returncode == 0 and GUARD_IP in ip.stdout
            and route.returncode == 0 and GUARD_GW in route.stdout)


def sudo_run(args):
    return command(["sudo", "-n", *args])


def inspect_router(name):
    r = sudo_run(["docker", "inspect", "-f",
                  "{{.State.Running}} {{.State.Pid}}", name])
    if r.returncode:
        # Docker CLI may return "Error: No such object" or
        # "error: no such object" depending on version/locale.
        message = (r.stderr + "\n" + r.stdout).lower()
        if "no such object" in message or "no such container" in message:
            return {"running": False, "pid": None}
        raise RuntimeError("No se pudo consultar Docker " + name
                           + ": " + r.stderr.strip()[:150])
    parts = r.stdout.strip().split()
    if len(parts) != 2:
        raise RuntimeError("Respuesta inspect inesperada para " + name)
    is_up = parts[0] == "true"
    if not parts[1].isdigit():
        raise RuntimeError("PID de Docker invalido")
    return {"running": is_up, "pid": int(parts[1]) if is_up else None}


def read_hq_interface(pid):
    r = sudo_run(["nsenter", "-t", str(pid), "-n",
                  "ip", "-j", "link", "show", "dev", "wan-p"])
    if r.returncode:
        # Puede aparecer brevemente durante la fase de despliegue.
        if "does not exist" in r.stderr or "Cannot find device" in r.stderr:
            return -1
        raise RuntimeError("Consulta interfaz wan-p: " + r.stderr.strip()[:150])
    value = json.loads(r.stdout)
    if not isinstance(value, list) or not value:
        raise RuntimeError("JSON ip link no valido")
    return 1 if "UP" in value[0].get("flags", []) else 0


def read_selected_route(pid):
    r = sudo_run(["nsenter", "-t", str(pid), "-n",
                  "ip", "-4", "route", "get", DST])
    if r.returncode:
        # Ausencia de ruta durante la transicion NO es error del exporter.
        if "Network is unreachable" in r.stderr or "unreachable" in r.stderr:
            return "none"
        raise RuntimeError("Consulta ruta: " + r.stderr.strip()[:150])
    m = re.search(r"\bdev\s+(wan-[pb])\b", r.stdout)
    return m.group(1) if m else "none"


def collect():
    sample = {
        "observed_at": now(),
        "observed_unix": time.time(),
        "source_ok": 0,
        "error": "",
        "topology": "unknown",
        "routers": {"hq": 0, "s1": 0},
        "wan_primary_admin_up": -1,
        "selected_link": "none",
        "route_target": DST,
        "mode": "live",
        "poll_interval_note": "Sondeo discreto; no garantiza deteccion instantanea"
    }
    try:
        if not management_guard():
            raise RuntimeError("Red administrativa fuera de guardia; detener observacion")
        hq = inspect_router(HQ)
        s1 = inspect_router(S1)
        sample["routers"] = {"hq": int(hq["running"]), "s1": int(s1["running"])}
        if not hq["running"] and not s1["running"]:
            sample["topology"] = "offline"
        elif hq["running"] and s1["running"]:
            sample["topology"] = "active"
            sample["wan_primary_admin_up"] = read_hq_interface(hq["pid"])
            sample["selected_link"] = read_selected_route(hq["pid"])
        else:
            sample["topology"] = "partial"
        sample["source_ok"] = 1
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as err:
        sample["error"] = str(err)[:240]
        sample["topology"] = "degraded"
    return sample


def store_event(kind, severity, snap):
    event = {
        "observed_at": snap["observed_at"],
        "event": kind,
        "severity": severity,
        "primary_admin_up": snap["wan_primary_admin_up"],
        "selected_link": snap["selected_link"],
        "topology": snap["topology"]
    }
    DATA["events"].append(event)
    with (ROOT / "b3-wan-live-events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"{now()} EVENTO_B3={kind} severidad={severity} ruta={snap['selected_link']}",
          flush=True)


def record(snapshot):
    with LOCK:
        prev = DATA["snapshot"]
        active = snapshot["topology"] == "active" and snapshot["source_ok"] == 1
        prev_active = prev is not None and prev["topology"] == "active" and prev["source_ok"] == 1
        if prev is not None and prev["topology"] != "active" and active:
            store_event("TOPOLOGY_STARTED", "info", snapshot)
        if prev_active and not active and snapshot["topology"] == "offline":
            store_event("TOPOLOGY_STOPPED", "info", snapshot)
        if prev_active and active:
            old = prev["wan_primary_admin_up"]
            new = snapshot["wan_primary_admin_up"]
            if old == 1 and new == 0:
                DATA["counters"]["wan_down"] += 1
                store_event("WAN_PRIMARY_DOWN", "warning", snapshot)
            elif old == 0 and new == 1:
                DATA["counters"]["wan_restored"] += 1
                store_event("WAN_PRIMARY_RESTORED", "info", snapshot)
            old_route = prev["selected_link"]
            new_route = snapshot["selected_link"]
            if old_route != new_route:
                DATA["counters"]["route_changed"] += 1
                store_event("WAN_ROUTE_CHANGED", "info", snapshot)
        DATA["snapshot"] = snapshot


def monitor(interval):
    while not STOP.is_set():
        snap = collect()
        record(snap)
        if snap["source_ok"] == 0:
            print(f"{now()} TELEMETRIA_DEGRADADA={snap['error']}", flush=True)
        STOP.wait(interval)


def get_state():
    with LOCK:
        snap = dict(DATA["snapshot"] or {})
        events = list(DATA["events"])
        counters = dict(DATA["counters"])
    age = max(0, time.time() - snap.get("observed_unix", 0))
    snap["age_seconds"] = round(age, 2)
    snap["fresh"] = bool(snap.get("source_ok") == 1 and age <= 5)
    return snap, events, counters


def metrics(snap, events, counters):
    lines = [
        "# HELP netlab360_live_source_up 1 when fresh source query succeeds",
        "# TYPE netlab360_live_source_up gauge",
        f"netlab360_live_source_up {int(snap.get('fresh', False))}",
        "# HELP netlab360_live_router_running Docker router process running",
        "# TYPE netlab360_live_router_running gauge",
    ]
    for router in ("hq", "s1"):
        lines.append(f'netlab360_live_router_running{{router="{router}"}} '
                     f'{snap.get("routers", {}).get(router, 0)}')
    lines.extend([
        "# HELP netlab360_live_wan_primary_admin_up HQ WAN-P admin state (-1 unavailable)",
        "# TYPE netlab360_live_wan_primary_admin_up gauge",
        "netlab360_live_wan_primary_admin_up "
        + str(snap.get("wan_primary_admin_up", -1)),
        "# HELP netlab360_live_wan_selected HQ route to LAN S1 selected by kernel",
        "# TYPE netlab360_live_wan_selected gauge",
    ])
    for link in ("wan-p", "wan-b"):
        lines.append(f'netlab360_live_wan_selected{{link="{link}"}} '
                     f'{int(snap.get("selected_link") == link)}')
    lines.extend([
        "# HELP netlab360_live_last_poll_timestamp_seconds Time of latest read",
        "# TYPE netlab360_live_last_poll_timestamp_seconds gauge",
        f'netlab360_live_last_poll_timestamp_seconds {snap.get("observed_unix", 0):.3f}',
        "# HELP netlab360_live_wan_events_total WAN transitions observed since process start",
        "# TYPE netlab360_live_wan_events_total counter",
    ])
    for label, key in (("down", "wan_down"), ("restored", "wan_restored"),
                       ("route_changed", "route_changed")):
        lines.append(f'netlab360_live_wan_events_total{{event="{label}"}} '
                     f'{counters[key]}')
    return "\n".join(lines) + "\n"


def dashboard(snap, events):
    state = snap.get("topology", "unknown")
    primary = snap.get("wan_primary_admin_up", -1)
    selected = snap.get("selected_link", "none")
    fresh = snap.get("fresh", False)
    banner = "EN VIVO · CONSULTA ACTUAL" if fresh else "DATOS DEGRADADOS / SIN FRESCURA"
    line_rows = []
    for e in events[-16:][::-1]:
        line_rows.append(
            "<tr><td>" + html.escape(e["observed_at"]) + "</td><td>"
            + html.escape(e["event"]) + "</td><td>"
            + html.escape(e["severity"]) + "</td><td>"
            + html.escape(e["selected_link"]) + "</td></tr>"
        )
    if not line_rows:
        line_rows = ["<tr><td colspan='4'>Sin eventos registrados en esta ejecucion</td></tr>"]
    return ("""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta http-equiv="refresh" content="2"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NETLAB360 | NOC telemetria viva</title>
<style>
:root{color-scheme:dark;font-family:system-ui,Segoe UI,sans-serif}
body{background:#0b1424;color:#f0f6ff;margin:0}
main{max-width:1024px;margin:36px auto;padding:0 20px}
h1{font-size:2rem}.pill{display:inline-block;border:1px solid #66b4e6;border-radius:30px;padding:7px 14px;color:#b8ddfa}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:15px;margin:26px 0}
.card{background:#14243d;border:1px solid #395171;padding:22px;border-radius:13px}
.card strong{display:block;font-size:1.8rem;margin-top:12px}
table{border-collapse:collapse;width:100%}th,td{border-bottom:1px solid #38516f;text-align:left;padding:10px;font-size:.9rem}
a{color:#9ed6ff}.note{color:#b5c6dc}code{font-size:.85rem}
</style></head><body><main>
<div class="pill">""" + html.escape(banner) + """</div>
<h1>NETLAB360 — Estado FRR dual-WAN</h1>
<p class="note">Datos obtenidos por sondeo de Docker y FIB de R-HQ. Actualizacion cada 2 segundos.
Esto NO significa que Prometheus ya este instalado o consultando. Sin routers, estado OFFLINE.</p>
<div class="grid">
<div class="card">Topologia<strong>""" + html.escape(state.upper()) + """</strong></div>
<div class="card">WAN primaria (HQ)<strong>""" + ("UP" if primary == 1 else "DOWN" if primary == 0 else "N/A") + """</strong></div>
<div class="card">Ruta a S1<strong>""" + html.escape(selected) + """</strong></div>
<div class="card">Frescura<strong>""" + (f"{snap.get('age_seconds', 0):.1f}s" if fresh else "DEGRADADA") + """</strong></div>
</div>
<section class="card"><h2>Eventos WAN observados</h2>
<table><thead><tr><th>Timestamp</th><th>Evento</th><th>Severidad</th><th>Ruta</th></tr></thead>
<tbody>""" + "\n".join(line_rows) + """</tbody></table></section>
<p><a href="/healthz">/healthz</a> · <a href="/api/v1/live">/api/v1/live</a> ·
<a href="/api/v1/events">/api/v1/events</a> · <a href="/metrics">/metrics</a></p>
<p class="note">Fuente exclusivamente local 127.0.0.1. Eventos detectados por muestreo;
intervalos y perdida entre sondeos no medidos. Archivo JSONL fuera del repositorio.</p>
</main></body></html>""").encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def answer(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        target = urlsplit(self.path).path
        snap, events, counters = get_state()
        if target == "/healthz":
            payload = {"status": "ok" if snap.get("fresh") else "degraded",
                       "source": "live", "live_monitoring": True,
                       "topology": snap.get("topology", "unknown"),
                       "fresh": snap.get("fresh"), "age_seconds": snap.get("age_seconds")}
            self.answer(200 if snap.get("fresh") else 503,
                        (json.dumps(payload) + "\n").encode(), "application/json")
        elif target == "/api/v1/live":
            self.answer(200, (json.dumps(snap, ensure_ascii=False) + "\n").encode(),
                        "application/json")
        elif target == "/api/v1/events":
            self.answer(200, (json.dumps({"events": events, "counters": counters},
                                         ensure_ascii=False) + "\n").encode(),
                        "application/json")
        elif target == "/metrics":
            self.answer(200, metrics(snap, events, counters).encode(),
                        "text/plain; version=0.0.4; charset=utf-8")
        elif target == "/":
            self.answer(200, dashboard(snap, events), "text/html; charset=utf-8")
        else:
            self.answer(404, b"No encontrado\n", "text/plain")

    def do_POST(self):
        self.answer(405, b"Solo lectura\n", "text/plain")

    def log_message(self, format, *args):
        print(f"{now()} HTTP {format % args}", flush=True)


def main():
    p = argparse.ArgumentParser(description="Telemetria FRRouting en loopback")
    actions = p.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--serve", action="store_true")
    p.add_argument("--port", type=int, default=9108)
    p.add_argument("--interval", type=float, default=1.0)
    args = p.parse_args()
    if args.interval < 0.5 or args.interval > 10:
        p.error("intervalo entre 0.5 y 10 segundos")
    if not (1024 <= args.port <= 65535):
        p.error("puerto fuera de rango")
    if socket.gethostname() != "netlab360-lab":
        p.error("hostname inesperado")
    if not management_guard():
        print("ERROR: red administrativa no coincide con lo esperado")
        return 3
    if command(["sudo", "-n", "-v"]).returncode != 0:
        print("ERROR: antes ejecutar sudo -v en ESTA terminal; no ejecutar como root")
        return 3
    snap = collect()
    print("B3_LIVE_PREFLIGHT=" + ("OK" if snap["source_ok"] else "ERROR"))
    print("B3_TOPOLOGIA=" + snap["topology"].upper())
    if snap["source_ok"] == 0:
        print("B3_LIVE_ERROR=" + snap["error"])
        return 4
    if args.check:
        print("RESULTADO_B3_LIVE_CHECK=0")
        return 0
    ROOT.mkdir(parents=True, exist_ok=True)
    # Registro JSONL de esta ejecucion solamente; no sobreescribir logs previos.
    path = ROOT / "b3-wan-live-events.jsonl"
    if path.exists():
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path.rename(ROOT / ("b3-wan-live-events-" + stamp + ".jsonl"))
    record(snap)
    worker = threading.Thread(target=monitor, args=(args.interval,), daemon=True)
    worker.start()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.daemon_threads = True
    print(f"B3_LIVE_LOCAL=http://127.0.0.1:{args.port}/", flush=True)
    print(f"B3_EVENTOS_LOCAL={path}", flush=True)
    print("B3_LIVE_MODO=EN_VIVO_SONDEO | NO_PROMETHEUS | CTRL_C_DETIENE", flush=True)
    try:
        server.serve_forever(poll_interval=0.3)
    except KeyboardInterrupt:
        print("B3_LIVE_PARADA_SOLICITADA=SI", flush=True)
    finally:
        STOP.set()
        server.server_close()
        worker.join(timeout=6)
        print("B3_LIVE_SERVIDOR_DETENIDO=SI", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
