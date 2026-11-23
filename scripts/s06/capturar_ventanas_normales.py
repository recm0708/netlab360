#!/usr/bin/env python3
"""S06-041: captura ventanas observacionales NORMAL de egress HQ.

Registra ground truth de la CONDICION DE EGRESO (sin netem/control de
tráfico, NOC saludable), respaldado por comprobaciones independientes
ANTES y DESPUES de cada muestra. No demuestra ausencia de todo fallo
posible en NETLAB360, ni introduce fallas o modifica la red.
Los RTT/packet-loss NO se usan para asignar la etiqueta.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from medir_rendimiento import measure_ping
from precheck_escenarios import (
    NS, DEVICE, CLIENT_IP, CLIENT_PREFIX, CLIENT_GW,
    classify_qdisc, inspect as precheck, read_json
)

ROOT = Path.home() / "netlab360-bootstrap/s06/datasets"
SCHEMA = "NETLAB360_S06_WINDOWED_EGRESS_NORMAL_V1"
PROBES = (
    ("HQ_A_S1", NS, "10.71.20.20"),
    ("HQ_A_S2", NS, "10.72.20.20"),
)
SERVICES = (
    "netlab360-s04-exporter", "netlab360-s04-prometheus", "netlab360-s05-noc",
    "netlab360-s05-ha-backend-hq", "netlab360-s05-ha-backend-s1",
    "netlab360-s05-ha-frontal-hq", "netlab360-s05-ha-monitor-s2",
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def command(args: tuple[str, ...]) -> str:
    output = subprocess.run(args, check=False, capture_output=True,
                            timeout=12, text=True)
    if output.returncode:
        raise RuntimeError("readonly_command_failed_" + str(args[:4]))
    return output.stdout


def route_check(result: object, target: str) -> bool:
    if not isinstance(result, list) or len(result) != 1:
        return False
    info = result[0]
    return (
        info.get("dst") == target
        and info.get("dev") == DEVICE
        and info.get("prefsrc", info.get("src")) == CLIENT_IP
        and info.get("gateway") == CLIENT_GW
    )


def evidence_snapshot() -> dict:
    """Ground truth por estado de red y control, independiente del RTT."""
    checked = utc()
    raw = json.loads(command((
        "sudo", "-n", "ip", "netns", "exec", NS,
        "tc", "-j", "qdisc", "show", "dev", DEVICE,
    )))
    qdisc = classify_qdisc(raw)
    routes = {}
    for name, _, target in PROBES:
        routes[name] = route_check(json.loads(command((
            "sudo", "-n", "ip", "-n", NS, "-j", "-4",
            "route", "get", target
        ))), target)

    services = {}
    for name in SERVICES:
        services[name] = command(("systemctl", "is-active", name)).strip()
    graph = read_json("http://127.0.0.1:9130/api/v1/graph")
    health = read_json("http://127.0.0.1:9130/healthz")
    graph_ok = (
        health.get("healthy") is True
        and graph.get("routing", {}).get("available") is True
        and graph.get("ha_service", {}).get("status") == "running"
        and graph.get("ha_service", {}).get("active_backend") == "BACKEND_HQ"
        and graph.get("lacp", {}).get("available") is True
        and graph.get("sdn", {}).get("status") == "connected"
        and not graph.get("source_warnings")
        and len(graph.get("nodes", [])) == 18
        and len(graph.get("links", [])) == 21
    )
    return {
        "checked_at_utc": checked,
        "qdisc_state": qdisc["state"],
        "routes_ok": routes,
        "services": services,
        "noc_healthy": graph_ok,
        "snapshot_valid": (
            qdisc["state"] == "CANDIDATE_NOQUEUE"
            and all(routes.values())
            and all(v == "active" for v in services.values())
            and graph_ok
        ),
        "observed_root_kinds": qdisc["root_kinds"],
    }


def classify_window(before: dict, after: dict, measurements: list[dict]) -> dict:
    """Etiqueta solo si la red está intacta en ambos extremos del intervalo."""
    valid = (
        before.get("snapshot_valid") is True
        and after.get("snapshot_valid") is True
        and before.get("qdisc_state") == "CANDIDATE_NOQUEUE"
        and after.get("qdisc_state") == "CANDIDATE_NOQUEUE"
        and len(measurements) == len(PROBES)
        and {m.get("probe_id") for m in measurements} ==
        {p[0] for p in PROBES}
        and all(m.get("result", {}).get("measurement_valid") is True
                for m in measurements)
    )
    # El resultado de RTT y la pérdida no determinan la clase operacional.
    return {
        "ground_truth_label": "NORMAL" if valid else "UNKNOWN",
        "ground_truth_verified": valid,
        "label_scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
        "label_evidence": (
            "independent_qdisc_routes_services_noc_before_after"
            if valid else "insufficient_independent_evidence"
        ),
    }


def health_failures(samples: list[dict]) -> list[str]:
    bad = []
    for i, x in enumerate(samples, start=1):
        if not x.get("ground_truth_verified", False):
            bad.append(f"window_{i}_unverified")
    return bad


def capture(rounds: int, packets: int, pause: float) -> tuple[dict, list[dict]]:
    if not 2 <= rounds <= 80:
        raise ValueError("rounds debe estar entre 2 y 80")
    if not 2 <= packets <= 6:
        raise ValueError("packets debe estar entre 2 y 6")
    if not 0 <= pause <= 5:
        raise ValueError("pause fuera de 0..5")
    if os.geteuid() == 0:
        raise RuntimeError("No ejecutar todo el recolector como root")
    pre = precheck()
    if pre["qdisc"]["state"] != "CANDIDATE_NOQUEUE":
        raise RuntimeError("Qdisc inicial noqueue no verificada")
    if pre["target"]["namespace"] != NS or pre["target"]["interface"] != DEVICE:
        raise RuntimeError("Target diferente del candidato HQ")
    if pre["target"]["ipv4"] != f"{CLIENT_IP}/{CLIENT_PREFIX}":
        raise RuntimeError("IP cliente no coincide")
    if pre["target"]["gateway"] != CLIENT_GW:
        raise RuntimeError("Gateway cliente no coincide")
    if pre["namespace_count"] != 21:
        raise RuntimeError("Inventario de 21 namespaces no verificado")

    identifier = ("S06_WINDOW_NORMAL_" +
                  datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                  + "_" + secrets.token_hex(3))
    path = ROOT / "raw" / identifier
    path.mkdir(parents=True, exist_ok=False, mode=0o700)
    records_file = path / "ventanas.jsonl"
    meta_file = path / "metadata.json"
    meta = {
        "schema": SCHEMA, "session_id": identifier,
        "start_utc": utc(), "status": "capturing", "rounds": rounds,
        "packet_count_per_probe": packets,
        "source": "NETLAB360_REAL_HQ_TO_S1_S2",
        "stimulus": "NONE", "mutating_action_executed": False,
        "label_scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
        "ground_truth_policy": "verified_qdisc_routes_services_noc_at_both_boundaries",
        "training_ready": False, "target": f"{NS}/{DEVICE}",
        "management_interface": "ens33",
        "sample_outcomes": [],
    }
    meta_file.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    observations = []
    try:
        with records_file.open("x", encoding="utf-8") as stream:
            for n in range(1, rounds + 1):
                before = evidence_snapshot()
                measurements = [measure_ping(x, packets) for x in PROBES]
                after = evidence_snapshot()
                classification = classify_window(before, after, measurements)
                record = {
                    "schema": SCHEMA, "session_id": identifier,
                    "window_index": n, "recorded_at_utc": utc(),
                    "before": before, "after": after,
                    "measurements": measurements, **classification,
                    "qdisc_intervention_executed": False,
                }
                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                stream.flush()
                observations.append(record)
                print(f"S06_041_VENTANA={n}/{rounds} "
                      f"ETIQUETA={classification['ground_truth_label']} "
                      f"VERIFICADA={classification['ground_truth_verified']}",
                      flush=True)
                if n < rounds and pause:
                    time.sleep(pause)
    finally:
        meta["finished_at_utc"] = utc()
        meta["samples_recorded"] = len(observations)
        meta["verified"] = sum(bool(r["ground_truth_verified"])
                               for r in observations)
        meta["status"] = (
            "complete" if len(observations) == rounds
            and meta["verified"] == rounds else "partial_quality"
        )
        if records_file.exists():
            meta["data_digest_sha256"] = hashlib.sha256(
                records_file.read_bytes()
            ).hexdigest()
        meta["sample_outcomes"] = health_failures(observations)
        meta_file.write_text(json.dumps(meta, indent=2) + "\n",
                             encoding="utf-8")
    return {"path": str(path), "meta": meta}, observations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=20)
    parser.add_argument("--packets", type=int, default=3)
    parser.add_argument("--pause", type=float, default=0)
    args = parser.parse_args()
    os.umask(0o077)
    output, rows = capture(args.rounds, args.packets, args.pause)
    meta = output["meta"]
    print("S06_041_SESION=" + meta["session_id"])
    print("S06_041_DIRECTORIO=" + output["path"])
    print(f"S06_041_VENTANAS={meta['samples_recorded']}")
    print(f"S06_041_NORMAL_VERIFICADAS={meta['verified']}")
    print("S06_041_CAMBIOS_RED=NINGUNO")
    if meta["status"] != "complete":
        raise RuntimeError("Calidad parcial, no declarar ground truth universal")
    print("S06_041_CAPTURA_NORMAL=OK_VERIFICADA_SCOPED")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print("S06_041_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
