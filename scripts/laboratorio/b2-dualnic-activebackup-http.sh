#!/usr/bin/env bash
# NETLAB360 | Laboratorio: b2 dualnic activebackup http
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# NETLAB360 B2 — Servidor dual-NIC virtual: bond active-backup con dos enlaces.
# Todos los cambios se limitan a nl360-dnica/nl360-dnicb, NO a ens33.
set -Eeuo pipefail
[[ "$#" -eq 1 && "$1" == "--snapshot-confirmado" ]] || { echo "USO: $0 --snapshot-confirmado"; exit 2; }
[[ "$(hostname)" == "netlab360-lab" && "$(id -u)" -ne 0 ]] || { echo "ERROR_HOST_O_USUARIO"; exit 2; }
cd "$HOME/proyectos/netlab360"
sudo -v
for cmd in ip python3 curl grep git sudo; do command -v "$cmd" >/dev/null || { echo "HERRAMIENTA_FALTANTE=$cmd"; exit 2; }; done
ip -4 -br addr show ens33 | grep -Fq "192.168.47.40/24" || { echo "ERROR_IP_ADMIN"; exit 2; }
ip -4 route show default | grep -Fq "default via 192.168.47.2 dev ens33" || { echo "ERROR_GW_ADMIN"; exit 2; }
A=nl360-dnica
B=nl360-dnicb
for n in "$A" "$B"; do
 if sudo ip netns list | awk '{print $1}' | grep -Fxq "$n"; then echo "ERROR_NS_PREEXISTENTE=$n"; exit 3; fi
