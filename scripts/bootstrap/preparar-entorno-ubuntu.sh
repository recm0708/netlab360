#!/usr/bin/env bash
# NETLAB360 | Herramientas del proyecto: preparar entorno ubuntu
# Alcance: ejecutar únicamente los recursos del componente correspondiente.
# Seguridad: mantener separada la red de administración del laboratorio.

# NETLAB360: preparación de herramientas del anfitrión Ubuntu Desktop.
# NO despliega FRRouting/OVS ni topologías de red.
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive

if [ "$(id -u)" -eq 0 ]; then
  echo "Ejecutar como usuario normal con sudo disponible, no como root." >&2
  exit 1
fi
source /etc/os-release
if [ "$ID" != "ubuntu" ] || [ "$VERSION_ID" != "26.04" ]; then
  echo "SO no validado para este instalador: $PRETTY_NAME" >&2
  exit 1
fi
if [ "$(dpkg --print-architecture)" != "amd64" ]; then
  echo "Arquitectura distinta de amd64: requiere revisión." >&2
  exit 1
fi
if [ "$(hostname)" != "netlab360-lab" ]; then
  echo "Host inesperado, no se instaló nada." >&2
  exit 1
fi

REPORT_DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$REPORT_DIR"
REPORT_FILE="$REPORT_DIR/02-preparacion-herramientas-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$REPORT_FILE") 2>&1

echo "== NETLAB360 | Preparación de herramientas =="
echo "Hora: $(date -Is) | Host: $(hostname) | OS: $PRETTY_NAME"
echo "Reporte: $REPORT_FILE"
sudo -v

install_apt() {
  sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
}

echo "== 1. Mantenimiento SO y herramientas básicas =="
sudo apt-get update
sudo env DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
install_apt \
  ca-certificates curl wget gnupg apt-transport-https git gh \
  jq yq unzip zip rsync tree htop tmux \
  build-essential make shellcheck \
  python3 python3-venv python3-pip python3-dev pipx \
  ansible \
  iproute2 iputils-ping iputils-arping ethtool \
  dnsutils traceroute mtr-tiny tcpdump iperf3 net-tools \
  openssh-server open-vm-tools open-vm-tools-desktop

echo "== 2. Actualizar GitHub CLI desde la fuente oficial =="
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl --fail --silent --show-error --location \
  https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  -o /etc/apt/keyrings/githubcli-archive-keyring.gpg
sudo chmod a+r /etc/apt/keyrings/githubcli-archive-keyring.gpg
cat <<EOF | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null
deb [arch=amd64 signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main
EOF
sudo apt-get update
install_apt gh

echo "== 3. Docker Engine oficial (Ubuntu resolute) =="
for conflict in docker.io docker-compose docker-compose-v2 podman-docker containerd runc; do
  if dpkg -s "$conflict" 2>/dev/null | grep -q '^Status: install ok installed$'; then
    echo "Conflicto detectado: paquete $conflict instalado. Detener sin eliminarlo." >&2
    exit 2
  fi
done
sudo curl --fail --silent --show-error --location \
  https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
cat <<EOF | sudo tee /etc/apt/sources.list.d/docker.sources >/dev/null
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: resolute
Components: stable
Architectures: amd64
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt-get update
install_apt docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo docker version
sudo docker compose version
sudo docker buildx version
sudo docker run --rm hello-world

echo "== 4. OpenTofu oficial =="
sudo curl --fail --silent --show-error --location \
  https://get.opentofu.org/opentofu.gpg \
  -o /etc/apt/keyrings/opentofu.gpg
curl --fail --silent --show-error --location \
  https://packages.opentofu.org/opentofu/tofu/gpgkey |
  sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/opentofu-repo.gpg
sudo chmod a+r /etc/apt/keyrings/opentofu.gpg /etc/apt/keyrings/opentofu-repo.gpg
cat <<EOF | sudo tee /etc/apt/sources.list.d/opentofu.list >/dev/null
deb [signed-by=/etc/apt/keyrings/opentofu.gpg,/etc/apt/keyrings/opentofu-repo.gpg] https://packages.opentofu.org/opentofu/tofu/any/ any main
EOF
sudo apt-get update
install_apt tofu

echo "== 5. Node.js 24 LTS (NodeSource) =="
curl --fail --silent --show-error --location \
  https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key |
  sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/nodesource.gpg
sudo chmod a+r /etc/apt/keyrings/nodesource.gpg
cat <<EOF | sudo tee /etc/apt/sources.list.d/nodesource.sources >/dev/null
Types: deb
URIs: https://deb.nodesource.com/node_24.x
Suites: nodistro
Components: main
Architectures: amd64
Signed-By: /etc/apt/keyrings/nodesource.gpg
EOF
sudo apt-get update
install_apt nodejs
if [[ "$(node -v)" != v24.* ]]; then
  echo "Node.js no quedó en rama 24 LTS: $(node -v)" >&2
  exit 3
fi

echo "== 6. Limpieza y verificación final =="
sudo apt-get autoremove --purge -y
sudo apt-get clean
date -Is
hostnamectl
python3 --version
git --version
gh --version | head -n 1
ansible --version | head -n 2
tofu version | head -n 2
node --version
npm --version
sudo docker version --format '{{.Server.Version}}'
sudo docker compose version
systemctl is-active docker ssh open-vm-tools
ip -4 -br addr show ens33
ip -4 route show default
df -h /
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
if [ -f /var/run/reboot-required ]; then
  echo "REINICIO PENDIENTE: SI. Verificar después del reinicio."
else
  echo "REINICIO PENDIENTE: NO"
fi
echo "REPORTE: $REPORT_FILE"
echo "OK: herramientas base instaladas. NO desplegar todavía topologías."
