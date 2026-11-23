#!/usr/bin/env python3
"""S06-046: una observacion ICMP actual HQ→S1/S2, sin cambios de red.

La captura es una medicion activa acotada (3 paquetes por ruta). Ningun
resultado se declara ground truth de degradacion: la etiqueta es UNKNOWN.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import secrets
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from capturar_ventanas_normales import evidence_snapshot, PROBES
from capturar_ventanas_controladas import read_guard
from medir_rendimiento import measure_ping, preflight
from evaluar_deteccion_binaria import FEATURES

ROOT = Path.home() / "netlab360-bootstrap/s06/telemetria-hq-live"
LATEST = ROOT / "ultima.json"
SCHEMA = "NETLAB360_S06_046_HQ_FRESH_TELEMETRY_V1"
MAX_AGE_SECONDS = 30
MAX_PAYLOAD_BYTES = 32768
SOURCE = "NETLAB360_REAL_HQ_TO_S1_S2"
TARGET = "nl360-s02-h-hq-120/eth0"
PROBE_TARGETS = {name: {"namespace": ns, "ip": ip}
                 for name, ns, ip in PROBES}


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _stamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp_missing")
    try:
        dt = datetime.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("timestamp_invalid") from exc
    if dt.tzinfo is None:
        raise ValueError("timestamp_without_timezone")
    return dt.astimezone(timezone.utc)


def age_seconds(value: object, now: datetime | None = None) -> float:
    t = now if now is not None else datetime.now(timezone.utc)
    if t.tzinfo is None:
        raise ValueError("now_must_be_aware")
    return (t.astimezone(timezone.utc) - _stamp(value)).total_seconds()


def guard_ok(data: object) -> bool:
    return (isinstance(data, dict)
            and data.get("schema") == "NETLAB360_S06_HQ_EXPERIMENT_GUARD_V1"
            and data.get("state") == "NONE"
            and data.get("qdisc") == "BASELINE"
            and data.get("target") == TARGET)


def boundary_ok(data: object) -> bool:
    return (isinstance(data, dict)
            and data.get("snapshot_valid") is True
            and data.get("qdisc_state") == "CANDIDATE_NOQUEUE"
            and data.get("noc_healthy") is True
            and isinstance(data.get("routes_ok"), dict)
            and set(data["routes_ok"]) == set(PROBE_TARGETS)
            and all(value is True for value in data["routes_ok"].values()))


def validate_snapshot(data: object, *, now: datetime | None = None) -> dict:
    """Fail closed ante antiguedad, corrupcion, cambios de red o calidad."""
    if not isinstance(data, dict):
        raise ValueError("snapshot_not_object")
    if (data.get("schema") != SCHEMA
            or data.get("source") != SOURCE
            or data.get("target") != TARGET
            or data.get("network_mutations_executed") is not False
            or data.get("ground_truth_label") != "UNKNOWN"
            or data.get("ground_truth_verified") is not False
            or data.get("packets_per_probe") != 3):
        raise ValueError("snapshot_contract_mismatch")

    age = age_seconds(data.get("collected_at_utc"), now)
    if not -2 <= age <= MAX_AGE_SECONDS:
        raise ValueError("snapshot_stale_or_future")

    started = _stamp(data.get("started_at_utc"))
    ended = _stamp(data["collected_at_utc"])
    if not 0 <= (ended - started).total_seconds() <= 25:
        raise ValueError("collection_duration_invalid")
    if not (guard_ok(data.get("guard_before"))
            and guard_ok(data.get("guard_after"))
            and boundary_ok(data.get("before"))
            and boundary_ok(data.get("after"))):
        raise ValueError("baseline_boundaries_not_verified")
    measurements = data.get("measurements")
    if not isinstance(measurements, list) or len(measurements) != len(PROBE_TARGETS):
        raise ValueError("missing_or_extra_probes")
    if {m.get("probe_id") for m in measurements if isinstance(m, dict)} != set(PROBE_TARGETS):
        raise ValueError("probe_identity_mismatch")

    clean = {}
    for item in measurements:
        identity = item["probe_id"]
        expected = PROBE_TARGETS[identity]
        if (item.get("source_namespace") != expected["namespace"]
                or item.get("destination_ip") != expected["ip"]
                or item.get("kind") != "icmp"
                or item.get("requested_packets") != 3):
            raise ValueError("non_allowlisted_measurement")
        if not 0 <= age_seconds(item.get("recorded_at_utc"), now) <= MAX_AGE_SECONDS:
            raise ValueError("probe_stale")
        result = item.get("result")
        if not isinstance(result, dict) or result.get("measurement_valid") is not True:
            raise ValueError("measurement_incomplete")
        if result.get("sent") != 3 or result.get("received") != 3:
            raise ValueError("packet_loss_outside_trained_scope")
        features = []
        for key in FEATURES:
            value = result.get(key)
            if type(value) not in (int, float):
                raise ValueError("feature_type_invalid")
            import math
            if not math.isfinite(value) or value < 0:
                raise ValueError("feature_nonfinite")
            features.append(float(value))
        if features[3] != 0:
            raise ValueError("packet_loss_outside_trained_scope")
        clean[identity] = tuple(features)
    return {"collected_at_utc": data["collected_at_utc"],
            "age_seconds": age, "features_by_route": clean,
            "source": SOURCE, "target": TARGET}


def read_latest(*, now: datetime | None = None) -> dict:
    if LATEST.is_symlink() or not LATEST.is_file():
        raise ValueError("live_snapshot_missing")
    stat = LATEST.stat()
    if stat.st_size > MAX_PAYLOAD_BYTES or stat.st_size == 0:
        raise ValueError("live_snapshot_size_invalid")
    if stat.st_uid != os.geteuid() or (stat.st_mode & 0o077):
        raise ValueError("live_snapshot_permissions_invalid")
    data = json.loads(LATEST.read_text(encoding="utf-8"))
    return validate_snapshot(data, now=now)


def capture_once() -> dict:
    if os.geteuid() == 0:
        raise RuntimeError("collector_must_run_unprivileged")
    # Preflight ya existente protege gestion, topologia y health NOC.
    preflight()
    begin = utc()
    before, guard_before = evidence_snapshot(), read_guard()
    if not boundary_ok(before) or not guard_ok(guard_before):
        raise RuntimeError("baseline_precondition_not_verified")
    measures = [measure_ping(probe, 3) for probe in PROBES]
    after, guard_after = evidence_snapshot(), read_guard()
    result = {
        "schema": SCHEMA,
        "source": SOURCE,
        "target": TARGET,
        "started_at_utc": begin,
        "collected_at_utc": utc(),
        "packets_per_probe": 3,
        "before": before, "guard_before": guard_before,
        "measurements": measures,
        "after": after, "guard_after": guard_after,
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "network_mutations_executed": False,
    }
    validate_snapshot(result)
    return result


def persist_snapshot(snapshot: dict) -> Path:
    validate_snapshot(snapshot)
    if ROOT.is_symlink():
        raise ValueError("snapshot_directory_symlink")
    ROOT.mkdir(parents=True, mode=0o700, exist_ok=True)
    if ROOT.stat().st_uid != os.geteuid() or ROOT.stat().st_mode & 0o077:
        raise ValueError("snapshot_directory_not_private")
    if LATEST.is_symlink():
        raise ValueError("latest_symlink_forbidden")

    ident = (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
             + "_" + secrets.token_hex(4))
    archive = ROOT / ("S06_046_HQ_" + ident + ".json")
    serialized = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    if len(serialized.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise ValueError("snapshot_too_large")
    with archive.open("x", encoding="utf-8") as f:
        f.write(serialized)
    archive.chmod(0o600)
    tmp = ROOT / (".latest-" + secrets.token_hex(4))
    try:
        with tmp.open("x", encoding="utf-8") as f:
            f.write(serialized)
        tmp.chmod(0o600)
        os.replace(tmp, LATEST)
    finally:
        tmp.unlink(missing_ok=True)
    return archive


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--collect", action="store_true", required=True)
    opts = args.parse_args()
    os.umask(0o077)
    data = capture_once()
    archive = persist_snapshot(data)
    print("S06_046_ARCHIVO=" + str(archive))
    print("S06_046_ULTIMA=" + str(LATEST))
    print("S06_046_RUTAS=HQ_A_S1,HQ_A_S2")
    print("S06_046_PAQUETES=3_POR_RUTA")
    print("S06_046_GROUND_TRUTH=UNKNOWN")
    print("S06_046_INFRAESTRUCTURA_MUTADA=NO")
    print("S06_046_CAPTURA_RECIENTE=OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
        print("S06_046_ERROR=" + type(exc).__name__ + ": " + str(exc),
              file=sys.stderr)
        sys.exit(1)
