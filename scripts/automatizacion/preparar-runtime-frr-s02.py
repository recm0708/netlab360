#!/usr/bin/env python3
"""Preparar /etc/frr para tres routers S02 de forma atomica, SIN desplegar.

Genera un runtime nuevo en staging, verifica 3/3 routers y renombra el anterior
a copia historica. No elimina directorios ni toca interfaces, rutas o Docker
Compose. Ejecutar como usuario normal con "sudo -v" previamente.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from datetime import datetime

HOME = Path.home()
ROOT = HOME / "proyectos/netlab360"
BASE = HOME / "netlab360-bootstrap/s02"
SOURCE = BASE / "rendered"
RUNTIME = BASE / "runtime"
ROUTERS = ("R-HQ", "R-S1", "R-S2")
CONTAINERS = ("nl360-s02-r-hq", "nl360-s02-r-s1", "nl360-s02-r-s2")
IMAGE = "quay.io/frrouting/frr:10.7.1"
HASHES = {
    "R-HQ": "8fcc1e756c7ad026a5dfdbdf9fc0b65ec8841e9de494fe0fe543383ba2b2ac36",
    "R-S1": "345eb21fdf66c16b82c2e3b294b5c278553232907606468a02b776f8f82ad036",
    "R-S2": "7bfb8be5d642b9c52bc628af24eb238b7b445dfc0aa3ea898badfec484f4e917",
}


def command(*args: str) -> str:
    return subprocess.run(args, check=True, text=True, capture_output=True, timeout=35).stdout


def build_daemons(original: str) -> str:
    """Conservar plantilla original; definir exactamente zebra/ospfd una vez."""
    lines = [
        line for line in original.splitlines()
        if line.split("=", 1)[0].strip() not in {"zebra", "ospfd"}
    ]
    return "\n".join(lines + ["zebra=yes", "ospfd=yes", ""])


def validate_file(path: Path, uid: int, gid: int, mode: int) -> None:
    info = path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid != uid
            or info.st_gid != gid or stat.S_IMODE(info.st_mode) != mode):
        raise RuntimeError(f"Permisos o propietario invalidos: {path}")


def main() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("Ejecutar como usuario de Ubuntu, NO como root")
    if not BASE.is_dir() or not SOURCE.is_dir():
        raise RuntimeError("Faltan los directorios de trabajo S02")
    if RUNTIME.is_symlink():
        raise RuntimeError("Runtime es symlink: no cambiarlo")
    if any((SOURCE / f"{r}.frr.conf").is_symlink() for r in ROUTERS):
        raise RuntimeError("Configuracion de origen es symlink")
    print("========== VALIDAR CONFIGURACIONES ORIGEN ==========")
    for r in ROUTERS:
        checksum = hashlib.sha256((SOURCE / f"{r}.frr.conf").read_bytes()).hexdigest()
        if checksum != HASHES[r]:
            raise RuntimeError(f"Hash FRR inesperado: {r} {checksum}")
        print(f"ORIGEN={r} SHA256={checksum}")
    names = command("sudo", "-n", "docker", "ps", "-a", "--format", "{{.Names}}").splitlines()
    if set(CONTAINERS) & set(names):
        raise RuntimeError("Existen contenedores S02; inspeccionar antes de preparar")
    template = command(
        "sudo", "-n", "docker", "run", "--rm", "--network", "none",
        "--cap-drop", "ALL", "--entrypoint", "/bin/cat",
        IMAGE, "/etc/frr/daemons"
    )
    daemons = build_daemons(template)
    if daemons.count("\nzebra=yes\n") != 1 or daemons.count("\nospfd=yes\n") != 1:
        raise RuntimeError("Activacion zebra/ospfd no verificable")
    stage = Path(tempfile.mkdtemp(prefix=".runtime-s02-stage-", dir=BASE))
    print(f"STAGING={stage}")
    previous = None
    try:
        for r in ROUTERS:
            dest = stage / r
            dest.mkdir(mode=0o755)
            src = SOURCE / f"{r}.frr.conf"
            shutil.copyfile(src, dest / "frr.conf")
            (dest / "daemons").write_text(daemons, encoding="utf-8")
            (dest / "vtysh.conf").write_text(
                f"service integrated-vtysh-config\nhostname {r}\n", encoding="utf-8"
            )
            if hashlib.sha256((dest / "frr.conf").read_bytes()).hexdigest() != HASHES[r]:
                raise RuntimeError(f"Integridad alterada en {r}")
            command("sudo", "-n", "chown", "100:101", str(dest), str(dest / "daemons"))
            command("sudo", "-n", "chown", "100:102",
                    str(dest / "frr.conf"), str(dest / "vtysh.conf"))
            os.chmod(dest, 0o755)
            os.chmod(dest / "daemons", 0o640)
            os.chmod(dest / "frr.conf", 0o660)
            os.chmod(dest / "vtysh.conf", 0o660)
            validate_file(dest / "daemons", 100, 101, 0o640)
            validate_file(dest / "frr.conf", 100, 102, 0o660)
            validate_file(dest / "vtysh.conf", 100, 102, 0o660)
            print(f"RUNTIME_VALIDADO={r} ARCHIVOS=3")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if RUNTIME.exists():
            previous = BASE / f"runtime-backup-{stamp}"
            if previous.exists():
                raise RuntimeError("Ya existe backup destino; no sobrescribir")
            RUNTIME.rename(previous)
            print(f"RUNTIME_ANTERIOR_CONSERVADO={previous}")
        try:
            stage.rename(RUNTIME)
        except OSError:
            if previous is not None and not RUNTIME.exists():
                previous.rename(RUNTIME)
            raise
        print("RUNTIME_S02_ACTIVADO=3")
        print("S02_PREPARACION_RESULTADO=0")
    except Exception:
        print(f"PREPARACION_NO_COMPLETADA_STAGING_CONSERVADO={stage}", file=sys.stderr)
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"S02_PREPARACION_ERROR={type(e).__name__}: {e}", file=sys.stderr)
        print("S02_PREPARACION_RESULTADO=1", file=sys.stderr)
        sys.exit(1)
