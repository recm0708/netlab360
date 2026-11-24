#!/usr/bin/env python3
"""G5: SLI S04 observados y SLO de laboratorio propuesto, sin confundir con SLA.

Solo lee localhost:9091; no despliega servicios ni modifica redes.
Los porcentajes corresponden únicamente a muestras realmente registradas.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = "http://127.0.0.1:9091"
JOB = '{job="netlab360-s04-multisede"}'
METRICS = {
    "scrape": f"up{JOB}",
    "fuente_condicional": "netlab360_s04_source_up",
}
INTERVAL_SECONDS = 2


def query_scalar(expr: str, reader=urlopen) -> float:
    query = urlencode({"query": expr})
    with reader(BASE + "/api/v1/query?" + query, timeout=10) as r:
        answer = json.load(r)
    if answer.get("status") != "success":
        raise RuntimeError("Prometheus devolvio status no exitoso")
    values = answer.get("data", {}).get("result", [])
    if not isinstance(values, list) or len(values) != 1:
        raise RuntimeError(f"Cardinalidad SLI inesperada en: {expr}")
    try:
        result = float(values[0]["value"][1])
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        raise RuntimeError("Muestra SLI no numerica") from exc
    if not math.isfinite(result):
        raise RuntimeError("Muestra SLI infinita/NaN")
    return result


def summarize(successes: float, total: float, target: float) -> dict:
    if not (math.isfinite(total) and math.isfinite(successes)
            and total > 0 and 0 <= successes <= total
            and 0 < target <= 100):
        raise ValueError("SLI, ventana u objetivo invalidos")
    ok = round(successes)
    n = round(total)
    if abs(ok-successes) > 1e-5 or abs(n-total) > 1e-5:
        raise ValueError("Metricas de conteo no enteras")
    fail = n - ok
    # Numero maximo discreto de errores que respeta el SLO propuesto.
    allowance = math.floor(n * (100.0 - target) / 100.0 + 1e-9)
    pct = 100.0 * ok / n
    return {"ok": ok, "total": n, "fail": fail, "pct": pct,
            "allowance": allowance, "error_budget_remaining": allowance-fail,
            "would_pass_proposed_target": pct + 1e-9 >= target}


def measure(minutes: int = 15, target: float = 99.0, scalar=query_scalar) -> dict:
    if minutes not in (15, 30, 60):
        raise ValueError("Ventana fuera de las tres permitidas")
    if not 0 < target <= 100:
        raise ValueError("Objetivo propuesto fuera de rango")
    results = {}
    for name, selector in METRICS.items():
        count = scalar(f"count_over_time({selector}[{minutes}m])")
        successes = scalar(f"sum_over_time({selector}[{minutes}m])")
        results[name] = summarize(successes, count, target)
    nominal = minutes * 60 // INTERVAL_SECONDS
    # Referencia de programación, NO faltas verificadas ni disponibilidad.
    return {"schema": "NETLAB360_S04_G5_SLI_V1",
            "observed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "window_minutes": minutes, "proposed_target_pct": target,
            "scrape_interval_nominal_seconds": INTERVAL_SECONDS,
            "nominal_scrape_slots": nominal,
            "sli": results,
            "evaluation": "provisional_not_formal_slo",
            "scope": ("scrape: muestras up 1/0 registradas; "
                      "fuente_condicional: source_up solo entre muestras presentes; "
                      "ninguno es disponibilidad de red extremo a extremo")}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=int, default=15, choices=(15, 30, 60))
    p.add_argument("--proposed-slo", type=float, default=99.0)
    p.add_argument("--save", action="store_true")
    args = p.parse_args()
    result = measure(args.minutes, args.proposed_slo)
    print("========== S04 G5 SLI OBSERVABILIDAD ==========")
    print("S04_G5_OBSERVADO_UTC=" + result["observed_at_utc"])
    print(f"S04_G5_VENTANA_MIN={result['window_minutes']}")
    print(f"S04_G5_SLO_PROPUESTO_PCT={result['proposed_target_pct']:.3f}")
    print("S04_G5_SLO_ESTADO=PROPUESTA_NO_APROBADA")
    print(f"S04_G5_CADENCIA_NOMINAL_SEG={INTERVAL_SECONDS}")
    print(f"S04_G5_POSICIONES_TEORICAS_APROX={result['nominal_scrape_slots']}")
    for label in ("scrape", "fuente_condicional"):
        s = result["sli"][label]
        name = label.upper()
        print(f"S04_G5_{name}_EXITOS={s['ok']}/{s['total']}")
        print(f"S04_G5_{name}_SLI_PCT={s['pct']:.3f}")
        print(f"S04_G5_{name}_FALLOS_OBSERVADOS={s['fail']}")
        print(f"S04_G5_{name}_PRESUPUESTO_ERRORES_PROPUESTO={s['allowance']}")
        print(f"S04_G5_{name}_PRESUPUESTO_REMANENTE={s['error_budget_remaining']}")
        print(f"S04_G5_{name}_CUMPLIRIA_SLO_PROPUESTO={int(s['would_pass_proposed_target'])}")
    print("S04_G5_NIVEL_DE_RED_USUARIO_FINAL=NO_MEDIDO")
    if args.save:
        folder = Path.home() / "netlab360-bootstrap/s04/evidencias"
        if not folder.is_dir() or folder.is_symlink():
            raise RuntimeError("Directorio local de evidencia no valido")
        name = ("S04_G5_SLI_"
                + result["observed_at_utc"].replace(":", "").replace("+", "")
                + f"_{args.minutes}m.json")
        path = folder / name
        with path.open("x", encoding="utf-8", newline="\n") as fd:
            json.dump(result, fd, ensure_ascii=False, indent=2, sort_keys=True)
            fd.write("\n")
        print(f"S04_G5_REGISTRO_JSON={path}")
    print("S04_G5_SLI_REPRODUCIBLE=OK")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"S04_G5_ERROR={type(exc).__name__}: {exc}")
        raise SystemExit(1)
