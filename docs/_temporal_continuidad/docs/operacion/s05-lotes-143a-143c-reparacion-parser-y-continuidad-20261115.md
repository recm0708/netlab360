# NETLAB360 — Continuidad S05 al 15-11-2026: fallo 142B y reparación /proc

**ESTE ES EL PUNTO DE REANUDACIÓN VIGENTE.** La bitácora 142A–142C anterior es histórica y su bloque 142B original NO debe repetirse.

## Situación exacta

- **142A=OK** en ~/netlab360-bootstrap/s05/evidencias/noc-integracion/05_Precheck_Codigo_Observabilidad_NOC.txt: 15 pruebas nuevas, 14 topología, 14 layout y 6 HA-UI = **49/49**; IP 192.168.47.40/24, gateway 192.168.47.2; git main eef8946 limpio.
- **142B=ERROR DOS VECES EN EL PASO 826**: el primer switch HQ muestra identidad S05_HQ_a14ac59efb1e996a, modo 802.3ad, flags UP/LOWER_UP, pero el JSON iproute2 omite la clave ad_num_ports y devuelve None; el assert exigía entero 2. El histórico 06_Precheck_Raw_Bonds_OVS_Observador.txt conserva el resultado fallido del segundo intento; el primer intento también consta en terminal compartida. **NO existe marcador 142B OK y los pasos 827–830 no se ejecutaron**.
- **142C NO SE EJECUTÓ**. No se ha desplegado el observador nuevo, no se ha reiniciado NOC, FRR, OVS, LACP, Faucet ni Ubuntu.
- Helper root instalado PREVIO: /usr/local/libexec/netlab360-observer root:root 755, SHA256 **8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad**. Es la versión FRR/FIB estable; mantenerla hasta disponer de backup y rollback.
- En la auditoría anterior lote 140, ip -d link sí reflejaba ad_num_ports 2 y el verificador LACP existente verificaba **Number of ports: 2** vía /proc/net/bonding para HQ/S1/S2. El error de JSON no prueba caída de LACP.
- NOC 9130 y exporter 9110 activos antes del error; FIB S1=s1p/S2=s2p, HTTP backend HQ; 3 LACP 2/2, OpenFlow Faucet conectado, reloj Panamá. La UI desplegada conserva grafo 18 nodos/21 enlaces pero **sin telemetría LACP/SDN** aún.
- La rama de corrección añade fallback para iproute2: comprobar propietario y bonding 802.3ad por JSON y, si ad_num_ports está ausente, usar ip netns exec con nombre fijo para leer /proc/net/bonding/<bond> y exigir Number of ports único 0-2 y modo IEEE 802.3ad. Si hay error/ambigüedad: UNKNOWN, no RUNNING inventado. Tests incluyen caso None, un solo miembro, propietario ajeno y /proc inválido.
- **NO** repetir 142A ni 142B original, ni ninguna prueba de falla LACP/SDN, ni reiniciar VMware/Ubuntu/servicios. Los estados efímeros siguen necesitándose para S05.

## Orden de siguientes lotes (sin cambios de infraestructura)

### 143A: sincronizar y ejecutar tests del parser nuevo (pasos 836–841)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
{
echo "========== 836 GIT / GATES =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git log -1 --oneline
grep -Fxq '========== LOTE142A_CODIGO_Y_BASELINE=OK ==========' "$DIR/05_Precheck_Codigo_Observabilidad_NOC.txt"
test -s "$DIR/06_Precheck_Raw_Bonds_OVS_Observador.txt"
echo "HISTORICO_142B=FALLIDO_PRESERVADO_NO_REPETIR"
echo "========== 837 COMPILAR =========="
python3 -m py_compile scripts/operacion/s05-observador-privilegiado.py servicios/topologia-s05/app.py tests/test_s05_noc_lacp_sdn_telemetria.py
echo "========== 838 TESTS LACP-SDN =========="
python3 -m unittest discover -s tests -p 'test_s05_noc_lacp_sdn_telemetria.py' -v
echo "========== 839 REGRESION =========="
for p in test_s05_topologia.py test_s05_layout.py test_s05_ha_ui.py; do
 python3 -m unittest discover -s tests -p "$p" -v
done
echo "========== 840 HELPER LEGACY TODAVIA INSTALADO =========="
HELPER=/usr/local/libexec/netlab360-observer
test -f "$HELPER" && test ! -L "$HELPER"
stat -c '%U:%G %a %n' "$HELPER"
OLD=$(sha256sum "$HELPER" | awk '{print $1}')
echo "SHA_HELPER_INSTALADO=$OLD"
test "$OLD" = 8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad
echo "SHA_NUEVO=$(sha256sum scripts/operacion/s05-observador-privilegiado.py | awk '{print $1}')"
echo "========== 841 RED Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE143A_PARSER_CORREGIDO=OK =========="
} 2>&1 | tee "$DIR/08_Precheck_Parser_Bond_Proc.txt"
BASH
~~~

