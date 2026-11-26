#!/usr/bin/env bash
# Aprovisionar exclusivamente el canal de consulta y contrastar el registro existente.
set -Eeuo pipefail
umask 077
export LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1

test "$#" -eq 1
EVIDENCE="$1"
test -d "$EVIDENCE"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
ACCOUNT=netlab360-s08-api
OWNER=netlab360-s08-alerts
INSTALL=/usr/local/libexec/netlab360/s08-alertas
DB=/var/lib/netlab360/s08-alertas/notificaciones.sqlite3
UNIT=netlab360-s08-alert-read.socket
SOCKET=/run/netlab360-s08-alert-read/control.sock
TEMPLATE=netlab360-s08-alert-read@.service
SCRIPT="$INSTALL/consultar_alertas.py"
STAGE="$(mktemp -d /tmp/netlab360-s08-alert-read.XXXXXX)"
CREATED=0
ACCEPTED=0

finish() {
    local rc=$?
    trap - EXIT
    if [[ "$ACCEPTED" -ne 1 && "$CREATED" -eq 1 ]]; then
        sudo -n systemctl stop "$UNIT" || true
        if test -z "$(systemctl list-units --type=service --state=running --no-legend 'netlab360-s08-alert-read@*.service')"; then
            sudo -n rm -f -- "/run/systemd/system/$UNIT" "/run/systemd/system/$TEMPLATE" "$SCRIPT"
            sudo -n systemctl daemon-reload
            echo "CANAL_NUEVO_REVERTIDO=OK"
        else
            echo "CANAL_NUEVO_REQUIERE_REVISION=SI"
        fi
    fi
    rm -rf -- "$STAGE"
    exit "$rc"
}
trap finish EXIT

inspect() {
    sudo -n -u "$OWNER" /usr/bin/python3 -I -B "$INSTALL/recibir_alertas.py" "$1" --database "$DB"
}

echo "========== 1001 VERIFICAR AISLAMIENTO =========="
test "$(id -u)" -ne 0
test "$(systemctl is-active netlab360-s08-alert-receiver)" = active
test "$(systemctl is-active netlab360-s08-alert-am)" = active
cmp "$INSTALL/recibir_alertas.py" scripts/s08/recibir_alertas.py
test "$(sudo -n stat -c '%U:%a' "$DB")" = "$OWNER:600"
sudo -n -u "$ACCOUNT" test ! -r "$DB"
sudo -n -u "$ACCOUNT" test ! -w "$DB"
sudo -n -u "$ACCOUNT" test ! -r "$INSTALL/webhook.secret"
sudo -n -u "$ACCOUNT" test ! -r "$INSTALL/web.yml"
test "$(systemctl show "$UNIT" -p LoadState --value)" = not-found
for f in "$SCRIPT" "/run/systemd/system/$UNIT" "/run/systemd/system/$TEMPLATE" "$SOCKET"; do
    sudo -n test ! -e "$f"
    sudo -n test ! -L "$f"
done
for scope in operational validation; do
    inspect "$scope" > "$EVIDENCE/$scope-antes.json"
done
chmod 0755 "$STAGE"
git archive HEAD servicios/consola-s08/api | tar -xf - -C "$STAGE"
chmod -R a+rX "$STAGE/servicios"
echo "ACCESO_DIRECTO_API_BASE_Y_SECRETOS=DENEGADO"

echo "========== 1002 ACTIVAR CANAL DELIMITADO =========="
CREATED=1
sudo -n install -o root -g root -m 0644 scripts/s08/consultar_alertas.py "$SCRIPT"
for f in "$UNIT" "$TEMPLATE"; do
    sudo -n install -o root -g root -m 0644 "operacion/plantillas/$f" "/run/systemd/system/$f"
    cmp "operacion/plantillas/$f" "/run/systemd/system/$f"
done
cmp scripts/s08/consultar_alertas.py "$SCRIPT"
sudo -n systemd-analyze verify "/run/systemd/system/$UNIT" "/run/systemd/system/$TEMPLATE"
sudo -n systemctl daemon-reload
sudo -n systemctl start "$UNIT"
test "$(systemctl is-active "$UNIT")" = active
test "$(stat -c '%U:%a' "$SOCKET")" = "$ACCOUNT:600"
test ! -w "$SOCKET"
echo "CANAL_UNIX_ACTIVO=OK"

echo "========== 1003 CONTRASTE REAL =========="
sudo -n -u "$ACCOUNT" /usr/bin/python3 -I -B - "$STAGE" > "$EVIDENCE/consulta-api.json" <<'PY'
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(sys.argv[1]) / "servicios/consola-s08"))
from api import notification_reader as N
result = {scope: N.collect(scope) for scope in N.SCOPES}
print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
assert all(row["transport"] == "OK" for row in result.values()), "NOTIFICATION_TRANSPORT"
PY
for scope in operational validation; do
    inspect "$scope" > "$EVIDENCE/$scope-despues.json"
done
/usr/bin/python3 -I -B - "$EVIDENCE" "$ROOT" <<'PY'
from pathlib import Path
import json
import sys
root = Path(sys.argv[1])
sys.path.insert(0, str(Path(sys.argv[2]) / "servicios/consola-s08"))
from api import notification_reader as N
observed = json.loads((root / "consulta-api.json").read_text())
for scope, row in observed.items():
    before = json.loads((root / (scope + "-antes.json")).read_text())
    after = json.loads((root / (scope + "-despues.json")).read_text())
    assert before == after, "HISTORY_CHANGED_DURING_COMPARISON"
    expected = N.project(json.dumps({"schema": "NETLAB360_S08_NOTIFICATIONS_V1",
                                     "status": "OK", "result": after}).encode(), scope)
    assert row["transport"] == "OK"
    assert all(row[key] == value for key, value in expected.items())
    print(f"ALCANCE={scope} REGISTROS={row['total']} CONTRASTE=MATCH")
    if scope == "validation":
        assert any(r["status"] == "firing" and any(
            q["status"] == "resolved" and q["fingerprint"] == r["fingerprint"]
            and q["starts_at_utc"] == r["starts_at_utc"] for q in row["records"])
                   for r in row["records"])
print("ALCANCES_CONTRASTADOS=2/2")
print("VALIDACION_SINTETICA_SEPARADA=OK")
PY
sudo -n -u "$ACCOUNT" test ! -r "$DB"
sudo -n -u "$ACCOUNT" test ! -w "$DB"
test "$(systemctl is-active "$UNIT")" = active
echo "HISTORIAL_ORIGINAL_CONSERVADO=OK"
ACCEPTED=1
echo "LECTURA_NOTIFICACIONES=OK"
