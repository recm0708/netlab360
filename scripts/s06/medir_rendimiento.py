#!/usr/bin/env python3
"""NETLAB360 S06: medir RTT, perdidas y HTTP desde namespaces aislados.

No cambia interfaces, rutas, servicios ni topologia. Los destinos, scripts
y parametros estan enumerados y acotados. Son mediciones activas de baja carga,
no etiquetas supervisadas de incidentes ni pruebas de rendimiento iperf3.
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
import subprocess
import sys
import time
from urllib.request import urlopen

BASE = Path.home() / "netlab360-bootstrap/s06/datasets"
ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "NETLAB360_S06_PERFORMANCE_OBSERVATIONAL_V1"
PROBES = (
    ("HQ_A_S1", "nl360-s02-h-hq-120", "10.71.20.20"),
    ("HQ_A_S2", "nl360-s02-h-hq-120", "10.72.20.20"),
    ("S2_A_FRONTAL_HQ", "nl360-s02-h-s2-320", "10.70.20.23"),
)
HTTP_NS = "nl360-s02-h-s2-320"
HTTP_ENDPOINT = "http://10.70.20.23:8080/api/v1/service"
PARENT_RE = re.compile(r"^S06_BASELINE_\d{8}T\d{6}Z_[0-9a-f]{6}$")

# El codigo viaja como argumento exacto a Python dentro del namespace;
# no hay bash -c, shell=True, ni URL parametrizable desde el navegador.
HTTP_PROBE = r"""
import json
import time
from urllib.request import Request, ProxyHandler, build_opener
url = "http://10.70.20.23:8080/api/v1/service"
request = Request(url, headers={"Cache-Control": "no-store"})
start = time.monotonic()
with build_opener(ProxyHandler({})).open(request, timeout=5) as response:
    data = json.load(response)
    result = {
        "http_status": response.status,
        "elapsed_ms": round((time.monotonic() - start) * 1000, 3),
        "service": data.get("service"),
        "role": data.get("role"),
        "availability": data.get("status"),
        "active_backend": data.get("active_backend"),
        "selected_path": data.get("selected_path"),
    }
