# NETLAB360 S05 — Lotes 144A–144C: diagnóstico HA HTTP antes del despliegue NOC

**Corte 15/11/2026. 143A, 143B y 143C están COMPLETADOS. NO REPETIR.**

Resultado real: 143A aprobó 21 tests del parser +14 topología +14 layout +6 HA/UI = **55/55**; la VM hizo pull a main 1fba8c5, gestión ens33 192.168.47.40/24 default 192.168.47.2 y Git limpio. 143B verificó los **seis bonds** HQ/S1/S2 2/2 en /proc/net/bonding aunque JSON informó ad_num_ports=None, alias 802.3ad correcto; Faucet/OVS owner válido, connected=true, 25 flows. FIB S1=s1p y S2=s2p. 143C verificó 4 tarjetas UI, node --check, servicios NOC/exporter active; los nuevos hashes quedaron guardados en 10_PreRollout_NOC_Panel_y_Hashes.txt.

**Anomalía:** La API NOC mostró snapshot HA con available=True pero status=offline, active_backend=None, selected_path=None a 2026-11-15T12:39:45+00:00 y source_warnings=[]. No afirmar que es solo visual ni que todo HA está apagado. El monitor HTTP de S2 prueba tres endpoints desde netns nl360-s02-h-s2-320. Diagnosticar antes de reiniciar NOC.

**Instalación:** No se reemplazó el ejecutable root:root 0755 /usr/local/libexec/netlab360-observer SHA antiguo 8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad; el código nuevo solo existe en GitHub. No crear sudoers, no modificar redes, FRR, Faucet, OVS, LACP ni reiniciar guest.

## 144A: 2 muestras NOC, fuente monitor S2 y servicios (pasos 854–859)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
{
echo "========== 854 GATES PREVIOS =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git log -1 --oneline
grep -Fxq '========== LOTE143A_PARSER_CORREGIDO=OK ==========' "$DIR/08_Precheck_Parser_Bond_Proc.txt"
grep -Fxq '========== LOTE143B_FUENTES_6_BONDS_OVS=OK ==========' "$DIR/09_Validacion_Real_Bonds_Proc_y_OVS.txt"
grep -Fxq '========== LOTE143C_PRE_ROLLOUT_NOC=OK ==========' "$DIR/10_PreRollout_NOC_Panel_y_Hashes.txt"

echo "========== 855 SEIS SERVICIOS =========="
for svc in netlab360-s04-exporter netlab360-s05-noc \
 netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 \
 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
 echo "$svc=$(systemctl is-active "$svc" || true)"
 systemctl show "$svc" -p MainPID -p ActiveState -p NRestarts
done

echo "========== 856 DOS MUESTRAS API =========="
python3 - <<'PY'
import json,time
from urllib.request import urlopen
for i in (1,2):
 with urlopen("http://127.0.0.1:9130/api/v1/graph",timeout=10) as f:
  d=json.load(f)
 ha=d.get("ha_service") or {}
 print("MUESTRA",i,"HA=",ha,"WARNINGS=",d.get("source_warnings"))
 print("MUESTRA",i,"FIB=",d.get("routing"))
 if i==1: time.sleep(4)
PY

echo "========== 857 OBSERVACION RAW HA S2 =========="
python3 - <<'PY'
from pathlib import Path
from datetime import datetime,timezone
import json
p=Path.home()/"netlab360-bootstrap/s05/ha/observacion-http-s2.json"
print("SOURCE_FILE_EXISTS=",p.is_file(),"SYMLINK=",p.is_symlink())
if p.is_file() and not p.is_symlink():
 d=json.loads(p.read_text())
 print("OWNER=",d.get("owner"),"SOURCE=",d.get("source_netns"))
 stamp=d.get("observed_at_utc")
 print("SAMPLE_UTC=",stamp)
 try: print("AGE_SECONDS=",round((datetime.now(timezone.utc)-datetime.fromisoformat(stamp)).total_seconds(),2))
 except (ValueError,TypeError): print("AGE_SECONDS=UNKNOWN")
 for role,row in (d.get("services") or {}).items():
  print(role,"STATUS=",row.get("status"),"BACKEND=",row.get("active_backend"),"PATH=",row.get("selected_path"))
PY

echo "========== 858 GESTION =========="
date -Is
ip -4 -br address show ens33
ip -4 route show default
echo "========== 859 GIT =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE144A_DIAGNOSTICO_HA=COMPLETADO =========="
} 2>&1 | tee "$DIR/11_Diagnostico_HA_Muestras_S2.txt"
BASH
~~~

