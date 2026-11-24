#!/usr/bin/env python3
"""Auditoría de nombres, documentos y dependencias, sin modificar el repositorio."""
from __future__ import annotations
import argparse
import collections
import posixpath
from pathlib import Path, PurePosixPath
import re
import subprocess
import unicodedata
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
DOC_NAMES = {
    "ADR-001-vmware-vm-sin-iso.md": "adr-001-entorno-virtualizacion.md",
    "ADR-002-ip-fija-vmnet8.md": "adr-002-direccion-administrativa.md",
    "ADR-003-redes-virtuales-aisladas.md": "adr-003-aislamiento-redes.md",
    "S03_09_GitOps_CI_Regresion_PullRequest.md": "s03-gitops-ci-regresion.md",
    "ACTA-ACEPTACION-TECNICA-S05-20261115.md": "s05-acta-aceptacion-tecnica.md",
    "01-inventario-host-y-vmware.md": "inventario-host-y-vmware.md",
    "02-ubuntu-desktop-instalacion-ssh.md": "ubuntu-desktop-y-ssh.md",
    "s01-s08-hitos-descripciones-y-contador-s05.md": "gestion-milestones-s01-s08.md",
    "normalizacion-issues-y-etiquetas-es.md": "convenciones-issues-etiquetas.md",
    "s05-ovs-faucet-vs-bridge-frr-y-limpieza-segura.md": "s05-dominio-sdn-ovs-faucet.md",
    "s06-estudio-prospectivo-uniforme-y-cierre-consolidado.md": "s06-protocolo-uniforme-v2.md",
    "s07-plan-intervencion-y-watchdog.md": "s07-intervencion-ospf-y-watchdog.md",
    "s07-ensayos-servicios.md": "s07-ensayos-operacionales.md",
}
TEST_NAMES = {
    "test_b3_live_exporter.py": "test_s01_b3_live_exporter.py",
    "test_b4_diagnostico_reglas.py": "test_s01_diagnostico_reglas.py",
    "test_b4_fuentes_reales.py": "test_s01_fuentes_reales.py",
    "test_b4_perfil_estadistico.py": "test_s01_perfil_estadistico.py",
    "test_iac_frr.py": "test_s01_iac_frr.py",
    "test_auditar_titulos_prs.py": "test_transversal_titulos_prs.py",
    "test_capturas_por_fase.py": "test_transversal_capturas.py",
    "test_documentacion_proyecto.py": "test_transversal_documentacion.py",
    "test_normalizar_issues_etiquetas.py": "test_transversal_issues_etiquetas.py",
    "test_reconciliar_milestones_netlab360.py": "test_transversal_milestones.py",
}
REVIEW = re.compile(
    r"(?i)\b(?:chat|reanudaci[oó]n|reanud[ae]r|pr[oó]ximo\s+(?:bloque|gate|incremento)"
    r"|siguiente\s+(?:bloque|paso|incremento)|progreso\s+s0[1-8]|avance\s+funcional\s+estimado"
    r"|no\s+cerrar|pendiente(?:s)?\s+(?:de\s+)?(?:captura|aceptaci[oó]n|validaci[oó]n)"
    r"|captura.{0,80}pendiente|no\s+se\s+(?:ha\s+)?versionad[oa])\b"
)
MD_LINK = re.compile(r"!?\[[^\]\n]+\]\(([^)\n]+)\)")

def proposed_name(path):
    p = PurePosixPath(path)
    n = p.name
    if p.suffix == ".md":
        if n in DOC_NAMES:
            return str(p.with_name(DOC_NAMES[n]))
        if re.match(r"s06-\d+[a-z]?-", n):
            return str(p.with_name(re.sub(r"^s06-\d+[a-z]?-", "s06-", n)))
    if p.parent == PurePosixPath("tests") and n in TEST_NAMES:
        return str(p.with_name(TEST_NAMES[n]))
    if p.suffix == ".py" and "-" in p.stem:
        return str(p.with_name(p.stem.replace("-", "_") + ".py"))
    return path

def markdown_lines(content):
    fence = None
    for i, line in enumerate(content.splitlines(), 1):
        match = re.match(r"^\s*([\x60~]{3,})", line)
        if match:
            mark = match.group(1)
            if fence is None:
                fence = mark[0]
            elif mark[0] == fence:
                fence = None
            continue
        if fence is None:
            yield i, line

def anchors(content):
    result = set()
    counts = collections.Counter()
    for _, line in markdown_lines(content):
        h = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not h:
            continue
        value = h.group(1).lower()
        slug = "".join(ch for ch in value if ch in "_- " or unicodedata.category(ch)[0] in "LN")
        slug = slug.replace(" ", "-")
        n = counts[slug]
        counts[slug] += 1
        result.add(slug if n == 0 else f"{slug}-{n}")
    return result

# Las rutas fijadas a una revisión histórica no se resuelven contra los archivos vigentes de main.
def resolve_link(source, link):
    raw = unquote(link.strip())
    for base in ("https://github.com/recm0708/netlab360/blob/main/",
                 "https://github.com/recm0708/netlab360/tree/main/"):
        if raw.startswith(base):
            target, _, anchor = raw[len(base):].partition("#")
            return posixpath.normpath(target), anchor
    if "://" in raw or raw.startswith(("mailto:", "data:")):
        return None
    target, _, anchor = raw.partition("#")
    if not target:
        return source, anchor
    if target.startswith("/"):
        return None
    return posixpath.normpath(posixpath.join(posixpath.dirname(source), target)), anchor

