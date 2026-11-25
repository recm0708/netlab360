#!/usr/bin/env bash
# Validar y actualizar de forma reversible el broker; ejecutar el piloto aislado.
set -Eeuo pipefail
umask 077
export LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1
BASE=98c31fc8eba1ddcbe7c9526028a24f8c51f879a5
TARGET="$(git rev-parse HEAD)"
DIR="$HOME/netlab360-bootstrap/s08/evidencias/s08-007"
STAMP="$(date +%Y%m%d_%H%M%S)"
PY="$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python"
ACCOUNT=netlab360-s08-api
INSTALL=/usr/local/libexec/netlab360/s08-broker
RUNTIME=/run/netlab360-s08-broker
UNIT=netlab360-s08-probe.socket
STAGE=""
UPDATED=0
ACCEPTED=0

verify_data() {
    "$PY" -B - "$DIR/S08-007B_Estado_Antes_20261125_051459.json" <<'PY'
from pathlib import Path
from contextlib import closing
import hashlib, json, os, sqlite3, sys
home = Path.home()
state = home / "netlab360-bootstrap/s08/estado"
dev = Path(f"/tmp/netlab360-ui-session-{os.getuid()}/estado")
paths = {
    "SQLITE_DEFINITIVA":state/"consola.sqlite3",
    "SQLITE_DESARROLLO":dev/"consola.sqlite3",
    "SQLITE_HISTORICA":home/"netlab360-bootstrap/s04/historial/incidentes.sqlite3",
    "JSON_DEFINITIVO":state/"alertas-historicas.json",
    "JSON_DESARROLLO":dev/"alertas-historicas.json",
}
baseline = json.loads(Path(sys.argv[1]).read_text())
for name, path in paths.items():
    assert path.is_file() and not path.is_symlink(), name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == baseline[name]["file_sha256"], name
    if path.suffix == ".sqlite3":
        with closing(sqlite3.connect(path.as_uri()+"?mode=ro",uri=True)) as db:
            assert db.execute("PRAGMA quick_check").fetchall() == [("ok",)]
    print(name+"=SIN_CAMBIOS")
print("ARCHIVOS_PROTEGIDOS_INTACTOS=5/5")
PY
}

pid_for() {
    ss -H -ltnp "sport = :$1" | grep -oE 'pid=[0-9]+' | cut -d= -f2 | sort -u
}

idle_broker() {
    local running ns port
    for _ in $(seq 1 50); do
        running="$(systemctl list-units --type=service --state=running --no-legend --plain 'netlab360-s08-probe@*.service')"
        [[ -z "$running" ]] && break
        sleep 0.2
    done
    test -z "$running"
    if pgrep -x iperf3 >/dev/null; then return 1; fi
    if ps -eo comm=,args= | awk '$1 ~ /^python/ && /[c]ontent_worker[.]py/ {found=1} END{exit !found}'; then return 1; fi
    for ns in nl360-s02-h-hq-120 nl360-s02-h-s1-220 nl360-s02-h-s2-320; do
        for port in 5201 5202; do
            test -z "$(sudo -n ip netns exec "$ns" ss -H -lntu "sport = :$port")"
        done
    done
    sudo -n flock -n "$RUNTIME/active.lock" /usr/bin/true
    echo "BROKER_LIBRE=OK PUERTOS_LIBRES=6/6 PROCESOS_RESIDUALES=0"
}

