#!/usr/bin/env python3
"""S06: consolidacion auditable de sesiones reales, sin alterar originales.

Normaliza series de Prometheus y medidas ICMP/HTTP a registros largos
tipados con procedencia, unidades y tiempos UTC. No atribuye ground truth,
no crea train/test ni ejecuta scripts de red.
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

ROOT = Path.home() / "netlab360-bootstrap/s06/datasets"
SCHEMA = "NETLAB360_S06_CURATED_V1"
BASE_ID = re.compile(r"^S06_BASELINE_\d{8}T\d{6}Z_[0-9a-f]{6}$")
PERF_ID = re.compile(r"^S06_PERF_\d{8}T\d{6}Z_[0-9a-f]{6}$")
S04_NAMES = {
    "netlab360_s04_router_running",
    "netlab360_s04_source_up",
    "netlab360_s04_topology_mode",
    "netlab360_s04_vlan_admin_up",
    "netlab360_s04_wan_admin_up",
}
ICMP_UNITS = {
    "sent": "packets",
    "received": "packets",
    "loss_pct": "percent",
    "rtt_min_ms": "ms",
    "rtt_avg_ms": "ms",
    "rtt_max_ms": "ms",
    "rtt_mdev_ms": "ms",
    "rtt_p95_ms": "ms",
}
HTTP_UNITS = {"elapsed_ms": "ms"}


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def parse_utc(s: str) -> datetime:
    if not isinstance(s, str):
        raise ValueError("Marca temporal sin texto")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("Marca temporal no incluye zona UTC")
    if dt.utcoffset().total_seconds() != 0:
        raise ValueError("Marca temporal no UTC")
    return dt.astimezone(timezone.utc)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_dir(session: str, pattern: re.Pattern) -> Path:
    if not pattern.fullmatch(session):
        raise ValueError("Identificador de sesion no permitido")
    base = ROOT / "raw"
    folder = base / session
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Sesion ausente o symlink")
    return folder


def load_session(session: str, pattern: re.Pattern,
                 schema: str, filename: str, checksum_key: str) -> tuple[dict, list[dict]]:
    directory = safe_dir(session, pattern)
    meta_file = directory / "metadata.json"
    data_file = directory / filename
    if (not meta_file.is_file() or not data_file.is_file()
            or meta_file.is_symlink() or data_file.is_symlink()):
        raise ValueError("Datos o metadatos originales ausentes/symlink")
    metadata = json.loads(meta_file.read_text(encoding="utf-8"))
    if (metadata.get("schema") != schema
            or metadata.get("session_id") != session
            or metadata.get("status") != "complete"
            or metadata.get("ground_truth_label") != "UNKNOWN"
            or metadata.get("ground_truth_verified") is not False):
        raise ValueError("Metadatos de sesion no aprobados")
    data = data_file.read_bytes()
    if sha(data) != metadata.get(checksum_key):
        raise ValueError("Checksum original distinto al registrado")
    lines = data.decode("utf-8").splitlines()
    expected = metadata.get("samples_complete", metadata.get("samples_recorded"))
    if not lines or not isinstance(expected, int) or len(lines) != expected:
        raise ValueError("Cantidad de muestras originales incoherente")
    records = [json.loads(x) for x in lines]
    for n, record in enumerate(records, 1):
        if (record.get("session_id") != session
                or record.get("sample_index") != n
                or record.get("schema") != schema
                or record.get("ground_truth_label") != "UNKNOWN"
                or record.get("ground_truth_verified") is not False):
            raise ValueError(f"Muestra original invalida en posicion {n}")
        timestamp = record.get("recorded_at_utc")
        parse_utc(timestamp)
    if any(
        parse_utc(records[i]["recorded_at_utc"])
        > parse_utc(records[i + 1]["recorded_at_utc"])
        for i in range(len(records) - 1)
    ):
        raise ValueError("Muestras no ordenadas cronologicamente")
    return metadata, records


def as_number(value: object, *, allow_missing: bool = False) -> float | None:
    if value is None and allow_missing:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Valor no numerico")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Valor no finito")
    return number


def long_row(*, source: str, session: str, idx: int,
             observed: str, acquired: str, name: str, value: object,
             unit: str, context: dict, allow_missing: bool = False) -> dict:
    return {
        "schema": SCHEMA, "source": source, "session_id": session,
        "sample_index": idx, "observed_at_utc": observed,
        "captured_at_utc": acquired, "signal": name,
        "value": as_number(value, allow_missing=allow_missing),
        "unit": unit, "context": context,
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "training_ready": False,
    }


def transform_baseline(session: str, records: list[dict]) -> tuple[list[dict], dict]:
    output = []
    seen = set()
    duplicates = 0
    families = set()
    counts = Counter()
    for rec in records:
        if rec.get("observed_healthy") is not True or rec.get("quality_warnings"):
            raise ValueError("Baseline con observaciones no saludables")
        acquisition = rec["recorded_at_utc"]
        samples = rec.get("metric_samples")
        if not isinstance(samples, list) or not samples:
            raise ValueError("Sin series Prometheus")
        for metric in samples:
            name = metric.get("name")
            if name not in S04_NAMES:
                raise ValueError("Familia S04 desconocida")
            labels = metric.get("labels")
            if not isinstance(labels, dict) or labels.get("__name__") != name:
                raise ValueError("Etiquetas de Prometheus sin identidad")
            if not all(isinstance(k, str) and isinstance(v, str)
                       for k, v in labels.items()):
                raise ValueError("Etiquetas Prometheus no textuales")
            stamp = as_number(metric.get("timestamp_unix"))
            observed = datetime.fromtimestamp(stamp, tz=timezone.utc).isoformat(
                timespec="milliseconds")
            if abs((parse_utc(acquisition) - parse_utc(observed)).total_seconds()) > 120:
                raise ValueError("Muestra de Prometheus obsoleta o futura")
            key = (name, stamp, json.dumps(labels, sort_keys=True))
            if key in seen:
                duplicates += 1
            else:
                seen.add(key)
            families.add(name)
            counts[name] += 1
            output.append(long_row(
                source="prometheus_s04", session=session,
                idx=rec["sample_index"],
                observed=observed, acquired=acquisition,
                name=name, value=metric["value"], unit="state",
                context={"labels": labels},
            ))
    if families != S04_NAMES:
        raise ValueError("Familias S04 incompletas")
    return output, {
        "families": sorted(families),
        "counts_by_family": dict(sorted(counts.items())),
        "prometheus_repeated_scrape_samples": duplicates,
        "note": "Los scrapes repetidos se contabilizan; no son observaciones independientes",
    }


def transform_perf(session: str, records: list[dict]) -> tuple[list[dict], dict]:
    output = []
    probes = Counter()
    missing = Counter()
    for rec in records:
        if rec.get("kind") not in ("icmp", "http"):
            raise ValueError("Tipo de sonda desconocido")
        result = rec.get("result")
        if not isinstance(result, dict) or result.get("measurement_valid") is not True:
            raise ValueError("Sonda no valida para normalizar")
        stamp = rec["recorded_at_utc"]
        ctx = {
            "probe_id": rec["probe_id"],
            "round": rec["round"],
            "namespace": rec["source_namespace"],
            "destination": rec.get("destination_ip", rec.get("destination_url")),
        }
        if rec["kind"] == "http":
            if rec.get("probe_id") != "S2_A_FRONTAL_HQ_HTTP":
                raise ValueError("Sonda HTTP ajena a catalogo")
            if result.get("http_status") != 200:
                raise ValueError("HTTP sin codigo correcto")
            ctx["backend"] = result.get("active_backend")
            ctx["http_status"] = result["http_status"]
            units = HTTP_UNITS
            source = "http_s05"
        else:
            if rec.get("probe_id") not in {
                "HQ_A_S1", "HQ_A_S2", "S2_A_FRONTAL_HQ"
            }:
                raise ValueError("Sonda ICMP ajena al catalogo")
            units = ICMP_UNITS
            source = "icmp_s02"
            sent = as_number(result.get("sent"))
            received = as_number(result.get("received"))
            if not (sent > 0 and 0 <= received <= sent):
                raise ValueError("Contadores ICMP inconsistentes")
            loss = as_number(result.get("loss_pct"))
            if abs(loss - 100.0 * (sent - received) / sent) > 1.1:
                raise ValueError("Perdida ICMP inconsistente")
        probes[rec["probe_id"]] += 1
        for metric_name, unit in units.items():
            value = result.get(metric_name)
            if value is None:
                missing[f"{rec['probe_id']}::{metric_name}"] += 1
            output.append(long_row(
                source=source, session=session, idx=rec["sample_index"],
                observed=stamp, acquired=stamp, name=metric_name,
                value=value, unit=unit, context=dict(ctx),
                allow_missing=True,
            ))
    expected = {
        "HQ_A_S1": 3, "HQ_A_S2": 3,
        "S2_A_FRONTAL_HQ": 3, "S2_A_FRONTAL_HQ_HTTP": 3,
    }
    if dict(probes) != expected:
        raise ValueError("Cobertura por sonda diferente a S06-033")
    return output, {
        "counts_by_probe": dict(sorted(probes.items())),
        "missing_values": dict(sorted(missing.items())),
        "note": "RTT nulo puede ser legitimo cuando no hay respuestas; no imputar cero",
    }


def analyze(base_id: str, perf_id: str) -> tuple[list[dict], dict]:
    base_meta, base_samples = load_session(
        base_id, BASE_ID, "NETLAB360_S06_OBSERVATIONAL_V1",
        "observaciones.jsonl", "observations_sha256"
    )
    perf_meta, perf_samples = load_session(
        perf_id, PERF_ID, "NETLAB360_S06_PERFORMANCE_OBSERVATIONAL_V1",
        "mediciones.jsonl", "data_digest_sha256"
    )
    if perf_meta.get("reference_session") != base_id:
        raise ValueError("Sesiones no estan enlazadas")
    if len(base_samples) != 12 or len(perf_samples) != 12:
        raise ValueError("Numero de muestras distinto a S06-032/033")
    raw_base, quality_base = transform_baseline(base_id, base_samples)
    raw_perf, quality_perf = transform_perf(perf_id, perf_samples)
    rows = sorted(raw_base + raw_perf, key=lambda r: (
        r["observed_at_utc"], r["source"], r["session_id"],
        r["sample_index"], r["signal"],
        json.dumps(r["context"], sort_keys=True)
    ))
    count_source = Counter(row["source"] for row in rows)
    count_missing = sum(r["value"] is None for r in rows)
    report = {
        "schema": SCHEMA, "generated_at_utc": now_utc(),
        "source_sessions": {"baseline": base_id, "performance": perf_id},
        "record_counts": {
            "raw_baseline": len(base_samples),
            "raw_performance": len(perf_samples),
            "normalized_rows": len(rows),
            "by_source": dict(sorted(count_source.items())),
            "missing_numeric_values": count_missing,
        },
        "period_utc": {
            "first": min(r["observed_at_utc"] for r in rows),
            "last": max(r["observed_at_utc"] for r in rows),
        },
        "baseline_quality": quality_base,
        "performance_quality": quality_perf,
        "ground_truth_labels_available": 0,
        "training_ready": False,
        "time_split_ready": False,
        "notes": [
            "Fuentes originales verificadas por SHA-256 antes de derivar",
            "Retener scrapes repetidos e informar su cantidad; no aumentar tamaño efectivo",
            "Estado de router/WAN/VLAN y RTT/HTTP son señales diferentes",
            "Sin experimentos con ground truth, no se generan etiquetas ni particiones ML",
            "P95 basado en cinco paquetes por prueba es exploratorio",
            "No se han medido throughput ni jitter UDP en estos dos datasets",
        ],
    }
    return rows, report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--performance", required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    rows, report = analyze(args.baseline, args.performance)
    print("S06_QA_FUENTES=2")
    print(f"S06_QA_FILAS={len(rows)}")
    print(f"S06_QA_DUPLICADOS_SCRAPE={report['baseline_quality']['prometheus_repeated_scrape_samples']}")
    print(f"S06_QA_VALORES_AUSENTES={report['record_counts']['missing_numeric_values']}")
    print("S06_QA_GROUND_TRUTH=0")
    if args.check_only:
        print("S06_QA_CHECK_ONLY=OK")
        return

    ident = "S06_QA_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + secrets.token_hex(3)
    directory = ROOT / "curated" / ident
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    data_file = directory / "metricas_normalizadas.jsonl"
    report_file = directory / "reporte_calidad.json"
    with data_file.open("x", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
    report["normalized_sha256"] = sha(data_file.read_bytes())
    report["session_id"] = ident
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    print("S06_QA_DIRECTORIO=" + str(directory))
    print("S06_QA_DATA_SHA256=" + report["normalized_sha256"])
    print("S06_QA_NORMALIZACION=OK_DATOS_NO_ETIQUETADOS")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"S06_QA_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
