#!/usr/bin/env python3
"""NETLAB360 S05: monitor HTTP de los tres nodos HA desde cliente S2.

Solo lee endpoints HTTP fijos desde el namespace S02 S2-320.
Publica snapshot UTC en state local S05, jamás ejecuta Docker/sudo/FRR.
No constituye HA física ni supervisión desde un host independiente.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, ProxyHandler, build_opener

BASE = Path.home() / "netlab360-bootstrap/s05/ha"
OUTPUT = BASE / "observacion-http-s2.json"
OWNER = "NETLAB360_S05_HA_MONITOR_V1"
SOURCE = "nl360-s02-h-s2-320"
SERVICE = "netlab360-s05-ha"
TARGETS = {
    "BACKEND_HQ": {"site": "HQ", "role": "backend", "ip": "10.70.20.21", "port": 8088},
    "BACKEND_S1": {"site": "S1", "role": "backend", "ip": "10.71.20.21", "port": 8088},
    "FRONTAL_HQ": {"site": "HQ", "role": "frontend", "ip": "10.70.20.23", "port": 8080},
}
OPENER = build_opener(ProxyHandler({}))


def ensure_network_namespace() -> None:
    expected = Path("/run/netns") / SOURCE
    if not expected.exists():
        raise RuntimeError("Network namespace de cliente S2 no existe")
    running = os.stat("/proc/self/ns/net").st_ino
    if running != os.stat(expected).st_ino:
        raise RuntimeError("Monitor no está dentro del namespace de S2")


def probe(identity: str) -> dict:
    cfg = TARGETS[identity]
    url = f"http://{cfg['ip']}:{cfg['port']}/api/v1/service"
    request = Request(url, headers={"Accept": "application/json",
                                    "Cache-Control": "no-store"})
    sample = {"ip": cfg["ip"], "site": cfg["site"], "status": "unknown"}
    try:
        with OPENER.open(request, timeout=0.75) as response:
            code = response.status
            body = response.read(4096)
    except HTTPError as exc:
        code = exc.code
        body = exc.read(4096)
    except (TimeoutError, OSError, URLError):
        return {**sample, "status": "offline"}
    try:
        info = json.loads(body)
        if (not isinstance(info, dict) or
                info.get("service") != SERVICE or
                info.get("id") != identity or
                info.get("role") != cfg["role"] or
                (cfg["role"] == "backend" and info.get("site") != cfg["site"])):
            raise ValueError("Identidad HTTP inesperada")
        if cfg["role"] == "backend":
            if code != 200 or info.get("status") != "healthy":
                raise ValueError("Respuesta backend no saludable")
            return {**sample, "status": "running"}
        if code == 503 and info.get("status") == "unavailable":
            return {**sample, "status": "offline",
                    "active_backend": None, "selected_path": None}
        if code != 200 or info.get("status") != "available":
            raise ValueError("Respuesta frontal no saludable")
        chosen = info.get("active_backend")
        path = info.get("selected_path")
        if (chosen, path) not in (("BACKEND_HQ", "PRINCIPAL"),
                                  ("BACKEND_S1", "RESPALDO")):
            raise ValueError("Selección inválida de frontal")
        return {**sample, "status": "running",
                "active_backend": chosen, "selected_path": path}
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        return sample


def observe() -> dict:
    with ThreadPoolExecutor(max_workers=3) as pool:
        values = list(pool.map(probe, TARGETS))
    return {
        "owner": OWNER,
        "source_netns": SOURCE,
        "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "services": dict(zip(TARGETS, values)),
        "routing_note": "Selección HTTP por healthcheck, NO ruta FIB",
    }


def save(data: dict) -> None:
    if OUTPUT.exists() and (OUTPUT.is_symlink() or not OUTPUT.is_file()):
        raise RuntimeError("Archivo de monitor no es regular")
    BASE.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=BASE, encoding="utf-8",
                                         delete=False) as fp:
            tmp = Path(fp.name)
            json.dump(data, fp, sort_keys=True, ensure_ascii=False)
            fp.write("\n")
        os.chmod(tmp, 0o600)
        os.replace(tmp, OUTPUT)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def run(interval: float, once: bool) -> None:
    ensure_network_namespace()
    previous = None
    while True:
        data = observe()
        save(data)
        services = data["services"]
        current = tuple((k, v["status"],
                         v.get("active_backend")) for k, v in services.items())
        if current != previous:
            print("S05_HA_MONITOR_CAMBIO=" + json.dumps(current), flush=True)
            previous = current
        if once:
            print("S05_HA_MONITOR_ONCE=OK", flush=True)
            break
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--once", action="store_true")
    mode.add_argument("--serve", action="store_true")
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    if not 0.5 <= args.interval <= 5.0:
        raise ValueError("interval fuera de 0.5..5 segundos")
    if args.check:
        if set(TARGETS) != {"BACKEND_HQ", "BACKEND_S1", "FRONTAL_HQ"}:
            raise ValueError("identidades de servicio diferentes")
        print("S05_HA_MONITOR_CONTRATO=OK")
        print("S05_HA_MONITOR_PROBES=SOLO_LECTURA")
        return
    run(args.interval, args.once)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"S05_HA_MONITOR_ERROR={type(exc).__name__}:{exc}", file=sys.stderr)
        sys.exit(2)
