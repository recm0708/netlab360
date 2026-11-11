#!/usr/bin/env python3
"""NETLAB360 S05: servicio HTTP activo/respaldo de sedes HQ y S1.

Una instancia por network namespace S05, sin privilegios, en systemd.
El frontal consulta dos backends definidos en código en cada solicitud.
Una sola VM demuestra redundancia lógica de aplicación, NO HA física.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

SERVICE = "netlab360-s05-ha"
BACKENDS = (
    {"id": "BACKEND_HQ", "site": "HQ", "address": "10.70.20.21",
     "port": 8088, "network": "nl360-s05-ha-hq"},
    {"id": "BACKEND_S1", "site": "S1", "address": "10.71.20.21",
     "port": 8088, "network": "nl360-s05-ha-s1"},
)
FRONTEND = {"id": "FRONTAL_HQ", "site": "HQ", "address": "10.70.20.23",
            "port": 8080, "network": "nl360-s05-ha-fe"}
ROLES = {"backend-hq": BACKENDS[0], "backend-s1": BACKENDS[1],
         "frontend-hq": FRONTEND}
TIMEOUT = 0.7


def now_panama() -> str:
    return datetime.now(ZoneInfo("America/Panama")).isoformat(timespec="seconds")


def backend_health(backend: dict) -> dict:
    """Solicitud real con identidad validada; no aceptamos upstream inventado."""
    url = f"http://{backend['address']}:{backend['port']}/healthz"
    request = Request(url, headers={"Accept": "application/json",
                                   "Cache-Control": "no-store"})
    with urlopen(request, timeout=TIMEOUT) as response:
        if response.status != 200:
            raise ValueError("Upstream sin estado HTTP 200")
        raw = response.read(4096)
    value = json.loads(raw)
    if (not isinstance(value, dict) or
            value.get("service") != SERVICE or
            value.get("role") != "backend" or
            value.get("id") != backend["id"] or
            value.get("site") != backend["site"] or
            value.get("status") != "healthy"):
        raise ValueError("Identidad de backend no coincide")
    return value


def choose_backend(reader=backend_health) -> tuple[dict, dict, str] | None:
    """Preferencia HQ; S1 únicamente cuando HQ no responde válidamente."""
    for index, backend in enumerate(BACKENDS):
        try:
            health = reader(backend)
        except (OSError, ValueError, HTTPError, URLError, TimeoutError,
                json.JSONDecodeError):
            continue
        return backend, health, "PRINCIPAL" if index == 0 else "RESPALDO"
    return None


def payload(role: str, reader=backend_health) -> tuple[int, dict]:
    if role in ("backend-hq", "backend-s1"):
        backend = ROLES[role]
        return 200, {"service": SERVICE, "role": "backend",
                     "id": backend["id"], "site": backend["site"],
                     "status": "healthy", "observed_at_panama": now_panama()}
    selection = choose_backend(reader)
    if selection is None:
        return 503, {"service": SERVICE, "role": "frontend",
                     "id": "FRONTAL_HQ", "status": "unavailable",
                     "active_backend": None, "selected_path": None,
                     "observed_at_panama": now_panama()}
    backend, health, path = selection
    return 200, {"service": SERVICE, "role": "frontend",
                 "id": "FRONTAL_HQ", "status": "available",
                 "active_backend": backend["id"],
                 "active_site": backend["site"],
                 "selected_path": path,
                 "backend_status": health["status"],
                 "observed_at_panama": now_panama()}


def handler(role: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "NETLAB360-HA/1"

        def do_GET(self):
            if self.path not in ("/", "/healthz", "/api/v1/service"):
                self.send_error(404, "Ruta no registrada")
                return
            code, data = payload(role)
            raw = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(raw)))
            if data.get("active_backend"):
                self.send_header("X-Netlab360-Backend", data["active_backend"])
                self.send_header("X-Netlab360-Path", data["selected_path"])
            self.end_headers()
            self.wfile.write(raw)

        def log_message(self, fmt, *args):
            print(f"S05_HTTP_{role} " + (fmt % args), flush=True)

    return Handler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=tuple(ROLES))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        assert BACKENDS[0]["address"] != BACKENDS[1]["address"]
        assert set(ROLES) == {"backend-hq", "backend-s1", "frontend-hq"}
        print("S05_HTTP_CODIGO=OK")
        print("S05_HTTP_SERVIDORES_EN_EJECUCION=NO_COMPROBADOS")
        return 0
    if not args.role:
        parser.error("Se requiere --role para iniciar el servicio")
    node = ROLES[args.role]
    bind = (node["address"], node["port"])
    with ThreadingHTTPServer(bind, handler(args.role)) as server:
        server.daemon_threads = True
        print(f"S05_HTTP_ROLE={args.role} BIND={bind[0]}:{bind[1]}", flush=True)
        server.serve_forever(poll_interval=0.25)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except OSError as exc:
        print(f"S05_HTTP_ERROR={type(exc).__name__}:{exc}", file=sys.stderr)
        sys.exit(2)
