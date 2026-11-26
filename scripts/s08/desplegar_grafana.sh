#!/usr/bin/env bash
# Despliegue aislado del artefacto oficial, sin modificar los servicios existentes.
set -Eeuo pipefail
umask 077
export LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1

test "$#" -eq 1
EVIDENCE="$1"
test -d "$EVIDENCE"
cd "$(dirname "$0")/../.."
ROOT="$PWD"
CACHE="$HOME/netlab360-bootstrap/s08/paquetes/s08-008"
VERSION=13.3.2
FILE=grafana_13.3.2_44555861735_linux_amd64.tar.gz
DIGEST=e6f06cf4ad96a4809294c2e78d3ebe6bc42a79bff36ffe35eefbe502fc19aa87
URL="https://dl.grafana.com/grafana/release/$VERSION/$FILE"
ACCOUNT=netlab360-s08-grafana
UNIT=netlab360-s08-grafana.service
PREFIX=/opt/netlab360-grafana
INSTALL="$PREFIX/grafana-$VERSION"
CONFIG="$PREFIX/grafana-config"
STATE=/var/lib/netlab360/grafana
SECRETS=/etc/netlab360/grafana
STAGE="$(mktemp -d "$CACHE/.grafana.XXXXXX")"
STARTED=0
ACCEPTED=0

finish() {
    local rc=$?
    trap - EXIT
    if [[ "$ACCEPTED" -ne 1 ]]; then
        if [[ "$STARTED" -eq 1 ]]; then
            sudo -n systemctl stop "$UNIT" || true
        fi
        echo "GRAFANA_NO_ACEPTADO=SI"
        echo "ENTORNO_DIAGNOSTICO=$STAGE"
        echo "RECURSOS_APROVISIONADOS_CONSERVADOS=SI"
    else
        rm -rf -- "$STAGE"
    fi
    exit "$rc"
}
trap finish EXIT

echo "========== 1012 PRECONDICIONES GRAFANA =========="
test "$(dpkg --print-architecture)" = amd64
test "$(systemctl show "$UNIT" -p LoadState --value)" = not-found
test -z "$(ss -H -ltn 'sport = :3000')"
if getent passwd "$ACCOUNT" >/dev/null || getent group "$ACCOUNT" >/dev/null; then
    echo "IDENTIDAD_PREEXISTENTE_REQUIERE_REVISION"
    exit 1
fi
sudo -v
for f in "$PREFIX" "$STATE" "$SECRETS" "/run/systemd/system/$UNIT"; do
    sudo -n test ! -e "$f"
    sudo -n test ! -L "$f"
done
curl --noproxy '*' -fsS http://127.0.0.1:9091/-/ready
# No habilitar interfaces de modificación de Prometheus a través de Grafana.
curl --noproxy '*' -fsS http://127.0.0.1:9091/api/v1/status/flags |
    python3 -c 'import json,sys; d=json.load(sys.stdin)["data"]; assert d["web.enable-admin-api"]=="false" and d["web.enable-lifecycle"]=="false"'
echo "PROMETHEUS_ADMIN_API_Y_LIFECYCLE=DESHABILITADOS"

echo "========== 1013 ARTEFACTO OFICIAL =========="
if [[ ! -e "$CACHE/$FILE" ]]; then
    curl --proto '=https' --tlsv1.2 --fail --location --retry 2 \
        --connect-timeout 15 --max-time 600 --output "$STAGE/$FILE" "$URL"
    printf '%s  %s\n' "$DIGEST" "$STAGE/$FILE" | sha256sum -c -
    test ! -e "$CACHE/$FILE"
    mv -- "$STAGE/$FILE" "$CACHE/$FILE"
fi
test -f "$CACHE/$FILE"
test ! -L "$CACHE/$FILE"
printf '%s  %s\n' "$DIGEST" "$CACHE/$FILE" | sha256sum -c -
echo "ARTEFACTO_OFICIAL_VERIFICADO=OK"
mkdir "$STAGE/extract"
python3 -I -B - "$CACHE/$FILE" "$STAGE/extract" <<'PY'
import tarfile
import sys
with tarfile.open(sys.argv[1], "r:gz") as archive:
    archive.extractall(sys.argv[2], filter="data")
PY
mapfile -t ROOTS < <(find "$STAGE/extract" -mindepth 1 -maxdepth 1 -type d)
test "${#ROOTS[@]}" -eq 1
SOURCE="${ROOTS[0]}"
test -x "$SOURCE/bin/grafana"
test -d "$SOURCE/public"
test -f "$SOURCE/conf/defaults.ini"
ldd "$SOURCE/bin/grafana" > "$EVIDENCE/dependencias-binario.txt" 2>&1 || true
if grep -F 'not found' "$EVIDENCE/dependencias-binario.txt"; then exit 1; fi
echo "EXTRACCION_Y_BINARIO=OK"

