#!/usr/bin/env python3
"""NETLAB360 S02: WAN veth 3 routers/4 enlaces, SOLO namespaces FRR.

plan: validacion declarativa sin sudo, sin cambios.
precheck: comprueba identidad de routers, redes y ausencia de enlaces previos.
up: crea 4 veth, loopbacks, IP, aplica FRR; rollback exclusivo si falla.
La prueba de vecinos OSPF/FIB se realiza despues mediante validador independiente.
status: muestra interfaces/vecindades/rutas sin cambios.
down: retira SOLO los enlaces WAN de S02, sin detener los 3 routers.
No modifica ens33, VMnet8, rutas/firewall del host, ni namespaces ajenos.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime

import yaml

ROOT = Path.home() / "proyectos/netlab360"
BASE = Path.home() / "netlab360-bootstrap/s02"
STATE = BASE / "wan-links-state.json"
IPAM = ROOT / "inventario/ipam/topologia-s02.yaml"
OWNER = "NETLAB360_S02_WAN_LINKS_V1"
PROJECT = "netlab360-s02-wan"
ROUTERS = {
    "R-HQ": "nl360-s02-r-hq",
    "R-S1": "nl360-s02-r-s1",
    "R-S2": "nl360-s02-r-s2",
}
# VLAN y switches NO se crean en este paso. Nombre WAN distinto por router.
LINKS = [
    ("WAN-PRIMARIA-HQ-S1", "s1p", "R-S1", "n2h1p", "n2s1p"),
    ("WAN-RESPALDO-HQ-S1", "s1b", "R-S1", "n2h1b", "n2s1b"),
    ("WAN-PRIMARIA-HQ-S2", "s2p", "R-S2", "n2h2p", "n2s2p"),
    ("WAN-RESPALDO-HQ-S2", "s2b", "R-S2", "n2h2b", "n2s2b"),
]


def execute(*argv: str, allow_failure: bool = False, timeout: int = 35) -> str:
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    if p.returncode and not allow_failure:
        raise RuntimeError(
            f"Comando fallido ({p.returncode}): {' '.join(argv)}\n"
            f"{p.stdout[-2500:]} {p.stderr[-2500:]}"
        )
    return p.stdout


def privilege(*argv: str, **kwargs) -> str:
    return execute("sudo", "-n", *argv, **kwargs)


def plan() -> list[dict]:
    data = yaml.safe_load(IPAM.read_text(encoding="utf-8"))
    if data.get("schema_version") != "0.2" or data.get("status") != "candidate":
        raise ValueError("IPAM S02 no es candidate schema_version=0.2")
    found = {v["id"]: v for v in data["wan_links"]}
    if len(found) != 4 or set(found) != {x[0] for x in LINKS}:
        raise ValueError("IPAM no contiene exactamente las cuatro WAN S02")
    records = []
    for ident, nic, branch, temp_hq, temp_br in LINKS:
        v = found[ident]
        if v["a"]["router"] != "R-HQ" or v["b"]["router"] != branch:
            raise ValueError(f"Extremos incorrectos para {ident}")
        if v["ospf_cost"] != (10 if "PRIMARIA" in ident else 100):
            raise ValueError(f"Costo OSPF incorrecto: {ident}")
        records.append({
            "id": ident, "nic": nic, "branch": branch,
            "temporary_hq": temp_hq, "temporary_branch": temp_br,
            "hq_ip": v["a"]["address"], "branch_ip": v["b"]["address"],
        })
        print(f"S02_PLAN={ident} IF={nic} HQ={v['a']['address']} "
              f"{branch}={v['b']['address']} COSTO={v['ospf_cost']}")
    print("S02_PLAN_WAN=4")
    return records


def containers() -> dict:
    info = {}
    for logical, name in ROUTERS.items():
        data = json.loads(privilege("docker", "inspect", name))[0]
        if not data["State"]["Running"]:
            raise RuntimeError(f"Router detenido: {name}")
        if data["HostConfig"]["NetworkMode"] != "none":
            raise RuntimeError(f"Red Docker no aislada: {name}")
        if data["Config"].get("Image") != "quay.io/frrouting/frr:10.7.1":
            raise RuntimeError(f"Imagen FRR inesperada: {name}")
        labels = data["Config"].get("Labels") or {}
        if labels.get("com.docker.compose.project") != PROJECT:
            raise RuntimeError(f"Contenedor ajeno a Compose S02: {name}")
        pid = data["State"]["Pid"]
        if not isinstance(pid, int) or pid <= 1:
            raise RuntimeError(f"PID invalido: {name}")
        info[logical] = {"id": data["Id"], "pid": str(pid), "name": name}
    return info


def ns(info: dict, logical: str, *args: str, allow_failure: bool = False) -> str:
    return privilege(
        "nsenter", "-t", info[logical]["pid"], "-n", *args,
        allow_failure=allow_failure,
    )


def host_before() -> dict:
    addr = execute("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    default = execute("ip", "-4", "route", "show", "default")
    if "192.168.47.40/24" not in addr:
        raise RuntimeError("IP administrativa inesperada")
    if "default via 192.168.47.2 dev ens33" not in default:
        raise RuntimeError("Gateway administrativo inesperado")
    return {
        "ens33": addr,
        "routes": execute("ip", "-4", "route", "show", "table", "main"),
    }


def precheck(records: list[dict], current: dict) -> dict:
    host = host_before()
    if STATE.exists() or STATE.is_symlink():
        raise RuntimeError("WAN S02 posee estado previo; usar status/down o diagnosticar")
    for logical, loop in (("R-HQ", "10.79.0.1/32"), ("R-S1", "10.79.0.2/32"), ("R-S2", "10.79.0.3/32")):
        output = ns(current, logical, "ip", "-4", "-o", "addr", "show", "dev", "lo")
        if loop in output:
            raise RuntimeError(f"Loopback S02 preexistente: {logical} {loop}")
    for v in records:
        for dev in (v["temporary_hq"], v["temporary_branch"]):
            if execute("ip", "link", "show", "dev", dev, allow_failure=True):
                raise RuntimeError(f"Veth temporal preexistente: {dev}")
        for site, temp in (("R-HQ", v["temporary_hq"]), (v["branch"], v["temporary_branch"])):
            for dev in (v["nic"], temp):
                if ns(current, site, "ip", "link", "show", "dev", dev, allow_failure=True):
                    raise RuntimeError(f"Interfaz preexistente: {site}/{dev}")
    if execute("git", "-C", str(ROOT), "status", "--porcelain").strip():
        raise RuntimeError("Git tiene cambios locales pendientes")
    privilege("docker", "image", "inspect", "quay.io/frrouting/frr:10.7.1")
    print("S02_WAN_PRECHECK=OK")
    return host


def verify_ownership(state: dict, current: dict) -> None:
    if state.get("owner") != OWNER or set(state.get("ids", {})) != set(ROUTERS):
        raise RuntimeError("Marcador de propiedad WAN S02 invalido")
    for logical, item in current.items():
        if item["id"] != state["ids"][logical]:
            raise RuntimeError(f"Router reemplazado; no modificar red: {logical}")


def cleanup(records: list[dict], current: dict) -> None:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("Sin estado WAN S02 seguro para retirar interfaces")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    verify_ownership(state, current)
    for v in records:
        # Borrar un solo extremo destruye ambos extremos del par veth.
        for logical in ("R-HQ", v["branch"]):
            if ns(current, logical, "ip", "link", "show", "dev", v["nic"], allow_failure=True):
                ns(current, logical, "ip", "link", "delete", "dev", v["nic"])
                print(f"S02_WAN_RETIRADA={v['id']} lado={logical}")
                break
        for logical, temp in (("R-HQ", v["temporary_hq"]), (v["branch"], v["temporary_branch"])):
            if ns(current, logical, "ip", "link", "show", "dev", temp, allow_failure=True):
                ns(current, logical, "ip", "link", "delete", "dev", temp)
                print(f"S02_WAN_TEMP_NAMESPACE_RETIRADO={logical}/{temp}")
        for temp in (v["temporary_hq"], v["temporary_branch"]):
            if execute("ip", "link", "show", "dev", temp, allow_failure=True):
                privilege("ip", "link", "delete", "dev", temp)
                print(f"S02_WAN_TEMP_HOST_RETIRADO={temp}")
    for logical, loop in (("R-HQ", "10.79.0.1/32"), ("R-S1", "10.79.0.2/32"), ("R-S2", "10.79.0.3/32")):
        if loop in ns(current, logical, "ip", "-4", "-o", "addr", "show", "dev", "lo"):
            ns(current, logical, "ip", "addr", "del", loop, "dev", "lo")
            print(f"S02_LOOPBACK_RETIRADA={logical}:{loop}")
    after = host_before()
    if (after["ens33"] != state["host"]["ens33"]
            or after["routes"] != state["host"]["routes"]):
        raise RuntimeError("Red del host distinta de la registrada; conservar state")
    STATE.unlink()
    print("S02_HOST_POSTCHECK=OK")
    print("S02_WAN_DOWN=OK")


def up(records: list[dict], current: dict) -> None:
    host = precheck(records, current)
    BASE.mkdir(parents=True, exist_ok=True)
    value = {
        "owner": OWNER, "created": datetime.now().isoformat(),
        "ids": {k: v["id"] for k, v in current.items()}, "host": host
    }
    with STATE.open("x", encoding="utf-8") as fh:
        json.dump(value, fh, indent=2)
    try:
        for logical, loop in (("R-HQ", "10.79.0.1/32"), ("R-S1", "10.79.0.2/32"), ("R-S2", "10.79.0.3/32")):
            ns(current, logical, "ip", "link", "set", "lo", "up")
            ns(current, logical, "ip", "addr", "add", loop, "dev", "lo")
            print(f"S02_LOOPBACK_CREADA={logical}:{loop}")
        for v in records:
            h = v["temporary_hq"]
            b = v["temporary_branch"]
            branch = v["branch"]
            nic = v["nic"]
            privilege("ip", "link", "add", h, "type", "veth", "peer", "name", b)
            privilege("ip", "link", "set", h, "netns", current["R-HQ"]["pid"])
            privilege("ip", "link", "set", b, "netns", current[branch]["pid"])
            ns(current, "R-HQ", "ip", "link", "set", h, "name", nic)
            ns(current, branch, "ip", "link", "set", b, "name", nic)
            ns(current, "R-HQ", "ip", "addr", "add", v["hq_ip"], "dev", nic)
            ns(current, branch, "ip", "addr", "add", v["branch_ip"], "dev", nic)
            ns(current, "R-HQ", "ip", "link", "set", nic, "up")
            ns(current, branch, "ip", "link", "set", nic, "up")
            print(f"S02_WAN_CREADA={v['id']} IF={nic}")
        for logical in ROUTERS:
            ns(current, logical, "ip", "link", "set", "lo", "up")
            output = privilege("docker", "exec", current[logical]["name"],
                               "vtysh", "-b")
            if any(s in output.lower() for s in ("processing failure", "invalid input", "unknown command")):
                raise RuntimeError(f"FRR rechazo configuracion en {logical}: {output}")
            print(f"S02_FRR_REAPLICADA={logical}")
        print("S02_WAN_LINKS_UP=4")
        if host_before() != host:
            raise RuntimeError("El host cambio durante el despliegue WAN")
        print("S02_HOST_GESTION_INTACTO=SI")
        print("S02_WAN_UP=OK")
    except BaseException:
        print("S02_UP_NO_COMPLETADO: ROLLBACK EXCLUSIVO WAN", file=sys.stderr)
        try:
            cleanup(records, containers())
        except Exception as err:
            print(f"S02_ROLLBACK_ERROR={err}; estado conservado", file=sys.stderr)
        raise


def status(records: list[dict], current: dict) -> None:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("WAN S02 no tiene state propio: todavia no desplegada")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    verify_ownership(state, current)
    for logical in ROUTERS:
        print(f"========== {logical} ==========")
        print(ns(current, logical, "ip", "-4", "-br", "addr").strip())
        print(privilege("docker", "exec", current[logical]["name"],
                        "vtysh", "-c", "show ip ospf neighbor").strip())
    if host_before() != state["host"]:
        raise RuntimeError("Host red cambiado")
    print("S02_HOST_GESTION_INTACTO=SI")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "precheck", "up", "status", "down"])
    args = parser.parse_args()
    records = plan()
    if args.action == "plan":
        print("S02_SIN_CAMBIOS=SI")
        return
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal; sudo -v previamente")
    current = containers()
    if args.action == "precheck":
        precheck(records, current)
    elif args.action == "up":
        up(records, current)
    elif args.action == "status":
        status(records, current)
    else:
        cleanup(records, current)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"S02_WAN_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
