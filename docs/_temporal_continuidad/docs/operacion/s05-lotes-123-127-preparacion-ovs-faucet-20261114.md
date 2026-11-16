# NETLAB360 S05 · Cinco lotes 123–127 para preparar OVS/Faucet

Corte real 14/11/2026: LOTE122_AUDITORIA_PRE_SDN=OK en el segundo intento. 18 namespaces y 3 contenedores FRR operativos, 6 unidades HA/NOC activas, 13 GiB de RAM y 132 GiB de disco disponibles, ens33=192.168.47.40/24 gateway .2. OVS, Faucet y Ryu no instalados. El primer intento de 122 fue interrumpido por SSH; no demostró un problema de red.

Objetivo: instalar OVS sin bridges, descargar Faucet en Docker y validar una topología aislada sin lanzarla todavía. La configuración versionada está en config/s05/sdn/faucet.yaml, con datapath br-s05-sdn (ID 0x505), VLAN410 para dos hosts A/B y VLAN420 para host C aislado. Ninguno tendrá interfaz física o troncal a S02, WAN ni ens33.

Fuentes oficiales: Open vSwitch Debian/Ubuntu Packaging, Faucet Docker Installation, Faucet check_faucet_config. La etiqueta Docker latest no garantiza reproducibilidad: registrar digest de imagen antes de arrancar.

NO reboot, apt upgrade, docker restart de FRR, NetworkManager restart, modificar bridges S02 o enlazar ens33. Si se corta SSH durante APT/Docker, inspeccionar proceso y estado antes de repetir.

## Lote 123 — inspección de colisiones y red (pasos 648–654)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-preparacion"
mkdir -p "$DIR"
sudo -v
{
echo "========== 648 GIT Y CORTE =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
test -f config/s05/sdn/faucet.yaml
grep -Fxq '========== LOTE122_AUDITORIA_PRE_SDN=OK ==========' "$HOME/netlab360-bootstrap/s05/evidencias/cierre-practico/01_Auditoria_SDN_HA_y_Reinicio_Pendiente.txt"
git log -1 --oneline
echo "========== 649 APT DISPONIBLE =========="
dpkg-query -W openvswitch-switch openvswitch-common 2>&1 || true
apt-cache policy openvswitch-switch openvswitch-common | head -45
echo "========== 650 RECURSOS EXCLUSIVOS =========="
for dev in br-s05-sdn sdna0 sdnb0 sdnc0; do
 if ip link show dev "$dev" >/dev/null 2>&1; then echo "CONFLICTO_LINK_$dev=SI"; exit 3; fi
 echo "SDN_LINK_$dev=LIBRE"
done
for ns in nl360-s05-sdn-a nl360-s05-sdn-b nl360-s05-sdn-c; do
 if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then echo "CONFLICTO_NS_$ns=SI"; exit 3; fi
 echo "SDN_NS_$ns=LIBRE"
done
if sudo -n ss -ltnH | awk '{print $4}' | grep -Eq '(^|:)16653$'; then echo "CONFLICTO_PORT16653=SI"; exit 3; fi
if sudo -n docker ps -a --format '{{.Names}}' | grep -Fxq nl360-s05-faucet; then echo "CONFLICTO_FAUCET=SI"; exit 3; fi
echo "PORT16653_Y_FAUCET=LIBRES"
echo "========== 651 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
ip -4 -o address show dev ens33 | grep -Fq '192.168.47.40/24'
ip -4 route show default | grep -Fq 'via 192.168.47.2 dev ens33'
echo "========== 652 OVS ACTUAL =========="
if command -v ovs-vsctl >/dev/null 2>&1; then sudo -n ovs-vsctl --timeout=12 list-br; else echo "OVS=NO_INSTALADO"; fi
echo "========== 653 DOCKER =========="
sudo -n docker ps --format '{{.Names}} {{.Status}}'
echo "========== 654 GIT FINAL =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE123_AUDITORIA_SDN=OK =========="
} 2>&1 | tee "$DIR/01_Auditoria_Preinstalacion_SDN.txt"
BASH
~~~

## Lote 124 — actualizar índices y simular instalación; sin cambios de servicio (655–658)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-preparacion"
sudo -v
grep -Fxq '========== LOTE123_AUDITORIA_SDN=OK ==========' "$DIR/01_Auditoria_Preinstalacion_SDN.txt"
{
echo "========== 655 INDICES APT =========="
sudo -n apt-get update
echo "========== 656 VERSIONES CANDIDATAS =========="
apt-cache policy openvswitch-switch openvswitch-common
echo "========== 657 SIMULACION =========="
plan="$(sudo -n apt-get -s install --no-install-recommends openvswitch-switch openvswitch-common)"
printf '%s\n' "$plan"
if grep -Eq '^Remv ' <<< "$plan"; then echo "APT_PLAN_REMUEVE_PAQUETES=ABORTAR"; exit 3; fi
echo "APT_PLAN_SIN_REMOCIONES=OK"
echo "========== 658 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== LOTE124_APT_SIMULACION=OK =========="
} 2>&1 | tee "$DIR/02_APT_Simulacion_OVS.txt"
BASH
~~~

Revisar el plan de paquetes. Si incluye eliminación o actualización de componentes críticos del sistema, NO ejecutar 125. No ejecutar apt upgrade.

