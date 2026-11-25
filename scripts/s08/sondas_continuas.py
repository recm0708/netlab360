#!/usr/bin/env python3
"""Adquisición Blackbox con destinos fijos y relés Unix sin privilegios."""
import argparse
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
from pathlib import Path
import re
import socket
import socketserver
import subprocess
import sys
import threading
from urllib.parse import urlencode
from urllib.request import ProxyHandler, build_opener

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "consola") if (ROOT / "consola").is_dir()
                else str(ROOT.parents[1] / "servicios/consola-s08"))
from api import slo_contract as S, probe_catalog as C

RUNTIME = Path("/run/netlab360-s08-observacion")
PORT = 9116
LIMIT = 65536
OPEN = build_opener(ProxyHandler({}))


def selection(path, origin=None):
    """No aceptar parámetros URL, destinos o módulos suministrados por el cliente."""
    if not isinstance(path, str) or not path.startswith("/probe/"):
        raise ValueError("UNKNOWN_PROBE")
    item = S.probe(path[len("/probe/"):])
    if origin is not None and item["origin"] != origin:
        raise ValueError("WRONG_PROBE_ORIGIN")
    return item


def metric(raw, name):
    lines = re.findall(rb"^" + name.encode() + rb" ([^\s]+)$", raw, re.M)
    if len(lines) != 1:
        raise ValueError("INVALID_PROBE_METRIC:" + name)
    value = float(lines[0])
    if not math.isfinite(value):
        raise ValueError("INVALID_PROBE_VALUE")
    return value


def checked_metrics(raw, item):
    if not 0 < len(raw) <= LIMIT or metric(raw, "probe_success") not in (0, 1):
        raise ValueError("INVALID_PROBE_BODY")
    duration = metric(raw, "probe_duration_seconds")
    if not 0 <= duration <= 5:
        raise ValueError("INVALID_PROBE_DURATION")
    if item["module"] == "http_service" and metric(raw, "probe_success") == 1:
        if metric(raw, "probe_http_status_code") != 200:
            raise ValueError("INVALID_HTTP_STATUS")
    # Proyectar únicamente métricas verificadas y no aceptar etiquetas externas.
    lines = [f'probe_success {int(metric(raw, "probe_success"))}',
             f"probe_duration_seconds {duration:.9f}"]
    if item["module"] == "http_service":
        code = metric(raw, "probe_http_status_code")
        if code != int(code) or not 0 <= code <= 599:
            raise ValueError("INVALID_HTTP_CODE")
        lines.append(f"probe_http_status_code {int(code)}")
    return ("\n".join(lines) + "\n").encode()


def verify_source(item):
    """Verificar identidad y ruta local sin usar sudo en cada adquisición."""
    pair = C.ROUTES[item["route"]]
    src, dst = C.ENDPOINTS[pair.origin], C.ENDPOINTS[pair.destination]
    def ip(*args):
        result = subprocess.run(["/usr/sbin/ip", "-j", "-4", *args],
                                capture_output=True, check=True, timeout=1)
        return json.loads(result.stdout)
    addresses = ip("addr", "show", "dev", src.interface)
    if len(addresses) != 1 or addresses[0].get("ifname") != src.interface:
        raise ValueError("SOURCE_INTERFACE")
    actual = [x["local"] for x in addresses[0]["addr_info"]
              if x.get("family") == "inet" and x.get("prefixlen") == 24]
    if actual != [src.address]:
        raise ValueError("SOURCE_ADDRESS")
    route = ip("route", "get", dst.address)
    if (len(route) != 1 or route[0].get("dev") != src.interface
            or route[0].get("prefsrc", route[0].get("src")) != src.address
            or route[0].get("gateway") != src.gateway):
        raise ValueError("SOURCE_ROUTE")


def probe(item):
    verify_source(item)
    query = urlencode({"module": item["module"], "target": item["target"]})
    with OPEN.open("http://127.0.0.1:9115/probe?" + query, timeout=4) as response:
        return checked_metrics(response.read(LIMIT + 1), item)


class BoundedThreads(socketserver.ThreadingMixIn):
    """Rechazar exceso de concurrencia en vez de crear trabajadores ilimitados."""
    daemon_threads = True
    def process_request(self, request, address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, address)
        except BaseException:
            self.slots.release()
            raise
    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.slots.release()


class Relay(BoundedThreads, socketserver.UnixStreamServer):
    def __init__(self, path, origin):
        self.origin = origin
        self.slots = threading.BoundedSemaphore(4)
        super().__init__(str(path), RelayHandler)


class RelayHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(6)
        try:
            line = self.rfile.readline(96)
            if not line.endswith(b"\n"):
                return
            item = selection(line[:-1].decode("ascii"), self.server.origin)
            raw = probe(item)
            self.wfile.write(raw)
        except (OSError, ValueError, subprocess.SubprocessError):
            # Un transporte fallido no se convierte en probe_success=0.
            return


def relay(origin):
    path = RUNTIME / origin.lower() / "probe.sock"
    if path.exists() or path.is_symlink():
        raise RuntimeError("RELAY_SOCKET_ALREADY_EXISTS")
    with Relay(path, origin) as server:
        path.chmod(0o600)
        server.serve_forever()


def acquire(item):
    path = RUNTIME / item["origin"].lower() / "probe.sock"
    with closing(socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)) as sock:
        sock.settimeout(6)
        sock.connect(str(path))
        sock.sendall(("/probe/" + item["id"] + "\n").encode("ascii"))
        sock.shutdown(socket.SHUT_WR)
        with sock.makefile("rb") as handle:
            raw = handle.read(LIMIT + 1)
    return checked_metrics(raw, item)


class Gateway(BoundedThreads, HTTPServer):
    def __init__(self, address):
        self.slots = threading.BoundedSemaphore(8)
        super().__init__(address, GatewayHandler)


class GatewayHandler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(7)

    def do_GET(self):
        try:
            item = selection(self.path)
        except ValueError:
            self.send_error(404)
            return
        try:
            raw = acquire(item)
        except (OSError, ValueError):
            self.send_error(503)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, *_):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("HQ", "S2", "gateway"))
    args = parser.parse_args()
    if args.mode == "gateway":
        with Gateway(("127.0.0.1", PORT)) as server:
            server.serve_forever()
    else:
        relay(args.mode)


if __name__ == "__main__":
    main()
