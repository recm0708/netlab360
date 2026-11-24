#!/usr/bin/env bash
# NETLAB360 | Validación: precheck b2 l2 trunk acl
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# NETLAB360 B2-L2: precheck NO destructivo de capacidades trunk/VLAN/ACL.
set -Eeuo pipefail
cd "$HOME/proyectos/netlab360"
[[ "$(hostname)" == "netlab360-lab" ]] || { echo 'ERROR: hostname'; exit 3; }
[[ "$(id -u)" -ne 0 ]] || { echo 'ERROR: cuenta root'; exit 3; }
sudo -v
mkdir -p "$HOME/netlab360-bootstrap/evidencias"
LOG="$HOME/netlab360-bootstrap/evidencias/b2-l2-precheck-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1
echo '========== PRECHECK TRUNK VLAN ACL =========='
date -Is; hostname; echo "LOG_LOCAL=$LOG"
FAIL=0
for x in ip bridge nsenter python3 ping sudo git; do
  if command -v "$x" >/dev/null; then echo "REQUERIDO_OK=$x"; else echo "REQUERIDO_FALTA=$x"; FAIL=$((FAIL+1)); fi
done
python3 scripts/validacion/validar_ipam.py inventario/ipam/topologia-b1.yaml || FAIL=$((FAIL+1))
bash -n scripts/laboratorio/b2-l2-aislado.sh
ip -4 -br address show ens33
ip -4 route show default
if ip -4 -br address show ens33 | grep -Fq '192.168.47.40/24' && ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33'; then echo 'RED_GESTION=OK'; else echo 'RED_GESTION=ERROR'; FAIL=$((FAIL+1)); fi
uname -r
bridge -V || true
if command -v nft >/dev/null 2>&1; then nft --version; echo 'NFT_DISPONIBLE=SI'; else echo 'NFT_DISPONIBLE=NO_PLANIFICAR'; fi
for x in bridge 8021q bonding; do if [ -e "/sys/module/$x" ]; then echo "MODULO_VISIBLE=$x"; else echo "MODULO_NO_VISIBLE=$x"; fi; done
echo '========== DOCKER Y NAMESPACES (SOLO LECTURA) =========='
sudo -n docker ps -a || true
sudo -n ip netns list
git status --short --branch
echo "REQUERIDOS_FALTANTES=$FAIL"
if [ "$FAIL" -eq 0 ]; then echo 'B2_L2_PREFLIGHT=OK'; else echo 'B2_L2_PREFLIGHT=ERROR'; exit 1; fi