## Lote 125 — instalar SOLO paquetes OVS; no crear bridges (659–662)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-preparacion"
sudo -v
grep -Fxq '========== LOTE124_APT_SIMULACION=OK ==========' "$DIR/02_APT_Simulacion_OVS.txt"
{
echo "========== 659 INSTALAR OVS =========="
sudo -n env DEBIAN_FRONTEND=noninteractive NEEDRESTART_MODE=l apt-get install -y --no-install-recommends openvswitch-switch openvswitch-common
echo "========== 660 VERIFICAR OVS =========="
dpkg-query -W openvswitch-switch openvswitch-common
sudo -n ovs-vsctl --timeout=12 show
echo "========== 661 NO EXISTEN BRIDGES OVS =========="
puentes="$(sudo -n ovs-vsctl --timeout=12 list-br)"
printf '%s\n' "$puentes"
if [[ -n "$puentes" ]]; then echo "OVS_EXISTEN_BRIDGES=ABORTAR"; exit 3; fi
echo "OVS_BRIDGES=0"
echo "========== 662 GESTION Y FRR =========="
ip -4 -br address show ens33
ip -4 route show default
sudo -n docker ps --format '{{.Names}} {{.Status}}'
ip -4 -o address show dev ens33 | grep -Fq '192.168.47.40/24'
ip -4 route show default | grep -Fq 'via 192.168.47.2 dev ens33'
echo "========== LOTE125_OVS_INSTALADO_SIN_BRIDGE=OK =========="
} 2>&1 | tee "$DIR/03_Instalacion_Controlada_OVS.txt"
BASH
~~~

Si SSH se interrumpe durante instalación, NO lanzar APT otra vez sin consultar estado dpkg/apt y ovs-vsctl. No reiniciar.

## Lote 126 — descargar imagen Faucet, SIN ejecutar contenedor (663–666)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-preparacion"
sudo -v
grep -Fxq '========== LOTE125_OVS_INSTALADO_SIN_BRIDGE=OK ==========' "$DIR/03_Instalacion_Controlada_OVS.txt"
{
echo "========== 663 PULL CONTROLADOR =========="
sudo -n docker pull faucet/faucet:latest
echo "========== 664 IDENTIFICAR DIGEST =========="
sudo -n docker image inspect faucet/faucet:latest --format 'ID={{.Id}} ARCH={{.Architecture}}'
sudo -n docker image inspect faucet/faucet:latest --format 'DIGESTS={{json .RepoDigests}}'
echo "========== 665 NO EJECUTAR AUN =========="
if sudo -n docker ps -a --format '{{.Names}}' | grep -Fxq nl360-s05-faucet; then echo "FAUCET_YA_EXISTE=ABORTAR"; exit 3; fi
echo "FAUCET_NO_CREADO=OK"
echo "========== 666 OVS NO MODIFICA S02 =========="
test -z "$(sudo -n ovs-vsctl --timeout=12 list-br)"
echo "OVS_BRIDGES=0"
echo "========== LOTE126_FAUCET_IMAGEN_PREPARADA=OK =========="
} 2>&1 | tee "$DIR/04_Imagen_Faucet_y_Digest.txt"
BASH
~~~

## Lote 127 — configuración de Faucet y test en contenedor SIN red (667–670)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-preparacion"
BASE="$HOME/netlab360-bootstrap/s05/sdn-faucet"
sudo -v
grep -Fxq '========== LOTE126_FAUCET_IMAGEN_PREPARADA=OK ==========' "$DIR/04_Imagen_Faucet_y_Digest.txt"
{
echo "========== 667 REGRESION SDN OFFLINE =========="
python3 -m unittest discover -s tests -p 'test_s05_sdn_faucet_config.py' -v
echo "========== 668 STAGING SIN SOBREESCRIBIR =========="
mkdir -p "$BASE/config" "$BASE/logs"
if [[ -e "$BASE/config/faucet.yaml" ]]; then
 cmp -s config/s05/sdn/faucet.yaml "$BASE/config/faucet.yaml" ||
 { echo "FAUCET_CONFIG_YA_DIFIERE=ABORTAR"; exit 3; }
else
 cp config/s05/sdn/faucet.yaml "$BASE/config/faucet.yaml"
fi
sha256sum config/s05/sdn/faucet.yaml "$BASE/config/faucet.yaml"
echo "========== 669 VALIDAR CONTROLADOR SIN NETWORK =========="
sudo -n docker run --rm --network none --cap-drop ALL --security-opt no-new-privileges \
 --entrypoint /bin/sh -v "$BASE/config:/etc/faucet:ro" faucet/faucet:latest \
 -c 'check_faucet_config /etc/faucet/faucet.yaml >/dev/null && echo FAUCET_CONFIG_CHECK=OK'
echo "========== 670 NO HAY BRIDGE NI CONTAINER ACTIVO =========="
test -z "$(sudo -n ovs-vsctl --timeout=12 list-br)"
sudo -n docker ps --format '{{.Names}} {{.Status}}'
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE127_SDN_CONFIG_VALIDADA_SIN_DESPLIEGUE=OK =========="
} 2>&1 | tee "$DIR/05_Faucet_Config_Validada_Offline.txt"
BASH
~~~

Cuando estos cinco lotes concluyan, crear por separado los recursos SDN exclusivos con script seguro/rollback y aceptación de OpenFlow, VLAN 410/420, prueba A↔B permitida y A↔C aislada, falla/restauración, HTTP/FRR/NOC sin alteraciones. Hasta entonces NO declarar SDN desplegado ni reiniciar Windows/VMware.
