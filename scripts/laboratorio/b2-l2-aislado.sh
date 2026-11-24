#!/usr/bin/env bash
# NETLAB360 | Laboratorio: b2 l2 aislado
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# Prueba B2: VLAN L2 efimera mediante namespaces y veth.
# Precondicion humana: snapshot VMware confirmado. No modifica ens33.
set -Eeuo pipefail

if [[ "${1:-}" != "--snapshot-confirmado" ]]; then
  echo "BLOQUEADO: confirmar antes snapshot VMware NETLAB360-BASE-HERRAMIENTAS."
  echo "Despues: bash $0 --snapshot-confirmado"
  exit 2
fi
if [[ "$(hostname)" != "netlab360-lab" ]]; then
  echo "ERROR: hostname inesperado" >&2; exit 2
fi
if ! ip -4 -o addr show ens33 | grep -q '192\.168\.47\.40/24'; then
  echo "ERROR: IPv4 ens33 inesperada" >&2; exit 2
fi
if ! ip -4 route show default | grep -q 'default via 192\.168\.47\.2 dev ens33'; then
  echo "ERROR: gateway ens33 inesperado" >&2; exit 2
fi

cd "$HOME/proyectos/netlab360"
python3 scripts/validacion/validar_ipam.py inventario/ipam/topologia-b1.yaml
python3 - <<'PY'
import yaml
from pathlib import Path
x=yaml.safe_load(Path('inventario/ipam/topologia-b1.yaml').read_text())
assert x['sites']['HQ']['vlans'][0]['id']==110
assert x['sites']['HQ']['vlans'][0]['subnet']=='10.70.10.0/24'
PY

for ns in nl360-sw nl360-a nl360-b; do
  if sudo ip netns list | grep -Eq "^$ns([[:space:]]|$)"; then
    echo "ERROR: namespace $ns ya existente; no tocarlo" >&2; exit 3
  fi
done
sudo -v
mkdir -p "$HOME/netlab360-bootstrap/evidencias"
LOG="$HOME/netlab360-bootstrap/evidencias/05-b2-l2-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1
ORIGINAL_IP="$(ip -4 -o addr show ens33)"
ORIGINAL_ROUTE="$(ip -4 route show table main)"
cleanup() {
  rc=$?
  trap - EXIT
  echo "========== LIMPIEZA AUTOMATICA =========="
  for ns in nl360-sw nl360-a nl360-b; do
    sudo ip netns delete "$ns" 2>/dev/null || true
  done
  if [[ "$(ip -4 -o addr show ens33)" != "$ORIGINAL_IP" ]]; then
    echo "ALERTA: IP ens33 cambiada externamente" >&2
    rc=4
  fi
  if [[ "$(ip -4 route show table main)" != "$ORIGINAL_ROUTE" ]]; then
    echo "ALERTA: rutas del host distintas del precheck" >&2
    rc=5
  fi
  echo "LOG_LOCAL: $LOG"
  echo "CODIGO_FINAL: $rc"
  exit "$rc"
}
trap cleanup EXIT

echo "========== B2 | EXPERIMENTO VLAN L2 AISLADO =========="
date -Is
echo "Este script no puede comprobar el snapshot VMware: operador lo ha confirmado."
for ns in nl360-sw nl360-a nl360-b; do
  sudo ip netns add "$ns"
  sudo ip -n "$ns" link set lo up
done
sudo ip -n nl360-sw link add br-lab type bridge vlan_filtering 1
sudo ip -n nl360-sw link set br-lab up

sudo ip -n nl360-sw link add sw-a type veth peer name pc-a
sudo ip -n nl360-sw link add sw-b type veth peer name pc-b
sudo ip -n nl360-sw link set pc-a netns nl360-a
sudo ip -n nl360-sw link set pc-b netns nl360-b
sudo ip -n nl360-a link set pc-a name eth0
sudo ip -n nl360-b link set pc-b name eth0

for port in sw-a sw-b; do
  sudo ip -n nl360-sw link set "$port" master br-lab
  sudo ip netns exec nl360-sw bridge vlan del dev "$port" vid 1
  sudo ip netns exec nl360-sw bridge vlan add dev "$port" vid 110 pvid untagged
  sudo ip -n nl360-sw link set "$port" up
done

sudo ip -n nl360-a addr add 10.70.10.10/24 dev eth0
sudo ip -n nl360-b addr add 10.70.10.11/24 dev eth0
sudo ip -n nl360-a link set eth0 up
sudo ip -n nl360-b link set eth0 up
echo "========== VLAN DEL SWITCH =========="
sudo ip netns exec nl360-sw bridge vlan show
echo "========== PRUEBA POSITIVA: VLAN 110 =========="
sudo ip netns exec nl360-a ping -c 3 -W 2 10.70.10.11

echo "========== PRUEBA NEGATIVA: CAMBIAR PUERTO A VLAN 120 =========="
sudo ip netns exec nl360-sw bridge vlan del dev sw-b vid 110
sudo ip netns exec nl360-sw bridge vlan add dev sw-b vid 120 pvid untagged
if sudo ip netns exec nl360-a ping -c 2 -W 1 10.70.10.11 >/dev/null 2>&1; then
  echo "ERROR: ping atraveso VLAN separadas" >&2
  exit 6
fi
echo "OK: VLAN 110 y VLAN 120 aisladas."

echo "========== RECONCILIAR Y RECUPERAR VLAN 110 =========="
sudo ip netns exec nl360-sw bridge vlan del dev sw-b vid 120
sudo ip netns exec nl360-sw bridge vlan add dev sw-b vid 110 pvid untagged
sudo ip netns exec nl360-a ping -c 3 -W 2 10.70.10.11
echo "PRUEBA B2-L2: OK (conectividad, aislamiento, recuperacion)."
echo "Se eliminaran los namespaces al finalizar."
