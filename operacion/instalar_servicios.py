#!/usr/bin/env python3
"""Instalamos unidades revisadas sin activar la topología.

El modo administrativo exige fuentes independientes y
protegidas por root. No reemplazamos archivos existentes.
"""

import argparse
import os
from pathlib import Path
import re
import socket
import stat
import subprocess


ROOT = Path(__file__).resolve().parents[1]

SYSTEMD = Path("/etc/systemd/system")
SUDOERS = Path("/etc/sudoers.d")

NAMES = (
    "netlab360-s04-exporter.service",
    "netlab360-s04-prometheus.service",
    "netlab360-s05-noc.service",
    "netlab360-s05-ha-backend-hq.service",
    "netlab360-s05-ha-backend-s1.service",
    "netlab360-s05-ha-frontal-hq.service",
    "netlab360-s05-ha-monitor-s2.service",
)

OBSERVER = "netlab360-observer"


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def read(*args):
    return subprocess.check_output(
        args, text=True, timeout=30
    ).strip()


def source_pairs(root=ROOT):
    rows = []

    for name in NAMES:
        folder = (
            "operacion/plantillas"
            if name == "netlab360-s04-prometheus.service"
            else "servicios/systemd"
        )

        rows.append((
            root / folder / name,
            SYSTEMD / name,
            0o644,
        ))

    rows.append((
        root / "operacion/plantillas" / OBSERVER,
        SUDOERS / OBSERVER,
        0o440,
    ))

    return rows


def secure_source(path):
    """Exigimos propiedad root y una cadena sin symlinks."""
    require(path.is_absolute(), "ABSOLUTE_SOURCE_REQUIRED")

    for entry in (path, *path.parents):
        data = entry.lstat()

        require(
            not stat.S_ISLNK(data.st_mode),
            f"SYMLINK_REJECTED: {entry}",
        )

        require(
            data.st_uid == 0
            and data.st_gid == 0
            and not data.st_mode & 0o022,
            f"UNTRUSTED_SOURCE: {entry}",
        )

    require(path.is_file(), "SOURCE_NOT_REGULAR")


def absent(path):
    require(
        not path.exists() and not path.is_symlink(),
        f"DESTINATION_EXISTS: {path}",
    )


def validate_observer_rule(text):
    """Admitimos exclusivamente la consulta snapshot."""
    lines = [
        row.strip()
        for row in text.splitlines()
        if row.strip() and not row.lstrip().startswith("#")
    ]

    pattern = (
        r"rc-aa-ec\s+ALL\s*=\s*"
        r"\(root(?::root)?\)\s*NOPASSWD:\s*"
        r"/usr/local/libexec/netlab360-observer\s+snapshot"
    )

    require(
        len(lines) == 1
        and re.fullmatch(pattern, lines[0]) is not None,
        "SUDOERS_POLICY_INVALID",
    )


def validate_unit(source):
    data = source.read_text(encoding="utf-8")

    require(
        "[Unit]" in data and "[Service]" in data,
        f"UNIT_STRUCTURE_INVALID: {source.name}",
    )

    require(
        re.search(r"^User=rc-aa-ec$", data, re.M),
        f"UNIT_USER_INVALID: {source.name}",
    )

    require(
        not re.search(
            r"^ExecStart=.*\bsudo\b", data, re.M
        ),
        f"UNIT_PRIVILEGE_INVALID: {source.name}",
    )

    if source.name == "netlab360-s04-prometheus.service":
        require(
            "--web.listen-address=127.0.0.1:9091" in data,
            "PROMETHEUS_BIND_INVALID",
        )

    return data


