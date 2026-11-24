#!/usr/bin/env python3
"""Recupera SOLO Faucet existente tras [Errno 13] en /var/log/faucet.

NO recrea contenedor, bridge, veth ni namespaces. NO altera S02, FRR,
ens33, VLAN, LACP o NOC. No aceptar sin conectividad/segmentacion reales.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

LAB_PATH = Path(__file__).resolve().with_name("s05_sdn_ovs_faucet_aislado.py")
spec = importlib.util.spec_from_file_location("s05_sdn_lab_recovery", LAB_PATH)
assert spec is not None and spec.loader is not None
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)

EXPECTED_FAILURE = "Permission denied: '/var/log/faucet/faucet.log'"


def preflight() -> tuple[dict, dict]:
    """Todos los controles son solo lectura, nunca modifica estado."""
    data = lab.state_read()
    if data.get("status") != "needs_inspection":
        raise RuntimeError("El estado no es needs_inspection; no recuperar")
    if data.get("image") != lab.IMAGE:
        raise RuntimeError("La imagen del state no coincide con el digest")
    if not lab.owned_bridge() or not lab.owned_controller():
        raise RuntimeError("Propiedad SDN del bridge o contenedor no verificada")
    if lab.ovs("get-controller", lab.BRIDGE) != "tcp:127.0.0.1:16653":
        raise RuntimeError("Controlador OVS diferente de localhost previsto")
    if set(lab.ovs("list-ports", lab.BRIDGE).splitlines()) != {
        row[0] for row in lab.HOSTS.values()
    }:
        raise RuntimeError("Puertos de bridge inesperados, detener")
    if not set(lab.NS.values()).issubset(lab.namespaces()):
        raise RuntimeError("Faltan namespaces propios; no recuperar automáticamente")
    for site, (host, _, port, addr) in lab.HOSTS.items():
        if lab.ovs("get", "Interface", host, "ofport") != str(port):
            raise RuntimeError(f"Ofport incorrecto de {site}")
        observed = lab.root("ip", "-n", lab.NS[site], "-4",
                            "-br", "address", "show", "eth0").stdout
        if addr not in observed:
            raise RuntimeError(f"IP inesperada en {site}")
    lab.preserve(data["before"])

    raw = lab.root("docker", "inspect", lab.CONTROLLER).stdout
    container = json.loads(raw)[0]
    cfg = container.get("Config", {})
    state = container.get("State", {})
    if cfg.get("Image") != lab.IMAGE:
        raise RuntimeError("Imagen de contenedor distinta del digest permitido")
    if cfg.get("User") not in ("", "0", "0:0", "root", "root:root"):
        raise RuntimeError("El contenedor no inicia con usuario root: revisar UID")
    if state.get("Running") is False and (
        state.get("Status") != "exited" or state.get("ExitCode") != 255
    ):
        raise RuntimeError("Salida del contenedor diferente del fallo 255 previsto")
    if not state.get("Running") and state.get("Status") != "exited":
        raise RuntimeError("Estado Docker no recuperable de forma automática")

    bindings = container.get("HostConfig", {}).get("PortBindings", {})
    mapping = bindings.get("6653/tcp", [])
    if not any(x.get("HostIp") == "127.0.0.1" and
               x.get("HostPort") == "16653" for x in mapping):
        raise RuntimeError("Publicación Docker 127.0.0.1:16653→6653 no coincide")

    mounts = container.get("Mounts", [])
    expected = {
        "/var/log/faucet": (lab.LOGDIR, True),
        "/etc/faucet": (lab.CONFIG.parent, False),
    }
    for destination, (source, writable) in expected.items():
        matches = [x for x in mounts if x.get("Destination") == destination]
        if len(matches) != 1:
            raise RuntimeError(f"Mount {destination} ausente o duplicado")
        mount = matches[0]
        if (mount.get("Type") != "bind"
                or os.path.realpath(mount.get("Source", "")) != str(source.resolve())
                or mount.get("RW") is not writable):
            raise RuntimeError(f"Mount {destination} distinto del autorizado")

    if lab.LOGDIR.is_symlink() or not lab.LOGDIR.is_dir():
        raise RuntimeError("Directorio logs ausente o simbólico")
    info = os.stat(lab.LOGDIR)
    if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o002:
        raise RuntimeError("Logs no es directorio normal o es world-writable")

    log = lab.root("docker", "logs", "--tail", "100", lab.CONTROLLER,
                   timeout=15)
    all_logs = log.stdout + log.stderr
    if EXPECTED_FAILURE not in all_logs:
        raise RuntimeError("No consta la causa Errno13; no aplicar reparación")

    print(f"S05_SDN_RECOVERY_STATE={data['status']}", flush=True)
    print(f"S05_SDN_RECOVERY_DOCKER={state['Status']}_EXIT_{state.get('ExitCode')}",
          flush=True)
    print(f"S05_SDN_RECOVERY_LOGS_PERMISSIONS={info.st_uid}:{info.st_gid}:"
          f"{stat.S_IMODE(info.st_mode):04o}", flush=True)
    print("S05_SDN_RECOVERY_CAUSA=ERRNO13_LOG_FAUCET_VERIFICADA", flush=True)
    print("S05_SDN_RECOVERY_PROPIEDAD_Y_S02=VALIDADOS", flush=True)
    return data, container


def recover() -> None:
    data, container = preflight()
    # root del contenedor SIN CAP_DAC_OVERRIDE necesita ser DUEÑO del bind.
    # Conserva el grupo del usuario para permitir lectura de evidencias.
    lab.root("chown", f"0:{os.getgid()}", str(lab.LOGDIR))
    lab.root("chmod", "0750", str(lab.LOGDIR))
    print("S05_SDN_RECOVERY_LOGS=ROOT_OWNER_MODE_0750", flush=True)

    if container["State"]["Running"] is False:
        lab.root("docker", "start", lab.CONTROLLER, timeout=40)
        print("S05_SDN_RECOVERY_FAUCET=START_EXISTING_CONTAINER", flush=True)
    else:
        print("S05_SDN_RECOVERY_FAUCET=ALREADY_RUNNING_NO_RESTART", flush=True)

    for attempt in range(1, 22):
        connected = lab.ovs("--format=csv", "--data=bare",
                            "--no-heading", "--columns=is_connected",
                            "list", "Controller").lower()
        if "true" in connected.splitlines():
            print(f"S05_SDN_RECOVERY_OPENFLOW=CONNECTED_INTENTO_{attempt}",
                  flush=True)
            break
        time.sleep(1)
    else:
        raise RuntimeError("Faucet no conectó: NO declarar SDN recuperado")

    # Aceptación integral en estado needs_inspection sin forzar status=active.
    last = None
    for attempt in range(1, 4):
        try:
            lab.status(allow_recovery=True)
            print(f"S05_SDN_RECOVERY_ACEPTACION=OK_INTENTO_{attempt}", flush=True)
            break
        except (RuntimeError, subprocess.TimeoutExpired, TimeoutError) as exc:
            last = exc
            print(f"S05_SDN_RECOVERY_ACEPTACION=PENDIENTE_INTENTO_{attempt}",
                  flush=True)
            if attempt < 3:
                time.sleep(3)
    else:
        raise RuntimeError(f"SDN NO validado (state permanece parcial): {last}")

    data["recovery"] = {
        "cause": EXPECTED_FAILURE,
        "action": "chown root:host-group chmod 0750 log bind; docker start existing",
        "validation": "OVS connected, flows, 4 pings VLAN, S02 preserved",
        "previous_error": data.get("error", ""),
    }
    data.pop("error", None)
    data["status"] = "active"
    lab.state_write(data)
    print("S05_SDN_RECOVERY_STATUS=ACTIVE_TRAS_ACEPTACION_REAL", flush=True)
    print("S05_SDN_RECOVERY=OK_SIN_RECREAR_RECURSOS", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("precheck", "recover"))
    parser.add_argument("--confirm-recovery", action="store_true")
    args = parser.parse_args()
    if args.action == "recover" and not args.confirm_recovery:
        parser.error("recover exige --confirm-recovery")
    try:
        if args.action == "precheck":
            preflight()
        else:
            recover()
    except Exception as exc:
        print(f"S05_SDN_RECOVERY_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
