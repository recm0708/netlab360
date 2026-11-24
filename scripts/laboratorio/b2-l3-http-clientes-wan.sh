#!/usr/bin/env bash
# NETLAB360: HTTP real HQ->S1 sobre WAN-P, WAN-B y WAN-P.
# Namespace de cliente/servidor + transportes veth P2P; no altera host.
set -Eeuo pipefail
[[ "$#" -eq 1 && "$1" == "--snapshot-confirmado" ]] || { echo "USO: $0 --snapshot-confirmado"; exit 2; }
[[ "$(hostname)" == "netlab360-lab" && "$(id -u)" -ne 0 ]] || { echo "ERROR_HOST_O_USUARIO"; exit 3; }
cd "$HOME/proyectos/netlab360"
sudo -v
for cmd in ip nsenter docker sysctl python3 curl git; do
  command -v "$cmd" >/dev/null || { echo "FALTA=$cmd"; exit 3; }
done
ip -4 -br addr show ens33 | grep -Fq 192.168.47.40/24 || { echo "ERROR_IP_HOST"; exit 3; }
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' || { echo "ERROR_GW_HOST"; exit 3; }
HC=nl360-e2e-hq
SS=nl360-e2e-s1
HQR=nl360-b2-r-hq
S1R=nl360-b2-r-s1
for ns in "$HC" "$SS"; do
  sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns" && { echo "ERROR_NS_EXISTE=$ns"; exit 3; }
done
for r in "$HQR" "$S1R"; do
  if sudo docker container inspect "$r" >/dev/null 2>&1; then
    echo "ERROR_ROUTER_B2_PREEXISTENTE=$r"; exit 3
  fi
