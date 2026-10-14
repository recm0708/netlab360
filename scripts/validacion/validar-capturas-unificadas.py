#!/usr/bin/env python3
"""Auditoría de integridad para el repositorio de capturas unificadas de NETLAB360.

Comprueba los 57 PNG originales según el mapa SHA256 de migración y, si
se incorporó el lote05, los PNG adicionales de lotes 05 (cinco) y 06 (veinticuatro) según sus manifiestos.
No modifica ningún archivo; salida 0 solo si los conteos y hashes coinciden.
"""
from pathlib import Path
import csv
import hashlib

ROOT = Path(__file__).resolve().parents[2]
CAPTURAS = ROOT / "evidencias/capturas"
MANIFIESTOS = ROOT / "evidencias/manifiestos"
MAPA = MANIFIESTOS / "MAPA_ORIGEN_A_RAIZ_2026-10-13.csv"
LOTE05 = MANIFIESTOS / "MANIFIESTO_SHA256_NETLAB360_LOTE05_DUALNIC_5PNG.csv"
LOTE06 = MANIFIESTOS / "MANIFIESTO_SHA256_NETLAB360_LOTE06_IAC_B4_24PNG.csv"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_csv(path):
    with path.open(newline="", encoding="utf-8") as reader:
        return list(csv.DictReader(reader))

def main():
    assert CAPTURAS.is_dir() and MANIFIESTOS.is_dir()
    assert not any(p.is_dir() for p in CAPTURAS.iterdir()), "Quedan subdirectorios en capturas"
    assert MAPA.is_file(), "Falta mapa de migracion"
    mapa = load_csv(MAPA)
    assert len(mapa) == 61, f"Mapa incompleto: {len(mapa)}"
    rutas = [r["ruta_actual"] for r in mapa]
    assert len(rutas) == len(set(rutas)), "Rutas repetidas en mapa"
    historicos = set()
    antiguos_csv = set()
    for fila in mapa:
        relativo = Path(fila["ruta_actual"])
        assert not relativo.is_absolute() and ".." not in relativo.parts
        archivo = ROOT / relativo
        assert archivo.is_file(), f"Falta: {archivo}"
        assert archivo.stat().st_size == int(fila["bytes"]), f"Tamano diferente: {archivo}"
        assert sha(archivo) == fila["sha256"], f"SHA diferente: {archivo}"
        if relativo.suffix.lower() == ".png":
            assert relativo.parent == Path("evidencias/capturas")
            historicos.add(relativo.name)
        else:
            assert relativo.suffix.lower() == ".csv"
            assert relativo.parent == Path("evidencias/manifiestos")
            antiguos_csv.add(relativo.name)
    assert len(historicos) == 57
    assert len(antiguos_csv) == 4
    assert all(p.suffix.lower() == ".png" for p in CAPTURAS.iterdir())

    actuales = {p.name for p in CAPTURAS.glob("*.png")}
    if LOTE05.is_file():
        nuevos = load_csv(LOTE05)
        assert len(nuevos) == 5
        nombres = [r["archivo"] for r in nuevos]
        assert len(set(nombres)) == 5
        assert not set(nombres) & historicos, "Lote05 duplica historicos"
        for fila in nuevos:
            p = CAPTURAS / fila["archivo"]
            assert p.is_file()
            assert p.stat().st_size == int(fila["bytes"])
            assert sha(p) == fila["sha256"], f"SHA lote05 diferente: {p}"
        historicos |= set(nombres)
        estado = "LOTE05_INCORPORADO=SI"
        esperado = 62
    else:
        estado = "LOTE05_INCORPORADO=NO"
        esperado = 57

    if LOTE06.is_file():
        assert LOTE05.is_file(), "Lote06 requiere lote05"
        nuevos = load_csv(LOTE06)
        assert len(nuevos) == 24, "Lote06 incompleto"
        nombres = [r["archivo"] for r in nuevos]
        assert len(set(nombres)) == 24, "Duplicados lote06"
        assert not (set(nombres) & historicos), "Lote06 colisiona con anteriores"
        assert sum(n.startswith("B4_") for n in nombres) == 13
        assert sum(n.startswith("IAC_") for n in nombres) == 11
        for fila in nuevos:
            p = CAPTURAS / fila["archivo"]
            assert p.is_file(), "PNG lote06 ausente"
            assert p.stat().st_size == int(fila["bytes"]), "Tamano lote06 incorrecto"
            assert sha(p) == fila["sha256"], f"SHA lote06 diferente: {p}"
        historicos |= set(nombres)
        esperado = 86
        estado06 = "LOTE06_INCORPORADO=SI"
    else:
        estado06 = "LOTE06_INCORPORADO=NO"
    assert actuales == historicos, "PNG inesperados o faltantes"

    csv_actuales = {p.name for p in MANIFIESTOS.glob("*.csv")}
    esperado_csv = antiguos_csv | {MAPA.name}
    if LOTE05.is_file():
        esperado_csv.add(LOTE05.name)
    if LOTE06.is_file():
        esperado_csv.add(LOTE06.name)
    assert csv_actuales == esperado_csv, "Manifiestos inesperados o faltantes"
    print(f"PNG_DIRECTOS={esperado}")
    print(f"CSV_VERIFICADOS={len(csv_actuales)}")
    print("COLISIONES_Y_SUBCARPETAS=0")
    print("SHA256_ORIGINALES=OK")
    print(estado)
    print(estado06)
    print("AUDITORIA_CAPTURAS_PLANAS=OK")

if __name__ == "__main__":
    main()
