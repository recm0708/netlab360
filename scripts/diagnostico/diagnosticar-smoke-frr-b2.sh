#!/usr/bin/env bash
# NETLAB360: diagnostico ESTATICO tras fallar el primer smoke FRR.
# No inicia zebra/ospfd ni modifica configuraciones, contenedores, rutas o interfaces.
set -Eeuo pipefail
IMAGE="quay.io/frrouting/frr:10.7.1"
[[ "$(hostname)" == "netlab360-lab" ]] || { echo "Host inesperado" >&2; exit 2; }
cd "$HOME/proyectos/netlab360"
sudo -v
if sudo docker ps -a --format '{{.Names}}' | grep -Eq '^nl360-frr-smoke$'; then
  echo "Hay un contenedor nl360-frr-smoke existente. No interferir." >&2; exit 3
fi

DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$DIR"
LOG="$DIR/10-b2-frr-diagnostico-estatico-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1

echo "========== B2 | DIAGNOSTICO FRR ESTATICO =========="
date -Is
hostname
echo "========== GESTION HOST (ANTES) =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== IMAGEN EN CACHE =========="
sudo docker image inspect "$IMAGE" \
  --format 'Id={{.Id}} Arquitectura={{.Architecture}} Entrypoint={{json .Config.Entrypoint}} Cmd={{json .Config.Cmd}}'
echo "========== CONFIG FRR Y RUTINAS DE ARRANQUE (LECTURA) =========="
sudo docker run --rm --network none --name nl360-frr-static-inspect \
  --cap-drop ALL --read-only --security-opt no-new-privileges \
  --pids-limit 32 --memory 128m --entrypoint /bin/sh "$IMAGE" -c '
    echo "--- usuarios y grupos ---"
    grep "^frr:" /etc/passwd
    grep -E "^(frr|frrvty):" /etc/group
    echo "--- ficheros y propiedades ---"
    ls -ld /etc/frr /var/run/frr /run/frr
    ls -l /etc/frr/daemons
    echo "--- notas iniciales de daemons ---"
    sed -n "1,60p" /etc/frr/daemons
    echo "--- daemons y opciones declaradas ---"
    grep -nE "^(zebra|ospfd|mgmtd|staticd|bgpd|vtysh_enable|zebra_options|ospfd_options)=" /etc/frr/daemons || true
    echo "--- entrypoint completo ---"
    cat /usr/lib/frr/docker-start
    echo "--- frrcommon: funciones pertinentes ---"
    grep -nE "daemon_list|watchfrr|mgmtd|zebra|ospfd|frr.conf|/etc/frr/daemons|source " /usr/lib/frr/frrcommon.sh || true
    echo "--- frrinit: usuarios/propiedades ---"
    grep -nE "chown|chmod|/etc/frr|frr.conf|frrvty|start|permissions" /usr/lib/frr/frrinit.sh | head -n 55 || true
    echo "--- usuario y capacidades proceso inspector (NO daemon) ---"
    id
    grep "^Cap" /proc/self/status
  '
echo "========== POSTCHECK =========="
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
sudo ip netns list
ip -4 -br address show ens33
ip -4 route show default
git status --short --branch
echo "DIAGNOSTICO_ESTATICO: OK (solo lectura, ningun daemon FRR iniciado)."
echo "LOG_LOCAL: $LOG"