### 143B: seis bonds verificados con JSON + /proc, OVS y API (842–847)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
sudo -v
grep -Fxq '========== LOTE143A_PARSER_CORREGIDO=OK ==========' "$DIR/08_Precheck_Parser_Bond_Proc.txt"
{
echo "========== 842 LACP JSON Y PROC =========="
python3 - <<'PY'
import json,re,subprocess
from pathlib import Path
h=Path.home()
for sede in ("hq","s1","s2"):
 p=h/f"netlab360-bootstrap/s05/lacp-multisede/state-{sede}.json"
 state=json.loads(p.read_text())
 assert state["status"]=="active"
 for lado,ns,bond in (("SW",f"nl360-s02-sw-{sede}","s5bond0"),("CLIENT",f"nl360-s05-lacp-{sede}","bond0")):
  j=subprocess.run(["sudo","-n","ip","-n",ns,"-j","-d","link","show","dev",bond],capture_output=True,text=True,timeout=8,check=True)
  row=json.loads(j.stdout)[0]; info=row.get("linkinfo") or {}; data=info.get("info_data") or {}
  assert row.get("ifalias")==state["alias"] and row.get("ifname","").split("@")[0]==bond
  assert info.get("info_kind")=="bond" and str(data.get("mode"))=="802.3ad"
  assert {"UP","LOWER_UP"}.issubset(set(row.get("flags",[])))
  p=subprocess.run(["sudo","-n","ip","netns","exec",ns,"/usr/bin/cat",f"/proc/net/bonding/{bond}"],capture_output=True,text=True,timeout=8,check=True)
  assert re.search(r"(?m)^Bonding Mode:\s*IEEE 802\.3ad\b",p.stdout)
  nums=re.findall(r"(?m)^\s*Number of ports:\s*(\d+)\s*$",p.stdout)
  assert len(nums)==1 and int(nums[0])==2,(sede,lado,nums)
  value=data.get("ad_num_ports")
  assert value is None or (type(value) is int and value==2)
  print(f"LACP_{sede.upper()}_{lado}=JSON_PORTS_{value}_PROC_PORTS_{nums[0]}_ALIAS_OK")
print("LACP_FUENTES=6_DE_6_OK")
PY
echo "========== 843 OVS CONTROLLER =========="
sudo -n ovs-vsctl --timeout=3 get Bridge br-s05-sdn external_ids:netlab360-owner
sudo -n ovs-vsctl --timeout=3 list-ports br-s05-sdn
sudo -n ovs-vsctl --timeout=3 --format=csv --data=bare --no-heading --columns=is_connected list Controller
echo "========== 844 FAUCET Y FLOWS =========="
sudo -n docker inspect nl360-s05-faucet --format 'RUNNING={{.State.Running}} OWNER={{index .Config.Labels "netlab360.owner"}}'
sudo -n ovs-ofctl -O OpenFlow13 dump-flows br-s05-sdn | awk 'index($0,"cookie=")&&index($0,"actions="){n++}END{print "OPENFLOW_FLOWS="n;exit(n>0?0:1)}'
echo "========== 845 API NOC EXISTENTE =========="
python3 - <<'PY'
import json
from urllib.request import urlopen
with urlopen("http://127.0.0.1:9130/api/v1/graph",timeout=8) as f:d=json.load(f)
print("FIB=",d.get("routing"));print("HA=",d.get("ha_service"));print("WARNINGS=",d.get("source_warnings"))
print("LACP_API=",d.get("lacp","SIN_DESPLEGAR"));print("SDN_API=",d.get("sdn","SIN_DESPLEGAR"))
PY
echo "========== 846 HOST =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== 847 GIT =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE143B_FUENTES_6_BONDS_OVS=OK =========="
} 2>&1 | tee "$DIR/09_Validacion_Real_Bonds_Proc_y_OVS.txt"
BASH
~~~

### 143C: HTML/JS y hashes antes del rollout (848–853)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/noc-integracion"
grep -Fxq '========== LOTE143B_FUENTES_6_BONDS_OVS=OK ==========' "$DIR/09_Validacion_Real_Bonds_Proc_y_OVS.txt"
{
echo "========== 848 CUATRO TARJETAS =========="
python3 - <<'PY'
from pathlib import Path
s=Path("servicios/topologia-s05/index.html").read_text()
assert all(x in s for x in ("obs-hq-state","obs-s1-state","obs-s2-state","obs-sdn-state","renderObservedSources","formatPanamaStamp"))
assert s.count('<svg id="network"')==1
print("UI_NOC=4_TARJETAS_SVG_INTACTO")
PY
echo "========== 849 JAVASCRIPT =========="
python3 - <<'PY' | node --check
import re
from pathlib import Path
s=Path("servicios/topologia-s05/index.html").read_text()
b=re.findall(r"<script>([\s\S]*?)</script>",s)
assert len(b)==1
print(b[0])
PY
echo "========== 850 HASHES =========="
sha256sum scripts/operacion/s05-observador-privilegiado.py servicios/topologia-s05/app.py servicios/topologia-s05/index.html
sha256sum /usr/local/libexec/netlab360-observer
echo "========== 851 SERVICIOS =========="
systemctl is-active netlab360-s05-noc netlab360-s04-exporter
echo "========== 852 HOST =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== 853 GIT =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE143C_PRE_ROLLOUT_NOC=OK =========="
} 2>&1 | tee "$DIR/10_PreRollout_NOC_Panel_y_Hashes.txt"
BASH
~~~

## Después de 143A/B/C OK

**NO desplegar aún si algún lote falla.** Tras verificar outputs, instalar el helper actualizado con backup root:root 0755 y control de SHA (NO ejecutar repo del usuario como root), validar su acción sudoers existente snapshot con FRR/FIB y LACP 3x2/2 + SDN connected/flows>0; reiniciar únicamente servicio NOC 9130 con rollback; verificar JSON API y tarjetas reales en navegador con hora Panamá y observaciones UNKNOWN si fuente no disponible. Sin changes de ens33, FRR/OSPF, HA HTTP, LACP, OVS/Faucet o VM.

**Otros pendientes al cierre:** S05 #64 dashboard real, #32 HA de instancia/equipo, #31 caracterización P1/P1B, #105 importación/verificación de PNG originales; luego S06 aprendizaje automático, S07 AIOps y S08 entregables. No reejecutar fallas WAN/LACP/SDN ya validadas. Respaldo del estado de VM para reboot guest #106 sigue pendiente; suspensión VMware anterior no prueba persistencia tras apagado real.
