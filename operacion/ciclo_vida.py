#!/usr/bin/env python3
"""Organizamos las dependencias operacionales de NETLAB360.

El catálogo presenta procedimientos revisables. No ejecuta
los comandos de despliegue ni concede autorización.
"""

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

UNITS = (
    "netlab360-s04-exporter.service",
    "netlab360-s04-prometheus.service",
    "netlab360-s05-noc.service",
    "netlab360-s05-ha-backend-hq.service",
    "netlab360-s05-ha-backend-s1.service",
    "netlab360-s05-ha-frontal-hq.service",
    "netlab360-s05-ha-monitor-s2.service",
)

CONTAINERS = (
    "nl360-s02-r-hq",
    "nl360-s02-r-s1",
    "nl360-s02-r-s2",
    "nl360-s05-faucet",
)

NETWORK_COMPONENTS = (
    ("WAN", "scripts/laboratorio/s02_wan_links.py",
     "--snapshot-confirmado"),
    ("LAN", "scripts/laboratorio/s02_lan_vlan.py",
     "--snapshot-confirmado"),
    ("HA", "scripts/laboratorio/s05_ha_red_servicios.py",
     "--confirm-isolated"),
    ("LACP_HQ", "scripts/laboratorio/s05_lacp_hq_integracion.py",
     "--confirm-isolated"),
    ("LACP_S1", "scripts/laboratorio/s05_lacp_s1_integracion.py",
     "--confirm-isolated"),
    ("LACP_S2", "scripts/laboratorio/s05_lacp_s2_integracion.py",
     "--confirm-isolated"),
    ("SDN", "scripts/laboratorio/s05_sdn_ovs_faucet_aislado.py",
     "--confirm-isolated"),
)

# Las puertas de aceptación impiden confundir un plan
# con una ejecución autorizada sobre recursos activos.
DEPLOYMENT = (
    ("01", "Verificar perfil y aislamiento administrativo",
     "operacion/verificar.sh"),
    ("02", "Instalar dependencias e imágenes en VM nueva",
     "operacion/instalar.sh"),
    ("03", "Generar configuraciones independientes",
     "operacion/configurar.sh"),
    ("04", "Instalar fuentes privilegiadas revisadas",
     "operacion/instalar-protegidos.sh"),
    ("05", "Renderizar configuración FRR S02",
     "scripts/automatizacion/render_frr_s02.py"),
    ("06", "Preparar runtime FRR y permisos internos",
     "scripts/automatizacion/preparar_runtime_frr_s02.py"),
    ("07", "Iniciar exclusivamente los tres routers",
     "scripts/laboratorio/s02-routers-start.sh"),
    ("08", "Construir enlaces WAN",
     NETWORK_COMPONENTS[0][1]),
    ("09", "Validar adyacencias OSPF",
     "scripts/validacion/validar_ospf_s02.py"),
    ("10", "Construir LAN y nueve VLAN",
     NETWORK_COMPONENTS[1][1]),
    ("11", "Validar segmentación y conectividad LAN",
     "scripts/validacion/validar_lan_s02.py"),
    ("12", "Construir red de servicios HA",
     NETWORK_COMPONENTS[2][1]),
    ("13", "Construir agregación LACP HQ",
     NETWORK_COMPONENTS[3][1]),
    ("14", "Construir agregación LACP S1",
     NETWORK_COMPONENTS[4][1]),
    ("15", "Construir agregación LACP S2",
     NETWORK_COMPONENTS[5][1]),
    ("16", "Construir dominio SDN independiente",
     NETWORK_COMPONENTS[6][1]),
    ("17", "Revisar identidades de los nuevos routers",
     "scripts/s07/preflight_protegido.py"),
    ("18", "Comprobar el entorno científico",
     "requirements-cientifico.txt"),
    ("19", "Comprobar estado operacional integrado",
     "operacion/estado.sh"),
)

GATES = (
    "VM dedicada, sin recursos anteriores ni ajenos.",
    "Comprobar perfil y ausencia de colisiones.",
    "Verificar imágenes y fuentes administrativas.",
    "Instalar unidades y sudoers mediante revisión separada.",
    "Confirmar salvaguarda real antes de las operaciones S02.",
    "Validar cada etapa antes de ejecutar la siguiente.",
    "No copiar estados de propiedad ni identidades anteriores.",
    "Iniciar servicios solamente después de crear sus redes.",
    "No iniciar automáticamente API, broker ni actuaciones RFC.",
    "Detenerse ante errores o propiedad no verificable.",
)


def validate_catalog():
    """Comprobamos referencias y el orden de dependencias."""
    steps = [item[0] for item in DEPLOYMENT]

    if steps != [f"{n:02d}" for n in range(1, 20)]:
        raise ValueError("INVALID_DEPLOYMENT_ORDER")

    for _, _, name in DEPLOYMENT:
        path = ROOT / name

        if not path.is_file() or path.is_symlink():
            raise ValueError(f"MISSING_COMPONENT: {name}")

    for _, name, flag in NETWORK_COMPONENTS:
        source = (ROOT / name).read_text()

        if flag not in source:
            raise ValueError(f"CONFIRMATION_MISSING: {name}")

    return True


def deployment_plan():
    """Presentamos las etapas sin ejecutar acciones mutadoras."""
    validate_catalog()

    print("MODO=PLAN")
    print("PERFIL=ubuntu-26.04-amd64")

    for number, description, path in DEPLOYMENT:
        print(f"{number}. {description}")
        print(f"    COMPONENTE={path}")

    print("========== CONTRATOS DE RED ==========")

    for name, path, flag in NETWORK_COMPONENTS:
        print(f"{name}_PLAN=python3 {path} plan")
        print(f"{name}_PRECHECK=python3 {path} precheck")
        print(f"{name}_UP=python3 {path} up {flag}")
        print(f"{name}_STATUS=python3 {path} status")

    print("========== ORDEN DE SERVICIOS ==========")
    print("ANTES_DE_HA=Exporter, Prometheus y NOC")
    print("ANTES_DE_LACP=Cuatro servicios HTTP HA")
    print("EJECUCION_CANDIDATA=operacion/reconstruir.py")

    for unit in UNITS:
        print(f"ORDEN_SERVICIO={unit}")

    print("========== PUERTAS DE ACEPTACION ==========")

    for requirement in GATES:
        print(f"REQUISITO={requirement}")

    print("ETAPAS_PLANIFICADAS=19")
    print("COMPONENTES_RED=7")
    print("SERVICIOS_PLANIFICADOS=7")
    print("DESPLIEGUE_EJECUTADO=NO")
    print("DESPLIEGUE_AUTOMATICO_VALIDADO=NO")
    print("PLAN_DESPLIEGUE=OK")


def shutdown_plan():
    """Describimos el orden inverso sin retirar recursos."""
    print("MODO=PLAN_DETENCION")

    print("REQUISITO=No tener RFC, ensayos ni watchdogs activos.")

    for unit in reversed(UNITS):
        print(f"DETENER_SERVICIO={unit}")

    for name, path, _ in reversed(NETWORK_COMPONENTS):
        print(f"REVISAR_RETIRADA={name} | {path}")

    print("ULTIMA_ETAPA=Routers FRR tras retirar WAN y LAN.")
    print("PRESERVAR=Estados, bases de datos y configuraciones.")
    print("DETENCION_EJECUTADA=NO")


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "action",
        choices=("deploy-plan", "shutdown-plan"),
    )

    args = parser.parse_args()

    if args.action == "deploy-plan":
        deployment_plan()
    else:
        shutdown_plan()


if __name__ == "__main__":
    main()
