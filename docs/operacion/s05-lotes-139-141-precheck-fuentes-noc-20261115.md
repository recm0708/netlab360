# NETLAB360 · S05 · Lotes 139–141: precheck para telemetría NOC real (15/11/2026)

## Corte comprobado (NO hay que repetir pruebas dinámicas)

- 136: SDN OpenFlow conectado, VLAN410 A/B permitida, VLAN420 C aislada, ens33 .40/24 GW .2 y Git limpios, 7/7 TXT verificados SHA256.
- 137A: 9/9 tests de seguridad, precheck puerto sdna0, Faucet y servicios existentes OK.
- 137B: falla exclusivamente sdna0, A→B 10/0, RC1; OpenFlow siguió conectado y gestión/FRR/NOC/HA no se tocaron. sdna0 restaurado, comunicación A↔B devuelta al primer intento; watchdog restore-only cancelado. Usuario afirma capturas 61 y 62 tomadas. PNG aún sin auditoría de bytes.
- 138: tres LACP HQ/S1/S2 2/2, 4 pings por sede, FRR OSPF principal S1=s1p, S2=s2p, 6 servicios active; ens33 .40/24 y GW .2, 3/3 TXT SHA256 correctos. LOTE138_REGRESION_FALLA_SDN=OK.

## Objetivo NOC próximo

Antes de integrar en el dashboard 9130 el estado LACP y Faucet, debemos identificar las fuentes de lectura que realmente están disponibles al usuario de systemd. El dashboard se ejecuta como rc-aa-ec (sin root), con observador privilegiado instalado por separado, ya autorizado por sudoers para su acción snapshot existente. No conceder root adicional, ni pedir contraseña en HTTP, ni cambiar systemd/VM/FRR/OVS. La telemetría debe distinguir estado UNKNOWN por fuente ausente/caducada, enlaces LACP 2/2 o 1/1 observados, y Faucet controlador conectado/desconectado, sin pintar disponibilidad a partir de un JSON state=active.

### Lote 139A — servicios NOC y API reales, pasos 796–801 (SOLO LECTURA)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
mkdir -p "$DIR"
sudo -v
{
echo "========== 796 GIT ACTUAL =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git log -1 --oneline

echo "========== 797 SERVICIOS NOC =========="
for svc in netlab360-s04-exporter netlab360-s05-noc \
 netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 \
 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
 echo "$svc=$(systemctl is-active "$svc" || true)"
done
systemctl show netlab360-s05-noc -p MainPID -p User -p ExecMainStatus -p ActiveState
systemctl show netlab360-s04-exporter -p MainPID -p ActiveState

echo "========== 798 SOCKETS LOCALES =========="
sudo -n ss -ltnp | grep -E ':(9110|9130)([[:space:]]|$)' || true

echo "========== 799 DOS MUESTRAS API CON CADUCIDAD =========="
python3 - <<'PY'
import json, time
from urllib.request import urlopen
for n in (1,2):
 print(f"========== API_MUESTRA_{n} ==========")
 for name,url in (
  ("NOC_GRAPH","http://127.0.0.1:9130/api/v1/graph"),
  ("EXPORTER","http://127.0.0.1:9110/api/v1/state")):
  try:
   with urlopen(url,timeout=6) as response:
    d=json.load(response)
   if name=="NOC_GRAPH":
    print("NOC_PROJECT=",d.get("project"),"PHASE=",d.get("phase"))
    print("NOC_CLOCK=",d.get("vm_clock"))
    print("NOC_TELEMETRY=",d.get("telemetry"))
    print("NOC_ROUTING=",d.get("routing"))
    print("NOC_HA=",d.get("ha_service"))
    print("NOC_WARNINGS=",d.get("source_warnings"))
    print("NOC_COUNTS=",d.get("counts"))
   else:
    print("EXPORTER_SOURCE_OK=",d.get("source_ok"),
          "TOPOLOGY=",d.get("topology"),
          "STAMP=",d.get("observed_at_utc"))
  except Exception as exc:
   print(f"{name}_ERROR={type(exc).__name__}: {exc}")
 if n==1:
  time.sleep(4)
PY

echo "========== 800 HEALTH ENDPOINT =========="
curl --noproxy '*' -fsS --connect-timeout 3 --max-time 6 \
 http://127.0.0.1:9130/healthz

echo
echo "========== 801 GESTION Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE139A_AUDITORIA_NOC=COMPLETADA =========="
} 2>&1 | tee "$DIR/01_Auditoria_Servicios_y_API_NOC.txt"
BASH
~~~

