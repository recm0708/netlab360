#!/usr/bin/env python3
"""Instalamos componentes protegidos únicamente en un perfil nuevo.

El modo plan no modifica el sistema. El modo de instalación
requiere fuentes revisadas y protegidas por el administrador.
No instala sudoers, unidades systemd ni autorizaciones RFC.
"""

import argparse
import csv
import json
import os
from pathlib import Path
import pwd
import socket
import stat
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]

LIBEXEC = Path("/usr/local/libexec")
STATE_BASE = Path("/var/lib/netlab360")

MANIFEST = "operacion/componentes-protegidos.tsv"

# Lista cerrada de fuentes y destinos admitidos.
# El manifiesto no puede seleccionar ejecutores arbitrarios.
ALLOWED = {
    "scripts/s06/guardia_protegida.py":
        "netlab360/s06-guardia.py",
    "scripts/s06/controlador_hq_protegido.py":
        "netlab360/s06-hq-controlador.py",
    "scripts/s06/rollback_qdisc_aislado.py":
        "netlab360/s06-rollback-isotest.py",
    "scripts/s06/rollback_veth_aislado.py":
        "netlab360/s06-veth-rollback.py",
    "scripts/s07/api_s07.py":
        "netlab360/s07-api.py",
    "scripts/s07/rfc_ospf_operacional.py":
        "netlab360/s07-ospf-broker.py",
    "scripts/s07/ospf_trial.py":
        "netlab360/s07-ospf-trial.py",
    "scripts/s07/preflight_protegido.py":
        "netlab360/s07-preflight.py",
    "scripts/s07/recovery_rehearsal.py":
        "netlab360/s07-recovery.py",
    "scripts/s07/rfc_live_read.py":
        "netlab360/s07-rfc-live.py",
    "scripts/s07/rfc_protegido_preview.py":
        "netlab360/s07-rfc-preview.py",
    "scripts/s07/wan_trial_guard.py":
        "netlab360/s07-wan-trial.py",
    "scripts/operacion/s05_observador_privilegiado.py":
        "netlab360-observer",
}

STATE_NAMES = (
    "s07-api",
    "s07-ospf-broker",
    "s07-ospf-trial",
    "s07-preflight",
    "s07-recovery",
    "s07-rfc-live",
    "s07-rfc-preview",
    "s07-wan-trial",
)

def exists(path):
    """Detectamos también enlaces simbólicos rotos."""
    return os.path.lexists(path)

def trusted(path):
    """Exigimos rutas root:root sin escritura de terceros."""
    path = Path(path).absolute()

    for item in (path, *path.parents):
        info = item.lstat()

        if stat.S_ISLNK(info.st_mode):
            raise ValueError(f"UNTRUSTED_SYMLINK: {item}")

        if info.st_uid != 0 or info.st_gid != 0:
            raise ValueError(f"UNTRUSTED_OWNER: {item}")

        if info.st_mode & 0o022:
            raise ValueError(f"UNTRUSTED_PERMISSIONS: {item}")

def source_path(repo, relative):
    """Validamos que una fuente permanezca dentro del repositorio."""
    rel = Path(relative)

    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("INVALID_SOURCE_PATH")

    path = repo / rel

    if path.is_symlink() or not path.is_file():
        raise ValueError("INVALID_SOURCE")

    if not path.resolve().is_relative_to(repo.resolve()):
        raise ValueError("SOURCE_OUTSIDE_REPOSITORY")

    return path

def read_manifest(repo):
    """Comprobamos el alcance y los permisos de cada ejecutor."""
    manifest = source_path(repo, MANIFEST)

    with manifest.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    if len(rows) != len(ALLOWED):
        raise ValueError("INVALID_MANIFEST_COUNT")

    seen = set()

    for row in rows:
        source = row["fuente"]

        if source not in ALLOWED or source in seen:
            raise ValueError("INVALID_MANIFEST_SOURCE")

        expected = str(LIBEXEC / ALLOWED[source])

        if row["destino"] != expected:
            raise ValueError("INVALID_MANIFEST_DESTINATION")

        if (row["propietario"], row["grupo"]) != ("root", "root"):
            raise ValueError("INVALID_MANIFEST_OWNER")

        if row["modo"] not in {"0750", "0755"}:
            raise ValueError("INVALID_MANIFEST_MODE")

        path = source_path(repo, source)
        compile(path.read_bytes(), str(path), "exec")

        seen.add(source)

    if seen != set(ALLOWED):
        raise ValueError("INCOMPLETE_MANIFEST")

    return rows

