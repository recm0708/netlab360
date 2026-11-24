#!/usr/bin/env python3
"""NETLAB360 S05: fallo/retorno exclusivo de sdna0, con rescate systemd.

El experimento interrumpe el puerto HOST OVS sdna0 y demuestra que A→B
deja de funcionar; C sigue aislado. Un timer restore-only re-habilita
sdna0 incluso si se interrumpe SSH. Nunca mueve ens33 ni reinicia Faucet.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import secrets
import shutil
import signal
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "scripts/laboratorio/s05_sdn_ovs_faucet_aislado.py"
CHECK = ROOT / "scripts/validacion/s05_sdn_evidencia60_aislamiento.py"
spec = importlib.util.spec_from_file_location("s05_sdn_ovs_fault", LAB)
assert spec and spec.loader
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)
spec_check = importlib.util.spec_from_file_location("s05_sdn_icmp_fault", CHECK)
assert spec_check and spec_check.loader
icmp = importlib.util.module_from_spec(spec_check)
spec_check.loader.exec_module(icmp)

PORT = "sdna0"
RESCUE_PREFIX = "nl360-s05-sdn-port-a-rescate-"
RESCUE_SECONDS = 120
SERVICES = (
    "netlab360-s04-exporter",
    "netlab360-s05-noc",
    "netlab360-s05-ha-backend-hq",
    "netlab360-s05-ha-backend-s1",
    "netlab360-s05-ha-frontal-hq",
    "netlab360-s05-ha-monitor-s2",
)


def marker(label: str) -> None:
    print(f"========== {label} ==========", flush=True)


def device_up() -> bool:
    raw = lab.root("ip", "-j", "link", "show", "dev", PORT).stdout
    links = json.loads(raw)
    if len(links) != 1 or links[0].get("ifname", "").split("@")[0] != PORT:
        raise RuntimeError("sdna0 no es una interfaz exclusiva identificable")
    return "UP" in links[0].get("flags", [])


def controller_connected() -> None:
    connected = lab.ovs("--format=csv", "--data=bare", "--no-heading",
                        "--columns=is_connected", "list", "Controller").lower()
    if "true" not in connected.splitlines():
        raise RuntimeError("Faucet no esta conectado a OVS")
    print("S05_SDN_FAULT_OPENFLOW=CONNECTED", flush=True)


def protected_services(data: dict) -> None:
    lab.preserve(data["before"])
    for unit in SERVICES:
        status = lab.run("systemctl", "is-active", unit, allowed=(0, 3)).stdout.strip()
        if status != "active":
            raise RuntimeError(f"Servicio protegido no activo: {unit} ({status})")
    print("S05_SDN_FAULT_GESTION_FRR_NOC_HA=CONSERVADOS", flush=True)


# La propiedad del bridge, controlador y puerto debe comprobarse antes de inducir una interrupción.
def precheck() -> dict:
    data = lab.state_read()
    if data.get("status") != "active":
        raise RuntimeError("SDN no esta activo; no provocar fallo")
    if not lab.owned_bridge() or not lab.owned_controller():
        raise RuntimeError("Bridge o contenedor no pertenecen a S05")
    ports = lab.ovs("list-ports", lab.BRIDGE).splitlines()
    if set(ports) != {row[0] for row in lab.HOSTS.values()}:
        raise RuntimeError("Puertos OVS ajenos; no arriesgar enlace")
    if lab.ovs("get", "Interface", PORT, "ofport") != "1":
        raise RuntimeError("Ofport A no es OFPORT1")
    if not device_up():
        raise RuntimeError("sdna0 no esta UP; evitar segundo fallo")
    if not shutil.which("systemd-run") or not shutil.which("ip"):
        raise RuntimeError("No hay systemd-run/ip para rescate temporizado")
    timers = lab.root("systemctl", "list-timers", "--all", "--plain",
                      "--no-legend", timeout=14).stdout
    if RESCUE_PREFIX in timers:
        raise RuntimeError("Ya existe un temporizador de rescate SDN pendiente")
    lab.status()
    protected_services(data)
    print("S05_SDN_FAULT_PRECHECK=OK_SIN_MODIFICACIONES", flush=True)
    return data


# Armamos el rescate independiente antes de deshabilitar el puerto; no depende del proceso SSH.
def failsafe_arm() -> str:
    executable = shutil.which("ip")
    if not executable or not Path(executable).is_absolute():
        raise RuntimeError("iproute2 sin ruta absoluta")
    name = RESCUE_PREFIX + secrets.token_hex(5)
    lab.root("systemd-run", "--unit", name,
             f"--on-active={RESCUE_SECONDS}s",
             "--description", "NETLAB360 S05 re-enable sdna0 only",
             executable, "link", "set", "dev", PORT, "up", timeout=18)
    print(f"S05_SDN_FAULT_RESCATE={name}.timer", flush=True)
    return name


def failsafe_cancel(name: str) -> None:
    lab.root("systemctl", "stop", name + ".timer", timeout=15)
    print("S05_SDN_FAULT_RESCATE_CANCELADO=SI", flush=True)


def interrupt(signal_number: int, _frame: object) -> None:
    raise InterruptedError(f"Interrupcion recibida: {signal_number}")


def run_fault() -> None:
    data = precheck()
    rescue: str | None = None
    may_have_changed = False
    error: BaseException | None = None
    old_handlers: dict[int, object] = {}
    try:
        rescue = failsafe_arm()
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            old_handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, interrupt)

        marker("INICIO_CAPTURA_S05_61_SDN_A_ENLACE_CAIDO")
        if not device_up() or not lab.owned_bridge():
            raise RuntimeError("Identidad del puerto A cambio antes del fallo")
        may_have_changed = True
        lab.root("ip", "link", "set", "dev", PORT, "down")
        if device_up():
            raise RuntimeError("Puerto sdna0 sigue UP: falla no acreditada")
        print("S05_SDN_PORT_A_ESTADO=DOWN", flush=True)
        icmp.measure("a", "198.18.41.12", allowed=False)
        controller_connected()
        protected_services(data)
        print("S05_SDN_FALLA_ENLACE=CONFIRMADA_SIN_A_B", flush=True)
        marker("FIN_CAPTURA_S05_61_SDN_A_ENLACE_CAIDO")
    except BaseException as exc:
        error = exc
        print(f"S05_SDN_FAULT_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
    finally:
        for sig, previous in old_handlers.items():
            signal.signal(sig, previous)
        if may_have_changed:
            try:
                if not lab.owned_bridge() or PORT not in lab.ovs("list-ports", lab.BRIDGE).splitlines():
                    raise RuntimeError("Propiedad del puerto perdida; watchdog permanece")
                lab.root("ip", "link", "set", "dev", PORT, "up")
                may_have_changed = False
                print("S05_SDN_PORT_A_RESTAURACION=SOLICITADA", flush=True)
            except BaseException as exc:
                print(f"S05_SDN_FAULT_RESTORE_ERROR={exc}", file=sys.stderr, flush=True)
                if error is None:
                    error = exc
        if not may_have_changed:
            try:
                marker("INICIO_CAPTURA_S05_62_SDN_A_ENLACE_RESTAURADO")
                if not device_up():
                    raise RuntimeError("sdna0 no aparece UP tras restauracion")
                last: BaseException | None = None
                for attempt in range(1, 5):
                    try:
                        lab.status()
                        controller_connected()
                        protected_services(data)
                        print(f"S05_SDN_RETORNO_VERIFICADO=INTENTO_{attempt}", flush=True)
                        break
                    except (RuntimeError, TimeoutError) as exc:
                        last = exc
                        if attempt < 4:
                            time.sleep(3)
                else:
                    raise RuntimeError(f"Retorno sin aceptacion: {last}")
                marker("FIN_CAPTURA_S05_62_SDN_A_ENLACE_RESTAURADO")
                if rescue:
                    failsafe_cancel(rescue)
            except BaseException as exc:
                print(f"S05_SDN_FAULT_POSTCHECK_ERROR={exc}", file=sys.stderr, flush=True)
                if error is None:
                    error = exc
    if error is not None:
        raise RuntimeError(f"Prueba SDN incompleta; conservado rescate si es necesario: {error}")
    print("S05_SDN_FALLA_RETORNO=OK_DOWN_UP_ENLACE_A", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("precheck", "run"))
    parser.add_argument("--confirm-fault", action="store_true")
    args = parser.parse_args()
    if args.action == "run" and not args.confirm_fault:
        parser.error("run exige --confirm-fault")
    if args.action == "precheck":
        precheck()
    else:
        run_fault()


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        print(f"S05_SDN_FALLA_RETORNO_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr, flush=True)
        sys.exit(2)