restore() {
    local rc=$?
    trap - EXIT
    if [[ "$UPDATED" == 1 && "$ACCEPTED" == 0 ]]; then
        echo "========== CONTENCION Y REVERSION =========="
        # Cada operación de reversión es comprobada; no depende de errexit dentro de if.
        if sudo -n systemctl stop "$UNIT" &&
           sudo -n systemctl stop 'netlab360-s08-probe@*.service' &&
           sudo -n install -o root -g root -m 0644 "$STAGE/previous/entry.py" "$INSTALL/entry.py" &&
           sudo -n install -o root -g root -m 0644 "$STAGE/previous/api/probe_broker.py" "$INSTALL/api/probe_broker.py" &&
           sudo -n install -o root -g root -m 0644 "$STAGE/previous/api/content_worker.py" "$INSTALL/api/content_worker.py" &&
           sudo -n rm -f -- "$INSTALL/api/broker_stream.py" "$INSTALL/api/stream_protocol.py" &&
           cmp "$STAGE/previous/entry.py" "$INSTALL/entry.py" &&
           cmp "$STAGE/previous/api/probe_broker.py" "$INSTALL/api/probe_broker.py" &&
           cmp "$STAGE/previous/api/content_worker.py" "$INSTALL/api/content_worker.py" &&
           sudo -n systemctl start "$UNIT" &&
           test "$(systemctl is-active "$UNIT")" = active; then
            echo "BROKER_ANTERIOR_RESTAURADO=OK"
        else
            echo "REVERSION_REQUIERE_REVISION=SI"
            sudo -n systemctl stop "$UNIT" || true
        fi
    fi
    if [[ -n "$STAGE" ]]; then
        if [[ "$rc" == 0 && "$ACCEPTED" == 1 ]]; then
            if sudo -n -u "$ACCOUNT" find "$STAGE/private" -mindepth 1 -delete &&
               sudo -n rmdir "$STAGE/private" && rm -r -- "$STAGE"; then
                echo "ENTORNO_PILOTO_ELIMINADO=OK"
            else
                echo "LIMPIEZA_REQUIERE_REVISION=$STAGE"
                rc=1
            fi
        else
            echo "ENTORNO_PILOTO_CONSERVADO=$STAGE"
        fi
    fi
    exit "$rc"
}
trap restore EXIT
trap 'echo "ERROR_LINEA=$LINENO COMANDO=$BASH_COMMAND"' ERR

echo "========== 881 PRECONDICIONES =========="
test "$(hostname)" = netlab360-lab
test "$(id -u)" -ne 0
test "$(git branch --show-current)" = s08/consola-trabajos
test -z "$(git status --porcelain)"
git merge-base --is-ancestor "$BASE" "$TARGET"
test -x "$PY"
test "$(id -u "$ACCOUNT")" = 997
test "$(id -u netlab360-s08-worker)" = 994
test "$(pid_for 9140)" = 831731
test "$(pid_for 9130)" = 2138999
test -z "$(ss -H -ltn 'sport = :9145')"
MGMT="$(ip -4 -o addr show dev ens33)"
ROUTE="$(ip -4 route show default)"
sudo -v
SUDO_BEFORE="$(sudo -n -l)"
test "$(systemctl is-active "$UNIT")" = active
test "$(systemctl is-enabled "$UNIT")" = enabled
test "$(stat -c '%U:%a' "$RUNTIME/control.sock")" = "$ACCOUNT:600"
verify_data
idle_broker
echo "PRECONDICIONES=OK"

echo "========== 882 REGRESION Y CI =========="
"$PY" -B - <<'PY'
import unittest
suite = unittest.defaultTestLoader.discover("tests",pattern="test_s08_*.py")
result = unittest.TextTestRunner(verbosity=1).run(suite)
assert result.wasSuccessful() and not result.skipped
assert result.testsRun == 307, result.testsRun
print("PRUEBAS_S08=307/307")
PY
node --check servicios/consola-s08/ui/static/jobs.js
node --check servicios/consola-s08/ui/static/app.js
python3 -B scripts/validacion/auditar_estilo_repositorio.py | tee "$DIR/S08-007CDE_Estilo_$STAMP.txt"
grep -Fx 'CANDIDATOS_REVISION=0' "$DIR/S08-007CDE_Estilo_$STAMP.txt"
gh pr checks 267 --watch --fail-fast
test "$(gh pr view 267 --json headRefOid --jq .headRefOid)" = "$TARGET"
echo "CI_PR_267=SUCCESS"

