#!/usr/bin/env python3
"""Audita y normaliza los hitos de NETLAB360 sin alterar sus estados."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

REPO = "recm0708/netlab360"
ENDPOINT = f"repos/{REPO}"

DESCRIPTIONS = {
  1: """## Fase 1 — Fundamentos, VM y línea base
**Propósito:** establecer un entorno NETLAB360 reproducible, administrable y seguro para el proyecto multisede.

**Alcance y entregables:** VMware/Ubuntu, accesos SSH y GitHub, IP fija de gestión 192.168.47.40/24, inventario IPAM, convenciones de evidencias y diseño base de redes; validaciones iniciales de la infraestructura y continuidad académica.

**Criterio de aceptación:** disponibilidad de VM y red de gestión, accesos verificables, reserva sin colisiones, documentación y pruebas iniciales registradas.

**Estado:** CERRADA y técnicamente aceptada. Este hito no acredita por sí solo la ejecución de funcionalidades avanzadas de las fases 02–08. Referencia: issue #1.""",

  2: """## Fase 2 — Topología multisede y enrutamiento resiliente
**Propósito:** construir la red empresarial virtual de tres sedes (HQ, S1 y S2).

**Alcance y entregables:** FRRouting, OSPF, cuatro enlaces WAN principales/alternativos, nueve VLAN, direccionamiento coherente, conmutación de enlaces y restauración de rutas.

**Criterio de aceptación:** adyacencias, conectividad, selección de rutas y failover WAN S1/S2 demostrados, con gestión VMware separada y capturas/configuraciones verificadas.

**Estado:** CERRADA y técnicamente aceptada. Se limita a topología virtual multisede de tres sedes; no representa enlaces WAN físicos. Referencias: issues #2, #13 y #14.""",

  3: """## Fase 3 — Automatización, SoT e integración GitOps
**Propósito:** automatizar auditoría y cambios de configuración reproducibles en FRR sin perder control del estado deseado.

**Alcance y entregables:** Source of Truth (SoT) candidate, inventario, Ansible para compliance/drift/reconciliación, OpenTofu como metadatos locales con terraform_data, pruebas unitarias, PR y CI GitOps.

**Criterio de aceptación:** cambios Ansible verificables, plan idempotente OpenTofu, separación entre configuración candidata y red operativa y pruebas CI aprobadas.

**Estado:** CERRADA y técnicamente aceptada. OpenTofu no administra proveedores/recursos externos reales en esta fase; esa ampliación corresponde a la fase 09 (#17). Referencias: issues #3, #16, #18, #19.""",

  4: """## Fase 4 — Observabilidad, incidentes y calidad de servicio
**Propósito:** obtener visibilidad reproducible de la red y registrar degradaciones e incidentes controlados.

**Alcance y entregables:** exporter de telemetría, Prometheus/TSDB, NOC e histórico SQLite, indicadores SLI/SLO experimentales, API de incidentes y pruebas de persistencia y retorno.

**Criterio de aceptación:** fuentes, métricas, escenarios de falla/recuperación, alertas y persistencia verificadas con procedencia y pruebas CI, conservando estados UNKNOWN cuando falten datos.

**Estado:** CERRADA y técnicamente aceptada. El objetivo SLO del laboratorio no se presenta como garantía contractual en producción. Referencias: issues #4, #15 y #20–#22.""",

  5: """## Fase 5 — Servicios resilientes, LACP, SDN y NOC integrado
**Propósito:** integrar resiliencia de servicios y enlaces con observabilidad multisede comprobable.

**Alcance y entregables:** HA HTTP lógica HQ → S1 → HQ, LACP IEEE 802.3ad en HQ/S1/S2 (2→1→2), OVS/Faucet con VLAN de comunicación/aislamiento, NOC con 18 nodos y 21 enlaces, catálogo de 71 PNG y evidencias HTTP.

**Criterio de aceptación:** conmutación y restauración reales documentadas, LACP/SDN observables, pruebas de seguridad sin afectar gestión, seis issues técnicas completadas (#5, #23, #31, #32, #64 y #105).

**Estado:** CERRADA y técnicamente aceptada; seis issues asignadas, todas cerradas. No incluye HA física, cuarta sede ni WireGuard. La ampliación WireGuard corresponde a la fase 09, issue #24; una cuarta sede permanece condicionada. Si GitHub muestra un porcentaje menor, contrastar el contador con todas las issues y pull requests asignados.""",

  6: """## Fase 6 — Ciencia de datos y diagnóstico inteligente en NETLAB360
**Propósito:** convertir mediciones de red en diagnósticos explicables y contrastados con datos nuevos sin automatizar acciones sobre la infraestructura.

**Alcance y entregables:** ventanas etiquetadas y calidad de datos, control root/watchdog, regla P95, IsolationForest y LogisticRegression, inferencia y NOC de solo lectura, estudio prospectivo V2 con TRAIN→VALIDATION→TEST cronológico y muestreo homogéneo (3 ICMP), TP/FP/TN/FN, F1, recuperación y deriva descriptiva.

**Criterio de aceptación:** trazabilidad de datos, TEST no visto, ausencia de leakage, modelos congelados, seguridad y limitaciones explícitas de escenarios, FAULT y pronóstico.

**Estado:** CERRADA y técnicamente aceptada. TEST V2 y auditoría científica validados para degradación ICMP controlada. FAULT HTTP HQ independiente y recuperación verificados, sin alterar TEST V2. Concept drift inferencial y pronóstico/horizonte MAE no evaluables. Once capturas incorporadas al catálogo oficial. Issues #6, #25 y #26 cerradas.""",

  7: """## Fase 7 — AIOps supervisado

**Propósito:** integrar diagnóstico y gestión supervisada de intervenciones.

**Alcance y entregables:** normalización de eventos, correlación RCA,
runbooks, Intent Assurance, RFC, aprobación administrativa, ejecución
protegida, watchdog y API local controlada.

**Criterio de aceptación:** intervenciones delimitadas con autorización,
auditoría, verificación y recuperación independiente.

**Estado:** CERRADA. Issues #7 y #190–#197 completadas, 49 capturas
oficiales y 253 acumuladas. Informe 7.3 revisado (184 páginas).
Regresión histórica: 1258 casos, uno omitido y cero fallos.
La aceptación no demuestra pronóstico futuro ni remediación autónoma.
""",

  8: """## Fase 8 — Integración y plataforma interactiva

**Propósito:** consolidar las funcionalidades de NETLAB360 en una aplicación web operativa, segura y demostrable.

**Alcance y entregables:** consola integrada, FastAPI, interfaz gráfica, pruebas ICMP/HTTP/TCP/UDP, sondas Blackbox, SLI/SLO, error budget, burn rate, Alertmanager, evaluación de Grafana especializado, ML, RCA, RAG, RFC supervisadas y recuperación automática.

**Criterio de aceptación:** integración con datos reales, controles de seguridad, acciones delimitadas con retorno independiente, recuperación desde apagado completo, regresión y catálogo gráfico de la fase.

**Estado:** ABIERTA. Implementación pendiente. Las ampliaciones tecnológicas corresponden a la fase 09 y la aceptación científica y entrega final a la fase 10.""",

  9: """## Fase 9 — Ampliación tecnológica y automatización avanzada

**Propósito:** extender la cobertura tecnológica de NETLAB360 mediante implementaciones reales, aisladas y reproducibles.

**Alcance y entregables:** OpenTofu con proveedores y recursos reales, WireGuard, Ansible multivendor con VyOS, GitOps periódico, gNMI/OpenConfig, gRPC/Protobuf, Kubernetes, Cilium, Hubble, eBPF y OpenTelemetry.

**Criterio de aceptación:** casos de uso verificables, recursos autorizados, protección de la red administrativa, interoperabilidad, observabilidad, integración con la consola y regresión.

**Estado:** ABIERTA. Ampliación aprobada dentro de la planificación del equipo, pendiente de implementación. La arquitectura concreta de cada tecnología depende de su viabilidad y de sus requisitos de seguridad.""",

  10: """## Fase 10 — Validación científica, aceptación integral y entrega

**Propósito:** ampliar la evaluación experimental de NETLAB360 y consolidar su aceptación técnica y académica.

**Alcance y entregables:** datasets independientes, evaluación ML, predicción temporal, MAE, capacidad TCP/UDP, QoS/QoE, explicabilidad, concept drift, RCA, regresión integral, informe PDF, presentación y TAR técnico.

**Criterio de aceptación:** resultados reproducibles, separación cronológica de datos, evaluación independiente, limitaciones explícitas, seguridad, demostración integrada y entregables verificados.

**Estado:** ABIERTA. Planificación aprobada por el equipo; experimentos y entrega pendientes. La exportación OVA/OVF permanece condicionada a confirmación docente."""
}


