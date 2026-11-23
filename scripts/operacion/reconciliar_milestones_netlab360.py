#!/usr/bin/env python3
"""NETLAB360 — reconciliación segura de milestones S01–S08.

--check: comprobar estados de forma no mutadora.
--apply: actualizar SOLO descripciones, y si GitHub mantiene un contador
        S05 obsoleto intentar UNA desvinculación/reasignación de la issue #5
        conservando cierre/casillas; nunca reabrir issues ni milestones.

Se requiere gh CLI autenticado como colaborador del repositorio.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import sys

REPO = "recm0708/netlab360"
ENDPOINT = f"repos/{REPO}"
S05_EXPECTED = frozenset((5, 23, 31, 32, 64, 105))

DESCRIPTIONS = {
  1: """## S01 — Fundamentos, VM y línea base
**Propósito:** establecer un entorno NETLAB360 reproducible, administrable y seguro para el proyecto multisede.

**Alcance y entregables:** VMware/Ubuntu, accesos SSH y GitHub, IP fija de gestión 192.168.47.40/24, inventario IPAM, convenciones de evidencias y diseño base de redes; validaciones iniciales de la infraestructura y continuidad académica.

**Criterio de aceptación:** disponibilidad de VM y red de gestión, accesos verificables, reserva sin colisiones, documentación y pruebas iniciales registradas.

**Estado:** CERRADA y técnicamente aceptada. Este hito no acredita por sí solo la ejecución de funcionalidades avanzadas S02–S08. Referencia: issue #1.""",

  2: """## S02 — Topología multisede y enrutamiento resiliente
**Propósito:** construir la red empresarial virtual de tres sedes (HQ, S1 y S2).

**Alcance y entregables:** FRRouting, OSPF, cuatro enlaces WAN principales/alternativos, nueve VLAN, direccionamiento coherente, conmutación de enlaces y restauración de rutas.

**Criterio de aceptación:** adyacencias, conectividad, selección de rutas y failover WAN S1/S2 demostrados, con gestión VMware separada y capturas/configuraciones verificadas.

**Estado:** CERRADA y técnicamente aceptada. Se limita a topología virtual multisede de tres sedes; no representa enlaces WAN físicos. Referencias: issues #2, #13 y #14.""",

  3: """## S03 — Automatización, SoT e integración GitOps
**Propósito:** automatizar auditoría y cambios de configuración reproducibles en FRR sin perder control del estado deseado.

**Alcance y entregables:** Source of Truth (SoT) candidate, inventario, Ansible para compliance/drift/reconciliación, OpenTofu como metadatos locales con terraform_data, pruebas unitarias, PR y CI GitOps.

**Criterio de aceptación:** cambios Ansible verificables, plan idempotente OpenTofu, separación entre configuración candidata y red operativa y pruebas CI aprobadas.

**Estado:** CERRADA y técnicamente aceptada. OpenTofu no administra proveedores/recursos externos reales en esta fase; esa ampliación opcional continúa separada en S08 (#17). Referencias: issues #3, #16, #18, #19.""",

  4: """## S04 — Observabilidad, incidentes y calidad de servicio
**Propósito:** obtener visibilidad reproducible de la red y registrar degradaciones e incidentes controlados.

**Alcance y entregables:** exporter de telemetría, Prometheus/TSDB, NOC e histórico SQLite, indicadores SLI/SLO experimentales, API de incidentes y pruebas de persistencia y retorno.

**Criterio de aceptación:** fuentes, métricas, escenarios de falla/recuperación, alertas y persistencia verificadas con procedencia y pruebas CI, conservando estados UNKNOWN cuando falten datos.

**Estado:** CERRADA y técnicamente aceptada. El objetivo SLO del laboratorio no se presenta como garantía contractual en producción. Referencias: issues #4, #15 y #20–#22.""",

  5: """## S05 — Servicios resilientes, LACP, SDN y NOC integrado
**Propósito:** integrar resiliencia de servicios y enlaces con observabilidad multisede comprobable.

**Alcance y entregables:** HA HTTP lógica HQ → S1 → HQ, LACP IEEE 802.3ad en HQ/S1/S2 (2→1→2), OVS/Faucet con VLAN de comunicación/aislamiento, NOC con 18 nodos y 21 enlaces, catálogo de 71 PNG y evidencias HTTP.

**Criterio de aceptación:** conmutación y restauración reales documentadas, LACP/SDN observables, pruebas de seguridad sin afectar gestión, seis issues técnicas completadas (#5, #23, #31, #32, #64 y #105).

**Estado:** CERRADA y técnicamente aceptada; seis issues asignadas, todas cerradas. No incluye HA física, cuarta sede ni WireGuard. Propuesta opcional de ampliación reubicada en S08, issue #24. Si GitHub muestra un porcentaje menor, verificar contadores de milestone frente a las seis issues.""",

  6: """## S06 — Ciencia de datos y diagnóstico inteligente en NETLAB360
**Propósito:** convertir mediciones de red en diagnósticos explicables y contrastados con datos nuevos sin automatizar acciones sobre la infraestructura.

**Alcance y entregables:** ventanas etiquetadas y calidad de datos, control root/watchdog, regla P95, IsolationForest y LogisticRegression, inferencia y NOC de solo lectura, estudio prospectivo V2 con TRAIN→VALIDATION→TEST cronológico y muestreo homogéneo (3 ICMP), TP/FP/TN/FN, F1, recuperación y deriva descriptiva.

**Criterio de aceptación:** trazabilidad de datos, TEST no visto, ausencia de leakage, modelos congelados, seguridad y limitaciones explícitas de escenarios, FAULT y pronóstico.

**Estado:** ABIERTA, avance técnico estimado ~90 %. TEST V2 y auditoría científica validados para retardo artificial de 40 ms sobre cliente HQ; FAULT distinto aún no verificado, concept drift inferencial y pronóstico/horizonte MAE no evaluables con datos disponibles. Pendientes cierre de alcance, evidencias y revisión del informe. Issues #6, #25, #26.""",

  7: """## S07 — AIOps supervisado, recomendaciones y reversión segura
**Propósito:** operar diagnósticos S06 mediante un ciclo asistido y auditable, con decisiones y cambios sensibles siempre supervisados.

**Alcance y entregables:** correlación telemetría–estado de red–incidentes, catálogo allowlisted de acciones/runbooks, prechecks de propiedad, bloqueo, permisos y carga, explicación, recomendación, aprobación humana, ejecución, verificación y rollback.

**Criterio de aceptación:** escenarios reales reversibles y trazados de detectar → explicar → recomendar → aprobar → ejecutar → verificar → restaurar; comportamiento seguro ante UNKNOWN/falla parcial, sin shell arbitrario ni mutaciones desatendidas.

**Estado:** ABIERTA. Fuentes S04/S05 y diagnóstico S06 disponibles; el flujo AIOps propio aún no está completado. Referencia: issue #7.""",

  8: """## S08 — Consola interactiva, regresión integral y entrega académica
**Propósito:** consolidar NETLAB360 en una demostración web operativa y entregar los artefactos técnicos y académicos verificados.

**Alcance y entregables:** menú único para topología, OSPF/WAN, HA, LACP, SDN, diagnóstico IA, métricas, pruebas seguras e incidentes; APIs y acciones controladas con autorización; arranque/reconstrucción desde VM apagada, regresión, catálogo de evidencias, informe académico, presentación y TAR técnico independiente autorizado.

**Criterio de aceptación:** interfaz funcional sin shell libre, escenarios demostrables con rollback y gestión intacta, documentación y evidencias revisadas, TAR íntegro y entregables que satisfacen guía docente.

**Estado:** ABIERTA. Opcionales condicionados y no implementados: cuarta sede/WireGuard (#24), data sources/recursos externos OpenTofu (#17) y OVA/OVF si lo exige la entrega (#29). No acreditarlos como realizados ni convertirlos automáticamente en requisitos del núcleo S08."""
}
EXPECTED_STATES = {n: ("closed" if n <= 5 else "open") for n in range(1, 9)}


