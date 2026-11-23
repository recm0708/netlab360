#!/usr/bin/env python3
"""S06-042: observar DEGRADED/RECOVERY en egreso HQ realmente conectado.

Etiquetas exclusivamente por estado del ejecutor privilegiado root-owned,
su qdisc verificada y marcas UTC; RTT/pérdida son features y jamás etiquetas.
No ejecuta comandos de modificación de red ni usa interfaces temporales.
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

SCRIPTS = str(Path(__file__).resolve().parent)
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)

from medir_rendimiento import measure_ping
from precheck_escenarios import NS, DEVICE, CLIENT_GW, CLIENT_IP

EXE = "/usr/local/libexec/netlab360/s06-hq-controlador.py"
ROOT = Path.home() / "netlab360-bootstrap/s06/datasets/raw"
SCHEMA = "NETLAB360_S06_HQ_CONTROLLED_WINDOWS_V1"
SCOPE = "HQ_CLIENT_EGRESS_NETWORK_STATE"
PROBES = (
    ("HQ_A_S1", NS, "10.71.20.20"),
    ("HQ_A_S2", NS, "10.72.20.20")
)


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def command(args: list[str]) -> str:
    p = subprocess.run(args, capture_output=True, text=True,
                       check=False, timeout=12)
    if p.returncode:
        raise RuntimeError("readonly_probe_failed_" + str(args[:5]))
    return p.stdout


def read_guard() -> dict:
    raw = command(["sudo", "-n", EXE, "status"])
    for line in raw.splitlines():
        if line.startswith("S06_042_STATE_JSON="):
            data = json.loads(line.partition("=")[2])
            if data.get("schema") != "NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1":
                raise RuntimeError("unexpected_guard_schema")
            if data.get("target") != f"{NS}/{DEVICE}":
                raise RuntimeError("guard_target_not_HQ")
            return data
    raise RuntimeError("no_guard_state_available")


def route_check() -> dict:
    values = {}
    for ident, _, dst in PROBES:
        result = json.loads(command([
            "sudo", "-n", "ip", "-n", NS, "-j", "-4",
            "route", "get", dst,
        ]))
        values[ident] = (
            isinstance(result, list) and len(result) == 1
            and result[0].get("dst") == dst
            and result[0].get("dev") == DEVICE
            and result[0].get("prefsrc", result[0].get("src")) == CLIENT_IP
            and result[0].get("gateway") == CLIENT_GW
        )
    return values


def snapshot() -> dict:
    state = read_guard()
    routes = route_check()
    return {
        "checked_at_utc": utc(),
        "guard": state,
        "routes_ok": routes,
        "routes_verified": all(routes.values()),
    }


def classify(expected: str, before: dict, after: dict,
             measures: list[dict]) -> dict:
    if expected not in ("DEGRADED", "RECOVERY"):
        raise ValueError("expected_class_not_allowed")
    b, a = before.get("guard", {}), after.get("guard", {})
    common = (
        before.get("routes_verified") is True
        and after.get("routes_verified") is True
        and b.get("token") and b.get("token") == a.get("token")
        and b.get("target") == f"{NS}/{DEVICE}"
        and a.get("target") == f"{NS}/{DEVICE}"
        and b.get("human_approval") is True
        and a.get("human_approval") is True
        and len(measures) == len(PROBES)
        and {m.get("probe_id") for m in measures} ==
        {p[0] for p in PROBES}
        and all(m.get("result", {}).get("measurement_valid") is True
                for m in measures)
    )
    if expected == "DEGRADED":
        verified = (
            bool(common)
            and b.get("state") == "APPLIED"
            and a.get("state") == "APPLIED"
            and b.get("qdisc") == "OWN_NETEM"
            and a.get("qdisc") == "OWN_NETEM"
            and b.get("ground_truth_degraded_verified") is True
            and a.get("ground_truth_degraded_verified") is True
            and "applied_at_utc" in b and "applied_at_utc" in a
        )
    else:
        verified = (
            bool(common)
            and b.get("state") == "RESTORED"
            and a.get("state") == "RESTORED"
            and b.get("qdisc") == "BASELINE"
            and a.get("qdisc") == "BASELINE"
            and "expired_at_utc" in b and "expired_at_utc" in a
            and "applied_at_utc" in b and "applied_at_utc" in a
        )
    return {
        "ground_truth_label": expected if verified else "UNKNOWN",
        "ground_truth_verified": bool(verified),
        "label_scope": SCOPE,
        "label_source": "root_owned_controller_and_tc_independent_of_rtt"
        if verified else "insufficient_guard_or_probe_confirmation",
    }


def capture(expected: str, rounds: int, packets: int) -> dict:
    if expected not in ("DEGRADED", "RECOVERY"):
        raise ValueError("unsupported_expected_class")
    if not 2 <= rounds <= 15 or not 2 <= packets <= 3:
        raise ValueError("rounds/packets_outside_safe_limits")
    if os.geteuid() == 0:
        raise RuntimeError("collector_must_run_unprivileged")
    initial = read_guard()
    desired = "APPLIED" if expected == "DEGRADED" else "RESTORED"
    if initial.get("state") != desired:
        raise RuntimeError("controller_not_in_expected_state")
    name = ("S06_WINDOW_" + expected + "_" +
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "_" + secrets.token_hex(3))
    folder = ROOT / name
    folder.mkdir(mode=0o700, parents=True, exist_ok=False)
    stream_file, meta_file = folder / "ventanas.jsonl", folder / "metadata.json"
    meta = {
        "schema": SCHEMA, "session_id": name,
        "expected_class": expected, "status": "capturing",
        "started_at_utc": utc(), "rounds_requested": rounds,
        "packets": packets, "controller_token": initial.get("token"),
        "label_scope": SCOPE, "training_ready": False,
        "source": "REAL_HQ_S1_S2", "network_changes_by_collector": False,
    }
    meta_file.write_text(json.dumps(meta, indent=2)+"\n", encoding="utf-8")
    records = []
    try:
        with stream_file.open("x", encoding="utf-8") as stream:
            for index in range(1, rounds+1):
                before = snapshot()
                measured = [measure_ping(probe, packets) for probe in PROBES]
                after = snapshot()
                labels = classify(expected, before, after, measured)
                row = {
                    "schema": SCHEMA, "session_id": name,
                    "window_index": index, "recorded_at_utc": utc(),
                    "before": before, "after": after,
                    "measurements": measured, **labels,
                    "network_changes_by_collector": False,
                }
                stream.write(json.dumps(row, ensure_ascii=False)+"\n")
                stream.flush()
                records.append(row)
                print(f"S06_042_VENTANA={index}/{rounds} "
                      f"ETIQUETA={labels['ground_truth_label']} "
                      f"VERIFICADA={labels['ground_truth_verified']}",
                      flush=True)
    finally:
        meta["finished_at_utc"] = utc()
        meta["samples_recorded"] = len(records)
        meta["verified"] = sum(r["ground_truth_verified"] for r in records)
        meta["unknown"] = len(records) - meta["verified"]
        meta["status"] = ("complete" if len(records) == rounds
                          and meta["verified"] == rounds else "partial_quality")
        if stream_file.exists():
            meta["data_digest_sha256"] = hashlib.sha256(
                stream_file.read_bytes()).hexdigest()
        meta_file.write_text(json.dumps(meta, indent=2)+"\n", encoding="utf-8")
    print("S06_042_SESION=" + name)
    print("S06_042_DIRECTORIO=" + str(folder))
    print(f"S06_042_VERIFICADAS={meta['verified']}/{meta['samples_recorded']}")
    print("S06_042_COLLECTOR_NO_MUTATION=SI")
    if meta["status"] != "complete":
        raise RuntimeError("partial_quality_keep_UNKNOWN_do_not_relabel")
    return meta


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--expected", required=True,
                   choices=("DEGRADED", "RECOVERY"))
    p.add_argument("--rounds", type=int, default=5)
    p.add_argument("--packets", type=int, default=2)
    args = p.parse_args()
    os.umask(0o077)
    capture(args.expected, args.rounds, args.packets)
    print("S06_042_CONTROLLED_WINDOW_CAPTURE=OK")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as exc:
        print(f"S06_042_COLLECTOR_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr)
        sys.exit(1)
