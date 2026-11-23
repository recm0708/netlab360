#!/usr/bin/env python3
"""S06-043: ciclos autónomos supervisados en cliente REAL HQ existente.

Controlador root de S06-042 es la única entidad que ejecuta tc. Este
orquestador como usuario normal encadena ciclos independientes, siempre
con autorización literal explícita y watchdog previo, y aborta cualquier
ciclo posterior ante estado no validado. No crea namespaces/interfaces,
no elimina datos originales ni cambia rutas/gestión.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import time

EXE = "/usr/local/libexec/netlab360/s06-hq-controlador.py"
COLLECTOR = Path(__file__).resolve().parent / "capturar_ventanas_controladas.py"
BASE = Path.home() / "netlab360-bootstrap/s06"
APPROVAL = "AUTORIZO_HQ_VLAN120_NETEM_40MS_35S"
SCHEMA = "NETLAB360_S06_043_REAL_HQ_BATCH_V1"
WINDOW_SCHEMA = "NETLAB360_S06_HQ_CONTROLLED_WINDOWS_V1"
CLIENT = "nl360-s02-h-hq-120/eth0"
ROUND_DEGRADED = 4
ROUND_RECOVERY = 6


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run(args: list[str], *, timeout: int = 40) -> str:
    proc = subprocess.run(args, check=False, capture_output=True,
                          text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError("command_failed=" + str(args[:4])
                           + " rc=" + str(proc.returncode)
                           + " stderr=" + proc.stderr[-200:])
    return proc.stdout


def guard(*args: str) -> str:
    return run(["sudo", "-n", EXE, *args])


def guard_state() -> dict:
    raw = guard("status")
    for line in raw.splitlines():
        if line.startswith("S06_042_STATE_JSON="):
            record = json.loads(line.partition("=")[2])
            if record.get("schema") != "NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1":
                raise RuntimeError("guard_schema_unexpected")
            if record.get("target") != CLIENT:
                raise RuntimeError("guard_target_changed")
            return record
    raise RuntimeError("missing_guard_state")


def check_ready() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("execute_orchestrator_as_unprivileged_user")
    q = guard_state()
    if q.get("state") != "NONE" or q.get("qdisc") != "BASELINE":
        raise RuntimeError("previous_cycle_not_clean")
    stdout = guard("audit")
    if "S06_042_GUARD_AUDIT=OK_READONLY" not in stdout:
        raise RuntimeError("guard_audit_failed")


def validated_session(log: str, expected: str, token: str,
                      expected_rounds: int) -> dict:
    ids = re.findall(r"^S06_042_SESION=(.+)$", log, flags=re.MULTILINE)
    dirs = re.findall(r"^S06_042_DIRECTORIO=(.+)$", log,
                      flags=re.MULTILINE)
    if len(ids) != 1 or len(dirs) != 1:
        raise RuntimeError("collector_session_reference_missing")
    folder = Path(dirs[0])
    if folder.is_symlink() or folder.parent != BASE / "datasets/raw":
        raise RuntimeError("untrusted_dataset_path")
    if folder.name != ids[0]:
        raise RuntimeError("session_id_folder_mismatch")
    meta_path = folder / "metadata.json"
    rows_path = folder / "ventanas.jsonl"
    if any(p.is_symlink() or not p.is_file()
           for p in (meta_path, rows_path)):
        raise RuntimeError("dataset_files_missing_or_symlink")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    content = rows_path.read_bytes()
    if (
        meta.get("schema") != WINDOW_SCHEMA
        or meta.get("session_id") != ids[0]
        or meta.get("controller_token") != token
        or meta.get("expected_class") != expected
        or meta.get("status") != "complete"
        or meta.get("samples_recorded") != expected_rounds
        or meta.get("verified") != expected_rounds
        or meta.get("unknown") != 0
        or meta.get("data_digest_sha256") != hashlib.sha256(content).hexdigest()
    ):
        raise RuntimeError("dataset_integrity_or_ground_truth_unverified")
    rows = [json.loads(s) for s in content.decode().splitlines()
            if s.strip()]
    if len(rows) != expected_rounds:
        raise RuntimeError("window_count_unexpected")
    seen = set()
    observed_rtt = []
    guard_status = "APPLIED" if expected == "DEGRADED" else "RESTORED"
    expected_qdisc = "OWN_NETEM" if expected == "DEGRADED" else "BASELINE"
    for row in rows:
        index = row.get("window_index")
        if (not isinstance(index, int) or index in seen
                or row.get("schema") != WINDOW_SCHEMA
                or row.get("session_id") != ids[0]
                or row.get("ground_truth_label") != expected
                or row.get("ground_truth_verified") is not True
                or row.get("label_scope") != "HQ_CLIENT_EGRESS_NETWORK_STATE"
                or row.get("network_changes_by_collector") is not False):
            raise RuntimeError("invalid_labeled_window")
        seen.add(index)
        for boundary in ("before", "after"):
            snap = row.get(boundary, {})
            state = snap.get("guard", {})
            if (state.get("state") != guard_status
                    or state.get("qdisc") != expected_qdisc
                    or state.get("token") != token
                    or snap.get("routes_verified") is not True):
                raise RuntimeError("window_not_independently_verified")
        measurements = row.get("measurements", [])
        if (not isinstance(measurements, list) or len(measurements) != 2
                or {m.get("probe_id") for m in measurements} !=
                {"HQ_A_S1", "HQ_A_S2"}):
            raise RuntimeError("unexpected_measurement_count_or_route")
        for m in measurements:
            result = m.get("result", {})
            if result.get("measurement_valid") is not True:
                raise RuntimeError("invalid_measurement")
            observed_rtt.append(float(result["rtt_avg_ms"]))
    if seen != set(range(1, expected_rounds + 1)):
        raise RuntimeError("unexpected_window_index")
    return {
        "session_id": ids[0], "path": str(folder),
        "label": expected, "windows": len(rows),
        "measurement_count": len(observed_rtt),
        "rtt_avg_ms": sum(observed_rtt) / len(observed_rtt),
        "digest_sha256": meta["data_digest_sha256"],
    }


def save_manifest(path: Path, doc: dict) -> None:
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    tmp.chmod(0o600)
    tmp.replace(path)


def wait_recovery(token: str, timeout: int = 75) -> dict:
    stop = time.monotonic() + timeout
    last = None
    while time.monotonic() < stop:
        try:
            last = guard_state()
            if last.get("token") != token:
                raise RuntimeError("watchdog_state_token_changed")
            if last.get("state") == "ESCALATED":
                raise RuntimeError("watchdog_ESCALATED_do_not_cleanup")
            if last.get("state") == "RESTORED":
                if (last.get("qdisc") != "BASELINE"
                        or last.get("restoration_trigger") != "WATCHDOG"
                        or last.get("final_qdisc_state") != "BASELINE"):
                    raise RuntimeError("restoration_incomplete_or_not_autonomous")
                return last
            if last.get("state") in ("NONE", "RESTORED_NO_CHANGE"):
                raise RuntimeError("watchdog_unexpected_final_state")
        except RuntimeError as exc:
            # Transient lock contention from independent watchdog is expected;
            # other errors are not silently converted into success.
            if "concurrent_operation" not in str(exc):
                raise
        time.sleep(1)
    raise RuntimeError("watchdog_timeout_leave_state_untouched")


def run_one(index: int, folder: Path, report: dict) -> dict:
    check_ready()
    label = f"{index:02d}"
    cycle = {"number": index, "status": "preparing",
             "start_utc": utc()}
    report["cycles"].append(cycle)
    save_manifest(folder / "manifest.json", report)

    started = guard("start", "--approve", APPROVAL)
    (folder / f"ciclo_{label}_inicio.txt").write_text(started)
    if ("S06_042_TIMER_ARMED_BEFORE_TC=OK" not in started
            or "S06_042_PRODUCTION_QDISC=APPLIED" not in started):
        raise RuntimeError("guard_start_not_accepted")
    match = re.search(r"^S06_042_TOKEN=([0-9a-f]{16})$", started,
                      flags=re.MULTILINE)
    if not match:
        raise RuntimeError("missing_controller_token")
    token = match.group(1)
    cycle.update(token=token, status="applied", applied_utc=utc())
    save_manifest(folder / "manifest.json", report)
    print(f"S06_043_CICLO={index} WATCHDOG=ARMADO NETEM=APLICADO",
          flush=True)

    # No permitir que una captura fallida active un nuevo experimento.
    data_d = run(
        [sys.executable, "-u", str(COLLECTOR),
         "--expected", "DEGRADED", "--rounds",
         str(ROUND_DEGRADED), "--packets", "2"], timeout=25)
    (folder / f"ciclo_{label}_degraded.txt").write_text(data_d)
    degraded = validated_session(data_d, "DEGRADED", token, ROUND_DEGRADED)
    cycle.update(degraded=degraded, status="waiting_for_timer")
    save_manifest(folder / "manifest.json", report)

    restored = wait_recovery(token)
    (folder / f"ciclo_{label}_watchdog.json").write_text(
        json.dumps(restored, indent=2, ensure_ascii=False) + "\n")
    cycle.update(status="restored", restored_utc=utc())
    save_manifest(folder / "manifest.json", report)
    print(f"S06_043_CICLO={index} WATCHDOG=RESTORED QDISC=BASELINE",
          flush=True)

    data_r = run(
        [sys.executable, "-u", str(COLLECTOR),
         "--expected", "RECOVERY", "--rounds",
         str(ROUND_RECOVERY), "--packets", "3"], timeout=40)
    (folder / f"ciclo_{label}_recovery.txt").write_text(data_r)
    recovery = validated_session(data_r, "RECOVERY", token, ROUND_RECOVERY)
    if degraded["rtt_avg_ms"] <= recovery["rtt_avg_ms"] + 15:
        raise RuntimeError("measured_degradation_not_separated_from_recovery")
    cycle.update(recovery=recovery, status="ready_to_cleanup")
    save_manifest(folder / "manifest.json", report)

    # Guarda evidencia antes de que cleanup quite estado protegido.
    guard("cleanup")
    final = guard_state()
    if final.get("state") != "NONE" or final.get("qdisc") != "BASELINE":
        raise RuntimeError("cleanup_postconditions_failed")
    check_ready()
    cycle.update(status="complete", finished_utc=utc())
    save_manifest(folder / "manifest.json", report)
    print(f"S06_043_CICLO={index} DEGRADED={degraded['windows']} "
          f"RECOVERY={recovery['windows']} "
          f"RTT_D={degraded['rtt_avg_ms']:.3f}ms "
          f"RTT_R={recovery['rtt_avg_ms']:.3f}ms "
          "STATE=NONE", flush=True)
    return cycle


def orchestrate(cycles: int, approval: str) -> dict:
    if os.geteuid() == 0:
        raise RuntimeError("execute_orchestrator_as_unprivileged_user")
    if cycles < 2 or cycles > 3:
        raise ValueError("cycles_must_be_2_or_3")
    if approval != APPROVAL:
        raise RuntimeError("explicit_approval_required_for_entire_batch")
    if not COLLECTOR.is_file():
        raise RuntimeError("collector_missing")
    check_ready()
    folder = BASE / "experimentos" / (
        "S06_043_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "_" + secrets.token_hex(3))
    folder.mkdir(mode=0o700, parents=True, exist_ok=False)
    report = {
        "schema": SCHEMA, "session": folder.name,
        "start_utc": utc(), "planned_cycles": cycles,
        "status": "running", "explicit_human_approval": True,
        "target": CLIENT, "intended_mutations": "tc netem delay 40ms; TTL 35s",
        "management_interface_mutated": False,
        "new_namespaces_created": False, "new_interfaces_created": False,
        "ground_truth_source": "root_controller_and_tc_status_not_rtt",
        "operational_deployment_authorized": False,
        "cycles": [],
    }
    manifest = folder / "manifest.json"
    save_manifest(manifest, report)
    print("S06_043_DIRECTORIO=" + str(folder), flush=True)
    try:
        for i in range(1, cycles + 1):
            run_one(i, folder, report)
        report["status"] = "complete"
        report["finished_utc"] = utc()
        report["complete_cycles"] = cycles
    except Exception as exc:
        report["status"] = "stopped_requires_review"
        report["stop_reason"] = type(exc).__name__ + ": " + str(exc)
        report["finished_utc"] = utc()
        save_manifest(manifest, report)
        print("S06_043_ABORT=SI",
              "S06_043_NO_REPETIR_NI_BORRAR_ESTADO=SI", flush=True)
        raise
    save_manifest(manifest, report)
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cycles", required=True, type=int)
    p.add_argument("--approve-batch", required=True)
    args = p.parse_args()
    os.umask(0o077)
    outcome = orchestrate(args.cycles, args.approve_batch)
    deg = sum(c["degraded"]["windows"] for c in outcome["cycles"])
    rec = sum(c["recovery"]["windows"] for c in outcome["cycles"])
    print("S06_043_CICLOS_VALIDOS=" + str(outcome["complete_cycles"]))
    print("S06_043_DEGRADED_NUEVAS=" + str(deg))
    print("S06_043_RECOVERY_NUEVAS=" + str(rec))
    print("S06_043_HQ_ORIGINAL=BASELINE")
    print("S06_043_SESIONES_MULTIPLES=OK")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print("S06_043_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
