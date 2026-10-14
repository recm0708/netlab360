#!/usr/bin/env python3
"""NETLAB360: migra las capturas versionadas a una sola carpeta (sin modificar bytes).

Uso:
  python3 scripts/mantenimiento/aplanar-capturas.py --plan
  python3 scripts/mantenimiento/aplanar-capturas.py --aplicar

Guardias: rama main limpia y alineada con origin/main, inventario conocido,
sin colisiones (incluidas diferencias de mayúsculas), y SHA-256 conservados.
Solo modifica rutas dentro de evidencias/; NO toca redes, Docker ni otras VMs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURAS = Path("evidencias/capturas")
MANIFIESTOS = Path("evidencias/manifiestos")
LOTE_DIRS = {
    "B1_B2_lote01": (19, "MANIFIESTO_SHA256_LOTE01.csv"),
    "B3_lote02": (5, "MANIFIESTO_SHA256_LOTE02.csv"),
    "B2_B3_lote03": (20, "MANIFIESTO_SHA256_NETLAB360_LOTE03_20PNG.csv"),
    "B2_LACP_lote04": (13, "MANIFIESTO_SHA256_NETLAB360_LOTE04_LACP_13PNG.csv"),
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plan_migracion():
    items = [Path(p) for p in git("ls-files", "--", str(CAPTURAS)).splitlines() if p]
    esperado = sum(x[0] for x in LOTE_DIRS.values())
    png = [p for p in items if p.suffix.lower() == ".png"]
    csvs = [p for p in items if p.suffix.lower() == ".csv"]
    assert len(png) == esperado == 57, f"Conteo PNG no esperado: {len(png)}"
    assert len(csvs) == len(LOTE_DIRS) == 4, f"Conteo CSV: {len(csvs)}"
    assert len(items) == len(png) + len(csvs), "Hay ficheros adicionales no contemplados"

    grupos = Counter(p.parent.name for p in png)
    for grupo, (cantidad, _) in LOTE_DIRS.items():
        assert grupos[grupo] == cantidad, f"{grupo}: esperado {cantidad}, detectado {grupos[grupo]}"
    assert set(grupos) == set(LOTE_DIRS), "Hay directorios no previstos"

    movimientos = []
    rutas_destino = set()
    for origen in items:
        grupo = origen.parent.name
        assert origen.parent == CAPTURAS / grupo and grupo in LOTE_DIRS
        assert (ROOT / origen).is_file() and not (ROOT / origen).is_symlink()
        if origen.suffix.lower() == ".png":
            destino = CAPTURAS / origen.name
        else:
            nombre = LOTE_DIRS[grupo][1]
            if grupo in ("B2_B3_lote03", "B2_LACP_lote04"):
                assert origen.name == nombre
            else:
                assert origen.name == "MANIFIESTO_SHA256.csv"
            destino = MANIFIESTOS / nombre
        clave = str(destino).casefold()
        assert clave not in rutas_destino, f"Colision de destino: {destino}"
        rutas_destino.add(clave)
        assert not (ROOT / destino).exists(), f"Ya existe el destino: {destino}"
        movimientos.append((origen, destino, sha256(ROOT / origen), (ROOT / origen).stat().st_size))
    return movimientos


def main():
    parser = argparse.ArgumentParser()
    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--plan", action="store_true")
    selector.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    assert git("rev-parse", "--show-toplevel") == str(ROOT), "Ubicacion inesperada"
    assert git("branch", "--show-current") == "main", "Debe estar en main"
    assert not git("status", "--porcelain"), "Repositorio con cambios: NO migrar"
    assert git("rev-parse", "HEAD") == git("rev-parse", "origin/main"), "Ejecutar primero git pull --ff-only"

    movimientos = plan_migracion()
    print("PNG_EN_LOTES=57")
    print("MANIFIESTOS_EN_LOTES=4")
    print("COLISIONES=0")
    print("MIGRACION_PLANIFICADA=61")
    for origen, destino, _, _ in movimientos:
        print(f"{origen} -> {destino}")
    if args.plan:
        print("MODO=PREVISUALIZACION_SIN_CAMBIOS")
        return

    (ROOT / MANIFIESTOS).mkdir(parents=True, exist_ok=True)
    for origen, destino, firma, _ in movimientos:
        subprocess.run(["git", "mv", "--", str(origen), str(destino)], cwd=ROOT, check=True)
        assert sha256(ROOT / destino) == firma, f"Archivo modificado: {destino}"

    indice = ROOT / MANIFIESTOS / "MAPA_ORIGEN_A_RAIZ_2026-10-13.csv"
    assert not indice.exists(), "El indice de migracion ya existe"
    with indice.open("w", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        writer.writerow(["ruta_original", "ruta_actual", "sha256", "bytes"])
        for origen, destino, firma, longitud in movimientos:
            writer.writerow([str(origen), str(destino), firma, longitud])

    finales = list((ROOT / CAPTURAS).glob("*.png"))
    assert len(finales) == 57, f"Esperados 57 PNG en raiz; reales {len(finales)}"
    # git mv mueve archivos, pero Git no gestiona carpetas vacias en el
    # filesystem de Ubuntu. Eliminarlas solamente si estan vacias.
    for nombre in LOTE_DIRS:
        carpeta = ROOT / CAPTURAS / nombre
        if carpeta.exists():
            assert carpeta.is_dir() and not carpeta.is_symlink(), f"Ruta inesperada: {carpeta}"
            assert not any(carpeta.iterdir()), f"Carpeta NO vacia: {carpeta}"
            carpeta.rmdir()
    assert not any((ROOT / CAPTURAS / nombre).exists() for nombre in LOTE_DIRS)
    print("MIGRACION_REALIZADA=SI")
    print("PNG_DIRECTOS=57")
    print("MANIFIESTOS_REUBICADOS=4")
    print("SHA256_CONSERVADOS=SI")
    print("INDICE_RUTAS_CREADO=SI")
    print("NOTA=git mv esta staged, agregar indice/archivos nuevos y hacer commit/push manual.")


if __name__ == "__main__":
    main()
