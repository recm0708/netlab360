# NETLAB360 · S05 · Lotes 128–131: OVS/Faucet en una isla OpenFlow

Estado verificado 14/11/2026: 123 auditoría OK; 124 APT simulación 5 nuevos, 0 remociones, 0 upgrades; 125 OVS 3.7.1 instalado y cero bridges; 126 imagen Faucet descargada y fijada al digest sha256:34c5d8c1ce207de37abc7e4d9b1b60e020d43524d85e80449c637a7867e5ea32; 127 cuatro pruebas Python OK, check_faucet_config OK y hashes del YAML original y operativo idénticos.

Diseño: contenedor Faucet sin reinicio automático, OpenFlow mapeado en host solo a 127.0.0.1:16653, OVS br-s05-sdn DPID 0x505, fail_mode secure/OpenFlow13, tres namespaces y veth privados. VLAN410 permite A/B, VLAN420 C aislado. Clientes A=198.18.41.11/24, B=.12/24, C=.13/24; sin conexión a ens33, troncales S02 ni WAN.

Script oficial del proyecto: scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py. Acciones plan, precheck, up, status, inspect, down. El estado state-sdn.json se crea ANTES de recursos; si UP se corta, inspeccionar y no repetir. Up/down requieren --confirm-isolated. No ejecutar down sin autorización de reversión.

## Lote 128 — pruebas y precheck, SIN CAMBIOS (pasos 671–676)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
mkdir -p "$DIR"
sudo -v
{
echo "========== 671 GIT Y LOTE127 =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
test -f scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py
grep -Fxq '========== LOTE127_SDN_CONFIG_VALIDADA_SIN_DESPLIEGUE=OK ==========' "$HOME/netlab360-bootstrap/s05/evidencias/sdn-preparacion/05_Faucet_Config_Validada_Offline.txt"
git log -1 --oneline
echo "========== 672 REGRESION PYTHON =========="
python3 -m py_compile scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py
python3 -m unittest discover -s tests -p 'test_s05_sdn_faucet_config.py' -v
python3 -m unittest discover -s tests -p 'test_s05_sdn_ovs_faucet_aislado.py' -v
echo "========== 673 REPO Y CONFIG OPERATIVA =========="
cmp -s config/s05/sdn/faucet.yaml "$HOME/netlab360-bootstrap/s05/sdn-faucet/config/faucet.yaml"
sha256sum config/s05/sdn/faucet.yaml "$HOME/netlab360-bootstrap/s05/sdn-faucet/config/faucet.yaml"
echo "========== 674 PLAN =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py plan
echo "========== 675 PRECHECK =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py precheck
echo "========== 676 POSTCHECK SIN CAMBIOS =========="
sudo -n ovs-vsctl --timeout=12 show
ip -4 -br address show ens33
ip -4 route show default
sudo -n docker ps --format '{{.Names}} {{.Status}}'
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE128_SDN_PRECHECK=OK =========="
} 2>&1 | tee "$DIR/01_SDN_Precheck_Propiedad_y_Aislamiento.txt"
BASH
~~~

Si no sale el marcador exacto LOTE128_SDN_PRECHECK=OK, NO ejecutar 129.

## Lote 129 — CREAR CONTROLADOR, OVS y tres namespaces aislados (677–679)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
sudo -v
grep -Fxq '========== LOTE128_SDN_PRECHECK=OK ==========' "$DIR/01_SDN_Precheck_Propiedad_y_Aislamiento.txt"
{
echo "========== 677 DESPLIEGUE PROTEGIDO =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py up --confirm-isolated
echo "========== 678 INSPECCION DE PROPIEDAD =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py inspect
echo "========== 679 GESTION FINAL =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE129_SDN_DESPLIEGUE=OK =========="
} 2>&1 | tee "$DIR/02_SDN_Despliegue_OVS_Faucet.txt"
BASH
~~~

Si SSH falla durante 129, NO repetir UP. Reconectar y ejecutar SOLO:

~~~bash
cd ~/proyectos/netlab360
sudo -v
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py inspect
sudo -n docker ps -a --filter 'name=nl360-s05-faucet'
sudo -n ovs-vsctl --timeout=12 show
~~~

Compartir salida si indica provisioning o needs_inspection; no borrar nada ni reiniciar.

