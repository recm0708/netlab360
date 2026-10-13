#!/usr/bin/env python3
"""NETLAB360 B3: API y panel NOC historico, solo lectura, sin dependencias."""
import argparse
import html
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

DEFAULT_DATA = Path.home() / "netlab360-bootstrap/evidencias/b3-linea-base"
PHASES = [
    ("normal", "WAN principal"),
    ("cambio_respaldo", "Conmutacion a respaldo"),
    ("respaldo", "WAN de respaldo"),
    ("cambio_principal", "Retorno a principal"),
    ("restaurada", "Principal restaurada"),
]


def load_files(directory):
    summary_file = directory / "b3-resumen-convergencia.json"
    metrics_file = directory / "b3-metricas-retrospectivas.prom"
    if not summary_file.is_file() or not metrics_file.is_file():
        raise ValueError("No existen ambos archivos B3 de linea base")
    if summary_file.stat().st_size > 2_000_000 or metrics_file.stat().st_size > 2_000_000:
        raise ValueError("Archivo de linea base demasiado grande")
    raw = json.loads(summary_file.read_text(encoding="utf-8"))
    metrics = metrics_file.read_text(encoding="utf-8")
    if not isinstance(raw, dict) or not isinstance(raw.get("fases"), dict):
        raise ValueError("Esquema JSON inesperado")
    if raw.get("tipo") != "analisis_retrospectivo":
        raise ValueError("Origen sin marca 'analisis_retrospectivo'")
    total = raw.get("muestras_totales")
    good = raw.get("exitosas")
    if type(total) is not int or type(good) is not int or total <= 0 or good < 0 or good > total:
        raise ValueError("Totales inconsistentes")
    n, successes = 0, 0
    for phase, _label in PHASES:
        entry = raw["fases"].get(phase)
        if not isinstance(entry, dict):
            raise ValueError("Falta la fase " + phase)
        samples, received, lost = (
            entry.get("muestras"), entry.get("recibidas"), entry.get("perdidas")
        )
        if not all(type(v) is int for v in (samples, received, lost)):
            raise ValueError("Conteos no enteros en " + phase)
        if samples < 0 or received < 0 or lost < 0 or received + lost != samples:
            raise ValueError("Conteos incorrectos en " + phase)
        n += samples
        successes += received
    if n != total or successes != good:
        raise ValueError("Totales de fases no coinciden")
    if "netlab360_icmp_samples{" not in metrics or "netlab360_icmp_losses{" not in metrics:
        raise ValueError("Metricas de linea base no reconocidas")
    return raw, metrics