print(json.dumps(result, separators=(",", ":")))
"""


def utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def run(*argv: str, timeout: float = 15) -> subprocess.CompletedProcess:
    return subprocess.run(argv, text=True, capture_output=True,
                          timeout=timeout, check=False)


def validate_limits(rounds: int, packets: int, pause: float) -> None:
    if not 1 <= rounds <= 8:
        raise ValueError("rounds fuera de rango 1..8")
    if not 2 <= packets <= 10:
        raise ValueError("packets fuera de rango 2..10")
    if not 0 <= pause <= 10:
        raise ValueError("pause fuera de rango 0..10")


def percentile(values: list[float], pct: float = 95) -> float | None:
    if not values:
        return None
    data = sorted(values)
    idx = (len(data) - 1) * pct / 100
    lo = math.floor(idx)
    hi = math.ceil(idx)
    return round(data[lo] + (data[hi] - data[lo]) * (idx - lo), 3)


def parse_ping(raw: str, expected_packets: int, returncode: int) -> dict:
    if returncode not in (0, 1):
        raise ValueError("ping no pudo completar la medicion")
    summary = re.search(
        r"(?P<sent>\d+)\s+packets transmitted,\s*"
        r"(?P<received>\d+)\s+(?:packets\s+)?received\b", raw
    )
    loss = re.search(r"(?P<loss>\d+(?:\.\d+)?)%\s+packet loss\b", raw)
    if not summary or not loss:
        raise ValueError("ping sin resumen parseable")
    sent = int(summary["sent"])
    received = int(summary["received"])
    loss_pct = float(loss["loss"])
    if (sent != expected_packets or received > sent or
            not 0 <= loss_pct <= 100 or
            abs(loss_pct - 100 * (sent - received) / sent) > 1.1):
        raise ValueError("inconsistencia de paquetes o perdida")

    matches = re.findall(
        r"\bicmp_seq=\d+\b[^\n]*?\btime[=<]([\d.]+)\s*ms\b", raw
    )
    rtts = [float(x) for x in matches]
    if len(rtts) != received or any(not math.isfinite(x) or x < 0 for x in rtts):
        raise ValueError("RTT por paquete incompleto o no finito")

    summary_rtt = re.search(
        r"\b(?:rtt|round-trip) min/avg/max/(?:mdev|stddev)\s*=\s*"
        r"([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)\s*ms", raw
    )
    if received > 0 and not summary_rtt:
        raise ValueError("ping sin resumen de RTT")
    if received == 0 and summary_rtt:
        raise ValueError("RTT incompatible con cero respuestas")
    if summary_rtt:
        mn, avg, mx, dev = (float(x) for x in summary_rtt.groups())
        if not (0 <= mn <= avg <= mx and dev >= 0):
            raise ValueError("RTT de resumen inconsistente")
    else:
        mn = avg = mx = dev = None

    return {
        "sent": sent, "received": received, "loss_pct": loss_pct,
        "rtt_min_ms": mn, "rtt_avg_ms": avg, "rtt_max_ms": mx,
        "rtt_mdev_ms": dev, "rtt_p95_ms": percentile(rtts),
        "rtt_samples_ms": rtts, "ping_returncode": returncode,
        "measurement_valid": True,
    }


def check_management() -> None:
    ip = run("ip", "-4", "-o", "addr", "show", "dev", "ens33")
    route = run("ip", "-4", "route", "show", "default")
    if (ip.returncode or route.returncode
            or "192.168.47.40/24" not in ip.stdout
            or "default via 192.168.47.2 dev ens33" not in route.stdout):
        raise RuntimeError("Red administrativa fuera de estado esperado")


def preflight() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("No ejecutar como root, usar sudo -v antes")
    check_management()
    state = run("git", "-C", str(ROOT), "status", "--porcelain")
    if state.returncode or state.stdout.strip():
        raise RuntimeError("Repositorio con cambios locales o inaccesible")
    namespaces = run("sudo", "-n", "ip", "netns", "list")
    if namespaces.returncode:
        raise RuntimeError("No se pudo consultar namespaces con sudo -n")
    current = {row.split()[0] for row in namespaces.stdout.splitlines() if row.strip()}
    needed = {item[1] for item in PROBES} | {HTTP_NS}
    if not needed.issubset(current) or len(current) != 21:
        raise RuntimeError("Namespaces o topologia inesperados")
    with urlopen("http://127.0.0.1:9130/api/v1/graph", timeout=8) as r:
        graph = json.load(r)
    with urlopen("http://127.0.0.1:9110/api/v1/state", timeout=8) as r:
        exporter = json.load(r)
    if (exporter.get("source_ok") is not True
            or graph.get("routing", {}).get("available") is not True
            or graph.get("ha_service", {}).get("status") != "running"
            or graph.get("ha_service", {}).get("active_backend") != "BACKEND_HQ"
            or graph.get("source_warnings")):
        raise RuntimeError("Fuentes NOC/S04 no estan en estado de referencia")


def validate_reference(session: str) -> dict:
    if not PARENT_RE.fullmatch(session):
        raise ValueError("Identificador de baseline invalido")
    raw_dir = (BASE / "raw" / session)
    if raw_dir.is_symlink() or not raw_dir.is_dir():
        raise ValueError("Sesion de referencia ausente o symlink")
    metadata = raw_dir / "metadata.json"
    if not metadata.is_file() or metadata.is_symlink():
        raise ValueError("Metadata de referencia ausente o symlink")
    data = json.loads(metadata.read_text(encoding="utf-8"))
    if (data.get("session_id") != session
            or data.get("status") != "complete"
            or data.get("schema") != "NETLAB360_S06_OBSERVATIONAL_V1"
            or data.get("ground_truth_verified") is not False):
        raise ValueError("Referencia observacional no aprobada")
    return data


def measure_ping(probe: tuple[str, str, str], packets: int) -> dict:
    ident, origin, target = probe
    began = utc()
    args = (
        "sudo", "-n", "ip", "netns", "exec", origin,
        "ping", "-n", "-c", str(packets), "-i", "0.25",
        "-W", "2", "-w", str(max(6, packets + 3)), target
    )
    try:
        result = run(*args, timeout=max(12, packets + 6))
        measurement = parse_ping(result.stdout, packets, result.returncode)
        warnings = []
        if measurement["loss_pct"] > 0:
            warnings.append("observed_packet_loss_not_ground_truth")
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        measurement = {"measurement_valid": False, "error_type": type(exc).__name__}
        warnings = ["ping_measurement_unavailable"]
    return {
        "recorded_at_utc": utc(), "started_at_utc": began,
        "kind": "icmp", "probe_id": ident, "source_namespace": origin,
        "destination_ip": target, "requested_packets": packets,
        "result": measurement, "quality_warnings": warnings,
        "ground_truth_label": "UNKNOWN", "ground_truth_verified": False,
    }


def parse_http(raw: str) -> dict:
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("HTTP no regreso objeto")
    elapsed = result.get("elapsed_ms")
    if (type(elapsed) not in (float, int) or
            not math.isfinite(elapsed) or elapsed < 0 or elapsed > 10000):
        raise ValueError("Tiempo HTTP no valido")
    if (result.get("http_status") != 200 or
            result.get("service") != "netlab360-s05-ha" or
            result.get("role") != "frontend" or
            result.get("availability") != "available" or
            result.get("active_backend") not in ("BACKEND_HQ", "BACKEND_S1")):
        raise ValueError("Respuesta HTTP distinta de contrato S05")
    return {
        "http_status": 200, "elapsed_ms": float(elapsed),
        "availability": "available",
        "active_backend": result["active_backend"],
        "selected_path": result.get("selected_path"),
        "measurement_valid": True,
    }


def measure_http() -> dict:
    began = utc()
    try:
        p = run(
            "sudo", "-n", "ip", "netns", "exec", HTTP_NS,
            "/usr/bin/python3", "-c", HTTP_PROBE, timeout=12
        )
        if p.returncode:
            raise ValueError("S05 HTTP no respondio con el estado esperado")
        result = parse_http(p.stdout)
        warnings = []
        if result["active_backend"] != "BACKEND_HQ":
            warnings.append("fallback_observed_no_induced_failure")
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        result = {"measurement_valid": False, "error_type": type(exc).__name__}
        warnings = ["http_measurement_unavailable"]
    return {
        "recorded_at_utc": utc(), "started_at_utc": began,
        "kind": "http", "probe_id": "S2_A_FRONTAL_HQ_HTTP",
        "source_namespace": HTTP_NS, "destination_url": HTTP_ENDPOINT,
        "result": result, "quality_warnings": warnings,
        "ground_truth_label": "UNKNOWN", "ground_truth_verified": False,
    }


def store(path: Path, data: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    os.replace(tmp, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--reference-session", required=True)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--packets", type=int, default=5)
    parser.add_argument("--pause", type=float, default=1)
    args = parser.parse_args()
    os.umask(0o077)
    validate_limits(args.rounds, args.packets, args.pause)
    reference = validate_reference(args.reference_session)
    preflight()
    print("S06_RENDIMIENTO_PRECHECK=OK")
    print("S06_REFERENCIA=" + reference["session_id"])
    print("S06_PRUEBAS_POR_RONDA=3_ICMP_1_HTTP")
    if args.check_only:
        print("S06_RENDIMIENTO_MODO=SOLO_DIAGNOSTICO")
        return

    session_id = (
        "S06_PERF_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        + "_" + secrets.token_hex(3)
    )
    directory = BASE / "raw" / session_id
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    data_file = directory / "mediciones.jsonl"
    meta_file = directory / "metadata.json"
    meta = {
        "schema": SCHEMA, "session_id": session_id,
        "reference_session": args.reference_session,
        "status": "capturing", "started_at_utc": utc(),
        "ground_truth_label": "UNKNOWN",
        "ground_truth_verified": False,
        "observation_kind": "active_low_rate_probes",
        "probe_catalog": [
            {"id": p[0], "namespace": p[1], "destination": p[2]} for p in PROBES
        ] + [{"id": "S2_A_FRONTAL_HQ_HTTP", "namespace": HTTP_NS,
              "destination": HTTP_ENDPOINT}],
        "rounds_requested": args.rounds, "ping_packets": args.packets,
        "samples_expected": args.rounds * 4,
        "data_provenance": "Real NETLAB360 S02/S05 namespaces; no synthetic",
        "training_ready": False,
    }
    store(meta_file, meta)
    samples = 0
    complete = 0
    try:
        with data_file.open("x", encoding="utf-8") as stream:
            for round_no in range(1, args.rounds + 1):
                if round_no > 1 and args.pause:
                    time.sleep(args.pause)
                for item in (*[measure_ping(p, args.packets) for p in PROBES],
                             measure_http()):
                    samples += 1
                    item["schema"] = SCHEMA
                    item["session_id"] = session_id
                    item["round"] = round_no
                    item["sample_index"] = samples
                    stream.write(json.dumps(item, ensure_ascii=False) + "\n")
                    stream.flush()
                    complete += int(item["result"].get("measurement_valid") is True)
                    label = ("OK" if item["result"].get("measurement_valid")
                             else "UNKNOWN")
                    print(f"S06_MEDICION={samples}/{meta['samples_expected']} "
                          f"PRUEBA={item['probe_id']} CALIDAD={label}", flush=True)
    finally:
        meta["finished_at_utc"] = utc()
        meta["samples_recorded"] = samples
        meta["samples_valid"] = complete
        meta["status"] = ("complete" if complete == meta["samples_expected"]
                          else "partial_quality")
        if data_file.exists():
            meta["data_digest_sha256"] = hashlib.sha256(
                data_file.read_bytes()).hexdigest()
        store(meta_file, meta)

    print("S06_RENDIMIENTO_SESION=" + session_id)
    print("S06_RENDIMIENTO_DIRECTORIO=" + str(directory))
    print(f"S06_RENDIMIENTO_VALIDAS={complete}/{samples}")
    if complete != meta["samples_expected"]:
        raise SystemExit("S06_RENDIMIENTO=DATOS_PARCIALES_REVISAR_JSONL")
    print("S06_RENDIMIENTO=OK_SIN_ETIQUETADO_SUPERVISADO")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, KeyError) as exc:
        print(f"S06_RENDIMIENTO_ERROR={type(exc).__name__}: {exc}",
              file=sys.stderr)
        sys.exit(1)
