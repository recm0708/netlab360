#!/usr/bin/env python3
"""S05 P1: recuperar los cuatro originales de TAR a carpeta NUEVA, sin sobrescribir."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import tarfile

BASE = Path.home() / "netlab360-bootstrap/s05/evidencias"
TAR = BASE / "NETLAB360_S05_P1_LACP_EVIDENCIA_TECNICA_20261110.tar.gz"
OUT = BASE / "lacp-p1-historico-verificado-20261110"
EXPECTED = {
    "S05_P1_20261110-110047.log": "dcdeef8ba087d9aace2eb0159cc815306bf3970cc983eb286dd1bc5541bfdbbc",
    "01_un_flujo.json": "c35de996410cdff0b9e158975188c9133e77724acbe3364bc8632dbb7a5b5adb",
    "02_ocho_flujos.json": "cf078a66abb4e44492fe140fa9d5e8b8598e46ca4b12bd7bd955620059bd949a",
    "03_falla_retorno.json": "a14c6b3343d801cb73d81af6a38e4423edafbfaf56026cf139658d2335bf4579",
}
MAX_BYTES = 32 * 1024 * 1024
MANIFEST = "MANIFIESTO_RECUPERACION_ORIGINALES_P1_20261110.sha256"


def verified_members(tar_path: Path, expected: dict[str, str]) -> dict[str, bytes]:
    if not tar_path.is_file() or tar_path.is_symlink():
        raise RuntimeError("TAR no es archivo regular o está ausente")
    found: dict[str, bytes] = {}
    with tarfile.open(tar_path, "r:gz") as archive:
        for member in archive:
            name = Path(member.name).name
            if name not in expected:
                continue
            if not member.isfile() or name in found or not 0 <= member.size <= MAX_BYTES:
                raise RuntimeError(f"Miembro inseguro, duplicado o excesivo: {name}")
            content = archive.extractfile(member)
            if content is None:
                raise RuntimeError(f"No puede leerse: {name}")
            with content:
                raw = content.read(MAX_BYTES + 1)
            if len(raw) != member.size:
                raise RuntimeError(f"Tamaño no coincide: {name}")
            digest = hashlib.sha256(raw).hexdigest()
            if digest != expected[name]:
                raise RuntimeError(f"SHA no coincide: {name}")
            found[name] = raw
    if set(found) != set(expected):
        raise RuntimeError(f"Miembros esperados ausentes: {sorted(set(expected) - set(found))}")
    return found


def recover(data: dict[str, bytes], dest: Path) -> None:
    if dest.exists() or dest.is_symlink():
        raise RuntimeError("Destino ya existe; no sobrescribir evidencia recuperada")
    dest.mkdir(mode=0o700, parents=False, exist_ok=False)
    for name, raw in data.items():
        target = dest / name
        with target.open("xb") as stream:
            os.chmod(target, 0o600)
            stream.write(raw)
        if hashlib.sha256(target.read_bytes()).hexdigest() != EXPECTED[name]:
            raise RuntimeError("Verificación pos-escritura falló: " + name)
        print("P1_ORIGINAL_RECUPERADO=", name, "SHA256=", EXPECTED[name], flush=True)
    manifest = dest / MANIFEST
    lines = [f"{EXPECTED[name]}  {name}\n" for name in sorted(EXPECTED)]
    with manifest.open("x", encoding="utf-8") as stream:
        os.chmod(manifest, 0o600)
        stream.writelines(lines)
    print("P1_DESTINO=", dest)
    print("P1_MANIFIESTO_NUEVO=", manifest)
    print("S05_P1_RECUPERACION=OK_4_ORIGINALES")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--recover", action="store_true")
    args = parser.parse_args()
    found = verified_members(TAR, EXPECTED)
    for name in sorted(found):
        print("P1_TAR_ORIGINAL_SHA=OK", name, EXPECTED[name])
    if args.check:
        print("S05_P1_RECUPERACION_PRECHECK=OK_SIN_ESCRIBIR")
    else:
        if OUT.parent != BASE or not BASE.is_dir():
            raise RuntimeError("Ubicación de recuperación inesperada")
        recover(found, OUT)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, tarfile.TarError) as exc:
        print(f"S05_P1_RECUPERACION_ERROR={type(exc).__name__}:{exc}", file=sys.stderr)
        sys.exit(2)
