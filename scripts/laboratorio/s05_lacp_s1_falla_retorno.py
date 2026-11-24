#!/usr/bin/env python3
"""NETLAB360 S05: degradación LACP S1 2→1→2, con restauración protegida.

Solo baja y levanta el MIEMBRO S05 s5c1 dentro de nl360-s05-lacp-s1.
No elimina namespaces, no cambia VLAN/bridge/FRR/ens33/systemd HA.
Ante corte SSH: temporizador transitorio systemd restaura s5c1.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import secrets
import shutil
import signal
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "s05_lacp_s1", ROOT / "scripts/laboratorio/s05_lacp_s1_integracion.py"
)
assert SPEC is not None and SPEC.loader is not None
lab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab)
MEMBER = "s5c1"
MAX_FALLBACK_SECONDS = 120
HTTP = "http://10.70.20.23:8080/api/v1/service"


def marker(message: str) -> None:
    print(f"========== {message} ==========", flush=True)


def identity() -> dict:
    lab.identity()
    data = lab.read_state()
    if data["status"] != "active":
        raise RuntimeError("LACP S1 no activo")
    if lab.alias_of(lab.CLIENT, MEMBER) != data["alias"]:
        raise RuntimeError("Puerto de prueba sin propiedad S05")
    return data


def check_http() -> None:
    raw = lab.ns_exec(
        lab.CLIENT, "curl", "--noproxy", "*", "-fsS",
        "--connect-timeout", "2", "--max-time", "6", HTTP,
        timeout=11,
    )
    doc = json.loads(raw)
    if doc.get("active_backend") != "BACKEND_HQ":
        raise RuntimeError(f"HTTP HQ no principal: {doc.get('active_backend')}")
    print("S05_LACP_S1_HTTP_REAL=200_BACKEND_HQ", flush=True)


def availability() -> None:
    for target in (lab.GW, "10.70.20.23", "10.71.20.21", "10.72.20.20"):
        lab.ping_verified(
            lab.CLIENT, target, prefix="S05_LACP_S1_FALLBACK_PING"
        )
    check_http()


def check_baseline(data: dict) -> None:
    lab.assert_management_preserved(data["before"]["mgmt"])
    lab.assert_protected(data["before"]["switch"])
    lab.assert_services()


def precheck() -> dict:
    data = identity()
    lab.status(data, ping=True)
    check_http()
    check_baseline(data)
    if shutil.which("systemd-run") is None:
        raise RuntimeError("systemd-run no disponible; no arriesgar enlace")
    lab.cmd("systemd-run", "--version")
    # Comprobar el API de systemd sin crear servicios en precheck.
    lab.cmd("systemctl", "--version")
    print("S05_LACP_S1_FALLA_PRECHECK=OK_SIN_CAMBIOS", flush=True)
    return data


def failsafe_arm() -> str:
    unit = "nl360-s05-lacp-s1-rescate-" + secrets.token_hex(5)
    ip = shutil.which("ip")
    if not ip or not Path(ip).is_absolute():
        raise RuntimeError("No se encontró iproute2 para protección")
    lab.cmd(
        "systemd-run", "--unit", unit,
        f"--on-active={MAX_FALLBACK_SECONDS}s",
        "--description", "NETLAB360 S05 LACP S1 restore-only watchdog",
        ip, "-n", lab.CLIENT, "link", "set", "dev", MEMBER, "up",
        root=True, timeout=14,
    )
    if lab.cmd("systemctl", "is-active", f"{unit}.timer").strip() != "active":
        raise RuntimeError("Temporizador de rescate no activo")
    print(f"S05_LACP_S1_RESCATE_SYSTEMD={unit}.timer", flush=True)
    return unit


def failsafe_cancel(unit: str) -> None:
    timer = f"{unit}.timer"
    load = lab.cmd("systemctl", "show", timer, "-p", "LoadState", "--value", check=False).strip()
    if load != "not-found":
        try:
            lab.cmd("systemctl", "stop", timer, root=True, timeout=14)
        except RuntimeError:
            if lab.cmd("systemctl", "show", timer, "-p", "LoadState", "--value", check=False).strip() != "not-found":
                raise
    state = lab.cmd("systemctl", "is-active", timer, check=False).strip()
    if state not in ("inactive", "failed", "unknown"):
        raise RuntimeError("Estado de temporizador no confirmado como inactivo")
    print("S05_LACP_S1_RESCATE_CANCELADO=SI", flush=True)


def interrupt(signum: int, _frame: object) -> None:
    raise InterruptedError(f"Señal recibida: {signum}; iniciar restauración")


def exercise() -> None:
    data = precheck()
    rescue = None
    changed = False
    saved_handlers: dict[int, object] = {}
    error = None
    try:
        rescue = failsafe_arm()
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            saved_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, interrupt)

        marker("S05_S1_INICIO_BASELINE_DOS")
        lab.bond_ports(lab.SW, lab.SW_BOND, 2, attempts=8)
        lab.bond_ports(lab.CLIENT, lab.CLIENT_BOND, 2, attempts=8)
        check_baseline(data)
        print("S05_LACP_S1_ESTADO_INICIAL=2_2", flush=True)

        marker("INICIO_CAPTURA_S05_53_LACP_S1_UN_ENLACE")
        # Solo una interfaz que ya existe y pertenece al cliente S05.
        if lab.alias_of(lab.CLIENT, MEMBER) != data["alias"]:
            raise RuntimeError("La identidad del miembro cambió antes de la falla")
        changed = True  # Garantiza restauración incluso si ip link set falla.
        lab.ip_ns(lab.CLIENT, "link", "set", "dev", MEMBER, "down")
        lab.bond_ports(lab.CLIENT, lab.CLIENT_BOND, 1, attempts=15)
        lab.bond_ports(lab.SW, lab.SW_BOND, 1, attempts=15)
        print("S05_LACP_S1_ESTADO_FALLA=1_1", flush=True)
        availability()
        check_baseline(data)
        print("S05_LACP_S1_SERVICIOS_DURANTE_FALLA=OK", flush=True)
        marker("FIN_CAPTURA_S05_53_LACP_S1_UN_ENLACE")
    except BaseException as exc:
        error = exc
        print(f"S05_LACP_S1_PRUEBA_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
    finally:
        for sig, handler in saved_handlers.items():
            signal.signal(sig, handler)
        # Restaurar antes de toda lectura, impresión o cancelación del rescate.
        if changed:
            try:
                if lab.alias_of(lab.CLIENT, MEMBER) != data["alias"]:
                    raise RuntimeError("Miembro reemplazado; preservar temporizador de rescate")
                lab.ip_ns(lab.CLIENT, "link", "set", "dev", MEMBER, "up")
                changed = False
                print("S05_LACP_S1_ENLACE_RESTAURADO=SI", flush=True)
            except BaseException as exc:
                print(f"S05_LACP_S1_RESTAURACION_ERROR={exc}", file=sys.stderr,
                      flush=True)
                if error is None:
                    error = exc

        # No cancelar rescate si no se acredita restauración del agregador.
        if not changed:
            try:
                marker("INICIO_CAPTURA_S05_54_LACP_S1_RETORNO")
                lab.bond_ports(lab.CLIENT, lab.CLIENT_BOND, 2, attempts=15)
                lab.bond_ports(lab.SW, lab.SW_BOND, 2, attempts=15)
                lab.status(data, ping=True)
                check_http()
                check_baseline(data)
                print("S05_LACP_S1_ESTADOS_2_1_2=OK" if error is None
                      else "S05_LACP_S1_ESTADO_FINAL_2=RECUPERADO_TRAS_ERROR",
                      flush=True)
                marker("FIN_CAPTURA_S05_54_LACP_S1_RETORNO")
                if rescue:
                    failsafe_cancel(rescue)
            except BaseException as exc:
                print(f"S05_LACP_S1_POSTCHECK_ERROR={exc}", file=sys.stderr, flush=True)
                if error is None:
                    error = exc
    if error is not None:
        raise RuntimeError(f"Ensayo incompleto, revisar logs: {error}") from error
    print("S05_LACP_S1_PRUEBA=OK_2_1_2", flush=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("precheck", "run"))
    p.add_argument("--confirm-failover", action="store_true")
    a = p.parse_args()
    if a.action == "run" and not a.confirm_failover:
        p.error("run requiere --confirm-failover")
    if a.action == "precheck" and a.confirm_failover:
        p.error("--confirm-failover solo con run")
    if a.action == "precheck":
        precheck()
    else:
        exercise()


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(f"S05_LACP_S1_FALLA_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
        sys.exit(2)
