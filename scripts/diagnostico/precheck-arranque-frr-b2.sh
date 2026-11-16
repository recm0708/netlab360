#!/usr/bin/env bash
# NETLAB360 | Herramientas del proyecto: precheck arranque frr b2
# Alcance: ejecutar únicamente los recursos del componente correspondiente.
# Seguridad: mantener separada la red de administración del laboratorio.

# NETLAB360 B2-L3: inspección de arranque/configuración de FRRouting 10.7.1.
# Solo un contenedor efímero SIN red, sin demonios, cap-drop ALL, rootfs read-only.
set -Eeuo pipefail
IMAGE="quay.io/frrouting/frr:10.7.1"
if [[ "$(hostname)" != "netlab360-lab" ]]; then
  echo "ERROR: hostname distinto de netlab360-lab" >&2
  exit 2
fi
if ! ip -4 -o addr show dev ens33 | grep -q '192\.168\.47\.40/24'; then
  echo "ERROR: dirección ens33 inesperada" >&2
  exit 2
fi
cd "$HOME/proyectos/netlab360"
DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$DIR"
LOG="$DIR/08-b2-frr-entrypoint-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1

echo "========== NETLAB360 B2 | FRR ARRANQUE (LECTURA) =========="
date -Is
hostname
sudo -v
echo "========== METADATOS DE IMAGEN =========="
sudo docker image inspect "$IMAGE" \
  --format 'OS={{.Os}} Arch={{.Architecture}} User={{.Config.User}} Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
echo "========== PROCESOS ANTES =========="
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'

echo "========== SONDEO ESTÁTICO CONTENEDOR TEMPORAL =========="
sudo docker run --rm --network none --name nl360-frr-startup-inspect \
  --cap-drop ALL --security-opt no-new-privileges --read-only \
  --pids-limit 32 --memory 128m --entrypoint /bin/sh "$IMAGE" -c '
    echo "--- daemons: habilitación y valores ---"
    grep -nE "^(zebra|ospfd|bgpd|staticd|mgmtd|vtysh_enable|watchfrr_enable|zebra_options|ospfd_options)=" /etc/frr/daemons || true
    echo "--- usuarios/grupos registrados ---"
    grep "^frr:" /etc/passwd || true
    grep -E "^(frr|frrvty):" /etc/group || true
    echo "--- rutas que pudieran iniciar los procesos ---"
    for f in /usr/lib/frr/docker-start /usr/lib/frr/frrinit.sh /usr/lib/frr/docker-entrypoint.sh /etc/init.d/frr /usr/lib/frr/ospfd /usr/lib/frr/zebra; do
      if [ -e "$f" ]; then ls -l "$f"; fi
    done
    echo "--- directorios de montaje ---"
    ls -ld /etc/frr /var/run/frr /run/frr /var/log/frr 2>&1 || true
    echo "--- contenido previsto de /etc/frr ---"
    ls -la /etc/frr
    echo "--- cabecera de arranque cuando exista ---"
    if [ -f /usr/lib/frr/docker-start ]; then
      sed -n "1,85p" /usr/lib/frr/docker-start
    fi
  '

echo "========== POSTCHECK =========="
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
sudo docker network ls --format 'table {{.Name}}\t{{.Driver}}'
ip -4 -br addr show ens33
ip -4 route show default
git status --short --branch
echo "No se han iniciado los daemons de FRR ni alterado redes."
echo "LOG_LOCAL: $LOG"
