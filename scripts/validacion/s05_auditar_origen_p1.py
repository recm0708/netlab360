#!/usr/bin/env python3
"""NETLAB360 S05: investigar la procedencia de P1 SIN modificar originales.

Lee los JSON y manifiesto vigentes y busca el TAR historico.
No extrae, modifica, copia, renombra ni recalcula manifiestos.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import tarfile

BASE = Path.home() / "netlab360-bootstrap/s05/evidencias/lacp-p1"
EVIDENCE = BASE.parent
EXPECTED = {
    "S05_P1_20261110-110047.log": "dcdeef8ba087d9aace2eb0159cc815306bf3970cc983eb286dd1bc5541bfdbbc",
    "01_un_flujo.json": "c35de996410cdff0b9e158975188c9133e77724acbe3364bc8632dbb7a5b5adb",
    "02_ocho_flujos.json": "cf078a66abb4e44492fe140fa9d5e8b8598e46ca4b12bd7bd955620059bd949a",
    "03_falla_retorno.json": "a14c6b3343d801cb73d81af6a38e4423edafbfaf56026cf139658d2335bf4579",
}
MAX_MEMBER_BYTES = 32 * 1024 * 1024


def file_digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def archive_matches(path: Path, expected: dict[str, str]) -> dict[str, list[str]]:
    """Retorna hashes de miembros regulares por nombre base, sin extraerlos."""
    hashes = {name: [] for name in expected}
    with tarfile.open(path, "r:*") as archive:
        for member in archive:
            name = Path(member.name).name
            if name not in hashes or not member.isfile():
                continue
            if not (0 <= member.size <= MAX_MEMBER_BYTES):
                raise ValueError("Miembro fuera de limite: " + member.name)
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("No se puede leer el miembro: " + member.name)
            sha = hashlib.sha256()
            with stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    sha.update(block)
            hashes[name].append(sha.hexdigest())
    return hashes


def archives() -> list[Path]:
    candidate = EVIDENCE / "NETLAB360_S05_P1_LACP_EVIDENCIA_TECNICA_20261110.tar.gz"
    found = [candidate] if candidate.is_file() and not candidate.is_symlink() else []
    if EVIDENCE.is_dir():
        for path in sorted(EVIDENCE.rglob("*P1*.tar*")):
            if path.is_file() and not path.is_symlink() and path not in found:
                found.append(path)
            if len(found) >= 30:
                break
    return found


def run() -> int:
    print("========== NETLAB360 146B-A P1 AUDITORIA SOLO LECTURA ==========")
    print("BASE=", BASE)
    print("NO_EXTRAER=SI NO_REESCRIBIR_MANIFIESTO=SI")
    manifest = BASE / "MANIFIESTO_SHA256_S05_P1_2026-11-10.txt"
    print("MANIFIESTO_PRESENTE=", manifest.is_file() and not manifest.is_symlink())
    if manifest.is_file() and not manifest.is_symlink():
        for row in manifest.read_text(encoding="utf-8").splitlines():
            if row.strip():
                print("MANIFIESTO_ORIGINAL=", row)

    for name, expected in EXPECTED.items():
        path = BASE / name
        if not path.is_file() or path.is_symlink():
            print("ARCHIVO_ACTUAL=", name, "ESTADO=AUSENTE_O_SIMBOLICO")
            continue
        digest = file_digest(path)
        print("ARCHIVO_ACTUAL=", name, "BYTES=", path.stat().st_size,
              "SHA256=", digest, "COINCIDE_HISTORICO=", digest == expected)

    candidates = archives()
    print("TAR_CANDIDATOS=", len(candidates))
    correct_archive = False
    for archive_path in candidates:
        print("========== ARCHIVO_COMPRIMIDO=", archive_path, "==========")
        print("TAR_BYTES=", archive_path.stat().st_size)
        try:
            matches = archive_matches(archive_path, EXPECTED)
        except (OSError, ValueError, tarfile.TarError) as exc:
            print("TAR_ERROR=", type(exc).__name__, str(exc)[:250])
            continue
        unique = True
        for name, expected in EXPECTED.items():
            found = matches[name]
            ok = len(found) == 1 and found[0] == expected
            print("TAR_MIEMBRO=", name, "COINCIDE_HISTORICO=", ok,
                  "APARICIONES=", len(found), "SHA256=", ",".join(found))
            unique = unique and ok
        if unique:
            correct_archive = True
            print("TAR_P1_ORIGINAL_VERIFICADO=SI")
    if not correct_archive:
        print("S05_P1_ORIGEN=NO_LOCALIZADO_O_NO_VERIFICADO")
        print("S05_P1_AUDITORIA=REQUIERE_CONCILIACION")
        return 2
    print("S05_P1_ORIGEN=ARCHIVO_TAR_VALIDADO_SIN_EXTRACCION")
    print("S05_P1_AUDITORIA=ORIGINAL_CANDIDATO_LOCALIZADO")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    args = parser.parse_args()
    sys.exit(run())