# Los estados se corresponden con la aceptación al cierre de la fase 07.
EXPECTED_STATES = {
    n: "closed" if n <= 7 else "open"
    for n in range(1, 11)
}


EXPECTED_ISSUES = {
    5: {5, 23, 31, 32, 64, 105},
    7: {7, *range(190, 198)},
}


def gh(path, data=None, *, paginate=False):
    """Consulta REST paginada o modificación explícita de metadatos."""
    command = ["gh", "api", path]

    if paginate:
        if data is not None:
            raise ValueError("pagination_with_write")
        command += ["--paginate", "--slurp"]

    if data is not None:
        command += ["--method", "PATCH", "--input", "-"]

    result = subprocess.run(
        command,
        input=json.dumps(data) if data is not None else None,
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )

    value = json.loads(result.stdout)

    if paginate:
        if not isinstance(value, list) or not all(
            isinstance(page, list) for page in value
        ):
            raise RuntimeError("invalid_pagination")
        return [item for page in value for item in page]

    return value


def milestone(number):
    """Valida identidad y estado sin depender exclusivamente del título."""
    result = gh(f"{ENDPOINT}/milestones/{number}")

    if (
        result.get("number") != number
        or result.get("title") not in {
            f"S{number:02d}", f"Fase {number}"
        }
    ):
        raise RuntimeError(f"milestone_{number}_identity_mismatch")

    if result.get("state") != EXPECTED_STATES[number]:
        raise RuntimeError(f"milestone_{number}_unexpected_state")

    return result


