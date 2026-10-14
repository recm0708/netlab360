#!/usr/bin/env bash
# NETLAB360 B2-L2: HTTP real entre VLAN 110/120 + ACL aislada en router.
# Solo opera namespaces nl360-acl*, NO toca ens33, gateway ni nftables del host.
set -Eeuo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "BLOQUEADO: usar --snapshot-confirmado"; exit 2
fi
if [[ "$1" != "--snapshot-confirmado" ]]; then
  echo "BLOQUEADO: usar --snapshot-confirmado"; exit 2
fi
[[ "$(hostname)" == "netlab360-lab" ]] || { echo "ERROR_HOSTNAME"; exit 2; }
[[ "$(id -u)" -ne 0 ]] || { echo "ERROR: ejecutar con usuario normal"; exit 2; }
cd "$HOME/proyectos/netlab360"
sudo -v
for tool in ip bridge nft python3 curl sysctl git sudo; do
  command -v "$tool" >/dev/null || { echo "HERRAMIENTA_FALTANTE=$tool"; exit 2; }
done
python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml
ip -4 -br address show ens33 | grep -Fq "192.168.47.40/24" || { echo "ERROR_IP_GESTION"; exit 3; }
ip -4 route show default | grep -Fq "default via 192.168.47.2 dev ens33" || { echo "ERROR_GATEWAY"; exit 3; }

A=nl360-acla
B=nl360-aclb
R=nl360-aclr
C=nl360-aclc
S=nl360-acls
NAMES="$A $B $R $C $S"
for ns in $NAMES; do
  if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
    echo "ERROR_NAMESPACE_PREEXISTENTE=$ns"
    exit 3
  fi
done

EVID="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$EVID"
LOG="$EVID/b2-l2-acl-http-$(date +%Y%m%d-%H%M%S).log"
ORIG_IP="$(ip -4 -o addr show ens33)"
ORIG_ROUTE="$(ip -4 route show table main)"
OWNED=""
exec > >(tee "$LOG") 2>&1

cleanup() {
  rc=$?
  trap - EXIT
  echo "========== LIMPIEZA B2-L2 ACL HTTP =========="
  # Se eliminan exclusivamente procesos en namespaces creados por este ensayo.
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
    if ! sudo ip netns delete "$ns" 2>/dev/null; then
      echo "ERROR_LIMPIEZA_NAMESPACE=$ns"
      rc=7
    fi
  done
  if [[ "$(ip -4 -o addr show ens33)" == "$ORIG_IP" &&
        "$(ip -4 route show table main)" == "$ORIG_ROUTE" ]]; then
    echo "RED_GESTION_INTACTA=SI"
  else
    echo "RED_GESTION_INTACTA=NO"
    rc=8
  fi
  for ns in $NAMES; do
    if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      echo "RESIDUO_NAMESPACE=$ns"
      rc=9
    fi
  done
  echo "LOG_LOCAL=$LOG"
  echo "RESULTADO_B2_L2_ACL_HTTP=$rc"
  exit "$rc"
}
trap cleanup EXIT

echo "========== B2-L2 HTTP REAL + ACL EN NAMESPACE =========="
date -Is
hostname
echo "TOPOLOGIA=HQ:VLAN110-CLIENTE->ROUTER-ACL->VLAN120-SERVIDOR"
echo "ENLACES=trunk SW-A<->SW-B y trunk SW-A<->R-HQ-local"
echo "IPAM_HQ_USUARIOS=10.70.10.0/24"
echo "IPAM_HQ_SERVICIOS=10.70.20.0/24"
echo "PUERTOS_HTTP=8080 permitido; 8081 bloqueado"
echo "AVISO=esta prueba no usa FRR ni demuestra conectividad HQ-S1"

for ns in $NAMES; do
  sudo ip netns add "$ns"
  OWNED="$ns $OWNED"
  sudo ip -n "$ns" link set lo up
done

for sw in "$A" "$B"; do
  sudo ip -n "$sw" link add br0 type bridge vlan_filtering 1
  sudo ip -n "$sw" link set br0 up
done

access() {
  local sw="$1" port="$2" peer="$3" dest="$4" vlan="$5" ipaddr="$6"
  sudo ip -n "$sw" link add "$port" type veth peer name "$peer"
  sudo ip -n "$sw" link set "$peer" netns "$dest"
  sudo ip -n "$dest" link set "$peer" name eth0
  sudo ip -n "$sw" link set "$port" master br0
  sudo ip netns exec "$sw" bridge vlan del dev "$port" vid 1 >/dev/null 2>&1 || true
  sudo ip netns exec "$sw" bridge vlan add dev "$port" vid "$vlan" pvid untagged
  sudo ip -n "$sw" link set "$port" up
  sudo ip -n "$dest" addr add "$ipaddr" dev eth0
  sudo ip -n "$dest" link set eth0 up
}

access "$A" a110 c-peer "$C" 110 10.70.10.10/24
access "$B" b120 s-peer "$S" 120 10.70.20.20/24

trunk_port() {
  local sw="$1" port="$2"
  sudo ip -n "$sw" link set "$port" master br0
  sudo ip netns exec "$sw" bridge vlan del dev "$port" vid 1 >/dev/null 2>&1 || true
  sudo ip netns exec "$sw" bridge vlan add dev "$port" vid 110
  sudo ip netns exec "$sw" bridge vlan add dev "$port" vid 120
  sudo ip -n "$sw" link set "$port" up
}

