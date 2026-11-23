#!/usr/bin/env python3
"""S06-050: preregistro inmutable de TEST futuro sin reentrenar ni cambiar la red."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from inferencia_hq_readonly import REPORT, verified_report
from evaluar_deteccion_binaria import RAW, NORMAL_A, NORMAL_B, NORMAL_TEST, DEGRADED_INITIAL, SOURCE_MANIFEST, read_event_batches
from auditar_gates_prospectivos import session_time

ROOT = Path.home() / "netlab360-bootstrap/s06/preregistros"
FREEZE = ROOT / "S06_050_Prerregistro_Prospectivo.json"
AUDIT = (Path.home() / "netlab360-bootstrap/s06/auditorias-prospectivas"
         / "S06_049_20261123T110156Z_5ef7af/auditoria-readiness.json")
SCHEMA = "NETLAB360_S06_050_PREREGISTERED_V1"


def read_regular(path: Path, limit: int = 150000) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("source_not_regular")
    size = path.stat().st_size
    if not 0 < size <= limit:
        raise ValueError("source_size_invalid")
    return path.read_bytes()


def packet_count(session: str, controlled: bool) -> int:
    data = json.loads(read_regular(RAW / session / "metadata.json"))
    if data.get("session_id") != session or data.get("status") != "complete":
        raise ValueError("session_metadata_invalid")
    if controlled:
        if data.get("expected_class") != "DEGRADED":
            raise ValueError("controlled_class_invalid")
        count = data.get("packets")
    else:
        if (data.get("stimulus") != "NONE" or
                data.get("mutating_action_executed") is not False):
            raise ValueError("normal_conditions_invalid")
        count = data.get("packet_count_per_probe")
    if type(count) is not int or not 2 <= count <= 6:
        raise ValueError("packet_count_invalid")
    return count


def build(now: datetime | None = None) -> dict:
    report = verified_report()
    audit = json.loads(read_regular(AUDIT))
    if (audit.get("schema") != "NETLAB360_S06_049_READINESS_AUDIT_V1"
            or audit.get("gate") != "PENDING_NEW_PROSPECTIVE_EVIDENCE"
            or audit.get("audit_only") is not True
            or audit.get("chronology", {}).get("global_chronological_holdout") is not False
            or audit.get("verified_unique_windows_per_route") !=
               {"NORMAL": 60, "DEGRADED": 16, "RECOVERY": 24, "FAULT": 0}):
        raise ValueError("s06_049_gate_invalid")
    if (report.get("production_deployment_authorized") is not False
            or report.get("evaluation_exploratory") is not True
            or report.get("globally_chronological_holdout") is not False):
        raise ValueError("frozen_evaluation_invalid")
    train = report["train_normal_sessions"] + report["train_degraded_sessions"]
    test = (report["test_normal_sessions"] + report["test_degraded_sessions"]
            + report["test_recovery_sessions"])
    cycles = read_event_batches(SOURCE_MANIFEST)
    used = set(train + test + [NORMAL_A, NORMAL_B, NORMAL_TEST, DEGRADED_INITIAL])
    used.update(c[key]["session_id"] for c in cycles for key in ("degraded", "recovery"))
    latest = max(session_time(s) for s in used)
    clock = now or datetime.now(timezone.utc)
    if clock.tzinfo is None or clock.astimezone(timezone.utc) <= latest:
        raise ValueError("freeze_clock_not_after_existing_data")
    normal_ids = report["train_normal_sessions"] + report["test_normal_sessions"]
    packet_sizes = sorted({packet_count(s, False) for s in normal_ids}
                          | {packet_count(DEGRADED_INITIAL, True)})
    homogeneous = len(packet_sizes) == 1
    return {
        "schema": SCHEMA,
        "frozen_at_utc": clock.astimezone(timezone.utc).isoformat(),
        "latest_historical_session_start": latest.isoformat(),
        "scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
        "evaluation_digest": hashlib.sha256(read_regular(REPORT)).hexdigest(),
        "model_file_hashes": dict(report["model_files_sha256"]),
        "features": list(report["features"]),
        "methods": ["P95_RTT", "IsolationForest", "LogisticRegression"],
        "historical_ids_excluded_from_future_test": sorted(used),
        "historical_packet_counts": packet_sizes,
        "historical_sampling_homogeneous": homogeneous,
        "future_plan": {
            "freeze_models_no_fit_or_threshold_tuning": True,
            "new_sessions_after_freeze_only": True,
            "same_packet_count_required": True,
            "normal_windows_per_route_min": 20,
            "positive_independent_event_tokens_min": 2,
            "positive_windows_per_route_min": 8,
            "recovery_windows_per_route_min": 6,
            "labels_independent_of_rtt": True,
            "network_stimulus_requires_separate_explicit_authorization": True,
            "root_watchdog_and_recovery_required": True,
            "different_failure_type": "UNPROVEN_SEPARATE_EXPERIMENT_REQUIRED",
            "drift": "DESCRIPTIVE_ONLY_IF_SAMPLING_COMPARABLE",
            "concept_drift": "REQUIRES_POST_FREEZE_LABELS",
            "forecast_horizon": "NOT_DEFINED_NO_PREDICTION_CLAIM",
            "unknown_metrics": "NO_EVALUABLE_NOT_ZERO",
        },
        "new_prospective_test_completed": False,
        "production_deployment_authorized": False,
        "models_retrained": False,
        "network_mutations_executed": False,
        "status": "PLAN_READY" if homogeneous else "BLOCKED_INCOMPATIBLE_SAMPLING",
    }


def compare_frozen(old: dict, current: dict) -> None:
    if not isinstance(old, dict) or old.get("schema") != SCHEMA:
        raise ValueError("freeze_schema_invalid")
    if not set(old) == set(current):
        raise ValueError("frozen_fields_modified")
    for key in current:
        if key != "frozen_at_utc" and old[key] != current[key]:
            raise ValueError("frozen_contract_or_model_changed")
    freeze_time = datetime.fromisoformat(old["frozen_at_utc"])
    if freeze_time.tzinfo is None or freeze_time.astimezone(timezone.utc) <= datetime.fromisoformat(old["latest_historical_session_start"]):
        raise ValueError("frozen_timestamp_invalid")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--freeze", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    current = build()
    if args.freeze:
        if ROOT.is_symlink():
            raise ValueError("freeze_root_symlink")
        ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
        if ROOT.stat().st_uid != os.geteuid() or ROOT.stat().st_mode & 0o077:
            raise ValueError("freeze_root_not_private")
        if FREEZE.is_symlink():
            raise ValueError("freeze_symlink_forbidden")
        with FREEZE.open("x", encoding="utf-8") as stream:
            json.dump(current, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        FREEZE.chmod(0o600)
        frozen = current
    else:
        frozen = json.loads(read_regular(FREEZE))
        if FREEZE.stat().st_uid != os.geteuid() or FREEZE.stat().st_mode & 0o077:
            raise ValueError("freeze_permissions_invalid")
        compare_frozen(frozen, current)
    print("========== S06-050 PRERREGISTRO ==========")
    print("METODOS=" + ",".join(frozen["methods"]))
    print("MODELOS_CONGELADOS=" + str(len(frozen["model_file_hashes"])))
    print("PAQUETES_ORIGINALES=" + ",".join(map(str, frozen["historical_packet_counts"])))
    print("MUESTREO_COMPATIBLE=" + ("SI" if frozen["historical_sampling_homogeneous"] else "NO"))
    print("STATUS=" + frozen["status"])
    print("TEST_PROSPECTIVO_EJECUTADO=NO")
    print("MODELOS_REENTRENADOS=NO")
    print("CAMBIOS_RED=NINGUNO")
    print("PRERREGISTRO=" + str(FREEZE))
    print("S06_050_PRERREGISTRO=OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, KeyError, TypeError,
            json.JSONDecodeError) as exc:
        print("S06_050_ERROR=" + type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        sys.exit(1)
