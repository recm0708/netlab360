#!/usr/bin/env python3
"""NETLAB360 S04: observacion multisede de solo lectura, aislada del exporter B3.

El SoT es la referencia de elementos ESPERADOS, no una prueba de disponibilidad.
Estado apagado != fuente de observacion inalcanzable. No crea redes ni contenedores.
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

SOT_PATH = Path.home() / "netlab360-bootstrap/s03/rendered/sot-s03.json"
ADMIN_IP = "192.168.47.40/24"
ADMIN_ROUTE = "default via 192.168.47.2 dev ens33"
EXPECTED = {"R-HQ": 4, "R-S1": 2, "R-S2": 2}
DOCKER_PROJECT = "netlab360-s02-wan"


class ObserveError(RuntimeError):
    pass


def run(argv: list[str], timeout: int = 7) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)


def execute(argv: list[str], runner=run) -> str:
    try:
        result = runner(argv)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ObserveError(f"consulta fallida: {argv[0]} ({type(exc).__name__})") from exc
    if result.returncode:
        raise ObserveError(f"consulta fallida: {argv[0]} (codigo {result.returncode}): {result.stderr.strip()[:100]}")
    return result.stdout


def management_guard(runner=run, hostname=None) -> None:
    if (hostname if hostname is not None else socket.gethostname()) != "netlab360-lab":
        raise ObserveError("hostname de gestion no autorizado")
    a = execute(["ip", "-4", "-br", "addr", "show", "ens33"], runner)
    route = execute(["ip", "-4", "route", "show", "default"], runner)
    if ADMIN_IP not in a or ADMIN_ROUTE not in route:
        raise ObserveError("red administrativa fuera de la linea base: detener observacion")


def load_sot(path: Path = SOT_PATH) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ObserveError("SoT JSON no disponible como archivo regular")
    data = json.loads(path.read_text(encoding="utf-8"))
    devices = data.get("devices", {})
    if data.get("project") != "NETLAB360" or data.get("source_status") != "candidate":
        raise ObserveError("SoT no corresponde a version candidate de NETLAB360")
    if set(devices) != set(EXPECTED):
        raise ObserveError("SoT debe incluir exactamente R-HQ, R-S1 y R-S2")
    if sum(len(d.get("vlans", [])) for d in devices.values()) != 9:
        raise ObserveError("SoT debe incluir exactamente 9 VLAN")
    if sum(len(d.get("wan", [])) for d in devices.values()) != 8:
        raise ObserveError("SoT debe incluir exactamente 8 extremos WAN")
    for logical, device in devices.items():
        cname = device.get("container", "")
        if not re.fullmatch(r"nl360-s02-r-(hq|s1|s2)", cname):
            raise ObserveError(f"contenedor inesperado en {logical}")
        if not cname.endswith(logical.lower().replace("r-", "")):
            raise ObserveError(f"asociacion de contenedor incorrecta en {logical}")
        if len(device.get("wan", [])) != EXPECTED[logical] or len(device.get("vlans", [])) != 3:
            raise ObserveError(f"cardinalidad WAN/VLAN inesperada en {logical}")
        interfaces = [w.get("interface") for w in device["wan"]] + [v.get("interface") for v in device["vlans"]]
        if any(not isinstance(x, str) or not re.fullmatch(r"(?:s[12][pb]|trunk0\.\d{3})", x) for x in interfaces):
            raise ObserveError(f"interfaces no permitidas en {logical}")
        if len(interfaces) != len(set(interfaces)):
            raise ObserveError(f"interfaces duplicadas en {logical}")
    return data


def inspect_router(container: str, runner=run) -> dict:
    command = ["sudo", "-n", "docker", "inspect", container]
    try:
        r = runner(command)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ObserveError(f"Docker inaccesible ({type(exc).__name__})") from exc
    if r.returncode:
        detail = (r.stderr + " " + r.stdout).lower()
        if "no such object" in detail or "no such container" in detail:
            return {"running": False, "pid": None}
        raise ObserveError(f"Docker inaccesible o permiso no disponible: {r.stderr.strip()[:120]}")
    try:
        obj = json.loads(r.stdout)[0]
        if obj["Name"].lstrip("/") != container:
            raise ObserveError("Docker devolvio otro contenedor")
        if obj["HostConfig"]["NetworkMode"] != "none":
            raise ObserveError(f"red Docker no permitida: {container}")
        if (obj["Config"].get("Labels") or {}).get("com.docker.compose.project") != DOCKER_PROJECT:
            raise ObserveError(f"proyecto Docker no autorizado: {container}")
        running = obj["State"]["Running"] is True
        pid = int(obj["State"]["Pid"]) if running else None
        if running and (pid is None or pid <= 1):
            raise ObserveError("PID de contenedor no valido")
        return {"running": running, "pid": pid}
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise ObserveError(f"Docker devolvio respuesta invalida para {container}") from exc


def read_links(pid: int, runner=run) -> dict:
    raw = execute(["sudo", "-n", "nsenter", "-t", str(pid), "-n", "ip", "-j", "link", "show"], runner)
    try:
        data = json.loads(raw)
        return {item["ifname"].split("@", 1)[0]: item for item in data}
    except (ValueError, KeyError, TypeError) as exc:
        raise ObserveError("salida ip -j link invalida") from exc


def status_of_link(link: dict | None) -> int:
    if not link:
        return -1
    return 1 if "UP" in link.get("flags", []) else 0


def collect(sot: dict, runner=run, hostname=None) -> dict:
    observed = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state = {
        "project": "NETLAB360", "phase": "S04", "observed_at_utc": observed,
        "source_ok": False, "topology": "unknown", "source_status": sot["source_status"],
        "scope": "Docker/router existence and interface administrative flags; no OSPF or HTTP health claim",
        "routers": {}, "sites": {}, "errors": [],
    }
    try:
        management_guard(runner, hostname)
        discovered = {}
        for logical, device in sorted(sot["devices"].items()):
            discovered[logical] = inspect_router(device["container"], runner)
        active = sum(int(x["running"]) for x in discovered.values())
        state["topology"] = "offline" if active == 0 else "partial" if active < 3 else "active"
        for logical, device in sorted(sot["devices"].items()):
            runtime = discovered[logical]
            site = logical.replace("R-", "")
            info = {"router": logical, "container": device["container"],
                    "running": int(runtime["running"]), "wan": {}, "vlans": {}}
            links = read_links(runtime["pid"], runner) if runtime["running"] else {}
            for w in device["wan"]:
                info["wan"][w["interface"]] = {
                    "admin_up": status_of_link(links.get(w["interface"])) if runtime["running"] else -1,
                    "address_expected": w["address"],
                }
            for v in device["vlans"]:
                info["vlans"][str(v["id"])] = {
                    "admin_up": status_of_link(links.get(v["interface"])) if runtime["running"] else -1,
                    "interface": v["interface"],
                }
            state["sites"][site] = info
            state["routers"][logical] = int(runtime["running"])
        state["source_ok"] = True
    except (ObserveError, ValueError, TypeError, KeyError) as exc:
        state["source_ok"] = False
        state["topology"] = "unknown"
        state["errors"] = [str(exc)[:220]]
        # No retained measurements on error: prevents stale data reported as live.
        state["routers"] = {}
        state["sites"] = {}
    return state


def prometheus_metrics(state: dict) -> str:
    ok = int(state["source_ok"])
    out = ["# HELP netlab360_s04_source_up Collector read succeeded (not topology availability)",
           "# TYPE netlab360_s04_source_up gauge", f"netlab360_s04_source_up {ok}",
           "# HELP netlab360_s04_topology_mode Topology state, including intentionally offline",
           "# TYPE netlab360_s04_topology_mode gauge"]
    for mode in ("offline", "partial", "active", "unknown"):
        out.append(f'netlab360_s04_topology_mode{{mode="{mode}"}} {int(state["topology"] == mode)}')
    out += ["# HELP netlab360_s04_router_running Router running (0 stopped, -1 unknown)",
            "# TYPE netlab360_s04_router_running gauge"]
    for logical in sorted(EXPECTED):
        out.append(f'netlab360_s04_router_running{{router="{logical}"}} {state["routers"].get(logical, -1)}')
    out += ["# HELP netlab360_s04_wan_admin_up Link administrative up (-1 unknown or not deployed)",
            "# TYPE netlab360_s04_wan_admin_up gauge",
            "# HELP netlab360_s04_vlan_admin_up VLAN interface administrative up (-1 unknown or not deployed)",
            "# TYPE netlab360_s04_vlan_admin_up gauge"]
    for logical, device in sorted(state["sites"].items()):
        for name, row in sorted(device["wan"].items()):
            out.append(f'netlab360_s04_wan_admin_up{{site="{logical}",interface="{name}"}} {row["admin_up"]}')
        for number, row in sorted(device["vlans"].items()):
            out.append(f'netlab360_s04_vlan_admin_up{{site="{logical}",vlan="{number}"}} {row["admin_up"]}')
    return "\n".join(out) + "\n"


def serve(sot: dict, port: int, interval: float, runner=run) -> None:
    store = {"state": collect(sot, runner)}
    lock = threading.RLock()
    stop = threading.Event()

    def poll():
        while not stop.wait(interval):
            latest = collect(sot, runner)
            with lock:
                store["state"] = latest

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            with lock:
                current = store["state"]
            path = urlsplit(self.path).path
            if path in ("/api/v1/state", "/healthz"):
                data = (current if path == "/api/v1/state" else
                        {"service": "s04-exporter", "source_ok": current["source_ok"],
                         "topology": current["topology"], "observed_at_utc": current["observed_at_utc"]})
                body, ctype, code = json.dumps(data, ensure_ascii=False).encode(), "application/json", 200
            elif path == "/metrics":
                body, ctype, code = prometheus_metrics(current).encode(), "text/plain; version=0.0.4", 200
            else:
                body, ctype, code = b"not found\n", "text/plain", 404
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            self.send_response(405)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *_args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    monitor = threading.Thread(target=poll, daemon=True)
    monitor.start()
    print(f"S04_EXPORTER_URL=http://127.0.0.1:{port}/api/v1/state", flush=True)
    print("S04_MODO=SOLO_LECTURA", flush=True)
    try:
        server.serve_forever(poll_interval=0.3)
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
        monitor.join(timeout=interval + 2)
        print("S04_EXPORTER_DETENIDO=SI", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="NETLAB360 S04 observador de 3 sedes (solo lectura)")
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true", help="validar SoT y red administrativa, sin Docker")
    actions.add_argument("--once", action="store_true", help="consultar Docker e interfaces una sola vez")
    actions.add_argument("--serve", action="store_true", help="API local, sin desplegar infraestructura")
    parser.add_argument("--port", type=int, default=9110)
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    if not (1024 <= args.port <= 65535 and args.interval >= 0.5):
        parser.error("puerto o intervalo invalido")
    sot = load_sot()
    management_guard()
    print("S04_SOT=3_ROUTERS_4_WAN_9_VLAN")
    print("S04_SOT_STATUS=" + sot["source_status"])
    if args.check:
        print("S04_PREFLIGHT=OK")
        print("S04_CONSULTA_DOCKER_EJECUTADA=NO")
    elif args.once:
        snap = collect(sot)
        print(json.dumps(snap, ensure_ascii=False, indent=2, sort_keys=True))
        print("S04_RESULTADO_OBSERVACION=" + ("OK" if snap["source_ok"] else "UNKNOWN"))
        if not snap["source_ok"]:
            raise SystemExit(2)
    else:
        serve(sot, args.port, args.interval)


if __name__ == "__main__":
    try:
        main()
    except (ObserveError, ValueError, OSError) as exc:
        print(f"S04_ERROR={str(exc)}", flush=True)
        raise SystemExit(2)
