#!/usr/bin/env bash
# NETLAB360 B3 — obtener binarios Prometheus/promtool desde imagen oficial pinned.
# No instala paquetes apt; NO arranca servicios, NO altera redes del host.
set -Eeuo pipefail
REPO="$HOME/proyectos/netlab360"
BASE="$HOME/netlab360-bootstrap/prometheus"
BIN="$BASE/bin"
IMAGE="quay.io/prometheus/prometheus:v3.7.0"
TEMP="nl360-prometheus-extract-$$"
CREATED=0
finish() {
  if (( CREATED == 1 )); then
    sudo docker rm -f "$TEMP" >/dev/null 2>&1 || true
  fi
}
trap finish EXIT
[[ "$(hostname)" == netlab360-lab ]] || { echo "ERROR: hostname inesperado"; exit 3; }
[[ "$(id -u)" != 0 ]] || { echo "ERROR: usar cuenta normal"; exit 3; }
cd "$REPO"
sudo -v
ip -4 -br address show ens33 | grep -Fq '192.168.47.40/24' ||
  { echo "ERROR: IP administrativa cambiada"; exit 3; }
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' ||
  { echo "ERROR: gateway cambiado"; exit 3; }
echo "========== PREPARAR PROMETHEUS LOCAL NETLAB360 =========="
date -Is
hostname
if ss -H -ltn '( sport = :9090 )' | grep -q .; then
  echo "ERROR: puerto localhost 9090 ya ocupado; revisar"; exit 3
fi
mkdir -p "$BIN" "$BASE/data"
if sudo docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "IMAGEN_PROMETHEUS_LOCAL: SI"
else
  echo "IMAGEN_PROMETHEUS_LOCAL: NO; descargando imagen fijada $IMAGE"
  sudo docker pull "$IMAGE"
fi
sudo docker image inspect "$IMAGE" --format \
  'PROMETHEUS_IMAGE_DIGEST={{.Id}} OS={{.Os}} ARCH={{.Architecture}}'
if sudo docker container inspect "$TEMP" >/dev/null 2>&1; then
  echo "ERROR: nombre temporal ya existe"; exit 3
fi
# docker create no inicia el contenedor ni crea redes del laboratorio.
sudo docker create --network none --name "$TEMP" "$IMAGE" >/dev/null
CREATED=1
sudo docker cp "$TEMP:/bin/prometheus" "$BIN/prometheus"
sudo docker cp "$TEMP:/bin/promtool" "$BIN/promtool"
sudo chown "$(id -u):$(id -g)" "$BIN/prometheus" "$BIN/promtool"
chmod 755 "$BIN/prometheus" "$BIN/promtool"
"$BIN/prometheus" --version | head -n 2
"$BIN/promtool" --version | head -n 2
echo "========== INTEGRIDAD SHA256 =========="
sha256sum "$BIN/prometheus" "$BIN/promtool"
echo "========== VALIDAR CONFIGURACION =========="
"$BIN/promtool" check config servicios/observabilidad/prometheus/prometheus.yml
"$BIN/promtool" check rules servicios/observabilidad/prometheus/rules/wan-alerts.yml
echo "PROMETHEUS_BINARIOS: OK"
echo "PROMETHEUS_CONFIGURACION: OK"
echo "RESULTADO_PREPARACION_PROMETHEUS=0"
