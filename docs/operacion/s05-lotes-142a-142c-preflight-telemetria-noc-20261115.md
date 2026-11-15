# NETLAB360 S05 — Lotes 142A–142C: precheck para observaciones LACP/SDN en NOC

> **ADVERTENCIA DE CONTINUIDAD (15/11/2026):** 142A aprobó 49/49 pruebas, 142B falló DOS veces en paso 826 (iproute2 omite ad_num_ports en JSON; aparece None) y 142C no se ejecutó. **NO ejecutar de nuevo el 142B de este documento ni el 142C sin la nueva validación.** Conservar el TXT 06 original fallido. Seguir [lotes 143A–143C corregidos](s05-lotes-143a-143c-reparacion-parser-y-continuidad-20261115.md), que verifican seis bonds con /proc/net/bonding antes de instalar cualquier observador. [Corte maestro](../gestion/CORTE-MAESTRO-NETLAB360-S05-142B-20261115.md).

Corte real (15/11/2026): 139A NOC 9130 y exporter 9110 activos y dos muestras actualizadas, FIB S1=s1p S2=s2p, backend HTTP HQ principal, sin warnings. 139B helper privilegiado raíz root:root 0755, SHA igual al repositorio, snapshot FRR/FIB RC0. Lote 140 LACP HQ/S1/S2 2/2 en ambos extremos y Faucet/OVS OpenFlow conectado, estado S05 propio. Lote 141 14+4 tests OK, grafo 18 nodos/21 enlaces, sin campos LACP ni SDN.

PR de implementación: observador autorizado amplía su única acción snapshot con lectura de seis bonds Linux 802.3ad y OVS/Faucet; el API NOC exige propietario y marca UTC fresca y representa UNKNOWN si faltan datos. UI tiene cuatro tarjetas fuera del SVG, manteniendo el mismo formato de hora Panama. Esta PR no ejecuta cambios en la VM: primero verificar JSON real y el helper antes de instalar root.

## Lote 142A — código, regresiones y estado previo (820–825), SOLO LECTURA

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
mkdir -p "$DIR"
sudo -v
{
echo "========== 820 VERSION Y GATES HISTORICOS =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git log -1 --oneline
for f in "$DIR"/0{1,2,3,4}_*.txt; do test -s "$f"; done

echo "========== 821 SINTAXIS NUEVOS COMPONENTES =========="
python3 -m py_compile \
 scripts/operacion/s05-observador-privilegiado.py \
 servicios/topologia-s05/app.py tests/test_s05_noc_lacp_sdn_telemetria.py

echo "========== 822 PRUEBAS NUEVAS =========="
python3 -m unittest discover -s tests \
 -p 'test_s05_noc_lacp_sdn_telemetria.py' -v

echo "========== 823 REGRESIONES EXISTENTES =========="
for p in test_s05_topologia.py test_s05_layout.py test_s05_ha_ui.py; do
 python3 -m unittest discover -s tests -p "$p" -v
done

echo "========== 824 OBSERVADOR ACTUAL INSTALADO =========="
OBS=/usr/local/libexec/netlab360-observer
test -f "$OBS"
test ! -L "$OBS"
stat -c '%U:%G %a %n' "$OBS"
ACTUAL="$(sha256sum "$OBS" | awk '{print $1}')"
echo "SHA_INSTALADO=$ACTUAL"
echo "SHA_NUEVO=$(sha256sum scripts/operacion/s05-observador-privilegiado.py | awk '{print $1}')"
test "$ACTUAL" = '8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad'
echo "OBSERVADOR_ANTERIOR=INTEGRO_Y_RESTAURABLE"

echo "========== 825 GESTION Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE142A_CODIGO_Y_BASELINE=OK =========="
} 2>&1 | tee "$DIR/05_Precheck_Codigo_Observabilidad_NOC.txt"
BASH
~~~

