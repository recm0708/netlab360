#!/usr/bin/env bash
# NETLAB360 | Laboratorio: s05 lacp capacidad comparativa
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# NETLAB360 S05/P1B: rendimiento de LACP sin tope -b.
# Solo dos namespaces privados + dos veth por extremo. Nunca toca ens33/VMnet8.
# Contencion: 2 vCPU para servidor, 2 para cliente, nice +10 y timeout.
set -Eeuo pipefail
if [[ $# -ne 1 || ( "$1" != "--precheck" && "$1" != "--run" ) ]]; then
  echo "USO: bash scripts/laboratorio/s05-lacp-capacidad-comparativa.sh --precheck|--run"
  exit 2
fi
MODE="$1"
A=nl360-s05-ca
B=nl360-s05-cb
IP_A=198.18.252.1
IP_B=198.18.252.2
PORT=5216
REPO="$HOME/proyectos/netlab360"
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-p1b"
OWNED=""
section() { printf '\n========== %s ==========\n' "$1"; }
die() { printf 'S05_P1B_ERROR=%s\n' "$*" >&2; exit 2; }

preflight() {
  [[ "$(hostname)" == netlab360-lab && "$(id -u)" -ne 0 ]] ||
    die "Host o usuario equivocado"
  for t in ip iperf3 python3 git sudo modinfo taskset timeout nice ping; do
    command -v "$t" >/dev/null 2>&1 || die "No existe: $t"
  done
  [[ -d "$REPO/.git" && -z "$(git -C "$REPO" status --porcelain)" ]] ||
    die "Git tiene cambios locales"
  ip -4 -o addr show dev ens33 | grep -Fq 192.168.47.40/24 ||
    die "Direccion ens33 inesperada"
  ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' ||
    die "Gateway ens33 inesperado"
  modinfo bonding >/dev/null 2>&1 || die "Modulo bonding no disponible"
  CPU_SET="$(python3 - <<'PY'
import os
cpus=sorted(os.sched_getaffinity(0))
if len(cpus)<6: raise SystemExit("Menos de seis CPU disponibles")
print(f"{cpus[0]},{cpus[1]} {cpus[2]},{cpus[3]}")
PY
)"
  read -r SERVER_CPUS CLIENT_CPUS <<< "$CPU_SET"
  sudo -v
  for ns in "$A" "$B"; do
    if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      die "Namespace preexistente: $ns"
    fi
  done
  if ip -4 route show table all | grep -Fq '198.18.252.'; then
    die "Subred de ensayo presente en host"
  fi
  memory="$(free -b | awk '/^Mem:/ {print $7}')"
  if [[ "$memory" =~ ^[0-9]+$ ]] && (( memory < 2147483648 )); then
    die "Memoria disponible < 2 GiB"
  fi
  echo "S05_P1B_PRECHECK_GESTION_GIT=OK"
  echo "S05_P1B_NAMESPACE=LIBRES"
  echo "S05_P1B_CPU_SERVIDOR=$SERVER_CPUS"
  echo "S05_P1B_CPU_CLIENTE=$CLIENT_CPUS"
  echo "S05_P1B_IPERF3_SIN_LIMITADOR_B=SI"
  echo "S05_P1B_LIMITACION=AFINIDAD_4_VCPU_EN_TOTAL"
  echo "S05_P1B_RED_GESTION_PROTEGIDA=SI"
}

section "S05 P1B PRECHECK"
preflight
if [[ "$MODE" == --precheck ]]; then
  echo "S05_P1B_PRECHECK=OK_SIN_CAMBIOS"; exit 0
fi
umask 077
mkdir -p "$DIR"
LOG="$DIR/S05_P1B_$(date +%Y%m%d-%H%M%S).log"
BEFORE_ADDR="$(ip -4 -o addr show dev ens33)"
BEFORE_ROUTES="$(ip -4 route show table main)"
exec > >(tee "$LOG") 2>&1
cleanup() {
  rc=$?
  trap - EXIT INT TERM
  section "INICIO_CAPTURA_S05_P1B_05_POSTCHECK"
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
      sudo -n ip netns delete "$ns" || rc=8
    fi
  done
  if [[ "$(ip -4 -o addr show dev ens33)" == "$BEFORE_ADDR" &&
        "$(ip -4 route show table main)" == "$BEFORE_ROUTES" ]]; then
    echo "S05_P1B_RED_GESTION_INTACTA=SI"
  else
    echo "S05_P1B_RED_GESTION_INTACTA=NO"; rc=9
  fi
  for ns in "$A" "$B"; do
    if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
      echo "S05_P1B_NS_RESIDUAL=$ns"; rc=10
    fi
  done
  echo "S05_P1B_LOG_LOCAL=$LOG"
  echo "S05_P1B_JSON_DIR=$DIR"
  echo "S05_RESULTADO_P1B=$rc"
  echo "FIN_CAPTURA_S05_P1B_05_POSTCHECK"
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

ports() {
  local ns="$1" count="$2" info
  for i in $(seq 1 30); do
    info="$(sudo -n ip netns exec "$ns" cat /proc/net/bonding/bond0 2>/dev/null || true)"
    if grep -Eq "^[[:space:]]*Number of ports:[[:space:]]*$count[[:space:]]*$" <<< "$info"; then
      printf 'S05_P1B_%s_PUERTOS_ACTIVOS=%s\n' "$ns" "$count"
      return 0
    fi
    sleep 1
  done
  echo "$info" | grep -E 'Bonding Mode:|MII Status:|Number of ports:' || true
  die "Puertos agregados no son $count en $ns"
}
tx() {
  sudo -n ip -n "$A" -j -s link show dev "$1" |
    python3 -c 'import sys,json; x=json.load(sys.stdin)[0]; s=x.get("stats64") or x.get("stats") or {}; print(s.get("tx",{}).get("bytes",-1))'
}
report() {
  python3 - "$1" "$2" "$3" <<'PY'
import json, sys
path, name, count = sys.argv[1:]
with open(path, encoding="utf-8") as stream:
    d=json.load(stream)
if d.get("error"): raise SystemExit("IPERF3_ERROR="+str(d["error"]))
end=d.get("end") or {}
rx=(end.get("sum_received") or {}).get("bits_per_second")
streams=len(end.get("streams") or [])
if rx is None or streams != int(count):
    raise SystemExit("IPERF3_RESULTADO_INCOMPLETO="+name)
print(f"S05_P1B_{name}_RX_MBPS={rx/1e6:.2f}")
print(f"S05_P1B_{name}_FLUJOS={streams}")
print(f"S05_P1B_{name}_RETX={(end.get('sum_sent') or {}).get('retransmits','NO_REPORTADO')}")
cpu=end.get("cpu_utilization_percent") or {}
print(f"S05_P1B_{name}_CPU_IPERF_LOCAL_PCT={cpu.get('host_total','NO_REPORTADO')}")
print(f"S05_P1B_{name}_CPU_IPERF_REMOTA_PCT={cpu.get('remote_total','NO_REPORTADO')}")
PY
}
measure() {
  local label="$1" count="$2" c1 c2 d1 d2
  c1="$(tx s5c1)"; c2="$(tx s5c2)"
  sudo -n ip netns exec "$A" timeout --signal=INT --kill-after=5s 25s \
    taskset -c "$CLIENT_CPUS" nice -n 10 \
    iperf3 -c "$IP_B" -B "$IP_A" -p "$PORT" -P "$count" \
      -t 8 -O 1 -J > "$DIR/$label.json"
  d1="$(tx s5c1)"; d2="$(tx s5c2)"
  report "$DIR/$label.json" "$label" "$count"
  if (( c1 >= 0 && c2 >= 0 && d1 >= c1 && d2 >= c2 )); then
    printf 'S05_P1B_%s_C1_TX_BYTES=%d\n' "$label" "$((d1-c1))"
    printf 'S05_P1B_%s_C2_TX_BYTES=%d\n' "$label" "$((d2-c2))"
  else
    printf 'S05_P1B_%s_CONTADORES=NO_VERIFICABLES\n' "$label"
  fi
}
section "S05 P1B CREACION DE TOPOLOGIA AISLADA"
date -Is
echo "S05_P1B_DOMINIO=198.18.252.0/30_SOLO_NS"
echo "S05_P1B_SIN_LIMITADOR_IPERF=SI"
echo "S05_P1B_ADVERTENCIA=solo_rendimiento_virtual_con_CPU_controlada"
for ns in "$A" "$B"; do
  sudo -n ip netns add "$ns"
  OWNED="$ns $OWNED"
  sudo -n ip -n "$ns" link set lo up
  sudo -n ip -n "$ns" link add bond0 type bond mode 802.3ad miimon 100 lacp_rate fast
  sudo -n ip -n "$ns" link set bond0 type bond xmit_hash_policy layer3+4
done
for i in 1 2; do
  sudo -n ip -n "$A" link add "s5c$i" type veth peer name "s5d$i"
  sudo -n ip -n "$A" link set "s5d$i" netns "$B"
  sudo -n ip -n "$A" link set "s5c$i" master bond0
  sudo -n ip -n "$B" link set "s5d$i" master bond0
  sudo -n ip -n "$A" link set "s5c$i" up
  sudo -n ip -n "$B" link set "s5d$i" up
done
sudo -n ip -n "$A" addr add "$IP_A/30" dev bond0
sudo -n ip -n "$B" addr add "$IP_B/30" dev bond0
sudo -n ip -n "$A" link set bond0 up
sudo -n ip -n "$B" link set bond0 up
ports "$A" 2
ports "$B" 2
sudo -n ip netns exec "$A" ping -c 2 -W 2 "$IP_B"
sudo -n ip netns exec "$B" taskset -c "$SERVER_CPUS" nice -n 10 \
  iperf3 -s -B "$IP_B" -p "$PORT" > "$DIR/servidor.log" 2>&1 &
SERVER_PID=$!
sleep 2
kill -0 "$SERVER_PID" || die "Servidor iperf3 no iniciado"

section "INICIO_CAPTURA_S05_P1B_01_UN_FLUJO_DOS"
measure UN_FLUJO_DOS 1
echo "FIN_CAPTURA_S05_P1B_01_UN_FLUJO_DOS"

section "INICIO_CAPTURA_S05_P1B_02_OCHO_DOS"
measure OCHO_DOS 8
echo "FIN_CAPTURA_S05_P1B_02_OCHO_DOS"

section "INICIO_CAPTURA_S05_P1B_03_OCHO_UNO"
sudo -n ip -n "$A" link set s5c1 down
ports "$A" 1
ports "$B" 1
measure OCHO_UNO 8
echo "FIN_CAPTURA_S05_P1B_03_OCHO_UNO"

section "INICIO_CAPTURA_S05_P1B_04_OCHO_RETORNO"
sudo -n ip -n "$A" link set s5c1 up
ports "$A" 2
ports "$B" 2
measure OCHO_RETORNO 8
echo "S05_P1B_LACP_2_1_2=OK"
echo "FIN_CAPTURA_S05_P1B_04_OCHO_RETORNO"
