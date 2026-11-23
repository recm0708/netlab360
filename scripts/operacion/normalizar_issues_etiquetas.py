#!/usr/bin/env python3
"""NETLAB360: normalizar las 53 issues y TODAS las etiquetas del repositorio.

--check: lectura de inventario, estados, casillas, títulos, etiquetas.
--apply: migrar nombres/descripciones de etiquetas, asignaciones semánticas,
         sin modificar cuerpo, estado, milestones ni campos de PR.
Las issues duplicadas o no planificadas conservan su motivo nativo en GitHub.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import subprocess
import sys
from urllib.parse import quote

REPO = "recm0708/netlab360"
ROOT = "repos/" + REPO

PHASES = {
    1: (1,9,10,11,12,30,33,35,38,39,40,41,42,46),
    2: (2,13,14),
    3: (3,16,18,19,51),
    4: (4,15,20,21,22,47),
    5: (5,23,31,32,64,105),
    6: (6,25,26,153),
    7: (7,),
    8: (8,17,24,27,28,29,34,36,37,43,44,45,48,106),
}
THEMES = {
    "infraestructura": (1,5,10,11,24,30,39,41,106),
    "enrutamiento": (2,13,14,42),
    "automatización": (3,7,16,17,18,19,33,40),
    "observabilidad": (4,12),
    "telemetría": (20,21),
    "seguridad": (22,38),
    "disponibilidad": (31,32),
    "sdn": (23,),
    "documentación": (35,43,51,105),
    "datos": (25,),
    "inteligencia-artificial": (6,26),
    "entrega": (8,27,28,29,37,44,45),
    "gestión-académica": (9,36,46,47,48),
    "pruebas": (34,153),
    "visualización": (15,64),
}
URGENT = frozenset((6,7,8,25,26,27,43,44,45,106))
OPTIONAL = frozenset((17,24,28,29,37))
EXPECTED_CLOSED = frozenset(
    n for f, nums in PHASES.items() for n in nums
    if f <= 5 or n in (28,37,153)
)
ALL_IDS = frozenset(n for nums in PHASES.values() for n in nums)

TYPE_INFO = {
    "infraestructura": ("1D76DB", "Equipos, VM, conectividad, inventario y servicios fundamentales."),
    "enrutamiento": ("0E8A16", "FRRouting, OSPF, rutas WAN y conmutación entre sedes."),
    "automatización": ("006B75", "Ansible, OpenTofu, GitOps, CI y procedimientos automatizados."),
    "observabilidad": ("0E8A16", "Supervisión y registro del estado de redes y servicios."),
    "telemetría": ("1D76DB", "Métricas, series temporales, indicadores SLI y Prometheus."),
    "seguridad": ("B60205", "Seguridad de acceso, aislamiento, privilegios y reversión."),
    "disponibilidad": ("5319E7", "Alta disponibilidad, agregación y recuperación controlada."),
    "sdn": ("0052CC", "Redes definidas por software con Open vSwitch y Faucet."),
    "documentación": ("C2E0C6", "Documentos, evidencias gráficas, catálogos y trazabilidad técnica."),
    "datos": ("BFD4F2", "Datos de entrenamiento, procedencia, etiquetas y particiones."),
    "inteligencia-artificial": ("7057FF", "Modelos de IA, clasificación, evaluación y limitaciones."),
    "entrega": ("D4C5F9", "Empaquetado, presentación y entregables del proyecto."),
    "gestión-académica": ("FBCA04", "Coordinación académica, revisiones y requisitos docentes."),
    "pruebas": ("BFDADC", "Ensayos, regresión y validaciones reproducibles."),
    "visualización": ("C5DEF5", "Consola NOC, paneles, gráficos e interfaz de observación."),
    "accesibilidad": ("C5DEF5", "Accesibilidad de interfaces, navegación y usabilidad para diferentes capacidades."),
}
DEFINITIONS = {
    **{f"fase:{n:02d}": ("E4EAF1", f"Actividades correspondientes a la fase S{n:02d} de NETLAB360.")
       for n in range(1, 9)},
    **{f"tipo:{name}": values for name, values in TYPE_INFO.items()},
    "prioridad:alta": ("B60205", "Trabajo prioritario que condiciona un resultado central o la entrega."),
    "prioridad:media": ("FBCA04", "Trabajo relevante sin bloqueo crítico inmediato."),
    "alcance:opcional": ("D4C5F9", "Ampliación condicionada a requisitos o autorización; no acreditada como implementada."),
    "tipo:error": ("D73A4A", "Incidencia técnica reproducible que requiere corrección."),
    "tipo:mejora": ("A2EEEF", "Ampliación o perfeccionamiento de una funcionalidad existente."),
    "tipo:consulta": ("D4C5F9", "Consulta o cuestión técnica que requiere valoración."),
    "resolución:duplicada": ("CFD3D7", "Solicitud consolidada en otra issue sin ejecución duplicada."),
    "resolución:inválida": ("E4E669", "Solicitud no aplicable al alcance tras su revisión."),
    "resolución:no-planificada": ("FFFFFF", "Funcionalidad descartada de forma justificada por alcance."),
    "colaboración:primer-aporte": ("7057FF", "Actividad apropiada para una primera contribución."),
    "colaboración:ayuda-solicitada": ("008672", "Actividad en la que se solicita apoyo técnico."),
    "estado:bloqueado": ("B60205", "Actividad detenida por una dependencia documentada; no implica cierre."),
}
ALIASES = {
    **{f"semana:{n:02d}": f"fase:{n:02d}" for n in range(1, 9)},
    "tipo:infra": "tipo:infraestructura",
    "tipo:docs": "tipo:documentación",
    "tipo:dashboard": "tipo:visualización",
    "tipo:telemetria": "tipo:telemetría",
    "tipo:ia": "tipo:inteligencia-artificial",
    "tipo:automatizacion": "tipo:automatización",
    "bug": "tipo:error",
    "documentation": "tipo:documentación",
    "duplicate": "resolución:duplicada",
    "enhancement": "tipo:mejora",
    "good first issue": "colaboración:primer-aporte",
    "help wanted": "colaboración:ayuda-solicitada",
    "invalid": "resolución:inválida",
    "question": "tipo:consulta",
    "wontfix": "resolución:no-planificada",
    "accessibility": "tipo:accesibilidad",
}
OLD_OR_CANONICAL = frozenset(DEFINITIONS) | frozenset(ALIASES)
TITLE_PATTERN = re.compile(r"^\[S(\d{2})\] [^\n]{12,160}$")
UNWANTED_TITLE_STATUS = re.compile(
    r"(?:\s*[—–-]\s*)?(?:cerrad[oa]|pendiente|concluid[oa]|no implementad[oa]|"
    r"validad[oa]|reprogramad[oa]|completad[oa])\s*$", re.IGNORECASE
)
CHECKBOX_UNDONE = re.compile(r"(?m)^\s*-\s*\[ \]")


def validate_definitions() -> None:
    """Verificar los límites GitHub antes de cualquier mutación de etiquetas."""
    for name, (color, description) in DEFINITIONS.items():
        if not isinstance(description, str) or not description or len(description) > 100:
            raise ValueError(f"label_description_invalid_{name}")


def gh(path: str, method: str = "GET", obj: dict | None = None,
       paginated: bool = False):
    args = ["gh", "api", "--method", method, path]
    if paginated:
        args += ["--paginate", "--slurp"]
    if obj is not None:
        args += ["--input", "-"]
    result = subprocess.run(
        args, input=json.dumps(obj, ensure_ascii=False) if obj is not None else None,
        capture_output=True, text=True, check=False, timeout=120
    )
    if result.returncode:
        raise RuntimeError(f"GitHub API {method} {path}: {result.stderr.strip()[-500:]}")
    if not result.stdout.strip():
        return None
    return json.loads(result.stdout)


def paged(path: str) -> list[dict]:
    raw = gh(path, paginated=True)
    if not isinstance(raw, list):
        raise ValueError("pagination_not_list")
    if not raw:
        return []
    pages = raw if isinstance(raw[0], list) else [raw]
    if not all(isinstance(page, list) for page in pages):
        raise ValueError("pagination_page_invalid")
    return [item for page in pages for item in page]


def all_items() -> list[dict]:
    return paged(f"{ROOT}/issues?state=all&per_page=100")


def label_inventory() -> dict[str, dict]:
    values = paged(f"{ROOT}/labels?per_page=100")
    return {x["name"]: x for x in values}


def phase_for(number: int) -> int:
    phases = [phase for phase, ids in PHASES.items() if number in ids]
    if len(phases) != 1:
        raise ValueError(f"issue_{number}_phase_not_unique")
    return phases[0]


def theme_for(number: int) -> str:
    values = [name for name, ids in THEMES.items() if number in ids]
    if len(values) != 1:
        raise ValueError(f"issue_{number}_theme_not_unique")
    return values[0]


def labels_for(number: int) -> list[str]:
    out = [f"fase:{phase_for(number)}", f"tipo:{theme_for(number)}"]
    # El identificador de fase debe tener siempre 2 dígitos.
    out[0] = f"fase:{phase_for(number):02d}"
    if number in OPTIONAL:
        out.append("alcance:opcional")
    if number in URGENT:
        out.append("prioridad:alta")
    return out


def check_baseline(items: list[dict]) -> list[dict]:
    issues = [x for x in items if "pull_request" not in x]
    ids = {x["number"] for x in issues}
    if len(issues) != len(ids) or ids != ALL_IDS:
        raise ValueError(f"issue_inventory_changed expected={len(ALL_IDS)} "
                         f"actual={len(issues)} extra={sorted(ids-ALL_IDS)} "
                         f"missing={sorted(ALL_IDS-ids)}")
    for x in issues:
        n = x["number"]
        phase = phase_for(n)
        if (x.get("milestone") or {}).get("number") != phase:
            raise ValueError(f"issue_{n}_wrong_milestone")
        expected_state = "closed" if n in EXPECTED_CLOSED else "open"
        if x.get("state") != expected_state:
            raise ValueError(f"issue_{n}_unexpected_state")
        title = x.get("title", "")
        m = TITLE_PATTERN.fullmatch(title)
        if (not m or int(m.group(1)) != phase
                or UNWANTED_TITLE_STATUS.search(title)):
            raise ValueError(f"issue_{n}_nonuniform_title:{title}")
        undone = len(CHECKBOX_UNDONE.findall(x.get("body") or ""))
        if x.get("state") == "closed" and undone:
            raise ValueError(f"issue_{n}_closed_with_{undone}_unchecked")
        if x.get("state") == "open" and not undone:
            raise ValueError(f"issue_{n}_open_without_pending_criteria")
    return issues


def inspect(items: list[dict], labels: dict[str, dict]) -> dict:
    issues = check_baseline(items)
    unexpected = sorted(set(labels)-OLD_OR_CANONICAL)
    mismatch = []
    for x in issues:
        current = {r["name"] for r in x.get("labels", [])}
        planned = set(labels_for(x["number"]))
        if current != planned:
            mismatch.append(x["number"])
    incorrect_definitions = [
        name for name, (color, description) in DEFINITIONS.items()
        if name in labels and (labels[name].get("description") != description
                               or labels[name].get("color", "").upper() != color.upper())
    ]
    aliases_present = sorted(set(ALIASES) & set(labels))
    missing = sorted(set(x for issue in issues for x in labels_for(issue["number"]))
                     - set(labels))
    return {
        "issue_count": len(issues),
        "open_count": sum(x["state"] == "open" for x in issues),
        "closed_count": sum(x["state"] == "closed" for x in issues),
        "issue_label_mismatch": mismatch,
        "canonical_labels_missing": missing,
        "canonical_descriptions_outdated": incorrect_definitions,
        "legacy_labels": aliases_present,
        "unknown_labels": unexpected,
    }


def url_label(name: str) -> str:
    return f"{ROOT}/labels/{quote(name, safe='')}"


def migrate_definitions(items: list[dict], old_labels: dict[str, dict]) -> None:
    names = set(old_labels)
    # Primero renombrar las etiquetas existentes, conservando su uso en issues/PR.
    for old, new in ALIASES.items():
        if old not in names:
            continue
        if new in names:
            print(f"COLISION_ETIQUETA={old} -> {new} (se conciliará sin pérdida)")
            continue
        color, description = DEFINITIONS[new]
        gh(url_label(old), "PATCH",
           {"new_name": new, "color": color, "description": description})
        names.remove(old)
        names.add(new)
        print(f"ETIQUETA_RENOMBRADA={old} -> {new}")

    # La creación se limita a las etiquetas usadas o preservadas de las existentes.
    used = {label for n in ALL_IDS for label in labels_for(n)}
    desired = used | (names & set(DEFINITIONS))
    for label in sorted(desired):
        color, description = DEFINITIONS[label]
        if label not in names:
            gh(f"{ROOT}/labels", "POST",
               {"name": label, "color": color, "description": description})
            names.add(label)
            print(f"ETIQUETA_CREADA={label}")
        else:
            existing = gh(url_label(label))
            if (existing.get("color","").upper() != color.upper()
                    or existing.get("description") != description):
                gh(url_label(label), "PATCH",
                   {"color": color, "description": description})
                print(f"ETIQUETA_DESCRIPCION_ACTUALIZADA={label}")


def set_issue_assignments(issues: list[dict]) -> None:
    for issue in sorted(issues, key=lambda r: r["number"]):
        n = issue["number"]
        current = {label["name"] for label in issue.get("labels", [])}
        desired = labels_for(n)
        if current != set(desired):
            gh(f"{ROOT}/issues/{n}/labels", "PUT", {"labels": desired})
            print(f"ISSUE_#{n}_ETIQUETAS={','.join(desired)}")


def remove_aliases_safely(items: list[dict]) -> None:
    labels = label_inventory()
    for old, new in ALIASES.items():
        if old not in labels:
            continue
        if new not in labels:
            raise RuntimeError(f"alias_without_target_{old}")
        # Si una PR conserva la antigua etiqueta, transferir la referencia sin
        # alterar el resto de sus etiquetas. Las issues reales ya tienen su set.
        for item in all_items():
            names = [lab["name"] for lab in item.get("labels", [])]
            if old not in names:
                continue
            if "pull_request" not in item:
                raise RuntimeError(f"issue_{item['number']}_old_label_remaining")
            new_names = list(dict.fromkeys([new if x == old else x for x in names]))
            gh(f"{ROOT}/issues/{item['number']}/labels", "PUT",
               {"labels": new_names})
            print(f"PR_#{item['number']}_ETIQUETA_TRANSFERIDA={old} -> {new}")
        if any(old in {lab["name"] for lab in item.get("labels", [])}
               for item in all_items()):
            raise RuntimeError(f"legacy_label_{old}_still_used")
        gh(url_label(old), "DELETE")
        print(f"ETIQUETA_OBSOLETA_ELIMINADA={old}")


def run(apply: bool) -> None:
    validate_definitions()
    if len(ALL_IDS) != 53 or sum(len(x) for x in PHASES.values()) != 53:
        raise ValueError("phase_inventory_size_invalid")
    issues = check_baseline(all_items())
    before = inspect(all_items(), label_inventory())
    print("========== NETLAB360 ISSUES Y ETIQUETAS ==========")
    print(f"ISSUES_REALES={before['issue_count']} ABIERTAS={before['open_count']} CERRADAS={before['closed_count']}")
    print("TITULOS_UNIFORMES=53_DE_53")
    print("CERRADAS_CON_CASILLAS_PENDIENTES=0")
    for key in ("issue_label_mismatch", "canonical_labels_missing",
                "canonical_descriptions_outdated", "legacy_labels", "unknown_labels"):
        print(f"DIAGNOSTICO_{key.upper()}={before[key]}")
    if not apply:
        print("MODO=SOLO_LECTURA")
        return
    if before["unknown_labels"]:
        raise ValueError("etiquetas_desconocidas_revisar_antes: "+
                         repr(before["unknown_labels"]))
    migrate_definitions(all_items(), label_inventory())
    set_issue_assignments(issues)
    remove_aliases_safely(all_items())
    after = inspect(all_items(), label_inventory())
    if any(after[k] for k in (
            "issue_label_mismatch","canonical_labels_missing",
            "canonical_descriptions_outdated","legacy_labels","unknown_labels")):
        raise RuntimeError("normalization_not_converged: "+repr(after))
    if after["issue_count"] != 53 or after["closed_count"] != before["closed_count"]:
        raise RuntimeError("issue_states_changed")
    print("TITULOS=53_UNIFORMES")
    print("ETIQUETAS_ISSUES=ASIGNADAS_POR_ALCANCE")
    print("ETIQUETAS_REPOSITORIO=TODAS_EN_ESPANOL_CON_DESCRIPCION")
    print("ESTADOS_Y_CHECKBOX=CONSERVADOS")
    print("MILESTONES=CONSERVADAS")
    print("S05_ISSUES=6_CERRADAS")
    print("========== NORMALIZACION_ISSUES_COMPLETA=OK ==========")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        run(args.apply)
    except (RuntimeError, ValueError, KeyError, TypeError, OSError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print("NORMALIZACION_ERROR="+type(exc).__name__+": "+str(exc),
              file=sys.stderr)
        sys.exit(1)
