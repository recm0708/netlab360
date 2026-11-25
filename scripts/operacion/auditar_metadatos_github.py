#!/usr/bin/env python3
"""Auditar metadatos de todos los PR e issues y proponer correcciones faltantes."""
import argparse
from collections import Counter
import json
import re
import subprocess

ROOT = "repos/recm0708/netlab360"
OWNER = "recm0708"
VERSION = "2026-03-10"
# Funcionalidades nuevas inequívocas; las tareas de validación y gestión son Task.
FEATURES = {7, 8, 17, 24, 64, 198, 190, 191, 192, 193, 194, 204, 205,
            206, 207, 208, 209, 210, 212, 213, 214, 215, 216, 217, 242, 243}


def api(path, *, payload=None, paginated=False):
    """Usar credenciales de gh sin imprimirlas ni modificar su configuración."""
    cmd = ["gh", "api", "-H", "X-GitHub-Api-Version: " + VERSION, path]
    if paginated:
        cmd += ["--paginate", "--slurp"]
    if payload is not None:
        cmd += ["--method", "PATCH", "--input", "-"]
    result = subprocess.run(cmd, input=None if payload is None else json.dumps(payload),
                            text=True, capture_output=True, timeout=120, check=True)
    data = json.loads(result.stdout)
    if paginated:
        return [row for page in data for row in page]
    return data


def plan(item, types, milestones):
    """Conservar metadatos existentes y separar decisiones ambiguas de las seguras."""
    changes = {}
    review = []
    labels = {x["name"] for x in item.get("labels", [])}
    pr = "pull_request" in item
    number = item["number"]
    match = re.match(r"^\[S(\d{2})\]", item["title"])
    if not item.get("assignees"):
        changes["assignees"] = [OWNER]
    if not labels:
        review.append("LABELS_AUSENTES")
    elif not any(x.startswith("tipo:") for x in labels):
        review.append("LABEL_TECNICA_AUSENTE")
    if not item.get("milestone"):
        if not pr and match and int(match[1]) in milestones:
            changes["milestone"] = int(match[1])
        elif not pr:
            review.append("MILESTONE_ISSUE_AUSENTE")
        elif not item["title"].startswith("[GESTIÓN]"):
            review.append("MILESTONE_PR_REVISAR_ALCANCE")
    if not pr and not item.get("type"):
        key = "bug" if "tipo:error" in labels else "feature" if number in FEATURES else "task"
        if key in types:
            changes["type"] = types[key]
        else:
            review.append("TYPE_NO_DISPONIBLE_" + key.upper())
    return changes, review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    assert api("user")["login"] == OWNER
    items = api(ROOT + "/issues?state=all&per_page=100", paginated=True)
    assert len({x["number"] for x in items}) == len(items)
    milestones = {x["number"] for x in api(ROOT + "/milestones?state=all&per_page=100", paginated=True)}
    types = {}
    try:
        for x in api(ROOT + "/issue-types"):
            if x.get("is_enabled", True):
                types[x["name"].casefold()] = x["name"]
    except subprocess.CalledProcessError:
        print("TYPE_API=NO_DISPONIBLE_O_SIN_PERMISOS")
    print("TYPES_DISPONIBLES=" + ",".join(sorted(types.values())))
    totals = Counter()
    for item in sorted(items, key=lambda x: x["number"]):
        number = item["number"]
        kind = "PR" if "pull_request" in item else "ISSUE"
        totals[kind] += 1
        changes, review = plan(item, types, milestones)
        if not item.get("labels"):
            totals[kind + "_SIN_LABELS"] += 1
        if not item.get("assignees"):
            totals[kind + "_SIN_ASSIGNEES"] += 1
        if not item.get("milestone"):
            totals[kind + "_SIN_MILESTONE"] += 1
        if kind == "ISSUE" and not item.get("type"):
            totals["ISSUE_SIN_TYPE"] += 1
        if review or changes:
            print(json.dumps({"kind": kind, "number": number, "title": item["title"],
                              "changes": changes, "review": review}, ensure_ascii=False), flush=True)
        if args.apply and changes:
            current = api(ROOT + "/issues/" + str(number))
            # No sobrescribir metadatos modificados después del inventario.
            fresh, _ = plan(current, types, milestones)
            if fresh != changes:
                raise RuntimeError("Metadatos modificados durante la auditoría: " + str(number))
            result = api(ROOT + "/issues/" + str(number), payload=changes)
            for key, value in changes.items():
                actual = result.get(key)
                if key == "assignees":
                    actual = [x["login"] for x in actual]
                elif key == "milestone":
                    actual = (actual or {}).get("number")
                elif key == "type":
                    actual = (actual or {}).get("name") if isinstance(actual, dict) else actual
                if actual != value:
                    raise RuntimeError("Cambio no confirmado: " + str(number) + " " + key)
            totals["ACTUALIZADOS"] += 1
    for key in ("PR", "ISSUE", "PR_SIN_LABELS", "PR_SIN_ASSIGNEES", "PR_SIN_MILESTONE",
                "ISSUE_SIN_LABELS", "ISSUE_SIN_ASSIGNEES", "ISSUE_SIN_MILESTONE",
                "ISSUE_SIN_TYPE", "ACTUALIZADOS"):
        print(f"{key}={totals[key]}")
    print("AUDITORIA_METADATOS=OK")


if __name__ == "__main__":
    main()