echo "========== 883 PREPARAR PILOTO =========="
STAGE="$(mktemp -d /tmp/netlab360-s08-cde.XXXXXX)"
chmod 0755 "$STAGE"
mkdir -p "$STAGE/repo" "$STAGE/deps" "$STAGE/previous/api" "$STAGE/new/api"
git archive "$TARGET" servicios/consola-s08 scripts/s07 scripts/s08/piloto_consola_trabajos.py | tar -xf - -C "$STAGE/repo"
chmod -R a+rX "$STAGE/repo"
"$PY" -B - "$STAGE/deps" <<'PY'
from importlib import metadata
from pathlib import Path
import shutil, sys
try:
    from packaging.requirements import Requirement
except ImportError:
    from pip._vendor.packaging.requirements import Requirement
destination = Path(sys.argv[1])
pending, copied = ["fastapi","uvicorn"], set()
while pending:
    dist = metadata.distribution(pending.pop())
    name = dist.metadata["Name"].lower().replace("_","-")
    if name in copied:
        continue
    base = Path(dist.locate_file("")).resolve()
    for item in dist.files or ():
        relative = Path(str(item))
        if relative.is_absolute() or ".." in relative.parts or "__pycache__" in relative.parts or relative.suffix == ".pyc":
            continue
        source = base / relative
        if source.is_file():
            target = destination / relative
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
    copied.add(name)
    for item in dist.requires or ():
        req = Requirement(item)
        if req.marker is None or req.marker.evaluate({"extra":""}):
            pending.append(req.name)
print("DEPENDENCIAS_COPIADAS="+str(len(copied)))
PY
chmod -R a+rX "$STAGE/deps"
sudo -n install -d -o "$ACCOUNT" -g "$ACCOUNT" -m 0700 "$STAGE/private"
sudo -n -u "$ACCOUNT" /usr/bin/python3 -I -B - "$STAGE" <<'PY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
sys.path[:0]=[str(root/"repo/servicios/consola-s08"),str(root/"deps")]
import uvicorn
from api import prometheus_reader, inference_reader, broker_client
from api.main import create_app
assert prometheus_reader.DIRECTORY == root/"repo/scripts/s07"
broker_client.check_identity()
compile((root/"repo/scripts/s08/piloto_consola_trabajos.py").read_text(),"piloto","exec")
print("IMPORTACIONES_Y_SINTAXIS_PILOTO=OK")
PY

echo "========== 884 VERIFICAR COPIA INSTALADA =========="
for f in __init__.py probe_catalog.py probe_executor.py transfer_executor.py content_executor.py content_worker.py job_contract.py probe_broker.py broker_transfer.py; do
    test -f "$INSTALL/api/$f"
    test ! -L "$INSTALL/api/$f"
    test "$(stat -c '%u:%g:%a' "$INSTALL/api/$f")" = "0:0:644"
    cmp "$INSTALL/api/$f" <(git show "$BASE:servicios/consola-s08/api/$f")
done
cmp "$INSTALL/entry.py" <(git show "$BASE:servicios/consola-s08/broker/entry.py")
for f in entry.py api/probe_broker.py api/content_worker.py; do
    cp "$INSTALL/$f" "$STAGE/previous/$f"
done
git show "$TARGET:servicios/consola-s08/broker/entry.py" > "$STAGE/new/entry.py"
for f in probe_broker.py content_worker.py broker_stream.py stream_protocol.py; do
    git show "$TARGET:servicios/consola-s08/api/$f" > "$STAGE/new/api/$f"
done
for f in broker_stream.py stream_protocol.py; do
    test ! -e "$INSTALL/api/$f"
    test ! -L "$INSTALL/api/$f"
done
BACKUP="$DIR/S08-007CDE_Broker_Anterior_$STAMP"
test ! -e "$BACKUP"
cp -a "$STAGE/previous" "$BACKUP"
echo "RESPALDO=$BACKUP"