## Lote 130 — aceptación OpenFlow y capturas (680–684)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
sudo -v
grep -Fxq '========== LOTE129_SDN_DESPLIEGUE=OK ==========' "$DIR/02_SDN_Despliegue_OVS_Faucet.txt"
{
echo "========== 680 ESTADO REAL =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py status

echo "========== 681 CAPTURA OPENFLOW =========="
echo "========== INICIO_CAPTURA_S05_58_SDN_FAUCET_OPENFLOW =========="
sudo -n ovs-vsctl --timeout=12 show
sudo -n ovs-ofctl -O OpenFlow13 dump-flows br-s05-sdn | sed -n '1,12p'
grep -E 'S05_SDN_(FAUCET_OPENFLOW|OPENFLOW_REGLAS|OFPORT_)' "$DIR/02_SDN_Despliegue_OVS_Faucet.txt"
echo "========== FIN_CAPTURA_S05_58_SDN_FAUCET_OPENFLOW =========="

echo "========== 682 CAPTURA VLAN410 =========="
echo "========== INICIO_CAPTURA_S05_59_SDN_VLAN410_PERMITIDA =========="
grep -E 'S05_SDN_PING_[AB]_198\.18\.41\.(11|12)=OK' "$DIR/02_SDN_Despliegue_OVS_Faucet.txt"
echo "S05_SDN_POLITICA_VLAN410=A_B_PERMITIDOS"
echo "========== FIN_CAPTURA_S05_59_SDN_VLAN410_PERMITIDA =========="

echo "========== 683 CAPTURA VLAN420 =========="
echo "========== INICIO_CAPTURA_S05_60_SDN_VLAN420_AISLADA =========="
grep -E 'S05_SDN_AISLAMIENTO_[AC]_198\.18\.41\.(11|13)=BLOQUEADO' "$DIR/02_SDN_Despliegue_OVS_Faucet.txt"
echo "S05_SDN_POLITICA_VLAN420=C_SEPARADA_SIN_ROUTER"
echo "========== FIN_CAPTURA_S05_60_SDN_VLAN420_AISLADA =========="

echo "========== 684 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
sudo -n docker ps --format '{{.Names}} {{.Status}}'
echo "========== LOTE130_SDN_POLITICAS=OK =========="
} 2>&1 | tee "$DIR/03_SDN_OpenFlow_VLAN410_420.txt"
BASH
~~~

Capturas obligatorias con rango inicio/fin completo y nombre sin extensión:
- S05_58_SDN_Faucet_OpenFlow_Conectado
- S05_59_SDN_VLAN410_Comunicacion_Permitida
- S05_60_SDN_VLAN420_Aislamiento_Verificado

## Lote 131 — regresión multisede, servicios y hashes (685–690)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
sudo -v
grep -Fxq '========== LOTE130_SDN_POLITICAS=OK ==========' "$DIR/03_SDN_OpenFlow_VLAN410_420.txt"
{
echo "========== 685 ESTADO SDN =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py status
echo "========== 686 TRES LACP =========="
for site in hq s1 s2; do
 python3 "scripts/laboratorio/s05-lacp-$site-integracion.py" status
done
echo "========== 687 OSPF FRR =========="
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.71.20.0/24'
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.72.20.0/24'
echo "========== 688 SERVICIOS =========="
for unit in netlab360-s04-exporter netlab360-s05-noc netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
 test "$(systemctl is-active "$unit")" = active
 echo "S05_SDN_SERVICE_$unit=active"
done
echo "========== 689 GESTION Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE131_SDN_INTEGRACION_SIN_REGRESION=OK =========="
} 2>&1 | tee "$DIR/04_SDN_Regresion_Multisede.txt"

echo "========== 690 MANIFIESTO SHA256 =========="
sha256sum "$DIR/01_SDN_Precheck_Propiedad_y_Aislamiento.txt" \
 "$DIR/02_SDN_Despliegue_OVS_Faucet.txt" \
 "$DIR/03_SDN_OpenFlow_VLAN410_420.txt" \
 "$DIR/04_SDN_Regresion_Multisede.txt" \
 > "$DIR/05_Manifiesto_SHA256_SDN.txt"
sha256sum -c "$DIR/05_Manifiesto_SHA256_SDN.txt"
BASH
~~~

Los hash 131 solo verifican TXT, no PNG originales. Después: falla/retorno de puerto/controlador SDN con rescate, telemetría real NOC, aceptación #23, y avance de #32 (HA de instancia). No reiniciar Ubuntu ni Windows; los namespaces S02/HA/LACP/SDN siguen efímeros y la recuperación tras reinicio está en #106.
