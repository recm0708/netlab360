#!/usr/bin/env python3
"""S06-044: evaluar NORMAL vs DEGRADED del cliente HQ, sin tocar la red.

- Holdout por SESSION ID (no por filas); eventos degradados agrupados por token.
- Tres métodos por ruta: regla P95, IsolationForest y LogisticRegression.
- Estado RECOVERY se analiza SOLO como falsa alarma postevento.
- NO afirma extrapolación a otras fallas ni distinción multiclase por RTT.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from entrenar_baseline_anomalias import read_session as read_normal, FEATURES, PROBES

BASE = Path.home() / "netlab360-bootstrap/s06"
RAW = BASE / "datasets/raw"
OUT = BASE / "evaluaciones"
SOURCE_MANIFEST = BASE / "experimentos/S06_043_20261123T073108Z_344e1e/manifest.json"
NORMAL_A = "S06_WINDOW_NORMAL_20261123T063314Z_c84c9d"
NORMAL_B = "S06_WINDOW_NORMAL_20261123T063345Z_e45910"
NORMAL_TEST = "S06_WINDOW_NORMAL_20261123T063414Z_2b5732"
DEGRADED_INITIAL = "S06_WINDOW_DEGRADED_20261123T070344Z_984563"
RECOVERY_INITIAL = "S06_WINDOW_RECOVERY_20261123T070420Z_6c4e05"
WINDOW_SCHEMA = "NETLAB360_S06_HQ_CONTROLLED_WINDOWS_V1"
EVAL_SCHEMA = "NETLAB360_S06_044_BINARY_HOLDOUT_V1"
TARGET = "nl360-s02-h-hq-120/eth0"
ID_RE = re.compile(r"^S06_WINDOW_(DEGRADED|RECOVERY)_\d{8}T\d{6}Z_[a-f0-9]{6}$")
TOKEN_RE = re.compile(r"^[a-f0-9]{16}$")
CAPTURE = "S06_F06_Evaluacion_Binaria_Modelos_HQ"


def feature_row(values: dict) -> tuple[float, ...]:
    if not isinstance(values, dict) or values.get("measurement_valid") is not True:
        raise ValueError("measurement_not_valid")
    result = []
    for name in FEATURES:
        v = values.get(name)
        if type(v) not in (float, int) or not math.isfinite(v) or v < 0:
            raise ValueError("feature_invalid_" + name)
        result.append(float(v))
    return tuple(result)


def read_controlled(sid: str, expected: str) -> tuple[dict, dict[str, list[tuple[float, ...]]]]:
    if expected not in ("DEGRADED", "RECOVERY"):
        raise ValueError("invalid_expected_class")
    if not ID_RE.fullmatch(sid) or not sid.startswith("S06_WINDOW_" + expected + "_"):
        raise ValueError("unauthorized_session_id")
    folder = RAW / sid
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("source_folder_missing_or_symlink")
    mp, rp = folder / "metadata.json", folder / "ventanas.jsonl"
    if any(p.is_symlink() or not p.is_file() for p in (mp, rp)):
        raise ValueError("source_file_missing_or_symlink")
    metadata = json.loads(mp.read_text(encoding="utf-8"))
    raw = rp.read_bytes()
    if (metadata.get("schema") != WINDOW_SCHEMA
            or metadata.get("session_id") != sid
            or metadata.get("expected_class") != expected
            or metadata.get("status") != "complete"
            or metadata.get("training_ready") is not False
            or metadata.get("network_changes_by_collector") is not False
            or metadata.get("label_scope") != "HQ_CLIENT_EGRESS_NETWORK_STATE"
            or metadata.get("data_digest_sha256") != hashlib.sha256(raw).hexdigest()):
        raise ValueError("controlled_metadata_not_verified")
    token = metadata.get("controller_token")
    if not isinstance(token, str) or not TOKEN_RE.fullmatch(token):
        raise ValueError("missing_approved_event_token")
    records = [json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    length = len(records)
    if (not 2 <= length <= 15
            or metadata.get("samples_recorded") != length
            or metadata.get("verified") != length
            or metadata.get("unknown") != 0):
        raise ValueError("incomplete_controlled_session")
    features = {probe: [] for probe in PROBES}
    indexes = set()
    status = "APPLIED" if expected == "DEGRADED" else "RESTORED"
    qstate = "OWN_NETEM" if expected == "DEGRADED" else "BASELINE"
    for row in records:
        i = row.get("window_index")
        if (type(i) is not int or i in indexes
                or row.get("schema") != WINDOW_SCHEMA
                or row.get("session_id") != sid
                or row.get("ground_truth_label") != expected
                or row.get("ground_truth_verified") is not True
                or row.get("label_scope") != "HQ_CLIENT_EGRESS_NETWORK_STATE"
                or row.get("network_changes_by_collector") is not False):
            raise ValueError("unverified_labeled_row")
        indexes.add(i)
        for boundary in ("before", "after"):
            state = row.get(boundary, {}).get("guard", {})
            if (row.get(boundary, {}).get("routes_verified") is not True
                    or state.get("state") != status
                    or state.get("qdisc") != qstate
                    or state.get("token") != token
                    or state.get("target") != TARGET
                    or state.get("human_approval") is not True):
                raise ValueError("event_boundary_not_independently_verified")
            if (expected == "DEGRADED"
                    and (state.get("ground_truth_degraded_verified") is not True
                         or "applied_at_utc" not in state)):
                raise ValueError("degradation_not_armed")
            if (expected == "RECOVERY"
                    and ("expired_at_utc" not in state
                         or "applied_at_utc" not in state)):
                raise ValueError("recovery_not_real")
        probes = row.get("measurements")
        if (not isinstance(probes, list) or len(probes) != len(PROBES)
                or {v.get("probe_id") for v in probes} != set(PROBES)):
            raise ValueError("probes_missing_or_repeated")
        for item in probes:
            features[item["probe_id"]].append(feature_row(item.get("result")))
    if indexes != set(range(1, length + 1)):
        raise ValueError("window_sequence_invalid")
    return metadata, features


def read_event_batches(manifest_path: Path) -> list[dict]:
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("source_manifest_missing_or_symlink")
    if manifest_path != SOURCE_MANIFEST:
        raise ValueError("source_manifest_not_pinned")
    report = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (report.get("schema") != "NETLAB360_S06_043_REAL_HQ_BATCH_V1"
            or report.get("status") != "complete"
            or report.get("complete_cycles") != 3
            or report.get("planned_cycles") != 3
            or report.get("new_namespaces_created") is not False
            or report.get("new_interfaces_created") is not False
            or report.get("management_interface_mutated") is not False
            or report.get("target") != TARGET):
        raise ValueError("manifest_not_accepted")
    cycles = report.get("cycles")
    if not isinstance(cycles, list) or len(cycles) != 3:
        raise ValueError("events_count_not_three")
    seen_tokens = set()
    result = []
    for number, cycle in enumerate(cycles, 1):
        token = cycle.get("token")
        if (cycle.get("number") != number or cycle.get("status") != "complete"
                or not isinstance(token, str) or not TOKEN_RE.fullmatch(token)
                or token in seen_tokens):
            raise ValueError("cycle_unverified_or_duplicate")
        seen_tokens.add(token)
        wd = manifest_path.parent / f"ciclo_{number:02d}_watchdog.json"
        if wd.is_symlink() or not wd.is_file():
            raise ValueError("watchdog_evidence_missing")
        w = json.loads(wd.read_text(encoding="utf-8"))
        if (w.get("token") != token or w.get("state") != "RESTORED"
                or w.get("qdisc") != "BASELINE"
                or w.get("restoration_trigger") != "WATCHDOG"
                or w.get("final_qdisc_state") != "BASELINE"):
            raise ValueError("watchdog_not_autonomous")
        pair = {}
        for label in ("DEGRADED", "RECOVERY"):
            field = cycle.get(label.lower(), {})
            sid = field.get("session_id")
            if not isinstance(sid, str) or field.get("path") != str(RAW / sid):
                raise ValueError("event_path_not_raw")
            meta, vectors = read_controlled(sid, label)
            count = 4 if label == "DEGRADED" else 6
            if (meta.get("controller_token") != token
                    or field.get("windows") != count
                    or len(vectors[PROBES[0]]) != count
                    or field.get("measurement_count") != count * len(PROBES)
                    or field.get("digest_sha256") != meta.get("data_digest_sha256")):
                raise ValueError("event_integrity_mismatch")
            pair[label.lower()] = {"session_id": sid, "vectors": vectors}
        result.append({"number": number, "token": token, **pair})
    return result


def validate_split(normal_ids: tuple[str, ...], degraded_ids: tuple[str, ...],
                   test_normal: str, test_degraded: str) -> None:
    train = list(normal_ids) + list(degraded_ids)
    test = [test_normal, test_degraded]
    if len(set(train + test)) != len(train) + len(test):
        raise ValueError("session_overlap_train_test")
    if not all(s.startswith("S06_WINDOW_NORMAL_") for s in normal_ids + (test_normal,)):
        raise ValueError("normal_split_incorrect")
    if not all(s.startswith("S06_WINDOW_DEGRADED_") for s in degraded_ids + (test_degraded,)):
        raise ValueError("degraded_split_incorrect")


def confusion(y: list[int], pred: list[int]) -> dict:
    if len(y) != len(pred) or not y or set(y) != {0, 1}:
        raise ValueError("binary_test_labels_missing")
    if any(x not in (0, 1) for x in y + pred):
        raise ValueError("not_binary_predictions")
    tp = sum(a == 1 and b == 1 for a, b in zip(y, pred))
    fp = sum(a == 0 and b == 1 for a, b in zip(y, pred))
    tn = sum(a == 0 and b == 0 for a, b in zip(y, pred))
    fn = sum(a == 1 and b == 0 for a, b in zip(y, pred))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": precision, "recall": recall, "f1": f1,
            "specificity": specificity, "test_samples": len(y)}


def p95(data: list[tuple[float, ...]]) -> float:
    values = sorted(x[0] for x in data)
    if not values:
        raise ValueError("empty_training_baseline")
    k = (len(values) - 1) * 0.95
    lo, hi = math.floor(k), math.ceil(k)
    return values[lo] + (values[hi] - values[lo]) * (k - lo)


def evaluate() -> tuple[dict, dict]:
    cycles = read_event_batches(SOURCE_MANIFEST)
    train_n = (NORMAL_A, NORMAL_B)
    test_n = NORMAL_TEST
    train_d = (DEGRADED_INITIAL, cycles[0]["degraded"]["session_id"],
               cycles[1]["degraded"]["session_id"])
    test_d = cycles[2]["degraded"]["session_id"]
    train_r = (RECOVERY_INITIAL, cycles[0]["recovery"]["session_id"],
               cycles[1]["recovery"]["session_id"])
    test_r = cycles[2]["recovery"]["session_id"]
    validate_split(train_n, train_d, test_n, test_d)
    if len(set(train_r + (test_r,))) != 4:
        raise ValueError("recovery_session_overlap")
    normal = {s: read_normal(s) for s in (*train_n, test_n)}
    degraded = {s: read_controlled(s, "DEGRADED")[1]
                for s in (*train_d, test_d)}
    recovered = {s: read_controlled(s, "RECOVERY")[1] for s in (*train_r, test_r)}
    if read_controlled(DEGRADED_INITIAL, "DEGRADED")[0]["controller_token"] != (
        read_controlled(RECOVERY_INITIAL, "RECOVERY")[0]["controller_token"]
    ):
        raise ValueError("initial_event_pair_token_not_identical")
    # Train/test separated by full sessions, even when two probes are correlated.
    # NO global chronological split: NORMAL test was captured before D training.
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("sklearn_missing_use_s06_python_env") from exc

    metrics, models = {}, {}
    for probe in PROBES:
        n_train = [item for session in train_n for item in normal[session][probe]]
        d_train = [item for session in train_d for item in degraded[session][probe]]
        n_test = normal[test_n][probe]
        d_test = degraded[test_d][probe]
        r_test = recovered[test_r][probe]
        if (len(n_train) != 40 or len(d_train) != 12
                or len(n_test) != 20 or len(d_test) != 4 or len(r_test) != 6):
            raise ValueError("expected_window_count_mismatch")
        truth = [0] * len(n_test) + [1] * len(d_test)
        test = n_test + d_test
        cutoff = p95(n_train)
        iso = IsolationForest(n_estimators=100, contamination=0.05,
                              random_state=42, n_jobs=1)
        iso.fit(n_train)
        clf = Pipeline([
            ("scale", StandardScaler()),
            ("logistic", LogisticRegression(
                class_weight="balanced", max_iter=1500, random_state=42
            )),
        ])
        clf.fit(n_train + d_train, [0] * len(n_train) + [1] * len(d_train))
        methods = {
            "P95_RTT": lambda rows: [int(x[0] > cutoff) for x in rows],
            "IsolationForest": lambda rows: [int(x == -1) for x in iso.predict(rows)],
            "LogisticRegression": lambda rows: [int(x) for x in clf.predict(rows)],
        }
        scored = {}
        for name, predict in methods.items():
            stats = confusion(truth, predict(test))
            rflags = predict(r_test)
            stats["recovery_false_alarms"] = sum(rflags)
            stats["recovery_test_samples"] = len(r_test)
            stats["recovery_false_alarm_rate"] = sum(rflags) / len(r_test)
            stats["classifier_type"] = ("unsupervised" if name == "IsolationForest"
                                        else "supervised" if name == "LogisticRegression"
                                        else "rule_based")
            scored[name] = stats
        metrics[probe] = {
            "train_normal_windows": len(n_train),
            "train_degraded_windows": len(d_train),
            "test_normal_windows": len(n_test),
            "test_degraded_windows": len(d_test),
            "test_recovery_windows": len(r_test),
            "p95_training_rtt_ms": cutoff,
            "methods": scored,
        }
        models[probe] = {"iforest": iso, "logistic": clf}
    report = {
        "schema": EVAL_SCHEMA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "dataset_scope": "HQ_CLIENT_EGRESS_NETWORK_STATE",
        "task": "binary_degradation_detection",
        "positive_label": "DEGRADED",
        "negative_label": "NORMAL",
        "train_normal_sessions": list(train_n),
        "train_degraded_sessions": list(train_d),
        "test_normal_sessions": [test_n],
        "test_degraded_sessions": [test_d],
        "test_recovery_sessions": [test_r],
        "recovery_not_used_for_binary_training": True,
        "split_strategy": "group_by_complete_session_and_event_token",
        "globally_chronological_holdout": False,
        "features": list(FEATURES),
        "excluded_features": [
            "qdisc", "guard_state", "controller_token", "event_timestamp",
            "ground_truth_label", "session_id",
        ],
        "metrics_by_probe": metrics,
        "limitations": [
            "four_positive_windows_per_probe_in_test",
            "two_routes_correlated_by_same_event",
            "single_fixed_40ms_latency_scenario",
            "normal_test_observed_before_degraded_train_no_global_time_holdout",
            "not_validated_for_ospf_wan_loss_other_incidents",
            "recovery_state_indistinguishable_from_normal_using_rtt_alone",
        ],
        "production_deployment_authorized": False,
        "s07_mutating_actions_authorized": False,
        "evaluation_exploratory": True,
    }
    return report, models


def capture_text(report: dict) -> str:
    lines = [
        f"========== INICIO CAPTURA {CAPTURE} ==========",
        "S06-044 | DETECCION BINARIA NORMAL VS DEGRADED (CLIENTE REAL HQ)",
        "SPLIT=POR_SESIONES_Y_EVENTOS_SIN_MEZCLAR",
        "TRAIN_NORMAL=40 TRAIN_DEGRADED=12 POR_RUTA",
        "TEST_NORMAL=20 TEST_DEGRADED=4 POR_RUTA",
        "RECOVERY_TEST=6 POR_RUTA (ANALISIS_POSINCIDENTE)",
    ]
    for probe in PROBES:
        vals = report["metrics_by_probe"][probe]
        for model in ("P95_RTT", "IsolationForest", "LogisticRegression"):
            m = vals["methods"][model]
            lines.append(
                f"RUTA={probe} MODELO={model} "
                f"TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']} "
                f"P={m['precision']:.3f} R={m['recall']:.3f} "
                f"F1={m['f1']:.3f} FA_RECOVERY={m['recovery_false_alarms']}/6"
            )
    lines += [
        "TEST_POSITIVOS=4_POR_RUTA (EVALUACION_EXPLORATORIA)",
        "GLOBAL_TIME_HOLDOUT=NO",
        "GENERALIZACION_A_OTRAS_FALLAS=NO_DEMOSTRADA",
        "CAMBIOS_RED=NINGUNO",
        f"========== FIN CAPTURA {CAPTURE} ==========",
    ]
    return "\n".join(lines) + "\n"


def persist(report: dict, models: dict) -> Path:
    import joblib
    out = OUT / ("S06_044_" +
                 datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                 + "_" + secrets.token_hex(3))
    out.mkdir(parents=True, mode=0o700, exist_ok=False)
    records = {}
    for probe in PROBES:
        for model in ("iforest", "logistic"):
            fname = probe.lower() + "_" + model + ".joblib"
            p = out / fname
            joblib.dump(models[probe][model], p)
            records[fname] = hashlib.sha256(p.read_bytes()).hexdigest()
    report["model_files_sha256"] = records
    (out / "evaluacion.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    evidence = out / (CAPTURE + ".txt")
    evidence.write_text(capture_text(report), encoding="utf-8")
    evidence.chmod(0o600)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    report, models = evaluate()
    print("S06_044_DATASET_SPLIT=GRUPOS_INDEPENDIENTES")
    for probe in PROBES:
        for name, m in report["metrics_by_probe"][probe]["methods"].items():
            print(f"S06_044_RUTA={probe} MODELO={name} "
                  f"TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']} "
                  f"PRECISION={m['precision']:.3f} RECALL={m['recall']:.3f} "
                  f"F1={m['f1']:.3f} RECOVERY_FP={m['recovery_false_alarms']}/6")
    if args.save:
        folder = persist(report, models)
        print("S06_044_EVALUACION_DIRECTORIO=" + str(folder))
        print("S06_044_CAPTURA_F06=" + str(folder / (CAPTURE + ".txt")))
    print("S06_044_PRODUCCION_AUTORIZADA=NO")
    print("S06_044_EVALUACION_BINARIA=OK_EXPLORATORIA")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError,
            TypeError, json.JSONDecodeError) as exc:
        print("S06_044_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
