#!/usr/bin/env python3
"""NETLAB360 B4: auditoría SOLO de archivos de telemetría realmente observados.

No crea anomalías ni inventa muestras. Emite metadatos y recuentos,
no el contenido de archivos potencialmente sensibles. Una fecha histórica
en un nombre NO constituye por sí sola un etiquetado independiente para ML.
Opcional --save: JSON de auditoría FUERA del repositorio.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE = Path.home() / "netlab360-bootstrap/evidencias"
OUTPUT = Path.home() / "netlab360-bootstrap/analitica/b4/inventario-fuentes-reales.json"
KNOWN_EVENTS = {
    "WAN_PRIMARY_DOWN", "WAN_PRIMARY_RESTORED",
    "WAN_ROUTE_CHANGED", "TOPOLOGY_STARTED", "TOPOLOGY_STOPPED",
}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 256), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_summary(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        data = csv.DictReader(f)
        names = data.fieldnames or []
        assert 0 < len(names) <= 60, "Cabecera CSV inválida"
        assert len(set(names)) == len(names), "Cabecera repetida"
        rows = 0
        for row in data:
            assert None not in row, "Fila con columnas extra"
            assert all(value is not None for value in row.values()), "Fila incompleta"
            rows += 1
            assert rows <= 100000, "CSV demasiado grande para esta fase"
    return {"rows": rows, "columns": names}


def jsonl_summary(path):
    counter = Counter()
    first = last = None
    with path.open(encoding="utf-8") as source:
        for index, line in enumerate(source, start=1):
            if not line.strip():
                continue
            assert index <= 100000, "JSONL demasiado grande"
            item = json.loads(line)
            assert isinstance(item, dict), "Evento no es un objeto JSON"
            event = item.get("event")
            stamp = item.get("observed_at")
            assert isinstance(event, str) and event in KNOWN_EVENTS, (
                f"Evento desconocido en {path.name}:{index}"
            )
            assert isinstance(stamp, str), "Falta timestamp"
            datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            counter[event] += 1
            if first is None:
                first = stamp
            last = stamp
    return {"events": sum(counter.values()), "types": dict(sorted(counter.items())),
            "first": first, "last": last}


def inspect():
    source_names = sorted(BASE.glob("17-b2-convergencia-*.csv"))
    baseline = BASE / "b3-linea-base/b3-resumen-convergencia.json"
    event_files = sorted((BASE / "b3-live").glob("b3-wan-live-events*.jsonl"))
    report = {"origin": "NETLAB360_b4_real_files_audit",
              "scope": "historical_observed_files_only",
              "files": [], "events_by_type": {}, "warnings": []}
    counters = Counter()
    for f in source_names:
        assert f.is_file() and not f.is_symlink()
        info = csv_summary(f)
        report["files"].append({"name": str(f), "kind": "raw_icmp_csv",
                                "sha256": digest(f), **info})
    if baseline.is_file():
        raw = json.loads(baseline.read_text(encoding="utf-8"))
        assert raw.get("tipo") == "analisis_retrospectivo"
        total = raw.get("muestras_totales")
        assert isinstance(total, int) and total > 0
        assert isinstance(raw.get("fases"), dict)
        report["files"].append({"name": str(baseline), "kind": "derived_historical_summary",
                                "sha256": digest(baseline), "samples": total,
                                "phase_names": sorted(raw["fases"])})
    else:
        report["warnings"].append("Resumen B3 retrospectivo no encontrado")
    for f in event_files:
        assert f.is_file() and not f.is_symlink()
        info = jsonl_summary(f)
        counters.update(info["types"])
        report["files"].append({"name": str(f), "kind": "exporter_real_events",
                                "sha256": digest(f), **info})
    report["events_by_type"] = dict(sorted(counters.items()))
    report["total_event_rows"] = sum(counters.values())
    report["raw_icmp_csv_count"] = len(source_names)
    report["exporter_jsonl_count"] = len(event_files)
    # Un log de TRANSICIONES no incluye intervalos normales entre eventos.
    report["independent_normal_labels_available"] = False
    report["ml_supervised_evaluation_ready"] = False
    report["decision"] = "AUDITORIA_REQUIERE_ETIQUETAS_Y_MUESTRAS_NORMALES_INDEPENDIENTES"
    if not source_names:
        report["warnings"].append("Faltan CSV originales ICMP, no reconstruir desde resumen")
    if not event_files:
        report["warnings"].append("No existen logs JSONL de eventos en carpeta esperada")
    if not counters:
        report["warnings"].append("Sin eventos útiles para evaluar incidentes")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true",
                        help="Guardar resultado fuera del repositorio")
    args = parser.parse_args()
    report = inspect()
    print("========== INICIO CAPTURA B4_01_Auditoria_Datos_Reales ==========")
    print("TIPO_FUENTE=RETROSPECTIVA_Y_EVENTOS_REALES")
    print("CSV_ICMP_ENCONTRADOS=" + str(report["raw_icmp_csv_count"]))
    print("JSONL_EVENTOS_ENCONTRADOS=" + str(report["exporter_jsonl_count"]))
    for entry in report["files"]:
        meta = "filas=" + str(entry["rows"]) if "rows" in entry else (
            "eventos=" + str(entry["events"]) if "events" in entry else
            "muestras=" + str(entry["samples"]))
        print(f"FUENTE={entry['kind']} | archivo={Path(entry['name']).name} | {meta}")
        print("SHA256=" + entry["sha256"])
    print("EVENTOS_POR_TIPO=" + json.dumps(report["events_by_type"], sort_keys=True))
    print("MUESTRAS_NORMALES_ETIQUETADAS_INDEPENDIENTEMENTE=NO")
    print("MODELO_ML_EVALUADO=NO")
    print("DECISION_B4=" + report["decision"])
    for warning in report["warnings"]:
        print("AVISO_DATOS=" + warning)
    if args.save:
        OUTPUT.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        assert not OUTPUT.is_symlink()
        import os
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=OUTPUT.parent,
                                prefix="inventario-", suffix=".tmp", delete=False) as tmp:
            json.dump(report, tmp, ensure_ascii=False, indent=2)
            tmp.write("\n")
            temp_path = Path(tmp.name)
        temp_path.chmod(0o600)
        os.replace(temp_path, OUTPUT)
        print("REPORTE_LOCAL=" + str(OUTPUT))
    print("AUDITORIA_B4_DATOS=OK")
    print("========== FIN CAPTURA B4_01_Auditoria_Datos_Reales ==========")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, AssertionError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit("AUDITORIA_B4_DATOS=ERROR: " + str(exc))
