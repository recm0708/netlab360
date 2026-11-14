# NETLAB360 · S05 · Recuperar el avance de S2, sin repetir S1 (14-11-2026)

## Hechos confirmados

- 115: siete pruebas correctas, precheck S1/S2 aprobado.
- 116: S1 LACP IEEE 802.3ad 2/2 en VLAN220 y 10.71.20.40; pings a 4 destinos, HQ/HA/FIB y gestión protegidas.
- 117 paso 596: precheck S2 pasó. Inventario IP aumentó de 36 a 37 al incorporar S1.
- 117 paso 597: UP no superó su precheck, porque una consulta READ-ONLY de bridge vlan show en switch S2 agotó 15 s. No aparecen marcadores de despliegue S2 ni se ejecutaron pasos 598–600. **Antes de volver a UP, inspeccionar estado parcial sin borrarlo.**
- PR #115 CI OK: validación VLAN con 2 intentos de hasta 30s por consulta y fallo estricto si ambos expiran; commit mínimo 2424d87bbd2806d9060c3fb56117e7d8515d2e03.
- Capturas recibidas: 18 PNG S05_32–47, incluida 39A/39B, más S05_50. Faltan por adjuntar 48/49, 51/52; 39A y 44 son complementables. Paquete de imágenes y SHA256 generado en esta conversación, no importado a GitHub.

## Lote 117R-A — lectura sin cambios, tests y estado S2

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
mkdir -p "$DIR"
sudo -v
{
echo "========== 605 SYNC =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git merge-base --is-ancestor 2424d87bbd2806d9060c3fb56117e7d8515d2e03 HEAD
git log -1 --oneline
grep -Fxq '========== LOTE116_LACP_S1=OK ==========' "$DIR/34_Despliegue_LACP_S1_VLAN220.txt"
echo "========== 606 TESTS =========="
python3 -m unittest discover -s tests -p 'test_s05_lacp_integracion_precheck.py' -v
python3 -m unittest discover -s tests -p 'test_s05_lacp_sucursales_integracion.py' -v
echo "========== 607 GUARDAS DE S2 =========="
STATE="$HOME/netlab360-bootstrap/s05/lacp-multisede/state-s2.json"
if [[ -e "$STATE" || -L "$STATE" ]]; then
  echo "S2_STATE_DETECTADO=ABORTAR_NO_REPETIR_UP"
  exit 3
fi
if sudo -n ip netns list | awk '{print $1}' | grep -Fxq nl360-s05-lacp-s2; then
  echo "S2_NAMESPACE_DETECTADO=ABORTAR_NO_REPETIR_UP"
  exit 3
fi
sudo -n ip netns exec nl360-s02-sw-s2 ip -j link show |
python3 -c '
import json,sys
names={row["ifname"].split("@")[0] for row in json.load(sys.stdin)}
busy=names & {"s5bond0","s5p1","s5p2","s5c1","s5c2"}
print("S2_PUERTOS_NUEVOS=" + ("LIBRES" if not busy else ",".join(sorted(busy))))
if busy: sys.exit(3)
'
echo "========== 608 PRECHECK S2 =========="
python3 scripts/laboratorio/s05-lacp-s2-integracion.py precheck
echo "========== 609 S1/HQ =========="
python3 scripts/laboratorio/s05-lacp-s1-integracion.py status
python3 scripts/laboratorio/s05-lacp-hq-integracion.py status
echo "========== 610 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE117R_A_PRECHECK_S2=OK =========="
} 2>&1 | tee "$DIR/37_Auditoria_Estado_Parcial_y_Precheck_S2.txt"
BASH
~~~

## Lote 117R-B — único despliegue S2 tras precheck correcto

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
sudo -v
grep -Fxq '========== LOTE117R_A_PRECHECK_S2=OK ==========' "$DIR/37_Auditoria_Estado_Parcial_y_Precheck_S2.txt"
STATE="$HOME/netlab360-bootstrap/s05/lacp-multisede/state-s2.json"
test ! -e "$STATE"
test ! -L "$STATE"
if sudo -n ip netns list | awk '{print $1}' | grep -Fxq nl360-s05-lacp-s2; then
  echo "S2_NAMESPACE_EXISTENTE=ABORTAR"
  exit 3
fi
{
echo "========== 611 UP S2 =========="
python3 scripts/laboratorio/s05-lacp-s2-integracion.py up --confirm-isolated
echo "========== 612 CAPTURA S05_51 =========="
echo "========== INICIO_CAPTURA_S05_51_LACP_S2_DOS_ENLACES =========="
python3 scripts/laboratorio/s05-lacp-s2-integracion.py status
sudo -n ip netns exec nl360-s02-sw-s2 bridge vlan show dev s5bond0
echo "========== FIN_CAPTURA_S05_51_LACP_S2_DOS_ENLACES =========="
echo "========== 613 HQ Y S1 =========="
python3 scripts/laboratorio/s05-lacp-hq-integracion.py status
python3 scripts/laboratorio/s05-lacp-s1-integracion.py status
echo "========== 614 HOST Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE117R_B_S2=OK =========="
} 2>&1 | tee "$DIR/38_Despliegue_Corregido_LACP_S2.txt"
BASH
~~~

Captura 51: S05_51_LACP_S2_Dos_Enlaces_VLAN320. Si UP falla o cae SSH, NO repetir UP sin inspección.

## Lote 118-R — tres bonds + FRR/HA/NOC

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
sudo -v
grep -Fxq '========== LOTE117R_B_S2=OK ==========' "$DIR/38_Despliegue_Corregido_LACP_S2.txt"
{
echo "========== 615 TRES SEDES =========="
echo "========== INICIO_CAPTURA_S05_52_LACP_TRES_SEDES =========="
for sede in hq s1 s2; do
  echo "========== SEDE $sede =========="
  python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status
done
echo "========== FIN_CAPTURA_S05_52_LACP_TRES_SEDES =========="
echo "========== 616 RUTAS FRR =========="
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.71.20.0/24'
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.72.20.0/24'
echo "========== 617 SERVICIOS =========="
for unit in netlab360-s04-exporter netlab360-s05-noc netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
  test "$(systemctl is-active "$unit")" = active
  echo "SERVICIO_$unit=active"
done
echo "========== 618 HOST =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE118_R_TRES_BONDS=OK =========="
} 2>&1 | tee "$DIR/39_Tres_Sedes_LACP_Validadas.txt"
BASH
~~~

Captura 52: S05_52_LACP_Tres_Sedes_8023ad_Operativas.

**Próximo bloque:** pruebas separadas de falla 2→1→2 de S1/S2 con rescate automático, SDN aislado OVS/Faucet, NOC y consolidación SHA-256. HQ no debe volver a desplegarse ni la VM reiniciarse.
