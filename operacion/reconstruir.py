#!/usr/bin/env python3
"""Reconstruimos la topología operacional en una VM nueva preparada.

Separamos preparación, construcción y aceptación.
No sustituimos recursos activos ni recuperamos identidades históricas.
"""

import argparse
import csv
import fcntl
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import time
from urllib.request import urlopen

from ciclo_vida import NETWORK_COMPONENTS, ROOT, UNITS


BASE = Path.home() / "netlab360-bootstrap"
PREFLIGHT = "/usr/local/libexec/netlab360/s07-preflight.py"

STATE_FILES = (
    "s02/wan-links-state.json",
    "s02/lan-vlan-state.json",
    "s02/runtime",
    "s05/ha/state.json",
    "s05/lacp-multisede/state-hq.json",
    "s05/lacp-multisede/state-s1.json",
    "s05/lacp-multisede/state-s2.json",
    "s05/sdn-faucet/state-sdn.json",
)

PROTECTED_STATES = (
    "s07-api", "s07-ospf-broker", "s07-ospf-trial",
    "s07-preflight", "s07-recovery", "s07-rfc-live",
    "s07-rfc-preview", "s07-wan-trial",
)

OBSERVABILITY = UNITS[:3]
HA_SERVICES = UNITS[3:]


def read(*args):
    """Consultamos el sistema con tiempo máximo y error explícito."""
    return subprocess.check_output(
        args, cwd=ROOT, text=True, timeout=30
    ).strip()


def execute(argv):
    """Ejecutamos exclusivamente los comandos del catálogo."""
    print("EJECUTAR=" + shlex.join(argv), flush=True)
    subprocess.run(argv, cwd=ROOT, check=True)


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def check_management():
    require(os.geteuid() != 0, "OPERATOR_REQUIRED")

    require(
        socket.gethostname() == "netlab360-lab",
        "HOSTNAME_NOT_SUPPORTED",
    )

    require(
        ROOT == Path.home() / "proyectos/netlab360",
        "REPOSITORY_PATH_NOT_SUPPORTED",
    )

    require(
        Path.home() == Path("/home/rc-aa-ec"),
        "USER_PROFILE_NOT_SUPPORTED",
    )

    addr = json.loads(read(
        "ip", "-j", "-4", "addr", "show", "dev", "ens33"
    ))

    require(
        len(addr) == 1 and any(
            x["local"] == "192.168.47.40"
            and x["prefixlen"] == 24
            for x in addr[0]["addr_info"]
        ),
        "ADMIN_ADDRESS_MISMATCH",
    )

    routes = json.loads(read(
        "ip", "-j", "-4", "route", "show", "default"
    ))

    require(
        len(routes) == 1
        and routes[0].get("gateway") == "192.168.47.2"
        and routes[0].get("dev") == "ens33",
        "ADMIN_ROUTE_MISMATCH",
    )


def check_empty_resources():
    """Rechazamos incluso contenedores detenidos y recursos ajenos."""
    require(
        not read("sudo", "-n", "docker", "ps", "-aq"),
        "HOST_HAS_CONTAINERS",
    )

    require(
        not read("sudo", "-n", "ip", "netns", "list"),
        "HOST_HAS_NAMESPACES",
    )

    require(
        not read("sudo", "-n", "ovs-vsctl", "list-br"),
        "HOST_HAS_OVS_BRIDGES",
    )

    for name in STATE_FILES:
        path = BASE / name

        require(
            not path.exists() and not path.is_symlink(),
            f"EXISTING_RUNTIME_STATE: {name}",
        )


def check_images():
    """Verificamos imágenes locales sin descargarlas."""
    path = ROOT / "operacion/imagenes.tsv"

    with path.open(encoding="utf-8") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))

    require(
        {r["componente"] for r in rows}
        == {"frr", "faucet", "prometheus"},
        "IMAGE_MANIFEST_INVALID",
    )

    for row in rows:
        reference = read(
            "sudo", "-n", "docker", "image", "inspect",
            "--format", "{{.Id}} {{.Architecture}}",
            row["referencia_inmutable"],
        )

        observed = read(
            "sudo", "-n", "docker", "image", "inspect",
            "--format", "{{.Id}} {{.Architecture}}",
            row["imagen_observada"],
        )

        require(
            reference == observed
            and reference.endswith(" amd64"),
            "IMAGE_REFERENCE_MISMATCH: "
            + row["componente"],
        )


