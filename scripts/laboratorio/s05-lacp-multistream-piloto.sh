#!/usr/bin/env bash
# NETLAB360 | Laboratorio: s05 lacp multistream piloto
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# NETLAB360 S05/P1: LACP multistream acotado, aislado de ens33/VMnet8.
# --precheck solo inspecciona; --run crea y retira dos namespaces propios.
set -Eeuo pipefail
if [[ $# -ne 1 || ( "$1" != "--precheck" && "$1" != "--run" ) ]]; then
  echo "USO: bash scripts/laboratorio/s05-lacp-multistream-piloto.sh --precheck|--run"; exit 2
fi
ACTION="$1"
A=nl360-s05-la
B=nl360-s05-lb
IPA=198.18.251.1
IPB=198.18.251.2
BASE="$HOME/netlab360-bootstrap/s05/evidencias/lacp-p1"
ROOT="$HOME/proyectos/netlab360"
OWNED=""
section() { printf '\n========== %s ==========\n' "$1"; }
fail() { echo "S05_ERROR=$*" >&2; exit 2; }
precheck() {
  [[ "$(hostname)" == netlab360-lab && "$(id -u)" -ne 0 ]] || fail "Identidad de host/usuario incorrecta"
  for tool in ip iperf3 python3 git sudo modinfo ping awk grep; do
    command -v "$tool" >/dev/null 2>&1 || fail "Dependencia ausente: $tool"
  done
  [[ -d "$ROOT/.git" && -z "$(git -C "$ROOT" status --porcelain)" ]] || fail "Git no limpio"
  ip -4 -o addr show dev ens33 | grep -Fq '192.168.47.40/24' || fail "ens33 IP alterada"
  ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' || fail "Ruta de gestion alterada"
  modinfo bonding >/dev/null 2>&1 || fail "Modulo bonding no encontrado"
  sudo -v
  for ns in "$A" "$B"; do
    if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      fail "Namespace existente: $ns"
    fi
  done
  if ip -4 route show table all | grep -Fq '198.18.251.'; then
    fail "La subred de ensayo aparece en rutas del host"
  fi
  echo "S05_PRECHECK_IDENTIDAD_RED_GIT=OK"
  echo "S05_PRECHECK_NAMESPACES=LIBRES"
  echo "S05_TRABAJO_LIMITADO=120_Mbps_por_flujo"
  echo "S05_ENS33_NO_TOCAR=SI"
}
section "S05 P1 PRECHECK LACP"
precheck
if [[ "$ACTION" == "--precheck" ]]; then
  echo "S05_P1_PRECHECK=OK_SIN_CAMBIOS_EN_INFRAESTRUCTURA"; exit 0
fi
umask 077
mkdir -p "$BASE"
LOG="$BASE/S05_P1_$(date +%Y%m%d-%H%M%S).log"
OLD_IP="$(ip -4 -o addr show dev ens33)"
OLD_ROUTES="$(ip -4 route show table main)"
exec > >(tee "$LOG") 2>&1
cleanup() {
  code=$?
  trap - EXIT INT TERM
  section "INICIO_CAPTURA_S05_LACP_04_LIMPIEZA"
  for ns in $OWNED; do
    if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      while read -r pid; do
        if [[ "$pid" =~ ^[0-9]+$ ]]; then sudo -n kill "$pid" 2>/dev/null || true; fi
      done < <(sudo -n ip netns pids "$ns" 2>/dev/null || true)
    fi
  done
  sleep 1
  for ns in $OWNED; do
    if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      sudo -n ip netns delete "$ns" || code=8
    fi
  done
  if [[ "$(ip -4 -o addr show dev ens33)" == "$OLD_IP" &&
        "$(ip -4 route show table main)" == "$OLD_ROUTES" ]]; then
    echo "S05_RED_GESTION_INTACTA=SI"
  else
    echo "S05_RED_GESTION_INTACTA=NO"; code=9
  fi
  for ns in "$A" "$B"; do
    if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      echo "S05_NAMESPACE_RESIDUAL=$ns"; code=10
    fi
  done
  echo "S05_P1_LOG_LOCAL=$LOG"
  echo "S05_P1_JSON_DIR=$BASE"
  echo "S05_RESULTADO_P1=$code"
  echo "FIN_CAPTURA_S05_LACP_04_LIMPIEZA"
  exit "$code"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
ports() {
  local ns="$1" count="$2" info
  for i in $(seq 1 30); do
    info="$(sudo -n ip netns exec "$ns" cat /proc/net/bonding/bond0 2>/dev/null || true)"
    if grep -Eq "^[[:space:]]*Number of ports:[[:space:]]*$count[[:space:]]*$" <<< "$info"; then
      printf 'S05_AGREGADOR_%s_PUERTOS=%s\n' "$ns" "$count"; return 0
    fi
    sleep 1
  done
  echo "$info" | grep -E 'Bonding Mode:|MII Status:|Number of ports:' || true
  fail "Esperados $count puertos activos en $ns"
}
bond() {
  echo "S05_BOND=$1"
  sudo -n ip netns exec "$1" cat /proc/net/bonding/bond0 |
    grep -E 'Bonding Mode:|Transmit Hash Policy:|MII Status:|LACP active:|Number of ports:|Slave Interface:'
}
tx() {
  sudo -n ip -n "$A" -j -s link show dev "$1" |
    python3 -c 'import json,sys; x=json.load(sys.stdin)[0]; s=x.get("stats64") or x.get("stats") or {}; print(s.get("tx",{}).get("bytes",-1))'
}
delta() {
  if (( $2 >= 0 && $3 >= 0 && $4 >= $2 && $5 >= $3 )); then
    printf 'S05_%s_A1_TX_BYTES=%s\n' "$1" "$(( $4 - $2 ))"
    printf 'S05_%s_A2_TX_BYTES=%s\n' "$1" "$(( $5 - $3 ))"
  else
    printf 'S05_%s_CONTADORES=NO_VERIFICABLES\n' "$1"
  fi
}
json_report() {
  python3 - "$1" "$2" <<'PY'
import json,sys
path,label=sys.argv[1:]
with open(path,encoding="utf-8") as fh: data=json.load(fh)
if data.get("error"): raise SystemExit("ERROR_IPERF3="+str(data["error"]))
end=data.get("end") or {}
received=end.get("sum_received") or end.get("sum") or {}
print(f"S05_{label}_RX_MBPS={received.get('bits_per_second',0)/1e6:.2f}")
print(f"S05_{label}_FLUJOS={len(end.get('streams') or [])}")
print(f"S05_{label}_RETRANSMISIONES_TCP={(end.get('sum_sent') or {}).get('retransmits','NO_REPORTADO')}")
if label=="FALLA_RETORNO":
    for it in data.get("intervals",[]):
        s=it.get("sum") or {}
        print(f"S05_INTERVALO={s.get('start','?')}-{s.get('end','?')} MBPS={s.get('bits_per_second',0)/1e6:.2f}")
PY
}
section "CREACION DE DOMINIO S05 AISLADO"
echo "S05_TIPO=IEEE802.3ad en veth, no NIC fisica"
for ns in "$A" "$B"; do
  sudo -n ip netns add "$ns"
  OWNED="$ns $OWNED"
  sudo -n ip -n "$ns" link set lo up
  sudo -n ip -n "$ns" link add bond0 type bond mode 802.3ad miimon 100 lacp_rate fast
  sudo -n ip -n "$ns" link set bond0 type bond xmit_hash_policy layer3+4
done
for i in 1 2; do
  sudo -n ip -n "$A" link add "s5a$i" type veth peer name "s5b$i"
  sudo -n ip -n "$A" link set "s5b$i" netns "$B"
  sudo -n ip -n "$A" link set "s5a$i" master bond0
  sudo -n ip -n "$B" link set "s5b$i" master bond0
  sudo -n ip -n "$A" link set "s5a$i" up
  sudo -n ip -n "$B" link set "s5b$i" up
done
sudo -n ip -n "$A" addr add "$IPA/30" dev bond0
sudo -n ip -n "$B" addr add "$IPB/30" dev bond0
sudo -n ip -n "$A" link set bond0 up
sudo -n ip -n "$B" link set bond0 up
ports "$A" 2
ports "$B" 2
sudo -n ip netns exec "$A" ping -c 2 -W 2 "$IPB"
sudo -n ip netns exec "$B" iperf3 -s -B "$IPB" -p 5215 > "$BASE/servidor.log" 2>&1 &
SERVER_PID=$!
sleep 2
kill -0 "$SERVER_PID" || fail "Servidor iperf3 no iniciado"
section "INICIO_CAPTURA_S05_LACP_01_UN_FLUJO"
bond "$A"
bond "$B"
b1="$(tx s5a1)"; b2="$(tx s5a2)"
sudo -n ip netns exec "$A" iperf3 -c "$IPB" -B "$IPA" -p 5215 -P 1 -b 120M -t 8 -O 1 -J > "$BASE/01_un_flujo.json"
a1="$(tx s5a1)"; a2="$(tx s5a2)"
json_report "$BASE/01_un_flujo.json" UN_FLUJO
delta UN_FLUJO "$b1" "$b2" "$a1" "$a2"
echo "FIN_CAPTURA_S05_LACP_01_UN_FLUJO"
section "INICIO_CAPTURA_S05_LACP_02_OCHO_FLUJOS"
b1="$(tx s5a1)"; b2="$(tx s5a2)"
sudo -n ip netns exec "$A" iperf3 -c "$IPB" -B "$IPA" -p 5215 -P 8 -b 120M -t 10 -O 1 -J > "$BASE/02_ocho_flujos.json"
a1="$(tx s5a1)"; a2="$(tx s5a2)"
json_report "$BASE/02_ocho_flujos.json" OCHO_FLUJOS
delta OCHO_FLUJOS "$b1" "$b2" "$a1" "$a2"
echo "FIN_CAPTURA_S05_LACP_02_OCHO_FLUJOS"
section "INICIO_CAPTURA_S05_LACP_03_FALLA_RETORNO"
sudo -n ip netns exec "$A" iperf3 -c "$IPB" -B "$IPA" -p 5215 -P 8 -b 120M -t 18 -i 1 -J > "$BASE/03_falla_retorno.json" 2> "$BASE/03_falla_retorno.err" &
CLIENT_PID=$!
sleep 5
echo "S05_FALLA_A1=$(date -Is)"
sudo -n ip -n "$A" link set s5a1 down
ports "$A" 1
ports "$B" 1
sleep 4
echo "S05_RETORNO_A1=$(date -Is)"
sudo -n ip -n "$A" link set s5a1 up
ports "$A" 2
ports "$B" 2
wait "$CLIENT_PID"
json_report "$BASE/03_falla_retorno.json" FALLA_RETORNO
bond "$A"
echo "S05_LACP_ESTADOS_2_1_2=OK"
echo "S05_LIMITE=intervalos de 1 segundo; no afirmar cero perdida ni capacidad maxima"
echo "FIN_CAPTURA_S05_LACP_03_FALLA_RETORNO"