## 144B: HTTP desde el cliente S2 + logs del monitor (pasos 860–865)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
grep -Fxq '========== LOTE144A_DIAGNOSTICO_HA=COMPLETADO ==========' "$DIR/11_Diagnostico_HA_Muestras_S2.txt"
{
echo "========== 860 IDENTIDAD ORIGEN S2 =========="
sudo -n ip -n nl360-s02-h-s2-320 -4 -br address show
sudo -n ip -n nl360-s02-h-s2-320 -4 route show
echo "========== 861 SONDEOS HTTP BACKENDS Y FRONTAL =========="
for url in \
 http://10.70.20.21:8088/api/v1/service \
 http://10.71.20.21:8088/api/v1/service \
 http://10.70.20.23:8080/api/v1/service; do
 echo "---- URL $url ----"
 if sudo -n ip netns exec nl360-s02-h-s2-320 /usr/bin/curl \
  --noproxy '*' --connect-timeout 2 --max-time 5 -sS -i "$url"; then
  echo "CURL=COMPLETADO_REVISAR_HTTP_STATUS_Y_JSON"
 else
  echo "CURL=ERROR_TRANSPORTE_O_COMANDO"
 fi
done
echo "========== 862 ESTADO SERVICIOS HA =========="
for svc in netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 \
 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
 echo "$svc=$(systemctl is-active "$svc" || true)"
 systemctl show "$svc" -p MainPID -p ExecMainStatus -p NRestarts
done
echo "========== 863 LOGS MONITOR =========="
journalctl -u netlab360-s05-ha-monitor-s2 --since '-20 minutes' -n 35 --no-pager || true
echo "========== 864 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== 865 GIT =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE144B_HTTP_S2=COMPLETADO =========="
} 2>&1 | tee "$DIR/12_Diagnostico_HTTP_Desde_S2.txt"
BASH
~~~

HTTP 503 puede dar curl RC0 sin --fail. Leer el código HTTP y el JSON. No reiniciar ni empezar otro failover.

## 144C: conservar ejecutable root legacy y contrato FIB (866–871)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
grep -Fxq '========== LOTE144B_HTTP_S2=COMPLETADO ==========' "$DIR/12_Diagnostico_HTTP_Desde_S2.txt"
{
echo "========== 866 HELPER LEGACY =========="
H=/usr/local/libexec/netlab360-observer
test -f "$H" && test ! -L "$H"
stat -c '%U:%G %a %n' "$H"
test "$(sha256sum "$H" | awk '{print $1}')" = 8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad
echo "========== 867 SNAPSHOT SUDOERS LEGACY =========="
python3 - <<'PY'
import json,subprocess
p=subprocess.run(["sudo","-n","/usr/local/libexec/netlab360-observer","snapshot"],capture_output=True,text=True,timeout=18)
print("OBSERVADOR_RC=",p.returncode)
if p.returncode: print("OBSERVADOR_ERROR=",p.stderr[:300])
else:
 d=json.loads(p.stdout)
 print("OWNER=",d.get("owner"),"ROUTERS=",sorted((d.get("routers") or {}).keys()))
 print("FIB=",d.get("routes"))
 print("LACP=",d.get("lacp","SIN_INSTALAR"),"SDN=",d.get("sdn","SIN_INSTALAR"))
PY
echo "========== 868 HASH VERSION NUEVA =========="
sha256sum scripts/operacion/s05-observador-privilegiado.py \
 servicios/topologia-s05/app.py servicios/topologia-s05/index.html
echo "========== 869 SYSTEMD SIN REINICIAR =========="
systemctl show netlab360-s05-noc -p MainPID -p User -p ActiveState
systemctl cat netlab360-s05-noc
echo "========== 870 RED =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== 871 GIT =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE144C_BASELINE_PRE_ROLLOUT=COMPLETADO =========="
} 2>&1 | tee "$DIR/13_Baseline_Helper_Legacy_PreRollout.txt"
BASH
~~~

Estos tres lotes son de SÓLO LECTURA. COMPLETADO no significa HA sano; no solicitar capturas todavía. Si HA permanece offline, diagnosticar su causa antes de reemplazar helper y reiniciar NOC. Después, previa validación, realizar backup SHA256 root:root 0755 del binario legacy, staging root seguro, probar snapshot FRR/FIB+LACP+SDN y reiniciar SOLO netlab360-s05-noc con reversión. Mantener SSH/ens33 y namespaces. Pendientes #64 NOC, #32 HA instancia, #31 P1/P1B, #105 PNG; S06, S07 y S08.
