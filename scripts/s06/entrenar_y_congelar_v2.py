#!/usr/bin/env python3
"""S06-V2: entrena y congela solo TRAIN uniforme, sin intervenir la red.

--freeze es de un solo uso. --check valida modelos guardados sin reentrenar.
NO importa TRAIN/TEST legacy como datos, NO usa VALIDATION/TEST V2.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from entrenar_baseline_anomalias import read_session as read_normal, PROBES, FEATURES
from evaluar_deteccion_binaria import read_controlled, p95
from auditar_muestreo_historico import inspect_session
from auditar_gates_prospectivos import session_time
from prerregistrar_estudio_futuro import (
    FREEZE as OLD_FREEZE, read_regular, compare_frozen,
    build as current_legacy_freeze,
)

BASE = Path.home() / "netlab360-bootstrap/s06"
STUDY = BASE / "estudio-uniforme-v2"
TRAIN = STUDY / "TRAIN_Manifest.json"
DEST = STUDY / "modelos-v2"
REPORT = DEST / "S06_V2_Training_Freeze.json"
SCHEMA = "NETLAB360_S06_V2_TRAIN_FREEZE_V1"
TRAIN_SCHEMA = "NETLAB360_S06_V2_TRAIN_DATASET_V1"
BATCH_SCHEMA = "NETLAB360_S06_043_REAL_HQ_BATCH_V1"
TARGET = "nl360-s02-h-hq-120/eth0"
APPROVED_NORMAL = (
    "S06_WINDOW_NORMAL_20261123T143842Z_1e1812",
    "S06_WINDOW_NORMAL_20261123T143913Z_b5d57c",
)


def assert_legacy_lock() -> None:
    old = json.loads(read_regular(OLD_FREEZE))
    compare_frozen(old, current_legacy_freeze())
    if old.get("status") != "BLOCKED_INCOMPATIBLE_SAMPLING":
        raise ValueError("legacy_frozen_contract_not_blocked")


def validate_train_map(data: dict) -> tuple[list[str], list[str], list[str], Path]:
    if (not isinstance(data, dict)
            or data.get("schema") != TRAIN_SCHEMA
            or data.get("status") != "TRAIN_VERIFIED"
            or data.get("models_trained") is not False
            or data.get("event_count") != 2
            or data.get("packets_per_window") != 3):
        raise ValueError("train_map_contract_invalid")
    normal = data.get("normal_sessions")
    degraded = data.get("degraded_sessions")
    recovery = data.get("recovery_sessions")
    if (normal != list(APPROVED_NORMAL) or not isinstance(degraded, list)
            or not isinstance(recovery, list)
            or len(degraded) != 2 or len(recovery) != 2
            or len(set(normal + degraded + recovery)) != 6):
        raise ValueError("train_session_partition_invalid")
    for sid, label in [
        *((s, "DEGRADED") for s in degraded),
        *((s, "RECOVERY") for s in recovery),
    ]:
        if not isinstance(sid, str) or not sid.startswith("S06_WINDOW_" + label + "_"):
            raise ValueError("train_session_class_invalid")
        session_time(sid)
    if (not session_time(normal[-1]) < min(map(session_time, degraded))
            or not max(map(session_time, degraded)) < max(map(session_time, recovery))):
        raise ValueError("train_chronology_invalid")
    mp = data.get("source_manifest")
    folder = Path(mp) if isinstance(mp, str) else Path(".")
    if (not isinstance(mp, str)
            or folder.name != "manifest.json"
            or folder.parent.parent != BASE / "experimentos"
            or folder.is_symlink() or not folder.is_file()):
        raise ValueError("source_manifest_scope_invalid")
    return normal, degraded, recovery, folder


def verified_training() -> tuple[dict, dict]:
    assert_legacy_lock()
    data = json.loads(read_regular(TRAIN, 50000))
    normal_ids, degraded_ids, recovery_ids, path = validate_train_map(data)
    manifest = json.loads(read_regular(path, 100000))
    if (manifest.get("schema") != BATCH_SCHEMA
            or manifest.get("status") != "complete"
            or manifest.get("complete_cycles") != 2
            or manifest.get("planned_cycles") != 2
            or manifest.get("packets_per_degraded_window") != 3
            or manifest.get("target") != TARGET
            or manifest.get("explicit_human_approval") is not True
            or manifest.get("management_interface_mutated") is not False
            or manifest.get("new_namespaces_created") is not False
            or manifest.get("new_interfaces_created") is not False):
        raise ValueError("controlled_train_manifest_invalid")
    cycles = manifest.get("cycles")
    if not isinstance(cycles, list) or len(cycles) != 2:
        raise ValueError("train_cycles_missing")
    tokens = []
    for i, cycle in enumerate(cycles, 1):
        if (cycle.get("number") != i or cycle.get("status") != "complete"
                or cycle.get("degraded", {}).get("session_id") != degraded_ids[i - 1]
                or cycle.get("recovery", {}).get("session_id") != recovery_ids[i - 1]):
            raise ValueError("train_cycle_session_mismatch")
        token = cycle.get("token")
        if not isinstance(token, str) or len(token) != 16 or any(
                c not in "0123456789abcdef" for c in token):
            raise ValueError("train_event_token_invalid")
        tokens.append(token)
        watchdog = path.parent / f"ciclo_{i:02d}_watchdog.json"
        evidence = json.loads(read_regular(watchdog))
        if (evidence.get("token") != token
                or evidence.get("state") != "RESTORED"
                or evidence.get("qdisc") != "BASELINE"
                or evidence.get("restoration_trigger") != "WATCHDOG"
                or evidence.get("final_qdisc_state") != "BASELINE"):
            raise ValueError("autonomous_recovery_not_proven")
    if len(set(tokens)) != 2:
        raise ValueError("training_tokens_reused")

    tables = {"NORMAL": {}, "DEGRADED": {}, "RECOVERY": {}}
    source_digests = {}
    all_ids = normal_ids + degraded_ids + recovery_ids
    for label, ids, expected in [
        ("NORMAL", normal_ids, 20),
        ("DEGRADED", degraded_ids, 4),
        ("RECOVERY", recovery_ids, 6),
    ]:
        for i, sid in enumerate(ids):
            info = inspect_session(sid, label, "TRAIN" if label != "RECOVERY"
                                   else "RECOVERY_ANALYSIS")
            if (info["windows_per_route"] != expected
                    or info["packets_per_window"] != 3
                    or info["measurements_with_packet_loss"] != 0
                    or info["packets_metadata_matches_actual"] is not True):
                raise ValueError("incompatible_or_partial_training_window")
            if label == "NORMAL":
                vectors = read_normal(sid)
            else:
                meta, vectors = read_controlled(sid, label)
                if meta.get("controller_token") != tokens[i]:
                    raise ValueError("train_event_ground_truth_token_mismatch")
            tables[label][sid] = vectors
            source_digests[sid] = hashlib.sha256(
                read_regular(BASE / "datasets/raw" / sid / "ventanas.jsonl",
                             2000000)).hexdigest()
    return {
        "normal_sessions": normal_ids,
        "degraded_sessions": degraded_ids,
        "recovery_sessions": recovery_ids,
        "event_tokens": tokens,
        "source_digests": source_digests,
        "source_train_map_digest": hashlib.sha256(read_regular(TRAIN)).hexdigest(),
        "source_batch_digest": hashlib.sha256(read_regular(path)).hexdigest(),
        "training_session_latest": max(session_time(s) for s in all_ids).isoformat(),
    }, tables


def build_estimators(vectors: dict) -> tuple[dict, dict]:
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("sklearn_missing_use_science_venv") from exc

    models = {}
    cutoffs = {}
    for route in PROBES:
        normal = [item for rows in vectors["NORMAL"].values() for item in rows[route]]
        degraded = [item for rows in vectors["DEGRADED"].values() for item in rows[route]]
        recovery = [item for rows in vectors["RECOVERY"].values() for item in rows[route]]
        if len(normal) != 40 or len(degraded) != 8 or len(recovery) != 12:
            raise ValueError("training_class_balance_invalid")
        if any(len(v) != len(FEATURES) or any(
                type(x) not in (float, int) or not math.isfinite(x) or x < 0 for x in v)
               for v in normal + degraded + recovery):
            raise ValueError("training_feature_invalid")
        threshold = float(p95(normal))
        iso = IsolationForest(n_estimators=100, contamination=0.05,
                              random_state=42, n_jobs=1)
        iso.fit(normal)
        clf = Pipeline([
            ("scale", StandardScaler()),
            ("logistic", LogisticRegression(
                class_weight="balanced", max_iter=1500, random_state=42)),
        ])
        clf.fit(normal + degraded, [0] * len(normal) + [1] * len(degraded))
        models[route] = {"iforest": iso, "logistic": clf}
        cutoffs[route] = threshold
    return models, cutoffs


def persist_freeze(source: dict, models: dict, cutoffs: dict) -> Path:
    import joblib
    if (STUDY.is_symlink() or not STUDY.is_dir()
            or STUDY.stat().st_uid != os.geteuid()
            or STUDY.stat().st_mode & 0o077):
        raise ValueError("study_directory_not_private")
    DEST.mkdir(mode=0o700, exist_ok=False)
    files = {}
    for route in PROBES:
        for kind in ("iforest", "logistic"):
            filename = f"{route.lower()}_{kind}.joblib"
            target = DEST / filename
            if target.exists() or target.is_symlink():
                raise ValueError("model_duplicate")
            joblib.dump(models[route][kind], target)
            target.chmod(0o600)
            files[filename] = hashlib.sha256(read_regular(target, 10000000)).hexdigest()
    report = {
        "schema": SCHEMA,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "training_complete": True,
        "operational_deployment_authorized": False,
        "independent_test_completed": False,
        "validation_data_used": False,
        "test_data_used": False,
        "old_models_modified": False,
        "network_mutations_by_training": False,
        "scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
        "features": list(FEATURES),
        "routes": list(PROBES),
        "class_packet_count_uniform": 3,
        "train_normal_per_route": 40,
        "train_degraded_per_route": 8,
        "train_recovery_per_route": 12,
        "train_recovery_excluded_from_fit": True,
        "training": source,
        "parameters": {
            "P95_RTT": "NORMAL_TRAIN_95TH_PERCENTILE_ON_RTT_AVG",
            "IsolationForest": {"n_estimators": 100, "contamination": 0.05,
                                "random_state": 42, "n_jobs": 1},
            "LogisticRegression": {"class_weight": "balanced",
                                   "max_iter": 1500, "random_state": 42,
                                   "standard_scaler": True},
        },
        "p95_cutoffs_ms": cutoffs,
        "model_files_sha256": files,
        "generalization_demonstrated": False,
        "forecast_horizon_defined": False,
        "allowed_next_stage": "COLLECT_VALIDATION_NO_NEW_FIT",
    }
    with REPORT.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    REPORT.chmod(0o600)
    return REPORT


def verify_report(data: dict, source: dict) -> None:
    if (data.get("schema") != SCHEMA
            or data.get("training_complete") is not True
            or data.get("independent_test_completed") is not False
            or data.get("validation_data_used") is not False
            or data.get("test_data_used") is not False
            or data.get("operational_deployment_authorized") is not False
            or data.get("class_packet_count_uniform") != 3
            or data.get("train_normal_per_route") != 40
            or data.get("train_degraded_per_route") != 8
            or data.get("train_recovery_per_route") != 12
            or data.get("train_recovery_excluded_from_fit") is not True
            or data.get("features") != list(FEATURES)
            or data.get("routes") != list(PROBES)
            or data.get("training") != source):
        raise ValueError("v2_freeze_contract_invalid")
    file_digests = data.get("model_files_sha256")
    if not isinstance(file_digests, dict) or len(file_digests) != 4:
        raise ValueError("v2_model_inventory_invalid")
    for route in PROBES:
        for kind in ("iforest", "logistic"):
            fname = f"{route.lower()}_{kind}.joblib"
            if fname not in file_digests:
                raise ValueError("v2_model_missing")
            target = DEST / fname
            if hashlib.sha256(read_regular(target, 10000000)).hexdigest() != file_digests[fname]:
                raise ValueError("v2_model_file_changed")
    limits = data.get("p95_cutoffs_ms", {})
    if (set(limits) != set(PROBES)
            or any(type(v) not in (float, int) or not math.isfinite(v) or v < 0
                   for v in limits.values())):
        raise ValueError("v2_p95_cutoff_invalid")
    if (data.get("generalization_demonstrated") is not False
            or data.get("forecast_horizon_defined") is not False):
        raise ValueError("v2_scope_overclaimed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--freeze", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    source, vectors = verified_training()
    if args.freeze:
        if DEST.exists() or DEST.is_symlink():
            raise ValueError("v2_freeze_exists_no_retraining_or_overwriting")
        models, cutoffs = build_estimators(vectors)
        persist_freeze(source, models, cutoffs)
    if DEST.is_symlink() or not DEST.is_dir():
        raise ValueError("v2_model_dir_invalid")
    data = json.loads(read_regular(REPORT, 200000))
    verify_report(data, source)
    print("========== S06 V2 TRAIN MODELOS CONGELADOS ==========")
    print("NORMAL_TRAIN_POR_RUTA=40")
    print("DEGRADED_TRAIN_POR_RUTA=8")
    print("RECOVERY_ENTRENAMIENTO=EXCLUIDO")
    print("MUESTREO_TRES_PAQUETES=VERIFICADO")
    print("EVENTOS_POSITIVOS_TRAIN=2")
    print("MODELOS_V2=4")
    print("MODELOS_LEGACY=NO_MODIFICADOS")
    print("VALIDATION_USADA=NO")
    print("TEST_USADO=NO")
    print("GENERALIZACION_PROBADA=NO")
    print("CAMBIOS_RED=NINGUNO")
    print("S06_V2_CONGELACION=" + str(REPORT))
    print("S06_V2_TRAIN_FREEZE=OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError, TypeError,
            json.JSONDecodeError) as exc:
        print("S06_V2_TRAIN_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
