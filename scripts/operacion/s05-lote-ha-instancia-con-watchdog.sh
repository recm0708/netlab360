#!/usr/bin/env bash
# S05: UNA prueba HA de backend con rescate systemd independiente de SSH.
# No interviene WAN, LACP, Faucet, ens33 ni namespaces.
set -Eeuo pipefail
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "USO: bash $0 --precheck | --run --confirm-fault" >&2; exit 2
fi
MODE="$1"
if [[ "$MODE" != "--precheck" && !( "$MODE" == "--run" && "${2:-}" == "--confirm-fault" ) ]]; then
  echo "MODO INVALIDO; se requiere --run --confirm-fault para modificar backend HQ" >&2
  exit 2
fi

cd "$HOME/proyectos/netlab360"
BACKEND="netlab360-s05-ha-backend-hq.service"
SUFFIX="netlab360-s05-ha-hq-rescue-$(date -u +%Y%m%dT%H%M%SZ)-$$"
TIMER="${SUFFIX}.timer"

preflight() {
  echo "========== S05 HA INSTANCIA PREFLIGHT =========="
  test "$(hostname)" = "netlab360-lab"
  test "$(git branch --show-current)" = main
  test -z "$(git status --porcelain)"
  ip -4 -br address show ens33 | grep -Fq "192.168.47.40/24"
  ip -4 route show default | grep -Fq "default via 192.168.47.2 dev ens33"
  for u in netlab360-s04-exporter.service netlab360-s05-noc.service \
    netlab360-s05-ha-backend-hq.service netlab360-s05-ha-backend-s1.service \
    netlab360-s05-ha-frontal-hq.service netlab360-s05-ha-monitor-s2.service; do
    test "$(systemctl is-active "$u")" = active
    echo "SERVICE_${u}=active"
  done
  test "$(systemctl is-active "$BACKEND")" = active
  test -f "$HOME/netlab360-bootstrap/s05/evidencias/ha-instancia/17_Auditoria_Procedencia_TAR_P1_y_P1B.txt"
  grep -Fq "LOTE147A_DIAGNOSTICO=COMPLETADO" \
    "$HOME/netlab360-bootstrap/s05/evidencias/ha-instancia/17_Auditoria_Procedencia_TAR_P1_y_P1B.txt"
  python3 scripts/validacion/s05_ha_noc_ciclo.py --precheck
  sudo -n /usr/bin/true
  command -v systemd-run >/dev/null
  echo "S05_HA_INSTANCIA_PREFLIGHT=OK_SOLO_LECTURA"
}
preflight
if [[ "$MODE" == "--precheck" ]]; then
  echo "S05_HA_INSTANCIA_MODO=SOLO_LECTURA"
  exit 0
fi

echo "========== S05 HA ARMAR RESCATE AUTONOMO =========="
sudo -n systemd-run --unit="$SUFFIX" --on-active=120s \
  /usr/bin/systemctl start "$BACKEND"
test "$(systemctl is-active "$TIMER")" = active
echo "S05_HA_RESCATE_TIMER_ARMADO=$TIMER"
echo "S05_HA_RESCATE_ACCION=systemctl start $BACKEND"
echo "S05_HA_RESCATE_PLAZO=120s"

echo "========== S05 HA CICLO CONTROLADO =========="
set +e
python3 scripts/validacion/s05_ha_noc_ciclo.py --run --hold-seconds 8
CYCLE_RC=$?
set -e
echo "S05_HA_CICLO_RC=$CYCLE_RC"

if [[ $CYCLE_RC -ne 0 ]]; then
  echo "S05_HA_CICLO=NO_APROBADO_RESCATE_CONSERVADO"
  echo "S05_HA_RESCATE_PENDIENTE=$TIMER"
  sudo -n systemctl start "$BACKEND" || true
  exit 3
fi

echo "========== S05 HA RECUPERACION Y REGRESION =========="
test "$(systemctl is-active "$BACKEND")" = active
python3 scripts/validacion/s05_ha_noc_ciclo.py --precheck
for u in netlab360-s04-exporter netlab360-s05-noc \
  netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 \
  netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
  test "$(systemctl is-active "$u")" = active
done
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"

echo "========== S05 HA CANCELAR TIMER TRAS ACEPTACION =========="
sudo -n systemctl stop "$TIMER"
echo "S05_HA_RESCATE_TIMER_CANCELADO=$TIMER"
echo "S05_HA_CICLO_INSTANCIA=HQ_S1_HQ_OK"
echo "S05_HA_ESTADO_FINAL=BACKEND_HQ_PRINCIPAL"
echo "S05_HA_GESTION=INTACTA"
echo "========== S05_LOTE_HA_INSTANCIA=OK =========="
