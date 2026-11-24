#!/usr/bin/env bash
# Aceptación S07-008A-C; no cancelar watchdogs ante error.
set -Eeuo pipefail
trap 'echo "ERROR_LINEA=$LINENO CODIGO=$?"; echo "No repetir ni cancelar watchdogs; conservar resultados."' ERR
export GIT_PAGER=cat PAGER=cat GH_PAGER=cat SYSTEMD_PAGER=cat
export PYTHONDONTWRITEBYTECODE=1 GIT_TERMINAL_PROMPT=0
umask 077
cd "$HOME/proyectos/netlab360"
test "$(git branch --show-current)" = main
test -z "$(git status --porcelain)"
test "$(hostname)" = netlab360-lab
sudo -v
BOOT="$HOME/netlab360-bootstrap"
STATE="/var/lib/netlab360/s07-api"
EXEC="/usr/local/libexec/netlab360/s07-api.py"
UNIT="netlab360-s07-api.service"
SOCK="/run/netlab360-s07-api/api.sock"
PF="/usr/local/libexec/netlab360/s07-preflight.py"
RUN="$(mktemp -d "$BOOT/s07/orquestador/S07_008AC_$(date +%Y%m%d_%H%M%S)_XXXXXX")"
echo "========== NETLAB360 S07-008A-C =========="
date -Is
echo "DIRECTORIO_RESULTADOS=$RUN"
echo "========== 01 PRECHECK =========="
GESTION="$(ip -4 -o addr show dev ens33)"
GATEWAY="$(ip -4 route show default)"
[[ "$GESTION" == *"192.168.47.40/24"* ]]
[[ "$GATEWAY" == *"192.168.47.2 dev ens33"* ]]
test "$(sudo -n ip netns list | wc -l)" -eq 21
test "$(sudo -n docker ps -q | wc -l)" -eq 4
for u in "$UNIT" netlab360-s07-ospf-broker.service netlab360-s07-rfc-live.service netlab360-s07-rfc-preview.service; do
    if systemctl is-active --quiet "$u"; then echo "SERVICIO_PREVIO_ACTIVO=$u"; exit 19; fi
done
TIMERS="$(systemctl list-timers --all --plain --no-legend)"
if grep -Eq 'netlab360-s07-(wan-rescue-|http-rescue-|ospf-|recovery-)|nl360-s05-.*rescate-' <<< "$TIMERS"; then
    echo "WATCHDOG_PENDIENTE";exit 20
fi
sudo -n cmp -s scripts/s07/ospf_trial.py /usr/local/libexec/netlab360/s07-ospf-trial.py
sudo -n cmp -s scripts/s07/rfc_ospf_operacional.py /usr/local/libexec/netlab360/s07-ospf-broker.py
sudo -n cmp -s scripts/s07/preflight_protegido.py "$PF"
echo "PRECHECK=OK"
echo "========== 02 PRUEBAS API =========="
python3 -m unittest discover -s tests -p 'test_s07_api.py' -v
echo "PRUEBAS_API=OK"
echo "========== 03 SNAPSHOT Y PREFLIGHT =========="
sudo -n /usr/bin/python3 -I "$PF" check > "$RUN/preflight-inicial.json"
python3 scripts/s07/api_snapshot_s07.py > "$RUN/advisory.json"
python3 - "$RUN" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1])
d=json.loads((p/"preflight-inicial.json").read_text())
assert d["ok"] and d["configuration_status"]=="MET"
s=json.loads((p/"advisory.json").read_text())
assert set(s)=={"observed_at_utc","incidents","hypotheses","runbooks"}
print("SNAPSHOT_DECLARATIVO=OK")
print("PREFLIGHT=MET")
PY
echo "========== 04 INSTALACION PROTEGIDA =========="
sudo -n python3 -I - "$EXEC" "$STATE" <<'PY'
from pathlib import Path
import stat,sys
exe,state=map(Path,sys.argv[1:])
for p in (exe.parent,state.parent):
    s=p.lstat()
    assert stat.S_ISDIR(s.st_mode) and s.st_uid==s.st_gid==0 and not s.st_mode&0o022
for p in (exe,state,state/"advisory.json",state/"idempotency.sqlite3"):
    if p.exists() or p.is_symlink():
        s=p.lstat()
        assert s.st_uid==s.st_gid==0 and not stat.S_ISLNK(s.st_mode)
print("RUTAS_PROTEGIDAS=OK")
PY
sudo -n install -d -o root -g root -m 0700 "$STATE"
if sudo -n test -e "$EXEC"; then
    sudo -n cmp -s scripts/s07/api_s07.py "$EXEC"
else
    sudo -n install -o root -g root -m 0755 scripts/s07/api_s07.py "$EXEC"
fi
sudo -n install -o root -g root -m 0600 "$RUN/advisory.json" "$STATE/advisory.json"
sudo -n cmp -s scripts/s07/api_s07.py "$EXEC"
sudo -n systemd-run --unit="$UNIT" --property=Type=exec \
    --property=RuntimeDirectory=netlab360-s07-api --property=RuntimeDirectoryMode=0755 \
    --property=NoNewPrivileges=yes --property=ProtectHome=yes --property=UMask=0077 \
    /usr/bin/python3 -I "$EXEC" serve
