#!/usr/bin/env python3
"""S06-045: replay de inferencia HQ, solo lectura; NO servicio productivo.

Reutiliza modelos privados S06-044 y sesiones verificadas. El TEST historico
NO es una nueva validacion independiente. No lee ni altera interfaces de red.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Literal

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from evaluar_deteccion_binaria import (
    FEATURES, PROBES, EVAL_SCHEMA, NORMAL_TEST, SOURCE_MANIFEST,
    read_normal, read_controlled, read_event_batches,
)
from telemetria_hq_live import read_latest

EVAL_DIR = (Path.home() / "netlab360-bootstrap/s06/evaluaciones"
            / "S06_044_20261123T081627Z_2ade0e")
REPORT = EVAL_DIR / "evaluacion.json"
MODEL_NAMES = ("P95_RTT", "IsolationForest", "LogisticRegression")
SCENARIOS = ("NORMAL", "DEGRADED", "RECOVERY")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
MODE = "HISTORICAL_REPLAY_ONLY"


def _is_regular(path: Path) -> bool:
    return not path.is_symlink() and path.is_file()


def verified_report() -> dict:
    """No deserializar modelos antes de validar todos sus digests locales."""
    if not _is_regular(REPORT) or REPORT.stat().st_size > 100_000:
        raise ValueError("evaluation_report_missing_or_invalid")
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    if (data.get("schema") != EVAL_SCHEMA
            or data.get("features") != list(FEATURES)
            or data.get("target") != "nl360-s02-h-hq-120/eth0"
            or data.get("evaluation_exploratory") is not True
            or data.get("production_deployment_authorized") is not False
            or data.get("s07_mutating_actions_authorized") is not False
            or data.get("globally_chronological_holdout") is not False
            or data.get("recovery_not_used_for_binary_training") is not True
            or set(data.get("metrics_by_probe", {})) != set(PROBES)):
        raise ValueError("evaluation_contract_incompatible")

    hashes = data.get("model_files_sha256")
    expected = {f"{route.lower()}_{model}.joblib"
                for route in PROBES for model in ("iforest", "logistic")}
    if not isinstance(hashes, dict) or set(hashes) != expected:
        raise ValueError("model_inventory_incompatible")
    for name, digest in hashes.items():
        path = EVAL_DIR / name
        if (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
                or not _is_regular(path)
                or hashlib.sha256(path.read_bytes()).hexdigest() != digest):
            raise ValueError("model_digest_or_source_invalid")
    return data


def _load_models(route: str) -> dict:
    # Solo se permite abrir archivos cuyos nombres/hashes estan fijados por
    # verified_report(); nunca se acepta un path enviado por HTTP.
    import joblib
    from sklearn.ensemble import IsolationForest
    from sklearn.pipeline import Pipeline

    iso = joblib.load(EVAL_DIR / f"{route.lower()}_iforest.joblib")
    logistic = joblib.load(EVAL_DIR / f"{route.lower()}_logistic.joblib")
    if not isinstance(iso, IsolationForest) or not isinstance(logistic, Pipeline):
        raise ValueError("unexpected_model_types")
    return {"IsolationForest": iso, "LogisticRegression": logistic}


def _features(values: object) -> tuple[float, ...]:
    if (not isinstance(values, (tuple, list))
            or len(values) != len(FEATURES)):
        raise ValueError("missing_features")
    row = []
    for value in values:
        if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
            raise ValueError("nonfinite_or_negative_feature")
        row.append(float(value))
    if row[3] > 100:
        raise ValueError("loss_out_of_range")
    return tuple(row)


def _historical_rows(route: str, scenario: str) -> list[tuple[float, ...]]:
    if route not in PROBES or scenario not in SCENARIOS:
        raise ValueError("route_or_scenario_not_allowed")
    if scenario == "NORMAL":
        records = read_normal(NORMAL_TEST)
    else:
        # Valida integridad de TODOS los ciclos, sus tokens y watchdogs.
        final = read_event_batches(SOURCE_MANIFEST)[-1]
        sid = final[scenario.lower()]["session_id"]
        _, records = read_controlled(sid, scenario)
    return [_features(row) for row in records[route]]


def _score(row: tuple[float, ...], route: str,
           report: dict, models: dict) -> dict[str, str]:
    cutoff = report["metrics_by_probe"][route]["p95_training_rtt_ms"]
    if type(cutoff) not in (int, float) or not math.isfinite(cutoff) or cutoff < 0:
        raise ValueError("threshold_invalid")
    iso = int(models["IsolationForest"].predict([row])[0])
    logistic = int(models["LogisticRegression"].predict([row])[0])
    if iso not in (-1, 1) or logistic not in (0, 1):
        raise ValueError("prediction_out_of_contract")
    return {
        "P95_RTT": "DEGRADED" if row[0] > cutoff else "NORMAL",
        "IsolationForest": "DEGRADED" if iso == -1 else "NORMAL",
        "LogisticRegression": "DEGRADED" if logistic == 1 else "NORMAL",
    }


def _unknown(reason: str, *, route: str | None = None,
             scenario: str | None = None) -> dict:
    return {
        "schema": "NETLAB360_S06_045_INFERENCE_V1",
        "mode": MODE,
        "route": route,
        "scenario": scenario,
        "operational_state": "UNKNOWN",
        "binary_consensus": "UNKNOWN",
        "reason": reason,
        "predictions": None,
        "network_mutations_authorized": False,
        "production_deployment_authorized": False,
        "new_independent_validation": False,
    }


def infer(route: str, scenario: str, window_index: int) -> dict:
    """Inferir sobre muestra historica verificada, nunca telemetria en vivo."""
    if route not in PROBES or scenario not in SCENARIOS:
        return _unknown("UNSUPPORTED_ROUTE_OR_SCENARIO", route=route,
                        scenario=scenario)
    if type(window_index) is not int or not 1 <= window_index <= 20:
        return _unknown("INVALID_WINDOW_INDEX", route=route, scenario=scenario)
    try:
        report = verified_report()
        rows = _historical_rows(route, scenario)
        if window_index > len(rows):
            return _unknown("WINDOW_NOT_IN_VERIFIED_SESSION",
                            route=route, scenario=scenario)
        row = rows[window_index - 1]
        predictions = _score(row, route, report, _load_models(route))
    except (OSError, ValueError, KeyError, IndexError, TypeError,
            RuntimeError, ImportError, json.JSONDecodeError):
        return _unknown("UNVERIFIED_DATA_OR_MODEL",
                        route=route, scenario=scenario)

    unanimous = len(set(predictions.values())) == 1
    consensus = next(iter(predictions.values())) if unanimous else "UNKNOWN"
    operational = consensus if scenario != "RECOVERY" else "UNKNOWN"
    reason = ("RECOVERY_NOT_DISTINGUISHABLE_FROM_NORMAL"
              if scenario == "RECOVERY" else
              "MODEL_DISAGREEMENT" if not unanimous else "CONSENSUS_EXPLORATORY")
    return {
        "schema": "NETLAB360_S06_045_INFERENCE_V1",
        "mode": MODE,
        "route": route,
        "scenario": scenario,
        "window_index": window_index,
        "features": dict(zip(FEATURES, row)),
        "predictions": predictions,
        "binary_consensus": consensus,
        "operational_state": operational,
        "reason": reason,
        "explanation": {
            "observed_rtt_avg_ms": row[0],
            "p95_training_threshold_ms":
                report["metrics_by_probe"][route]["p95_training_rtt_ms"],
            "loss_pct": row[3],
            "not_calibrated_confidence": True,
        },
        "network_mutations_authorized": False,
        "production_deployment_authorized": False,
        "new_independent_validation": False,
    }



def infer_live(route: str) -> dict:
    """Inferencia de ventana ICMP RECIENTE, nunca entrenamiento ni ground truth."""
    mode = "FRESH_READONLY_EXPLORATORY"

    def unknown(reason: str) -> dict:
        return {**_unknown(reason, route=route), "mode": mode,
                "fresh_telemetry_verified": False,
                "ground_truth_label": "UNKNOWN",
                "model_generalization_demonstrated": False}

    if route not in PROBES:
        return unknown("UNSUPPORTED_ROUTE")
    try:
        fresh = read_latest()   # TTL, identidad, qdisc, salud NOC y calidad.
    except (ValueError, OSError, TypeError, KeyError, json.JSONDecodeError):
        return unknown("LIVE_TELEMETRY_MISSING_STALE_OR_INVALID")
    try:
        row = _features(fresh["features_by_route"][route])
        report = verified_report()
        predictions = _score(row, route, report, _load_models(route))
    except (ValueError, OSError, RuntimeError, ImportError,
            KeyError, IndexError, TypeError, json.JSONDecodeError):
        return unknown("UNVERIFIED_DATA_OR_MODEL")

    unanimous = len(set(predictions.values())) == 1
    binary = next(iter(predictions.values())) if unanimous else "UNKNOWN"
    # La qdisc basal no prueba ausencia universal de degradacion. Un resultado
    # anomalo requiere contrastar otras fuentes, no activar acciones de red.
    state = "NORMAL" if binary == "NORMAL" else "UNKNOWN"
    reason = ("BASELINE_AND_UNANIMOUS_NORMAL_SCOPED"
              if binary == "NORMAL" else
              "MODEL_DISAGREEMENT" if binary == "UNKNOWN" else
              "DEGRADATION_INDICATION_UNCONFIRMED")
    return {
        "schema": "NETLAB360_S06_046_FRESH_INFERENCE_V1",
        "mode": mode,
        "route": route,
        "observed_at_utc": fresh["collected_at_utc"],
        "age_seconds": round(fresh["age_seconds"], 3),
        "features": dict(zip(FEATURES, row)),
        "predictions": predictions,
        "binary_consensus": binary,
        "operational_state": state,
        "reason": reason,
        "fresh_telemetry_verified": True,
        "ground_truth_label": "UNKNOWN",
        "explanation": {
            "source": fresh["source"],
            "target": fresh["target"],
            "scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
            "rtt_avg_ms": row[0],
            "p95_training_threshold_ms":
                report["metrics_by_probe"][route]["p95_training_rtt_ms"],
            "loss_pct": row[3],
            "model_generalization_demonstrated": False,
            "confidence_calibrated": False,
        },
        "network_mutations_authorized": False,
        "production_deployment_authorized": False,
        "new_independent_validation": False,
        "model_generalization_demonstrated": False,
    }


def audit_errors() -> dict:
    """Reproducir FP/FN a nivel ventana y contrastarlos con S06-044."""
    report = verified_report()
    result = {}
    for route in PROBES:
        models = _load_models(route)
        by_class = {scenario: _historical_rows(route, scenario)
                    for scenario in SCENARIOS}
        if {k: len(v) for k, v in by_class.items()} != {
                "NORMAL": 20, "DEGRADED": 4, "RECOVERY": 6}:
            raise ValueError("audit_window_count_mismatch")
        route_summary = {}
        for model in MODEL_NAMES:
            fp = [i for i, row in enumerate(by_class["NORMAL"], 1)
                  if _score(row, route, report, models)[model] == "DEGRADED"]
            fn = [i for i, row in enumerate(by_class["DEGRADED"], 1)
                  if _score(row, route, report, models)[model] == "NORMAL"]
            fp_recovery = [
                i for i, row in enumerate(by_class["RECOVERY"], 1)
                if _score(row, route, report, models)[model] == "DEGRADED"
            ]
            recorded = report["metrics_by_probe"][route]["methods"][model]
            if (len(fp) != recorded["fp"] or len(fn) != recorded["fn"]
                    or len(fp_recovery) != recorded["recovery_false_alarms"]):
                raise ValueError("stored_metrics_differ_from_replay")
            route_summary[model] = {
                "false_positive_normal_windows": fp,
                "false_negative_degraded_windows": fn,
                "false_positive_recovery_windows": fp_recovery,
            }
        result[route] = route_summary
    return {
        "schema": "NETLAB360_S06_045_ERROR_AUDIT_V1",
        "mode": MODE,
        "routes": result,
        "derived_from_existing_test": True,
        "new_independent_validation": False,
        "changes_to_network": False,
    }


def make_app():
    """FastAPI opcional: la CI offline no necesita dependencias web."""
    from fastapi import FastAPI, Query

    app = FastAPI(title="NETLAB360 S06-045 (replay read-only)",
                  docs_url=None, redoc_url=None,
                  openapi_url=None)

    @app.get("/healthz")
    def healthz():
        return {"healthy": True, "mode": MODE,
                "production_deployment_authorized": False}

    @app.get("/api/v1/s06/live")
    def live(route: Literal["HQ_A_S1", "HQ_A_S2"] = "HQ_A_S1"):
        # GET solo lee ultimo snapshot reciente, nunca ejecuta ping ni writes.
        return infer_live(route)

    @app.get("/api/v1/s06/replay")
    def replay(route: Literal["HQ_A_S1", "HQ_A_S2"],
               scenario: Literal["NORMAL", "DEGRADED", "RECOVERY"],
               window_index: int = Query(ge=1, le=20)):
        return infer(route, scenario, window_index)

    @app.get("/api/v1/s06/error-audit")
    def errors():
        try:
            return audit_errors()
        except (OSError, ValueError, KeyError, TypeError, ImportError,
                RuntimeError, json.JSONDecodeError):
            return _unknown("UNVERIFIED_DATA_OR_MODEL")

    return app


def main():
    p = argparse.ArgumentParser(description=__doc__)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--audit", action="store_true")
    group.add_argument("--serve", action="store_true")
    args = p.parse_args()
    if args.audit:
        print(json.dumps(audit_errors(), ensure_ascii=False, indent=2))
        print("S06_045_ERROR_AUDIT=OK_REPLAY_ONLY")
    else:
        import uvicorn
        # Loopback obligado; puerto distinto del NOC S05 9130 y S08 9140.
        uvicorn.run(make_app(), host="127.0.0.1", port=9145,
                    workers=1, access_log=False)


if __name__ == "__main__":
    main()
