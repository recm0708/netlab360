#!/usr/bin/env python3
"""NETLAB360 S05: solo red de servicios HA (3 netns nuevos, 3 puertos L2).
NO inicia servidores HTTP, no instala nada, no modifica rutas del host ni FRR.
Acciones: plan, precheck, up --confirm-isolated, status, down --confirm-isolated.
Mantiene estado ownership local bajo ~/netlab360-bootstrap/s05/ha/state.json.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BASE = Path.home() / "netlab360-bootstrap/s05/ha"
STATE = BASE / "state.json"
PRECHECK = ROOT / "scripts/validacion/s05-ha-precheck.py"
OWNER = "NETLAB360_S05_HA_RED_V1"

# Exclusivos de S05, distintos de tr-sw, a120, a220 y de interfaces WAN.
ROWS = [
    {"role": "BACKEND_HQ", "site": "HQ", "sw": "nl360-s02-sw-hq",
     "ns": "nl360-s05-ha-hq", "port": "ha-hq21", "peer": "p-hq21",
     "vid": 120, "addr": "10.70.20.21/24", "gw": "10.70.20.1"},
    {"role": "BACKEND_S1", "site": "S1", "sw": "nl360-s02-sw-s1",
     "ns": "nl360-s05-ha-s1", "port": "ha-s121", "peer": "p-s121",
     "vid": 220, "addr": "10.71.20.21/24", "gw": "10.71.20.1"},
    {"role": "FRONTAL_HQ", "site": "HQ", "sw": "nl360-s02-sw-hq",
     "ns": "nl360-s05-ha-fe", "port": "ha-hq23", "peer": "p-hq23",
     "vid": 120, "addr": "10.70.20.23/24", "gw": "10.70.20.1"},
]

def cmd(*argv: str, root: bool = False, check: bool = True, timeout: int = 25) -> str:
    full = (["sudo", "-n"] if root else []) + list(argv)
    p = subprocess.run(full, text=True, capture_output=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError(
            "Fallo de comando solo en contexto S05: "
            + " ".join(argv) + " / " + (p.stderr or p.stdout)[-700:]
        )
    return p.stdout if not (p.returncode and not check) else ""


def ns_list() -> set[str]:
    return {
        line.split()[0] for line in cmd("ip", "netns", "list", root=True).splitlines()
        if line.strip()
    }


def mgmt() -> dict:
    addr = cmd("ip", "-4", "-o", "address", "show", "dev", "ens33")
    routes = cmd("ip", "-4", "route", "show", "table", "main")
    if "192.168.47.40/24" not in addr:
        raise RuntimeError("IP ens33 distinta de la línea base")
    if "default via 192.168.47.2 dev ens33" not in routes:
        raise RuntimeError("Gateway de gestión distinto de la línea base")
    return {"ens33": addr, "routes": routes}


def check_identity() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario normal; sudo -v antes")
    if cmd("hostname").strip() != "netlab360-lab":
        raise RuntimeError("Hostname diferente a netlab360-lab")
    if cmd("git", "-C", str(ROOT), "status", "--porcelain").strip():
        raise RuntimeError("Git con cambios locales pendientes")
    mgmt()


def confirm_precheck() -> None:
    output = cmd(sys.executable, str(PRECHECK), "--check", timeout=90)
    print(output, end="", flush=True)
    if "S05_HA_PRECHECK=OK_DISENO_PENDIENTE" not in output:
        raise RuntimeError("Precheck integral HA no aprobado")


def plan() -> None:
    print("========== S05 HA RED PROPUESTA ==========")
    for row in ROWS:
        print(
            f"S05_HA_PLAN={row['role']} SEDE={row['site']} "
            f"NS={row['ns']} SW={row['sw']} PUERTO={row['port']} "
            f"VLAN={row['vid']} IP={row['addr']} GW={row['gw']}"
        )
    print("S05_HA_PLAN_NS=3_PUERTOS=3")
    print("S05_HA_PLAN_FRR=NO_CAMBIOS")
    print("S05_HA_PLAN_HOST=NO_RUTAS_NI_ENS33")


def precheck() -> None:
    check_identity()
    if STATE.exists() or STATE.is_symlink():
        raise RuntimeError("Ya hay estado HA S05; usar status/down, no up")
    confirm_precheck()
    existing = ns_list()
    for row in ROWS:
        if row["ns"] in existing:
            raise RuntimeError("Namespace ya presente: " + row["ns"])
        if cmd("ip", "-n", row["sw"], "link", "show", "dev", row["port"],
               root=True, check=False):
            raise RuntimeError("Puerto ya presente: " + row["port"])
        if cmd("ip", "-n", row["sw"], "link", "show", "dev", row["peer"],
               root=True, check=False):
            raise RuntimeError("Interfaz temporal ya presente: " + row["peer"])
    print("S05_HA_PRECHECK_PUERTOS_Y_NETNS=LIBRES")
    print("S05_HA_RED_PRECHECK=OK_SIN_CAMBIOS")


def write_state(data: dict) -> None:
    BASE.mkdir(parents=True, exist_ok=True, mode=0o700)
    temp = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=BASE, encoding="utf-8",
                                         delete=False) as fh:
            temp = Path(fh.name)
            json.dump(data, fh, ensure_ascii=False, indent=2)
        os.chmod(temp, 0o600)
        os.replace(temp, STATE)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def read_state() -> dict:
    if not STATE.is_file() or STATE.is_symlink():
        raise RuntimeError("Estado HA S05 ausente o enlace simbólico")
    data = json.loads(STATE.read_text(encoding="utf-8"))
    if (data.get("owner") != OWNER
            or data.get("roles") != [r["role"] for r in ROWS]
            or data.get("namespaces") != [r["ns"] for r in ROWS]
            or data.get("ports") != [r["port"] for r in ROWS]):
        raise RuntimeError("Estado S05 inválido: detener modificaciones")
    return data


def attach(row: dict) -> None:
    sw, ns, port, peer = row["sw"], row["ns"], row["port"], row["peer"]
    vid = str(row["vid"])
    cmd("ip", "netns", "add", ns, root=True)
    cmd("ip", "-n", ns, "link", "set", "lo", "up", root=True)
    cmd("ip", "-n", sw, "link", "add", port, "type", "veth",
        "peer", "name", peer, root=True)
    cmd("ip", "-n", sw, "link", "set", peer, "netns", ns, root=True)
    cmd("ip", "-n", ns, "link", "set", peer, "name", "eth0", root=True)
    cmd("ip", "-n", sw, "link", "set", port, "master", "br0", root=True)
    # Reproduce el modo acceso untagged de S02; solo el puerto nuevo.
    cmd("ip", "netns", "exec", sw, "bridge", "vlan", "del",
        "dev", port, "vid", "1", root=True)
    cmd("ip", "netns", "exec", sw, "bridge", "vlan", "add",
        "dev", port, "vid", vid, "pvid", "untagged", root=True)
    cmd("ip", "-n", sw, "link", "set", port, "up", root=True)
    cmd("ip", "-n", ns, "address", "add", row["addr"], "dev", "eth0", root=True)
    cmd("ip", "-n", ns, "link", "set", "eth0", "up", root=True)
    cmd("ip", "-n", ns, "route", "add", "default", "via", row["gw"],
        "dev", "eth0", root=True)
    print(f"S05_HA_RED_CREADA={row['role']} IP={row['addr']} "
          f"SW={sw} VLAN={vid}", flush=True)


def network_status(validate_ping: bool) -> None:
    known = ns_list()
    for row in ROWS:
        ns, sw, port = row["ns"], row["sw"], row["port"]
        if ns not in known:
            raise RuntimeError("Namespace HA ausente: " + ns)
        addr = cmd("ip", "-n", ns, "-4", "-br", "address", "show", "dev",
                   "eth0", root=True)
        if row["addr"] not in addr or "UP" not in addr:
            raise RuntimeError("Dirección/interfaz HA inválida: " + ns)
        route = cmd("ip", "-n", ns, "-4", "route", "show", "default", root=True)
        if f"default via {row['gw']}" not in route:
            raise RuntimeError("Gateway HA incorrecto: " + ns)
        vlans = cmd("ip", "netns", "exec", sw, "bridge", "vlan",
                    "show", "dev", port, root=True)
        if not re.search(rf"(?<!\d){row['vid']}(?!\d).*PVID", vlans, re.S):
            raise RuntimeError("Puerto VLAN HA no conforme: " + port)
        if validate_ping:
            cmd("ip", "netns", "exec", ns, "ping", "-n", "-c", "2",
                "-W", "2", row["gw"], root=True, timeout=9)
        print(f"S05_HA_RED_ESTADO_{row['role']}=OK IP={row['addr']} "
              f"VLAN={row['vid']}", flush=True)
    if validate_ping:
        for role in ("BACKEND_HQ", "BACKEND_S1", "FRONTAL_HQ"):
            row = next(x for x in ROWS if x["role"] == role)
            cmd("ip", "netns", "exec", "nl360-s02-h-s2-320",
                "ping", "-n", "-c", "2", "-W", "2",
                row["addr"].split("/")[0], root=True, timeout=9)
            print(f"S05_HA_S2_ALCANZA_{role}=OK", flush=True)
    mgmt()
    print("S05_HA_GESTION_INTACTA=SI")


def cleanup(verified: dict) -> None:
    if verified.get("status") not in ("creating", "active", "cleanup_pending"):
        raise RuntimeError("Estado HA no permite limpieza automática")
    known = ns_list()
    # Nunca borrar namespaces con procesos activos; detener servicio HA antes.
    for row in ROWS:
        if row["ns"] in known:
            pids = cmd("ip", "netns", "pids", row["ns"], root=True).strip()
            if pids:
                raise RuntimeError(
                    f"Namespace {row['ns']} tiene procesos {pids}: "
                    "detener SOLO procesos S05 antes de down"
                )
    for row in reversed(ROWS):
        sw, port = row["sw"], row["port"]
        cmd("ip", "-n", sw, "link", "delete", "dev", port,
            root=True, check=False)
        if row["ns"] in known:
            cmd("ip", "netns", "delete", row["ns"], root=True)
            print(f"S05_HA_RED_RETIRADA={row['role']}", flush=True)
    if any(r["ns"] in ns_list() for r in ROWS):
        raise RuntimeError("Persisten namespaces S05 tras limpieza")
    mgmt()
    STATE.unlink()
    print("S05_HA_RED_DOWN=OK")
    print("S05_HA_GESTION_INTACTA=SI")


def up() -> None:
    precheck()
    before = mgmt()
    data = {
        "owner": OWNER, "status": "creating",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "roles": [r["role"] for r in ROWS],
        "namespaces": [r["ns"] for r in ROWS],
        "ports": [r["port"] for r in ROWS],
        "management_before": before,
    }
    write_state(data)
    try:
        for row in ROWS:
            attach(row)
        network_status(validate_ping=True)
        if mgmt() != before:
            raise RuntimeError("Host fue modificado; abortar y retirar solo S05")
        data["status"] = "active"
        write_state(data)
        print("S05_HA_RED_UP=OK")
        print("S05_HA_S02_CONSERVADO=SI")
        print("S05_HA_SERVIDORES_HTTP=NO_INICIADOS")
    except BaseException:
        print("S05_HA_RED_UP=ERROR; retirando solo recursos S05", file=sys.stderr)
        try:
            cleanup(read_state())
        except Exception as exc:
            data["status"] = "cleanup_pending"
            write_state(data)
            print("S05_HA_CLEANUP_REQUIERE_REVISION=" + str(exc),
                  file=sys.stderr)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", "precheck", "up", "status", "down"])
    parser.add_argument("--confirm-isolated", action="store_true")
    args = parser.parse_args()
    if args.action in ("up", "down") and not args.confirm_isolated:
        parser.error("up/down requieren --confirm-isolated")
    if args.action not in ("up", "down") and args.confirm_isolated:
        parser.error("--confirm-isolated solo con up/down")
    if args.action == "plan":
        plan()
        return
    check_identity()
    if args.action == "precheck":
        precheck()
    elif args.action == "up":
        up()
    elif args.action == "status":
        state = read_state()
        if state["status"] != "active":
            raise RuntimeError(f"Estado HA no activo: {state['status']}")
        network_status(validate_ping=True)
        print("S05_HA_RED_STATUS=OK")
    elif args.action == "down":
        cleanup(read_state())


if __name__ == "__main__":
    try:
        main()
    except BaseException as e:
        print(f"S05_HA_RED_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(2)
