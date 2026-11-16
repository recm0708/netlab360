#!/usr/bin/env bash
# Importación verificable de 21 imágenes auténticas en rama aislada.
set -Eeuo pipefail
umask 077
if (( $# != 1 )); then
  echo 'Uso: importar-capturas-validadas-20261025.sh RUTA_ZIP'
  exit 2
fi
ROOT="$HOME/proyectos/netlab360"
PLAN="evidencias/manifiestos/PLAN_CARGA_CAPTURAS_2026-10-25.csv"
LOTE="evidencias/manifiestos/MANIFIESTO_SHA256_CAPTURAS_2026-10-25.csv"
BRANCH="upload/capturas-fases-20261025"
INBOX="$1"
cd "$ROOT"
test "$(git branch --show-current)" = main
test -z "$(git status --porcelain)"
test -f "$PLAN"
test -f "$INBOX"
test ! -L "$INBOX"
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo 'CARGA_DETENIDA=RAMA_LOCAL_EXISTENTE'; exit 3
fi
if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  echo 'CARGA_DETENIDA=RAMA_REMOTA_EXISTENTE'; exit 3
fi
echo '========== AUDITORIA PREVIA 21 PNG =========='
date -Is
git log -1 --oneline
python3 - "$ROOT" "$INBOX" "$PLAN" <<'PY'
import csv, hashlib, pathlib, sys, zipfile
root, packed, plan = map(pathlib.Path, sys.argv[1:])
with (root / plan).open(encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 21
expected = {r['ruta_actual']: r for r in rows}
assert len(expected) == 21
with zipfile.ZipFile(packed) as z:
    infos = z.infolist()
    names = [x.filename for x in infos]
    assert len(names) == 21 and set(names) == set(expected), 'Lote distinto del autorizado'
    total = 0
    for info in infos:
        assert not info.is_dir()
        assert ((info.external_attr >> 16) & 0o170000) != 0o120000, 'Enlace ZIP no permitido'
        rel = pathlib.PurePosixPath(info.filename)
        assert not rel.is_absolute() and '..' not in rel.parts
        assert len(rel.parts) == 4 and rel.parts[:2] == ('evidencias','capturas')
        assert rel.parts[2] in ('fase1', 'fase2', 'fase3')
        phase = int(rel.parts[2][-1])
        assert rel.name.startswith(f'S{phase:02d}_') and rel.suffix.lower() == '.png'
        assert not (root / pathlib.Path(*rel.parts)).exists(), 'Archivo ya existente'
        data = z.read(info)
        assert data.startswith(b'\x89PNG\r\n\x1a\n')
        assert len(data) == int(expected[info.filename]['bytes'])
        assert hashlib.sha256(data).hexdigest() == expected[info.filename]['sha256']
        total += len(data)
assert total < 5_000_000
print(f'IMAGENES_AUDITADAS={len(rows)}/21')
print(f'BYTES_VERIFICADOS={total}')
print('SHA256_ORIGINALES=OK')
PY
git switch -c "$BRANCH" origin/main
python3 - "$ROOT" "$INBOX" "$PLAN" "$LOTE" <<'PY'
import csv, hashlib, pathlib, sys, zipfile
root, packed, plan, dest = sys.argv[1:]
root = pathlib.Path(root)
with (root / plan).open(encoding='utf-8', newline='') as f:
    rows = list(csv.DictReader(f))
with zipfile.ZipFile(packed) as z:
    for row in rows:
        target = root / row['ruta_actual']
        assert not target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(z.read(row['ruta_actual']))
        b = target.read_bytes()
        assert hashlib.sha256(b).hexdigest() == row['sha256']
        row['git_blob_sha'] = hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
with (root / dest).open('w', encoding='utf-8', newline='') as f:
    fields=['nombre_original','ruta_actual','sha256','bytes','git_blob_sha','clasificacion']
    writer=csv.DictWriter(f,fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
print('MANIFIESTO_SHA256_APROBADO=OK')
PY
echo '========== REGRESION ANTES DE PUBLICAR =========='
python3 scripts/validacion/validar-capturas-unificadas.py
python3 -m unittest discover -s tests -p 'test_capturas_por_fase.py' -v
git add -- evidencias/capturas/fase1 evidencias/capturas/fase2 evidencias/capturas/fase3 "$LOTE"
test "$(git diff --cached --name-only --diff-filter=A | wc -l)" -eq 22
test -z "$(git diff --name-only)"
git diff --cached --stat
git commit -m 'docs(evidencias): agregar 21 PNG originales S01-S03 con hashes verificados'
git push -u origin "$BRANCH"
git switch main
echo "RAMA_PUBLICADA=$BRANCH"
echo 'CAPTURAS_PUBLICADAS_EN_RAMA=4/9/8'
echo 'MAIN_LOCAL_SIN_MODIFICACIONES=SI'
echo 'CAPTURAS_LISTAS_PARA_REVISION_PR=OK'
