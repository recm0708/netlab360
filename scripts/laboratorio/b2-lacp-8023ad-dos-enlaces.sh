#!/usr/bin/env bash
# NETLAB360 — laboratorio LACP 802.3ad 2 enlaces con fallo y restauracion.
# Solo opera 2 namespaces de propiedad nl360-lacpa / nl360-lacpb.
# Nunca configura ens33, VMnet8, Docker ni rutas/nftables del host.
set -Eeuo pipefail

[[ $# -eq 1 && "$1" == "--snapshot-confirmado" ]] ||
  { echo "USO: $0 --snapshot-confirmado"; exit 2; }
[[ "$(hostname)" == netlab360-lab && "$(id -u)" -ne 0 ]] ||
  { echo "ERROR_HOST_O_USUARIO"; exit 2; }
cd "$HOME/proyectos/netlab360"
sudo -v
for t in ip python3 curl grep git sudo; do
  command -v "$t" >/dev/null || { echo "FALTA=$t"; exit 2; }
done
ip -4 -br addr show ens33 | grep -Fq '192.168.47.40/24' ||
  { echo "ERROR_GESTION_IP"; exit 2; }
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' ||
  { echo "ERROR_GESTION_GW"; exit 2; }

A=nl360-lacpa
B=nl360-lacpb
for ns in "$A" "$B"; do
  if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
    echo "ERROR_NAMESPACE_PREEXISTENTE=$ns"; exit 3
  fi
done
EVID="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$EVID"
LOG="$EVID/b2-lacp-8023ad-$(date +%Y%m%d-%H%M%S).log"
OLD_IP="$(ip -4 -o addr show dev ens33)"
OLD_ROUTES="$(ip -4 route show table main)"
OWNED=""
exec > >(tee "$LOG") 2>&1

cleanup() {
  rc=$?
  trap - EXIT INT TERM
  echo "========== LIMPIEZA EXCLUSIVA LACP =========="
  for ns in $OWNED; do
    if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      while read -r pid; do
        if [[ "$pid" =~ ^[0-9]+$ ]]; then
          sudo kill "$pid" 2>/dev/null || true
        fi
      done < <(sudo ip netns pids "$ns" 2>/dev/null || true)
    fi
  done
  sleep 0.3
  for ns in $OWNED; do
    if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      if ! sudo ip netns delete "$ns"; then
        echo "ERROR_LIMPIEZA_NS=$ns"; rc=8
      fi
    fi
  done
  if [[ "$(ip -4 -o addr show dev ens33)" == "$OLD_IP" &&
        "$(ip -4 route show table main)" == "$OLD_ROUTES" ]]; then
    echo "RED_GESTION_INTACTA=SI"
  else
    echo "RED_GESTION_INTACTA=NO"; rc=9
  fi
  for ns in "$A" "$B"; do
    if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      echo "RESIDUO_NS=$ns"; rc=10
    fi
  done
  echo "LOG_LOCAL=$LOG"
  echo "RESULTADO_B2_LACP=$rc"
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

check_bond() {
  local ns="$1" report
  report="$(sudo ip netns exec "$ns" cat /proc/net/bonding/bond0)"
  echo "$report"
  grep -Fq 'IEEE 802.3ad' <<< "$report" || {
    echo "ERROR_BOND_NO_ES_8023AD=$ns"; return 5;
  }
  grep -Fq 'MII Status: up' <<< "$report" || {
    echo "ERROR_BOND_NO_UP=$ns"; return 5;
  }
  echo "BOND_8023AD_$ns=OK"
}
# Consultar el agregador ACTIVO (no solo cantidad de veth configurados).
wait_active_ports() {
  local ns="$1" wanted="$2" i report
  for i in $(seq 1 20); do
    report="$(sudo ip netns exec "$ns" cat /proc/net/bonding/bond0 2>/dev/null || true)"
    if grep -Eq "^[[:space:]]*Number of ports:[[:space:]]*$wanted[[:space:]]*$" <<< "$report"; then
      echo "LACP_AGREGADOR_$ns PUERTOS_ACTIVOS=$wanted (sondeo $i)"
      return 0
    fi
    sleep 1
  done
  echo "ERROR_AGREGADOR_$ns: puertos activos esperados=$wanted"
  echo "$report" | grep -E 'Bonding Mode:|Aggregator ID:|Number of ports:|Slave Interface:|MII Status:' || true
  return 5
}
http_check() {
  local label="$1" i response
  for i in $(seq 1 20); do
    response="$(sudo ip netns exec "$A" curl --noproxy '*' \
      -fsS --connect-timeout 2 --max-time 4 \
      http://198.18.250.2:8080/ 2>/dev/null)" && {
      if [[ "$response" == NETLAB360_LACP_HTTP_OK ]]; then
        echo "HTTP_BODY=$response"
        echo "HTTP_LACP_$label=OK (sondeo $i)"
        return 0
      fi
    }
    sleep 1
  done
  echo "ERROR_HTTP_LACP_$label"
  return 6
}

echo "========== NETLAB360 LACP REAL 802.3ad EN DOS NAMESPACES =========="
date -Is
hostname
echo "ENLACES=dos pares veth, agregacion 802.3ad con LACP en ambas puntas"
echo "SUBRED_LAB=198.18.250.0/30 (reservada para pruebas aisladas)"
echo "NOTA=esto no constituye doble NIC fisica de VMware ni LACP en un switch externo"
echo "MODULO_BONDING_VISIBLE=$(test -d /sys/module/bonding && echo SI || echo NO)"
echo "PRECHECK_LACP=OK"

for ns in "$A" "$B"; do
  sudo ip netns add "$ns"
  OWNED="$ns $OWNED"
  sudo ip -n "$ns" link set lo up
done

# Se permite autoload del driver bonding por iproute2 en namespace de prueba.
# No se activa un bond del host ni se cambia su kernel networking.
for ns in "$A" "$B"; do
  sudo ip -n "$ns" link add bond0 type bond mode 802.3ad \
    miimon 100 lacp_rate fast
done

for idx in 1 2; do
  sudo ip -n "$A" link add "a$idx" type veth peer name "b$idx"
  sudo ip -n "$A" link set "b$idx" netns "$B"
  sudo ip -n "$A" link set "a$idx" master bond0
  sudo ip -n "$B" link set "b$idx" master bond0
  sudo ip -n "$A" link set "a$idx" up
  sudo ip -n "$B" link set "b$idx" up
done

sudo ip -n "$A" addr add 198.18.250.1/30 dev bond0
sudo ip -n "$B" addr add 198.18.250.2/30 dev bond0
sudo ip -n "$A" link set bond0 up
sudo ip -n "$B" link set bond0 up
sleep 7

WEBROOT="$EVID/b2-lacp-http-root"
mkdir -p "$WEBROOT"
printf 'NETLAB360_LACP_HTTP_OK\n' > "$WEBROOT/index.html"
sudo ip netns exec "$B" python3 -m http.server 8080 \
  --bind 198.18.250.2 --directory "$WEBROOT" \
  > "$EVID/b2-lacp-http-server.log" 2>&1 &
sleep 1

echo "========== INICIO CAPTURA B2_LACP_01 =========="
date -Is
echo "========== BOND A MODE Y 2 SLAVES =========="
check_bond "$A"
echo "========== BOND B MODE Y 2 SLAVES =========="
check_bond "$B"
wait_active_ports "$A" 2
wait_active_ports "$B" 2
echo "========== HTTP A TRAVES DEL BOND =========="
http_check DOS_ENLACES
echo "========== FIN CAPTURA B2_LACP_01 =========="

echo "========== FALLA CONTROLADA ENLACE A1 =========="
sudo ip -n "$A" link set a1 down
sleep 5
echo "========== INICIO CAPTURA B2_LACP_02 =========="
date -Is
echo "========== SLAVES DESPUES DE FALLA =========="
check_bond "$A"
check_bond "$B"
wait_active_ports "$A" 1
wait_active_ports "$B" 1
echo "========== SERVICIO CON UN ENLACE SOBREVIVIENTE =========="
http_check UN_ENLACE
echo "========== FIN CAPTURA B2_LACP_02 =========="

echo "========== RESTAURACION DEL ENLACE A1 =========="
sudo ip -n "$A" link set a1 up
sleep 7
echo "========== INICIO CAPTURA B2_LACP_03 =========="
date -Is
echo "========== AMBOS ENLACES DE NUEVO PRESENTES =========="
check_bond "$A"
check_bond "$B"
wait_active_ports "$A" 2
wait_active_ports "$B" 2
http_check ENLACE_RESTAURADO
echo "========== FIN CAPTURA B2_LACP_03 =========="
echo "LACP_8023AD_TRES_ESTADOS=OK"
echo "NOTA=HTTP se probo despues de estabilizar cada estado; no hay medicion de cero perdidas durante transicion"
