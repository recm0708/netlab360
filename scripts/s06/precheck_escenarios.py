#!/usr/bin/env python3
"""S06-035: descubrir de forma no invasiva la viabilidad de netem en un cliente.

No añade ni elimina qdiscs, rutas, interfaces, contenedores o servicios.
Solo inspecciona la VM, el origen de datos S06 y guarda un plan privado.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
BASE = Path.home() / "netlab360-bootstrap"
NS = "nl360-s02-h-hq-120"
DEVICE = "eth0"
CLIENT_IP = "10.70.20.20"
CLIENT_PREFIX = 24
CLIENT_GW = "10.70.20.1"
MANAGEMENT_IP = "192.168.47.40/24"
MANAGEMENT_GW = "192.168.47.2"
CURATED_ID = "S06_QA_20261123T045339Z_4658bf"
SCHEMA = "NETLAB360_S06_EXPERIMENT_PREFLIGHT_V1"
READ_ONLY_COMMANDS = [
    ["ip", "-4", "-o", "addr", "show", "dev", "ens33"],
    ["ip", "-4", "route", "show", "default"],
    ["sudo", "-n", "ip", "netns", "list"],
    ["sudo", "-n", "ip", "-n", NS, "-j", "addr", "show", "dev", DEVICE],
    ["sudo", "-n", "ip", "-n", NS, "-j", "route", "show", "default"],
    ["sudo", "-n", "ip", "netns", "exec", NS, "tc", "-j", "qdisc", "show", "dev", DEVICE],
]


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run(args: list[str], *, timeout: float = 10) -> str:
    p = subprocess.run(args, capture_output=True, text=True,
                       timeout=timeout, check=False)
    if p.returncode != 0:
        raise RuntimeError(f"Consulta fallida: {args[0]} (rc={p.returncode})")
    return p.stdout


def read_json(address: str) -> dict:
    if address not in (
        "http://127.0.0.1:9110/api/v1/state",
        "http://127.0.0.1:9130/api/v1/graph",
        "http://127.0.0.1:9130/healthz",
    ):
        raise ValueError("URL no permitida")
    with urlopen(address, timeout=8) as resp:
        result = json.load(resp)
    if not isinstance(result, dict):
        raise ValueError("Respuesta API invalida")
    return result


def check_management(ip: str, route: str) -> None:
    if MANAGEMENT_IP not in ip:
        raise RuntimeError("IP ens33 fuera de referencia")
    if f"default via {MANAGEMENT_GW} dev ens33" not in route:
        raise RuntimeError("Ruta de gestion distinta")
    if "10.70." in route or "10.71." in route or "10.72." in route:
        raise RuntimeError("Rutas experimentales fuera del namespace detectadas")


def check_address(items: object) -> None:
    if not isinstance(items, list) or len(items) != 1:
        raise RuntimeError("Interfaz experimental no univoca")
    nic = items[0]
    if nic.get("ifname") != DEVICE or nic.get("operstate") != "UP":
        raise RuntimeError("Interfaz experimental ausente o down")
    ips = [
        value for value in nic.get("addr_info", [])
        if value.get("family") == "inet"
    ]
    if len(ips) != 1:
        raise RuntimeError("IPv4 experimental ambigua")
    addr = ips[0]
    if (addr.get("local") != CLIENT_IP
            or addr.get("prefixlen") != CLIENT_PREFIX):
        raise RuntimeError("IPv4 del cliente fuera del IPAM")


def check_default(routes: object) -> None:
    if not isinstance(routes, list) or len(routes) != 1:
        raise RuntimeError("Ruta default experimental ambigua")
    r = routes[0]
    if (r.get("dst") != "default"
            or r.get("gateway") != CLIENT_GW
            or r.get("dev") != DEVICE):
        raise RuntimeError("Gateway o dispositivo experimental inesperado")


def classify_qdisc(raw: object) -> dict:
    if not isinstance(raw, list):
        raise ValueError("qdisc JSON sin lista")
    root = [
        v for v in raw if isinstance(v, dict)
        and (v.get("root") is True or v.get("parent") == "root")
    ]
    if not root:
        # iproute2 suele representar 'noqueue' como root via el campo parent.
        root = [
            v for v in raw if isinstance(v, dict)
            and v.get("kind") == "noqueue"
        ]
    kinds = sorted({str(v.get("kind")) for v in root})
    existing_netem = any(v.get("kind") == "netem" for v in raw if isinstance(v, dict))
    if existing_netem:
        state = "BLOCKED_EXISTING_NETEM"
    elif len(root) == 1 and root[0].get("kind") == "noqueue":
        state = "CANDIDATE_NOQUEUE"
    else:
        state = "REVIEW_QDISC_BEFORE_CHANGE"
    return {
        "state": state,
        "root_kinds": kinds,
        "qdiscs": raw,
        "mutating_action_executed": False,
    }


def validate_curated() -> dict:
    target = BASE / "s06/datasets/curated" / CURATED_ID
    meta = target / "reporte_calidad.json"
    if target.is_symlink() or not meta.is_file() or meta.is_symlink():
        raise RuntimeError("Dataset de referencia S06-034 no disponible")
    obj = json.loads(meta.read_text(encoding="utf-8"))
    if (obj.get("schema") != "NETLAB360_S06_CURATED_V1"
            or obj.get("ground_truth_labels_available") != 0
            or obj.get("training_ready") is not False
            or obj.get("record_counts", {}).get("normalized_rows") != 375):
        raise RuntimeError("Informe de referencia S06-034 no corresponde")
    return {
        "dataset": CURATED_ID,
        "rows": 375,
        "ground_truth_verified": False,
    }


def inspect() -> dict:
    if os.geteuid() == 0:
        raise RuntimeError("No ejecutar el programa completo como root")
    p = run(["git", "-C", str(ROOT), "status", "--porcelain"])
    if p.strip():
        raise RuntimeError("Git tiene cambios locales")
    mgmt_ip = run(READ_ONLY_COMMANDS[0])
    mgmt_route = run(READ_ONLY_COMMANDS[1])
    check_management(mgmt_ip, mgmt_route)
    names = {
        s.split()[0] for s in run(READ_ONLY_COMMANDS[2]).splitlines() if s.strip()
    }
    if len(names) != 21 or NS not in names:
        raise RuntimeError("Namespaces inesperados o cliente ausente")
    nic = json.loads(run(READ_ONLY_COMMANDS[3]))
    routes = json.loads(run(READ_ONLY_COMMANDS[4]))
    check_address(nic)
    check_default(routes)
    qdisc = classify_qdisc(json.loads(run(READ_ONLY_COMMANDS[5])))

    exporter = read_json("http://127.0.0.1:9110/api/v1/state")
    graph = read_json("http://127.0.0.1:9130/api/v1/graph")
    health = read_json("http://127.0.0.1:9130/healthz")
    if (exporter.get("source_ok") is not True
            or health.get("healthy") is not True
            or graph.get("source_warnings")
            or graph.get("routing", {}).get("available") is not True
            or graph.get("ha_service", {}).get("active_backend") != "BACKEND_HQ"
            or len(graph.get("nodes", [])) != 18
            or len(graph.get("links", [])) != 21):
        raise RuntimeError("S04/S05 fuera de referencia operativa")

    data = validate_curated()
    return {
        "schema": SCHEMA,
        "checked_at_utc": timestamp(),
        "scenario_id": "S06_ISOLATED_CLIENT_LATENCY_CANDIDATE",
        "target": {"namespace": NS, "interface": DEVICE,
                   "ipv4": f"{CLIENT_IP}/{CLIENT_PREFIX}",
                   "gateway": CLIENT_GW,
                   "candidate_only": True},
        "management_protected": True,
        "namespace_count": len(names),
        "noc": {"nodes": 18, "links": 21, "ha_backend": "BACKEND_HQ"},
        "dataset": data,
        "qdisc": qdisc,
        "planned_phases": [
            "baseline_without_intervention",
            "verify_stimulus_active",
            "measure_while_intervention_active",
            "rollback_with_independent_watchdog",
            "verify_restored_network_and_measure",
        ],
        "ground_truth_policy": {
            "baseline": "UNKNOWN until separate precheck validates a normal session",
            "degraded": "UNKNOWN until applied netem and resulting metrics are independently verified",
            "recovery": "UNKNOWN until qdisc removed and return tests pass",
            "fault": "not authorized in S06-035",
        },
        "actions_executed": "READ_ONLY",
        "next_gate": "Review qdisc, watchdog privileges, lifecycle and rollback before experiments",
    }


def save(report: dict) -> Path:
    ident = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + secrets.token_hex(3)
    folder = BASE / "s06/planes" / ("S06_035_" + ident)
    folder.mkdir(parents=True, mode=0o700, exist_ok=False)
    path = folder / "precheck_escenarios.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-plan", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    report = inspect()
    print("S06_035_PRECHECK=OK_SOLO_LECTURA")
    print("S06_035_CLIENTE=" + NS)
    print("S06_035_INTERFAZ=" + DEVICE)
    print("S06_035_QDISC_ESTADO=" + report["qdisc"]["state"])
    print("S06_035_QDISC_ROOT=" + ",".join(report["qdisc"]["root_kinds"]))
    print("S06_035_TOPOLOGIA=21_NS_18_NODOS_21_ENLACES")
    print("S06_035_GROUND_TRUTH=UNKNOWN")
    print("S06_035_CAMBIOS_DE_RED=NINGUNO")
    if args.save_plan:
        print("S06_035_PLAN_JSON=" + str(save(report)))
    print("S06_035_PLANIFICACION=LISTA_PARA_REVISION_NO_EJECUTAR_NETEM")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"S06_035_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
