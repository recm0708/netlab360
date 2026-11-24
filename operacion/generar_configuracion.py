#!/usr/bin/env python3
"""Generamos un paquete de configuración aislado, sin activar el laboratorio."""

import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys


REFERENCE_REPO = Path("/home/rc-aa-ec/proyectos/netlab360")

FRR_HASHES = {
    "R-HQ": "8fcc1e756c7ad026a5dfdbdf9fc0b65ec8841e9de494fe0fe543383ba2b2ac36",
    "R-S1": "345eb21fdf66c16b82c2e3b294b5c278553232907606468a02b776f8f82ad036",
    "R-S2": "7bfb8be5d642b9c52bc628af24eb238b7b445dfc0aa3ea898badfec484f4e917",
}

UNITS = (
    "netlab360-s04-exporter.service",
    "netlab360-s05-ha-backend-hq.service",
    "netlab360-s05-ha-backend-s1.service",
    "netlab360-s05-ha-frontal-hq.service",
    "netlab360-s05-ha-monitor-s2.service",
    "netlab360-s05-noc.service",
)


def safe_source(repo, relative):
    """Limitamos las fuentes a archivos regulares del repositorio."""
    relative = Path(relative)

    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("SOURCE_OUTSIDE_REPOSITORY")

    path = repo / relative

    if path.is_symlink() or not path.is_file():
        raise ValueError("INVALID_SOURCE")

    if not path.resolve().is_relative_to(repo):
        raise ValueError("SOURCE_OUTSIDE_REPOSITORY")

    return path


def copy(source, destination, mode=0o600):
    """Creamos archivos nuevos, sin sobrescribir destinos."""
    destination.parent.mkdir(parents=True, exist_ok=True)

    with source.open("rb") as src, destination.open("xb") as dst:
        shutil.copyfileobj(src, dst)

    destination.chmod(mode)


def protected_entries(repo):
    """Validamos fuentes y destinos de instalación privilegiada."""
    path = safe_source(
        repo, "operacion/componentes-protegidos.tsv"
    )

    with path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    if len(rows) != 13:
        raise ValueError("INVALID_EXECUTOR_COUNT")

    destinations = set()

    for row in rows:
        destination = row["destino"]

        if not re.fullmatch(
            r"/usr/local/libexec/(netlab360/[a-z0-9-]+\.py|netlab360-observer)",
            destination,
        ):
            raise ValueError("INVALID_DESTINATION")

        if destination in destinations:
            raise ValueError("DUPLICATE_DESTINATION")

        destinations.add(destination)

        if row["propietario"] != "root" or row["grupo"] != "root":
            raise ValueError("INVALID_OWNER")

        if row["modo"] not in {"0750", "0755"}:
            raise ValueError("INVALID_MODE")

        source = safe_source(repo, row["fuente"])

        compile(source.read_bytes(), str(source), "exec")

    return rows


