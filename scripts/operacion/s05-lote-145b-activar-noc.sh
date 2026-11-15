#!/usr/bin/env bash
# NETLAB360 S05: procedimiento versionado, ejecutar como usuario rc-aa-ec.
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
grep -Fxq '========== LOTE145A_HELPER_ROOT_NOC=OK ==========' \
 "$DIR/14_Instalacion_Atomica_Observador_NOC.txt"

(
set -Eeuo pipefail
BIN=/usr/local/libexec/netlab360-observer
BACKUP=/var/backups/netlab360/s05-observer-legacy-20261115
NEW_SHA=ba2a87081cf8537dcd388bb86a8e2437679aea4a079411094948695b252ef54f
OLD_SHA=8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad
RESTARTED=0
ACCEPTED=0
rollback() {
 if [ "$RESTARTED" = 1 ] && [ "$ACCEPTED" = 0 ]; then
  echo "========== ROLLBACK_NOC_SOLO_SERVICIO =========="
  if test "$(sudo -n sha256sum "$BACKUP" | awk '{print $1}')" = "$OLD_SHA"; then
   sudo -n install -o root -g root -m 0755 "$BACKUP" "$BIN" || true
   sudo -n systemctl restart netlab360-s05-noc || true
  fi
 fi
}
trap rollback EXIT

echo "========== 880 HELPER NUEVO =========="
test "$(sudo -n sha256sum "$BIN" | awk '{print $1}')" = "$NEW_SHA"
test "$(sudo -n sha256sum "$BACKUP" | awk '{print $1}')" = "$OLD_SHA"
test "$(systemctl is-active netlab360-s05-noc)" = active
test "$(systemctl is-active netlab360-s04-exporter)" = active

echo "========== 881 RESTART SOLO NOC =========="
RESTARTED=1
sudo -n systemctl restart netlab360-s05-noc

echo "========== 882 ENDPOINT HEALTH =========="
for n in 1 2 3 4 5 6 7 8; do
 if curl --noproxy '*' -fsS --connect-timeout 1 --max-time 3 \
  http://127.0.0.1:9130/healthz >/dev/null; then break; fi
 sleep 1
done
curl --noproxy '*' -fsS --max-time 6 http://127.0.0.1:9130/healthz

echo "========== 883 DOS MUESTRAS REALES =========="
python3 - <<'PY'
import json,time
from urllib.request import urlopen
ok_http=0
for i in (1,2):
 with urlopen("http://127.0.0.1:9130/api/v1/graph",timeout=16) as f:
  d=json.load(f)
 print("MUESTRA",i,"NODOS=",len(d.get("nodes",[])),"ENLACES=",len(d.get("links",[])))
 print("HORA_VM=",d.get("vm_clock"))
 print("FIB=",d.get("routing"))
 print("HA=",d.get("ha_service"))
 print("LACP=",d.get("lacp"))
 print("SDN=",d.get("sdn"))
 print("WARNINGS=",d.get("source_warnings"))
 assert len(d.get("nodes",[]))==18
 assert len(d.get("links",[]))==21
 assert d["routing"]["available"] is True
 assert d["routing"]["routes"]["S1"]["dev"]=="s1p"
 assert d["routing"]["routes"]["S2"]["dev"]=="s2p"
 assert d["lacp"]["available"] is True
 for site in ("HQ","S1","S2"):
  row=d["lacp"]["sites"][site]
  assert (row["status"],row["switch_members"],row["client_members"])==("up",2,2)
 assert d["sdn"]["available"] is True
 assert d["sdn"]["status"]=="connected"
 assert type(d["sdn"]["flow_count"]) is int and d["sdn"]["flow_count"]>0
 assert not d["source_warnings"],d["source_warnings"]
 if (d.get("ha_service") or {}).get("status")=="running" and \
    (d.get("ha_service") or {}).get("active_backend")=="BACKEND_HQ":
  ok_http+=1
 if i==1: time.sleep(4)
print("HA_HTTP_MUESTRAS_HQ_RUNNING=",ok_http,"DE_2")
if not ok_http:
 print("HA_HTTP_INESTABLE_PENDIENTE_NO_FABRICAR_SALUD")
print("S05_NOC_DOS_MUESTRAS_LACP_SDN=OK")
PY

echo "========== 884 HTML CUATRO TARJETAS =========="
python3 - <<'PY'
from urllib.request import urlopen
with urlopen("http://127.0.0.1:9130/",timeout=8) as f:
 html=f.read().decode("utf-8")
for text in ("obs-hq-state","obs-s1-state","obs-s2-state",
             "obs-sdn-state","formatPanamaStamp","renderObservedSources"):
 assert text in html
print("NOC_HTML_PANAMA_LACP_SDN=OK")
PY

echo "========== 885 SEIS SERVICIOS =========="
for svc in netlab360-s04-exporter netlab360-s05-noc \
 netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 \
 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
 test "$(systemctl is-active "$svc")" = active
 echo "$svc=active"
done

echo "========== 886 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
ip -4 -br address show ens33 | grep -Fq 192.168.47.40/24
ip -4 route show default | grep -Fq 'via 192.168.47.2 dev ens33'

echo "========== 887 GIT =========="
test -z "$(git status --porcelain)"
git status --short --branch

echo "========== 888 ACEPTACION =========="
ACCEPTED=1
echo "========== LOTE145B_NOC_LACP_SDN=OK =========="
) 2>&1 | tee "$DIR/15_Rollout_NOC_LACP_SDN_2Muestras.txt"
BASH