echo "========== 1014 APROVISIONAR GRAFANA =========="
sudo -v
sudo -n useradd --system --user-group --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin "$ACCOUNT"
# Mantener intacta la frontera privada de /opt/netlab360.
sudo -n install -d -o root -g "$ACCOUNT" -m 0750 "$PREFIX"
sudo -n install -d -o root -g root -m 0755 "$INSTALL" "$CONFIG"
sudo -n cp -a -- "$SOURCE/." "$INSTALL/"
sudo -n chown -hR root:root "$INSTALL"
sudo -n chmod -R a+rX,go-w "$INSTALL"
sudo -n cp -a servicios/observabilidad/grafana/. "$CONFIG/"
sudo -n chown -hR root:root "$CONFIG"
sudo -n chmod -R a+rX,go-w "$CONFIG"
sudo -n install -d -o "$ACCOUNT" -g "$ACCOUNT" -m 0700 "$STATE" "$STATE/data" "$STATE/logs" "$STATE/plugins"
sudo -n install -d -o root -g root -m 0700 "$SECRETS"
sudo -n /usr/bin/python3 -I -B - "$SECRETS" <<'PY'
from pathlib import Path
import os
import secrets
import sys
for name in ("admin-password", "secret-key"):
    path = Path(sys.argv[1]) / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.write(secrets.token_urlsafe(48))
PY
# Comprobar el acceso efectivo antes de iniciar el proceso sin privilegios.
sudo -n -u "$ACCOUNT" /bin/sh -c 'cd "$1"' sh "$INSTALL"
sudo -n -u "$ACCOUNT" test -x "$INSTALL/bin/grafana"
sudo -n -u "$ACCOUNT" test -r "$CONFIG/grafana.ini"
sudo -n -u "$ACCOUNT" test -r "$CONFIG/provisioning/dashboards/netlab360.yml"
sudo -n -u "$ACCOUNT" test -w "$STATE/data"
echo "RUTAS_GRAFANA_ACCESIBLES=OK"
sudo -n install -o root -g root -m 0644 "operacion/plantillas/$UNIT" "/run/systemd/system/$UNIT"
sudo -n systemd-analyze verify "/run/systemd/system/$UNIT"
sudo -n systemctl daemon-reload
STARTED=1
sudo -n systemctl start "$UNIT"
for _ in $(seq 1 90); do
    if curl --noproxy '*' -fsS http://127.0.0.1:3000/api/health > "$EVIDENCE/grafana-health.json" 2>/dev/null; then break; fi
    test "$(systemctl is-active "$UNIT")" = active
    sleep 1
done
test -s "$EVIDENCE/grafana-health.json"
test "$(systemctl is-active "$UNIT")" = active
PID="$(systemctl show "$UNIT" -p MainPID --value)"
sudo -n /usr/bin/python3 -I -B - "$PID" "$ACCOUNT" <<'PY'
import pwd
import sys
from pathlib import Path
account = pwd.getpwnam(sys.argv[2])
status = dict(line.split(":",1) for line in Path("/proc/"+sys.argv[1]+"/status").read_text().splitlines() if ":" in line)
assert account.pw_uid > 0
assert [int(v) for v in status["Uid"].split()] == [account.pw_uid]*4
assert [int(v) for v in status["Gid"].split()] == [account.pw_gid]*4
assert status["NoNewPrivs"].strip() == "1"
assert all(int(status[k].strip(),16)==0 for k in ("CapInh","CapPrm","CapEff","CapBnd","CapAmb"))
print("GRAFANA_IDENTIDAD_NO_PRIVILEGIADA=OK")
PY
test "$(ss -H -ltn 'sport = :3000' | awk '{print $4}')" = 127.0.0.1:3000
echo "GRAFANA_LOOPBACK=OK"

echo "========== 1015 CONTRASTAR FUENTE Y DASHBOARD =========="
sudo -v
sudo -n cat "$SECRETS/admin-password" |
    "$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python" -I -B \
    scripts/s08/contrastar_grafana.py "$EVIDENCE/grafana-contraste.json"
sudo -n -u netlab360-s08-api test ! -r "$SECRETS/admin-password"
sudo -n -u netlab360-s08-api test ! -r "$STATE/data/grafana.db"
echo "GRAFANA_SECRETOS_Y_DB_AISLADOS=OK"
ACCEPTED=1
echo "GRAFANA_LOCAL=OK"
