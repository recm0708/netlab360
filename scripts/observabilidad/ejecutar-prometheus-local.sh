#!/usr/bin/env bash
# NETLAB360 — Prometheus como usuario normal y exclusivamente localhost.
set -Eeuo pipefail
REPO="$HOME/proyectos/netlab360"
BASE="$HOME/netlab360-bootstrap/prometheus"
BIN="$BASE/bin"
[[ "$(hostname)" == netlab360-lab ]] || { echo "ERROR: hostname inesperado"; exit 3; }
[[ "$(id -u)" != 0 ]] || { echo "ERROR: usuario root no permitido"; exit 3; }
cd "$REPO"
ip -4 -br address show ens33 | grep -Fq '192.168.47.40/24' ||
  { echo "ERROR: ens33 IP cambiada"; exit 3; }
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' ||
  { echo "ERROR: default gateway cambiado"; exit 3; }
[[ -x "$BIN/prometheus" && -x "$BIN/promtool" ]] ||
  { echo "ERROR: ejecutar antes preparar-prometheus-local.sh"; exit 3; }
if ss -H -ltn '( sport = :9090 )' | grep -q .; then
  echo "ERROR: puerto 9090 ocupado; no duplicar servidor"; exit 3
fi
"$BIN/promtool" check config servicios/observabilidad/prometheus/prometheus.yml
mkdir -p "$BASE/data"
echo "PROMETHEUS_LOCAL_URL=http://127.0.0.1:9090/"
echo "PROMETHEUS_SCRAPE_TARGET=127.0.0.1:9108"
echo "PROMETHEUS_MODO=TSDB_LOCAL_REAL | CTRL_C_DETIENE"
exec "$BIN/prometheus" \
  --config.file="$REPO/servicios/observabilidad/prometheus/prometheus.yml" \
  --storage.tsdb.path="$BASE/data" \
  --storage.tsdb.retention.time=1d \
  --web.listen-address=127.0.0.1:9090 \
  --log.level=info
