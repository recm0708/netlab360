#!/usr/bin/env bash
# NETLAB360 B2-L2: demostrar dos VLAN HQ sobre un trunk Linux bridge 802.1Q.
# Solo crea namespaces propios nl360-ta/tb/t110a/t110b/t120a/t120b.
# Nunca configura ens33, gateway, VMnet8 ni firewall del host.
set -Eeuo pipefail

if [[ "$#" -ne 1 || "$1" != "--snapshot-confirmado" ]]; then
  echo "BLOQUEADO: usar --snapshot-confirmado tras confirmar snapshot existente"
  exit 2
fi
[[ "$(hostname)" == "netlab360-lab" ]] || { echo "ERROR_HOSTNAME"; exit 2; }
[[ "$(id -u)" -ne 0 ]] || { echo "ERROR: usar usuario normal, no root"; exit 2; }
cd "$HOME/proyectos/netlab360"
sudo -v
for cmd in ip bridge ping python3 git sudo; do
  command -v "$cmd" >/dev/null || { echo "FALTA_HERRAMIENTA=$cmd"; exit 2; }
done
ip -4 -br address show ens33 | grep -Fq '192.168.47.40/24' || { echo "ERROR_IP_GESTION"; exit 2; }
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' || { echo "ERROR_GW_GESTION"; exit 2; }
python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml
NAMES="nl360-ta nl360-tb nl360-t110a nl360-t110b nl360-t120a nl360-t120b"
for ns in $NAMES; do
  if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
    echo "ERROR: namespace previo $ns. No modificarlo."
    exit 3
  fi
done

mkdir -p "$HOME/netlab360-bootstrap/evidencias"
LOG="$HOME/netlab360-bootstrap/evidencias/b2-l2-trunk-$(date +%Y%m%d-%H%M%S).log"
ORIG_IP="$(ip -4 -o addr show ens33)"
ORIG_ROUTE="$(ip -4 route show table main)"
OWNED=""
exec > >(tee "$LOG") 2>&1

cleanup() {
  rc=$?
  trap - EXIT
  echo "========== LIMPIEZA EXCLUSIVA TRUNK =========="
  for ns in $OWNED; do
    sudo ip netns delete "$ns" 2>/dev/null || { echo "ERROR_AL_BORRAR=$ns"; rc=7; }
  done
  if [[ "$(ip -4 -o addr show ens33)" != "$ORIG_IP" ]] ||
     [[ "$(ip -4 route show table main)" != "$ORIG_ROUTE" ]]; then
    echo "RED_GESTION_INTACTA=NO (comprobar causa externa)"
    rc=8
  else
    echo "RED_GESTION_INTACTA=SI"
  fi
  for ns in $NAMES; do
    if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      echo "RESIDUO_NAMESPACE=$ns"
      rc=9
    fi
  done
  echo "LOG_LOCAL=$LOG"
  echo "RESULTADO_B2_L2_TRUNK=$rc"
  exit "$rc"
}
trap cleanup EXIT

echo "========== B2-L2 TRUNK 802.1Q AISLADO =========="
date -Is
hostname
echo "SWITCHES=SW-HQ-A,SW-HQ-B | VLAN=110,120 | WAN=NO"
echo "IPAM_HQ_VLAN110=10.70.10.0/24"
echo "IPAM_HQ_VLAN120=10.70.20.0/24"
echo "CONTEXTO=dos switches dentro de HQ, NO tramo WAN/S1"

for ns in $NAMES; do
  sudo ip netns add "$ns"
  OWNED="$ns $OWNED"
  sudo ip -n "$ns" link set lo up
done

for sw in nl360-ta nl360-tb; do
  sudo ip -n "$sw" link add br-trk type bridge vlan_filtering 1
  sudo ip -n "$sw" link set br-trk up
done

