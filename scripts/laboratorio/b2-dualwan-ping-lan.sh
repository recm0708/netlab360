#!/usr/bin/env bash
# NETLAB360 B2 — prueba de paquetes ICMP reales entre LAN HQ y S1.
# No crea redes ni modifica enlaces. Requiere dualwan up.
set -Eeuo pipefail
if [[ "$#" -ne 1 ]]; then echo "Uso: bash $0 normal|respaldo|restaurada"; exit 2; fi
PHASE="$1"
case "$PHASE" in
  normal|respaldo|restaurada) ;;
  *) echo "Uso: bash $0 normal|respaldo|restaurada"; exit 2 ;;
esac
[[ "$(hostname)" == "netlab360-lab" ]] || { echo "ERROR: hostname no esperado"; exit 2; }
[[ "$(id -u)" != 0 ]] || { echo "ERROR: ejecutar como usuario normal"; exit 2; }
cd "$HOME/proyectos/netlab360"
STATE="$HOME/netlab360-bootstrap/estado-b2-dualwan"
LOGDIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$LOGDIR"
if [[ ! -f "$STATE/.nl360-owner" || "$(cat "$STATE/.nl360-owner")" != "netlab360-b2-dualwan" ]]; then
  echo "ERROR: orquestador dual-WAN no activo o estado no confiable"
  exit 3
fi
command -v ping >/dev/null || { echo "ERROR: ping no encontrado"; exit 3; }
sudo -v
HQ="nl360-b2-r-hq"; S1="nl360-b2-r-s1"
for c in "$HQ" "$S1"; do
  [[ "$(sudo docker inspect -f '{{.State.Running}}' "$c")" == true ]] || {
    echo "ERROR: router $c no activo"; exit 3
  }
done
ns() {
  local pid
  pid="$(sudo docker inspect -f '{{.State.Pid}}' "$1")"
  [[ "$pid" =~ ^[1-9][0-9]*$ ]] || return 3
  shift
  sudo nsenter -t "$pid" -n "$@"
}
LOG="$LOGDIR/16-b2-lan-ping-$PHASE-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1
echo "========== NETLAB360 | PING LAN $PHASE =========="
date -Is; hostname; echo "LOG_LOCAL: $LOG"
echo "========== CONTROL VMNET8 =========="
ip -4 -br address show ens33
ip -4 route show default
ip -4 -br address show ens33 | grep -q '192.168.47.40/24' || {
  echo "ERROR: ens33 inesperada"; exit 3
}
EXPECTED="wan-p"
if [[ "$PHASE" == respaldo ]]; then EXPECTED="wan-b"; fi
echo "========== RUTAS HACIA LAS LAN REMOTAS =========="
ROUTES_OK=0
for TRY in $(seq 1 15); do
  HQR="$(ns "$HQ" ip -4 route get 10.71.10.1 2>&1 || true)"
  S1R="$(ns "$S1" ip -4 route get 10.70.10.1 2>&1 || true)"
  if [[ "$HQR" == *"dev $EXPECTED"* && "$S1R" == *"dev $EXPECTED"* ]]; then
    ROUTES_OK=1
    break
  fi
  sleep 1
done
echo "HQ -> S1: $HQR"
echo "S1 -> HQ: $S1R"
if [[ "$ROUTES_OK" -ne 1 ]]; then
  echo "ERROR: rutas no convergieron en ambos sentidos hacia $EXPECTED; no ejecutar ICMP"
  exit 4
fi
echo "RUTAS_ESPERADAS: SI ($EXPECTED; intento $TRY)"
echo "========== ICMP HQ LAN => S1 LAN =========="
ns "$HQ" ping -n -I 10.70.10.1 -c 5 -i 0.3 -W 1 10.71.10.1
echo "PING_HQ_S1: OK"
echo "========== ICMP S1 LAN => HQ LAN =========="
ns "$S1" ping -n -I 10.71.10.1 -c 5 -i 0.3 -W 1 10.70.10.1
echo "PING_S1_HQ: OK"
echo "========== VERIFICACIÓN FINAL =========="
ip -4 -br address show ens33
ip -4 route show default
echo "RESULTADO_PING_LAN_$PHASE=0"
