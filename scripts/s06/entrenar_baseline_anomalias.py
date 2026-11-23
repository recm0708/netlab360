#!/usr/bin/env python3
"""S06-041B: IsolationForest exploratorio sobre NORMAL verificado de HQ.

Tres sesiones DIFERENTES: 2 solo TRAIN, 1 solo TEST (por sesión completa).
No usa qdisc/estado/etiqueta como features; no inventa sensibilidad/recall
ni F1 porque no existen aún DEGRADACIONES productivas etiquetadas.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys

RAW = Path.home() / "netlab360-bootstrap/s06/datasets/raw"
MODELS = Path.home() / "netlab360-bootstrap/s06/modelos"
SESSION_RE = re.compile(r"^S06_WINDOW_NORMAL_\d{8}T\d{6}Z_[0-9a-f]{6}$")
SCHEMA = "NETLAB360_S06_WINDOWED_EGRESS_NORMAL_V1"
MODEL_SCHEMA = "NETLAB360_S06_NORMAL_IFOREST_EXPLORATORY_V1"
FEATURES = ("rtt_avg_ms", "rtt_p95_ms", "rtt_mdev_ms", "loss_pct")
PROBES = ("HQ_A_S1", "HQ_A_S2")


def read_session(session: str) -> dict[str, list[tuple[float, ...]]]:
    if not SESSION_RE.fullmatch(session):
        raise ValueError("Identificador de sesion no autorizado")
    directory = RAW / session
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Sesion no disponible")
    meta_path, data_path = directory / "metadata.json", directory / "ventanas.jsonl"
    for path in (meta_path, data_path):
        if path.is_symlink() or not path.is_file():
            raise ValueError("Archivo ausente o symlink")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
    if (meta.get("schema") != SCHEMA or meta.get("session_id") != session
            or meta.get("status") != "complete"
            or meta.get("data_digest_sha256") != digest
            or meta.get("mutating_action_executed") is not False
            or meta.get("stimulus") != "NONE"
            or meta.get("label_scope") != "HQ_CLIENT_EGRESS_NETWORK_STATE"
            or meta.get("training_ready") is not False):
        raise ValueError("Fuente no integra, parcial o diferente de NORMAL verificado")
    result = {name: [] for name in PROBES}
    seen = set()
    rows = [json.loads(line) for line in data_path.read_text().splitlines()
            if line.strip()]
    if len(rows) != meta.get("samples_recorded") or len(rows) != meta.get("verified"):
        raise ValueError("El total de ventanas no coincide con metadata")
    for row in rows:
        number = row.get("window_index")
        if (row.get("schema") != SCHEMA or row.get("session_id") != session
                or type(number) is not int or number < 1 or number in seen
                or row.get("ground_truth_label") != "NORMAL"
                or row.get("ground_truth_verified") is not True
                or row.get("qdisc_intervention_executed") is not False
                or row.get("label_scope") != "HQ_CLIENT_EGRESS_NETWORK_STATE"
                or row.get("before", {}).get("snapshot_valid") is not True
                or row.get("after", {}).get("snapshot_valid") is not True):
            raise ValueError("Ventana no verificada o inconsistente")
        seen.add(number)
        probes = row.get("measurements")
        if not isinstance(probes, list) or len(probes) != len(PROBES):
            raise ValueError("Mediciones ausentes o duplicadas")
        for probe in probes:
            identity = probe.get("probe_id")
            if identity not in result or len(result[identity]) >= len(rows):
                raise ValueError("Sonda no autorizada")
            values = probe.get("result")
            if not isinstance(values, dict) or values.get("measurement_valid") is not True:
                raise ValueError("Medicion no valida")
            features = []
            for feature in FEATURES:
                val = values.get(feature)
                if type(val) not in (int, float) or not math.isfinite(val) or val < 0:
                    raise ValueError("Feature ausente, infinita o negativa")
                features.append(float(val))
            result[identity].append(tuple(features))
    if seen != set(range(1, len(rows) + 1)) or any(
            len(values) != len(rows) for values in result.values()):
        raise ValueError("Ventanas o sondas repetidas/missing")
    if len(rows) < 10:
        raise ValueError("Se requieren al menos diez ventanas por sesion")
    return result


def percentile(values: list[float], pct: float) -> float:
    if not values:
        raise ValueError("Sin valores")
    seq = sorted(values)
    pos = (len(seq) - 1) * pct / 100
    low = math.floor(pos)
    high = math.ceil(pos)
    return float(seq[low] + (seq[high] - seq[low]) * (pos - low))


def predict_threshold(train: list[tuple[float, ...]],
                      test: list[tuple[float, ...]]) -> tuple[float, int]:
    cutoff = percentile([r[0] for r in train], 95)
    false_alarms = sum(x[0] > cutoff for x in test)
    return cutoff, false_alarms


def analyze(train_a: str, train_b: str, test_id: str) -> tuple[dict, dict]:
    if len({train_a, train_b, test_id}) != 3:
        raise ValueError("TRAIN y TEST deben ser tres sesiones distintas")
    a, b, t = (read_session(s) for s in (train_a, train_b, test_id))
    # Import tardio: GitHub CI unitaria no necesita el venv de ciencia de datos.
    try:
        from sklearn.ensemble import IsolationForest
        import joblib
    except ImportError as exc:
        raise RuntimeError("Usar el venv S06-S08 con scikit-learn y joblib") from exc

    models = {}
    metrics = {}
    for probe in PROBES:
        train_rows = a[probe] + b[probe]
        test_rows = t[probe]
        if len(train_rows) < 20 or len(test_rows) < 10:
            raise ValueError("Numero de observaciones insuficiente para esta demo")
        estimator = IsolationForest(
            n_estimators=100, contamination=0.05,
            max_samples=min(256, len(train_rows)), random_state=42,
            n_jobs=1
        )
        estimator.fit(train_rows)
        flags = estimator.predict(test_rows)  # -1: anomalia
        false_positive_count = sum(int(v == -1) for v in flags)
        cutoff, rule_false_positive_count = predict_threshold(train_rows, test_rows)
        if len(flags) != len(test_rows):
            raise RuntimeError("Modelo devolvio conteo inconsistente")
        metrics[probe] = {
            "train_samples": len(train_rows),
            "test_samples": len(test_rows),
            "iforest_false_positive_count_on_normal": false_positive_count,
            "iforest_false_positive_rate_on_normal": false_positive_count / len(test_rows),
            "rule_p95_training_rtt_ms": cutoff,
            "rule_false_positive_count_on_normal": rule_false_positive_count,
            "rule_false_positive_rate_on_normal": rule_false_positive_count / len(test_rows),
            "recall_degraded": None,
            "f1_degraded": None,
            "precision_degraded": None,
        }
        models[probe] = estimator
    return {
        "schema": MODEL_SCHEMA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "train_sessions": [train_a, train_b],
        "test_sessions": [test_id],
        "feature_names": list(FEATURES),
        "label_scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
        "trained_only_on": "NORMAL",
        "label_leakage_controls": "exclude_qdisc_status_label_and_session_id",
        "metrics": metrics,
        "training_ready_for_binary_classifier": False,
        "real_degraded_test_not_yet_available": True,
        "operational_deployment_authorized": False,
    }, models


def save(report: dict, models: dict) -> Path:
    import joblib
    folder = MODELS / ("S06_IFOREST_NORMAL_" +
                       datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                       + "_" + secrets.token_hex(3))
    folder.mkdir(mode=0o700, parents=True, exist_ok=False)
    files = {}
    for key in PROBES:
        name = key.lower() + ".joblib"
        path = folder / name
        joblib.dump(models[key], path)
        files[key] = {"filename": name,
                      "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    report["model_files"] = files
    (folder / "reporte_modelo.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    return folder


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--train-a", required=True)
    p.add_argument("--train-b", required=True)
    p.add_argument("--test", required=True)
    p.add_argument("--save", action="store_true")
    args = p.parse_args()
    os.umask(0o077)
    report, models = analyze(args.train_a, args.train_b, args.test)
    for name, scores in report["metrics"].items():
        print("S06_041_MODELO=" + name
              + " TRAIN=" + str(scores["train_samples"])
              + " TEST=" + str(scores["test_samples"])
              + " IF_FP_RATE=" + f"{scores['iforest_false_positive_rate_on_normal']:.3f}"
              + " RULE_FP_RATE=" + f"{scores['rule_false_positive_rate_on_normal']:.3f}")
    if args.save:
        print("S06_041_MODELOS_DIRECTORIO=" + str(save(report, models)))
    print("S06_041_MODELO_ETAPA=EXPLORATORIO_SOLO_NORMAL")
    print("S06_041_RECALL_F1_DEGRADED=NO_CALCULABLE")
    print("S06_041_BASELINE_ML=OK_SIN_AUTORIZACION_PRODUCTIVA")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError,
            json.JSONDecodeError) as exc:
        print("S06_041_MODELO_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