def command(*args):
    """Ejecutamos comprobaciones fijas, sin intérprete de shell."""
    return subprocess.check_output(
        args,
        text=True,
        timeout=15,
        env={
            "PATH": "/usr/sbin:/usr/bin:/sbin:/bin",
            "LC_ALL": "C",
        },
    ).strip()

def check_profile():
    """Conservamos las comprobaciones del perfil de referencia."""
    if socket.gethostname() != "netlab360-lab":
        raise ValueError("REFERENCE_HOSTNAME_REQUIRED")

    user = pwd.getpwnam("rc-aa-ec")

    if user.pw_uid != 1000:
        raise ValueError("REFERENCE_OPERATOR_UID_REQUIRED")

    if user.pw_dir != "/home/rc-aa-ec":
        raise ValueError("REFERENCE_HOME_REQUIRED")

    addresses = json.loads(command(
        "/usr/sbin/ip", "-j", "-4", "addr",
        "show", "dev", "ens33",
    ))

    routes = json.loads(command(
        "/usr/sbin/ip", "-j", "-4", "route",
        "show", "default",
    ))

    if len(addresses) != 1:
        raise ValueError("REFERENCE_INTERFACE_REQUIRED")

    if not any(
        item.get("local") == "192.168.47.40"
        and item.get("prefixlen") == 24
        for item in addresses[0].get("addr_info", [])
    ):
        raise ValueError("REFERENCE_IP_REQUIRED")

    if (
        len(routes) != 1
        or routes[0].get("gateway") != "192.168.47.2"
        or routes[0].get("dev") != "ens33"
    ):
        raise ValueError("REFERENCE_GATEWAY_REQUIRED")

def check_absent(paths):
    """Rechazamos cualquier destino previamente existente."""
    for path in paths:
        if exists(path):
            raise ValueError(f"EXISTING_RESOURCE: {path}")

def check_clean_host(rows):
    """Impedimos instalar sobre recursos activos o históricos."""
    check_absent([
        STATE_BASE,
        LIBEXEC / "netlab360",
        LIBEXEC / "netlab360-observer",
        *(Path(row["destino"]) for row in rows),
    ])

    if command("/usr/sbin/ip", "netns", "list"):
        raise ValueError("EXISTING_NETWORK_NAMESPACES")

    if command("/usr/bin/docker", "ps", "-aq"):
        raise ValueError("EXISTING_CONTAINERS")

    units = command(
        "/usr/bin/systemctl", "list-units",
        "--all", "--plain", "--no-legend",
        "netlab360-*",
    )

    unit_files = command(
        "/usr/bin/systemctl", "list-unit-files",
        "--no-legend", "netlab360-*",
    )

    if units or unit_files:
        raise ValueError("EXISTING_NETLAB360_UNITS")

    for name in (
        "netlab360-s06",
        "netlab360-s06-hq",
        "netlab360-s06-isotest",
        "netlab360-s06-veth",
        "netlab360-s07-api",
        "netlab360-s07-rfc-live",
        "netlab360-s07-rfc-preview",
    ):
        if exists(Path("/run") / name):
            raise ValueError("EXISTING_RUNTIME_STATE")

def show_plan(rows):
    """Mostramos el alcance sin escribir archivos del sistema."""
    print("MODO=PLAN")

    for row in rows:
        print(
            f'{row["fuente"]} -> {row["destino"]}'
            f' | root:root | {row["modo"]}'
        )

    for name in STATE_NAMES:
        print(f"ESTADO={STATE_BASE / name} | root:root | 0700")

    print(f"EJECUTORES_PLANIFICADOS={len(rows)}")
    print(f"DIRECTORIOS_ESTADO_PLANIFICADOS={len(STATE_NAMES)}")
    print("IDENTIDADES_NUEVAS=PENDIENTES_DE_ENROLL")
    print("AUTORIZACIONES_RFC_CREADAS=NO")
    print("SUDOERS_MODIFICADO=NO")
    print("UNIDADES_INSTALADAS=NO")
    print("SERVICIOS_INICIADOS=NO")
    print("INSTALACION_EJECUTADA=NO")
    print("PLAN_PROTEGIDOS=OK")

