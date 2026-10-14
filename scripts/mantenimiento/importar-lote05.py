#!/usr/bin/env python3
"""Importar únicamente las 5 capturas auditadas del lote05 a una carpeta plana.

No extrae rutas del ZIP directamente: valida el hash total, cada SHA-256,
el manifiesto y los nombres explícitos antes de crear archivos.
Requiere que el aplanado de los cuatro lotes históricos haya finalizado.
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
ZIP_NAME = "NETLAB360_LOTE05_DUALNIC_NOC_5PNG_2026-10-13.zip"
ZIP_SHA = "9e57057e402a9a87e1c2e91997ad59dd88cb136d6329f75ba50721181959cdfa"
CSV_NAME = "MANIFIESTO_SHA256_NETLAB360_LOTE05_DUALNIC_5PNG.csv"
CSV_SHA = "de456693e4b884be2ec15a6e16c63efee684c7c3e81c659fd54c7b9a21e0a9db"
EXPECTED = {
    "B2_DUALNIC_01_Primaria_Activa.png": "3524bcfa383327ddf9eece83f0d92281b1beff736d0c10acfc368a728ed87445",
    "B2_DUALNIC_02_Conmutacion_Respaldo.png": "8f77af2c4c3865a0f964fc41c7aa9ac6b3dbe7b81c941a0b17a12bfb57387c4d",
    "B2_DUALNIC_03_Interfaz_Restaurada.png": "510dda6358ead4c79b4755d22d27132ff7c598990f70a393bab2fd8ae3566a6f",
    "B2_DUALNIC_04_Postcheck_Final.png": "6e34af2db4287f8ad049bdb9dff296a89a7b8bc7c35abbd528cc389f13097200",
    "B3_04_Postcheck_Servicio_NOC_Final.png": "9c004b3dd7e7a7030e142d9f0a3e4527ab2294ce50cb6ba28674c0bdb51d6d90",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    paquete = Path.home() / ZIP_NAME if len(sys.argv) == 1 else Path(sys.argv[1])
    assert paquete.is_file(), f"No se encontro el ZIP: {paquete}"
    assert sha(paquete.read_bytes()) == ZIP_SHA, "SHA256 ZIP incorrecto"
    destino = ROOT / "evidencias/capturas"
    manifiestos = ROOT / "evidencias/manifiestos"
    assert destino.is_dir() and manifiestos.is_dir(), "Primero ejecutar aplanado"
    assert len(list(destino.glob("*.png"))) == 57, "Se esperaban 57 PNG historicos en carpeta plana"
    # El primer aplanado se publico con los PNG ya trasladados,
    # pero git mv dejo cuatro directorios fisicos VACIOS en el clon.
    # No borrar directorios desconocidos o con datos; limpiamos solo
    # los cuatro nombres historicos cuando estan totalmente vacios.
    anteriores = {
        "B1_B2_lote01", "B3_lote02", "B2_B3_lote03", "B2_LACP_lote04"
    }
    directorios = [p for p in destino.iterdir() if p.is_dir()]
    assert all(p.name in anteriores and not p.is_symlink() and
               not any(p.iterdir()) for p in directorios), (
               "Subcarpeta desconocida o con archivos: NO eliminar ni importar")
    for name in EXPECTED:
        assert not (destino / name).exists(), f"Archivo ya existe: {name}"
    assert not (manifiestos / CSV_NAME).exists(), "Manifiesto del lote05 ya existe"

    with ZipFile(paquete) as z:
        assert z.testzip() is None, "ZIP corrupto"
        assert set(z.namelist()) == (
            {"capturas/" + name for name in EXPECTED}
            | {CSV_NAME, "LEEME_LOTE05.txt"}
        ), "Contenido ZIP no esperado"
        csv_bytes = z.read(CSV_NAME)
        assert sha(csv_bytes) == CSV_SHA, "SHA256 manifiesto incorrecto"
        rows = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8"))))
        assert len(rows) == 5
        assert {row["archivo"] for row in rows} == set(EXPECTED), "Nombres del manifiesto incorrectos"
        payload = {}
        for row in rows:
            name = row["archivo"]
            data = z.read("capturas/" + name)
            assert sha(data) == EXPECTED[name] == row["sha256"], f"PNG alterado: {name}"
            assert len(data) == int(row["bytes"]), f"Longitud incorrecta: {name}"
            payload[name] = data

    # Tras validar por completo el paquete, retirar solo carpetas antiguas VACIAS.
    for antigua in directorios:
        antigua.rmdir()
    assert not any(p.is_dir() for p in destino.iterdir())

    creados = []
    try:
        for name, data in payload.items():
            p = destino / name
            with p.open("xb") as f:
                f.write(data)
            creados.append(p)
        p = manifiestos / CSV_NAME
        with p.open("xb") as f:
            f.write(csv_bytes)
        creados.append(p)
    except Exception:
        for p in creados:
            p.unlink(missing_ok=True)
        raise

    assert len(list(destino.glob("*.png"))) == 62
    print("LOTE05_IMPORTADO=SI")
    print("CAPTURAS_PLANAS_PNG=62")
    print("PNG_NUEVOS=5")
    print("MANIFIESTO_05_IMPORTADO=SI")
    print("SHA256_INDIVIDUALES=OK")


if __name__ == "__main__":
    main()
