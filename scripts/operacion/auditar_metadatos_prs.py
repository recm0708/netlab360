#!/usr/bin/env python3
"""Audita la clasificación y asignación de PR sin modificar GitHub."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import subprocess
import sys

REPO = "recm0708/netlab360"
TITLE = re.compile(r"^\[(S0[1-8]|GESTIÓN)\] .{12,}$")
TOPIC = re.compile(r"^tipo:.+$")
PHASE_LABEL = re.compile(r"^fase:0[1-8]$")


def audit(prs):
    """Comprobar todos los registros, no solo los PR abiertos."""
    if not isinstance(prs, list) or not prs:
        raise ValueError("Inventario de PR ausente")
    seen = set()
    defects = []
    without_milestone = []
    review_milestone = []
    for pr in prs:
        number = pr["number"]
        if number in seen:
            raise ValueError("PR duplicado")
        seen.add(number)
        reasons = []
        labels = {x["name"] for x in pr.get("labels", [])}
        milestone = pr.get("milestone") or {}
        phase = milestone.get("title", "")
        title = TITLE.fullmatch(pr.get("title", ""))
        phase_labels = {label for label in labels if PHASE_LABEL.fullmatch(label)}
        if not title:
            reasons.append("TITULO")
        elif title.group(1) != "GESTIÓN" and "fase:" + title.group(1)[1:] not in phase_labels:
            reasons.append("ETIQUETA_FASE_TITULO")
        if any(label.startswith("fase:") and label not in phase_labels for label in labels):
            reasons.append("ETIQUETA_FASE_INVALIDA")
        # El hito es condicional; su pertinencia semántica requiere revisión humana.
        if not milestone:
            without_milestone.append(number)
        elif not re.fullmatch(r"S0[1-8]", phase):
            reasons.append("MILESTONE_INVALIDO")
        elif "fase:" + phase[1:] not in phase_labels:
            reasons.append("ETIQUETA_FASE_MILESTONE")
        elif len(phase_labels) > 1 or (title and title.group(1) == "GESTIÓN"):
            review_milestone.append(number)
        if not any(TOPIC.fullmatch(label) for label in labels):
            reasons.append("ETIQUETA_TEMATICA")
        if not any(x.get("login") for x in pr.get("assignees", [])):
            reasons.append("ASSIGNEE")
        if reasons:
            defects.append({"number": number, "reasons": reasons})
    return {"total": len(prs), "states": dict(Counter(p.get("state") for p in prs)),
            "defects": defects, "without_milestone": without_milestone,
            "review_milestone": review_milestone}


def fetch():
    """Recuperar todas las páginas REST con la sesión gh del operador."""
    result = subprocess.run(
        ["gh", "api", "--paginate", "--slurp",
         f"repos/{REPO}/pulls?state=all&per_page=100"],
        check=True, capture_output=True, text=True, timeout=120,
    )
    pages = json.loads(result.stdout)
    if not isinstance(pages, list) or not all(isinstance(page, list) for page in pages):
        raise ValueError("Respuesta de paginación inválida")
    return [pr for page in pages for pr in page]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    args = parser.parse_args()
    report = audit(fetch())
    print("PRS_TOTALES=" + str(report["total"]))
    print("PRS_SIN_METADATOS=" + str(len(report["defects"])))
    print("PRS_SIN_MILESTONE=" + str(len(report["without_milestone"])))
    print("PRS_MILESTONE_REVISION_SEMANTICA=" + str(len(report["review_milestone"])))
    for number in report["review_milestone"]:
        print(f"PR_{number}=REVISAR_PERTINENCIA_MILESTONE")
    for defect in report["defects"]:
        print(f"PR_{defect['number']}=" + ",".join(defect["reasons"]))
    print("METADATOS_PR=" + ("OK" if not report["defects"] else "REVISAR"))
    return int(bool(report["defects"]))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print("AUDITORIA_PR_ERROR=" + str(exc), file=sys.stderr)
        sys.exit(1)