## Lote 142B — inspeccionar JSON real de los seis bonds y OVS (826–830), SOLO LECTURA

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
grep -Fxq '========== LOTE142A_CODIGO_Y_BASELINE=OK ==========' \
 "$DIR/05_Precheck_Codigo_Observabilidad_NOC.txt"
{
echo "========== 826 JSON LACP DE LAS TRES SEDES =========="
python3 - <<'PY'
import json, subprocess
from pathlib import Path
h=Path.home()
for site in ("hq","s1","s2"):
 p=h/f"netlab360-bootstrap/s05/lacp-multisede/state-{site}.json"
 state=json.loads(p.read_text())
 for side,ns,bond in (
  ("SW",f"nl360-s02-sw-{site}","s5bond0"),
  ("CLIENT",f"nl360-s05-lacp-{site}","bond0")):
  result=subprocess.run(["sudo","-n","ip","-n",ns,"-j","-d",
                         "link","show","dev",bond],
    capture_output=True,text=True,timeout=8,check=True)
  rows=json.loads(result.stdout)
  assert isinstance(rows,list) and len(rows)==1
  row=rows[0]; info=row.get("linkinfo") or {}
  data=info.get("info_data") or {}
  alias=row.get("ifalias"); members=data.get("ad_num_ports")
  mode=str(data.get("mode")); flags=row.get("flags",[])
  print(f"{site.upper()}_{side}: ALIAS={alias} "
        f"MODE={mode} PORTS={members} FLAGS={','.join(flags)}")
  assert alias==state["alias"]
  assert info.get("info_kind")=="bond" and mode=="802.3ad"
  assert type(members) is int and members==2
  assert "UP" in flags and "LOWER_UP" in flags
print("LACP_RAW_JSON=6_DE_6_OK")
PY

echo "========== 827 OVS CONTROLLER =========="
sudo -n ovs-vsctl --timeout=3 \
 get Bridge br-s05-sdn external_ids:netlab360-owner
sudo -n ovs-vsctl --timeout=3 list-ports br-s05-sdn
sudo -n ovs-vsctl --timeout=3 --format=csv --data=bare \
 --no-heading --columns=is_connected list Controller

echo "========== 828 DOCKER Y FLUJOS =========="
sudo -n docker inspect nl360-s05-faucet \
 --format 'RUNNING={{.State.Running}} OWNER={{index .Config.Labels "netlab360.owner"}}'
sudo -n ovs-ofctl -O OpenFlow13 dump-flows br-s05-sdn |
 awk 'index($0,"cookie=")&&index($0,"actions="){n++}
 END{print "OPENFLOW_FLOWS="n;exit(n>0?0:1)}'

echo "========== 829 API NOC ORIGINAL =========="
python3 - <<'PY'
import json
from urllib.request import urlopen
with urlopen("http://127.0.0.1:9130/api/v1/graph",timeout=8) as r:
 d=json.load(r)
print("WARNINGS=",d.get("source_warnings"))
print("FIB=",d.get("routing"))
print("HA_HTTP=",d.get("ha_service"))
PY

echo "========== 830 GESTION Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE142B_JSON_Y_OVS=OK =========="
} 2>&1 | tee "$DIR/06_Precheck_Raw_Bonds_OVS_Observador.txt"
BASH
~~~

Si la lectura JSON difiere de las claves ifalias, linkinfo.info_kind, info_data.mode o info_data.ad_num_ports, NO instalar el observador: revisaremos primero el parser contra la salida real.

## Lote 142C — UI, sintaxis JS e integridad previa al despliegue (831–835), SOLO LECTURA

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
grep -Fxq '========== LOTE142B_JSON_Y_OVS=OK ==========' \
 "$DIR/06_Precheck_Raw_Bonds_OVS_Observador.txt"
{
echo "========== 831 PANEL WEB =========="
python3 - <<'PY'
from pathlib import Path
s=Path("servicios/topologia-s05/index.html").read_text()
needed=("obs-hq-state","obs-s1-state","obs-s2-state",
 "obs-sdn-state","formatPanamaStamp","renderObservedSources")
assert all(x in s for x in needed)
assert s.count('<svg id="network"')==1
print("UI=4_TARJETAS_FUERA_DEL_SVG_PANAMA")
PY

echo "========== 832 JS =========="
python3 - <<'PY' | node --check
import re
from pathlib import Path
p=Path("servicios/topologia-s05/index.html").read_text()
blocks=re.findall(r"<script>([\s\S]*?)</script>",p)
assert len(blocks)==1
print(blocks[0])
PY

echo "========== 833 HASHES DE VERSIONES =========="
sha256sum scripts/operacion/s05-observador-privilegiado.py \
 servicios/topologia-s05/app.py servicios/topologia-s05/index.html
sha256sum /usr/local/libexec/netlab360-observer

echo "========== 834 SERVICIOS Y HOST =========="
systemctl is-active netlab360-s05-noc netlab360-s04-exporter
ip -4 -br address show ens33
ip -4 route show default

echo "========== 835 GIT LIMPIO =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE142C_PREPARACION_ROLLOUT=OK =========="
} 2>&1 | tee "$DIR/07_Precheck_UI_Observador_y_Rollback.txt"
BASH
~~~

Estos tres lotes NO reinician el NOC, no tocan sudoers, no ejecutan la nueva versión como root ni cambian configuración. Tras analizar la salida, el siguiente bloque hará instalación atómica de root:root con copia de retorno, validación de FIB/LACP/SDN y reinicio exclusivamente del NOC 9130. No hay captura nueva obligatoria hasta aprobar el panel web con datos vivos y hora de Panamá.
