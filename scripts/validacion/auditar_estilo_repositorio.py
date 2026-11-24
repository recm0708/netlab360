#!/usr/bin/env python3
"""Inventario editorial de solo lectura: comentarios útiles, docstrings y títulos por ruta."""
import argparse
import ast
from collections import Counter
import io
from pathlib import Path
import re
import subprocess
import tokenize

ROOT = Path(__file__).resolve().parents[2]
EXTENSIONS = {".py", ".sh", ".yml", ".yaml", ".tf", ".service", ".conf", ".j2", ".html"}
SPECIAL = {".gitignore", ".gitattributes", ".editorconfig"}
GENERIC = re.compile(r"recursos propios del módulo, sin alterar la red administrativa|ejecutar únicamente los recursos del componente correspondiente|configuración del componente correspondiente; conservar los recursos ajenos", re.I)
EDITORIAL = re.compile(r"\b(?:en (?:este|otro|el) chat|continuidad en otro chat|la petición actual|el usuario ejecutó)\b", re.I)


def useful(value):
    value = value.strip().lstrip("#!/ *-").strip()
    return len(value) >= 12 and not value.startswith(("SPDX-", "Copyright", "coding:")) and not GENERIC.search(value)


def classify(path, source):
    """Distinguir contratos y comentarios de datos; las alertas requieren revisión humana."""
    flags = []
    if path.suffix == ".md":
        from auditar_repositorio import markdown_lines
        titles = [line[2:].strip() for _, line in markdown_lines(source) if line.startswith("# ")]
        if len(titles) != 1:
            flags.append("H1")
        if EDITORIAL.search(source):
            flags.append("VOZ_EDITORIAL")
        return ("README" if path.name == "README.md" else "DOCUMENTO",
                titles[0] if titles else "", flags)
    if path.suffix not in EXTENSIONS and path.name not in SPECIAL:
        return "EXCLUIDO", "", flags
    if path.suffix == ".py":
        tree = ast.parse(source)
        doc = ast.get_docstring(tree) or ""
        nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        comments = [t for t in tokenize.generate_tokens(io.StringIO(source).readline)
                    if t.type == tokenize.COMMENT and useful(t.string)]
        purpose = doc.splitlines()[0] if doc else (comments[0].string if comments else "")
        internal = sum(t.start[0] > (tree.body[0].end_lineno if tree.body else 1) for t in comments)
        if (not str(path).startswith("tests/") and len(source.splitlines()) >= 100
                and len(nodes) >= 4 and not internal and not any(ast.get_docstring(n) for n in nodes)):
            flags.append("BLOQUES_A_REVISAR")
    else:
        comments = re.findall(r"(?m)^\s*(?:#|!|//|<!--|/\*|\{#)([^\n]*)", source)
        purpose = next((x.strip() for x in comments if useful(x)), "")
    if not purpose:
        flags.append("PROPOSITO_A_REVISAR")
    if GENERIC.search(source):
        flags.append("COMENTARIO_GENERICO")
    return "CODIGO_CONFIGURACION", purpose, flags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    rows, candidates = [], []
    counts = Counter()
    for name in sorted(filter(None, paths)):
        path = Path(name)
        readable = path.suffix in EXTENSIONS | {".md"} or path.name in SPECIAL
        if readable:
            kind, purpose, flags = classify(path, (ROOT / path).read_text(encoding="utf-8"))
        else:
            kind, purpose, flags = "EXCLUIDO", "", []
        counts[kind] += 1
        rows.append(f"{name} | {kind} | {purpose} | {','.join(flags) or 'SIN_ALERTA'}")
        if flags:
            candidates.append(f"REVISAR {name} | {','.join(flags)}")
    summary = ["ARCHIVOS_AUDITADOS=" + str(len(rows))]
    summary += [f"{k}={v}" for k, v in sorted(counts.items())]
    summary += ["CANDIDATOS_REVISION=" + str(len(candidates)), *candidates,
                "AUDITORIA_ESTILO_SOLO_LECTURA=OK"]
    print("\n".join(summary))
    if args.output:
        output = args.output.resolve()
        if output == ROOT or ROOT in output.parents:
            raise ValueError("Guardar el informe fuera de Git")
        output.write_text("\n".join(summary + ["", *rows]) + "\n", encoding="utf-8")
        print("INFORME=" + str(output))


if __name__ == "__main__":
    main()