def write_new(path, content, mode):
    """Creamos un archivo exclusivo, sin reemplazar otro existente."""
    fd = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
    )

    with os.fdopen(fd, "wb") as f:
        f.write(content)
        f.flush()
        os.fchown(f.fileno(), 0, 0)
        os.fchmod(f.fileno(), mode)
        os.fsync(f.fileno())

def install_new(rows):
    """Instalación acotada; no inicia los componentes instalados."""
    if os.geteuid() != 0:
        raise ValueError("ROOT_REQUIRED")

    if not sys.flags.isolated:
        raise ValueError("ISOLATED_PYTHON_REQUIRED")

    # La revisión administrativa de las fuentes es previa
    # a cualquier ejecución privilegiada.
    trusted(Path(__file__).absolute())
    trusted(REPO / MANIFEST)

    sources = {}

    for row in rows:
        path = source_path(REPO, row["fuente"])
        trusted(path)
        sources[row["fuente"]] = path.read_bytes()

    check_profile()
    check_clean_host(rows)

    trusted(LIBEXEC.parent)
    trusted(STATE_BASE.parent)

    if LIBEXEC.exists():
        trusted(LIBEXEC)

    os.umask(0o077)

    # Creamos exclusivamente los destinos de una instalación nueva.
    if not LIBEXEC.exists():
        LIBEXEC.mkdir(mode=0o755)
        LIBEXEC.chmod(0o755)

    executor_dir = LIBEXEC / "netlab360"

    executor_dir.mkdir(mode=0o755)
    executor_dir.chmod(0o755)

    STATE_BASE.mkdir(mode=0o700)

    for name in STATE_NAMES:
        (STATE_BASE / name).mkdir(mode=0o700)

    for row in rows:
        path = Path(row["destino"])
        mode = int(row["modo"], 8)

        write_new(path, sources[row["fuente"]], mode)

        info = path.lstat()

        if (
            info.st_uid != 0
            or info.st_gid != 0
            or stat.S_IMODE(info.st_mode) != mode
            or path.read_bytes() != sources[row["fuente"]]
        ):
            raise ValueError("INSTALLED_FILE_MISMATCH")

        print(f"INSTALADO={path}")

    print("EJECUTORES_INSTALADOS=13")
    print("ESTADOS_INICIALES=8_DIRECTORIOS_VACIOS")
    print("IDENTIDADES_NUEVAS=PENDIENTES_DE_ENROLL")
    print("AUTORIZACIONES_RFC_CREADAS=NO")
    print("UNIDADES_INSTALADAS=NO")
    print("SUDOERS_MODIFICADO=NO")
    print("SERVICIOS_INICIADOS=NO")
    print("INSTALACION_PROTEGIDOS=OK")

def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    modes = parser.add_mutually_exclusive_group()

    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--apply", action="store_true")

    parser.add_argument(
        "--confirm-clean-host",
        action="store_true",
    )

    parser.add_argument(
        "--confirm-reviewed-source",
        action="store_true",
    )

    args = parser.parse_args(argv)

    if args.apply and not (
        args.confirm_clean_host
        and args.confirm_reviewed_source
    ):
        parser.error(
            "Se requiere --confirm-clean-host y "
            "--confirm-reviewed-source"
        )

    if not args.apply and (
        args.confirm_clean_host
        or args.confirm_reviewed_source
    ):
        parser.error("Las confirmaciones requieren --apply")

    rows = read_manifest(REPO)

    if args.apply:
        install_new(rows)
    else:
        show_plan(rows)

if __name__ == "__main__":
    try:
        main()
    except (
        OSError,
        ValueError,
        KeyError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        print(
            "Si hubo una instalación parcial, inspeccionar "
            "los destinos antes de cualquier nuevo intento.",
            file=sys.stderr,
        )
        sys.exit(3)
