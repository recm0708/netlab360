#!/usr/bin/env bash
# NETLAB360 S02 - comprobacion previa SIN MODIFICAR LA RED.
# Para validar nueva conexion SSH es imprescindible una prueba externa (Windows).
set -Eeuo pipefail
ROOT="$HOME/proyectos/netlab360"
RENDER="$HOME/netlab360-bootstrap/s02/rendered"
IMAGE="quay.io/frrouting/frr:10.7.1"
cd "$ROOT"

fail() { printf 'S02_PRECHECK_ERROR=%s\n' "$*" >&2; exit 3; }
[[ "$(hostname)" == "netlab360-lab" ]] || fail "hostname distinto de netlab360-lab"
[[ "$(id -u)" != 0 ]] || fail "Ejecutar como usuario normal"
for c in ip docker python3 systemctl sha256sum; do
  command -v "$c" >/dev/null || fail "No disponible: $c"
done

echo "========== S02 PRECHECK SIN DESPLIEGUE =========="
date -Is
git status --short --branch
echo "========== RED DE GESTION =========="
ip -4 -br addr show dev ens33
ip -4 route show default
ip -4 -o addr show dev ens33 | grep -Fq "192.168.47.40/24" ||
  fail "La IP de ens33 no coincide"
ip -4 route show default | grep -Fq "default via 192.168.47.2 dev ens33" ||
  fail "La ruta de gestion no coincide"

echo "========== SERVICIOS =========="
[[ "$(systemctl is-active docker)" == "active" ]] || fail "Docker inactivo"
[[ "$(systemctl is-active open-vm-tools)" == "active" ]] ||
  fail "open-vm-tools inactivo"
if [[ "$(systemctl is-active ssh.socket)" == "active" ]]; then
  echo "S02_OPENSSH_ACTIVACION=SOCKET"
elif [[ "$(systemctl is-active ssh.service)" == "active" ]]; then
  echo "S02_OPENSSH_ACTIVACION=SERVICIO"
else
  fail "OpenSSH sin servicio ni socket activo"
fi
sudo /usr/sbin/sshd -t || fail "sshd -t fallo; /run/sshd/configuracion a revisar"
echo "S02_SSHD_SINTAXIS=OK"
echo "S02_NUEVA_SESION_SSH=VALIDAR_EXTERNAMENTE"

echo "========== IPAM S02 =========="
sudo -v
python3 scripts/validacion/validar_ipam_s02.py

echo "========== FRR RENDER =========="
sudo docker image inspect "$IMAGE" --format 'FRR_LOCAL={{.Id}} {{.Architecture}}' ||
  fail "Imagen FRR no presente"
for router in R-HQ R-S1 R-S2; do
  [[ -f "$RENDER/$router.frr.conf" && ! -L "$RENDER/$router.frr.conf" ]] ||
    fail "Falta configuracion candidata: $router"
done
sha256sum "$RENDER"/R-HQ.frr.conf "$RENDER"/R-S1.frr.conf "$RENDER"/R-S2.frr.conf

echo "========== COLISIONES CON RECURSOS S02 =========="
for c in nl360-s02-r-hq nl360-s02-r-s1 nl360-s02-r-s2; do
  if sudo docker container inspect "$c" >/dev/null 2>&1; then
    fail "Contenedor S02 preexistente: $c"
  fi
done
[[ ! -e "$HOME/netlab360-bootstrap/estado-s02-wan" ]] ||
  fail "Estado WAN S02 preexistente, inspeccionar sin borrar"
echo "S02_DOCKER_CONTENEDORES_TOTAL=$(sudo docker ps -aq | wc -l)"
echo "S02_HOST_NETNS_TOTAL=$(sudo ip netns list | wc -l)"

echo "S02_DESPLIEGUE_EJECUTADO=NO"
echo "S02_PRECHECK_RESULTADO=0"