def check_host():
    require(os.geteuid() == 0, "ROOT_REQUIRED")

    require(
        socket.gethostname() == "netlab360-lab",
        "HOSTNAME_NOT_SUPPORTED",
    )

    require(
        "192.168.47.40/24" in read(
            "ip", "-4", "-o", "addr", "show", "dev", "ens33"
        ),
        "ADMIN_ADDRESS_MISMATCH",
    )

    require(
        "default via 192.168.47.2 dev ens33" in read(
            "ip", "-4", "route", "show", "default"
        ),
        "ADMIN_ROUTE_MISMATCH",
    )

    require(
        not read("docker", "ps", "-aq"),
        "HOST_HAS_CONTAINERS",
    )

    require(
        not read("ip", "netns", "list"),
        "HOST_HAS_NAMESPACES",
    )

    require(
        not read("ovs-vsctl", "list-br"),
        "HOST_HAS_OVS_BRIDGES",
    )

    for name in NAMES:
        current = read(
            "systemctl", "show", name,
            "-p", "LoadState", "--value",
        )

        require(
            current == "not-found",
            f"EXISTING_UNIT: {name}",
        )


def verify_sources(rows):
    units = []

    for source, destination, _ in rows:
        secure_source(source)
        absent(destination)

        if source.name == OBSERVER:
            validate_observer_rule(
                source.read_text(encoding="utf-8")
            )

            subprocess.run(
                ["/usr/sbin/visudo", "-cf", str(source)],
                check=True,
            )

        else:
            validate_unit(source)
            units.append(str(source))

    subprocess.run(
        ["systemd-analyze", "verify", *units],
        check=True,
    )


def install_new(source, destination, mode):
    """Creamos exclusivamente archivos nuevos."""
    content = source.read_bytes()

    fd = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT |
        os.O_EXCL | os.O_NOFOLLOW,
        mode,
    )

    with os.fdopen(fd, "wb") as output:
        os.fchown(output.fileno(), 0, 0)
        os.fchmod(output.fileno(), mode)
        output.write(content)
        output.flush()
        os.fsync(output.fileno())


def plan():
    print("MODO=PLAN")

    for source, destination, mode in source_pairs():
        print(
            f"{source.relative_to(ROOT)} -> "
            f"{destination} | root:root | {mode:04o}"
        )

    print("UNIDADES_PLANIFICADAS=7")
    print("REGLAS_SUDOERS_PLANIFICADAS=1")
    print("AUTOINICIO_HABILITADO=NO")
    print("SERVICIOS_INICIADOS=NO")
    print("PLAN_INSTALACION_SERVICIOS=OK")


def apply():
    check_host()

    # Comprobamos también el propio ejecutor administrativo.
    secure_source(Path(__file__).absolute())

    rows = source_pairs()

    verify_sources(rows)

    try:
        for source, destination, mode in rows:
            install_new(source, destination, mode)
            print(f"INSTALADO={destination}")

        subprocess.run(
            ["/usr/sbin/visudo", "-c"],
            check=True,
        )

        subprocess.run(
            ["systemctl", "daemon-reload"],
            check=True,
        )

    except BaseException:
        print("INSTALACION_INCOMPLETA=REQUIERE_REVISION")
        print("REVERSION_AUTOMATICA=NO")
        raise

    print("UNIDADES_INSTALADAS=7")
    print("REGLAS_SUDOERS_INSTALADAS=1")
    print("AUTOINICIO_HABILITADO=NO")
    print("SERVICIOS_INICIADOS=NO")


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)

    mode = parser.add_mutually_exclusive_group(required=True)

    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--apply", action="store_true")

    parser.add_argument(
        "--confirm-clean-host", action="store_true"
    )

    parser.add_argument(
        "--confirm-reviewed-source", action="store_true"
    )

    args = parser.parse_args(argv)

    if args.apply and not (
        args.confirm_clean_host
        and args.confirm_reviewed_source
    ):
        parser.error("Se requieren ambas confirmaciones")

    if args.plan and (
        args.confirm_clean_host
        or args.confirm_reviewed_source
    ):
        parser.error("Las confirmaciones requieren --apply")

    return args


def main():
    args = arguments()

    if args.plan:
        plan()
    else:
        apply()


if __name__ == "__main__":
    try:
        main()
    except (
        RuntimeError, OSError, ValueError,
        subprocess.SubprocessError,
    ) as error:
        print(f"INSTALACION_SERVICIOS_ERROR={error}")
        raise SystemExit(3)