for n in $(seq 1 20); do test -S "$SOCK" && break; sleep 0.5; done
systemctl is-active --quiet "$UNIT"
test -S "$SOCK"
stat -c '%U:%G %a %F %n' "$SOCK"
# Un UID ajeno no puede abrir el socket; prueba sin acceso al repo.
sudo -n -u nobody /usr/bin/python3 -I - "$SOCK" <<'PY'
import socket,sys
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
    try:s.connect(sys.argv[1])
    except PermissionError:print("UID_AJENO_TRANSPORTE=DENEGADO")
    else:raise SystemExit("UID_AJENO_ACCESO_INESPERADO")
PY
echo "API_UNIX=ACTIVA"
echo "========== 05 ACEPTACION REAL =========="
sudo -v
if python3 -u scripts/s07/aceptar_api_s07.py "$RUN" </dev/tty 2>&1 | tee "$RUN/ejecucion.txt"; then
    echo "CICLO_API=OK"
else
    echo "ACEPTACION_INCOMPLETA | NO REPETIR";exit 30
fi
echo "========== 06 POSTCONDICIONES =========="
RID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["rfc_id"])' "$RUN/summary.json")"
[[ "$RID" =~ ^[0-9a-f]{32}$ ]]
TIMER="netlab360-s07-ospf-$RID.timer"
if systemctl is-active --quiet "$TIMER"; then
    if ! sudo -n systemctl stop "$TIMER"; then
        if systemctl is-active --quiet "$TIMER"; then exit 39; fi
    fi
fi
if systemctl is-active --quiet "$TIMER"; then exit 39; fi
sudo -n systemctl stop "$UNIT"
if systemctl is-active --quiet "$UNIT"; then exit 39; fi
sudo -n /usr/bin/python3 -I "$PF" check > "$RUN/preflight-final.json"
python3 - "$RUN" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1])
a=json.loads((p/"preflight-inicial.json").read_text())
b=json.loads((p/"preflight-final.json").read_text())
assert b["ok"] and b["configuration_status"]=="MET"
for k in ("costs","neighbors","routes","management"):
    assert a[k]==b[k]
    print(k.upper()+"=RESTAURADO_O_INALTERADO")
PY
test "$(sudo -n ip netns list | wc -l)" -eq 21
test "$(sudo -n docker ps -q | wc -l)" -eq 4
test "$(ip -4 -o addr show dev ens33)" = "$GESTION"
test "$(ip -4 route show default)" = "$GATEWAY"
for u in netlab360-s04-exporter netlab360-s04-prometheus netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2 netlab360-s05-noc; do
    systemctl is-active --quiet "$u.service"
done
curl -fsS --max-time 10 http://127.0.0.1:9091/-/ready
curl -fsS --max-time 10 http://127.0.0.1:9130/healthz
echo
test -z "$(systemctl list-units --state=failed --no-legend --plain)"
TIMERS="$(systemctl list-timers --all --plain --no-legend)"
if grep -Eq 'netlab360-s07-(wan-rescue-|http-rescue-|ospf-|recovery-)|nl360-s05-.*rescate-' <<< "$TIMERS"; then echo "WATCHDOG_PENDIENTE";exit 40;fi
echo "NAMESPACES=21"
echo "CONTENEDORES=4"
echo "SERVICIOS_OPERACIONALES_ACTIVOS=7"
echo "WATCHDOGS_PENDIENTES=0"
echo "API_TEMPORAL=DETENIDA"
echo "========== 07 REGRESION Y BASES =========="
mkdir -p "$BOOT/archivo-local/regresiones"
LOG="$BOOT/archivo-local/regresiones/S07_008AC_$(date +%Y%m%d_%H%M%S).txt"
if python3 -m unittest discover -s tests -p 'test_*.py' -v > "$LOG" 2>&1; then tail -10 "$LOG";else tail -100 "$LOG";exit 50;fi
sudo -n /usr/bin/python3 -I - "$STATE/idempotency.sqlite3" <<'PY'
import sqlite3,sys
from pathlib import Path
from contextlib import closing
with closing(sqlite3.connect(Path(sys.argv[1]).as_uri()+"?mode=ro",uri=True)) as c:
    assert c.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
    assert c.execute("SELECT count(*) FROM requests WHERE code IS NULL").fetchone()[0]==0
    print("IDEMPOTENCIA_SQLITE=INTEGRA")
PY
python3 - <<'PY'
from pathlib import Path
from contextlib import closing
import sqlite3,sys
sys.path.insert(0,"scripts/s07")
from almacen_eventos import summary
db=Path.home()/"netlab360-bootstrap/s07/estado/eventos.sqlite3"
with closing(sqlite3.connect(db.as_uri()+"?mode=ro",uri=True)) as c:
    d=summary(c)
    assert d["total"]==116 and d["integrity"]=="ok"
print("REGISTROS_HISTORICOS=116")
PY
python3 scripts/validacion/validar-capturas-unificadas.py
test -z "$(git status --porcelain)"
git --no-pager status --short --branch
gh run list --commit "$(git rev-parse HEAD)" --limit 10 --json databaseId,workflowName,status,conclusion --jq '.[] | [.databaseId,.workflowName,.status,.conclusion] | @tsv'
echo "========== 08 RESULTADO =========="
echo "ISSUE_ACTUAL=197"
echo "API_VERSIONADA=VALIDADA"
echo "CICLO_INTEGRADO_API=VERIFIED"
echo "APROBACIONES=2/2"
echo "AUTORIZACION_AUTOMATICA=NO"
echo "RFC=$RID"
echo "DIRECTORIO_RESULTADOS=$RUN"
echo "========== S07-008A-C=OK =========="
