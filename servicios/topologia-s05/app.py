#!/usr/bin/env python3
"""NETLAB360 S05: topologia web solo lectura, con SoT y telemetria S04.

Estados observados separan administrativamente UP de ruta elegida/OSPF/trafico.
Un dato sin telemetria fresca es UNKNOWN; el inventario sigue visible.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
from pathlib import Path
import socket
import subprocess
from urllib.request import urlopen
from urllib.parse import urlsplit
import yaml

ROOT = Path(__file__).resolve().parents[2]
IPAM = ROOT / "inventario/ipam/topologia-s02.yaml"
EXT = ROOT / "inventario/topologia-extensiones-s05.json"
STATIC = Path(__file__).with_name("index.html")
EXPORTER = "http://127.0.0.1:9110/api/v1/state"
SITES = ("HQ", "S1", "S2")
IFACE = {"WAN-PRIMARIA-HQ-S1": "s1p",
         "WAN-RESPALDO-HQ-S1": "s1b",
         "WAN-PRIMARIA-HQ-S2": "s2p",
         "WAN-RESPALDO-HQ-S2": "s2b"}


def command(*argv: str, timeout: float = 3.0) -> subprocess.CompletedProcess:
    return subprocess.run(argv, text=True, capture_output=True, timeout=timeout, check=False)


def guard() -> None:
    if socket.gethostname() != "netlab360-lab":
        raise RuntimeError("VM distinta de netlab360-lab")
    addr = command("ip", "-4", "-o", "address", "show", "dev", "ens33")
    route = command("ip", "-4", "route", "show", "default")
    if (addr.returncode or "192.168.47.40/24" not in addr.stdout or
            route.returncode or "default via 192.168.47.2 dev ens33" not in route.stdout):
        raise RuntimeError("Proteccion de ens33/VMnet8: gestion no coincide")


def inventory() -> dict:
    data = yaml.safe_load(IPAM.read_text(encoding="utf-8"))
    if data.get("schema_version") != "0.2" or set(data["sites"]) != set(SITES):
        raise ValueError("IPAM S02 no corresponde a tres sedes")
    if data.get("status") != "candidate" or len(data.get("wan_links", [])) != 4:
        raise ValueError("Estado candidate/WAN S02 inesperado")
    if any(len(data["sites"][site]["vlans"]) != 3 for site in SITES):
        raise ValueError("Numero de VLANs por sede inesperado")
    if set(w["id"] for w in data["wan_links"]) != set(IFACE):
        raise ValueError("Identidad WAN no coincide con el contrato S02")
    return data


def extensions() -> dict:
    data = json.loads(EXT.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Extension de topologia: version incompatible")
    for kind in ("nodes", "links"):
        if not isinstance(data.get(kind), list):
            raise ValueError("Extension de topologia: lista invalida " + kind)
    return data


def telemetry() -> tuple[dict | None, str]:
    try:
        with urlopen(EXPORTER, timeout=1.5) as connection:
            snap = json.load(connection)
        stamp = datetime.fromisoformat(str(snap.get("observed_at_utc")))
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
        if (stamp.tzinfo is None or not (0 <= age <= 15) or
                snap.get("source_ok") is not True or
                snap.get("topology") not in ("active", "partial", "offline") or
                set(snap.get("sites", {})) != set(SITES)):
            return None, "Fuente S04 obsoleta/incompleta o no confiable"
        return snap, ""
    except (OSError, ValueError, TypeError, KeyError, TimeoutError):
        return None, "Exporter S04 127.0.0.1:9110 sin muestra confiable"


def namespaces() -> tuple[set[str] | None, str]:
    # Listar netns suele ser legible sin privilegios. Intentarlo primero
    # evita depender de la caché sudo y no modifica namespaces.
    for argv in (("ip", "netns", "list"), ("sudo", "-n", "ip", "netns", "list")):
        try:
            p = command(*argv, timeout=3.0)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if p.returncode == 0:
            return {row.split()[0] for row in p.stdout.splitlines() if row.strip()}, ""
    return None, "netns no consultable; estado UNKNOWN"


def observed_router(site: str, snapshot: dict | None) -> str:
    if snapshot is None:
        return "unknown"
    v = snapshot["sites"][site].get("running")
    return "running" if v == 1 else "offline" if v == 0 else "unknown"


def ns_state(name: str, discovered: set[str] | None) -> str:
    if discovered is None:
        return "unknown"
    return "namespace-present" if name in discovered else "offline"


def vlan_state(site: str, vid: int, snapshot: dict | None) -> str:
    if snapshot is None:
        return "unknown"
    value = (snapshot["sites"][site].get("vlans") or {}).get(str(vid), {}).get("admin_up")
    return "admin-up" if value == 1 else "admin-down" if value == 0 else "unknown"


def wan_state(w: dict, snap: dict | None) -> str:
    if snap is None:
        return "unknown"
    site_b = w["b"]["router"].replace("R-", "")
    if snap["topology"] == "offline":
        return "offline"
    iface = IFACE[w["id"]]
    a = (snap["sites"]["HQ"].get("wan") or {}).get(iface, {}).get("admin_up")
    b = (snap["sites"][site_b].get("wan") or {}).get(iface, {}).get("admin_up")
    if a == 0 or b == 0:
        return "admin-down"
    if a == 1 and b == 1:
        return "admin-up"
    return "unknown"


def graph(inv: dict, snap: dict | None, ns: set[str] | None, ext: dict) -> dict:
    # El instante se toma del reloj de la VM; UTC se conserva para trazabilidad
    # y America/Panama se ofrece explícitamente para su presentación.
    now_utc = datetime.now(timezone.utc)
    now_panama = now_utc.astimezone(ZoneInfo("America/Panama"))
    nodes: list[dict] = []
    links: list[dict] = []
    for site in SITES:
        d = inv["sites"][site]
        nodes.append({"id": "R-" + site, "site": site, "type": "router",
                      "label": d["router"], "detail": d["loopback"],
                      "status": observed_router(site, snap), "origin": "S02 IPAM"})
        switch = "SW-" + site
        nodes.append({"id": switch, "site": site, "type": "switch",
                      "label": switch, "detail": "Bridge VLAN filtering",
                      "status": ns_state("nl360-s02-sw-" + site.lower(), ns),
                      "origin": "S02 LAN"})
        links.append({"id": "TRUNK-" + site, "from": "R-" + site,
                      "to": switch, "type": "lan", "role": "trunk",
                      "status": "unknown", "detail": "Trunk 802.1Q, estado L2 no observado"})
        for vlan in d["vlans"]:
            vid = int(vlan["id"])
            ipnet = ipaddress.ip_network(vlan["subnet"], strict=True)
            last = {10: 10, 20: 20, 30: 30}[vid % 100]
            host_ip = str(ipaddress.ip_address(int(ipnet.network_address) + last))
            host = f"H-{site}-{vid}"
            nodes.append({"id": host, "site": site, "type": "host",
                          "label": "Host " + str(vid),
                          "detail": f"{vlan['name']} · {host_ip}/{ipnet.prefixlen}",
                          "vlan": vid, "gateway": vlan["gateway"],
                          "status": ns_state(f"nl360-s02-h-{site.lower()}-{vid}", ns),
                          "vlan_admin": vlan_state(site, vid, snap),
                          "origin": "S02 IPAM / host de prueba, no servidor físico"})
            links.append({"id": f"ACCESS-{site}-{vid}",
                          "from": switch, "to": host, "type": "access",
                          "role": "VLAN " + str(vid),
                          "status": "unknown", "detail": vlan["subnet"]})
    for w in inv["wan_links"]:
        links.append({"id": w["id"], "from": w["a"]["router"],
                      "to": w["b"]["router"], "type": "wan",
                      "role": "primary" if "PRIMARIA" in w["id"] else "backup",
                      "status": wan_state(w, snap),
                      "detail": (w["subnet"] + " · costo OSPF esperado " +
                                 str(w["ospf_cost"]) + " · ruta seleccionada no verificada"),
                      "a": w["a"]["address"], "b": w["b"]["address"]})
    # Adiciones futuras requieren registro explícito de recurso ya realizado.
    known = {n["id"] for n in nodes}
    for extra in ext["nodes"]:
        if extra.get("realized") is not True:
            continue
        if (extra.get("id") in known or extra.get("site") not in SITES or
                extra.get("type") not in ("router", "switch", "host", "server", "controller")):
            raise ValueError("Nodo extendido sin identidad/ubicacion valida")
        known.add(extra["id"])
        nodes.append({"id": extra["id"], "label": str(extra.get("label", extra["id"]))[:80],
                      "site": extra["site"], "type": extra["type"],
                      "detail": str(extra.get("detail", ""))[:160],
                      "origin": str(extra.get("evidence", "Extensión registrada"))[:160],
                      "status": "unknown"})
    existing_links = {item["id"] for item in links}
    for extra in ext["links"]:
        if extra.get("realized") is not True:
            continue
        if (extra.get("id") in existing_links or extra.get("from") not in known or
                extra.get("to") not in known or
                extra.get("type") not in ("wan", "lan", "access", "redundancy")):
            raise ValueError("Enlace extendido inválido")
        existing_links.add(extra["id"])
        links.append({"id": extra["id"], "from": extra["from"], "to": extra["to"],
                      "type": extra["type"], "role": str(extra.get("role", "additional"))[:48],
                      "detail": str(extra.get("detail", ""))[:160],
                      "status": "unknown"})
    return {
        "project": "NETLAB360", "phase": "S05", "schema_version": 1,
        "observed_at_utc": now_utc.isoformat(timespec="seconds"),
        "vm_clock": {
            "utc": now_utc.isoformat(timespec="seconds"),
            "panama": now_panama.isoformat(timespec="seconds"),
            "timezone": "America/Panama",
            "source": "system_clock_vm",
        },
        "source": "S02 IPAM candidate + S04 exporter solo lectura + netns solo lectura",
        "telemetry": {"available": snap is not None,
                      "topology": snap["topology"] if snap else "unknown",
                      "last_sample_utc": snap["observed_at_utc"] if snap else None},
        "counts": {"sites": 3, "routers": 3, "switches": 3, "hosts": 9,
                   "vlans": 9, "wan": 4, "extensions": len(nodes) - 15},
        "nodes": nodes, "links": links,
        "caveats": [
            "S02 IPAM es candidate: elementos dibujados no implican despliegue activo.",
            "admin-up es un flag administrativo; no confirma OSPF Full, FIB, HTTP o trafico.",
            "Los enlaces backup son candidatos de respaldo; su uso activo no esta verificado.",
            "UNKNOWN no equivale a DOWN; las redes estan intencionalmente desmontadas si se conoce su estado.",
        ],
    }


def current() -> dict:
    inv = inventory()
    ext = extensions()
    snap, s_error = telemetry()
    ns, ns_error = namespaces()
    result = graph(inv, snap, ns, ext)
    result["source_warnings"] = [x for x in (s_error, ns_error) if x]
    result["namespaces_observable"] = ns is not None
    return result


def serve(port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def send(self, status: int, content: bytes, mime: str):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            route = urlsplit(self.path).path
            if route in ("/", "/index.html"):
                self.send(200, STATIC.read_bytes(), "text/html; charset=utf-8")
            elif route == "/api/v1/graph":
                try:
                    data = current()
                    self.send(200, json.dumps(data, ensure_ascii=False).encode(),
                              "application/json; charset=utf-8")
                except (ValueError, KeyError, OSError) as exc:
                    self.send(503, json.dumps({"error": str(exc)[:150]}).encode(),
                              "application/json")
            elif route == "/healthz":
                self.send(200, b'{"healthy":true,"service":"netlab360-s05-topologia"}',
                          "application/json")
            else:
                self.send(404, b"Not found", "text/plain")

        def do_POST(self):
            self.send(405, b"method not allowed", "text/plain")

        def log_message(self, *_):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"S05_TOPOLOGIA_LOCAL=http://127.0.0.1:{port}/", flush=True)
    print("S05_TOPOLOGIA_READONLY=SI", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print("S05_TOPOLOGIA_DETENIDA=SI", flush=True)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--once", action="store_true")
    group.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=9130)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("Puerto fuera de rango")
    guard()
    if args.check:
        d = current()
        assert d["counts"]["wan"] == 4 and d["counts"]["hosts"] == 9
        print("S05_TOPOLOGIA_IPAM=3_SEDES_3_ROUTERS_3_SWITCHES_9_HOSTS_4_WAN")
        print("S05_TOPOLOGIA_CONSULTA=OK_SIN_CAMBIOS")
        print("S05_TOPOLOGIA_TELEMETRIA=" + d["telemetry"]["topology"].upper())
    elif args.once:
        print(json.dumps(current(), indent=2, ensure_ascii=False))
    else:
        serve(args.port)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, KeyError, OSError) as exc:
        print("S05_TOPOLOGIA_ERROR=" + str(exc))
        raise SystemExit(2)
