#!/usr/bin/env bash
# Validar y actualizar de forma reversible el broker; ejecutar el piloto aislado.
set -Eeuo pipefail
umask 077
export LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1
BASE=68569ecab6f395589c90a9e1f098cf8caeeb8c09
TARGET="$(git rev-parse HEAD)"
DIR="$HOME/netlab360-bootstrap/s08/evidencias/s08-008"
STAMP="$(date +%Y%m%d_%H%M%S)"
PY="$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python"
ACCOUNT=netlab360-s08-api
INSTALL=/usr/local/libexec/netlab360/s08-broker
RUNTIME=/run/netlab360-s08-broker
UNIT=netlab360-s08-probe.socket
STAGE=""
UPDATED=0
ACCEPTED=0
OLD_FILES=(__init__.py probe_catalog.py probe_executor.py transfer_executor.py content_executor.py content_worker.py job_contract.py probe_broker.py broker_transfer.py broker_stream.py stream_protocol.py)
CHANGED=(entry.py api/probe_broker.py api/broker_stream.py api/stream_protocol.py)
NEW=api/iperf_native.py

protected_state() {
    "$PY" -B - <<'PY'
from pathlib import Path
from contextlib import closing
import hashlib, json, os, sqlite3
home = Path.home()
state = home / "netlab360-bootstrap/s08/estado"
dev = Path(f"/tmp/netlab360-ui-session-{os.getuid()}/estado")
paths = [state/"consola.sqlite3", dev/"consola.sqlite3",
         home/"netlab360-bootstrap/s04/historial/incidentes.sqlite3",
         state/"alertas-historicas.json", dev/"alertas-historicas.json"]
result = {}
for path in paths:
    assert path.is_file() and not path.is_symlink()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.suffix == ".sqlite3":
        with closing(sqlite3.connect(path.as_uri()+"?mode=ro",uri=True)) as db:
            db.execute("PRAGMA query_only=ON")
            assert db.execute("PRAGMA quick_check").fetchall() == [("ok",)]
    else:
        data = json.loads(path.read_text())
        assert data["total"] == len(data["records"])
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    result[str(path)] = digest
print(json.dumps(result,sort_keys=True))
PY
}

