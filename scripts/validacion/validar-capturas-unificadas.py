#!/usr/bin/env python3
"""Valida la organización y el formato básico de las capturas por fase.

El control comprueba cantidades, nombres, cabeceras y dimensiones de PNG.
No modifica archivos ni depende de inventarios de procedencia externos.
"""
from __future__ import annotations

import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAPTURAS = ROOT / "evidencias" / "capturas"
FASES_COMPLETADAS = {1: 83, 2: 9, 3: 8, 4: 22, 5: 71, 6: 11}
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def inspeccionar_png(archivo: Path) -> tuple[int, int]:
    """Comprueba estructura inicial del PNG sin alterar su contenido."""
    if not archivo.is_file() or archivo.is_symlink():
        raise ValueError(f"Archivo PNG no válido: {archivo}")
    with archivo.open("rb") as entrada:
        cabecera = entrada.read(24)
    if len(cabecera) != 24 or cabecera[:8] != PNG_MAGIC or cabecera[12:16] != b"IHDR":
        raise ValueError(f"Cabecera PNG inválida: {archivo}")
    ancho, alto = struct.unpack(">II", cabecera[16:24])
    if ancho <= 0 or alto <= 0:
        raise ValueError(f"Dimensiones inválidas: {archivo}")
    return ancho, alto


def validar_catalogo() -> dict[int, int]:
    """Comprueba las ocho carpetas y enumera los resultados por fase."""
    conteos: dict[int, int] = {}
    for fase in range(1, 9):
        directorio = CAPTURAS / f"fase{fase}"
        if not directorio.is_dir():
            raise ValueError(f"Carpeta ausente: {directorio}")
        documentos = sorted(directorio.glob("*.md"))
        if fase in FASES_COMPLETADAS and [p.name for p in documentos] != ["README.md"]:
            raise ValueError(f"Se requiere un único README en {directorio}")
        imagenes = sorted(directorio.glob("*.png"))
        nombres = [item.name for item in imagenes]
        if len(nombres) != len(set(nombres)):
            raise ValueError(f"Nombres duplicados en fase {fase}")
        identificadores = []
        patron = re.compile(
            rf"S{fase:02d}_F(\d{{2,}})_"
            r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*\.png"
        )
        for archivo in imagenes:
            coincidencia = patron.fullmatch(archivo.name)
            if not coincidencia:
                raise ValueError(f"Nombre incorrecto: {archivo.name}")
            identificador = int(coincidencia.group(1))
            if coincidencia.group(1) != f"{identificador:02d}":
                raise ValueError(f"Numeración incorrecta: {archivo.name}")
            identificadores.append(identificador)
            inspeccionar_png(archivo)
        if sorted(identificadores) != list(range(1, len(imagenes) + 1)):
            raise ValueError(f"Numeración no consecutiva en fase {fase}")
        esperado = FASES_COMPLETADAS.get(fase)
        if esperado is not None and len(imagenes) != esperado:
            raise ValueError(f"Fase {fase}: {len(imagenes)} capturas; se esperaban {esperado}")
        conteos[fase] = len(imagenes)
        print(f"FASE_{fase}_PNG={len(imagenes)}")
    if list(CAPTURAS.glob("*.png")):
        raise ValueError("Existen capturas fuera de su carpeta de fase")
    print(f"PNG_TOTAL={sum(conteos.values())}")
    print("CATALOGO_CAPTURAS=OK")
    return conteos


if __name__ == "__main__":
    validar_catalogo()