def global_entries():
    """Recupera un inventario global independiente de los títulos."""
    rows = gh(
        f"{ENDPOINT}/issues?state=all&per_page=100",
        paginate=True
    )

    seen = set()

    for row in rows:
        number = row["number"]
        membership = (row.get("milestone") or {}).get("number")

        if number in seen or row.get("state") not in {"open", "closed"}:
            raise RuntimeError("invalid_inventory")

        if membership is not None and membership not in EXPECTED_STATES:
            raise RuntimeError("unknown_milestone_membership")

        seen.add(number)

    return rows

def inventory(number, *, entries=None):
    """Cuenta las asignaciones reales de issues y pull requests."""
    rows = global_entries() if entries is None else entries

    items = {}

    for entry in rows:
        if (entry.get("milestone") or {}).get("number") != number:
            continue

        identifier = entry["number"]

        if identifier in items:
            raise RuntimeError("invalid_inventory")

        items[identifier] = (
            "pr" if "pull_request" in entry else "issue",
            entry["state"]
        )

    issues = {
        key for key, value in items.items()
        if value[0] == "issue"
    }

    if number in EXPECTED_ISSUES and issues != EXPECTED_ISSUES[number]:
        raise RuntimeError(f"phase_{number}_issue_inventory_changed")

    opened = sum(value[1] == "open" for value in items.values())
    closed = len(items) - opened

    if EXPECTED_STATES[number] == "closed" and opened:
        raise RuntimeError(f"phase_{number}_open_items")

    if number == 7:
        if items.get(202) != ("pr", "closed"):
            raise RuntimeError("phase_7_pr_202_missing")

        pr = gh(f"{ENDPOINT}/pulls/202")

        if pr.get("state") != "closed" or pr.get("merged") is not True:
            raise RuntimeError("phase_7_pr_202_not_merged")

    return {"items": items, "open": opened, "closed": closed}



def all_inventories():
    """Contrasta todos los hitos mediante una misma consulta global."""
    rows = global_entries()

    return {
        number: inventory(number, entries=rows)
        for number in EXPECTED_STATES
    }


def counts_ok(hito, observed):
    """Distingue el inventario real del contador remoto."""
    return (
        hito.get("open_issues") == observed["open"]
        and hito.get("closed_issues") == observed["closed"]
    )


def run(apply):
    """La aplicación solo modifica títulos y descripciones."""
    before = {n: milestone(n) for n in EXPECTED_STATES}
    inventories = all_inventories()

    for n, current in before.items():
        inv = inventories[n]

        print(
            f"FASE={n:02d} TITULO={current['title']} "
            f"ESTADO={current['state']} "
            f"ABIERTOS_REALES={inv['open']} "
            f"CERRADOS_REALES={inv['closed']} "
            f"CONTADOR={'OK' if counts_ok(current, inv) else 'DISCREPANCIA'} "
            f"DESCRIPCION={'OK' if current.get('description') == DESCRIPTIONS[n].strip() else 'ACTUALIZAR'}"
        )

    if not apply:
        print("CAMBIOS_GITHUB=NINGUNO")
        return

    # Conservamos estados, fechas, membresías y numeración.
    for n, current in before.items():
        desired = {
            "title": f"Fase {n}",
            "description": DESCRIPTIONS[n].strip()
        }

        if any(current.get(k) != v for k, v in desired.items()):
            gh(f"{ENDPOINT}/milestones/{n}", desired)

        verified = milestone(n)

        if any(verified.get(k) != v for k, v in desired.items()):
            raise RuntimeError(f"phase_{n}_metadata_not_saved")

        if verified.get("due_on") != current.get("due_on"):
            raise RuntimeError(f"phase_{n}_due_date_changed")

        print(f"FASE_{n:02d}_METADATOS=VERIFICADOS")

    final_inventories = all_inventories()

    if final_inventories != inventories:
        raise RuntimeError("global_milestone_membership_changed")

    print("ASIGNACIONES_ORIGINALES=CONSERVADAS")
    print("MILESTONES_NETLAB360=ACTUALIZADAS")


def main():
    parser = argparse.ArgumentParser(description=__doc__)

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")

    args = parser.parse_args()
    run(args.apply)


if __name__ == "__main__":
    try:
        main()
    except (
        RuntimeError, OSError, ValueError, KeyError,
        TypeError, subprocess.SubprocessError
    ) as error:
        print("RECONCILIACION_ERROR=" + str(error), file=sys.stderr)
        sys.exit(1)