# Trunk 802.1Q entre SW-A y SW-B.
sudo ip -n "$A" link add tr-ab type veth peer name tr-ba
sudo ip -n "$A" link set tr-ba netns "$B"
trunk_port "$A" tr-ab
trunk_port "$B" tr-ba

# Trunk 802.1Q hacia router aislado con subinterfaces VLAN.
sudo ip -n "$A" link add tr-ar type veth peer name r-peer
sudo ip -n "$A" link set r-peer netns "$R"
sudo ip -n "$R" link set r-peer name eth0
trunk_port "$A" tr-ar
sudo ip -n "$R" link set eth0 up
sudo ip -n "$R" link add link eth0 name eth0.110 type vlan id 110
sudo ip -n "$R" link add link eth0 name eth0.120 type vlan id 120
sudo ip -n "$R" addr add 10.70.10.1/24 dev eth0.110
sudo ip -n "$R" addr add 10.70.20.1/24 dev eth0.120
sudo ip -n "$R" link set eth0.110 up
sudo ip -n "$R" link set eth0.120 up

sudo ip -n "$C" route add default via 10.70.10.1 dev eth0
sudo ip -n "$S" route add default via 10.70.20.1 dev eth0
# net.ipv4.ip_forward se establece EXCLUSIVAMENTE en network namespace R.
sudo ip netns exec "$R" sysctl -qw net.ipv4.ip_forward=1

WEBROOT="$EVID/b2-l2-acl-web"
mkdir -p "$WEBROOT"
printf 'NETLAB360_HTTP_SERVICIO_HQ_VLAN120_OK\n' > "$WEBROOT/index.html"

# Ambos servidores escuchan, para comprobar bloqueo por ACL y no por puerto cerrado.
sudo ip netns exec "$S" python3 -m http.server 8080 --bind 10.70.20.20 \
  --directory "$WEBROOT" > "$EVID/b2-l2-http-8080.log" 2>&1 &
sudo ip netns exec "$S" python3 -m http.server 8081 --bind 10.70.20.20 \
  --directory "$WEBROOT" > "$EVID/b2-l2-http-8081.log" 2>&1 &
sleep 1

echo "========== INICIO CAPTURA B2_L2_05 =========="
date -Is
echo "========== SWITCH A: VLAN ACCESS Y TRUNK =========="
sudo ip netns exec "$A" bridge vlan show
echo "========== SWITCH B: VLAN ACCESS Y TRUNK =========="
sudo ip netns exec "$B" bridge vlan show
echo "========== ROUTER: SUBINTERFACES 8021Q =========="
sudo ip -n "$R" -4 -br addr
echo "========== BASELINE SIN ACL: HTTP 8080 =========="
sudo ip netns exec "$C" curl --noproxy '*' -fsS --max-time 5 \
  http://10.70.20.20:8080/
echo "BASELINE_HTTP_8080=OK"
echo "========== BASELINE SIN ACL: HTTP 8081 =========="
sudo ip netns exec "$C" curl --noproxy '*' -fsS --max-time 5 \
  http://10.70.20.20:8081/
echo "BASELINE_HTTP_8081=OK"
echo "========== FIN CAPTURA B2_L2_05 =========="

# ACL nftables SOLO dentro de R, nunca en la network namespace de Ubuntu host.
sudo ip netns exec "$R" nft -f - <<'NFT'
table inet nl360_acl {
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related counter accept
    iifname "eth0.110" oifname "eth0.120" ip saddr 10.70.10.0/24 ip daddr 10.70.20.0/24 tcp dport 8080 counter accept
    iifname "eth0.110" oifname "eth0.120" ip saddr 10.70.10.0/24 ip daddr 10.70.20.0/24 tcp dport 8081 counter drop
  }
}
NFT

echo "========== INICIO CAPTURA B2_L2_06 =========="
date -Is
echo "========== ACL FORWARD =========="
sudo ip netns exec "$R" nft -a list chain inet nl360_acl forward
echo "========== HTTP 8080 PERMITIDO =========="
sudo ip netns exec "$C" curl --noproxy '*' -fsS --max-time 5 \
  http://10.70.20.20:8080/
echo "ACL_HTTP_8080_PERMITIDO=OK"

echo "========== CONTROL: SERVICIO 8081 ESCUCHANDO EN VLAN120 =========="
sudo ip netns exec "$S" curl --noproxy '*' -fsS --max-time 4 \
  http://10.70.20.20:8081/
echo "SERVICIO_8081_EN_VLAN120=ACTIVO"

echo "========== HTTP 8081 DENEGADO DESDE VLAN110 =========="
if sudo ip netns exec "$C" curl --noproxy '*' -sS \
  --connect-timeout 2 --max-time 4 http://10.70.20.20:8081/; then
  echo "ERROR: ACL permitio 8081"
  exit 6
else
  echo "ACL_HTTP_8081_DENEGADO=OK"
fi
echo "========== CONTADORES DE ACL =========="
sudo ip netns exec "$R" nft -a list chain inet nl360_acl forward
echo "ACL_ROUTER_NAMESPACE=OK"
echo "AVISO=inter-VLAN HQ unicamente, sin WAN HQ-S1"
echo "========== FIN CAPTURA B2_L2_06 =========="
