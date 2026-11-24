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


def audit(prs):
    """Comprobar todos los registros, no solo los PR abiertos."""
    if not isinstance(prs, list) or not prs:
        raise ValueError("Inventario de PR ausente")
    seen = set()
    defects = []
    for pr in prs:
        number = pr["number"]
        if number in seen:
            raise ValueError("PR duplicado")
        seen.add(number)
        reasons = []
        labels = {x["name"] for x in pr.get("labels", [])}
        milestone = pr.get("milestone") or {}
        phase = milestone.get("title", "")
        if not TITLE.fullmatch(pr.get("title", "")):
            reasons.append("TITULO")
        if not re.fullmatch(r"S0[1-8]", phase):
            reasons.append("MILESTONE")
        elif "fase:" + phase[1:] not in labels:
            reasons.append("ETIQUETA_FASE")
        if not any(TOPIC.fullmatch(label) for label in labels):
            reasons.append("ETIQUETA_TEMATICA")
        if not any(x.get("login") for x in pr.get("assignees", [])):
            reasons.append("ASSIGNEE")
        if reasons:
            defects.append({"number": number, "reasons": reasons})
    return {"total": len(prs), "states": dict(Counter(p.get("state") for p in prs)),
            "defects": defects}


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
