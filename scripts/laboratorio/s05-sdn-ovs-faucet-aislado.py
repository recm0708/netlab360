#!/usr/bin/env python3
"""NETLAB360 S05: un único dominio OpenFlow aislado, sin tocar S02/FRR/VMnet8.

Acciones: plan, precheck, up --confirm-isolated, status, down --confirm-isolated.
Un fichero de estado exclusivo se escribe ANTES de mutar. Si un SSH se corta
durante UP, NO repetir UP: inspeccionar state-sdn.json y recursos.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BASE = Path.home() / "netlab360-bootstrap/s05/sdn-faucet"
STATE = BASE / "state-sdn.json"
CONFIG = BASE / "config/faucet.yaml"
LOGDIR = BASE / "logs"
BRIDGE = "br-s05-sdn"
OWNER = "NETLAB360_S05_SDN_V1"
CONTROLLER = "nl360-s05-faucet"
CONTROL_PORT = 16653
DPID = "0000000000000505"
IMAGE = "faucet/faucet@sha256:34c5d8c1ce207de37abc7e4d9b1b60e020d43524d85e80449c637a7867e5ea32"
FRR = {"nl360-s02-r-hq", "nl360-s02-r-s1", "nl360-s02-r-s2"}
HOSTS = {
    "a": ("sdna0", "sdna1", 1, "198.18.41.11/24"),
    "b": ("sdnb0", "sdnb1", 2, "198.18.41.12/24"),
    "c": ("sdnc0", "sdnc1", 3, "198.18.41.13/24"),
}
NS = {site: f"nl360-s05-sdn-{site}" for site in HOSTS}


def run(*args: str, timeout: int = 25, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
    if result.returncode not in allowed:
        error = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"RC={result.returncode}: {' '.join(args)} :: {error[:550]}")
    return result


def root(*args: str, timeout: int = 25, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    return run("sudo", "-n", *args, timeout=timeout, allowed=allowed)


def ovs(*args: str) -> str:
    return root("ovs-vsctl", "--timeout=12", *args, timeout=17).stdout.strip()


def link_names() -> set[str]:
    data = json.loads(run("ip", "-j", "link", "show").stdout)
    return {item["ifname"].split("@")[0] for item in data}


def namespaces() -> set[str]:
    return {line.split()[0] for line in root("ip", "netns", "list").stdout.splitlines() if line.strip()}


def docker_names() -> set[str]:
    return set(root("docker", "ps", "--format", "{{.Names}}").stdout.splitlines())


def docker_all_names() -> set[str]:
    return set(root("docker", "ps", "-a", "--format", "{{.Names}}").stdout.splitlines())


def management() -> dict[str, str]:
    addr = run("ip", "-4", "-br", "address", "show", "ens33").stdout.strip()
    route = run("ip", "-4", "route", "show", "default").stdout.strip()
    if "192.168.47.40/24" not in addr or "UP" not in addr:
        raise RuntimeError("Gestion ens33 no coincide con la linea base")
    if "via 192.168.47.2 dev ens33" not in route:
        raise RuntimeError("Gateway original no coincide")
    return {"ens33": addr, "route": route}


def baseline() -> dict:
    before = {"management": management(),
              "namespaces": sorted(namespaces()),
              "docker": sorted(docker_names())}
    if not FRR.issubset(set(before["docker"])):
        raise RuntimeError("Los tres FRR de S02 no estan activos")
    return before


def preserve(before: dict) -> None:
    if management() != before["management"]:
        raise RuntimeError("La red de gestion ha cambiado")
    if not set(before["namespaces"]).issubset(namespaces()):
        raise RuntimeError("Se perdio algun namespace previo S02/HA/LACP")
    if not set(before["docker"]).issubset(docker_names()):
        raise RuntimeError("Se detuvo algun contenedor previo, incluidos FRR")
    print("S05_SDN_BASELINE_S02_FRR_GESTION=CONSERVADA", flush=True)


def check_image() -> None:
    image_id = root("docker", "image", "inspect", IMAGE,
                    "--format", "{{.Id}}").stdout.strip()
    if not image_id.startswith("sha256:"):
        raise RuntimeError("La imagen Faucet no esta fijada por digest")


def precheck() -> dict:
    if STATE.exists() or STATE.is_symlink():
        raise RuntimeError("Ya existe estado SDN; NO repetir up")
    if not CONFIG.is_file() or CONFIG.is_symlink():
        raise RuntimeError("Configuracion Faucet faltante o simbolica")
    if not LOGDIR.is_dir() or LOGDIR.is_symlink():
        raise RuntimeError("Directorio de logs no preparado")
    check_image()
    before = baseline()
    if ovs("list-br"):
        raise RuntimeError("Hay bridges OVS preexistentes; abortar")
    names = link_names()
    blocked = ({BRIDGE} | {value[0] for value in HOSTS.values()} |
               {value[1] for value in HOSTS.values()}) & names
    if blocked:
        raise RuntimeError(f"Dispositivos ocupados: {sorted(blocked)}")
    occupied_ns = set(NS.values()) & namespaces()
    if occupied_ns:
        raise RuntimeError(f"Namespaces ocupados: {sorted(occupied_ns)}")
    if CONTROLLER in docker_all_names():
        raise RuntimeError("Contenedor Faucet ya existe, NO reemplazar")
    listen = root("ss", "-ltnH").stdout
    if any(re.search(rf":{CONTROL_PORT}\s", line) for line in listen.splitlines()):
        raise RuntimeError("Puerto TCP de control ya ocupado")
    print("S05_SDN_PRECHECK=OK_SIN_CAMBIOS", flush=True)
    return before


def state_write(data: dict, *, exclusive: bool = False) -> None:
    BASE.mkdir(parents=True, exist_ok=True)
    if exclusive:
        fd = os.open(STATE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
    else:
        temp = STATE.with_suffix(".json.tmp")
        with temp.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
        temp.replace(STATE)


def state_read() -> dict:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("Falta state-sdn.json o su tipo no es seguro")
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if data.get("owner") != OWNER or data.get("bridge") != BRIDGE:
        raise RuntimeError("Propietario o bridge en el estado no corresponde")
    return data


def owned_controller() -> bool:
    if CONTROLLER not in docker_all_names():
        return False
    label = root("docker", "inspect", "--format",
                 '{{index .Config.Labels "netlab360.owner"}}',
                 CONTROLLER).stdout.strip()
    if label != OWNER:
        raise RuntimeError("Contenedor existente pertenece a otro propietario")
    return True


def owned_bridge() -> bool:
    if BRIDGE not in ovs("list-br").splitlines():
        return False
    owner = ovs("get", "Bridge", BRIDGE, "external_ids:netlab360-owner").strip('"')
    if owner != OWNER:
        raise RuntimeError("Bridge OVS pertenece a otro propietario")
    return True


def up() -> None:
    before = precheck()
    state = {"owner": OWNER, "bridge": BRIDGE, "status": "provisioning",
             "before": before, "image": IMAGE, "hosts": HOSTS}
    state_write(state, exclusive=True)
    print("S05_SDN_STATE=CREADO_ANTES_DE_MODIFICACIONES", flush=True)
    try:
        root("docker", "run", "-d", "--name", CONTROLLER,
             "--restart", "no", "--cap-drop", "ALL",
             "--security-opt", "no-new-privileges",
             "--label", f"netlab360.owner={OWNER}",
             "-p", f"127.0.0.1:{CONTROL_PORT}:6653",
             "-v", f"{CONFIG.parent}:/etc/faucet:ro",
             "-v", f"{LOGDIR}:/var/log/faucet:rw",
             IMAGE, timeout=40)
        print("S05_SDN_FAUCET_CONTAINER=CREADO", flush=True)
        ovs("add-br", BRIDGE)
        ovs("set", "Bridge", BRIDGE, "external_ids:netlab360-owner=" + OWNER,
            "other_config:datapath-id=" + DPID,
            "other_config:disable-in-band=true", "fail_mode=secure",
            "protocols=OpenFlow13")
        print("S05_SDN_OVS_BRIDGE=CREADO_AISLADO", flush=True)
        for site, (host, peer, port, addr) in HOSTS.items():
            ns = NS[site]
            root("ip", "netns", "add", ns)
            root("ip", "link", "add", host, "type", "veth", "peer", "name", peer)
            root("ip", "link", "set", peer, "netns", ns)
            root("ip", "-n", ns, "link", "set", peer, "name", "eth0")
            root("ip", "-n", ns, "link", "set", "lo", "up")
            root("ip", "-n", ns, "addr", "add", addr, "dev", "eth0")
            root("ip", "-n", ns, "link", "set", "eth0", "up")
            ovs("add-port", BRIDGE, host,
                "--", "set", "Interface", host, f"ofport_request={port}")
            root("ip", "link", "set", host, "up")
            print(f"S05_SDN_HOST_{site.upper()}={ns}/{addr}/OFPORT_{port}", flush=True)
        ovs("set-controller", BRIDGE, f"tcp:127.0.0.1:{CONTROL_PORT}")
        print("S05_SDN_OVS_CONTROLLER_CONFIGURADO=LOCALHOST", flush=True)
        for attempt in range(1, 16):
            connected = ovs("--format=csv", "--data=bare",
                            "--no-heading", "--columns=is_connected",
                            "list", "Controller").lower()
            if "true" in connected.splitlines():
                print(f"S05_SDN_OPENFLOW_CONECTADO=OK_INTENTO_{attempt}", flush=True)
                break
            time.sleep(1)
        else:
            raise RuntimeError("Faucet/OVS no establecieron canal OpenFlow")
        # El canal TCP puede estar conectado ANTES de instalarse el pipeline.
        # Reintentar la aceptacion sin volver a crear ningun recurso.
        last = None
        for attempt in range(1, 4):
            try:
                status()
                print(f"S05_SDN_ACEPTACION_INTENTO_{attempt}=OK", flush=True)
                break
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                last = exc
                print(f"S05_SDN_ACEPTACION_INTENTO_{attempt}=PENDIENTE",
                      flush=True)
                if attempt < 3:
                    time.sleep(3)
        else:
            raise RuntimeError(f"No se confirmo el flujo SDN: {last}")
        state["status"] = "active"
        state_write(state)
        print("S05_SDN_DESPLIEGUE=OK", flush=True)
    except BaseException as exc:
        state["status"] = "needs_inspection"
        state["error"] = str(exc)[:500]
        state_write(state)
        print("S05_SDN_UP=INTERRUMPIDO_REVISAR_ESTADO_NO_REPETIR", flush=True)
        raise


def ping(site: str, target: str, *, expect_success: bool) -> None:
    ns = NS[site]
    last = None
    for attempt in range(1, 3):
        p = root("ip", "netns", "exec", ns, "ping", "-n", "-c", "2", "-W", "2",
                 target, timeout=12, allowed=(0, 1, 2))
        if expect_success and p.returncode == 0:
            print(f"S05_SDN_PING_{site.upper()}_{target}=OK_INTENTO_{attempt}", flush=True)
            return
        if not expect_success and p.returncode == 1:
            print(f"S05_SDN_AISLAMIENTO_{site.upper()}_{target}=BLOQUEADO", flush=True)
            return
        last = p.returncode
        time.sleep(1)
    raise RuntimeError(f"Conectividad no validada de {site} hacia {target}: RC={last}")


def status() -> None:
    state = state_read()
    if state.get("status") not in ("active", "provisioning"):
        raise RuntimeError("Estado SDN parcial, requiere inspeccion antes de validar")
    if not owned_bridge() or not owned_controller():
        raise RuntimeError("OVS o controlador esperado no estan presentes")
    running = root("docker", "inspect", "--format", "{{.State.Running}}",
                   CONTROLLER).stdout.strip()
    if running != "true":
        raise RuntimeError("Faucet no esta ejecutandose")
    if not set(NS.values()).issubset(namespaces()):
        raise RuntimeError("Faltan namespaces SDN")
    ports = set(ovs("list-ports", BRIDGE).splitlines())
    if ports != {item[0] for item in HOSTS.values()}:
        raise RuntimeError(f"Puertos SDN inesperados: {sorted(ports)}")
    for site, (host, _, port, addr) in HOSTS.items():
        ofport = ovs("get", "Interface", host, "ofport")
        if ofport != str(port):
            raise RuntimeError(f"OFPORT no coincide: {site} {ofport} != {port}")
        ns_addr = root("ip", "-n", NS[site], "-4", "-br",
                       "address", "show", "eth0").stdout
        if addr not in ns_addr:
            raise RuntimeError(f"IP del cliente SDN {site} no coincide")
        print(f"S05_SDN_OFPORT_{site.upper()}={port}_VLAN_{410 if site in ('a', 'b') else 420}", flush=True)
    connected = ovs("--format=csv", "--data=bare", "--no-heading",
                    "--columns=is_connected", "list", "Controller").lower()
    if "true" not in connected.splitlines():
        raise RuntimeError("Controlador OpenFlow desconectado")
    print("S05_SDN_FAUCET_OPENFLOW=CONNECTED", flush=True)
    flows = root("ovs-ofctl", "-O", "OpenFlow13", "dump-flows", BRIDGE,
                 timeout=15).stdout
    flow_count = sum("cookie=" in row for row in flows.splitlines())
    if flow_count < 2:
        raise RuntimeError("No hay reglas suficientes observadas en OpenFlow")
    print(f"S05_SDN_OPENFLOW_REGLAS_OBSERVADAS={flow_count}", flush=True)
    ping("a", "198.18.41.12", expect_success=True)
    ping("b", "198.18.41.11", expect_success=True)
    ping("a", "198.18.41.13", expect_success=False)
    ping("c", "198.18.41.11", expect_success=False)
    preserve(state["before"])
    print("S05_SDN_STATUS=OK_SEGMENTACION_A_B_Y_C", flush=True)


def down() -> None:
    state = state_read()
    if owned_bridge():
        ports = set(ovs("list-ports", BRIDGE).splitlines())
        expected = {row[0] for row in HOSTS.values()}
        if not ports.issubset(expected):
            raise RuntimeError("Hay puertos ajenos en bridge; no eliminar")
    if owned_controller() and owned_bridge():
        pass
    print("S05_SDN_DOWN=SOLO_RECURSOS_PROPIEDAD_S05", flush=True)
    if owned_bridge():
        ovs("del-br", BRIDGE)
    for ns in NS.values():
        if ns in namespaces():
            root("ip", "netns", "delete", ns)
    for host, peer, _, _ in HOSTS.values():
        if host in link_names():
            root("ip", "link", "delete", host)
    if owned_controller():
        root("docker", "rm", "-f", CONTROLLER)
    preserve(state["before"])
    STATE.unlink()
    print("S05_SDN_DOWN=OK_RECURSOS_AISLADOS", flush=True)


def inspect() -> None:
    """Diagnostico read-only incluso si UP quedo parcial tras perder SSH."""
    print("========== S05 SDN INSPECCION SOLO LECTURA ==========")
    print(f"S05_SDN_STATE_EXISTE={STATE.exists() or STATE.is_symlink()}")
    if STATE.is_file() and not STATE.is_symlink():
        data = state_read()
        print(f"S05_SDN_STATE_STATUS={data.get('status', 'UNKNOWN')}")
        if data.get("error"):
            print(f"S05_SDN_STATE_ERROR={data['error']}")
    print(f"S05_SDN_OVS_BRIDGES={ovs('list-br').replace(chr(10), ',')}")
    if BRIDGE in ovs("list-br").splitlines():
        print(f"S05_SDN_BRIDGE_PROPIETARIO_OK={owned_bridge()}")
        print(f"S05_SDN_PORTS={ovs('list-ports', BRIDGE).replace(chr(10), ',')}")
    print("S05_SDN_NAMESPACES=" +
          ",".join(sorted(set(NS.values()) & namespaces())))
    print("S05_SDN_HOST_LINKS=" +
          ",".join(sorted({v[0] for v in HOSTS.values()} & link_names())))
    print(f"S05_SDN_CONTENEDOR_EXISTE={owned_controller()}")
    before = management()
    print("S05_SDN_GESTION=" + before["ens33"])
    print("S05_SDN_GATEWAY=" + before["route"])
    print("S05_SDN_INSPECCION=OK_SIN_CAMBIOS", flush=True)


def plan() -> None:
    print("S05_SDN_PLAN=DPID_0x505_VLAN_410_420_NO_S02", flush=True)
    for site, (host, _, port, address) in HOSTS.items():
        print(f"S05_SDN_PLAN_{site.upper()}={NS[site]}/{host}/OFPORT_{port}/{address}")
    print("S05_SDN_PLAN=NO_MODIFICAR_ENS33_FRR_WAN_LACP_HA", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("plan", "precheck", "up", "status", "inspect", "down"))
    parser.add_argument("--confirm-isolated", action="store_true")
    args = parser.parse_args()
    if args.action in ("up", "down") and not args.confirm_isolated:
        parser.error("up/down exigen --confirm-isolated")
    try:
        {"plan": plan, "precheck": precheck, "up": up,
         "status": status, "inspect": inspect, "down": down}[args.action]()
    except Exception as exc:
        print(f"S05_SDN_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
