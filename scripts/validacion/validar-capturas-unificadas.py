#!/usr/bin/env python3
"""NETLAB360 — auditoría de capturas reales, organizada por fases.

Fase 1 conserva un catálogo oficial de PNG con SHA-256,
tamaño, nombre y hash Git. Los manifiestos de procedencia se conservan independientes del catálogo vigente.
Fases 2–8 admiten nueva evidencia solo con prefijos técnicos correctos.
No modifica archivos, no requiere Docker y no crea capturas sintéticas.
"""
from __future__ import annotations

import csv
import hashlib
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURAS = ROOT / "evidencias" / "capturas"
MANIFIESTOS = ROOT / "evidencias" / "manifiestos"
MAPA = MANIFIESTOS / "MAPA_RENOMBRADO_FASE1_2026-10-25.csv"
PLAN = MANIFIESTOS / "PLAN_CARGA_CAPTURAS_2026-10-25.csv"
LOTE = MANIFIESTOS / "MANIFIESTO_SHA256_CAPTURAS_2026-10-25.csv"
S04_LOTE01 = "MANIFIESTO_SHA256_S04_LOTE01_2026-10-26.csv"
DYNAMIC = re.compile(r"MANIFIESTO_SHA256_S(0[4-8])_LOTE[0-9]{2}_[0-9]{4}-[0-9]{2}-[0-9]{2}\.csv")
HISTORICOS = {
    "MANIFIESTO_SHA256_LOTE01.csv",
    "MANIFIESTO_SHA256_LOTE02.csv",
    "MANIFIESTO_SHA256_NETLAB360_LOTE03_20PNG.csv",
    "MANIFIESTO_SHA256_NETLAB360_LOTE04_LACP_13PNG.csv",
    "MANIFIESTO_SHA256_NETLAB360_LOTE05_DUALNIC_5PNG.csv",
    "MANIFIESTO_SHA256_NETLAB360_LOTE06_IAC_B4_24PNG.csv",
    "MAPA_ORIGEN_A_RAIZ_2026-10-13.csv",
}


def file_hashes(path: Path) -> tuple[str, str, int]:
    data = path.read_bytes()
    git_input = f"blob {len(data)}\0".encode() + data
    return hashlib.sha256(data).hexdigest(), hashlib.sha1(git_input).hexdigest(), len(data)


