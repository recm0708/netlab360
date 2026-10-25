#!/usr/bin/env python3
"""NETLAB360 — auditoría de capturas reales, organizada por fases.

Fase 1 conserva 86 PNG de los lotes históricos 01–06; se valida por SHA-256,
tamaño, nombre y hash Git. Los siete CSV históricos permanecen inmutables.
Fases 2–8 admiten nueva evidencia solo con prefijos técnicos correctos.
No modifica archivos, no requiere Docker y no crea capturas sintéticas.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURAS = ROOT / "evidencias" / "capturas"
MANIFIESTOS = ROOT / "evidencias" / "manifiestos"
MAPA = MANIFIESTOS / "MAPA_RENOMBRADO_FASE1_2026-10-25.csv"
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
    assert {p.name for p in MANIFIESTOS.glob("*.csv")} == HISTORICOS | {MAPA.name}, (
        "Manifiestos históricos alterados o incompletos"
    )
    with MAPA.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 86, f"Esperadas 86 capturas históricas; mapa tiene {len(rows)}"
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

    actual_s01 = {p.relative_to(ROOT).as_posix() for p in
                  (CAPTURAS / "fase1").glob("*.png")}
    assert actual_s01 == targets, "Fase 1: faltan PNG o hay extras sin mapear"
    assert not list(CAPTURAS.glob("*.png")), "Persisten PNG fuera de las carpetas fase"
    print("S01_PNG_RENOMBRADOS=86/86")
    print("S01_SHA256_Y_GIT_BLOB_CONSERVADOS=86/86")
    print(f"MANIFIESTOS_HISTORICOS={len(HISTORICOS)}/7")

    for i in range(2, 9):
        folder = CAPTURAS / f"fase{i}"
        assert folder.is_dir()
        items = list(folder.glob("*.png"))
        for file in items:
            assert file.name.startswith(f"S{i:02d}_"), f"Prefijo incorrecto: {file}"
            assert file.stat().st_size > 0
        print(f"FASE_{i}_PNG_VERSIONADOS={len(items)}")

    print("AUDITORIA_CAPTURAS_POR_FASE=OK")


if __name__ == "__main__":
    main()
