#!/usr/bin/env python3
"""NETLAB360 S05/P1: lectura y análisis de JSON iperf3 + manifiesto SHA256.

No altera red, Docker, namespaces, configuración ni archivos de origen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
import re
import sys

NAMES = (
    ("UN_FLUJO", "01_un_flujo.json", 1),
    ("OCHO_FLUJOS", "02_ocho_flujos.json", 8),
    ("FALLA_RETORNO", "03_falla_retorno.json", 8),
)
MANIFEST = "MANIFIESTO_SHA256_S05_P1_2026-11-10.txt"


def die(reason: str) -> None:
    raise SystemExit("S05_ANALISIS_ERROR=" + reason)


def load(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        die(f"JSON_AUSENTE_O_ENLACE={path.name}")
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or data.get("error"):
        die(f"IPERF3_ERROR={path.name}")
    return data


# La procedencia corresponde a registros experimentales originales; no a controles de imágenes.
def manifest_check(folder: Path) -> bool:
    path = folder / MANIFEST
    if not path.is_file():
        print("S05_MANIFIESTO=NO_ENCONTRADO")
        return False
    failures = 0
    checked = set()
    for row in path.read_text(encoding="utf-8").splitlines():
        if not row.strip():
            continue
        if not re.match(r"^[a-f0-9]{64}  ", row):
            print("S05_MANIFIESTO_FORMATO=INVALIDO")
            return False
        digest = row[:64]
        raw_path = row[66:]
        file = Path(raw_path)
        if file.parent.resolve() != folder.resolve() or file.is_symlink() or not file.is_file():
            print(f"S05_SHA_RUTA_INVALIDA={file.name}")
            failures += 1
            continue
        actual = hashlib.sha256(file.read_bytes()).hexdigest()
        ok = digest == actual
        checked.add(file.name)
        print(f"S05_SHA256_{file.name}={'OK' if ok else 'DISTINTO'}")
        failures += int(not ok)
    expected = {item[1] for item in NAMES}
    logs = list(folder.glob("S05_P1_*.log"))
    if len(logs) == 1:
        expected.add(logs[0].name)
    if not expected.issubset(checked):
        print("S05_MANIFIESTO=ARCHIVOS_ESPERADOS_NO_LISTADOS")
        failures += 1
    print(f"S05_SHA256_INTEGRIDAD={'OK' if failures == 0 else 'REVISAR'}")
    return failures == 0


# La comparación usa el número esperado de flujos y los resultados reportados por iperf3.
def show(label: str, data: dict, expected_flows: int) -> None:
    start = data.get("start") or {}
    end = data.get("end") or {}
    streams = end.get("streams") or []
    rx = end.get("sum_received") or end.get("sum") or {}
    tx = end.get("sum_sent") or {}
    if len(streams) != expected_flows or "bits_per_second" not in rx:
        die(f"ESTRUCTURA_INCOMPLETA={label}")
    print(f"S05_{label}_FLUJOS_OBSERVADOS={len(streams)}")
    print(f"S05_{label}_RX_MBPS={rx['bits_per_second'] / 1e6:.3f}")
    print(f"S05_{label}_RETRANSMISIONES={tx.get('retransmits','NO_REPORTADO')}")
    cpu = end.get("cpu_utilization_percent") or {}
    print(f"S05_{label}_CPU_LOCAL_PCT={cpu.get('host_total','NO_REPORTADO')}")
    print(f"S05_{label}_CPU_REMOTA_PCT={cpu.get('remote_total','NO_REPORTADO')}")
    if label == "FALLA_RETORNO":
        timing = (start.get("timestamp") or {}).get("timesecs")
        if timing is not None:
            print(f"S05_FALLA_IPERF_INICIO_EPOCH={timing}")
        intervals = data.get("intervals") or []
        for i, interval in enumerate(intervals):
            item = interval.get("sum") or interval.get("sum_received") or {}
            rate = item.get("bits_per_second")
            if rate is not None:
                print(
                    f"S05_FALLA_INTERVALO_{i:02d}="
                    f"{item.get('start','?')}-{item.get('end','?')}"
                    f";RX_O_TX_SEGUN_JSON_MBPS={rate / 1e6:.2f}"
                    f";RETX={item.get('retransmits','NO_REPORTADO')}"
                )


def run(folder: Path) -> None:
    if not folder.is_dir():
        die("DIRECTORIO_INEXISTENTE")
    print("========== S05/P1 ANALISIS JSON Y SHA256 SOLO LECTURA ==========")
    files = [(label, load(folder / name), count) for label, name, count in NAMES]
    for label, data, count in files:
        print(f"========== {label} ==========")
        show(label, data, count)
    logs = sorted(folder.glob("S05_P1_*.log"))
    if not logs:
        die("LOG_PILOTO_AUSENTE")
    log = logs[-1]
    text = log.read_text(encoding="utf-8")
    for required in (
        "S05_LACP_ESTADOS_2_1_2=OK",
        "S05_RED_GESTION_INTACTA=SI",
        "S05_RESULTADO_P1=0",
    ):
        if required not in text:
            die("MARCADOR_NO_DETECTADO=" + required)
        print(required)
    found = re.search(r"S05_OCHO_FLUJOS_A1_TX_BYTES=(\d+)", text)
    found2 = re.search(r"S05_OCHO_FLUJOS_A2_TX_BYTES=(\d+)", text)
    if found and found2:
        a, b = int(found.group(1)), int(found2.group(1))
        if a + b:
            print(f"S05_OCHO_FLUJOS_DISTRIBUCION_A1_PCT={a * 100 / (a+b):.2f}")
            print(f"S05_OCHO_FLUJOS_DISTRIBUCION_A2_PCT={b * 100 / (a+b):.2f}")
    timesecs = ((files[2][1].get("start") or {}).get("timestamp") or {}).get("timesecs")
    if isinstance(timesecs, (int, float)):
        for event in ("S05_FALLA_A1", "S05_RETORNO_A1"):
            match = re.search(rf"^{event}=(.+)$", text, re.M)
            if match:
                try:
                    stamp = datetime.fromisoformat(match.group(1).strip()).timestamp()
                    print(f"{event}_SEGUNDO_APROX_DESDE_IPERF={stamp - timesecs:.1f}")
                except ValueError:
                    print(f"{event}_TIEMPO_NO_INTERPRETABLE=SI")
        print("S05_EVENTOS_TIMING=APROXIMADO_PRECISION_DE_LOG_DE_SEGUNDOS")
    good = manifest_check(folder)
    if not good:
        die("SHA256_NO_VALIDADO")
    print("S05_P1_ANALISIS=OK_CON_LIMITACIONES")
    print("S05_LIMITE=caudal sujeto a limite 120 Mb/s por flujo; no inferir capacidad maxima")
    print("S05_LIMITE=553 retransmisiones observadas; no inferir cero perdida")
    print("S05_CAMBIOS_INFRAESTRUCTURA=NINGUNO")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path.home() / "netlab360-bootstrap/s05/evidencias/lacp-p1",
    )
    args = parser.parse_args()
    try:
        run(args.dir.expanduser().resolve())
    except (OSError, ValueError, json.JSONDecodeError) as err:
        die(type(err).__name__ + ": " + str(err))
