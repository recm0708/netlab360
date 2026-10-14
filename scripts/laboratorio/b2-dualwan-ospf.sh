#!/usr/bin/env bash
# NETLAB360 B2-L3: FRR HQ-S1 con WAN doble, aislado de VMnet8.
# Requiere Ubuntu netlab360-lab y snapshot base confirmado. No usar --privileged.
set -Eeuo pipefail
ACTION=""; CONF=""
if (( $# > 0 )); then ACTION="$1"; fi
if (( $# > 1 )); then CONF="$2"; fi
ROOT="$HOME/proyectos/netlab360"
STATE="$HOME/netlab360-bootstrap/estado-b2-dualwan"
EVID="$HOME/netlab360-bootstrap/evidencias"
IMAGE="quay.io/frrouting/frr:10.7.1"
HQ="nl360-b2-r-hq"
S1="nl360-b2-r-s1"
PID_TMPFS="/run/frr:rw,nosuid,nodev,size=16m,uid=0,gid=101,mode=0770"
CRASH_TMPFS="/var/tmp/frr:rw,nosuid,nodev,size=16m,uid=100,gid=101,mode=0770"
UP_PENDING=0; UP_COMPLETE=0
usage() { echo "Uso: bash $0 precheck | up --snapshot-confirmado | status | fail | restore | down"; }
[[ "$ACTION" =~ ^(precheck|up|status|fail|restore|down)$ ]] || { usage; exit 2; }
if [[ "$ACTION" == up && "$CONF" != --snapshot-confirmado ]]; then usage; exit 2; fi
[[ "$(hostname)" == netlab360-lab ]] || { echo "ERROR: hostname inesperado"; exit 2; }
[[ "$(id -u)" != 0 ]] || { echo "ERROR: ejecutar como usuario normal"; exit 2; }
cd "$ROOT"
mkdir -p "$EVID"
sudo -v
LOG="$EVID/15-b2-dualwan-$ACTION-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1
echo "========== NETLAB360 B2-L3: $ACTION =========="
date -Is; hostname; echo "LOG_LOCAL: $LOG"

exists() { sudo docker container inspect "$1" >/dev/null 2>&1; }
running() { [[ "$(sudo docker inspect -f '{{.State.Running}}' "$1")" == true ]]; }
pid_of() { sudo docker inspect -f '{{.State.Pid}}' "$1"; }
ns() {
  local p; p="$(pid_of "$1")"; shift
  [[ "$p" =~ ^[1-9][0-9]*$ ]] || { echo "ERROR: PID no válido"; return 3; }
  sudo nsenter -t "$p" -n "$@"
}
state_guard() {
  [[ -f "$STATE/.nl360-owner" ]] || {
    echo "ERROR: no existe marcador de propiedad B2. No modificar ni borrar recursos."
    return 3
  }
  [[ "$(cat "$STATE/.nl360-owner")" == netlab360-b2-dualwan ]] || {
    echo "ERROR: marcador B2 inesperado. No modificar ni borrar recursos."
    return 3
  }
}
host_guard() {
  ip -4 -o addr show dev ens33 | grep -q '192\.168\.47\.40/24' ||
    { echo "ERROR: dirección ens33 inesperada"; return 3; }
  ip -4 route show default | grep -q '^default via 192\.168\.47\.2 dev ens33' ||
    { echo "ERROR: gateway de gestión inesperado"; return 3; }
  for s in docker ssh open-vm-tools; do
    [[ "$(systemctl is-active "$s")" == active ]] ||
      { echo "ERROR: servicio detenido $s"; return 3; }
  done
}
precheck() {
  host_guard
  command -v nsenter >/dev/null
  command -v ip >/dev/null
  python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml
  sudo docker image inspect "$IMAGE" --format 'FRR={{.Id}} Arch={{.Architecture}}'
  if exists "$HQ" || exists "$S1" || [[ -e "$STATE" ]]; then
    echo "ERROR: recursos previos B2; revisar antes de iniciar, no borrar"; return 3
  fi
  for l in nl2hp nl2sp nl2hb nl2sb; do
    if ip link show "$l" >/dev/null 2>&1; then echo "ERROR: veth $l ya existe"; return 3; fi
  done
  echo "RESULTADO_B2_DUALWAN_PRECHECK=0"
}
prepare_config() {
  local name="$1" router="$2" d="$STATE/$1"
  mkdir -p "$d"
  sudo docker run --rm --network none --cap-drop ALL \
    --entrypoint /bin/cat "$IMAGE" /etc/frr/daemons > "$d/daemons"
  if grep -q '^zebra=' "$d/daemons"; then
    sed -i 's/^zebra=.*/zebra=yes/' "$d/daemons"
  else
    printf 'zebra=yes\n' >> "$d/daemons"
  fi
  if grep -q '^ospfd=' "$d/daemons"; then
    sed -i 's/^ospfd=.*/ospfd=yes/' "$d/daemons"
  else
    printf 'ospfd=yes\n' >> "$d/daemons"
  fi
  cp "$ROOT/topologias/b2-frr/configs/$router.frr.conf" "$d/frr.conf"
  printf 'service integrated-vtysh-config\nhostname %s\n' "$router" > "$d/vtysh.conf"
  sudo chown 100:101 "$d" "$d/daemons"
  sudo chown 100:102 "$d/frr.conf" "$d/vtysh.conf"
  sudo chmod 755 "$d"
  sudo chmod 640 "$d/daemons"
  sudo chmod 660 "$d/frr.conf" "$d/vtysh.conf"
}
start_router() {
  sudo docker run -d --name "$1" --network none \
    --cap-drop ALL --cap-add NET_ADMIN --cap-add NET_RAW \
    --cap-add NET_BIND_SERVICE --cap-add SETPCAP --cap-add SYS_ADMIN \
    --cap-add SETUID --cap-add SETGID --cap-add CHOWN \
    --cap-add DAC_READ_SEARCH --cap-add DAC_OVERRIDE \
    --pids-limit 128 --memory 512m \
    --tmpfs "$PID_TMPFS" --tmpfs "$CRASH_TMPFS" \
    --mount "type=bind,source=$STATE/$1,target=/etc/frr" "$IMAGE"
}
pair() {
  local a="$1" b="$2" dest="$3"
  sudo ip link add "$a" type veth peer name "$b"
  sudo ip link set "$a" netns "$(pid_of "$HQ")"
  sudo ip link set "$b" netns "$(pid_of "$S1")"
  ns "$HQ" ip link set "$a" name "$dest"
  ns "$S1" ip link set "$b" name "$dest"
}
add_addr() { ns "$1" ip address add "$3" dev "$2"; ns "$1" ip link set "$2" up; }
interfaces() {
  ns "$HQ" ip link set lo up
  ns "$S1" ip link set lo up
  ns "$HQ" ip addr add 10.79.0.1/32 dev lo
  ns "$S1" ip addr add 10.79.0.2/32 dev lo
  pair nl2hp nl2sp wan-p
  pair nl2hb nl2sb wan-b
  add_addr "$HQ" wan-p 10.78.0.1/30
  add_addr "$S1" wan-p 10.78.0.2/30
  add_addr "$HQ" wan-b 10.78.0.5/30
  add_addr "$S1" wan-b 10.78.0.6/30
  ns "$HQ" ip link add lan0 type dummy
  ns "$S1" ip link add lan0 type dummy
  add_addr "$HQ" lan0 10.70.10.1/24
  add_addr "$S1" lan0 10.71.10.1/24
}
apply_config() {
  local out
  out="$(sudo docker exec "$1" vtysh -b 2>&1)" || { printf '%s\n' "$out"; return 5; }
  printf '%s\n' "$out"
  if printf '%s\n' "$out" | grep -Eqi 'processing failure|% Unknown|invalid input|failed to connect'; then
    echo "ERROR: configuración FRR en $1"; return 5
  fi
}
neighbors() { sudo docker exec "$1" vtysh -c 'show ip ospf neighbor'; }
routes() { sudo docker exec "$1" vtysh -c 'show ip route ospf'; }
wait_full() {
  local n count
  echo "========== ESPERAR VECINOS OSPF FULL =========="
  for n in $(seq 1 35); do
    running "$HQ" && running "$S1" || return 4
    count="$(neighbors "$HQ" | grep -ic Full || true)"
    echo "Intento $n: Full=$count"
    if [[ "$count" -ge 2 ]]; then echo "OSPF_DUAL_FULL: SI"; return 0; fi
    sleep 2
  done
  echo "ERROR: no hubo dos vecinos Full"; return 4
}
# La vecindad Full precede a veces la instalacion de rutas OSPF en zebra/FIB.
# Esperar las DOS rutas remotas antes de declarar UP exitoso.
# La comprobacion solo lee namespaces de los routers, no toca rutas del host.
wait_remote_routes() {
  local try hq_route s1_route
  echo "========== ESPERAR FIB OSPF WAN PRINCIPAL EN AMBOS ROUTERS =========="
  for try in $(seq 1 60); do
    running "$HQ" && running "$S1" || return 4
    hq_route="$(ns "$HQ" ip -4 route get 10.71.10.1 2>/dev/null || true)"
    s1_route="$(ns "$S1" ip -4 route get 10.70.10.1 2>/dev/null || true)"
    if [[ "$hq_route" == *"dev wan-p"* && "$s1_route" == *"dev wan-p"* ]]; then
      echo "FIB_HQ_S1=$hq_route"
      echo "FIB_S1_HQ=$s1_route"
      echo "RUTAS_OSPF_BIDIRECCIONALES_WAN_P=OK (sondeo $try)"
      return 0
    fi
    if (( try == 1 || try % 5 == 0 )); then
      echo "RUTAS_OSPF_PENDIENTES: sondeo $try/60; esperar instalacion en FIB"
    fi
    sleep 1
  done
  echo "ERROR: OSPF Full pero sin rutas remotas simetricas por WAN-P"
  echo "FIB_HQ=$hq_route"
  echo "FIB_S1=$s1_route"
  return 4
}
diagnostic() {
  for c in "$HQ" "$S1"; do
    if exists "$c"; then
      echo "========== $c DIAGNOSTICO =========="
      sudo docker inspect -f 'Estado={{.State.Status}} Exit={{.State.ExitCode}} Error={{.State.Error}}' "$c" || true
      sudo docker logs --timestamps --tail 65 "$c" 2>&1 || true
    fi
  done
}
cleanup() {
  local code=0
  echo "========== LIMPIEZA B2 EXCLUSIVA =========="
  for c in "$HQ" "$S1"; do
    if exists "$c"; then
      sudo docker logs --timestamps "$c" > "$EVID/15-b2-$(date +%Y%m%d-%H%M%S)-$c.log" 2>&1 || true
      sudo docker rm -f "$c" >/dev/null || code=8
    fi
  done
  for l in nl2hp nl2sp nl2hb nl2sb; do
    if ip link show "$l" >/dev/null 2>&1; then sudo ip link delete "$l" || code=8; fi
  done
  if [[ -f "$STATE/.nl360-owner" ]]; then
    state_guard || return 9
    cmp -s "$STATE/ens33-before" <(ip -4 -o addr show dev ens33) ||
      { echo "ALERTA: ens33 cambió"; code=9; }
    cmp -s "$STATE/routes-before" <(ip -4 route show table main) ||
      { echo "ALERTA: rutas del host cambiaron"; code=9; }
    sudo rm -rf -- "$STATE"
  elif [[ -e "$STATE" ]]; then
    echo "ALERTA: estado sin marcador; no borrar"; code=9
  fi
  sudo docker ps -a --filter 'name=nl360-b2-' --format 'table {{.Names}}\t{{.Status}}'
  ip -4 -br addr show ens33
  ip -4 route show default
  echo "RESULTADO_B2_LIMPIEZA=$code"
  return "$code"
}
on_exit() {
  local rc=$?
  trap - EXIT
  if [[ "$UP_PENDING" == 1 && "$UP_COMPLETE" != 1 ]]; then
    echo "ERROR: up interrumpido ($rc); limpieza automática"
    diagnostic
    cleanup || true
  fi
  exit "$rc"
}
trap on_exit EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

case "$ACTION" in
  precheck) precheck ;;
  up)
    precheck
    UP_PENDING=1
    mkdir -p "$STATE"
    printf 'netlab360-b2-dualwan\n' > "$STATE/.nl360-owner"
    ip -4 -o addr show dev ens33 > "$STATE/ens33-before"
    ip -4 route show table main > "$STATE/routes-before"
    prepare_config "$HQ" R-HQ
    prepare_config "$S1" R-S1
    start_router "$HQ"
    start_router "$S1"
    sleep 2
    running "$HQ" && running "$S1"
    interfaces
    apply_config "$HQ"
    apply_config "$S1"
    wait_full
    wait_remote_routes
    neighbors "$HQ"; neighbors "$S1"
    routes "$HQ"; routes "$S1"
    ns "$HQ" ip -4 route get 10.71.10.1
    ns "$S1" ip -4 route get 10.70.10.1
    host_guard
    UP_COMPLETE=1
    echo "RESULTADO_B2_DUALWAN_UP=0"
    ;;
  status)
    state_guard
    for c in "$HQ" "$S1"; do
      running "$c" || { echo "ERROR: router $c no está corriendo"; exit 3; }
      echo "========== $c =========="
      ns "$c" ip -4 -br address
      neighbors "$c"
      routes "$c"
    done
    ns "$HQ" ip -4 route get 10.71.10.1
    ns "$S1" ip -4 route get 10.70.10.1
    host_guard
    ;;
  fail)
    state_guard
    running "$HQ" && running "$S1"
    echo "========== RUTA PRINCIPAL ANTES DEL CORTE =========="
    BEFORE="$(ns "$HQ" ip -4 route get 10.71.10.1)"
    echo "$BEFORE"
    [[ "$BEFORE" == *"dev wan-p"* ]] || {
      echo "ERROR: la ruta inicial no usa wan-p. No provocar corte."
      exit 4
    }
    date -Is; ns "$HQ" ip link set wan-p down
    echo "WAN_PRIMARIA: DOWN"
    echo "========== ESPERAR CONMUTACION REAL A WAN-B =========="
    SWITCHED=0
    for TRY in $(seq 1 30); do
      ROUTE="$(ns "$HQ" ip -4 route get 10.71.10.1 2>&1 || true)"
      if [[ "$ROUTE" == *"dev wan-b"* ]]; then
        echo "RUTA_RESPALDO: $ROUTE"
        echo "CONMUTACION_WAN_B: OK (sondeo $TRY)"
        SWITCHED=1
        break
      fi
      sleep 1
    done
    neighbors "$HQ"; routes "$HQ"
    host_guard
    [[ "$SWITCHED" -eq 1 ]] || {
      echo "ERROR: ruta por WAN-B no comprobada; restaurar WAN-P antes del cierre."
      exit 4
    }
    ;;
  restore)
    state_guard
    running "$HQ" && running "$S1"
    echo "========== RESTAURAR SOLO ENLACE WAN-P =========="
    date -Is; ns "$HQ" ip link set wan-p up
    echo "WAN_PRIMARIA: UP"
    echo "========== ESPERAR RETORNO REAL A WAN-P =========="
    RETURNED=0
    for TRY in $(seq 1 50); do
      ROUTE="$(ns "$HQ" ip -4 route get 10.71.10.1 2>&1 || true)"
      if [[ "$ROUTE" == *"dev wan-p"* ]]; then
        echo "RUTA_PRINCIPAL: $ROUTE"
        echo "RESTAURACION_WAN_P: OK (sondeo $TRY)"
        RETURNED=1
        break
      fi
      sleep 1
    done
    neighbors "$HQ"; routes "$HQ"
    host_guard
    [[ "$RETURNED" -eq 1 ]] || {
      echo "ERROR: retorno por WAN-P no comprobado; proceder a down y analizar."
      exit 4
    }
    ;;
  down) state_guard; cleanup; host_guard ;;
esac
echo "RESULTADO_COMANDO_B2_DUALWAN=0"