done
[[ ! -e "$HOME/netlab360-bootstrap/estado-b2-dualwan" ]] || { echo "ERROR_ESTADO_B2_PREVIO"; exit 3; }
EVID="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$EVID"
LOG="$EVID/b2-l3-http-wan-$(date +%Y%m%d-%H%M%S).log"
OLDIP="$(ip -4 -o addr show dev ens33)"
OLDROUTE="$(ip -4 route show table main)"
UP=0
exec > >(tee "$LOG") 2>&1
rp() {
  local router="$1"
  shift
  sudo nsenter -t "$(sudo docker inspect -f '{{.State.Pid}}' "$router")" -n "$@"
}
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  echo "========== LIMPIEZA EXCLUSIVA HTTP WAN =========="
  for ns in "$HC" "$SS"; do
    if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      while read -r pid; do
        if [[ "$pid" =~ ^[0-9]+$ ]]; then sudo kill "$pid" 2>/dev/null || true; fi
      done < <(sudo ip netns pids "$ns" 2>/dev/null || true)
      if ! sudo ip netns delete "$ns"; then echo "LIMPIEZA_NS_ERROR=$ns"; rc=8; fi
    fi
  done
  if [[ "$UP" -eq 1 ]]; then
    if ! bash scripts/laboratorio/b2-dualwan-ospf.sh down; then
      echo "ERROR_LIMPIEZA_FRR"; rc=9
    fi
  fi
  if [[ "$(ip -4 -o addr show dev ens33)" == "$OLDIP" && "$(ip -4 route show table main)" == "$OLDROUTE" ]]; then
    echo "RED_GESTION_INTACTA=SI"
  else
    echo "RED_GESTION_INTACTA=NO"; rc=10
  fi
  echo "LOG_LOCAL=$LOG"
  echo "RESULTADO_B2_L3_HTTP_WAN=$rc"
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
check_route() {
  local dev="$1" a b n
  for n in $(seq 1 65); do
    a="$(rp "$HQR" ip -4 route get 10.71.10.20 2>&1 || true)"
    b="$(rp "$S1R" ip -4 route get 10.70.10.10 2>&1 || true)"
    if [[ "$a" == *"dev $dev"* && "$b" == *"dev $dev"* ]]; then
      echo "FIB_HQ=$a"; echo "FIB_S1=$b"; echo "RUTAS_SIMETRICAS_$dev=OK"; return 0
    fi
    sleep 1
  done
  echo "ERROR_RUTAS_$dev"; echo "FIB_HQ=$a"; echo "FIB_S1=$b"; return 6
}
check_http() {
  local phase="$1" body
  body="$(sudo ip netns exec "$HC" curl --noproxy '*' -fsS --max-time 8 http://10.71.10.20:8080/)"
  echo "HTTP_BODY=$body"
  [[ "$body" == NETLAB360_HTTP_S1_SERVICIO_REAL_OK ]] || return 7
  echo "HTTP_$phase=OK"
}
echo "========== LAB B2-L3 CLIENTE HQ A SERVIDOR HTTP S1 =========="
date -Is; hostname
echo "CLIENTE=10.70.10.10/32 | SERVIDOR=10.71.10.20/32:8080"
echo "AVISO: acceso a hosts mediante veth punto-a-punto y rutas /32; NO significa VLAN switch conectada a WAN"
bash scripts/laboratorio/b2-dualwan-ospf.sh precheck
bash scripts/laboratorio/b2-dualwan-ospf.sh up --snapshot-confirmado
UP=1
sudo ip netns add "$HC"
sudo ip netns add "$SS"
sudo ip -n "$HC" link set lo up
sudo ip -n "$SS" link set lo up
# Ambos extremos nacen en namespaces de laboratorio, nunca host.
sudo ip -n "$HC" link add eth0 type veth peer name e2ehq
sudo ip -n "$HC" link set e2ehq netns "$(sudo docker inspect -f '{{.State.Pid}}' "$HQR")"
sudo ip -n "$SS" link add eth0 type veth peer name e2es1
sudo ip -n "$SS" link set e2es1 netns "$(sudo docker inspect -f '{{.State.Pid}}' "$S1R")"
rp "$HQR" ip addr add 169.254.70.1/30 dev e2ehq
rp "$S1R" ip addr add 169.254.71.1/30 dev e2es1
rp "$HQR" ip link set e2ehq up
rp "$S1R" ip link set e2es1 up
sudo ip -n "$HC" addr add 169.254.70.2/30 dev eth0
sudo ip -n "$SS" addr add 169.254.71.2/30 dev eth0
sudo ip -n "$HC" addr add 10.70.10.10/32 dev lo
sudo ip -n "$SS" addr add 10.71.10.20/32 dev lo
sudo ip -n "$HC" link set eth0 up
sudo ip -n "$SS" link set eth0 up
sudo ip -n "$HC" route add 10.71.10.0/24 via 169.254.70.1 dev eth0 src 10.70.10.10
sudo ip -n "$SS" route add 10.70.10.0/24 via 169.254.71.1 dev eth0 src 10.71.10.20
rp "$HQR" ip route add 10.70.10.10/32 via 169.254.70.2 dev e2ehq
rp "$S1R" ip route add 10.71.10.20/32 via 169.254.71.2 dev e2es1
rp "$HQR" sysctl -qw net.ipv4.ip_forward=1
rp "$S1R" sysctl -qw net.ipv4.ip_forward=1
WEB="$EVID/b2-l3-http-s1-root"
mkdir -p "$WEB"
printf 'NETLAB360_HTTP_S1_SERVICIO_REAL_OK\n' > "$WEB/index.html"
sudo ip netns exec "$SS" python3 -m http.server 8080 --bind 10.71.10.20 \
  --directory "$WEB" > "$EVID/b2-l3-http-s1-server.log" 2>&1 &
sleep 1
echo "========== INICIO CAPTURA B2_L3_01 =========="
date -Is
check_route wan-p
sudo ip -n "$HC" -4 -br addr
sudo ip -n "$SS" -4 -br addr
check_http WAN_PRINCIPAL
echo "========== FIN CAPTURA B2_L3_01 =========="
bash scripts/laboratorio/b2-dualwan-ospf.sh fail
echo "========== INICIO CAPTURA B2_L3_02 =========="
date -Is
check_route wan-b
check_http WAN_RESPALDO
echo "========== FIN CAPTURA B2_L3_02 =========="
bash scripts/laboratorio/b2-dualwan-ospf.sh restore
echo "========== INICIO CAPTURA B2_L3_03 =========="
date -Is
check_route wan-p
check_http WAN_RESTAURADA
echo "========== FIN CAPTURA B2_L3_03 =========="
echo "B2_L3_HTTP_TRES_ESTADOS=OK"
echo "NOTA: al salir se retiran procesos y namespaces propios, luego FRR B2."
