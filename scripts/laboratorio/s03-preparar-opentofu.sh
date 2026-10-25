#!/usr/bin/env bash
# NETLAB360 fase 3: preparar espacio aislado para OpenTofu metadata-only.
# No inicia routers, no modifica enlaces WAN/LAN y nunca sobrescribe states.
set -Eeuo pipefail

ROOT="$HOME/proyectos/netlab360"
ART="$HOME/netlab360-bootstrap/iac/s03"
WORK="$ART/work"
MODEL="$ROOT/iac/s03/main.tf"
WAN_STATE="$HOME/netlab360-bootstrap/s02/wan-links-state.json"
LAN_STATE="$HOME/netlab360-bootstrap/s02/lan-vlan-state.json"

cd "$ROOT"
echo "========== PRECHECK OPENTOFU FASE 3 =========="
test "$(id -u)" -ne 0
test -f "$MODEL"
test -f "$ROOT/inventario/ipam/topologia-s02.yaml"
ip -4 -o addr show dev ens33 | grep -Fq '192.168.47.40/24'
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33'
test -z "$(git status --porcelain)"

if [[ -f "$WAN_STATE" && -f "$LAN_STATE" ]]; then
    echo "S03_TOFU_MODO_S02=DESPLEGADA_CON_ESTADOS"
elif [[ ! -e "$WAN_STATE" && ! -L "$WAN_STATE" &&
        ! -e "$LAN_STATE" && ! -L "$LAN_STATE" ]]; then
    # La ruta pausada solo se acepta si no quedan contenedores ni netns S02.
    if ! CONTAINERS="$(sudo -n docker ps -a --format '{{.Names}}')"; then
        echo "S03_TOFU_PREPARACION_DETENIDA=DOCKER_NO_COMPROBABLE"
        exit 4
    fi
    if printf '%s\n' "$CONTAINERS" | grep -Eq '^nl360-s02-r-(hq|s1|s2)$'; then
        echo "S03_TOFU_PREPARACION_DETENIDA=CONTENEDORES_S02_RESIDUALES"
        exit 4
    fi
    if ! NETNS="$(ip netns list)"; then
        echo "S03_TOFU_PREPARACION_DETENIDA=NETNS_NO_COMPROBABLE"
        exit 4
    fi
    if printf '%s\n' "$NETNS" | grep -Eq '^nl360-s02-'; then
        echo "S03_TOFU_PREPARACION_DETENIDA=NAMESPACES_S02_RESIDUALES"
        exit 4
    fi
    echo "S03_TOFU_MODO_S02=PAUSADA_Y_LIMPIA"
else
    echo "S03_TOFU_PREPARACION_DETENIDA=ESTADOS_S02_INCOMPLETOS"
    exit 4
fi

if [[ -L "$ART" || -e "$WORK" || -L "$WORK" ]]; then
    echo "S03_TOFU_PREPARACION_DETENIDA=WORK_EXISTENTE_NO_SOBRESCRIBIR"
    exit 3
fi
if [[ -e "$ART/s03-plan.tfplan" || -L "$ART/s03-plan.tfplan" ||
      -e "$ART/s03-manifest.json" || -L "$ART/s03-manifest.json" ||
      -e "$ART/s03-plan.json" || -L "$ART/s03-plan.json" ]]; then
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
