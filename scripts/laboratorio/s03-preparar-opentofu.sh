#!/usr/bin/env bash
# NETLAB360 S03 — crear ESPACIO EXTERNO para OpenTofu SIN sobrescribir states.
# Ejecutar como usuario SSH, no como root ni en subshell con sudo.
set -Eeuo pipefail
cd "$HOME/proyectos/netlab360"
ROOT="$PWD"
ART="$HOME/netlab360-bootstrap/iac/s03"
WORK="$ART/work"
MODEL="$ROOT/iac/s03/main.tf"
echo "========== PRECHECK OPEN TOFU S03 =========="
test "$(id -u)" -ne 0
test -f "$MODEL"
test -f "$ROOT/inventario/ipam/topologia-s02.yaml"
test -f "$HOME/netlab360-bootstrap/s02/wan-links-state.json"
test -f "$HOME/netlab360-bootstrap/s02/lan-vlan-state.json"
ip -4 -o addr show dev ens33 | grep -Fq '192.168.47.40/24'
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33'
test -z "$(git status --porcelain)"
if [[ -e "$WORK" || -L "$WORK" ]]; then
    echo "S03_TOFU_PREPARACION_DETENIDA=WORK_EXISTENTE_NO_SOBRESCRIBIR"
    exit 3
fi
if [[ -e "$ART/s03-plan.tfplan" || -L "$ART/s03-plan.tfplan" ||
      -e "$ART/s03-manifest.json" || -L "$ART/s03-manifest.json" ]]; then
    echo "S03_TOFU_PREPARACION_DETENIDA=ARTEFACTOS_EXISTENTES"
    exit 3
fi
umask 077
mkdir -p -m 700 "$ART" "$WORK"
install -m 600 "$MODEL" "$WORK/main.tf"
echo "S03_TOFU_WORKDIR=$WORK"
echo "S03_TOFU_MODULE_ORIGEN=$MODEL"
echo "S03_TOFU_ANTERIORES=SIN_SOBRESCRITURA"
echo "S03_TOFU_PREPARACION=OK"