def check_prepared_configuration():
    """Exigimos configuraciones previamente revisadas."""
    for name in (
        "s02/rendered/R-HQ.frr.conf",
        "s02/rendered/R-S1.frr.conf",
        "s02/rendered/R-S2.frr.conf",
        "s05/sdn-faucet/config/faucet.yaml",
        "prometheus/s04/prometheus-runtime.yml",
    ):
        path = BASE / name

        require(
            path.is_file() and not path.is_symlink(),
            f"CONFIGURATION_MISSING: {name}",
        )

    for name in (
        "s05/sdn-faucet/logs",
        "prometheus/s04/data",
    ):
        path = BASE / name

        require(
            path.is_dir() and not path.is_symlink(),
            f"PREPARED_DIRECTORY_MISSING: {name}",
        )

    for name in ("prometheus", "promtool"):
        path = BASE / "prometheus/bin" / name

        require(
            path.is_file() and os.access(path, os.X_OK),
            f"BINARY_MISSING: {name}",
        )

    read(
        str(BASE / "prometheus/bin/promtool"),
        "check", "config",
        str(BASE / "prometheus/s04/prometheus-runtime.yml"),
    )


def check_protected_components():
    """Comparamos las fuentes revisadas con las copias instaladas."""
    path = ROOT / "operacion/componentes-protegidos.tsv"

    # Las tres primeras columnas identifican las fuentes y destinos.
    # Localizamos las rutas por su formato para admitir la cabecera
    # del manifiesto sin duplicar su esquema.
    lines = path.read_text(encoding="utf-8").splitlines()
    checked = 0

    for line in lines:
        fields = line.split("\t")

        sources = [
            x for x in fields
            if x.startswith("scripts/")
            and x.endswith(".py")
        ]

        targets = [
            x for x in fields
            if x.startswith("/usr/local/libexec/")
        ]

        if not sources and not targets:
            continue

        require(
            len(sources) == len(targets) == 1,
            "PROTECTED_MANIFEST_INVALID",
        )

        source = ROOT / sources[0]
        target = targets[0]

        expected_mode = (
            "750" if source.parent.name == "s06"
            else "755"
        )

        read("sudo", "-n", "cmp", "--", str(source), target)

        metadata = read(
            "sudo", "-n", "stat",
            "-c", "%U:%G %a %F", target,
        )

        require(
            metadata == f"root:root {expected_mode} regular file",
            f"PROTECTED_PERMISSIONS_INVALID: {target}",
        )

        checked += 1

    require(checked == 13, "PROTECTED_COUNT_INVALID")

    for name in PROTECTED_STATES:
        path = f"/var/lib/netlab360/{name}"

        metadata = read(
            "sudo", "-n", "stat",
            "-c", "%U:%G %a %F", path,
        )

        require(
            metadata == "root:root 700 directory",
            f"STATE_PERMISSIONS_INVALID: {name}",
        )

        require(
            not read(
                "sudo", "-n", "find", path,
                "-mindepth", "1", "-maxdepth", "1", "-print",
            ),
            f"PROTECTED_STATE_NOT_EMPTY: {name}",
        )


def check_units():
    """Las unidades deben estar instaladas, pero aún no iniciadas."""
    for unit in UNITS:
        raw = read(
            "systemctl", "show", unit,
            "-p", "LoadState",
            "-p", "ActiveState",
            "-p", "FragmentPath",
            "-p", "DropInPaths",
        )

        data = dict(
            line.split("=", 1)
            for line in raw.splitlines()
        )

        require(
            data.get("LoadState") == "loaded"
            and data.get("ActiveState") == "inactive"
            and data.get("FragmentPath")
            == "/etc/systemd/system/" + unit
            and not data.get("DropInPaths"),
            f"UNIT_NOT_PREPARED: {unit}",
        )


def check_clean():
    """Puerta de entrada para una VM nueva, nunca para recuperar la actual."""
    read("sudo", "-n", "true")

    check_management()

    # Primero descartamos recursos activos, sin invocar instaladores.
    check_empty_resources()

    require(
        not read("git", "status", "--porcelain"),
        "REPOSITORY_NOT_CLEAN",
    )

    check_images()
    check_prepared_configuration()
    check_protected_components()
    check_units()

    print("VM_NUEVA_PREPARADA=OK")


def network_steps(name):
    """Conservamos las confirmaciones originales de cada componente."""
    _, source, flag = next(
        item for item in NETWORK_COMPONENTS
        if item[0] == name
    )

    return [
        ("command", ("python3", source, "precheck")),
        ("command", ("python3", source, "up", flag)),
        ("command", ("python3", source, "status")),
    ]


def service_steps(units):
    return [
        ("command", ("sudo", "-n", "systemctl", "start", unit))
        for unit in units
    ]


def steps():
    """Intercalamos los servicios que exigen los prechecks originales."""
    result = [
        ("command", (
            "python3",
            "scripts/automatizacion/preparar_runtime_frr_s02.py",
        )),
        ("command", (
            "bash", "scripts/laboratorio/s02-routers-start.sh",
        )),
    ]

    result += network_steps("WAN")

    result.append(("command", (
        "python3", "scripts/validacion/validar_ospf_s02.py",
    )))

    result += network_steps("LAN")

    result.append(("command", (
        "python3", "scripts/validacion/validar_lan_s02.py",
    )))

    result += service_steps(OBSERVABILITY)
    result.append(("wait", ("baseline",)))

    result += network_steps("HA")
    result += service_steps(HA_SERVICES)
    result.append(("wait", ("ha",)))

    for name in ("LACP_HQ", "LACP_S1", "LACP_S2", "SDN"):
        result += network_steps(name)

    # El registro se realiza únicamente para identidades nuevas.
    # No autoriza RFC ni actuaciones sobre los routers.
    result.append(("command", (
        "sudo", "-n", "/usr/bin/python3",
        "-I", PREFLIGHT, "enroll",
    )))

    result.append(("command", (
        "bash", "operacion/estado.sh",
    )))

    return result


