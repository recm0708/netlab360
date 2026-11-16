#!/usr/bin/env python3
"""Importa siete PNG S04 lote03 solo tras cotejar SHA256 contra CSV Windows.

No ejecuta git commit/push ni modifica servicios/red. --check es solo lectura.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
from pathlib import Path
import socket
import struct
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path.home() / "NETLAB360_S04_LOTE03_7PNG_ORIGINALES_2026-10-27.zip"
ORIGIN = "ORIGEN_SHA256_S04_LOTE03_2026-10-27.csv"
MANIFEST = "evidencias/manifiestos/MANIFIESTO_SHA256_S04_LOTE03_2026-10-27.csv"
NAMES = (
    "S04_12_Historico_Prometheus_G3_Persistente_Tras_Reinicio.png",
    "S04_13_NOC_Fuente_No_Disponible_UNKNOWN.png",
    "S04_14_NOC_Recuperacion_Fuente_Observabilidad.png",
    "S04_15_NOC_Historial_Incidentes_G3_Persistente-1.png",
    "S04_15_NOC_Historial_Incidentes_G3_Persistente-2.png",
    "S04_16_Persistencia_SQLite_Historial_NOC_Tras_Reinicio.png",
    "S04_17_Indicadores_SLI_SLO_Observabilidad.png",
)
FIELDS = ("ruta_relativa", "sha256", "bytes", "ancho_px", "alto_px",
          "clasificacion", "observacion")
NOTES = (
    "Series WAN y firing conservadas tras reinicio real de Prometheus",
    "Fuente observabilidad UNKNOWN y alarma exporter firing sin falsas WAN",
    "Exporter recuperado y NOC activo sin alarmas",
    "Historial NOC con transiciones reales G3, primera vista",
    "Historial NOC con transiciones reales G3, segunda vista",
    "SQLite persistente tras reinicio del proceso NOC",
    "SLI observados 15 y 60 minutos con SLO 99% propuesto",
)


def check_zip(archive: Path, repo: Path = ROOT) -> tuple[list[tuple[Path, bytes]], bytes]:
    if not archive.is_file() or archive.is_symlink():
        raise ValueError("ZIP ausente o simbolico")
    with ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Archivo ZIP CRC invalido")
        entries = z.namelist()
        if (len(entries) != 8 or len(set(entries)) != 8
                or set(entries) != set(NAMES) | {ORIGIN}):
            raise ValueError("Se esperan siete PNG y el CSV origen, sin otros archivos")
        manifest_rows = list(csv.DictReader(
            io.StringIO(z.read(ORIGIN).decode("utf-8-sig"))))
        if len(manifest_rows) != 7:
            raise ValueError("CSV origen distinto de siete entradas")
        indices = {r.get("Name"): r for r in manifest_rows}
        if len(indices) != 7 or set(indices) != set(NAMES):
            raise ValueError("CSV origen tiene nombres repetidos o inesperados")
        checked = []
        records = []
        for filename, note in zip(NAMES, NOTES):
            r = indices[filename]
            data = z.read(filename)
            digest = hashlib.sha256(data).hexdigest()
            try:
                size = int(r["Length"])
            except (KeyError, ValueError, TypeError) as exc:
                raise ValueError("Bytes origen ilegibles") from exc
            if (digest != str(r["SHA256"]).lower()
                    or size != len(data) or size < 1024):
                raise ValueError("SHA256/bytes fuente distintos: " + filename)
            if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("PNG invalido: " + filename)
            w, h = struct.unpack(">II", data[16:24])
            if not (100 <= w <= 10000 and 100 <= h <= 20000):
                raise ValueError("Dimensiones invalidas: " + filename)
            rel = Path("evidencias/capturas/fase4") / filename
            dest = repo / rel
            if not dest.parent.is_dir() or dest.is_symlink() or dest.exists():
                raise ValueError("Ruta PNG inexistente o ya publicada: " + str(rel))
            checked.append((dest, data))
            records.append(dict(zip(FIELDS, (
                rel.as_posix(), digest, str(size), str(w), str(h),
                "complementaria" if filename.endswith("Persistente-2.png")
                else "obligatoria", note))))
        target = repo / MANIFEST
        if (not target.parent.is_dir() or target.is_symlink()
                or target.exists()):
            raise ValueError("Manifiesto existente o ruta no segura")
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
        checked.append((target, buffer.getvalue().encode("utf-8")))
        return checked, z.read(ORIGIN)


def main() -> None:
    p = argparse.ArgumentParser()
    choice = p.add_mutually_exclusive_group(required=True)
    choice.add_argument("--check", action="store_true")
    choice.add_argument("--import", dest="do_import", action="store_true")
    args = p.parse_args()
    if socket.gethostname() != "netlab360-lab":
        raise ValueError("Solo VM NETLAB360")
    checked, origin = check_zip(ARCHIVE)
    print("========== S04 LOTE03 AUDITORIA ORIGEN WINDOWS ==========")
    print("S04_LOTE03_CRC_ZIP=OK")
    print("S04_LOTE03_HASH_WINDOWS_UBUNTU=7/7")
    print("S04_LOTE03_PNG_DIMENSIONES=7/7")
    print(f"S04_LOTE03_MANIFIESTO_BYTES={len(checked[-1][1])}")
    if args.do_import:
        for dest, data in checked:
            with dest.open("xb") as f:
                f.write(data)
        print("S04_LOTE03_PNG_IMPORTADAS=7/7")
        print("S04_LOTE03_MANIFIESTO_LF=OK")
        print("S04_LOTE03_IMPORTACION=OK")
    else:
        print("S04_LOTE03_PRECHECK=OK")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        print(f"S04_LOTE03_ERROR={type(exc).__name__}: {exc}")
        raise SystemExit(1)
