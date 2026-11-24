#!/usr/bin/env python3
"""S02 prueba de failover OSPF en S1 o S2, con RESTAURACION EN finally.

Solo baja/sube una interfaz WAN primaria en el namespace de R-HQ.
Nunca modifica interfaces o rutas del host. Mantener LAN/servicios activos.
Uso: sudo -v; python3 scripts/laboratorio/s02_failover_wan.py S1|S2 [--hold-seconds 0-30]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time

HOME = Path.home()
STATE = HOME / "netlab360-bootstrap/s02/wan-links-state.json"
CASES = {
    "S1": {"interface": "s1p", "backup": "s1b", "target": "10.79.0.2",
           "peer": "nl360-s02-r-s1", "other": "10.79.0.3",
           "other_dev": "s2p", "expected": "10.78.0.6"},
    "S2": {"interface": "s2p", "backup": "s2b", "target": "10.79.0.3",
           "peer": "nl360-s02-r-s2", "other": "10.79.0.2",
           "other_dev": "s1p", "expected": "10.78.0.14"},
}
HQ = "nl360-s02-r-hq"


def run(*cmd: str, allow_failure: bool = False, timeout: int = 25) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode and not allow_failure:
        raise RuntimeError(f"exit={p.returncode} {' '.join(cmd)}:\n{p.stdout}\n{p.stderr}")
    return p.stdout


def sud(*cmd: str, **kw) -> str:
    return run("sudo", "-n", *cmd, **kw)


# Solo aceptamos routers y estados pertenecientes a la topología WAN registrada.
def validate_ownership() -> dict[str, str]:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("No existe estado WAN S02 legitimo")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    if state.get("owner") != "NETLAB360_S02_WAN_LINKS_V1":
        raise RuntimeError("Marcador de propietario inesperado")
    current = {}
    for logical, name in (("R-HQ", HQ), ("R-S1", CASES["S1"]["peer"]),
                          ("R-S2", CASES["S2"]["peer"])):
        d = json.loads(sud("docker", "inspect", name))[0]
        if (d["Id"] != state["ids"].get(logical)
                or not d["State"]["Running"]
                or d["HostConfig"]["NetworkMode"] != "none"):
            raise RuntimeError(f"Router diferente/detenido/red ajena: {name}")
        current[logical] = str(d["State"]["Pid"])
    return current


def ns(pid: str, *command: str, allow_failure: bool = False) -> str:
    return sud("nsenter", "-t", pid, "-n", *command, allow_failure=allow_failure)


def route(pid: str, target: str) -> str:
    return ns(pid, "ip", "-4", "route", "get", target, allow_failure=True).strip()


def is_via(result: str, dev: str) -> bool:
    return "dev " + dev in result


# Esperamos la selección FIB prevista; observar una ruta no sustituye el ping posterior.
def wait_fib(pid: str, target: str, dev: str, limit: int = 60) -> str:
    result = ""
    for second in range(limit):
        result = route(pid, target)
        if is_via(result, dev):
            return result
        if second in (0, 9, 29, 49):
            print(f"S02_ESPERANDO_RUTA={target} DEV={dev} SEG={second + 1}/{limit}", flush=True)
        time.sleep(1)
    raise RuntimeError(f"FIB no convergio a {dev} para {target}: {result}")


def ping(pid: str, target: str) -> None:
    output = ns(pid, "ping", "-n", "-c", "2", "-W", "2",
                "-I", "10.79.0.1", target)
    if re.search(r"(?:^|,\s)0% packet loss(?:,|$)", output, re.MULTILINE) is None:
        raise RuntimeError(f"ICMP falla: {output}")


def host_guard(before: tuple[str, str]) -> None:
    after = (run("ip", "-4", "-o", "addr", "show", "dev", "ens33"),
             run("ip", "-4", "route", "show", "table", "main"))
    if before != after or "192.168.47.40/24" not in after[0]:
        raise RuntimeError("ATENCION: hubo cambio host; no modificar ens33")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("branch", choices=sorted(CASES))
    p.add_argument("--hold-seconds", type=int, default=0,
                   help="Ventana acotada de observación NOC (0-30 s), con recuperación automática")
    args = p.parse_args()
    if not 0 <= args.hold_seconds <= 30:
        p.error("--hold-seconds debe estar entre 0 y 30")

    def stop_and_restore(signum: int, _frame: object) -> None:
        raise KeyboardInterrupt(f"Señal {signum}; se iniciará la restauración WAN")

    signal.signal(signal.SIGTERM, stop_and_restore)
    signal.signal(signal.SIGHUP, stop_and_restore)
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal; autenticar sudo previamente")
    x = CASES[args.branch]
    pids = validate_ownership()
    h = pids["R-HQ"]
    b = pids["R-" + args.branch]
    host = (run("ip", "-4", "-o", "addr", "show", "dev", "ens33"),
            run("ip", "-4", "route", "show", "table", "main"))
    if "192.168.47.40/24" not in host[0]:
        raise RuntimeError("Red de gestion inesperada")
    link = ns(h, "ip", "-br", "link", "show", "dev", x["interface"])
    if "UP" not in link:
        raise RuntimeError("Primaria no esta UP; abortado")
    first = route(h, x["target"])
    peer_first = route(b, "10.79.0.1")
    other_first = route(h, x["other"])
    if not is_via(first, x["interface"]) or not is_via(peer_first, x["interface"]):
        raise RuntimeError(f"Ruta primaria no activa: {first} / {peer_first}")
    if not is_via(other_first, x["other_dev"]):
        raise RuntimeError(f"Otra sede no esta usando primaria: {other_first}")
    print(f"========== INICIO PRUEBA S02 FAILOVER {args.branch} ==========")
    print(f"S02_{args.branch}_BASELINE_HQ={first}")
    print(f"S02_{args.branch}_BASELINE_SUCURSAL={peer_first}")
    failure = None
    down_attempted = False
    try:
        down_attempted = True
        ns(h, "ip", "link", "set", x["interface"], "down")
        print(f"S02_{args.branch}_WAN_PRINCIPAL=DOWN", flush=True)
        new = wait_fib(h, x["target"], x["backup"])
        peer_new = wait_fib(b, "10.79.0.1", x["backup"])
        unaffected = route(h, x["other"])
        if not is_via(unaffected, x["other_dev"]):
            raise RuntimeError("Falla afecto ruta de otra sucursal")
        ping(h, x["target"])
        ping(h, x["other"])
        print(f"S02_{args.branch}_RUTA_RESPALDO_HQ={new}")
        print(f"S02_{args.branch}_RUTA_RESPALDO_SUCURSAL={peer_new}")
        print(f"S02_{args.branch}_OTRA_SEDE_ESTABLE=SI")
        print(f"S02_{args.branch}_CONMUTACION=OK", flush=True)
        if args.hold_seconds:
            print(f"S05_{args.branch}_VENTANA_NOC_SEG={args.hold_seconds}", flush=True)
            print(f"S05_{args.branch}_OBSERVACION_DE_RESPALDO=EN_CURSO", flush=True)
            time.sleep(args.hold_seconds)
            print(f"S05_{args.branch}_OBSERVACION_DE_RESPALDO=FINALIZADA", flush=True)
    except BaseException as e:
        failure = e
        print(f"S02_{args.branch}_FALLO_DURANTE_CORTE={type(e).__name__}: {e}", file=sys.stderr)
    finally:
        if down_attempted:
            try:
                ns(h, "ip", "link", "set", x["interface"], "up")
                print(f"S02_{args.branch}_WAN_PRINCIPAL=RESTAURADA", flush=True)
                again = wait_fib(h, x["target"], x["interface"], limit=90)
                peer_again = wait_fib(b, "10.79.0.1", x["interface"], limit=90)
                ping(h, x["target"])
                host_guard(host)
                print(f"S02_{args.branch}_RUTA_RESTAURADA_HQ={again}")
                print(f"S02_{args.branch}_RUTA_RESTAURADA_SUCURSAL={peer_again}")
                print(f"S02_{args.branch}_RETORNO_PRINCIPAL=OK", flush=True)
            except BaseException as e:
                print(f"S02_{args.branch}_RESTAURACION_ERROR={type(e).__name__}: {e}", file=sys.stderr)
                if failure is None:
                    failure = e
    if failure is not None:
        raise RuntimeError(f"Prueba {args.branch} incompleta; inspeccionar sin borrar WAN") from failure
    print(f"S02_{args.branch}_PRUEBA_COMPLETA=OK")
    print(f"========== FIN PRUEBA S02 FAILOVER {args.branch} ==========")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"S02_FAILOVER_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
