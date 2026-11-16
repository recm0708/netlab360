#!/usr/bin/env bash
# NETLAB360 | Laboratorio: s02 routers start
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# Inicio EXCLUSIVO de tres routers FRR aislados por Docker Compose S02.
# Valida runtime 3/3 ANTES de hacer compose up. NO crea WAN, VLAN o rutas host.
set -Eeuo pipefail
cd "$HOME/proyectos/netlab360"
BASE="$HOME/netlab360-bootstrap/s02"
COMPOSE="topologias/s02-frr/docker-compose.yml"
IMAGEN="quay.io/frrouting/frr:10.7.1"
sudo -v

echo "========== S02 VERIFICACION PREVIA =========="
bash scripts/diagnostico/precheck-s02.sh
sudo env HOME="$HOME" docker compose -f "$COMPOSE" config --quiet

for R in R-HQ R-S1 R-S2; do
  SRC="$BASE/rendered/$R.frr.conf"
  DST="$BASE/runtime/$R"
  [[ -d "$DST" && ! -L "$DST" ]] || {
    echo "S02_ERROR: runtime ausente o simbolico: $R"; exit 4;
  }
  for F in daemons frr.conf vtysh.conf; do
    [[ -f "$DST/$F" && ! -L "$DST/$F" ]] || {
      echo "S02_ERROR: archivo $R/$F faltante"; exit 4;
    }
  done
  sudo -n cmp -s "$SRC" "$DST/frr.conf" || {
    echo "S02_ERROR: archivo FRR diferente: $R"; exit 4;
  }
  [[ "$(sudo -n stat -c '%u:%g %a' "$DST/daemons")" == "100:101 640" ]] || exit 4
  [[ "$(sudo -n stat -c '%u:%g %a' "$DST/frr.conf")" == "100:102 660" ]] || exit 4
  [[ "$(sudo -n stat -c '%u:%g %a' "$DST/vtysh.conf")" == "100:102 660" ]] || exit 4
  sudo -n grep -qx 'zebra=yes' "$DST/daemons" || exit 4
  sudo -n grep -qx 'ospfd=yes' "$DST/daemons" || exit 4
  echo "S02_RUNTIME_VERIFICADO=$R"
done

for C in nl360-s02-r-hq nl360-s02-r-s1 nl360-s02-r-s2; do
  if sudo -n docker container inspect "$C" >/dev/null 2>&1; then
    echo "S02_ERROR: contenedor ya existe: $C"; exit 4
  fi
done

echo "========== S02 INICIAR AISLADOS =========="
sudo env HOME="$HOME" docker compose -f "$COMPOSE" up -d
sleep 6

echo "========== S02 REVISAR FRR =========="
for C in nl360-s02-r-hq nl360-s02-r-s1 nl360-s02-r-s2; do
  RUNNING="$(sudo -n docker inspect -f '{{.State.Running}}' "$C")"
  NETWORK="$(sudo -n docker inspect -f '{{.HostConfig.NetworkMode}}' "$C")"
  [[ "$RUNNING" == true && "$NETWORK" == none ]] || {
    echo "S02_ERROR: $C running=$RUNNING network=$NETWORK"; exit 5;
  }
  INFO="$(sudo -n docker exec "$C" vtysh -c 'show version' 2>&1)" || {
    echo "$INFO"; echo "S02_ERROR: vtysh $C"; exit 5;
  }
  if printf '%s\n' "$INFO" | grep -Eqi "processing failure|Can't open|does not exist"; then
    echo "$INFO"; echo "S02_ERROR: config FRR $C"; exit 5
  fi
  LOGS="$(sudo -n docker logs --tail 75 "$C" 2>&1)" || exit 5
  if printf '%s\n' "$LOGS" | grep -Eqi 'cannot run|frr.conf does not exist|processing failure|Operation not permitted'; then
    echo "$LOGS"; echo "S02_ERROR: inicializacion FRR $C"; exit 5
  fi
  echo "S02_ROUTER_OPERATIVO=$C NETWORK=none"
done

ip -4 -br addr show ens33
ip -4 route show default
echo "S02_ROUTER_START_OK=3"
echo "S02_ENLACES_WAN_CREADOS=0"
echo "S02_RESULTADO_ARRANQUE=0"