El marcador AUDITORIA_NOC=COMPLETADA únicamente indica consultas ejecutadas. No acredita disponibilidad de cada fuente si las advertencias dicen UNKNOWN. Si SSH se desconecta, no repetir cambios: no hay modificaciones a la red.

### Lote 139B — permisos y contrato del observador privilegiado, pasos 802–807 (SOLO LECTURA)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
HELPER="/usr/local/libexec/netlab360-observer"
sudo -v
{
echo "========== 802 ARCHIVOS Y PROPIEDAD =========="
test -f scripts/operacion/s05-observador-privilegiado.py
test -f "$HELPER"
stat -c '%U:%G %a %s %n' scripts/operacion/s05-observador-privilegiado.py
stat -c '%U:%G %a %s %n' "$HELPER"
sha256sum scripts/operacion/s05-observador-privilegiado.py "$HELPER"

echo "========== 803 LLAMADA AUTORIZADA SNAPSHOT =========="
python3 - <<'PY'
import json,subprocess
cmd=["sudo","-n","/usr/local/libexec/netlab360-observer","snapshot"]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=18)
print("OBSERVADOR_RC=",p.returncode)
if p.returncode:
 print("OBSERVADOR_ERROR=",p.stderr[:400])
else:
 d=json.loads(p.stdout)
 print("OBSERVADOR_PROJECT=",d.get("project"))
 print("OBSERVADOR_OWNER=",d.get("owner"))
 print("OBSERVADOR_ROUTERS=",sorted((d.get("routers") or {}).keys()))
 print("OBSERVADOR_FIB=",d.get("routes"))
 print("OBSERVADOR_OTRAS_FUENTES=",sorted(
  set(d)-{"project","owner","routers","routes"}))
PY

echo "========== 804 CONFIG SYSTEMD SIN CAMBIOS =========="
systemctl cat netlab360-s05-noc
echo "========== 805 PROCESO ACTIVO =========="
ps -eo pid,user,cmd | grep -E '[t]opologia-s05/app.py|[s]05-observador' || true

echo "========== 806 CONSULTA RAW A SCRIPT SIN PRIVILEGIOS =========="
python3 servicios/topologia-s05/app.py --check

echo "========== 807 VERSION Y GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE139B_OBSERVADOR_AUDITADO=COMPLETADO =========="
} 2>&1 | tee "$DIR/02_Auditoria_Observador_Privilegiado.txt"
BASH
~~~

No instalar ni sobrescribir el HELPER ni editar sudoers hasta validar esos resultados y diseñar la compatibilidad del contrato FIB existente. Evitar revelar identificadores internos del contenedor en imágenes de clase, si no aportan valor.

