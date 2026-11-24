#!/usr/bin/env bash
# NETLAB360: B1 - Verificación L2/L3 de compatibilidad, únicamente lectura.
# No ejecuta modprobe, ip link add, docker run, ni modifica ens33, rutas o firewall.
set -Eeuo pipefail

if [[ "$(hostname)" != "netlab360-lab" ]]; then
  echo "ERROR: destino inesperado; se esperaba netlab360-lab" >&2
  exit 2
fi

DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$DIR"
FILE="$DIR/04-b1-compatibilidad-l2-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$FILE") 2>&1

echo "========== NETLAB360 | B1 | PRECHECK L2/L3 (SOLO LECTURA) =========="
date -Is
hostname
echo "========== KERNEL / SO =========="
uname -a
. /etc/os-release
echo "$PRETTY_NAME"
echo "========== RED ADMIN Y DEFAULT ROUTE =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== LINKS DEL KERNEL =========="
ip -d -br link show
echo "========== NAMESPACES YA EXISTENTES =========="
ip netns list
echo "========== MODULOS DISPONIBLES EN ESTE KERNEL =========="
if command -v modinfo >/dev/null 2>&1; then
  for module in 8021q bonding openvswitch veth bridge; do
    if modinfo "$module" >/dev/null 2>&1; then
      echo "DISPONIBLE: $module"
    else
      echo "NO VERIFICADO: $module (módulo ausente o integrado, revisar)"
    fi
  done
else
  echo "modinfo NO DISPONIBLE. Instalar kmod únicamente tras acordarlo."
fi
echo "========== MODULOS ACTUALMENTE CARGADOS =========="
if command -v lsmod >/dev/null 2>&1; then
  lsmod | grep -E '^(8021q|bonding|openvswitch|veth|bridge)[[:space:]]' || true
else
  echo "lsmod no disponible"
fi
echo "========== FUNCIONES IP ROUTING (SOLO CONSULTA) =========="
sysctl net.ipv4.ip_forward
echo "========== HERRAMIENTAS EMULACIÓN DISPONIBLES =========="
for tool in ip tc bridge ovs-vsctl vtysh containerlab docker; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%-13s %s\n' "$tool" "$(command -v "$tool")"
  else
    printf '%-13s %s\n' "$tool" "NO INSTALADO (no es error en B1)"
  fi
done
echo "========== DOCKER / REDES POR DEFECTO =========="
sudo -v
sudo docker info --format 'Docker Server: {{.ServerVersion}} | Storage: {{.Driver}} | Cgroup: {{.CgroupVersion}}'
sudo docker network ls
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
echo "========== RECURSOS =========="
nproc
free -h
df -h /
echo "========== ESTADO DE GIT =========="
cd "$HOME/proyectos/netlab360"
git status --short --branch
echo "========== FINAL =========="
echo "No se han creado/cambiado interfaces, rutas, contenedores ni módulos."
echo "EVIDENCIA_LOCAL: $FILE"
