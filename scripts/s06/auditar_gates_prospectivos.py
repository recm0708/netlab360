#!/usr/bin/env python3
"""S06-049: auditoría read-only de suficiencia cronológica y prospectiva.

NO reentrena, NO decide nuevos umbrales, NO modifica red, NO puntúa
el TEST usado en S06-044 una segunda vez. Reporta GATES PENDIENTES.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from evaluar_deteccion_binaria import (
    NORMAL_A, NORMAL_B, NORMAL_TEST, DEGRADED_INITIAL, RECOVERY_INITIAL,
    SOURCE_MANIFEST, PROBES, read_normal, read_controlled, read_event_batches,
)
from inferencia_hq_readonly import verified_report

ROOT = Path.home() / "netlab360-bootstrap/s06/auditorias-prospectivas"
SCHEMA = "NETLAB360_S06_049_READINESS_AUDIT_V1"
ID_TIMESTAMP_RE = re.compile(
    r"^S06_WINDOW_(?:NORMAL|DEGRADED|RECOVERY)_(\d{8}T\d{6}Z)_[a-f0-9]{6}$"
)
NORMAL_IDS = (NORMAL_A, NORMAL_B, NORMAL_TEST)
EXPECTED_COUNTS = {"NORMAL": 60, "DEGRADED": 16, "RECOVERY": 24}
REQUIRED_SCENARIOS = ("NORMAL", "DEGRADED", "FAULT", "RECOVERY")


def session_time(identifier: str) -> datetime:
    if not isinstance(identifier, str):
        raise ValueError("invalid_session_identifier")
    match = ID_TIMESTAMP_RE.fullmatch(identifier)
    if not match:
        raise ValueError("invalid_session_timestamp")
    return datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(
        tzinfo=timezone.utc)


def chronology(train: list[str], test: list[str]) -> dict:
    if (not isinstance(train, list) or not isinstance(test, list)
            or not train or not test or len(train) != len(set(train))
            or len(test) != len(set(test)) or set(train) & set(test)):
        raise ValueError("sessions_not_disjoint")
    times_train = [session_time(x) for x in train]
    times_test = [session_time(x) for x in test]
    tmax, tmin = max(times_train), min(times_test)
    return {
        "train_session_count": len(train),
        "test_session_count": len(test),
        "train_last_start_utc": tmax.isoformat(),
        "test_first_start_utc": tmin.isoformat(),
        "disjoint_session_ids": True,
        "global_chronological_holdout": tmax < tmin,
    }


def validate_counts(counts: dict) -> None:
    if not isinstance(counts, dict) or set(counts) != set(EXPECTED_COUNTS):
        raise ValueError("class_inventory_incomplete")
    for name, expected in EXPECTED_COUNTS.items():
        if type(counts[name]) is not int or counts[name] != expected:
            raise ValueError("class_window_count_mismatch_" + name)


def count_originals() -> dict:
    normal = [read_normal(session_id) for session_id in NORMAL_IDS]
    for rows in normal:
        if set(rows) != set(PROBES) or any(len(rows[route]) != 20 for route in PROBES):
            raise ValueError("normal_window_count_invalid")
    pairs = [(DEGRADED_INITIAL, RECOVERY_INITIAL)]
    cycles = read_event_batches(SOURCE_MANIFEST)
    if len(cycles) != 3:
        raise ValueError("controlled_cycle_count_invalid")
    for cycle in cycles:
        pairs.append((cycle["degraded"]["session_id"],
                      cycle["recovery"]["session_id"]))
    counts = {"NORMAL": 20 * len(normal), "DEGRADED": 0, "RECOVERY": 0}
    for d_sid, r_sid in pairs:
        d_meta, d_data = read_controlled(d_sid, "DEGRADED")
        r_meta, r_data = read_controlled(r_sid, "RECOVERY")
        if (set(d_data) != set(PROBES) or set(r_data) != set(PROBES)
                or d_meta.get("controller_token") != r_meta.get("controller_token")):
            raise ValueError("event_pair_provenance_invalid")
        d_size = {len(d_data[p]) for p in PROBES}
        r_size = {len(r_data[p]) for p in PROBES}
        if len(d_size) != 1 or len(r_size) != 1:
            raise ValueError("correlated_probe_count_invalid")
        counts["DEGRADED"] += next(iter(d_size))
        counts["RECOVERY"] += next(iter(r_size))
    validate_counts(counts)
    return counts


def findings(report: dict, counts: dict) -> dict:
    validate_counts(counts)
    if report.get("globally_chronological_holdout") is not False:
        raise ValueError("legacy_report_contract_changed")
    if (report.get("recovery_not_used_for_binary_training") is not True
            or set(report.get("metrics_by_probe", {})) != set(PROBES)
            or report.get("production_deployment_authorized") is not False):
        raise ValueError("evaluation_not_compatible")
    train = (report["train_normal_sessions"]
             + report["train_degraded_sessions"])
    test = (report["test_normal_sessions"]
            + report["test_degraded_sessions"])
    time_gate = chronology(train, test)
    if time_gate["global_chronological_holdout"]:
        raise ValueError("unexpected_chronology_reaudit_required")
    result = {
        "schema": SCHEMA,
        "scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
        "sources": {
            "training_and_test": "S06-041_NORMAL_AND_S06-042_043_CONTROLLED",
            "binary_evaluation": "S06-044_EXISTING_TEST",
            "fresh_unlabeled_observations": "S06-046_047_NOT_AN_INDEPENDENT_LABELED_TEST",
        },
        "verified_unique_windows_per_route": {**counts, "FAULT": 0},
        "route_count": len(PROBES),
        "routes_share_same_controlled_event": True,
        "chronology": time_gate,
        "test_degraded_windows_per_route": 4,
        "second_independent_future_labeled_test_present": False,
        "new_fault_class_present": False,
        "horizon_target_defined": False,
        "concept_drift_evaluable_with_ground_truth": False,
        "data_drift_monitor_prospectively_validated": False,
        "limitations": [
            "NORMAL_TEST_CAPTURED_BEFORE_DEGRADED_TRAIN",
            "FOUR_POSITIVE_WINDOWS_PER_ROUTE_IN_TEST",
            "TWO_ROUTES_SHARE_STIMULUS",
            "SINGLE_FIXED_40MS_LATENCY_STIMULUS",
            "NO_NEW_FAULT_OR_LOSS_LABELED_TEST",
            "NO_PROSPECTIVE_TIME_HORIZON_OR_TARGET",
            "FRESH_THREE_PACKET_MEASUREMENTS_NOT_COMPARABLE_AS_ORIGINAL_WINDOWS",
        ],
        "requirements_before_phase_closure": [
            "NEW_SESSIONS_WITH_GLOBAL_TRAIN_EARLIER_THAN_TEST",
            "UNSEEN_POSITIVE_EVENT_WITH_INDEPENDENT_LABEL_AND_RECOVERY",
            "SECOND_DISTINCT_FAILURE_SCENARIO_OR_EXPLICIT_SCOPE_EXCLUSION",
            "EXPLAINABLE_FORECAST_HORIZON_OR_HONEST_NOT_ESTIMABLE",
            "DATA_DRIFT_MONITOR_WITH_BASELINE_AND_VALID_FRESH_SAMPLING",
            "FINAL_S06_RESULTS_WITH_LIMITATIONS_AND_EVIDENCE",
        ],
        "audit_only": True,
        "new_independent_model_validation_performed": False,
        "models_retrained": False,
        "networks_modified": False,
        "production_deployment_authorized": False,
        "gate": "PENDING_NEW_PROSPECTIVE_EVIDENCE",
    }
    return result


def run() -> dict:
    return findings(verified_report(), count_originals())


def save(result: dict) -> Path:
    if ROOT.is_symlink():
        raise ValueError("root_symlink_forbidden")
    ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    if ROOT.stat().st_uid != os.geteuid() or ROOT.stat().st_mode & 0o077:
        raise ValueError("root_permissions_not_private")
    folder = ROOT / ("S06_049_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                     + "_" + secrets.token_hex(3))
    folder.mkdir(mode=0o700)
    target = folder / "auditoria-readiness.json"
    with target.open("x", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
        file.write("\n")
    target.chmod(0o600)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", action="store_true",
                        help="Guardar informe privado; no reentrena ni cambia la red")
    args = parser.parse_args()
    os.umask(0o077)
    report = run()
    print("========== S06-049 AUDITORIA DE GATES ==========")
    for key, value in report["verified_unique_windows_per_route"].items():
        print(f"CLASE={key} VENTANAS={value}")
    chronology_data = report["chronology"]
    print("TRAIN_TEST_SESIONES_SEPARADAS=" +
          ("SI" if chronology_data["disjoint_session_ids"] else "NO"))
    print("HOLDOUT_GLOBAL_CRONOLOGICO=" +
          ("SI" if chronology_data["global_chronological_holdout"] else "NO"))
    for limitation in report["limitations"]:
        print("LIMITACION=" + limitation)
    print("EVENTO_FAULT_VERIFICADO=NO")
    print("TEST_PROSPECTIVO_NUEVO=NO")
    print("PRONOSTICO_HORIZONTE=NO_IMPLEMENTADO")
    print("DRIFT_VALIDADO_PROSPECTIVO=NO")
    print("MODELOS_REENTRENADOS=NO")
    print("CAMBIOS_RED=NINGUNO")
    if args.save:
        print("S06_049_REPORTE=" + str(save(report)))
    print("S06_049_GATE=PENDING_NEW_PROSPECTIVE_EVIDENCE")
    print("S06_049_AUDITORIA_READONLY=OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, TypeError, KeyError,
            json.JSONDecodeError) as exc:
        print("S06_049_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
