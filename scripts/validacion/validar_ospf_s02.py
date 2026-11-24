#!/usr/bin/env python3
"""NETLAB360 S02: validar WAN OSPF 4 Full HQ, 2 Full S1/S2 y FIB.

SOLO LECTURA de routers en Docker (y ping de prueba por namespaces).
No crea/mueve interfaces, no cambia rutas del host, no detiene contenedores.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time

C = {"HQ": "nl360-s02-r-hq", "S1": "nl360-s02-r-s1", "S2": "nl360-s02-r-s2"}
EXPECTED_FULL = {"HQ": 4, "S1": 2, "S2": 2}
ROUTES = (
    ("HQ", "10.79.0.2", "s1p"),
    ("HQ", "10.79.0.3", "s2p"),
    ("S1", "10.79.0.1", "s1p"),
    ("S2", "10.79.0.1", "s2p"),
    ("S1", "10.79.0.3", "s1p"),
    ("S2", "10.79.0.2", "s2p"),
)
LOOPS = {"HQ": "10.79.0.1", "S1": "10.79.0.2", "S2": "10.79.0.3"}


def run(*args: str, allow_failure: bool = False) -> str:
    p = subprocess.run(args, text=True, capture_output=True, timeout=30)
    if p.returncode and not allow_failure:
        raise RuntimeError(
            f"Fallo ({p.returncode}): {' '.join(args)}\n{p.stdout[-800:]} {p.stderr[-1500:]}"
        )
    return p.stdout


def sudo(*args: str, **kwargs) -> str:
    return run("sudo", "-n", *args, **kwargs)


# La lectura de namespaces utiliza los PID de los routers Docker inspeccionados.
def inspect() -> dict[str, str]:
    pids = {}
    for logical, name in C.items():
        data = json.loads(sudo("docker", "inspect", name))[0]
        if not data["State"]["Running"] or data["HostConfig"]["NetworkMode"] != "none":
            raise RuntimeError(f"Router no funciona aislado: {name}")
        if (data["Config"].get("Labels") or {}).get("com.docker.compose.project") != "netlab360-s02-wan":
            raise RuntimeError(f"Router no es del proyecto Compose S02: {name}")
        pids[logical] = str(data["State"]["Pid"])
    return pids


def ns(pids: dict[str, str], logical: str, *args: str, allow_failure=False) -> str:
    return sudo("nsenter", "-t", pids[logical], "-n", *args, allow_failure=allow_failure)


def full_count(logical: str) -> tuple[int, str]:
    output = sudo("docker", "exec", C[logical], "vtysh", "-c", "show ip ospf neighbor")
    return sum("Full" in line for line in output.splitlines()), output


# La selección del siguiente salto se comprueba por separado de las adyacencias OSPF.
def check_fib(pids: dict[str, str]) -> tuple[bool, list[str]]:
    rows = []
    result = True
    for router, target, dev in ROUTES:
        route = ns(pids, router, "ip", "-4", "route", "get", target, allow_failure=True).strip()
        passed = ("dev " + dev) in route
        rows.append(f"S02_FIB_{router}_A_{target}={'OK' if passed else 'PENDIENTE'} {route}")
        result &= passed
    return result, rows


def wait_and_validate(pids: dict[str, str]) -> None:
    print("========== ADYACENCIAS OSPF S02 ==========")
    status = {}
    fib = False
    routes = []
    for attempt in range(1, 61):
        status = {name: full_count(name)[0] for name in C}
        if status == EXPECTED_FULL:
            fib, routes = check_fib(pids)
            if fib:
                print(f"S02_OSPF_ESPERA_INTENTOS={attempt}")
                break
        if attempt == 1 or attempt % 5 == 0:
            text = " ".join(f"{s}_FULL={status[s]}" for s in C)
            print(f"S02_CONVERGENCIA_INTENTO={attempt}/60 {text} FIB={'OK' if fib else 'PENDIENTE'}", flush=True)
        time.sleep(2)
    else:
        for name in C:
            count, raw = full_count(name)
            print(f"S02_OSPF_VECINOS_{name}={count}\n{raw}")
        fib, routes = check_fib(pids)
        for line in routes:
            print(line)
        raise RuntimeError("OSPF no llego a FULL 4+2+2 con rutas FIB principal")

    for name in C:
        count, output = full_count(name)
        print(f"========== OSPF {name} ==========")
        print(output.strip())
        if count != EXPECTED_FULL[name]:
            raise RuntimeError(f"Recuento OSPF cambió: {name}={count}")
        print(f"S02_OSPF_FULL_{name}={count}")
    for line in routes:
        print(line)
    print("S02_FIB_WAN_PRIMARIA=6/6")

    print("========== PRUEBAS ICMP ENTRE LOOPBACKS ==========")
    checks = [
        ("HQ", "S1"), ("HQ", "S2"),
        ("S1", "HQ"), ("S2", "HQ"),
        ("S1", "S2"), ("S2", "S1"),
    ]
    for source, dest in checks:
        output = ns(
            pids, source, "ping", "-n", "-c", "2", "-W", "2",
            "-I", LOOPS[source], LOOPS[dest]
        )
        if re.search(r"(?:^|,\s)0% packet loss(?:,|$)", output, re.MULTILINE) is None:
            raise RuntimeError(f"Ping sin respuesta completa: {source}->{dest}\n{output}")
        print(f"S02_PING_{source}_A_{dest}=OK")
    print("S02_OSPF_Y_CONECTIVIDAD=VALIDADOS")


if __name__ == "__main__":
    try:
        pids = inspect()
        wait_and_validate(pids)
    except Exception as e:
        print(f"S02_OSPF_VALIDACION_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
