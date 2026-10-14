#!/usr/bin/env python3
"""NETLAB360 B4 — diagnostico descriptivo por reglas, SIN aprendizaje automatico.

Lee el CSV ICMP real y el perfil validado por SHA256. Señales operativas:
perdida de ICMP, FIB distinta a la esperada en fases estables y RTT > 3*p95
de fase normal. Detecta cambios de fase como EVENTOS OPERATIVOS, no incidentes.

La referencia RTT se obtiene de la MISMA sesion: es exploratoria e in-sample.
Prohibido usar conteos de señales como precision/recall/F1 o ground truth.
Nunca altera datos originales, redes, contenedores ni estado IaC.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from collections import Counter
from pathlib import Path
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[2]
HOME_BASE = Path.home() / "netlab360-bootstrap/analitica/b4"
PROFILE = HOME_BASE / "perfil-estadistico-real.json"
AUDIT = HOME_BASE / "inventario-fuentes-reales.json"
OUTPUT = HOME_BASE / "diagnostico-reglas-real.json"

spec = importlib.util.spec_from_file_location(
    "netlab360_b4_profile", ROOT / "scripts/analitica/b4-perfil-estadistico-real.py"
)
if spec is None or spec.loader is None:
    raise RuntimeError("No se pudo cargar analizador estadistico B4")
profile_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile_lib)

EXPECT = {"normal": "wan-p", "respaldo": "wan-b", "restaurada": "wan-p"}
NEEDED = {"fecha_local", "segundos_desde_inicio", "sondeo",
          "fase", "interfaz_fib", "icmp_ok", "rtt_ms", "codigo_ping"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_rows(rows: list[dict], normal_p95: float, factor: float = 3.0) -> dict:
    if not (math.isfinite(normal_p95) and normal_p95 > 0):
        raise ValueError("p95 de referencia normal inexistente o no positivo")
    if not (math.isfinite(factor) and 2.0 <= factor <= 10.0):
        raise ValueError("Factor de referencia permitido: 2.0 a 10.0")
    threshold = normal_p95 * factor
    signals = []
    transitions = []
    counts = Counter()
    total = 0
    before_phase = None
    seen_probes = set()
    for row in rows:
        if not NEEDED.issubset(row):
            raise ValueError("Faltan columnas obligatorias")
        phase = str(row["fase"]).strip()
        if not phase:
            raise ValueError("Fase vacia")
        seq = int(row["sondeo"])
        if seq <= 0 or seq in seen_probes:
            raise ValueError("Sondeo duplicado/invalido")
        seen_probes.add(seq)
        ok = profile_lib.icmp_bool(str(row["icmp_ok"]))
        fib = str(row["interfaz_fib"]).strip() or "none"
        elapsed = profile_lib.finite_number(str(row["segundos_desde_inicio"]), "elapsed")
        if elapsed < 0:
            raise ValueError("Tiempo negativo")
        rtt_text = str(row["rtt_ms"]).strip()
        rtt = profile_lib.finite_number(rtt_text, "RTT") if rtt_text else None
        if rtt is not None and rtt < 0:
            raise ValueError("RTT negativo")
        if before_phase is not None and phase != before_phase:
            transitions.append({"sondeo": seq, "de": before_phase, "a": phase,
                                "fib_observada": fib,
                                "tipo": "cambio_fase_operativo_no_anomalia"})
        before_phase = phase
        total += 1
        if not ok:
            counts["ICMP_FALLIDO"] += 1
            signals.append({"sondeo": seq, "fase": phase, "regla": "ICMP_FALLIDO"})
        if phase in EXPECT and fib != EXPECT[phase]:
            counts["FIB_INESPERADA_FASE_ESTABLE"] += 1
            signals.append({"sondeo": seq, "fase": phase, "regla": "FIB_INESPERADA_FASE_ESTABLE",
                            "esperada": EXPECT[phase], "observada": fib})
        if ok and rtt is not None and rtt > threshold:
            counts["RTT_SOBRE_REFERENCIA"] += 1
            signals.append({"sondeo": seq, "fase": phase, "regla": "RTT_SOBRE_REFERENCIA",
                            "observado_ms": rtt, "umbral_ms": round(threshold, 6)})
    if not rows:
        raise ValueError("CSV vacio")
    return {
        "samples": total,
        "baseline_normal_p95_ms": normal_p95,
        "threshold_factor": factor,
        "rtt_reference_threshold_ms": round(threshold, 6),
        "signal_counts": {k: counts.get(k, 0) for k in (
            "ICMP_FALLIDO", "FIB_INESPERADA_FASE_ESTABLE", "RTT_SOBRE_REFERENCIA")},
        "signal_occurrences": len(signals),
        "signals": signals,
        "operational_phase_transitions": transitions,
        "transition_count": len(transitions),
    }


def analyze(profile: dict, audit: dict, factor: float = 3.0) -> dict:
    sessions = profile.get("sessions")
    if not isinstance(sessions, list) or len(sessions) != 1:
        raise ValueError("Este prototipo acepta exactamente una sesion historica")
    if profile.get("source_inventory_sha256") != digest(AUDIT):
        raise ValueError("Auditoria fuente modificada despues del perfil")
    session = sessions[0]
    csv_path = Path(session["source_csv"])
    if not csv_path.is_file() or csv_path.is_symlink():
        raise ValueError("CSV de origen no disponible o es symlink")
    if digest(csv_path) != session["sha256"]:
        raise ValueError("SHA256 del CSV cambio despues del perfil")
    refs = [item for item in audit.get("files", []) if item.get("kind") == "raw_icmp_csv"]
    if len(refs) != 1 or refs[0]["sha256"] != session["sha256"]:
        raise ValueError("Fuente CSV incompatible con inventario")
    phases = session["phases"]
    normal = phases.get("normal")
    if not isinstance(normal, dict) or normal.get("samples", 0) < 10:
        raise ValueError("Se necesitan al menos 10 muestras en fase normal")
    p95 = float(normal["rtt_p95_nearest_rank_ms"])
    with csv_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        rows = list(reader)
    result = evaluate_rows(rows, p95, factor)
    if result["samples"] != session["samples"]:
        raise ValueError("Recuento difiere de perfil B4")
    if result["signal_counts"]["ICMP_FALLIDO"] != session["icmp_failed"]:
        raise ValueError("ICMP falla difiere del perfil")
    if (result["signal_counts"]["FIB_INESPERADA_FASE_ESTABLE"] !=
            session["stable_fib_mismatches"]):
        raise ValueError("Discrepancia FIB frente al perfil")
    return {
        "scope": "replay_historico_misma_sesion",
        "original_sha256": session["sha256"],
        "method": "reglas_deterministas_contextuales",
        "signal_interpretation": "indicadores exploratorios, no incidentes confirmados",
        "baseline_from_same_session": True,
        "train_test_separation": False,
        "supervised_ml_trained": False,
        "precision_recall_f1_evaluated": False,
        **result,
    }


def write_safe(payload: dict, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if target.is_symlink():
        raise ValueError("Destino symlink prohibido")
    with NamedTemporaryFile("w", encoding="utf-8", dir=target.parent,
                            prefix="diagnostico-b4-", suffix=".tmp", delete=False) as fp:
        json.dump(payload, fp, ensure_ascii=False, indent=2)
        fp.write("\n")
        temporary = Path(fp.name)
    try:
        temporary.chmod(0o600)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--factor", type=float, default=3.0)
    args = parser.parse_args()
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    inventory = json.loads(AUDIT.read_text(encoding="utf-8"))
    report = analyze(profile, inventory, args.factor)
    print("========== INICIO CAPTURA B4_08_Diagnostico_Reglas_Reales ==========")
    print("ORIGEN=CSV_HISTORICO_REAL_SHA256_VALIDADO")
    print("MUESTRAS=" + str(report["samples"]))
    print("METODO=REGLAS_DETERMINISTAS_NO_ML")
    print("NORMAL_P95_MS=" + str(report["baseline_normal_p95_ms"]))
    print("FACTOR_EXPLORATORIO=" + str(report["threshold_factor"]))
    print("UMBRAL_RTT_REFERENCIA_MS=" + str(report["rtt_reference_threshold_ms"]))
    for name, count in report["signal_counts"].items():
        print(f"REGLA={name} | SENIALES_OBSERVADAS={count}")
    print("TRANSICIONES_OPERATIVAS=" + str(report["transition_count"]))
    for t in report["operational_phase_transitions"]:
        print("CAMBIO_FASE=sondeo:{sondeo} {de}->{a} FIB:{fib_observada}".format(**t))
    print("LINEA_BASE_PROCEDE_MISMA_SESION=SI")
    print("CLASIFICACION_ML_EVALUADA=NO")
    if args.save:
        write_safe(report, OUTPUT)
        print("REPORTE_LOCAL=" + str(OUTPUT))
    print("B4_DIAGNOSTICO_REGLAS=OK")
    print("========== FIN CAPTURA B4_08_Diagnostico_Reglas_Reales ==========")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, AssertionError, KeyError, TypeError,
            json.JSONDecodeError) as exc:
        raise SystemExit("B4_DIAGNOSTICO_REGLAS=ERROR: " + str(exc))
