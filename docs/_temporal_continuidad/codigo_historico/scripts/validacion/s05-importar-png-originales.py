#!/usr/bin/env python3
"""S05: cotejar ZIP de 70 PNG originales contra CSV Windows y versionarlos sin sobrescribir."""
from __future__ import annotations
import argparse
import csv
import hashlib
from pathlib import Path
import re
import stat
import subprocess
import sys
import zipfile

REPO = Path(__file__).resolve().parents[2]
DEST = REPO / "evidencias/capturas/fase5"
BASE = Path.home() / "netlab360-bootstrap/s05/importacion-png"
SOURCE_CSV = BASE / "NETLAB360_S05_PNG_20261115-110810.csv"
SOURCE_ZIP = BASE / "NETLAB360_S05_70PNG_ORIGINALES.zip"
MANIFEST = "MANIFIESTO_SHA256_S05_PNG_20261115.sha256"
INVENTORY = "INVENTARIO_S05_PNG_VERIFICADO_20261115.csv"
ANCHOR = "d3506bdb33d28037f8860bd53bd1bf3bc3c6b33ff7083d58c80e5e377b1cccfe"
PNG_NAME = re.compile(r"^S05_[A-Za-z0-9][A-Za-z0-9_.-]*\.png$")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_csv(path: Path, expected_count: int = 70) -> dict[str, tuple[int, str]]:
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("CSV original ausente o simbólico")
    items = {}
    with path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name, raw_size, raw_hash = row["Archivo"], row["Bytes"], row["SHA256"]
            if not PNG_NAME.fullmatch(name) or name in items:
                raise RuntimeError("Nombre inválido o duplicado: " + name)
            size, digest = int(raw_size), raw_hash.lower()
            if not 8 <= size <= 5_000_000 or not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise RuntimeError("Metadatos inválidos: " + name)
            items[name] = size, digest
    if len(items) != expected_count:
        raise RuntimeError(f"Se esperaban {expected_count}, se hallaron {len(items)}")
    if len({v[1] for v in items.values()}) != len(items):
        raise RuntimeError("Hay SHA duplicados en el inventario")
    return items


def verify_zip(zip_path: Path, records: dict[str, tuple[int, str]]) -> dict[str, bytes]:
    if not zip_path.is_file() or zip_path.is_symlink():
        raise RuntimeError("ZIP original ausente o simbólico")
    verified = {}
    with zipfile.ZipFile(zip_path) as z:
        members = z.infolist()
        if len(members) != len(records):
            raise RuntimeError("Cantidad ZIP/CSV no coincide")
        for member in members:
            name = member.filename
            mode = (member.external_attr >> 16) & 0o170000
            if name not in records or name in verified or member.is_dir() or mode == stat.S_IFLNK:
                raise RuntimeError("Entrada ZIP ajena, insegura o duplicada: " + name)
            size, digest = records[name]
            if size != member.file_size:
                raise RuntimeError("Tamaño ZIP/CSV distinto: " + name)
            data = z.read(member)
            if not data.startswith(PNG_MAGIC) or len(data) != size:
                raise RuntimeError("Formato PNG/tamaño inválido: " + name)
            if hashlib.sha256(data).hexdigest() != digest:
                raise RuntimeError("SHA256 PNG distinto: " + name)
            verified[name] = data
    if set(verified) != set(records):
        raise RuntimeError("Inventario original incompleto")
    return verified


def import_png(items: dict[str, bytes], records: dict[str, tuple[int, str]], dest: Path) -> None:
    if not dest.is_dir() or dest.is_symlink():
        raise RuntimeError("Destino Git inexistente o simbólico")
    manifest = dest / MANIFEST
    inventory = dest / INVENTORY
    if manifest.exists() or inventory.exists() or any((dest / name).exists() for name in items):
        raise RuntimeError("Hay evidencia previa: no sobrescribir/importar dos veces")
    for name in sorted(items):
        with (dest / name).open("xb") as f:
            f.write(items[name])
        if hashlib.sha256((dest / name).read_bytes()).hexdigest() != records[name][1]:
            raise RuntimeError("Fallo tras copiar: " + name)
    with manifest.open("x", encoding="utf-8") as f:
        for name in sorted(records):
            f.write(f"{records[name][1]}  {name}\n")
    with inventory.open("x", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["archivo", "bytes", "sha256"])
        for name in sorted(records):
            size, digest = records[name]
            w.writerow([name, size, digest])
    print("S05_PNG_70_IMPORTADOS_GIT=OK")
    print("S05_PNG_MANIFIESTO=", manifest)
    print("S05_PNG_INVENTARIO_VERSIONADO=", inventory)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--import", dest="do_import", action="store_true")
    args = p.parse_args()
    records = read_csv(SOURCE_CSV)
    anchor = records.get("S05_63_NOC_LACP_Multisede_y_Faucet_Operativos.png")
    if anchor != (155432, ANCHOR):
        raise RuntimeError("Ancla de captura 63 original no coincide")
    data = verify_zip(SOURCE_ZIP, records)
    print("S05_PNG_CSV_ENTRADAS=", len(records))
    print("S05_PNG_BYTES_TOTALES=", sum(size for size, _ in records.values()))
    print("S05_PNG_ZIP_SHA256=70_70_VERIFICADOS")
    if args.check:
        print("S05_PNG_MODO=SOLO_LECTURA")
        return
    status = subprocess.check_output(
        ["git", "-C", str(REPO), "status", "--porcelain"], text=True
    )
    if status.strip():
        raise RuntimeError("Git tiene archivos modificados o sin seguimiento")
    import_png(data, records, DEST)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError, zipfile.BadZipFile,
            subprocess.CalledProcessError) as exc:
        print(f"S05_PNG_IMPORT_ERROR={type(exc).__name__}:{exc}", file=sys.stderr)
        sys.exit(2)