### Lote 140 — fuentes de enlaces físicos virtuales LACP y controlador OVS, pasos 808–813 (SOLO LECTURA)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
{
echo "========== 808 ESTADO LACP MULTISEDE =========="
for sede in hq s1 s2; do
 python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status
done

echo "========== 809 RAW BONDS SWITCH Y CLIENTE =========="
for sede in hq s1 s2; do
 echo "========== SEDE $sede SWITCH s5bond0 =========="
 sudo -n ip -n "nl360-s02-sw-$sede" -d link show dev s5bond0
 echo "========== SEDE $sede CLIENTE bond0 =========="
 sudo -n ip -n "nl360-s05-lacp-$sede" -d link show dev bond0
done

echo "========== 810 FAUCET Y OPENFLOW =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py inspect
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py status
sudo -n ovs-vsctl --timeout=12 --format=table \
 --columns=target,is_connected,status list Controller

echo "========== 811 ESTADO DE PUERTOS SDN =========="
sudo -n ovs-vsctl --timeout=12 show
sudo -n ovs-ofctl -O OpenFlow13 show br-s05-sdn | sed -n '1,24p'

echo "========== 812 IDENTIDAD CONFIG OPERATIVA =========="
python3 - <<'PY'
from pathlib import Path
import json
home=Path.home()
for site in ("hq","s1","s2"):
 f=home/f"netlab360-bootstrap/s05/lacp-multisede/state-{site}.json"
 d=json.loads(f.read_text())
 print(site,"OWNER=",d.get("owner"),"STATUS=",d.get("status"))
p=home/"netlab360-bootstrap/s05/sdn-faucet/state-sdn.json"
d=json.loads(p.read_text())
print("SDN_OWNER=",d.get("owner"),"STATUS=",d.get("status"))
PY

echo "========== 813 RED HOST Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE140_FUENTES_LACP_SDN=COMPLETADO =========="
} 2>&1 | tee "$DIR/03_Auditoria_Fuentes_LACP_y_SDN.txt"
BASH
~~~

Sin capturas obligatorias todavía. Los datos de un instante no bastan para declarar disponibilidad continua; la siguiente integración debe muestrear con caducidad y devolver UNKNOWN al perder observador, namespace, OVS o marcas de propiedad.

### Lote 141 — pruebas offline de contrato UI y protección de artefactos, pasos 814–819

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
{
echo "========== 814 VERSION UI =========="
git log -1 --oneline
echo "========== 815 REGRESION API GRAFO =========="
python3 -m unittest discover -s tests -p 'test_s05_topologia.py' -v
echo "========== 816 REGRESION VISUAL =========="
python3 -m unittest discover -s tests -p 'test_s05_ha_noc_ciclo.py' -v
echo "========== 817 INTEGRIDAD ESTATICA =========="
sha256sum servicios/topologia-s05/app.py \
 servicios/topologia-s05/index.html \
 scripts/operacion/s05-observador-privilegiado.py \
 inventario/topologia-extensiones-s05.json
echo "========== 818 API ACTUAL (SOLO LECTURA) =========="
python3 - <<'PY'
import json
from urllib.request import urlopen
with urlopen("http://127.0.0.1:9130/api/v1/graph",timeout=8) as r:
 d=json.load(r)
print("GRAPH_SCHEMA=",d.get("schema_version"))
print("GRAPH_NODES=",len(d.get("nodes",[])))
print("GRAPH_LINKS=",len(d.get("links",[])))
print("NOC_SOURCE_WARNINGS=",d.get("source_warnings",[]))
print("GRAPH_LACP_FUENTE=",d.get("lacp", "AUN_NO_INTEGRADA"))
print("GRAPH_SDN_FUENTE=",d.get("sdn", "AUN_NO_INTEGRADA"))
PY
echo "========== 819 GIT LIMPIO =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE141_CONTRATOS_NOC=COMPLETADO =========="
} 2>&1 | tee "$DIR/04_Pruebas_Contrato_NOC_PreIntegracion.txt"
BASH
~~~

Con estos datos se creará una extensión NOC que preserve el grafo actual, la FIB real, las horas Panama y el HA HTTP. No se crearán nuevas redes ni se reiniciarán servicios durante los prechecks. Después se desplegará primero backend con pruebas offline, se inspeccionará respuesta JSON con UNKNOWN correcto, y solo entonces se incorporarán gráficos/controles para LACP y Faucet. No cerrar #64 hasta pruebas visuales en navegador y capturas.