# Puertos access sin etiqueta hacia terminales Linux.
access_port() {
  sw="$1"; port="$2"; peer="$3"; pc="$4"; vlan="$5"; address="$6"
  sudo ip -n "$sw" link add "$port" type veth peer name "$peer"
  sudo ip -n "$sw" link set "$peer" netns "$pc"
  sudo ip -n "$pc" link set "$peer" name eth0
  sudo ip -n "$sw" link set "$port" master br-trk
  sudo ip netns exec "$sw" bridge vlan del dev "$port" vid 1 >/dev/null 2>&1 || true
  sudo ip netns exec "$sw" bridge vlan add dev "$port" vid "$vlan" pvid untagged
  sudo ip -n "$sw" link set "$port" up
  sudo ip -n "$pc" addr add "$address" dev eth0
  sudo ip -n "$pc" link set eth0 up
}
access_port nl360-ta a110 pa110 nl360-t110a 110 10.70.10.10/24
access_port nl360-tb b110 pb110 nl360-t110b 110 10.70.10.11/24
access_port nl360-ta a120 pa120 nl360-t120a 120 10.70.20.10/24
access_port nl360-tb b120 pb120 nl360-t120b 120 10.70.20.11/24

# Un solo enlace troncal etiquetado entre SW-HQ-A y SW-HQ-B.
sudo ip -n nl360-ta link add tr-a type veth peer name tr-b
sudo ip -n nl360-ta link set tr-b netns nl360-tb
for item in 'nl360-ta tr-a' 'nl360-tb tr-b'; do
  read -r sw port <<< "$item"
  sudo ip -n "$sw" link set "$port" master br-trk
  sudo ip netns exec "$sw" bridge vlan del dev "$port" vid 1 >/dev/null 2>&1 || true
  sudo ip netns exec "$sw" bridge vlan add dev "$port" vid 110
  sudo ip netns exec "$sw" bridge vlan add dev "$port" vid 120
  sudo ip -n "$sw" link set "$port" up
done

echo "========== INICIO CAPTURA B2_L2_02 =========="
date -Is
echo "========== VLAN SW-HQ-A =========="
sudo ip netns exec nl360-ta bridge vlan show
echo "========== VLAN SW-HQ-B =========="
sudo ip netns exec nl360-tb bridge vlan show
echo "========== VLAN110 POSITIVA A TRAVES DE TRUNK =========="
sudo ip netns exec nl360-t110a ping -n -c 3 -W 2 10.70.10.11
echo "PRUEBA_TRUNK_VLAN110=OK"
echo "========== VLAN120 POSITIVA A TRAVES DE TRUNK =========="
sudo ip netns exec nl360-t120a ping -n -c 3 -W 2 10.70.20.11
echo "PRUEBA_TRUNK_VLAN120=OK"
echo "========== FIN CAPTURA B2_L2_02 =========="

echo "========== INICIO CAPTURA B2_L2_03 =========="
date -Is
echo "========== AISLAMIENTO ENTRE VLAN CON MISMA SUBRED DE PRUEBA =========="
# Alias temporal de verificacion SOLO en VLAN120: mismo prefijo que VLAN110
# para demostrar que el bloqueo se debe a L2/ARP y NO a ausencia de ruta IP.
sudo ip -n nl360-t120b addr add 10.70.10.12/24 dev eth0
sudo ip -n nl360-t110a route get 10.70.10.12
if sudo ip netns exec nl360-t110a ping -n -c 2 -W 1 -w 4 10.70.10.12; then
  echo "ERROR: VLAN110 alcanzo host de VLAN120"
  exit 6
else
  echo "AISLAMIENTO_INTERVLAN_L2=OK (sin respuesta L2/ARP)"
fi
echo "========== CONECTIVIDAD SIGUE ACTIVA EN VLAN110 =========="
sudo ip netns exec nl360-t110a ping -n -c 2 -W 2 10.70.10.11
echo "========== CONECTIVIDAD SIGUE ACTIVA EN VLAN120 =========="
sudo ip netns exec nl360-t120a ping -n -c 2 -W 2 10.70.20.11
echo "B2_L2_TRUNK_Y_AISLAMIENTO=OK"
echo "NOTA: esta prueba NO implementa ACL ni prueba inter-VLAN routing o WAN"
echo "========== FIN CAPTURA B2_L2_03 =========="
