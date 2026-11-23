#!/usr/bin/env python3
"""Auditoría SOLO LECTURA de deriva descriptiva y oportunidades de detección V2."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from entrenar_baseline_anomalias import FEATURES, PROBES
from entrenar_y_congelar_v2 import BASE, STUDY, DEST, REPORT, read_regular, verified_training, verify_report
from evaluar_v2_congelado import read_stage, METHODS, SCHEMA as SCORE_SCHEMA

SCHEMA = "NETLAB360_S06_V2_FINAL_AUDIT_V1"
OUT = STUDY / "evaluaciones-v2/auditoria-cientifica-final.json"


def utc(s):
    if not isinstance(s, str):
        raise ValueError("timestamp_missing")
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None or d.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp_not_utc")
    return d.astimezone(timezone.utc)


def ks(a, b):
    if len(a) < 2 or len(b) < 2 or any(not math.isfinite(v) for v in a+b):
        raise ValueError("ks_invalid_samples")
    a, b = sorted(a), sorted(b)
    i = j = 0
    d = 0.0
    for v in sorted(set(a+b)):
        while i < len(a) and a[i] <= v: i += 1
        while j < len(b) and b[j] <= v: j += 1
        d = max(d, abs(i/len(a)-j/len(b)))
    return round(d, 6)


def feat(table, route, k):
    return [float(x[k]) for sample in table.values() for x in sample[route]]


def drift(a, b, c, route):
    result = {}
    for i, name in enumerate(FEATURES):
        train, validation, test = (feat(x, route, i) for x in (a, b, c))
        if (len(train), len(validation), len(test)) != (40, 20, 20):
            raise ValueError("normal_split_sizes_wrong")
        result[name] = {
            "train_mean": round(statistics.mean(train), 8),
            "validation_mean": round(statistics.mean(validation), 8),
            "test_mean": round(statistics.mean(test), 8),
            "test_minus_train_mean": round(statistics.mean(test)-statistics.mean(train), 8),
            "ks_train_validation": ks(train, validation),
            "ks_train_test": ks(train, test),
            "sample_sizes": [40,20,20],
            "inference": "DESCRIPTIVE_ONLY_NO_SIGNIFICANCE_CLAIM",
        }
    return result


def predicted(rows, method, cutoff, models):
    if method == "P95_RTT":
        out = [int(x[0] > cutoff) for x in rows]
    elif method == "IsolationForest":
        out = [int(x == -1) for x in models["iforest"].predict(rows)]
    elif method == "LogisticRegression":
        out = [int(x) for x in models["logistic"].predict(rows)]
    else:
        raise ValueError("unknown_method")
    if len(out) != len(rows) or any(x not in (0,1) for x in out):
        raise ValueError("prediction_replay_invalid")
    return out


def event_opportunities(stage, route, models, cutoff, rows, scored):
    result = {}
    for method in METHODS:
        result[method] = []
        for index, (sid, vectors) in enumerate(rows["DEGRADED"].items()):
            path = BASE / "datasets/raw" / sid / "ventanas.jsonl"
            raw = [json.loads(x) for x in read_regular(path, 2000000).decode().splitlines() if x]
            if len(raw) != 4 or len(vectors[route]) != 4:
                raise ValueError("event_window_count_invalid")
            applies = []
            records = []
            token = None
            for j, item in enumerate(raw, 1):
                guard = item.get("before", {}).get("guard", {})
                if token is None: token = guard.get("token")
                if (item.get("window_index") != j or item.get("session_id") != sid
                        or item.get("ground_truth_label") != "DEGRADED"
                        or item.get("ground_truth_verified") is not True
                        or guard.get("state") != "APPLIED" or not token
                        or guard.get("token") != token):
                    raise ValueError("event_label_or_guard_invalid")
                applies.append(utc(guard.get("applied_at_utc")))
                records.append(utc(item["recorded_at_utc"]))
            if len(set(applies)) != 1 or any(rec < applies[0] for rec in records):
                raise ValueError("event_timestamps_invalid")
            predictions = predicted(vectors[route], method, cutoff, models)
            expected = scored["metrics_by_route"][route]["methods"][method][
                "per_event_detected_windows"][index]
            if sum(predictions) != expected:
                raise ValueError("trace_disagrees_with_stored_scoring")
            first = next((i for i, p in enumerate(predictions) if p == 1), None)
            delay = (round((records[first]-applies[0]).total_seconds()*1000,3)
                     if first is not None else None)
            result[method].append({
                "session": sid, "event_ordinal": index+1,
                "positive_windows": sum(predictions),
                "first_detected_window": first+1 if first is not None else None,
                "retrospective_detection_opportunity_ms": delay,
                "true_online_alert_time_measured": False,
            })
    return result


def audit():
    source, train = verified_training()
    frozen = json.loads(read_regular(REPORT, 200000))
    verify_report(frozen, source)
    stages = {}
    scores = {}
    for stage in ("validation","test"):
        provenance, tables = read_stage(stage, frozen)
        score_path = STUDY / "evaluaciones-v2" / (stage+".json")
        scored = json.loads(read_regular(score_path, 250000))
        if (scored.get("schema") != SCORE_SCHEMA
                or scored.get("stage") != stage.upper()
                or scored.get("source") != provenance
                or scored.get("model_file_hashes") != frozen["model_files_sha256"]
                or scored.get("models_frozen_report_digest") !=
                   hashlib.sha256(read_regular(REPORT, 200000)).hexdigest()
                or scored.get("models_retrained") is not False
                or scored.get("data_used_for_model_fit") is not False):
            raise ValueError("stage_scoring_not_frozen_or_modified")
        stages[stage], scores[stage] = tables, scored
    import joblib
    results = {}
    for route in PROBES:
        models = {name: joblib.load(DEST / f"{route.lower()}_{name}.joblib")
                  for name in ("iforest","logistic")}
        results[route] = {
            "data_drift": drift(train["NORMAL"], stages["validation"]["NORMAL"],
                                stages["test"]["NORMAL"], route),
            "detection_opportunities": {
                st: event_opportunities(st, route, models,
                      frozen["p95_cutoffs_ms"][route], stages[st], scores[st])
                for st in ("validation","test")
            },
            "test_confusion": scores["test"]["metrics_by_route"][route]["methods"],
        }
    return {
        "schema": SCHEMA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "routes": list(PROBES),
        "results": results,
        "frozen_model_report_digest": hashlib.sha256(read_regular(REPORT,200000)).hexdigest(),
        "test_source_digest": hashlib.sha256(read_regular(STUDY/"evaluaciones-v2/test.json",250000)).hexdigest(),
        "split_counts_per_route": {"TRAIN":[40,8,12], "VALIDATION":[20,8,12], "TEST":[20,8,12]},
        "data_drift": "DESCRIPTIVE_ONLY",
        "concept_drift": "NO_EVALUABLE_WITH_ONLY_TWO_EVENTS_PER_SPLIT",
        "time_to_detection": "OFFLINE_FIRST_SCORABLE_WINDOW_NOT_ONLINE_ALERT",
        "forecast_horizon": "NO_EVALUABLE_NO_FUTURE_TARGET",
        "forecast_mae": None,
        "fault_class": "NO_INDEPENDENT_VERIFIED_FAULT",
        "new_test_performed": False,
        "test_used_to_tune_model": False,
        "models_retrained": False,
        "network_changes": False,
        "gate": "PROSPECTIVE_40MS_DETECTION_CONFIRMED_SCOPE_REVIEW_PENDING",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--save", action="store_true")
    args = p.parse_args()
    os.umask(0o077)
    if args.save and (OUT.exists() or OUT.is_symlink()):
        raise ValueError("final_audit_exists_no_overwrite")
    report = audit()
    print("========== S06 V2 AUDITORIA DE DRIFT Y DETECCION ==========")
    for route, info in report["results"].items():
        x = info["data_drift"]["rtt_avg_ms"]
        print(f"RUTA={route} RTT_TRAIN_MS={x['train_mean']:.4f} "
              f"RTT_TEST_MS={x['test_mean']:.4f} "
              f"CAMBIO_MS={x['test_minus_train_mean']:+.4f} "
              f"KS={x['ks_train_test']:.3f}")
        for method, events in info["detection_opportunities"]["test"].items():
            values = [x["retrospective_detection_opportunity_ms"] for x in events]
            print(f"RUTA={route} MODELO={method} "
                  f"OPORTUNIDAD_OFFLINE_MS={values} "
                  f"EVENTOS_DETECTADOS={sum(v is not None for v in values)}/2")
    print("DATA_DRIFT=DESCRIPTIVO")
    print("CONCEPT_DRIFT=NO_EVALUABLE")
    print("PRONOSTICO_TEMPORAL=NO_EVALUABLE")
    print("FAULT_INDEPENDIENTE=NO_VERIFICADO")
    print("ALERTA_REAL_MEDIDA=NO")
    print("REENTRENAMIENTO=NINGUNO")
    print("CAMBIOS_RED=NINGUNO")
    if args.save:
        if OUT.parent.is_symlink() or not OUT.parent.is_dir():
            raise ValueError("report_folder_invalid")
        if OUT.parent.stat().st_uid != os.geteuid() or OUT.parent.stat().st_mode & 0o077:
            raise ValueError("report_folder_not_private")
        with OUT.open("x",encoding="utf-8") as stream:
            json.dump(report,stream,ensure_ascii=False,indent=2)
            stream.write("\n")
        OUT.chmod(0o600)
        print("S06_V2_REPORTE_FINAL="+str(OUT))
    print("S06_V2_DRIFT_LATENCIA_AUDITADOS=OK")


if __name__ == "__main__":
    try: main()
    except (ValueError, TypeError, RuntimeError, OSError, KeyError, json.JSONDecodeError) as exc:
        print("S06_V2_AUDITORIA_ERROR="+type(exc).__name__+": "+str(exc),file=sys.stderr)
        sys.exit(1)
