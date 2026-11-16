#!/usr/bin/env bash
# NETLAB360 | Herramientas del proyecto: inspeccionar imagen frr b2
# Alcance: ejecutar únicamente los recursos del componente correspondiente.
# Seguridad: mantener separada la red de administración del laboratorio.

# NETLAB360 B2-L3: inspeccion segura de imagen FRR YA descargada.
# Crea UN contenedor efimero sin red, sin privilegios, --rm, con rootfs de solo lectura.
# NO inicia ospfd ni zebra, NO crea veth y NO modifica rutas / ens33 / Docker networks.
set -Eeuo pipefail

IMAGE="quay.io/frrouting/frr:10.7.1"
if [[ "$(hostname)" != "netlab360-lab" ]]; then
  echo "ERROR: host inesperado" >&2
  exit 2
fi
if ! ip -4 -o address show ens33 | grep -q '192\.168\.47\.40/24'; then
  echo "ERROR: IP de gestión inesperada" >&2
  exit 2
fi

DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$DIR"
LOG="$DIR/07-b2-inspeccion-imagen-frr-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1

echo "========== B2 FRR | INSPECCION LOCAL, SIN RUTEO =========="
date -Is
echo "========== IMAGEN E IDENTIDAD =========="
sudo -v
sudo docker image inspect "$IMAGE" \
  --format 'Id={{.Id}} Arquitectura={{.Architecture}} SO={{.Os}} Digests={{json .RepoDigests}}'
echo "========== ESTADO PREVIO =========="
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
sudo docker network ls --format 'table {{.Name}}\t{{.Driver}}'
ip -4 -br addr show ens33
ip -4 route show default

echo "========== SONDEO DE ARCHIVOS FRR EN CONTENEDOR EFIMERO =========="
sudo docker run --rm \
  --name nl360-frr-inspect \
  --network none \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --read-only \
  --pids-limit 32 \
  --memory 128m \
  --entrypoint /bin/sh \
  "$IMAGE" -c '
    echo "--- identidad ---"
    id
    id frr || true
    id frrvty || true
    echo "--- archivos /etc/frr ---"
    ls -ld /etc/frr
    ls -l /etc/frr/daemons /etc/frr/frr.conf /etc/frr/vtysh.conf 2>&1 || true
    echo "--- demonios configurados por defecto ---"
    grep -E "^(zebra|ospfd|bgpd|vtysh_enable|frr_profile|zebra_options|ospfd_options)=" /etc/frr/daemons 2>/dev/null || true
    echo "--- herramientas ---"
    for cmd in vtysh ip ping ps; do
      command -v "$cmd" || echo "$cmd: NO EN PATH"
    done
    echo "--- ejecutables FRR ---"
    ls -l /usr/lib/frr/zebra /usr/lib/frr/ospfd 2>&1 || true
  '

echo "========== ESTADO POSTERIOR =========="
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
sudo docker network ls --format 'table {{.Name}}\t{{.Driver}}'
ip -4 -br addr show ens33
ip -4 route show default

echo "========== FIN =========="
echo "No se desplegaron routers ni redes del proyecto."
echo "LOG_LOCAL: $LOG"