def read_http(url):
    with urlopen(url, timeout=5) as response:
        return json.load(response)


def graph_ready(graph, phase):
    if phase not in {"baseline", "ha"}:
        raise ValueError("UNKNOWN_READINESS_PHASE")

    routes = graph.get("routing", {}).get("routes", {})

    ready = (
        graph.get("telemetry", {}).get("available") is True
        and graph.get("routing", {}).get("available") is True
        and routes.get("S1", {}).get("dev") == "s1p"
        and routes.get("S2", {}).get("dev") == "s2p"
    )

    if phase == "ha":
        ready = (
            ready
            and graph.get("ha_service", {}).get("available") is True
        )

    return ready


def wait_ready(phase):
    """Esperamos observaciones válidas, no solamente procesos activos."""
    deadline = time.monotonic() + 90

    while time.monotonic() < deadline:
        try:
            graph = read_http(
                "http://127.0.0.1:9130/api/v1/graph"
            )

            source = read_http(
                "http://127.0.0.1:9110/api/v1/state"
            )

            if (
                source.get("source_ok") is True
                and source.get("topology") == "active"
                and graph_ready(graph, phase)
            ):
                print(f"READINESS_{phase.upper()}=OK")
                return

        except (OSError, ValueError, TypeError):
            pass

        time.sleep(3)

    raise RuntimeError(f"READINESS_TIMEOUT: {phase}")


def plan():
    print("MODO=PLAN")

    for index, (kind, argv) in enumerate(steps(), 1):
        value = (
            shlex.join(argv)
            if kind == "command"
            else "ESPERAR_TELEMETRIA_VALIDADA=" + argv[0]
        )

        print(f"{index:02d}. {value}")

    print(f"ACCIONES_PLANIFICADAS={len(steps())}")
    print("RECONSTRUCCION_EJECUTADA=NO")
    print("PLAN_RECONSTRUCCION=OK")


def run_steps(executor=execute, waiter=wait_ready):
    """Abortamos en el primer error, conservando los estados creados."""
    for kind, argv in steps():
        if kind == "command":
            executor(argv)
        elif kind == "wait":
            waiter(argv[0])
        else:
            raise ValueError("UNKNOWN_STEP_KIND")


def apply():
    check_clean()

    lock = BASE / ".reconstruccion.lock"

    fd = os.open(
        lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW,
        0o600,
    )

    with os.fdopen(fd, "w") as handle:
        fcntl.flock(
            handle.fileno(),
            fcntl.LOCK_EX | fcntl.LOCK_NB,
        )

        # Volvemos a comprobar dentro de la exclusión mutua.
        check_clean()

        try:
            run_steps()
        except BaseException:
            print("RECONSTRUCCION_INCOMPLETA=REQUIERE_REVISION")
            print("ESTADOS_CONSERVADOS=SI")
            print("REINTENTO_AUTOMATICO=NO")
            raise

    print("RECONSTRUCCION_EJECUTADA=SI")
    print("ACEPTACION_OPERACIONAL_BASICA=OK")
    print("VALIDACION_CIENTIFICA_HISTORICA=NO_REPRODUCIDA")


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)

    mode = parser.add_mutually_exclusive_group(required=True)

    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--check-clean", action="store_true")
    mode.add_argument("--apply", action="store_true")

    parser.add_argument(
        "--confirm-clean-host", action="store_true"
    )
    parser.add_argument(
        "--confirm-snapshot", action="store_true"
    )
    parser.add_argument(
        "--confirm-reviewed-config", action="store_true"
    )
    parser.add_argument(
        "--confirm-new-identity", action="store_true"
    )

    args = parser.parse_args(argv)

    confirmations = (
        args.confirm_clean_host,
        args.confirm_snapshot,
        args.confirm_reviewed_config,
        args.confirm_new_identity,
    )

    if args.apply and not all(confirmations):
        parser.error("Se requieren las cuatro confirmaciones")

    if not args.apply and any(confirmations):
        parser.error("Las confirmaciones requieren --apply")

    return args


def main():
    args = arguments()

    if args.plan:
        plan()
    elif args.check_clean:
        check_clean()
    else:
        apply()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError,
            subprocess.SubprocessError) as error:
        print(f"RECONSTRUCCION_ERROR={error}")
        raise SystemExit(3)
