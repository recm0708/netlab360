#!/usr/bin/env python3
"""S06-051: inventario read-only del protocolo ICMP por sesión y partición.

No ejecuta ping, no toca redes ni reentrena; no transforma ventanas históricas
en un TEST nuevo. Mantiene intacta el acta S06-050 bloqueada.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import secrets
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from evaluar_deteccion_binaria import (
    RAW, PROBES, NORMAL_A, NORMAL_B, NORMAL_TEST,
    DEGRADED_INITIAL, RECOVERY_INITIAL, SOURCE_MANIFEST,
    read_event_batches, read_controlled, read_normal,
)
from inferencia_hq_readonly import verified_report
from prerregistrar_estudio_futuro import (
    FREEZE, SCHEMA as FREEZE_SCHEMA, read_regular,
    compare_frozen, build as current_freeze,
)

ROOT = Path.home() / "netlab360-bootstrap/s06/auditorias-muestreo"
SCHEMA = "NETLAB360_S06_051_PROTOCOL_MIX_AUDIT_V1"
EXPECTED_TOTAL = {"NORMAL": 60, "DEGRADED": 16, "RECOVERY": 24}
ROLES = ("TRAIN", "TEST", "RECOVERY_ANALYSIS", "HISTORICAL_OTHER")


def verified_freeze() -> dict:
    frozen = json.loads(read_regular(FREEZE))
    if frozen.get("schema") != FREEZE_SCHEMA:
        raise ValueError("freeze_schema_invalid")
    compare_frozen(frozen, current_freeze())
    if (frozen.get("status") != "BLOCKED_INCOMPATIBLE_SAMPLING"
            or frozen.get("historical_packet_counts") != [2, 3]
            or frozen.get("models_retrained") is not False
            or frozen.get("new_prospective_test_completed") is not False):
        raise ValueError("frozen_gate_different_from_s06_050")
    return frozen


def session_catalog(report: dict, cycles: list[dict]) -> list[tuple[str, str, str]]:
    normal = [NORMAL_A, NORMAL_B, NORMAL_TEST]
    controlled = {
        "DEGRADED": [DEGRADED_INITIAL]
                    + [c["degraded"]["session_id"] for c in cycles],
        "RECOVERY": [RECOVERY_INITIAL]
                    + [c["recovery"]["session_id"] for c in cycles],
    }
    result = []
    for session in normal:
        role = "TRAIN" if session in report["train_normal_sessions"] else "TEST"
        if role == "TEST" and session not in report["test_normal_sessions"]:
            raise ValueError("unrecognized_normal_test")
        result.append((session, "NORMAL", role))
    for label, sessions in controlled.items():
        for session in sessions:
            if label == "DEGRADED":
                role = ("TRAIN" if session in report["train_degraded_sessions"]
                        else "TEST" if session in report["test_degraded_sessions"]
                        else "HISTORICAL_OTHER")
                if role == "HISTORICAL_OTHER":
                    raise ValueError("unrecognized_degraded_training_split")
            else:
                role = ("RECOVERY_ANALYSIS"
                        if session in report["test_recovery_sessions"]
                        else "HISTORICAL_OTHER")
            result.append((session, label, role))
    expected = set(report["train_normal_sessions"] +
                   report["train_degraded_sessions"] +
                   report["test_normal_sessions"] +
                   report["test_degraded_sessions"] +
                   report["test_recovery_sessions"])
    if len({sid for sid, _, _ in result}) != len(result) or not expected.issubset(
            {sid for sid, _, _ in result}):
        raise ValueError("duplicate_or_missing_split_session")
    if len(result) != 11:
        raise ValueError("historical_session_count_not_11")
    return result


def inspect_session(session: str, label: str, role: str) -> dict:
    if label not in EXPECTED_TOTAL or role not in ROLES:
        raise ValueError("unsupported_class_or_role")
    # Los lectores oficiales verifican etiquetas externas, integridad y
    # control root/watchdog antes de inspeccionar el protocolo de ICMP.
    if label == "NORMAL":
        features = read_normal(session)
    else:
        _, features = read_controlled(session, label)
    if set(features) != set(PROBES):
        raise ValueError("verified_feature_probe_scope_invalid")
    base = RAW / session
    if base.is_symlink() or not base.is_dir():
        raise ValueError("session_folder_invalid")
    meta = json.loads(read_regular(base / "metadata.json"))
    raw = read_regular(base / "ventanas.jsonl", limit=2000000)
    if meta.get("session_id") != session or meta.get("status") != "complete":
        raise ValueError("session_metadata_invalid")
    packets = (meta.get("packet_count_per_probe") if label == "NORMAL"
               else meta.get("packets"))
    if type(packets) is not int or not 2 <= packets <= 6:
        raise ValueError("metadata_packets_invalid")
    lines = [json.loads(row) for row in raw.decode("utf-8").splitlines()
             if row.strip()]
    if not lines or len(lines) != len(features[PROBES[0]]):
        raise ValueError("session_rows_count_invalid")
    effective = Counter()
    missing = 0
    for index, record in enumerate(lines, 1):
        if (record.get("session_id") != session
                or record.get("window_index") != index
                or record.get("ground_truth_label") != label
                or record.get("ground_truth_verified") is not True):
            raise ValueError("session_row_not_verified")
        measurements = record.get("measurements")
        if (not isinstance(measurements, list)
                or len(measurements) != len(PROBES)
                or {x.get("probe_id") for x in measurements} != set(PROBES)):
            raise ValueError("measurement_probe_scope_invalid")
        for m in measurements:
            result = m.get("result")
            if (m.get("kind") != "icmp"
                    or m.get("requested_packets") != packets
                    or not isinstance(result, dict)
                    or result.get("measurement_valid") is not True
                    or result.get("sent") != packets):
                raise ValueError("actual_packets_disagree_with_metadata")
            if (type(result.get("received")) is not int
                    or not 0 <= result["received"] <= packets):
                raise ValueError("received_packets_invalid")
            if result["received"] < packets:
                missing += 1
            effective[(m["probe_id"], packets)] += 1
    for route in PROBES:
        if effective[(route, packets)] != len(lines):
            raise ValueError("per_probe_count_not_consistent")
    return {
        "session_id": session,
        "class": label,
        "split_role": role,
        "windows_per_route": len(lines),
        "packets_per_window": packets,
        "transmissions_per_route": packets * len(lines),
        "packets_metadata_matches_actual": True,
        "measurements_with_packet_loss": missing,
    }


def summarize(records: list[dict]) -> dict:
    if not isinstance(records, list) or len(records) != 11:
        raise ValueError("session_inventory_count_invalid")
    tally = defaultdict(Counter)
    by_role = defaultdict(Counter)
    totals = Counter()
    for row in records:
        label, role = row["class"], row["split_role"]
        packets = row["packets_per_window"]
        windows = row["windows_per_route"]
        if (label not in EXPECTED_TOTAL or role not in ROLES
                or type(packets) is not int or not 2 <= packets <= 6
                or type(windows) is not int or windows < 1):
            raise ValueError("invalid_aggregate_session")
        tally[label][packets] += windows
        by_role[role][packets] += windows
        totals[label] += windows
    if dict(totals) != EXPECTED_TOTAL:
        raise ValueError("window_inventory_mismatch")
    all_counts = sorted({p for r in records for p in [r["packets_per_window"]]})
    if all_counts != [2, 3]:
        raise ValueError("frozen_packet_protocol_changed")
    by_class = {k: {str(p): v for p, v in sorted(tally[k].items())}
                for k in EXPECTED_TOTAL}
    by_split = {role: {str(p): v for p, v in sorted(by_role[role].items())}
                for role in ROLES}
    normal_sizes = set(tally["NORMAL"])
    degraded_sizes = set(tally["DEGRADED"])
    return {
        "schema": SCHEMA,
        "routes": list(PROBES),
        "windows_total_by_class_per_route": dict(totals),
        "packet_sizes_observed": all_counts,
        "windows_by_class_and_packet_size": by_class,
        "windows_by_split_and_packet_size": by_split,
        "class_packet_sizes_disjoint": normal_sizes.isdisjoint(degraded_sizes),
        "potential_protocol_class_confound": (
            "HIGH_IF_PACKET_SIZES_DISJOINT" if normal_sizes.isdisjoint(degraded_sizes)
            else "POSSIBLE_SAMPLING_BIAS_REQUIRES_CONTROL"),
        "methodological_decision": "KEEP_PREREGISTRATION_BLOCKED",
        "next_gate": "INDEPENDENT_COMPARABILITY_PROTOCOL_BEFORE_NEW_LABELED_TEST",
        "new_test_performed": False,
        "models_retrained": False,
        "existing_models_rescored": False,
        "network_mutations_executed": False,
    }


def audit() -> dict:
    verified_freeze()
    report = verified_report()
    cycles = read_event_batches(SOURCE_MANIFEST)
    rows = [inspect_session(*item) for item in session_catalog(report, cycles)]
    result = summarize(rows)
    result["session_inventory"] = rows
    return result


def persist(report: dict) -> Path:
    if ROOT.is_symlink():
        raise ValueError("output_folder_symlink")
    ROOT.mkdir(mode=0o700, parents=True, exist_ok=True)
    if ROOT.stat().st_uid != os.geteuid() or ROOT.stat().st_mode & 0o077:
        raise ValueError("output_folder_not_private")
    folder = ROOT / ("S06_051_" +
                     datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                     + "_" + secrets.token_hex(3))
    folder.mkdir(mode=0o700)
    file = folder / "auditoria-muestreo.json"
    with file.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    file.chmod(0o600)
    return file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", action="store_true")
    options = parser.parse_args()
    os.umask(0o077)
    report = audit()
    print("========== S06-051 AUDITORIA MUESTREO ORIGINAL ==========")
    for row in report["session_inventory"]:
        print(f"SESION={row['session_id']} CLASE={row['class']} "
              f"SPLIT={row['split_role']} PAQUETES={row['packets_per_window']} "
              f"VENTANAS={row['windows_per_route']} "
              f"CONTROL_PAQUETES=OK")
    for label, values in report["windows_by_class_and_packet_size"].items():
        for count, windows in values.items():
            print(f"CLASE={label} PAQUETES={count} VENTANAS_POR_RUTA={windows}")
    for role, values in report["windows_by_split_and_packet_size"].items():
        for count, windows in values.items():
            print(f"SPLIT={role} PAQUETES={count} VENTANAS_POR_RUTA={windows}")
    print("POSIBLE_CONFUSION_CLASE_MUESTREO=" +
          report["potential_protocol_class_confound"])
    print("ACTA_S06_050=CONSERVADA_BLOQUEADA")
    print("MODELOS=NO_REENTRENADOS_NI_REPUNTUADOS")
    print("TEST_NUEVO=NO")
    print("CAMBIOS_RED=NINGUNO")
    print("GATE_S06_051=" + report["next_gate"])
    if options.save:
        print("S06_051_REPORTE=" + str(persist(report)))
    print("S06_051_AUDITORIA_READONLY=OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, KeyError,
            TypeError, json.JSONDecodeError) as exc:
        print("S06_051_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
