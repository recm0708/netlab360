#!/usr/bin/env python3
"""Reconstruir tareas históricas a partir del registro de fusión y sus archivos."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import re
import subprocess

REPO = "recm0708/netlab360"
MARKER = "## Tareas históricas de integración"
TASK = re.compile(r"^\s*[-*+]\s+\[[ xX]\]\s+", re.MULTILINE)
UNCHECKED = re.compile(r"^\s*[-*+]\s+\[ \]\s+", re.MULTILINE)


def gh(*args):
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, timeout=120, check=True
    )
    return json.loads(result.stdout)


def group(path):
    if path.startswith("tests/"):
        return "Pruebas versionadas"
    if path.startswith(".github/"):
        return "Configuración y gestión de GitHub"
    if path.startswith("evidencias/"):
        return "Evidencias y manifiestos"
    if path.startswith("docs/") or path.lower().endswith((".md", ".rst")):
        return "Documentación"
    if path.startswith(("scripts/", "operacion/")):
        return "Scripts y operación"
    if path.startswith("servicios/"):
        return "Servicios y aplicación"
    return "Otros recursos versionados"


def historical_body(pr, files):
    original = pr.get("body") or ""
    if TASK.search(original) or MARKER in original:
        return None
    if pr["state"] != "MERGED" or not pr.get("mergedAt"):
        return None
    if len(files) != pr["changedFiles"] or not files:
        raise ValueError("Inventario de archivos incompleto")
    groups = defaultdict(list)
    for row in files:
        groups[group(row["filename"])].append(row)
    tasks = []
    for name, rows in sorted(groups.items()):
        counts = Counter(row["status"] for row in rows)
        detail = ", ".join(f"{key}: {value}" for key, value in sorted(counts.items()))
        tasks.append(f"- [x] Integrar los cambios de {name.lower()} ({len(rows)} archivos; {detail}).")
        for row in sorted(rows, key=lambda x: x["filename"])[:4]:
            path = row["filename"].replace("\x60", "'").replace("\n", " ")
            tasks.append(f"  - \x60{path}\x60")
        if len(rows) > 4:
            tasks.append("  - Resto de archivos: pestaña Files changed.")
    tasks.append(f"- [x] Integrar el PR en \x60{pr['baseRefName']}\x60 según su registro de fusión.")
    section = (
        "\n\n" + MARKER + "\n\n"
        "Conciliación retrospectiva del alcance integrado, basada en el registro de GitHub y los archivos del PR.\n\n"
        + "\n".join(tasks)
        + "\n\nEstas casillas acreditan integración histórica, no una nueva ejecución de CI, pruebas locales, "
        "revisión de seguridad o aceptación operacional. Las evidencias originales y limitaciones de la descripción "
        "se conservan. Las tareas nuevas se exigen antes de fusionar los PR posteriores.\n"
    )
    result = original + section
    if len(result.encode("utf-8")) > 65000:
        raise ValueError("Descripción demasiado extensa")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    prs = gh("pr", "list", "--repo", REPO, "--state", "all", "--limit", "1000",
             "--json", "number,title,body,state,mergedAt,baseRefName,headRefOid,changedFiles")
    assert len(prs) < 1000, "Inventario posiblemente truncado"
    stats = Counter()
    for pr in sorted(prs, key=lambda p: p["number"]):
        number = pr["number"]
        try:
            if TASK.search(pr.get("body") or ""):
                stats["existing"] += 1
                if UNCHECKED.search(pr.get("body") or ""):
                    print(f"PR_{number}=CASILLAS_PENDIENTES_CONSERVADAS", flush=True)
                continue
            if pr["state"] != "MERGED":
                stats["not_merged"] += 1
                continue
            pages = gh("api", "--paginate", "--slurp",
                       f"repos/{REPO}/pulls/{number}/files?per_page=100")
            files = [row for page in pages for row in page]
            body = historical_body(pr, files)
            if body is None:
                stats["existing"] += 1
                continue
            stats["eligible"] += 1
            if args.apply:
                current = gh("pr", "view", str(number), "--repo", REPO,
                             "--json", "body,state,mergedAt,headRefOid")
                if any(current[key] != pr[key] for key in ("body", "state", "mergedAt", "headRefOid")):
                    raise ValueError("El PR cambió durante la auditoría")
                updated = gh("api", "--method", "PATCH", f"repos/{REPO}/pulls/{number}",
                             "-f", "body=" + body)
                if updated.get("body") != body:
                    raise ValueError("No se confirmó la descripción actualizada")
                stats["updated"] += 1
            print(f"PR_{number}={'ACTUALIZADO' if args.apply else 'PLAN'} ARCHIVOS={len(files)}", flush=True)
        except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
            stats["errors"] += 1
            print(f"PR_{number}=REVISAR {type(exc).__name__}", flush=True)
    print(f"PRS_TOTALES={len(prs)}")
    for key in ("existing", "not_merged", "eligible", "updated", "errors"):
        print(f"{key.upper()}={stats[key]}")
    if stats["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
