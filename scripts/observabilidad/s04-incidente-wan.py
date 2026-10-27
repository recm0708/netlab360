#!/usr/bin/env python3
"""G3: incidente S1 WAN principal observado por Prometheus/NOC y restaurado.

Reutiliza el guardián S02 de propiedad y namespaces; no toca ens33 ni OpenTofu.
Para operar: sudo -v; python3 scripts/observabilidad/s04-incidente-wan.py --check
Luego: python3 scripts/observabilidad/s04-incidente-wan.py --execute --snapshot-confirmado
La prueba mantiene s1p administrativamente DOWN al menos 32 s y restaura en finally.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import signal
import sys
import time
from urllib.parse import urlencode
from urllib.request import urlopen

REPO = Path(__file__).resolve().parents[2]
S02 = REPO / "scripts/laboratorio/s02-failover-wan.py"
EXPORTER = "http://127.0.0.1:9110"
PROM = "http://127.0.0.1:9091"
NOC = "http://127.0.0.1:9120"
ALERT = "NETLAB360S04WANAdminDown"


def s02_module():
    spec = importlib.util.spec_from_file_location("netlab360_s02_failover", S02)
    if spec is None or spec.loader is None:
        raise RuntimeError("No es posible cargar guardas S02")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(url: str):
    if not any(url.startswith(base + "/") for base in (EXPORTER, PROM, NOC)):
        raise ValueError("URL ajena al laboratorio")
    with urlopen(url, timeout=5) as response:
        return json.load(response)


def alert_state():
    answer = read_json(PROM + "/api/v1/alerts")
    if answer.get("status") != "success":
        raise RuntimeError("Prometheus alerts no confiable")
    matches = [
        item for item in answer.get("data", {}).get("alerts", [])
        if item.get("labels", {}).get("alertname") == ALERT
        and item.get("labels", {}).get("site") == "HQ"
        and item.get("labels", {}).get("interface") == "s1p"
    ]
    if len(matches) > 1:
        raise RuntimeError("Alerta duplicada para HQ/s1p")
    return matches[0].get("state", "unknown") if matches else "inactive"


def query_scalar(metric: str, selector: str = ""):
    url = PROM + "/api/v1/query?" + urlencode({"query": metric + selector})
    answer = read_json(url)
    if answer.get("status") != "success":
        raise RuntimeError("Consulta Prometheus fallida")
    values = answer["data"]["result"]
    if len(values) != 1:
        raise RuntimeError(f"Serie ausente o duplicada: {metric}")
    return float(values[0]["value"][1])


def exporter_state():
    state = read_json(EXPORTER + "/api/v1/state")
    if state.get("source_ok") is not True or state.get("topology") != "active":
        raise RuntimeError("Exporter sin observacion valida de topologia activa")
    timestamp = datetime.fromisoformat(state["observed_at_utc"])
    age = (datetime.now(timezone.utc) - timestamp).total_seconds()
    if not 0 <= age <= 15:
        raise RuntimeError(f"Muestra exporter no fresca: {age}")
    return state


def guard_host(mod):
    host = (
        mod.run("ip", "-4", "-o", "addr", "show", "dev", "ens33"),
        mod.run("ip", "-4", "route", "show", "table", "main"),
    )
    if "192.168.47.40/24" not in host[0] or "default via 192.168.47.2 dev ens33" not in host[1]:
        raise RuntimeError("Gestion host fuera del baseline")
    return host


def precheck(mod):
    if mod.os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal, no root")
    if not S02.is_file() or S02.is_symlink():
        raise RuntimeError("Guarda S02 no disponible")
    host = guard_host(mod)
    pids = mod.validate_ownership()
    h, s1 = pids["R-HQ"], pids["R-S1"]
    state = exporter_state()
    if len(state["sites"]) != 3 or any(r != 1 for r in state["routers"].values()):
        raise RuntimeError("Routers incompletos")
    wan = [int(v["admin_up"]) for site in state["sites"].values() for v in site["wan"].values()]
    vlan = [int(v["admin_up"]) for site in state["sites"].values() for v in site["vlans"].values()]
    if len(wan) != 8 or len(vlan) != 9 or any(v != 1 for v in wan + vlan):
        raise RuntimeError("La red WAN/VLAN no parte de baseline sana")
    targets = read_json(PROM + "/api/v1/targets")
    matches = [
        t for t in targets.get("data", {}).get("activeTargets", [])
        if t.get("labels", {}).get("job") == "netlab360-s04-multisede"
    ]
    if len(matches) != 1 or matches[0].get("health") != "up":
        raise RuntimeError("Scrape target no UP")
    if query_scalar("netlab360_s04_source_up") != 1:
        raise RuntimeError("Fuente Prometheus inestable")
    if alert_state() != "inactive":
        raise RuntimeError("Alerta HQ/s1p activa antes del incidente")
    noc = read_json(NOC + "/api/v1/overview")
    tel, prom = noc.get("telemetry", {}), noc.get("prometheus", {})
    if not (tel.get("source_ok") and tel.get("fresh")
            and tel.get("topology") == "active"
            and prom.get("available") and prom.get("alerts_known")
            and prom.get("scrape") == "up"):
        raise RuntimeError("NOC sin fuentes validas")
    link = mod.ns(h, "ip", "-br", "link", "show", "dev", "s1p")
    if "UP" not in link:
        raise RuntimeError("La primaria HQ/s1p ya esta caida")
    for pid, target, dev in (
        (h, "10.79.0.2", "s1p"),
        (s1, "10.79.0.1", "s1p"),
        (h, "10.79.0.3", "s2p"),
    ):
        if not mod.is_via(mod.route(pid, target), dev):
            raise RuntimeError(f"Ruta inicial no usa {dev}")
    print("========== S04 G3 PRECHECK ==========", flush=True)
    print("S04_G3_SOT=3_ROUTERS_4_WAN_9_VLAN", flush=True)
    print("S04_G3_EXPORTER=active_fresh", flush=True)
    print("S04_G3_PROMETHEUS=up", flush=True)
    print("S04_G3_NOC=available", flush=True)
    print("S04_G3_WAN=8/8 VLAN=9/9", flush=True)
    print("S04_G3_BASELINE_S1=s1p S2=s2p", flush=True)
    print("S04_G3_ALERTA_BASELINE=inactive", flush=True)
    print("S04_G3_HOST_GESTION=PROTEGIDO", flush=True)
    print("S04_G3_PRECHECK=OK", flush=True)
    return pids, host


def observed_failure(mod, pids, host, seconds):
    h, s1 = pids["R-HQ"], pids["R-S1"]
    pending = False
    firing = False
    noc_firing = False
    last = "inactive"
    cut = False
    failure = None
    print("========== S04 G3 INICIO INCIDENTE ==========", flush=True)
    print("S04_G3_HORA_INICIO_UTC=" + stamp(), flush=True)
    try:
        # El flag se coloca antes de la instruccion para restaurar aun si esta falla.
        cut = True
        mod.ns(h, "ip", "link", "set", "s1p", "down")
        print("S04_G3_HQ_s1p=DOWN", flush=True)
        began = time.monotonic()
        while time.monotonic() - began < seconds:
            current = alert_state()
            if current != last:
                print(f"S04_G3_ALERTA_TRANSICION={last}->{current} UTC={stamp()}", flush=True)
                last = current
            if current == "pending":
                pending = True
            if current == "firing":
                firing = True
                if not noc_firing:
                    noc = read_json(NOC + "/api/v1/overview")
                    noc_firing = any(
                        a.get("labels", {}).get("alertname") == ALERT
                        and a.get("labels", {}).get("site") == "HQ"
                        and a.get("labels", {}).get("interface") == "s1p"
                        and a.get("state") == "firing"
                        for a in noc.get("prometheus", {}).get("alerts", [])
                    )
                    if noc_firing:
                        print("S04_G3_NOC_ALERTA_FIRING=SI", flush=True)
            elapsed = time.monotonic() - began
            if 0 <= elapsed % 10 < 1.2:
                print(f"S04_G3_CORTE_SEGUNDOS={elapsed:.1f}/{seconds}", flush=True)
            time.sleep(1)
        backup = mod.route(h, "10.79.0.2")
        peer = mod.route(s1, "10.79.0.1")
        other = mod.route(h, "10.79.0.3")
        if not (mod.is_via(backup, "s1b")
                and mod.is_via(peer, "s1b")
                and mod.is_via(other, "s2p")):
            raise RuntimeError(f"Respaldo u otra sede sin ruta esperada: {backup} / {peer} / {other}")
        mod.ping(h, "10.79.0.2")
        mod.ping(h, "10.79.0.3")
        print("S04_G3_RUTA_RESPALDO_HQ=" + backup, flush=True)
        print("S04_G3_RUTA_RESPALDO_S1=" + peer, flush=True)
        print("S04_G3_OTRA_SEDE_S2_ESTABLE=SI", flush=True)
        print("S04_G3_CONECTIVIDAD_DURANTE_INCIDENTE=OK", flush=True)
        if not (pending and firing and noc_firing):
            raise RuntimeError(
                f"Secuencia alerta incompleta pending={pending} firing={firing} noc={noc_firing}"
            )
        print("S04_G3_ALERTA_PENDING_Y_FIRING=OK", flush=True)
        print("========== S04 G3 FIN OBSERVACION DOWN ==========", flush=True)
    except BaseException as exc:
        failure = exc
        print(f"S04_G3_INCIDENTE_ERROR={type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
    finally:
        if cut:
            # Nunca dejar la interfaz intencionalmente DOWN al terminar.
            try:
                mod.ns(h, "ip", "link", "set", "s1p", "up")
                print("S04_G3_HQ_s1p=UP_RESTAURADA UTC=" + stamp(), flush=True)
                primary = mod.wait_fib(h, "10.79.0.2", "s1p", limit=90)
                peer_primary = mod.wait_fib(s1, "10.79.0.1", "s1p", limit=90)
                mod.ping(h, "10.79.0.2")
                mod.host_guard(host)
                print("S04_G3_RUTA_PRIMARIA_HQ=" + primary, flush=True)
                print("S04_G3_RUTA_PRIMARIA_S1=" + peer_primary, flush=True)
                print("S04_G3_HOST_GESTION_INTACTO=SI", flush=True)
            except BaseException as exc:
                print(f"S04_G3_RESTAURACION_ERROR={type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
                if failure is None:
                    failure = exc
    if failure is not None:
        raise RuntimeError("Incidente incompleto o restitucion no validada: revisar WAN sin desmontar") from failure
    print("========== S04 G3 RECUPERACION ALERTA ==========", flush=True)
    for _ in range(45):
        restored = exporter_state()
        if (restored["sites"]["HQ"]["wan"]["s1p"]["admin_up"] == 1
                and query_scalar("netlab360_s04_wan_admin_up", '{site="HQ",interface="s1p"}') == 1
                and alert_state() == "inactive"):
            print("S04_G3_WAN_ADMIN_RESTAURADA=1", flush=True)
            print("S04_G3_ALERTA_RESUELTA=SI_AUSENTE_EN_ACTIVAS UTC=" + stamp(), flush=True)
            print("S04_G3_RESULTADO=OK", flush=True)
            return
        time.sleep(1)
    raise RuntimeError("Prometheus o exporter no reflejan recuperacion en 45 s")


def stop_as_interrupt(_signum, _frame):
    raise KeyboardInterrupt("interrupcion recibida; ejecutar finalmente restauracion")


def main():
    p = argparse.ArgumentParser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--execute", action="store_true")
    p.add_argument("--snapshot-confirmado", action="store_true")
    p.add_argument("--hold-seconds", type=int, default=32)
    args = p.parse_args()
    if args.execute and not args.snapshot_confirmado:
        p.error("Para ejecutar se exige --snapshot-confirmado")
    if not 20 <= args.hold_seconds <= 60:
        p.error("--hold-seconds debe estar entre 20 y 60")
    mod = s02_module()
    pids, host = precheck(mod)
    if args.check:
        return
    for value in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(value, stop_as_interrupt)
    observed_failure(mod, pids, host, args.hold_seconds)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError, KeyboardInterrupt) as exc:
        print(f"S04_G3_ERROR={type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1)
