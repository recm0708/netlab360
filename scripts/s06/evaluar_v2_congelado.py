#!/usr/bin/env python3
"""S06 V2: puntuación posterior a freeze, sin reentrenamiento ni red.

VALIDATION y TEST solo se puntúan contra modelos congelados. Cada etapa
guarda resultado una vez y --check verifica sin repetir el scoring.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import statistics
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from auditar_muestreo_historico import inspect_session
from auditar_gates_prospectivos import session_time
from entrenar_baseline_anomalias import read_session as read_normal, PROBES, FEATURES
from evaluar_deteccion_binaria import read_controlled, confusion
from entrenar_y_congelar_v2 import (
    BASE, STUDY, DEST, REPORT, TARGET,
    verified_training, verify_report, read_regular
)

SCHEMA = "NETLAB360_S06_V2_FROZEN_SCORING_V1"
SCHEMA_STAGE = {
    "validation": "NETLAB360_S06_V2_VALIDATION_DATASET_V1",
    "test": "NETLAB360_S06_V2_TEST_DATASET_V1",
}
ENDPOINTS = STUDY / "evaluaciones-v2"
LABELS = ("NORMAL", "DEGRADED", "RECOVERY")
METHODS = ("P95_RTT", "IsolationForest", "LogisticRegression")


# La etapa se admite solo si respeta el orden y las restricciones del reporte congelado.
def parse_manifest(stage: str, frozen: dict) -> tuple[dict, dict]:
    if stage not in SCHEMA_STAGE:
        raise ValueError("stage_not_allowed")
    source = STUDY / f"{stage.upper()}_Manifest.json"
    data = json.loads(read_regular(source, 50000))
    normal = data.get("normal_session") or data.get("normal_session_id")
    degraded = data.get("degraded_sessions")
    recovery = data.get("recovery_sessions")
    tokens = data.get("event_tokens")
    mp = data.get("source_manifest")
    if (data.get("schema") != SCHEMA_STAGE[stage]
            or data.get("status") != f"{stage.upper()}_VERIFIED"
            or data.get("packets_per_window") != 3
            or data.get("models_retrained") is not False
            or not isinstance(normal, str)
            or not isinstance(degraded, list) or len(degraded) != 2
            or not isinstance(recovery, list) or len(recovery) != 2
            or not isinstance(tokens, list) or len(set(tokens)) != 2
            or not isinstance(mp, str)
            or len(set([normal] + degraded + recovery)) != 5):
        raise ValueError("stage_manifest_invalid")
    source_path = Path(mp)
    if (source_path.name != "manifest.json"
            or source_path.parent.parent != BASE / "experimentos"):
        raise ValueError("manifest_path_not_scoped")
    batch = json.loads(read_regular(source_path, 150000))
    if (batch.get("schema") != "NETLAB360_S06_043_REAL_HQ_BATCH_V1"
            or batch.get("status") != "complete"
            or batch.get("complete_cycles") != 2
            or batch.get("planned_cycles") != 2
            or batch.get("packets_per_degraded_window") != 3
            or batch.get("target") != TARGET
            or batch.get("management_interface_mutated") is not False
            or batch.get("new_namespaces_created") is not False
            or batch.get("new_interfaces_created") is not False):
        raise ValueError("controlled_stage_batch_invalid")
    cycles = batch.get("cycles")
    if not isinstance(cycles, list) or len(cycles) != 2:
        raise ValueError("controlled_stage_cycles_invalid")

    train_ids = set(frozen["training"]["normal_sessions"] +
                    frozen["training"]["degraded_sessions"] +
                    frozen["training"]["recovery_sessions"])
    train_tokens = set(frozen["training"]["event_tokens"])
    current_ids = [normal] + degraded + recovery
    if set(current_ids) & train_ids or set(tokens) & train_tokens:
        raise ValueError("stage_reuses_training_source")
    after = datetime.fromisoformat(frozen["frozen_at_utc"])
    if session_time(normal) <= after:
        raise ValueError("normal_collected_before_freeze")

    if stage == "test":
        prior, _ = parse_manifest("validation", frozen)
        prior_ids = [prior["normal_session"]] + prior["degraded_sessions"] + prior["recovery_sessions"]
        if (set(current_ids) & set(prior_ids)
                or set(tokens) & set(prior["event_tokens"])
                or session_time(normal) <= max(map(session_time, prior_ids))):
            raise ValueError("test_not_after_validation")

    raw_tokens = []
    for number, cycle in enumerate(cycles, 1):
        if (cycle.get("number") != number
                or cycle.get("status") != "complete"
                or cycle.get("degraded", {}).get("session_id") != degraded[number-1]
                or cycle.get("recovery", {}).get("session_id") != recovery[number-1]):
            raise ValueError("controlled_stage_cycle_source_invalid")
        token = cycle.get("token")
        if (not isinstance(token, str) or len(token) != 16 or any(
                c not in "0123456789abcdef" for c in token)):
            raise ValueError("stage_token_invalid")
        raw_tokens.append(token)
        watchdog = source_path.parent / f"ciclo_{number:02d}_watchdog.json"
        w = json.loads(read_regular(watchdog, 50000))
        if (w.get("token") != token
                or w.get("state") != "RESTORED"
                or w.get("qdisc") != "BASELINE"
                or w.get("restoration_trigger") != "WATCHDOG"
                or w.get("final_qdisc_state") != "BASELINE"):
            raise ValueError("stage_watchdog_not_independently_restored")
    if set(raw_tokens) != set(tokens) or len(set(raw_tokens)) != 2:
        raise ValueError("stage_token_mismatch")
    if not session_time(normal) < min(map(session_time, degraded)):
        raise ValueError("normal_not_before_positive_events")
    if min(map(session_time, recovery)) < min(map(session_time, degraded)):
        raise ValueError("recovery_precedes_degradation")
    normalized = dict(data, normal_session=normal)
    return normalized, batch


def read_stage(stage: str, frozen: dict) -> tuple[dict, dict]:
    manifest, batch = parse_manifest(stage, frozen)
    ids = {"NORMAL": [manifest["normal_session"]],
           "DEGRADED": manifest["degraded_sessions"],
           "RECOVERY": manifest["recovery_sessions"]}
    expected = {"NORMAL": 20, "DEGRADED": 4, "RECOVERY": 6}
    tables = {key: {} for key in LABELS}
    digests = {}
    for kind, sessions in ids.items():
        for i, sid in enumerate(sessions):
            info = inspect_session(sid, kind, "HISTORICAL_OTHER")
            if (info["windows_per_route"] != expected[kind]
                    or info["packets_per_window"] != 3
                    or info["packets_metadata_matches_actual"] is not True):
                raise ValueError("stage_measurement_not_comparable")
            if kind == "NORMAL":
                rows = read_normal(sid)
            else:
                metadata, rows = read_controlled(sid, kind)
                if metadata.get("controller_token") != batch["cycles"][i]["token"]:
                    raise ValueError("stage_ground_truth_token_mismatch")
            tables[kind][sid] = rows
            digests[sid] = hashlib.sha256(
                read_regular(BASE / "datasets/raw" / sid / "ventanas.jsonl",
                             2000000)).hexdigest()
    return {"manifest": manifest, "source_digests": digests,
            "batch_digest": hashlib.sha256(
                read_regular(Path(manifest["source_manifest"]), 150000)).hexdigest(),
            "manifest_digest": hashlib.sha256(
                read_regular(STUDY / f"{stage.upper()}_Manifest.json", 50000)).hexdigest(),
            "last_session_time_utc": max(session_time(s) for ids_ in ids.values()
                                         for s in ids_).isoformat()}, tables


# RECOVERY se analiza separadamente de los positivos DEGRADED y negativos NORMAL del cálculo binario.
def route_metrics(route: str, vectors: dict, frozen: dict, models: dict) -> dict:
    n = [x for sid in vectors["NORMAL"].values() for x in sid[route]]
    degraded_sessions = list(vectors["DEGRADED"].values())
    recovery_sessions = list(vectors["RECOVERY"].values())
    d = [x for session in degraded_sessions for x in session[route]]
    r = [x for session in recovery_sessions for x in session[route]]
    if len(n) != 20 or len(d) != 8 or len(r) != 12:
        raise ValueError("stage_class_window_count_invalid")
    cutoff = frozen["p95_cutoffs_ms"][route]
    if type(cutoff) not in (int, float) or not math.isfinite(cutoff) or cutoff < 0:
        raise ValueError("frozen_cutoff_invalid")
    predictors = {
        "P95_RTT": lambda rows: [int(row[0] > cutoff) for row in rows],
        "IsolationForest": lambda rows: [int(flag == -1) for flag in
                                               models["iforest"].predict(rows)],
        "LogisticRegression": lambda rows: [int(flag) for flag in
                                                 models["logistic"].predict(rows)],
    }
    outcome = {}
    for method, predict in predictors.items():
        preds_n, preds_d, preds_r = predict(n), predict(d), predict(r)
        if (len(preds_n) != 20 or len(preds_d) != 8 or len(preds_r) != 12
                or any(v not in (0, 1) for v in preds_n + preds_d + preds_r)):
            raise ValueError("model_prediction_invalid")
        metrics = confusion([0] * 20 + [1] * 8, preds_n + preds_d)
        metrics["recovery_false_alarms"] = sum(preds_r)
        metrics["recovery_test_samples"] = 12
        metrics["recovery_false_alarm_rate"] = sum(preds_r) / 12
        metrics["per_event_detected_windows"] = [
            sum(predict(session[route])) for session in degraded_sessions
        ]
        metrics["positive_events_with_any_detection"] = sum(
            x > 0 for x in metrics["per_event_detected_windows"])
        outcome[method] = metrics
    return {
        "methods": outcome,
        "normal_rtt_avg_ms": statistics.mean(x[0] for x in n),
        "normal_rtt_median_ms": statistics.median(x[0] for x in n),
        "normal_sample_count": len(n),
        "degraded_sample_count": len(d),
        "recovery_sample_count": len(r),
        "threshold_rtt_ms": cutoff,
        "drift_comment": "DESCRIPTIVE_ONLY_NOT_A_CONCEPT_DRIFT_TEST",
    }


def evaluate(stage: str) -> dict:
    if stage not in SCHEMA_STAGE:
        raise ValueError("stage_not_allowed")
    source, _ = verified_training()
    frozen = json.loads(read_regular(REPORT, 200000))
    verify_report(frozen, source)
    evidence, vectors = read_stage(stage, frozen)
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("joblib_required_science_env") from exc
    outcomes = {}
    for route in PROBES:
        models = {}
        for name in ("iforest", "logistic"):
            target = DEST / f"{route.lower()}_{name}.joblib"
            models[name] = joblib.load(target)
        outcomes[route] = route_metrics(route, vectors, frozen, models)
    result = {
        "schema": SCHEMA,
        "stage": stage.upper(),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "models_frozen_report_digest": hashlib.sha256(read_regular(REPORT, 200000)).hexdigest(),
        "model_file_hashes": frozen["model_files_sha256"],
        "features": list(FEATURES),
        "routes": list(PROBES),
        "source": evidence,
        "metrics_by_route": outcomes,
        "train_used_for_fit_only": True,
        "scored_only_after_model_freeze": True,
        "data_used_for_model_fit": False,
        "models_retrained": False,
        "network_mutations_executed": False,
        "forecast_horizon_assessed": False,
        "production_deployment_authorized": False,
        "generalization_beyond_hq_40ms_demonstrated": False,
        "limitations": [
            "TWO_ROUTES_CORRELATED_PER_EVENT",
            "ONLY_TWO_POSITIVE_EVENTS_IN_STAGE",
            "ONE_FIXED_40MS_LATENCY_SCENARIO",
            "NOT_VALIDATED_FOR_REAL_FAULT_OR_OSPF_SDNLACP_OUTAGE",
            "NO_FUTURE_FORECAST_HORIZON",
        ],
    }
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=tuple(SCHEMA_STAGE), required=True)
    p.add_argument("--save", action="store_true")
    args = p.parse_args()
    os.umask(0o077)
    target = ENDPOINTS / f"{args.stage}.json"
    if args.save and (target.exists() or target.is_symlink()):
        raise ValueError("existing_stage_result_no_rescore_or_overwrite")
    result = evaluate(args.stage)
    print(f"========== S06 V2 {args.stage.upper()} FROZEN SCORING ==========")
    for route in PROBES:
        row = result["metrics_by_route"][route]
        for name in METHODS:
            m = row["methods"][name]
            print(f"RUTA={route} MODELO={name} TP={m['tp']} FP={m['fp']} "
                  f"TN={m['tn']} FN={m['fn']} P={m['precision']:.3f} "
                  f"R={m['recall']:.3f} F1={m['f1']:.3f} "
                  f"RECOVERY_FP={m['recovery_false_alarms']}/12 "
                  f"EVENTOS_DETECTADOS={m['positive_events_with_any_detection']}/2")
    if args.save:
        if ENDPOINTS.is_symlink():
            raise ValueError("output_directory_symlink")
        ENDPOINTS.mkdir(parents=True, mode=0o700, exist_ok=True)
        if ENDPOINTS.stat().st_uid != os.geteuid() or ENDPOINTS.stat().st_mode & 0o077:
            raise ValueError("output_directory_not_private")
        with target.open("x", encoding="utf-8") as file:
            json.dump(result, file, ensure_ascii=False, indent=2)
            file.write("\n")
        target.chmod(0o600)
        print("S06_V2_EVALUACION=" + str(target))
    print("MODELOS_REENTRENADOS=NO")
    print("CAMBIOS_RED=NINGUNO")
    print("S06_V2_FROZEN_SCORING=OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError, TypeError,
            json.JSONDecodeError) as exc:
        print("S06_V2_SCORING_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