def prepare(repo, output):
    """Preparamos configuraciones en un directorio nuevo y privado."""
    repo = repo.resolve(strict=True)

    if not output.is_absolute():
        raise ValueError("ABSOLUTE_OUTPUT_REQUIRED")

    if output.exists() or output.is_symlink():
        raise ValueError("OUTPUT_EXISTS")

    output = output.resolve()

    if output.is_relative_to(repo):
        raise ValueError("OUTPUT_INSIDE_REPOSITORY")

    if not output.parent.is_dir():
        raise ValueError("OUTPUT_PARENT_MISSING")

    entries = protected_entries(repo)

    output.mkdir(mode=0o700, exist_ok=False)

    # Renderizamos la configuración candidata desde el SoT S02.
    rendered = output / "frr" / "rendered"

    renderer = safe_source(
        repo, "scripts/automatizacion/render_frr_s02.py"
    )

    subprocess.run(
        [
            sys.executable, "-B", str(renderer),
            "--inventory",
            str(repo / "inventario/ipam/topologia-s02.yaml"),
            "--output-dir", str(rendered),
        ],
        check=True,
        timeout=30,
    )

    for router, expected in FRR_HASHES.items():
        path = rendered / f"{router}.frr.conf"

        observed = hashlib.sha256(path.read_bytes()).hexdigest()

        if observed != expected:
            raise ValueError(f"FRR_BASELINE_MISMATCH_{router}")

    print("CONFIGURACIONES_FRR=3/3")

    # Preparamos las fuentes protegidas y sus destinos.
    # La propiedad root se aplicará en una etapa independiente.
    for row in entries:
        source = safe_source(repo, row["fuente"])

        relative = PurePosixPath(row["destino"]).relative_to(
            "/usr/local/libexec"
        )

        copy(
            source,
            output / "libexec" / Path(relative),
            mode=0o600,
        )

    copy(
        safe_source(repo, "operacion/componentes-protegidos.tsv"),
        output / "componentes-protegidos.tsv",
    )

    print("EJECUTORES_PREPARADOS=13/13")

    # Las unidades existentes conservan sus protecciones.
    # No sustituimos todavía sus dependencias de identidad.
    for unit in UNITS:
        copy(
            safe_source(repo, f"servicios/systemd/{unit}"),
            output / "systemd" / unit,
        )

    copy(
        safe_source(
            repo,
            "operacion/plantillas/netlab360-s04-prometheus.service"
        ),
        output / "systemd/netlab360-s04-prometheus.service",
    )

    print("UNIDADES_PREPARADAS=7/7")

    # La configuración runtime conserva el destino absoluto
    # esperado por el perfil histórico de referencia.
    template = safe_source(
        repo,
        "servicios/observabilidad/prometheus/s04-prometheus.yml"
    )

    rules = safe_source(
        repo,
        "servicios/observabilidad/prometheus/rules/s04-alerts.yml"
    )

    text = template.read_text(encoding="utf-8")

    relative_rule = "rules/s04-alerts.yml"

    if text.count(relative_rule) != 1:
        raise ValueError("PROMETHEUS_RULE_REFERENCE")

    target_rule = (
        REFERENCE_REPO /
        "servicios/observabilidad/prometheus/rules/s04-alerts.yml"
    )

    prom = output / "prometheus"
    prom.mkdir(mode=0o700)

    config = prom / "prometheus-runtime.yml"

    with config.open("x", encoding="utf-8") as f:
        f.write(text.replace(relative_rule, str(target_rule), 1))

    config.chmod(0o600)

    copy(rules, prom / "rules/s04-alerts.yml")

    copy(
        safe_source(
            repo,
            "servicios/observabilidad/prometheus/tests/s04-alertas.test.yml"
        ),
        prom / "tests/s04-alertas.test.yml",
    )

    print("PROMETHEUS_CONFIGURACION=PREPARADA")

    copy(
        safe_source(repo, "config/s05/sdn/faucet.yaml"),
        output / "sdn/faucet.yaml",
    )

    copy(
        safe_source(
            repo, "operacion/plantillas/netlab360-observer"
        ),
        output / "sudoers.d/netlab360-observer",
    )

    # Los datos describen el perfil, no una identidad activa.
    profile = {
        "schema": "NETLAB360_DEPLOYMENT_PROFILE_V1",
        "profile": "ubuntu-26.04-amd64-reference",
        "user": "rc-aa-ec",
        "hostname": "netlab360-lab",
        "repository": str(REFERENCE_REPO),
        "management": {
            "interface": "ens33",
            "address": "192.168.47.40/24",
            "gateway": "192.168.47.2",
        },
        "identity_enrollment_required": True,
        "clean_installation_validated": False,
        "portable_profile_validated": False,
        "execution_authorized": False,
    }

    with (output / "perfil.json").open(
        "x", encoding="utf-8"
    ) as f:
        json.dump(profile, f, indent=2)
        f.write("\n")

    print("CONFIGURACION_SDN=PREPARADA")
    print("SUDOERS_CANDIDATO=PREPARADO")
    print("ESTADOS_PRIVADOS_COPIADOS=NO")
    print("IDENTIDADES_HISTORICAS_COPIADAS=NO")
    print("INSTALACION_PRIVILEGIADA=NO")
    print("PAQUETE_GENERADO=" + str(output))
    print("CONFIGURACION_PREPARADA=OK")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--repo", type=Path, required=True
    )

    parser.add_argument(
        "--output", type=Path, required=True
    )

    args = parser.parse_args()

    prepare(args.repo, args.output)


if __name__ == "__main__":
    main()
