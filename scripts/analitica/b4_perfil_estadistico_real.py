#!/usr/bin/env python3
"""NETLAB360 B4 — perfil estadistico REAL del CSV B2 de convergencia.

No entrena modelos ni crea muestras artificiales. Verifica SHA-256 del CSV
contra el inventario B4 previamente auditado. Los eventos B3 se describen
separadamente y NUNCA se correlacionan por fila con la sesion B2 distinta.
Solo escribe un resumen atomico fuera del repositorio.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import NamedTemporaryFile

BASE = Path.home() / "netlab360-bootstrap"
AUDIT = BASE / "analitica/b4/inventario-fuentes-reales.json"
OUTPUT = BASE / "analitica/b4/perfil-estadistico-real.json"
NEEDED = {"fecha_local", "segundos_desde_inicio", "sondeo", "fase",
          "interfaz_fib", "icmp_ok", "rtt_ms", "codigo_ping"}
STABLE_EXPECTED = {"normal": "wan-p", "respaldo": "wan-b",
                   "restaurada": "wan-p"}
YES = {"1", "true", "si", "sí", "ok", "yes"}
NO = {"0", "false", "no", "error", "fail", "failed"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(262144), b""):
            h.update(chunk)
    return h.hexdigest()


def finite_number(raw: str, name: str) -> float:
    number = float(raw)
    if not math.isfinite(number):
        raise ValueError(f"Valor no finito: {name}")
    return number


def icmp_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in YES:
        return True
    if normalized in NO:
        return False
    raise ValueError(f"icmp_ok no reconocido: {value!r}")


def percentile_nearest_rank(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(q * len(ordered)) - 1)]


def analyze_csv(path: Path) -> dict:
    phases = defaultdict(lambda: {"samples": 0, "icmp_ok": 0,
                                  "fib": Counter(), "rtt": [],
                                  "stable_fib_mismatches": 0})
    seen = set()
    last_elapsed = -1.0
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames is not None
        if not NEEDED.issubset(reader.fieldnames):
            raise ValueError("Columnas B2 faltantes: " +
                             ", ".join(sorted(NEEDED - set(reader.fieldnames))))
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Fila CSV malformada")
            number = int(row["sondeo"])
            if number in seen or number <= 0:
                raise ValueError("Sondeo duplicado o invalido")
            seen.add(number)
            elapsed = finite_number(row["segundos_desde_inicio"], "elapsed")
            if elapsed < 0 or elapsed < last_elapsed:
                raise ValueError("Tiempos no monotonos")
            last_elapsed = elapsed
            phase = row["fase"].strip()
            if not phase:
                raise ValueError("Fase no etiquetada")
            fib = row["interfaz_fib"].strip() or "none"
            ok = icmp_bool(row["icmp_ok"])
            v = phases[phase]
            v["samples"] += 1
            v["icmp_ok"] += int(ok)
            v["fib"][fib] += 1
            if phase in STABLE_EXPECTED and fib != STABLE_EXPECTED[phase]:
                v["stable_fib_mismatches"] += 1
            raw_rtt = row["rtt_ms"].strip()
            if raw_rtt and ok:
                ms = finite_number(raw_rtt, "rtt_ms")
                if ms < 0:
                    raise ValueError("RTT negativo")
                v["rtt"].append(ms)
            if len(seen) > 100000:
                raise ValueError("CSV supera maximo operativo")
    if not seen:
        raise ValueError("CSV sin sondeos")

    result = {}
    for name in sorted(phases):
        v = phases[name]
        rtt = v["rtt"]
        result[name] = {
            "samples": v["samples"],
            "icmp_ok": v["icmp_ok"],
            "icmp_failed": v["samples"] - v["icmp_ok"],
            "fib_counts": dict(sorted(v["fib"].items())),
            "stable_fib_mismatches": v["stable_fib_mismatches"],
            "rtt_observations": len(rtt),
            "rtt_mean_ms": round(statistics.mean(rtt), 6) if rtt else None,
            "rtt_median_ms": round(statistics.median(rtt), 6) if rtt else None,
            "rtt_p95_nearest_rank_ms": percentile_nearest_rank(rtt, 0.95),
            "rtt_max_ms": max(rtt) if rtt else None,
        }
    return {
        "source_csv": str(path),
        "sha256": sha256(path),
        "samples": len(seen),
        "icmp_ok": sum(v["icmp_ok"] for v in phases.values()),
        "icmp_failed": sum(v["samples"]-v["icmp_ok"] for v in phases.values()),
        "stable_fib_mismatches": sum(v["stable_fib_mismatches"] for v in phases.values()),
        "phases": result,
    }


def generate(inventory: dict) -> dict:
    files = inventory.get("files")
    if not isinstance(files, list):
        raise ValueError("Inventario B4 invalido")
    sources = [f for f in files if f.get("kind") == "raw_icmp_csv"]
    if not sources:
        raise ValueError("Sin CSV ICMP auditados")
    summary = []
    for ref in sources:
        path = Path(ref["name"])
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"CSV original ausente o enlace: {path}")
        if sha256(path) != ref["sha256"]:
            raise ValueError(f"SHA256 del CSV cambio desde la auditoria: {path}")
        current = analyze_csv(path)
        if current["samples"] != ref["rows"]:
            raise ValueError("Numero de filas distinto del inventario")
        summary.append(current)
    return {
        "scope": "historical_real_icmp_observations_only",
        "source_inventory_sha256": sha256(AUDIT),
        "sessions": summary,
        "event_jsonl_separate_sessions": True,
        "events_total_not_training_samples": inventory.get("total_event_rows", 0),
        "classification_metrics_evaluated": False,
        "ml_trained": False,
        "convergence_time_measured_by_this_script": False,
        "notes": [
            "Fases son etiquetas operativas del ensayo, no ground truth independiente de un clasificador",
            "FIB observada por sondeo; no implica disponibilidad continua entre sondeos",
            "RTT p95 usa nearest-rank; n pequeno por fase limita inferencia",
            "No juntar eventos B3 y sondeos B2 como si compartieran una linea temporal",
        ],
    }


def persist(payload: dict, target: Path) -> None:
    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target.exists() and target.is_symlink():
        raise ValueError("El destino es symlink")
    with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent,
                            prefix="b4-profile-", suffix=".tmp", delete=False) as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
        tmp = Path(fp.name)
    try:
        tmp.chmod(0o600)
        os.replace(tmp, target)
    finally:
        tmp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    inventory = json.loads(AUDIT.read_text(encoding="utf-8"))
    report = generate(inventory)
    print("========== INICIO CAPTURA B4_04_Perfil_Estadistico_Real ==========")
    for i, session in enumerate(report["sessions"], 1):
        print(f"SESION={i} CSV={Path(session['source_csv']).name}")
        print(f"SHA256_ORIGINAL_VERIFICADO=SI | MUESTRAS={session['samples']}")
        print(f"ICMP_OK={session['icmp_ok']} | ICMP_FALLIDOS={session['icmp_failed']}")
        print(f"DESVIACIONES_FIB_EN_FASES_ESTABLES={session['stable_fib_mismatches']}")
        for phase, stats in session["phases"].items():
            print(f"FASE={phase} | N={stats['samples']} | ICMP_OK={stats['icmp_ok']} | "
                  f"FIB={json.dumps(stats['fib_counts'], sort_keys=True)}")
            print(f"RTT_MEDIA_MS={stats['rtt_mean_ms']} | "
                  f"RTT_P95_NEAREST_RANK_MS={stats['rtt_p95_nearest_rank_ms']} | "
                  f"RTT_MUESTRAS={stats['rtt_observations']}")
    print("JSONL_B3_Y_CSV_B2_NO_SINCRONIZADOS=SI")
    print("EVENTOS_B3_NO_EQUIVALEN_A_MUESTRAS_ETIQUETADAS=" +
          str(report["events_total_not_training_samples"]))
    print("ML_ENTRENADO=NO | METRICAS_CLASIFICACION=NO")
    if args.save:
        persist(report, OUTPUT)
        print("REPORTE_ESTADISTICO_LOCAL=" + str(OUTPUT))
    print("B4_PERFIL_ESTADISTICO=OK")
    print("========== FIN CAPTURA B4_04_Perfil_Estadistico_Real ==========")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, AssertionError, KeyError, TypeError,
            json.JSONDecodeError) as exc:
        raise SystemExit("B4_PERFIL_ESTADISTICO=ERROR: " + str(exc))