echo "========== 885 ACTUALIZAR BROKER =========="
sudo -v
idle_broker
UPDATED=1
sudo -n systemctl stop "$UNIT"
test -z "$(systemctl list-units --type=service --state=running --no-legend 'netlab360-s08-probe@*.service')"
for f in entry.py api/probe_broker.py api/content_worker.py api/broker_stream.py api/stream_protocol.py; do
    sudo -n install -o root -g root -m 0644 "$STAGE/new/$f" "$INSTALL/$f"
    cmp "$STAGE/new/$f" "$INSTALL/$f"
    test "$(stat -c '%u:%g:%a' "$INSTALL/$f")" = "0:0:644"
done
sudo -n systemctl start "$UNIT"
test "$(systemctl is-active "$UNIT")" = active
test "$(stat -c '%U:%a' "$RUNTIME/control.sock")" = "$ACCOUNT:600"

echo "========== 886-890 PILOTO HTTP REAL =========="
RESULT="$(mktemp "$DIR/S08-007CDE_Piloto_"$STAMP"_XXXXXX.jsonl")"
echo "EVIDENCIA=$RESULT"
sudo -n -u "$ACCOUNT" /usr/bin/timeout --kill-after=5s 180s \
    /usr/bin/python3 -I -B "$STAGE/repo/scripts/s08/piloto_consola_trabajos.py" \
    --deps "$STAGE/deps" --state "$STAGE/private/estado" | tee "$RESULT"
"$PY" -B - "$RESULT" <<'PY'
from pathlib import Path
import json, sys
rows=[json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines()]
assert len(rows)==4 and rows[-1]["kind"]=="acceptance"
assert rows[-1]["real_jobs"]==3 and rows[-1]["completed"]==2
assert rows[-1]["cancelled_under_load"]==1 and rows[-1]["history_reopened"]==3
assert rows[-1]["synthetic_queue_recovery"]==1
assert rows[-1]["storage"]["jobs"]==4 and rows[-1]["storage"]["integrity"]=="OK"
for row in rows[:-1]:
    job=row["job"]
    print("JOB="+job["job_id"]+" PERFIL="+job["data"]["selection"]["profile"]+" ESTADO="+job["status"])
    print("MUESTRAS="+str(len(job["data"]["progress"])))
    if job["status"]=="CANCELLED":
        assert job["data"]["cleanup_verified"] is True
        assert row["roles_observed_while_running"]==["receiver","sender"]
    elif job["data"]["selection"]["action"]=="test.content.tcp":
        assert row["roles_observed_while_running"]==["receiver","sender"]
        assert job["data"]["result"]["measurement"]["content_integrity_verified"] is True
print("HTTP_REAL_COMPLETADOS=2/2")
print("CANCELACION_REAL_BAJO_CARGA=1/1")
print("PROGRESO_REAL_CONTENIDO=OK")
print("HISTORICO_REABIERTO=3/3")
print("RECUPERACION_COLA_SINTETICA=1/1")
PY

echo "========== 891 CONTINUIDAD =========="
sudo -v
test -z "$(ss -H -ltn 'sport = :9145')"
idle_broker
test "$(pid_for 9140)" = 831731
test "$(pid_for 9130)" = 2138999
test "$(ip -4 -o addr show dev ens33)" = "$MGMT"
test "$(ip -4 route show default)" = "$ROUTE"
test "$(sudo -n -l)" = "$SUDO_BEFORE"
test "$(systemctl is-active "$UNIT")" = active
test "$(systemctl is-enabled "$UNIT")" = enabled
verify_data
bash operacion/estado.sh
git diff --check
test -z "$(git status --porcelain)"

echo "========== 892 ACEPTACION =========="
echo "S08_007CDE_PILOTO=OK"
echo "BROKER_NUEVO_INSTALADO=OK"
echo "API_TEMPORAL_DETENIDA=OK"
echo "FASTAPI_OPERACIONAL_REINICIADO=NO"
echo "MUTACIONES_RED=NO"
echo "NAVEGACION_VISUAL_PENDIENTE=SI"
ACCEPTED=1
