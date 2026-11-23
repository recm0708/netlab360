#!/usr/bin/env python3
"""S06: captura observacional de telemetria local; no modifica NETLAB360.

Produce JSONL y metadatos por sesion fuera del repositorio. Nunca genera
etiquetas de ground truth ni presupone que disponibilidad equivale a rendimiento.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
import sys
import time
from urllib.parse import urlencode
from urllib.request import urlopen

HOME = Path.home()
DATA_ROOT = HOME / "netlab360-bootstrap/s06/datasets"
HISTORY = HOME / "netlab360-bootstrap/s04/historial/incidentes.sqlite3"
SOURCES = {
    "s04": "http://127.0.0.1:9110",
    "noc": "http://127.0.0.1:9130",
    "prom": "http://127.0.0.1:9091",
}
METRICS = {
    "netlab360_s04_router_running",
    "netlab360_s04_source_up",
    "netlab360_s04_topology_mode",
    "netlab360_s04_vlan_admin_up",
    "netlab360_s04_wan_admin_up",
}
JOB_QUERY = 'up{job="netlab360-s04-multisede"}'
METRIC_QUERY = '{__name__=~"netlab360_s04_.*"}'
SCHEMA = "NETLAB360_S06_OBSERVATIONAL_V1"


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def request_json(source: str, path: str, *, params: dict | None = None,
                 timeout: float = 6) -> dict:
    """Solo URLs fijas de localhost; no recibe URL arbitraria de CLI."""
    if source not in SOURCES or not path.startswith("/"):
        raise ValueError("Origen o ruta no autorizados")
    url = SOURCES[source] + path
    if params:
        url += "?" + urlencode(params)
    with urlopen(url, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP {response.status} desde {source}")
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError("Respuesta JSON no es objeto")
    return value


def parse_prom_vector(payload: dict, *, s04_only: bool) -> list[dict]:
    if (payload.get("status") != "success" or
            payload.get("data", {}).get("resultType") != "vector"):
        raise ValueError("Respuesta instantanea Prometheus no valida")
    results = payload["data"].get("result")
    if not isinstance(results, list) or len(results) > 300:
        raise ValueError("Cantidad de series inesperada")
    items = []
    for entry in results:
        labels = entry.get("metric")
        value = entry.get("value")
        if (not isinstance(labels, dict) or not isinstance(value, list)
                or len(value) != 2):
            raise ValueError("Serie incompleta")
        name = labels.get("__name__")
        if (not isinstance(name, str)
                or (s04_only and name not in METRICS)
                or (not s04_only and name != "up")):
            raise ValueError("Nombre de metrica ajeno a la fuente")
        number = float(value[1])
        timestamp = float(value[0])
        if not math.isfinite(number) or not math.isfinite(timestamp):
            raise ValueError("Numero no finito")
        if not all(isinstance(k, str) and isinstance(v, str)
                   for k, v in labels.items()):
            raise ValueError("Etiquetas no textuales")
        items.append({
            "name": name, "labels": labels,
            "timestamp_unix": timestamp, "value": number,
        })
    return sorted(items, key=lambda x: (x["name"], str(sorted(x["labels"].items()))))


def quality(exporter: dict, graph: dict, health: dict,
            metrics: list[dict], scrape: list[dict]) -> tuple[bool, list[str]]:
    reasons = []
    if exporter.get("source_ok") is not True or exporter.get("topology") != "active":
        reasons.append("s04_source_unavailable")
    if health.get("healthy") is not True:
        reasons.append("noc_health_unknown")
    if (graph.get("telemetry") or {}).get("available") is not True:
        reasons.append("noc_telemetry_unknown")
    if (graph.get("routing") or {}).get("available") is not True:
        reasons.append("routing_unknown")
    ha = graph.get("ha_service") or {}
    if ha.get("status") != "running" or ha.get("active_backend") != "BACKEND_HQ":
        reasons.append("http_ha_baseline_unknown")
    lacp = graph.get("lacp") or {}
    sites = lacp.get("sites") or {}
    if (lacp.get("available") is not True or
        any((sites.get(s) or {}).get("status") != "up" or
            (sites.get(s) or {}).get("switch_members") != 2 or
            (sites.get(s) or {}).get("client_members") != 2
            for s in ("HQ", "S1", "S2"))):
        reasons.append("lacp_baseline_unknown")
    sdn = graph.get("sdn") or {}
    if sdn.get("status") != "connected" or sdn.get("available") is not True:
        reasons.append("sdn_unknown")
    if graph.get("source_warnings"):
        reasons.append("noc_source_warnings")
    if len(graph.get("nodes", [])) != 18 or len(graph.get("links", [])) != 21:
        reasons.append("unexpected_topology_size")
    if {m["name"] for m in metrics} != METRICS:
        reasons.append("missing_metric_families")
    sources = [m["value"] for m in metrics if m["name"] == "netlab360_s04_source_up"]
    if sources != [1.0]:
        reasons.append("source_metric_not_one")
    if not scrape or any(m["value"] != 1.0 for m in scrape):
        reasons.append("prom_scrape_unavailable")
    return not reasons, reasons


def get_sample(*, timeout: float = 6) -> dict:
    started_at = utc()
    exporter = request_json("s04", "/api/v1/state", timeout=timeout)
    graph = request_json("noc", "/api/v1/graph", timeout=timeout)
    health = request_json("noc", "/healthz", timeout=timeout)
    metrics = parse_prom_vector(
        request_json("prom", "/api/v1/query",
                     params={"query": METRIC_QUERY}, timeout=timeout),
        s04_only=True,
    )
    scrape = parse_prom_vector(
        request_json("prom", "/api/v1/query",
                     params={"query": JOB_QUERY}, timeout=timeout),
        s04_only=False,
    )
    good, reasons = quality(exporter, graph, health, metrics, scrape)
    return {
        "schema": SCHEMA,
        "recorded_at_utc": utc(),
        "started_at_utc": started_at,
        "source_timestamps": {
            "s04_observed_at_utc": exporter.get("observed_at_utc"),
            "noc_observed_at_utc": graph.get("observed_at_utc"),
            "noc_telemetry_last_sample_utc":
                (graph.get("telemetry") or {}).get("last_sample_utc"),
        },
        "observed_healthy": good,
        "quality_warnings": reasons,
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "scenario": "baseline_observacional_sin_falla_inducida",
        "metric_samples": metrics,
        "prometheus_scrape": scrape,
        "noc": {
            "node_count": len(graph.get("nodes", [])),
            "link_count": len(graph.get("links", [])),
            "route_available": (graph.get("routing") or {}).get("available"),
            "ha_status": (graph.get("ha_service") or {}).get("status"),
            "ha_backend": (graph.get("ha_service") or {}).get("active_backend"),
            "lacp": {
                s: {
                    "status": ((graph.get("lacp") or {}).get("sites") or {}).get(s, {}).get("status"),
                    "switch_members":
                        ((graph.get("lacp") or {}).get("sites") or {}).get(s, {}).get("switch_members"),
                    "client_members":
                        ((graph.get("lacp") or {}).get("sites") or {}).get(s, {}).get("client_members"),
                }
                for s in ("HQ", "S1", "S2")
            },
            "sdn_status": (graph.get("sdn") or {}).get("status"),
            "sdn_flow_count": (graph.get("sdn") or {}).get("flow_count"),
        },
    }


def sqlite_counts(db: Path = HISTORY) -> dict[str, int]:
    if not db.is_file() or db.is_symlink():
        raise ValueError("Historico SQLite no disponible o symlink")
    con = sqlite3.connect(db.as_uri() + "?mode=ro", uri=True)
    try:
        if con.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise ValueError("SQLite quick_check fallo")
        return {table: con.execute(
            f'SELECT count(*) FROM "{table}"'
        ).fetchone()[0] for table in ("active", "events")}
    finally:
        con.close()


def validate_limits(samples: int, interval: float, timeout: float) -> None:
    if not 1 <= samples <= 60:
        raise ValueError("samples debe estar entre 1 y 60")
    if not 1 <= interval <= 30:
        raise ValueError("interval debe estar entre 1 y 30 segundos")
    if not 2 <= timeout <= 10:
        raise ValueError("timeout debe estar entre 2 y 10 segundos")


def write_json(path: Path, data: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=6.0)
    args = parser.parse_args()
    os.umask(0o077)
    validate_limits(args.samples, args.interval, args.timeout)

    repo = Path(__file__).resolve().parents[2]
    head = subprocess.check_output(
        ("git", "-C", str(repo), "rev-parse", "HEAD"), text=True
    ).strip()
    sql = sqlite_counts()
    preflight = get_sample(timeout=args.timeout)
    if not preflight["observed_healthy"]:
        raise SystemExit("S06_PREFLIGHT_NO_APROBADO=" +
                         ",".join(preflight["quality_warnings"]))
    print(f"S06_PREFLIGHT=OK METRICAS={len(preflight['metric_samples'])}")
    print(f"S06_SQLITE_EVENTS={sql['events']} ACTIVE={sql['active']}")
    if args.check_only:
        print("S06_SOLO_DIAGNOSTICO=SI")
        return

    session_id = (
        "S06_BASELINE_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "_" + secrets.token_hex(3)
    )
    directory = DATA_ROOT / "raw" / session_id
    directory.mkdir(parents=True, exist_ok=False, mode=0o700)
    metadata_path = directory / "metadata.json"
    observations_path = directory / "observaciones.jsonl"
    metadata = {
        "schema": SCHEMA, "session_id": session_id,
        "status": "capturing", "started_at_utc": utc(),
        "git_commit": head, "source_urls": SOURCES,
        "operator_intent": "baseline_observacional_sin_falla_inducida",
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "samples_requested": args.samples,
        "interval_seconds": args.interval,
        "sqlite_initial_counts": sql,
        "raw_data_provenance": "S04/S05/Prometheus localhost; no synthetic",
        "data_privacy": "local_runtime_not_versioned",
    }
    write_json(metadata_path, metadata)
    count_ok = 0
    first = time.monotonic()
    try:
        with observations_path.open("x", encoding="utf-8") as stream:
            for i in range(args.samples):
                remaining = first + i * args.interval - time.monotonic()
                if remaining > 0:
                    time.sleep(remaining)
                try:
                    sample = get_sample(timeout=args.timeout)
                except (ValueError, OSError, RuntimeError, TimeoutError) as exc:
                    sample = {
                        "schema": SCHEMA, "recorded_at_utc": utc(),
                        "observed_healthy": False,
                        "quality_warnings": ["capture_error_" + type(exc).__name__],
                        "ground_truth_label": "UNKNOWN",
                        "ground_truth_verified": False,
                    }
                sample["session_id"] = session_id
                sample["sample_index"] = i + 1
                stream.write(json.dumps(sample, ensure_ascii=False) + "\n")
                stream.flush()
                count_ok += int(sample["observed_healthy"])
                print(f"S06_MUESTRA={i+1}/{args.samples} "
                      f"CALIDAD={'OK' if sample['observed_healthy'] else 'UNKNOWN'}",
                      flush=True)
    finally:
        metadata["finished_at_utc"] = utc()
        metadata["samples_complete"] = args.samples
        metadata["samples_healthy"] = count_ok
        metadata["status"] = ("complete" if count_ok == args.samples
                               else "partial_quality")
        if observations_path.is_file():
            metadata["observations_sha256"] = hashlib.sha256(
                observations_path.read_bytes()
            ).hexdigest()
        write_json(metadata_path, metadata)

    print("S06_SESION=" + session_id)
    print("S06_DIRECTORIO=" + str(directory))
    print(f"S06_MUESTRAS_VALIDAS={count_ok}/{args.samples}")
    if count_ok != args.samples:
        raise SystemExit("S06_CAPTURA=PARCIAL_REVISAR_QUALITY_WARNINGS")
    print("S06_BASELINE_OBSERVACIONAL=OK_SIN_ETIQUETAS_ENTRENAMIENTO")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, sqlite3.Error) as exc:
        print(f"S06_CAPTURA_ERROR={type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