observability_state() {
    local u pid
    for u in netlab360-s04-prometheus netlab360-s08-observe-bb-hq netlab360-s08-observe-bb-s2 netlab360-s08-observe-relay-hq netlab360-s08-observe-relay-s2 netlab360-s08-observe-gateway netlab360-s08-alert-am netlab360-s08-alert-receiver; do
        test "$(systemctl is-active "$u")" = active || return 1
        pid="$(systemctl show "$u" -p MainPID --value)"
        test "$pid" -gt 1 || return 1
        echo "$u=$pid"
    done
    sha256sum "$HOME/netlab360-bootstrap/s06/recuperacion-prometheus-20261122_232957/prometheus-runtime.yml" \
        servicios/observabilidad/prometheus/rules/s04-alerts.yml \
        /usr/local/libexec/netlab360/s08-observacion/s08-probe-alerts.yml
    sudo -n sha256sum /usr/local/libexec/netlab360/s08-alertas/webhook.secret \
        /usr/local/libexec/netlab360/s08-alertas/web.yml \
        "$HOME/netlab360-bootstrap/s08/alertmanager-prometheus.secret"
    sudo -n -u netlab360-s08-alerts /usr/bin/python3 -I -B \
        /usr/local/libexec/netlab360/s08-alertas/recibir_alertas.py validation \
        --database /var/lib/netlab360/s08-alertas/notificaciones.sqlite3
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

restore_files() {
    local f
    for f in "${CHANGED[@]}"; do
        sudo -n install -o root -g root -m 0644 "$STAGE/previous/$f" "$INSTALL/$f" || return 1
        cmp "$STAGE/previous/$f" "$INSTALL/$f" || return 1
    done
    sudo -n rm -f -- "$INSTALL/$NEW" || return 1
    test ! -e "$INSTALL/$NEW"
}

restore() {
    local rc=$?
    trap - EXIT
    if [[ "$UPDATED" == 1 && "$ACCEPTED" == 0 ]]; then
        echo "========== CONTENCION Y REVERSION =========="
        # Cada operación de reversión es comprobada; no depende de errexit dentro de if.
        if sudo -n systemctl stop "$UNIT" &&
           sudo -n systemctl stop 'netlab360-s08-probe@*.service' &&
           restore_files &&
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

echo "========== 964 PRECONDICIONES =========="
test "$(hostname)" = netlab360-lab
test "$(id -u)" -ne 0
test "$(git branch --show-current)" = s08/iperf-progreso-activo
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
PROTECTED_BEFORE="$(protected_state)"
OBS_BEFORE="$(observability_state)"
idle_broker
echo "PRECONDICIONES=OK"

echo "========== 965 PRUEBAS Y CI =========="
"$PY" -B -m unittest discover -s tests -p test_s08_stream.py -v
"$PY" -B -m unittest discover -s tests -p test_s08_jobs_http.py -v
node --check servicios/consola-s08/ui/static/jobs.js
python3 -B scripts/validacion/auditar_estilo_repositorio.py | tee "$DIR/S08-008BC4_Estilo_$STAMP.txt"
grep -Fx 'CANDIDATOS_REVISION=0' "$DIR/S08-008BC4_Estilo_$STAMP.txt"
gh pr checks 272 --watch --fail-fast
test "$(gh pr view 272 --json headRefOid --jq .headRefOid)" = "$TARGET"
echo "CI_PR_272=SUCCESS"

echo "========== 966 PREPARAR PILOTO =========="
STAGE="$(mktemp -d /tmp/netlab360-s08-bc4.XXXXXX)"
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

echo "========== 967 VERIFICAR COPIA INSTALADA =========="
for f in "${OLD_FILES[@]}"; do
    test -f "$INSTALL/api/$f"
    test ! -L "$INSTALL/api/$f"
    test "$(stat -c '%u:%g:%a' "$INSTALL/api/$f")" = "0:0:644"
    cmp "$INSTALL/api/$f" <(git show "$BASE:servicios/consola-s08/api/$f")
done
cmp "$INSTALL/entry.py" <(git show "$BASE:servicios/consola-s08/broker/entry.py")
test "$(stat -c '%u:%g:%a' "$INSTALL/entry.py")" = "0:0:644"
test ! -L "$INSTALL/entry.py"
test ! -e "$INSTALL/$NEW"
test ! -L "$INSTALL/$NEW"
for f in "${CHANGED[@]}"; do
    cp "$INSTALL/$f" "$STAGE/previous/$f"
done
git show "$TARGET:servicios/consola-s08/broker/entry.py" > "$STAGE/new/entry.py"
for f in api/probe_broker.py api/broker_stream.py api/stream_protocol.py "$NEW"; do
    git show "$TARGET:servicios/consola-s08/$f" > "$STAGE/new/$f"
done
BACKUP="$DIR/S08-008BC4_Broker_Anterior_$STAMP"
test ! -e "$BACKUP"
cp -a "$STAGE/previous" "$BACKUP"
echo "RESPALDO=$BACKUP"

echo "========== 968 ACTUALIZAR BROKER =========="
sudo -v
idle_broker
UPDATED=1
sudo -n systemctl stop "$UNIT"
test -z "$(systemctl list-units --type=service --state=running --no-legend 'netlab360-s08-probe@*.service')"
for f in "${CHANGED[@]}" "$NEW"; do
    sudo -n install -o root -g root -m 0644 "$STAGE/new/$f" "$INSTALL/$f"
    cmp "$STAGE/new/$f" "$INSTALL/$f"
    test "$(stat -c '%u:%g:%a' "$INSTALL/$f")" = "0:0:644"
done
sudo -n systemctl start "$UNIT"
test "$(systemctl is-active "$UNIT")" = active
test "$(stat -c '%U:%a' "$RUNTIME/control.sock")" = "$ACCOUNT:600"

echo "========== 969-972 PILOTO HTTP REAL =========="
RESULT="$(mktemp "$DIR/S08-008BC4_Piloto_"$STAMP"_XXXXXX.jsonl")"
echo "EVIDENCIA=$RESULT"
sudo -n -u "$ACCOUNT" /usr/bin/timeout --kill-after=5s 180s \
    /usr/bin/python3 -I -B "$STAGE/repo/scripts/s08/piloto_consola_trabajos.py" \
    --deps "$STAGE/deps" --state "$STAGE/private/estado" --iperf | tee "$RESULT"
"$PY" -B - "$RESULT" <<'PY'
from pathlib import Path
import json, sys
rows=[json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines()]
assert len(rows)==5 and rows[-1]["kind"]=="acceptance"
assert rows[-1]["real_jobs"]==4 and rows[-1]["completed"]==3
assert rows[-1]["cancelled_under_load"]==1 and rows[-1]["history_reopened"]==4
assert rows[-1]["synthetic_queue_recovery"]==1
assert rows[-1]["storage"]["jobs"]==5 and rows[-1]["storage"]["integrity"]=="OK"
expected={"tcp-10s":"SUCCEEDED","udp-10s":"SUCCEEDED","tcp-500mb":"CANCELLED","content-100mb":"SUCCEEDED"}
for row in rows[:-1]:
    job=row["job"]
    profile=job["data"]["selection"]["profile"]
    assert job["status"]==expected.pop(profile)
    assert row["roles_observed_while_running"]==["receiver","sender"]
    progress=job["data"]["progress"]
    assert progress
    if profile.startswith(("tcp-","udp-")):
        assert all("interval_bytes" in p for p in progress)
    if job["status"]=="CANCELLED":
        assert job["data"]["cleanup_verified"] is True
        assert job["data"]["result"] is None
    elif profile.startswith("content-"):
        assert job["data"]["result"]["measurement"]["content_integrity_verified"] is True
    print("PERFIL="+profile+" ESTADO="+job["status"]+" MUESTRAS="+str(len(progress)))
assert not expected
print("IPERF_TCP_UDP_EN_VIVO=2/2")
print("CANCELACION_IPERF_BAJO_CARGA=1/1")
print("CONTENIDO_REGRESION=1/1")
print("HISTORICO_REABIERTO=4/4")
PY

echo "========== 973 CONTINUIDAD =========="
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
test "$(protected_state)" = "$PROTECTED_BEFORE"
test "$(observability_state)" = "$OBS_BEFORE"
echo "ARCHIVOS_PROTEGIDOS_INTACTOS=5/5"
echo "OBSERVABILIDAD_SIN_REINICIOS=8/8"
bash operacion/estado.sh
git diff --check
test -z "$(git status --porcelain)"

echo "========== 974 ACEPTACION =========="
echo "S08_008BC4_LOCAL=OK"
echo "BROKER_NUEVO_INSTALADO=OK"
echo "API_TEMPORAL_DETENIDA=OK"
echo "FASTAPI_OPERACIONAL_REINICIADO=NO"
echo "MUTACIONES_RED=NO"
echo "NAVEGACION_VISUAL_PENDIENTE=SI"
ACCEPTED=1