done
EVID="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$EVID"
LOG="$EVID/b2-dualnic-activebackup-$(date +%Y%m%d-%H%M%S).log"
OLDIP="$(ip -4 -o addr show dev ens33)"
OLDROUTES="$(ip -4 route show table main)"
OWNED=""
exec > >(tee "$LOG") 2>&1
cleanup() {
 rc=$?
 trap - EXIT INT TERM
 echo "========== LIMPIEZA EXCLUSIVA DUAL-NIC =========="
 for ns in $OWNED; do
  if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
   while read -r pid; do
    if [[ "$pid" =~ ^[0-9]+$ ]]; then sudo kill "$pid" 2>/dev/null || true; fi
   done < <(sudo ip netns pids "$ns" 2>/dev/null || true)
  fi
 done
 sleep 0.3
 for ns in $OWNED; do
  if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
   sudo ip netns delete "$ns" || { echo "ERROR_CLEANUP=$ns"; rc=8; }
  fi
 done
 if [[ "$(ip -4 -o addr show dev ens33)" == "$OLDIP" &&
       "$(ip -4 route show table main)" == "$OLDROUTES" ]]; then
  echo "RED_GESTION_INTACTA=SI"
 else
  echo "RED_GESTION_INTACTA=NO"
  rc=9
 fi
 for ns in "$A" "$B"; do
  if sudo ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
   echo "RESIDUO_NS=$ns"
   rc=10
  fi
 done
 echo "LOG_LOCAL=$LOG"
 echo "RESULTADO_B2_DUALNIC=$rc"
 exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

bond_info() {
 local n="$1" expected="$2" output
 output="$(sudo ip netns exec "$n" cat /proc/net/bonding/bond0)"
 echo "$output" | grep -E 'Bonding Mode:|Currently Active Slave:|MII Status:|Slave Interface:|Link Failure Count:' || true
 grep -Fq "Bonding Mode: fault-tolerance (active-backup)" <<< "$output" || {
  echo "ERROR_MODO_BOND=$n"; return 5;
 }
 grep -Fq "Currently Active Slave: $expected" <<< "$output" || {
  echo "ERROR_NIC_ACTIVA=$n esperado=$expected"; return 5;
 }
 grep -Fq "MII Status: up" <<< "$output" || {
  echo "ERROR_BOND_DOWN=$n"; return 5;
 }
 local num
 num="$(grep -c '^Slave Interface:' <<< "$output")"
 [[ "$num" -eq 2 ]] || { echo "ERROR_SLAVES=$n num=$num"; return 5; }
 echo "DUAL_NIC_${n}_ACTIVA=$expected"
 echo "DUAL_NIC_${n}_MIEMBROS=$num"
}
http_test() {
 local phase="$1" n result
 for n in $(seq 1 15); do
  if result="$(sudo ip netns exec "$A" curl --noproxy '*' -fsS \
    --connect-timeout 2 --max-time 4 http://198.18.251.2:8080/ 2>/dev/null)"; then
   if [[ "$result" == "NETLAB360_DUAL_NIC_HTTP_OK" ]]; then
    echo "HTTP_BODY=$result"
    echo "HTTP_DUALNIC_$phase=OK (sondeo $n)"
    return 0
   fi
  fi
  sleep 1
 done
 echo "ERROR_HTTP_DUALNIC_$phase"
 return 6
}
echo "========== NETLAB360 SERVIDOR DUAL NIC ACTIVE-BACKUP =========="
date -Is; hostname
echo "DATO=dos enlaces veth en namespaces de prueba, NO NIC fisicas VMware"
echo "SUBRED_LAB=198.18.251.0/30, aislada de red ens33"
for ns in "$A" "$B"; do
 sudo ip netns add "$ns"
 OWNED="$ns $OWNED"
 sudo ip -n "$ns" link set lo up
 sudo ip -n "$ns" link add bond0 type bond mode active-backup miimon 100
done
for id in 1 2; do
 sudo ip -n "$A" link add "a$id" type veth peer name "b$id"
 sudo ip -n "$A" link set "b$id" netns "$B"
 sudo ip -n "$A" link set "a$id" master bond0
 sudo ip -n "$B" link set "b$id" master bond0
 sudo ip -n "$A" link set "a$id" up
 sudo ip -n "$B" link set "b$id" up
done
sudo ip -n "$A" addr add 198.18.251.1/30 dev bond0
sudo ip -n "$B" addr add 198.18.251.2/30 dev bond0
sudo ip -n "$A" link set bond0 up
sudo ip -n "$B" link set bond0 up
sleep 3

WEBROOT="$EVID/b2-dualnic-http-root"
mkdir -p "$WEBROOT"
printf 'NETLAB360_DUAL_NIC_HTTP_OK\n' > "$WEBROOT/index.html"
sudo ip netns exec "$B" python3 -m http.server 8080 --bind 198.18.251.2 \
  --directory "$WEBROOT" > "$EVID/b2-dualnic-http-server.log" 2>&1 &
sleep 1

echo "========== INICIO CAPTURA B2_DUALNIC_01 =========="
date -Is
echo "========== DOS NIC DISPONIBLES, PRIMARIA ACTIVA =========="
bond_info "$A" a1
bond_info "$B" b1
http_test PRIMARIA
echo "========== FIN CAPTURA B2_DUALNIC_01 =========="

echo "========== FALLA CONTROLADA NIC PRIMARIA =========="
sudo ip -n "$A" link set a1 down
sleep 3
echo "========== INICIO CAPTURA B2_DUALNIC_02 =========="
date -Is
echo "========== SEGUNDA NIC ASUME TRAFICO =========="
bond_info "$A" a2
bond_info "$B" b2
http_test RESPALDO
echo "========== FIN CAPTURA B2_DUALNIC_02 =========="

echo "========== RESTAURACION NIC A1 =========="
sudo ip -n "$A" link set a1 up
sleep 3
echo "========== INICIO CAPTURA B2_DUALNIC_03 =========="
date -Is
echo "========== AMBAS NIC DISPONIBLES; RESPALDO AUN ACTIVO =========="
bond_info "$A" a2
bond_info "$B" b2
http_test RECUPERADA
echo "DUALNIC_ACTIVE_BACKUP_TRES_ESTADOS=OK"
echo "NOTA=sin failback preferido; NIC a1 vuelve disponible pero activa a2; no es NIC de VM fisica"
echo "========== FIN CAPTURA B2_DUALNIC_03 =========="