# Inventariamos las rutas versionadas antes de verificar enlaces y consumidores de nombres.
def audit(root):
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    paths = sorted(p for p in paths if p)
    tracked = set(paths)
    texts = {}
    output = []
    add = output.append
    add("========== INVENTARIO VERSIONADO ==========")
    add("HEAD=" + subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip())
    counts = collections.Counter()
    folds = collections.defaultdict(list)
    for p in paths:
        f = root / p
        counts[PurePosixPath(p).suffix or "(sin extensión)"] += 1
        folds[p.casefold()].append(p)
        if not f.is_file() or f.is_symlink():
            add("ARCHIVO_ESPECIAL=" + p)
            continue
        if f.suffix.lower() == ".png":
            continue
        try:
            texts[p] = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            add("NO_TEXTO_UTF8=" + p)
    add("ARCHIVOS_VERSIONADOS=" + str(len(paths)))
    for k, v in sorted(counts.items()):
        add(f"EXTENSION {k} = {v}")
    for variants in folds.values():
        if len(variants) > 1:
            add("COLISION_CASEFOLD=" + " | ".join(variants))
    add("\n========== INVENTARIO COMPLETO ==========")
    for p in paths:
        add(p)
    docs = {p:s for p,s in texts.items() if p.endswith(".md")}
    add("\n========== DOCUMENTOS Y CONTENIDO A REVISAR ==========")
    duplicates = collections.defaultdict(set)
    for p, s in docs.items():
        lines = list(markdown_lines(s))
        headings = [(i,l) for i,l in lines if re.match(r"^#{1,6}\s",l)]
        add(f"\n--- {p} ({len(s.splitlines())} líneas) ---")
        if sum(bool(re.match(r"^#\s+\S", l)) for _, l in lines) != 1:
            add("TITULO_H1_REVISAR")
        for i,l in headings:
            add(f"H {i}: {l}")
        for i,l in lines:
            if REVIEW.search(l):
                add(f"REVISAR {i}: {l[:420]}")
        for block in re.split(r"\n\s*\n", s):
            normalized = " ".join(block.split())
            if len(normalized) >= 160 and not normalized.startswith(("#", "|", chr(96)*3)):
                duplicates[normalized].add(p)
    add("\n========== PARRAFOS IDENTICOS ENTRE DOCUMENTOS ==========")
    for block, refs in duplicates.items():
        if len(refs)>1:
            add(" | ".join(sorted(refs))+" :: "+block[:220])
    add("\n========== ENLACES Y ANCLAS A REVISAR ==========")
    errors=0
    for p,s in docs.items():
        for i,l in markdown_lines(s):
            for m in MD_LINK.finditer(l):
                resolved=resolve_link(p,m.group(1))
                if resolved is None:
                    continue
                target,anchor=resolved
                if target not in tracked and not any(x.startswith(target.rstrip("/")+"/") for x in paths):
                    errors+=1
                    add(f"RUTA {p}:{i} -> {m.group(1)}")
                elif anchor and target in docs and anchor not in anchors(docs[target]):
                    if f'id="{anchor}"' not in docs[target] and f'name="{anchor}"' not in docs[target]:
                        errors+=1
                        add(f"ANCLA {p}:{i} -> {m.group(1)}")
    add("REFERENCIAS_A_REVISAR="+str(errors))
    add("\n========== PROPUESTAS DE RENOMBRADO Y CONSUMIDORES ==========")
    candidates={p:proposed_name(p) for p in paths if proposed_name(p)!=p}
    final=[candidates.get(p,p).casefold() for p in paths]
    if len(final)!=len(set(final)):
        add("COLISION_PROPUESTAS=REVISAR")
    split={p:s.splitlines() for p,s in texts.items()}
    for old,new in candidates.items():
        add(f"\nRENOMBRE {old} -> {new}")
        name=PurePosixPath(old).name
        patterns={old,name}
        if PurePosixPath(old).suffix==".py":
            patterns.add(PurePosixPath(old).stem)
        count=0
        for p,lines in split.items():
            if p==old:
                continue
            for i,l in enumerate(lines,1):
                if any(x in l for x in patterns):
                    add(f"REF {p}:{i}: {l.strip()[:320]}")
                    count+=1
        add(f"REFERENCIAS_TEXTUALES={count}")
    add("PROPUESTAS="+str(len(candidates)))
    add("\n========== REFERENCIAS DINAMICAS DE RUTAS ==========")
    dynamic=re.compile(r"(?:glob\(|rglob\(|listdir\(|importlib\.|spec_from_file_location|find .*-(?:name|path)|unittest discover|pytest |ExecStart=|ReadWritePaths=|WorkingDirectory=)")
    for p,lines in split.items():
        if not p.endswith((".py",".sh",".yml",".yaml",".service",".json",".tf")):
            continue
        for i,l in enumerate(lines,1):
            if dynamic.search(l):
                add(f"DINAMICA {p}:{i}: {l.strip()[:240]}")
    add("\n========== DOCUMENTACION COMPLETA ==========")
    for p,s in docs.items():
        add(f"\n========== DOCUMENTO {p} ==========\n{s}")
    add("\nAUDITORIA_SOLO_LECTURA=OK")
    return "\n".join(output)+"\n"

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    dest=a.output.expanduser().resolve()
    if dest==ROOT or ROOT in dest.parents:
        p.error("El informe debe guardarse fuera del repositorio")
    if not dest.parent.is_dir():
        p.error("El directorio de salida debe existir")
    with dest.open("x",encoding="utf-8") as f:
        f.write(audit(ROOT))
    print("INFORME="+str(dest))
    print("AUDITORIA_SOLO_LECTURA=OK")

if __name__=="__main__":
    main()
