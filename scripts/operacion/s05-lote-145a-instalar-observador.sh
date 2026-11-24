#!/usr/bin/env bash
# NETLAB360 S05: instalación del observador privilegiado de solo lectura.
# Verifica la copia, propietario, permisos y acceso autorizado antes de integrar el NOC.
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v

(
set -Eeuo pipefail
OLD_SHA=8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad
NEW_SHA=ba2a87081cf8537dcd388bb86a8e2437679aea4a079411094948695b252ef54f
BIN=/usr/local/libexec/netlab360-observer
SRC="$PWD/scripts/operacion/s05_observador_privilegiado.py"
BACKUP=/var/backups/netlab360/s05-observer-legacy-20261115
STAGE=/usr/local/libexec/.netlab360-observer-stage-145
MUTATED=0
ACCEPTED=0
rollback() {
 if [ "$MUTATED" = 1 ] && [ "$ACCEPTED" = 0 ]; then
  echo "========== ROLLBACK_HELPER_LEGACY =========="
  sudo -n install -o root -g root -m 0755 "$BACKUP" "$BIN" || true
 fi
}
trap rollback EXIT

echo "========== 872 GIT GATES =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
for row in \
 "144A_DIAGNOSTICO_HA|11_Diagnostico_HA_Muestras_S2.txt" \
 "144B_HTTP_S2|12_Diagnostico_HTTP_Desde_S2.txt" \
 "144C_BASELINE_PRE_ROLLOUT|13_Baseline_Helper_Legacy_PreRollout.txt"; do
 mark="$(printf '%s' "$row" | cut -d'|' -f1)"
 file="$(printf '%s' "$row" | cut -d'|' -f2)"
 grep -Fxq "========== LOTE$mark=COMPLETADO ==========" "$DIR/$file"
done

echo "========== 873 IDENTIDAD Y SHA =========="
test -f "$BIN" && test ! -L "$BIN"
test -f "$SRC" && test ! -L "$SRC"
test "$(sudo -n sha256sum "$BIN" | awk '{print $1}')" = "$OLD_SHA"
test "$(sha256sum "$SRC" | awk '{print $1}')" = "$NEW_SHA"
test "$(stat -c '%U:%G:%a' "$BIN")" = root:root:755

echo "========== 874 BACKUP ROOT UNICO =========="
sudo -n install -d -o root -g root -m 0700 /var/backups/netlab360
if sudo -n test -e "$BACKUP"; then
 test "$(sudo -n sha256sum "$BACKUP" | awk '{print $1}')" = "$OLD_SHA"
else
 sudo -n install -o root -g root -m 0700 "$BIN" "$BACKUP"
fi
test "$(sudo -n sha256sum "$BACKUP" | awk '{print $1}')" = "$OLD_SHA"
echo "BACKUP_ROOT_LEGACY=SHA_OK"

echo "========== 875 STAGING Y REEMPLAZO ATOMICO =========="
sudo -n install -o root -g root -m 0755 "$SRC" "$STAGE"
test "$(sudo -n sha256sum "$STAGE" | awk '{print $1}')" = "$NEW_SHA"
MUTATED=1
sudo -n mv -f -T "$STAGE" "$BIN"
test "$(sudo -n sha256sum "$BIN" | awk '{print $1}')" = "$NEW_SHA"
test "$(stat -c '%U:%G:%a' "$BIN")" = root:root:755

echo "========== 876 SNAPSHOT REAL FRR FIB LACP SDN =========="
python3 - <<'PY'
import json,subprocess
from datetime import datetime,timezone
p=subprocess.run(
 ["sudo","-n","/usr/local/libexec/netlab360-observer","snapshot"],
 capture_output=True,text=True,timeout=28)
print("OBSERVADOR_RC=",p.returncode)
if p.returncode:
 print("OBSERVADOR_ERROR=",p.stderr[-500:])
 raise RuntimeError("Helper nuevo rechazado o sin respuesta")
data=json.loads(p.stdout)
assert data.get("owner")=="NETLAB360_S02_WAN_LINKS_V1"
assert set(data["routers"])=={"R-HQ","R-S1","R-S2"}
assert data["routes"]["S1"]["dev"]=="s1p"
assert data["routes"]["S2"]["dev"]=="s2p"
lacp=data["lacp"]; sdn=data["sdn"]
assert lacp["available"] is True
for site in ("HQ","S1","S2"):
 row=lacp["sites"][site]
 print("BOND",site,row)
 assert (row["status"],row["switch_members"],row["client_members"])==("up",2,2)
print("SDN",sdn)
assert sdn["available"] is True and sdn["connected"] is True
assert sdn["status"]=="connected"
assert type(sdn["flow_count"]) is int and sdn["flow_count"]>0
for label,obs in (("LACP",lacp),("SDN",sdn)):
 age=(datetime.now(timezone.utc)-datetime.fromisoformat(
  obs["observed_at_utc"])).total_seconds()
 print(label,"AGE_SECONDS=",round(age,2))
 assert -2<=age<=25
print("ROOT_HELPER=OK_FIB_LACP_SDN")
PY

echo "========== 877 NOC AUN SIN REINICIAR =========="
test "$(systemctl is-active netlab360-s05-noc)" = active
test "$(systemctl is-active netlab360-s04-exporter)" = active

echo "========== 878 RED Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
ip -4 -br address show ens33 | grep -Fq 192.168.47.40/24
ip -4 route show default | grep -Fq 'via 192.168.47.2 dev ens33'
test -z "$(git status --porcelain)"
git status --short --branch

echo "========== 879 ACEPTACION =========="
ACCEPTED=1
echo "========== LOTE145A_HELPER_ROOT_NOC=OK =========="
) 2>&1 | tee "$DIR/14_Instalacion_Atomica_Observador_NOC.txt"
BASH
