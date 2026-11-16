#!/usr/bin/env python3
"""Importacion segura del lote06 IaC/B4, 24 PNG originales en carpeta plana.

Modo --verificar: solo lee ZIP y repositorio. Modo --importar: tras comprobar
hashes y ausencia de colisiones, incorpora 24 PNG y manifiesto CSV.
No manipula datos de red ni estado OpenTofu. ZIP permanece fuera del repo.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
ZIP_NAME = "NETLAB360_LOTE06_IAC_B4_24PNG_AUDITADOS_2026-10-13.zip"
ZIP_SHA = "803ee03050a2261e938c56ed1c266097639c357f3fc77882a8a18eb5330bc781"
CSV_NAME = "MANIFIESTO_SHA256_NETLAB360_LOTE06_IAC_B4_24PNG.csv"
CSV_SHA = "fbf6b9567ad6249a071ab9b53ba89368d0c0ab275b84b5a00d82eb4e85718c7f"
CAPTURAS = ROOT / "evidencias/capturas"
MANIFIESTOS = ROOT / "evidencias/manifiestos"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    exclusive = parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("--verificar", action="store_true")
    exclusive.add_argument("--importar", action="store_true")
    parser.add_argument("--zip", type=Path, default=Path.home() / ZIP_NAME)
    args = parser.parse_args()
    source = args.zip
    assert source.is_file() and not source.is_symlink(), f"ZIP inexistente o symlink: {source}"
    assert sha(source.read_bytes()) == ZIP_SHA, "SHA256 del ZIP diferente"
    assert CAPTURAS.is_dir() and MANIFIESTOS.is_dir(), "Estructura Git no encontrada"
    assert not any(p.is_dir() for p in CAPTURAS.iterdir()), "Subcarpetas no esperadas"
    existentes = {p.name for p in CAPTURAS.glob("*.png")}
    assert len(existentes) == 62, "Se esperan exactamente 62 PNG historicos"
    assert len(list(MANIFIESTOS.glob("*.csv"))) == 6, "Se esperan seis CSV historicos"
    assert not (MANIFIESTOS / CSV_NAME).exists(), "Manifiesto lote06 ya importado"

    with ZipFile(source) as z:
        assert z.testzip() is None, "ZIP corrupto"
        manifest = z.read(CSV_NAME)
        assert sha(manifest) == CSV_SHA, "SHA256 manifiesto incorrecto"
        records = list(csv.DictReader(io.StringIO(manifest.decode("utf-8"))))
        assert len(records) == 24
        names = [r["archivo"] for r in records]
        assert len(set(names)) == 24, "Nombres duplicados"
        assert sum(n.startswith("B4_") for n in names) == 13
        assert sum(n.startswith("IAC_") for n in names) == 11
        assert not (set(names) & existentes), "Colision contra evidencias antiguas"
        assert all(Path(n).name == n and n.endswith(".png") for n in names), "Nombre inseguro"
        expected = {"capturas/" + n for n in names} | {CSV_NAME, "LEEME_LOTE06.txt"}
        assert set(z.namelist()) == expected, "Contenido ZIP no esperado"
        payload = {}
        for r in records:
            n = r["archivo"]
            data = z.read("capturas/" + n)
            assert data[:8] == b"\x89PNG\r\n\x1a\n", f"PNG invalido: {n}"
            assert sha(data) == r["sha256"], f"SHA256 incorrecto: {n}"
            assert len(data) == int(r["bytes"]), f"Tamano diferente: {n}"
            assert r["dictamen"] in ("VALIDA", "VALIDA_CON_OBSERVACION")
            payload[n] = data

    print("ZIP_LOTE06_INTEGRO=SI")
    print("MANIFIESTO_SHA256=OK")
    print("PNG_VALIDOS=24")
    print("COLISIONES=0")
    if args.verificar:
        print("LOTE06_MODO=SOLO_LECTURA")
        return

    created = []
    try:
        for name, data in payload.items():
            target = CAPTURAS / name
            with target.open("xb") as f:
                f.write(data)
            created.append(target)
        target = MANIFIESTOS / CSV_NAME
        with target.open("xb") as f:
            f.write(manifest)
        created.append(target)
    except BaseException:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    assert len(list(CAPTURAS.glob("*.png"))) == 86
    assert len(list(MANIFIESTOS.glob("*.csv"))) == 7
    print("LOTE06_IMPORTADO=SI")
    print("PNG_DIRECTOS=86")
    print("CSV_MANIFIESTOS=7")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, AssertionError) as error:
        print("LOTE06_ERROR=" + str(error), file=sys.stderr)
        raise SystemExit(1)