def gh(path: str, data: dict | None = None) -> object:
    cmd = ["gh", "api", "--method", "PATCH" if data is not None else "GET", path]
    if data is not None:
        cmd += ["--input", "-"]
    run = subprocess.run(
        cmd, input=json.dumps(data) if data is not None else None,
        capture_output=True, text=True, timeout=45, check=False,
    )
    if run.returncode:
        raise RuntimeError("github_api_failed: " + path + ": " + run.stderr.strip()[:600])
    try:
        return json.loads(run.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("github_response_not_json: " + path) from exc


def milestone(number: int) -> dict:
    obj = gh(f"{ENDPOINT}/milestones/{number}")
    if not isinstance(obj, dict) or obj.get("number") != number or obj.get("title") != f"S{number:02d}":
        raise RuntimeError(f"milestone_{number}_identity_mismatch")
    if obj.get("state") != EXPECTED_STATES[number]:
        raise RuntimeError(f"milestone_{number}_unexpected_state")
    return obj


def s05_inventory() -> dict:
    entries = gh(f"{ENDPOINT}/issues?milestone=5&state=all&per_page=100")
    if not isinstance(entries, list) or len(entries) >= 100:
        raise RuntimeError("s05_inventory_paginated_or_invalid")
    if any("pull_request" in x for x in entries):
        raise RuntimeError("s05_unexpected_pull_request")
    numbers = {x.get("number") for x in entries}
    if numbers != S05_EXPECTED:
        raise RuntimeError("s05_issue_inventory_changed: " + str(sorted(numbers)))
    if any(x.get("state") != "closed" for x in entries):
        raise RuntimeError("s05_issue_open_do_not_force_completion")
    return {"total": len(entries), "closed": len(entries), "open": 0,
            "numbers": sorted(numbers)}


def optional_issue_scope() -> None:
    item = gh(f"{ENDPOINT}/issues/24")
    if (not isinstance(item, dict) or item.get("state") != "open"
            or (item.get("milestone") or {}).get("number") != 8):
        raise RuntimeError("issue24_not_reassigned_to_s08")


def counts_ok(m: dict, inv: dict) -> bool:
    return m.get("open_issues") == inv["open"] and m.get("closed_issues") == inv["closed"]


def refresh_s05_once(inv: dict) -> None:
    before = milestone(5)
    if counts_ok(before, inv):
        print("S05_CONTADOR=100_POR_CIENTO_CONFIRMADO")
        return
    issue = gh(f"{ENDPOINT}/issues/5")
    if (issue.get("state") != "closed"
            or (issue.get("milestone") or {}).get("number") != 5):
        raise RuntimeError("s05_anchor_issue_invalid")
    print("S05_CONTADOR=DESINCRONIZADO_INTENTO_UNICO_RECUENTO")
    removed = False
    try:
        gh(f"{ENDPOINT}/issues/5", {"milestone": None})
        removed = True
        gh(f"{ENDPOINT}/issues/5", {"milestone": 5})
        removed = False
    finally:
        if removed:
            print("S05_RESTAURACION_DE_ASIGNACION=INTENTANDO")
            gh(f"{ENDPOINT}/issues/5", {"milestone": 5})
    verify = gh(f"{ENDPOINT}/issues/5")
    if verify.get("state") != "closed" or (verify.get("milestone") or {}).get("number") != 5:
        raise RuntimeError("s05_anchor_not_recovered")
    # La lista de issues por milestone puede tardar en sincronizarse tras PATCH.
    # Releer en vez de mover/reabrir una segunda vez la issue cerrada.
    inv2 = None
    for intento in range(5):
        try:
            inv2 = s05_inventory()
            break
        except RuntimeError as exc:
            if "s05_issue_inventory_changed" not in str(exc) or intento == 4:
                raise
            time.sleep(1)
    after = milestone(5)
    print(f"S05_CONTADOR_API_POST_RECUENTO={after.get('closed_issues')}/{after.get('open_issues', 0)+after.get('closed_issues',0)}")
    print("S05_RECUENTO="+("100_POR_CIENTO" if counts_ok(after, inv2)
                          else "AUN_DESINCRONIZADO_REQUIERE_SOPORTE_GITHUB"))


def run(apply: bool) -> None:
    if set(DESCRIPTIONS) != set(range(1, 9)):
        raise RuntimeError("missing_phase_descriptions")
    inv = s05_inventory()
    optional_issue_scope()
    before = [milestone(i) for i in range(1, 9)]
    print("========== NETLAB360 MILESTONES S01-S08 ==========")
    print(f"S05_INVENTARIO_REAL=CERRADAS_{inv['closed']}_ABIERTAS_{inv['open']}")
    print(f"S05_CONTADOR_API_ACTUAL=CERRADAS_{before[4]['closed_issues']}_ABIERTAS_{before[4]['open_issues']}")
    for index, m in enumerate(before, 1):
        status = "VIGENTE" if (m.get("description") or "").strip() == DESCRIPTIONS[index].strip() else "ACTUALIZACION_NECESARIA"
        print(f"MILESTONE=S{index:02d} ESTADO={m['state'].upper()} DESCRIPCION={status}")
    if not apply:
        print("MODO=SOLO_AUDITORIA")
        print("CAMBIOS_GITHUB=NINGUNO")
        return
    for number, previous in enumerate(before, 1):
        desired = DESCRIPTIONS[number].strip()
        if (previous.get("description") or "").strip() == desired:
            print(f"DESCRIPCION_S{number:02d}=YA_ACTUALIZADA")
            continue
        result = gh(f"{ENDPOINT}/milestones/{number}", {"description": desired})
        if result.get("description") != desired:
            raise RuntimeError(f"milestone_{number}_description_not_saved")
        if result.get("state") != EXPECTED_STATES[number]:
            raise RuntimeError(f"milestone_{number}_state_changed")
        print(f"DESCRIPCION_S{number:02d}=ACTUALIZADA")
    refresh_s05_once(inv)
    for i in range(1,9):
        current=milestone(i)
        if (current.get("description") or "").strip() != DESCRIPTIONS[i].strip():
            raise RuntimeError(f"milestone_{i}_final_description_mismatch")
    inv = s05_inventory()
    print("MILestones_8_DESCRIPCIONES=VERIFICADAS")
    print(f"S05_ISSUES_REALES=CERRADAS_{inv['closed']}_ABIERTAS_{inv['open']}")
    print("ISSUE24=S08_ABIERTA_OPCIONAL")
    print("FASES_01_A_05=CONSERVADAS_CERRADAS")
    print("FASES_06_A_08=CONSERVADAS_ABIERTAS")
    print("CAMBIOS_EN_REDES=NINGUNO")
    print("========== MILESTONES_NETLAB360_RECONCILIADAS=OK ==========")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = p.parse_args()
    run(a.apply)


if __name__ == "__main__":
    try: main()
    except (RuntimeError, OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as err:
        print("RECONCILIACION_ERROR=" + type(err).__name__ + ": " + str(err), file=sys.stderr)
        sys.exit(1)