def main() -> None:
    assert CAPTURAS.is_dir() and MANIFIESTOS.is_dir(), "Faltan directorios de evidencias"
    assert MAPA.is_file(), "Falta mapa nuevo de rutas S01"
    permitidos = HISTORICOS | {MAPA.name, PLAN.name}
    if LOTE.is_file():
        permitidos.add(LOTE.name)
    presentes = {p.name for p in MANIFIESTOS.glob("*.csv")}
    nuevos = {name for name in presentes if DYNAMIC.fullmatch(name)}
    assert presentes == permitidos | nuevos and HISTORICOS <= presentes, (
        "Manifiestos históricos alterados o incompletos; revisar lotes S04-S08"
    )
    with MAPA.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 79, f"Esperadas 79 capturas S01 del catálogo; mapa tiene {len(rows)}"
    assert {p.name for p in CAPTURAS.iterdir() if p.is_dir()} == {
        f"fase{i}" for i in range(1, 9)
    }, "Se esperaban directorios fase1 a fase8"

    targets: set[str] = set()
    originals: set[str] = set()
    for row in rows:
        prior = Path(row["ruta_anterior"])
        rel = Path(row["ruta_actual"])
        assert prior.parent == Path("evidencias/capturas")
        assert rel.parent == Path("evidencias/capturas/fase1")
        assert rel.name.startswith("S01_") and rel.suffix.lower() == ".png"
        assert not (ROOT / prior).exists(), f"Ruta anterior sin retirar: {prior}"
        assert row["ruta_anterior"] not in originals
        assert row["ruta_actual"] not in targets
        targets.add(row["ruta_actual"])
        originals.add(row["ruta_anterior"])
        full = ROOT / rel
        assert full.is_file() and not full.is_symlink(), f"Captura ausente: {rel}"
        digest, git_blob, size = file_hashes(full)
        assert digest == row["sha256"], f"SHA-256 diferente: {rel}"
        assert git_blob == row["git_blob_sha"], f"Blob Git diferente: {rel}"
        assert size == int(row["bytes"]) and size > 0, f"Tamaño inválido: {rel}"

    extras = set()
    fase_esperada = {i: set() for i in range(1, 9)}
    if LOTE.is_file():
        assert PLAN.is_file(), "Falta el plan original del lote"
        with LOTE.open(encoding="utf-8", newline="") as stream:
            aprobadas = list(csv.DictReader(stream))
        with PLAN.open(encoding="utf-8", newline="") as stream:
            plan = list(csv.DictReader(stream))
        assert len(aprobadas) == len(plan) == 21, "Lote de 21 fotos incompleto"
        assert {x["ruta_actual"] for x in aprobadas} == {
            x["ruta_actual"] for x in plan
        }, "Rutas de lote distintas del plan"
        for row in aprobadas:
            ruta = Path(row["ruta_actual"])
            fase = int(ruta.parent.name.removeprefix("fase"))
            assert 1 <= fase <= 3
            assert ruta.parent == Path(f"evidencias/capturas/fase{fase}")
            assert ruta.name.startswith(f"S{fase:02d}_") and ruta.suffix.lower() == ".png"
            assert row["ruta_actual"] not in targets and row["ruta_actual"] not in extras
            assert not ruta.is_absolute() and ".." not in ruta.parts
            original = ROOT / ruta
            assert original.is_file() and not original.is_symlink()
            sha256, blob, size = file_hashes(original)
            assert (sha256 == row["sha256"] and
                    blob == row["git_blob_sha"] and
                    size == int(row["bytes"]) and size > 0), f"SHA del lote diferente: {ruta}"
            extras.add(row["ruta_actual"])
            fase_esperada[fase].add(row["ruta_actual"])
        assert [len(fase_esperada[i]) for i in (1, 2, 3)] == [4, 9, 8]
        print("LOTE_20261025_SHA256_Y_BLOB=21/21")
    else:
        assert PLAN.is_file(), "Falta plan de lote previsto"

    # Lotes S04-S08: aceptar solo manifiestos de fase cuya ruta y
    # SHA-256, tamano, y dimensiones de cada captura puedan comprobarse.
    expected_dynamic = {i: set() for i in range(4, 9)}
    if list((CAPTURAS / "fase4").glob("*.png")):
        assert S04_LOTE01 in nuevos, "Primer lote S04 sin manifiesto"
    for name in sorted(nuevos):
        match = DYNAMIC.fullmatch(name)
        assert match is not None
        fase = int(match.group(1))
        manifest = MANIFIESTOS / name
        assert manifest.is_file() and not manifest.is_symlink()
        with manifest.open(encoding="utf-8-sig", newline="") as stream:
            registros = list(csv.DictReader(stream))
        assert registros, f"Manifiesto vacio: {name}"
        if name == S04_LOTE01:
            assert len(registros) == 7, "Primer lote S04 distinto de 7 PNG"
        for row in registros:
            ruta = Path(row["ruta_relativa"])
            assert not ruta.is_absolute() and ".." not in ruta.parts
            assert ruta.parent == Path(f"evidencias/capturas/fase{fase}")
            assert ruta.name.startswith(f"S{fase:02d}_") and ruta.suffix.lower() == ".png"
            key = ruta.as_posix()
            assert key not in expected_dynamic[fase], f"Captura duplicada: {key}"
            fichero = ROOT / ruta
            assert fichero.is_file() and not fichero.is_symlink()
            digest, _blob, size = file_hashes(fichero)
            assert digest == row["sha256"] and size == int(row["bytes"]) and size > 0, (
                f"SHA-256 o bytes diferentes: {ruta}"
            )
            with fichero.open("rb") as image:
                header = image.read(24)
            assert header[:8] == b"\x89PNG\r\n\x1a\n", f"Formato PNG invalido: {ruta}"
            width, height = struct.unpack(">II", header[16:24])
            assert width == int(row["ancho_px"]) and height == int(row["alto_px"])
            assert width > 0 and height > 0, f"Dimensiones invalidas: {ruta}"
            expected_dynamic[fase].add(key)
        print(f"LOTE_{name}_SHA256_Y_DIMENSIONES={len(registros)}/{len(registros)}")

    actual_s01 = {p.relative_to(ROOT).as_posix() for p in
                  (CAPTURAS / "fase1").glob("*.png")}
    assert actual_s01 == targets | fase_esperada[1], "Fase 1: faltan PNG o hay extras sin mapear"
    assert not list(CAPTURAS.glob("*.png")), "Persisten PNG fuera de las carpetas fase"
    print("S01_PNG_RENOMBRADOS=79/79")
    print("S01_SHA256_Y_GIT_BLOB_CONSERVADOS=79/79")
    print(f"MANIFIESTOS_HISTORICOS={len(HISTORICOS)}/7")

    for i in range(2, 9):
        folder = CAPTURAS / f"fase{i}"
        assert folder.is_dir()
        items = list(folder.glob("*.png"))
        if i in (2, 3):
            assert {p.relative_to(ROOT).as_posix() for p in items} == fase_esperada[i], (
                f"Fase {i}: capturas distintas del manifiesto aprobado"
            )
        if i >= 4:
            assert {p.relative_to(ROOT).as_posix() for p in items} == expected_dynamic[i], (
                f"Fase {i}: PNG sin manifiesto o faltantes"
            )
        for file in items:
            assert file.name.startswith(f"S{i:02d}_"), f"Prefijo incorrecto: {file}"
            assert file.stat().st_size > 0
        print(f"FASE_{i}_PNG_VERSIONADOS={len(items)}")

    print("AUDITORIA_CAPTURAS_POR_FASE=OK")


if __name__ == "__main__":
    main()
