#!/usr/bin/env bash
# NETLAB360 B2-L3: solo lectura; verifica host, IPAM, Docker y la etiqueta FRR.
# No descarga imagen, no crea bridges, routers ni contenedores.
set -Eeuo pipefail

if [[ "$(hostname)" != "netlab360-lab" ]]; then
  echo "ERROR: Host inesperado" >&2
  exit 2
fi

cd "$HOME/proyectos/netlab360"
mkdir -p "$HOME/netlab360-bootstrap/evidencias"
LOG="$HOME/netlab360-bootstrap/evidencias/06-b2-frr-precheck-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1
IMAGE="quay.io/frrouting/frr:10.7.1"

echo "========== NETLAB360 B2 - PRECHECK FRR / OSPF (SOLO LECTURA) =========="
date -Is
hostname
echo "========== IDENTIDAD / RUTAS DE GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
ip -4 route show table main
if ! ip -4 -o address show dev ens33 | grep -q '192\.168\.47\.40/24'; then
  echo "ERROR: Dirección de ens33 inesperada." >&2
  exit 2
fi
if ! ip -4 route show default | grep -q 'default via 192\.168\.47\.2 dev ens33'; then
  echo "ERROR: Gateway de gestión inesperado." >&2
  exit 2
fi
echo "========== VALIDAR IPAM =========="
python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml
echo "========== ESTADO DE GIT =========="
git status --short --branch
echo "========== REDES Y PROCESOS DEL LABORATORIO =========="
sudo -v
sudo ip netns list
sudo docker network ls --format 'table {{.Name}}\t{{.Driver}}'
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
echo "========== DOCKER / SISTEMA =========="
systemctl is-active docker ssh open-vm-tools
sudo docker info --format 'Docker={{.ServerVersion}}; Storage={{.Driver}}; Cgroup={{.CgroupVersion}}'
echo "========== CONECTIVIDAD DEL REGISTRO =========="
getent ahostsv4 quay.io | head -n 3 || true
echo "========== CONSULTA MANIFIESTO FRR OFICIAL =========="
echo "Imagen candidata: $IMAGE"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
if sudo docker manifest inspect "$IMAGE" > "$TMP"; then
  echo "MANIFIESTO_FRR: DISPONIBLE"
  if jq -e 'has("manifests")' "$TMP" >/dev/null; then
    jq -r '.manifests[]? | "\(.platform.os)/\(.platform.architecture) \(.digest)"' "$TMP"
  else
    echo "Manifiesto individual encontrado; la arquitectura debe verificarse tras la descarga."
    jq -r '"MediaType: \(.mediaType // "desconocido")"' "$TMP"
  fi
else
  echo "MANIFIESTO_FRR: NO VERIFICADO. Revisar etiqueta/red; NO hacer pull ni desplegar routers."
fi
echo "========== CIERRE =========="
echo "No se descargaron imágenes ni se alteraron redes, rutas, módulos o contenedores."
echo "EVIDENCIA_LOCAL: $LOG"
