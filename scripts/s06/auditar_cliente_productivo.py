#!/usr/bin/env python3
"""S06-039: auditoría preventiva del cliente HQ sin intervención.

Solo lecturas de ip/tc/systemctl/API local y escrituras opcionales de
reporte privado. NO habilita operaciones de netem sobre el cliente real.
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

from precheck_escenarios import (  # Reusar invariantes S06-035 validadas en VM.
    BASE, NS, DEVICE, CLIENT_IP, CLIENT_GW, classify_qdisc,
    inspect as inspect_035, read_json,
)

SCHEMA = "NETLAB360_S06_PRODUCTION_READONLY_PREFLIGHT_V1"
PROBES = {"HQ_A_S1": "10.71.20.20", "HQ_A_S2": "10.72.20.20"}
SERVICES = (
    "netlab360-s04-exporter", "netlab360-s04-prometheus", "netlab360-s05-noc",
    "netlab360-s05-ha-backend-hq", "netlab360-s05-ha-backend-s1",
    "netlab360-s05-ha-frontal-hq", "netlab360-s05-ha-monitor-s2",
)
ISOLATED_NS = "nl360-s06-isotest"
ISOLATED_STATE = "/run/netlab360-s06-isotest/state.json"
# Catálogo cerrado: estos argv nunca incluyen qdisc add/change/replace/del.
ROUTE_COMMANDS = {
    name: ["sudo", "-n", "ip", "-n", NS, "-j", "-4", "route", "get", destination]
    for name, destination in PROBES.items()
}
LINK_CMD = ["sudo", "-n", "ip", "-n", NS, "-j", "-d", "link", "show", "dev", DEVICE]
QDISC_CMD = ["sudo", "-n", "ip", "netns", "exec", NS,
             "tc", "-j", "qdisc", "show", "dev", DEVICE]
NS_CMD = ["sudo", "-n", "ip", "netns", "list"]
STATE_ABSENT_CMD = ["sudo", "-n", "test", "!", "-e", ISOLATED_STATE]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def command(argv: list[str]) -> str:
    p = subprocess.run(argv, capture_output=True, text=True,
                       timeout=12, check=False)
    if p.returncode != 0:
        raise RuntimeError("Consulta no disponible: " + " ".join(argv[:4])
                           + f" rc={p.returncode}")
    return p.stdout


def confirm_route(value: object, target: str) -> dict:
    if not isinstance(value, list) or len(value) != 1:
        raise RuntimeError("Ruta IPAM ambigua")
    row = value[0]
    if row.get("dst") != target:
        raise RuntimeError("El destino de la ruta difiere del catalogo")
    if row.get("dev") != DEVICE or row.get("prefsrc", row.get("src")) != CLIENT_IP:
        raise RuntimeError("La ruta no sale del cliente esperado")
    via = row.get("gateway")
    if via is not None and via != CLIENT_GW:
        raise RuntimeError("Next-hop distinto al gateway IPAM")
    return {
        "destination": target, "interface": DEVICE,
        "source": CLIENT_IP, "gateway_seen": via,
        "route": row,
    }


def confirm_link(value: object) -> dict:
    if not isinstance(value, list) or len(value) != 1:
        raise RuntimeError("Interfaz candidata ausente o no univoca")
    link = value[0]
    if link.get("ifname") != DEVICE or link.get("operstate") != "UP":
        raise RuntimeError("Interfaz candidata inesperada/down")
    kind = link.get("linkinfo", {}).get("info_kind")
    # Clase conocida ayuda a auditar; no se interpreta como permiso de cambio.
    return {
        "ifname": DEVICE,
        "ifindex": link.get("ifindex"),
        "link_index": link.get("link_index"),
        "link_netnsid": link.get("link_netnsid"),
        "link_type": kind or "UNKNOWN_REVIEW",
        "operstate": link.get("operstate"),
        "production_connected": True,
    }


def confirm_qdisc(value: object) -> dict:
    result = classify_qdisc(value)
    if result["state"] != "CANDIDATE_NOQUEUE":
        raise RuntimeError("Qdisc productiva fuera del baseline: " + result["state"])
    return result


def confirm_services(values: dict[str, str]) -> None:
    for service in SERVICES:
        if values.get(service, "").strip() != "active":
            raise RuntimeError("Servicio no saludable: " + service)


def ensure_isolated_cleanup(names: set[str], state_absent: bool) -> None:
    if ISOLATED_NS in names or not state_absent:
        raise RuntimeError("Restos de laboratorio aislado requieren revision")
    if len(names) != 21 or NS not in names:
        raise RuntimeError("Inventario de namespaces fuera de referencia")


def inspect() -> dict:
    if os.geteuid() == 0:
        raise RuntimeError("No ejecutar la auditoria como root")
    base = inspect_035()
    confirm_qdisc(base["qdisc"]["qdiscs"])
    names = {
        line.split()[0] for line in command(NS_CMD).splitlines() if line.strip()
    }
    # sudo test ! -e falla si encuentra estado; no se ignoran errores.
    state_absent = subprocess.run(
        STATE_ABSENT_CMD, check=False, text=True,
        capture_output=True, timeout=12
    ).returncode == 0
    ensure_isolated_cleanup(names, state_absent)
    link = confirm_link(json.loads(command(LINK_CMD)))
    qdisc = confirm_qdisc(json.loads(command(QDISC_CMD)))
    routes = {
        name: confirm_route(json.loads(command(ROUTE_COMMANDS[name])), dst)
        for name, dst in PROBES.items()
    }
    services = {
        name: command(["systemctl", "is-active", name]).strip()
        for name in SERVICES
    }
    confirm_services(services)
    graph = read_json("http://127.0.0.1:9130/api/v1/graph")
    if (graph.get("lacp", {}).get("available") is not True
            or graph.get("sdn", {}).get("status") != "connected"
            or graph.get("ha_service", {}).get("status") != "running"):
        raise RuntimeError("HA/LACP/SDN no saludable")

    return {
        "schema": SCHEMA,
        "checked_at_utc": utc_now(),
        "reference": "S06-038B_ROLLBACK_AISLADO_VALIDADO",
        "read_only": True, "network_changes_executed": False,
        "target": {"namespace": NS, "interface": DEVICE,
                   "ip": CLIENT_IP, "gateway": CLIENT_GW, "link": link,
                   "qdisc": qdisc["state"]},
        "route_get": routes, "services": services,
        "topology": {"namespaces": len(names), "nodes": len(graph["nodes"]),
                     "links": len(graph["links"]),
                     "ha_backend": graph["ha_service"]["active_backend"]},
        "isolated_test_residue": False,
        "baseline_s06_034": base["dataset"],
        "production_change_authorized": False,
        "ground_truth_verified": False,
        "training_ready": False,
        "pending_gates": [
            "root_owned_executor_for_real_client_separately_reviewed",
            "explicit_human_approval_per_experiment",
            "independent_watchdog_real_client_failure_tests",
            "qdisc_ownership_and_recovery_veth_verified",
            "measurement_windows_and_ground_truth_independent_of_predictors",
            "failsafe_postchecks_and_manual_recovery_plan",
        ],
    }


def save(report: dict) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    folder = (BASE / "s06/planes" /
              ("S06_039_" + stamp + "_" + secrets.token_hex(3)))
    folder.mkdir(mode=0o700, parents=True, exist_ok=False)
    target = folder / "auditoria_preintervencion.json"
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    return target


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--save-report", action="store_true")
    args = p.parse_args()
    os.umask(0o077)
    report = inspect()
    print("S06_039_AUDITORIA=OK_SOLO_LECTURA")
    print("S06_039_CLIENTE=" + report["target"]["namespace"])
    print("S06_039_INTERFACE=" + report["target"]["interface"])
    print("S06_039_LINK_TYPE=" + report["target"]["link"]["link_type"])
    print("S06_039_QDISC=" + report["target"]["qdisc"])
    print("S06_039_RUTAS_CONTROLADAS=" + str(len(report["route_get"])))
    print("S06_039_SERVICIOS_ACTIVOS=" + str(len(report["services"])))
    print("S06_039_RESIDUOS_ISOTEST=NINGUNO")
    if args.save_report:
        print("S06_039_REPORTE=" + str(save(report)))
    print("S06_039_CAMBIOS_PRODUCTIVOS=NO")
    print("S06_039_INTERVENCION_AUTORIZADA=NO")
    print("S06_039_READY_FOR_DESIGN_REVIEW=SI")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, TypeError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print("S06_039_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