def render_dashboard(data):
    total = int(data["muestras_totales"])
    ok = int(data["exitosas"])
    origin = html.escape(str(data.get("origen", "sin especificar")))
    table_rows = []
    bars = []
    for key, label in PHASES:
        entry = data["fases"][key]
        n, received, lost = (
            entry["muestras"], entry["recibidas"], entry["perdidas"]
        )
        routes = entry.get("rutas_observadas", {})
        if not isinstance(routes, dict):
            routes = {}
        routes_text = ", ".join(
            html.escape(str(route)) + ": " + html.escape(str(count))
            for route, count in routes.items()
        ) or "Sin rutas registradas"
        escaped_label = html.escape(label)
        table_rows.append(
            "<tr><th scope='row'>" + escaped_label + "</th><td>" + str(n) +
            "</td><td>" + str(received) + "</td><td>" + str(lost) +
            "</td><td>" + routes_text + "</td></tr>"
        )
        width = (n / total * 100) if total else 0
        bars.append(
            "<div class='baritem'><span>" + escaped_label + "</span>"
            "<div class='rail'><span style='width:" + f"{width:.2f}" +
            "%'></span></div><b>" + str(n) + "</b></div>"
        )
    loss = total - ok
    markup = """<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NETLAB360 | NOC historico</title>
<style>
:root { color-scheme: dark; font-family: system-ui,Segoe UI,sans-serif; }
* { box-sizing: border-box; }
body { margin: 0; background: #0b1424; color: #edf4ff; line-height: 1.5; }
main { width: min(1020px,94%); margin: 40px auto 70px; }
small, .muted { color: #b0bfd6; } h1 { font-size: 2.2rem; margin: 6px 0 0; }
.tag { display: inline-block; border: 1px solid #5684b5; border-radius: 999px;
padding: 5px 11px; color: #c9ddf9; font-weight: 600; font-size: .83rem; }
p { max-width: 800px; }
.cards { display:grid; grid-template-columns: repeat(auto-fit,minmax(170px,1fr)); gap: 14px; margin: 30px 0; }
.card,.panel { background: #122239; border: 1px solid #2a4260; border-radius: 14px; padding: 22px; }
.big { display: block; font-size: 2rem; font-weight: 700; margin-top: 5px; }
.panel { margin-top: 20px; overflow-x: auto; } h2 { font-size: 1.15rem; margin-top: 0; }
table { border-collapse: collapse; width: 100%; min-width: 640px; }
th,td { text-align:left; padding: 10px 12px; border-bottom: 1px solid #36506f; font-size:.91rem; }
th { color: #e6f1ff; } td { color:#dae5f5; }
.baritem { display:grid; grid-template-columns: 190px 1fr 35px; gap: 14px; align-items:center; margin: 15px 0; font-size:.91rem; }
.rail { height: 12px; border-radius: 12px; background:#263e5d; overflow:hidden; }
.rail span { display:block; background:#68b5e8; height:100%; border-radius: 12px; }
a { color:#a8d5ff; } footer { margin-top:32px; color:#afc1dc; font-size:.82rem; }
@media (max-width:600px) {.baritem{grid-template-columns:110px 1fr 25px;gap:8px;} h1{font-size:1.75rem;}}
</style></head><body><main>
<span class="tag">NETLAB360 • HISTORICO • NO EN VIVO</span>
<h1>Panel NOC — linea base B2</h1>
<p class="muted">Datos medidos durante un ensayo anterior con FRRouting/OSPF y WAN
principal/respaldo. La vista se carga desde un JSON local, no desde un router
actualmente desplegado, y <strong>no representa el estado actual de la red</strong>.</p>
<div class="cards">
<div class="card">Sondeos ICMP<span class="big">__TOTAL__</span></div>
<div class="card">Exitosos<span class="big">__GOOD__</span></div>
<div class="card">Fallidos observados<span class="big">__LOSS__</span></div>
<div class="card">Modo de datos<span class="big" style="font-size:1.2rem">Retrospectivo</span></div>
</div>
<section class="panel"><h2>Distribucion de muestras por fase</h2>__BARS__</section>
<section class="panel"><h2>Detalle por estado WAN</h2>
<table><thead><tr><th>Fase</th><th>Muestras</th><th>Recibidas</th>
<th>Fallidas</th><th>Rutas FIB observadas</th></tr></thead>
<tbody>__ROWS__</tbody></table></section>
<section class="panel"><h2>Fuente y acceso API</h2>
<p>CSV original: <code>__ORIGIN__</code></p>
<p><a href="/api/v1/baseline">/api/v1/baseline</a> ·
<a href="/metrics">/metrics</a> · <a href="/healthz">/healthz</a></p>
<p class="muted">El endpoint /metrics expone un resumen historico en formato
Prometheus. No significa que exista un scraper activo o alertas configuradas.</p>
</section>
<footer>Los sondeos discretos no garantizan cero perdidas entre mediciones.
El proyecto solo se publica en 127.0.0.1; use un tunel SSH local para
visualizarlo desde Windows.</footer>
</main></body></html>"""
    return (markup.replace("__TOTAL__", str(total))
            .replace("__GOOD__", str(ok))
            .replace("__LOSS__", str(loss))
            .replace("__BARS__", "\n".join(bars))
            .replace("__ROWS__", "\n".join(table_rows))
            .replace("__ORIGIN__", origin)).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path not in ("/", "/healthz", "/api/v1/baseline", "/metrics"):
            self.reply(404, b"Not found\n", "text/plain; charset=utf-8")
            return
        try:
            data, metrics = load_files(self.server.data_dir)
        except (OSError, ValueError, json.JSONDecodeError) as err:
            # Logs only, avoid exposing system paths/tracebacks to remote clients.
            self.log_error("Datos invalidos: %s", str(err))
            self.reply(503, b"Datos historicos no disponibles\n",
                       "text/plain; charset=utf-8")
            return
        if path == "/healthz":
            payload = {"status": "ok", "mode": "historical",
                       "live_monitoring": False, "samples": data["muestras_totales"]}
            self.reply(200, (json.dumps(payload) + "\n").encode(),
                       "application/json; charset=utf-8")
        elif path == "/api/v1/baseline":
            self.reply(200, (json.dumps(data, ensure_ascii=False) + "\n").encode(),
                       "application/json; charset=utf-8")
        elif path == "/metrics":
            self.reply(200, metrics.encode("utf-8"),
                       "text/plain; version=0.0.4; charset=utf-8")
        else:
            self.reply(200, render_dashboard(data), "text/html; charset=utf-8")

    def do_POST(self):
        self.reply(405, b"Read-only\n", "text/plain; charset=utf-8")

    def log_message(self, fmt, *args):
        print(datetime.now().astimezone().isoformat(timespec="seconds")
              + " NOC " + (fmt % args), flush=True)


def main():
    parser = argparse.ArgumentParser(description="NETLAB360 B3 dashboard historico, loopback")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()
    if args.port < 1024 or args.port > 65535:
        parser.error("Puerto debe estar entre 1024 y 65535")
    try:
        data, metrics = load_files(args.data_dir)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("B3_VALIDACION_ERROR:", error)
        return 3
    print("B3_DATOS_HISTORICOS: OK")
    print("B3_MUESTRAS:", data["muestras_totales"])
    print("B3_METRICAS_LINEAS:", len(metrics.splitlines()))
    if args.check:
        print("RESULTADO_B3_CHECK=0")
        return 0
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.data_dir = args.data_dir
    print(f"B3_NOC_LOCAL: http://127.0.0.1:{args.port}/", flush=True)
    print("B3_MODO: HISTORICO | NO EN VIVO | Ctrl+C para detener", flush=True)
    try:
        server.serve_forever(poll_interval=0.3)
    except KeyboardInterrupt:
        print("\nB3_DETENCION_SOLICITADA=SI")
    finally:
        server.server_close()
        print("B3_SERVIDOR_DETENIDO=SI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
