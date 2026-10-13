#!/usr/bin/env bash
# NETLAB360 B2-L3: smoke FRR v3 con verificación explícita de acceso y rollback.
# Capacidades concretas FRR revisadas; SYS_ADMIN tiene alcance amplio dentro del contenedor.
# NO crea WAN, no usa network host, no toca ens33.
set -Eeuo pipefail

if [[ "$#" -ne 1 ]]; then
  echo "Uso: bash $0 --snapshot-confirmado"; exit 2
fi
if [[ "$1" != "--snapshot-confirmado" ]]; then
  echo "Uso: bash $0 --snapshot-confirmado"; exit 2
fi
[[ "$(hostname)" == netlab360-lab ]] || { echo "Host no esperado" >&2; exit 2; }
ip -4 -o address show dev ens33 | grep -q '192\.168\.47\.40/24' || { echo "IP ens33 inesperada" >&2; exit 2; }
ip -4 route show default | grep -q 'default via 192\.168\.47\.2 dev ens33' || { echo "Gateway inesperado" >&2; exit 2; }

cd "$HOME/proyectos/netlab360"
python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml
IMAGE="quay.io/frrouting/frr:10.7.1"
NAME="nl360-frr-smoke-v3"
sudo -v
if sudo docker container inspect "$NAME" >/dev/null 2>&1; then
  echo "ERROR: $NAME ya existe. No se elimina ni modifica." >&2; exit 3
fi
sudo docker image inspect "$IMAGE" >/dev/null

DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$DIR"
LOG="$DIR/12-b2-frr-smoke-v3-$(date +%Y%m%d-%H%M%S).log"
TMP="$(mktemp -d /tmp/nl360-smoke-v3.XXXXXXXX)"
IP_BEFORE="$(ip -4 -o address show dev ens33)"
ROUTES_BEFORE="$(ip -4 route show table main)"

cleanup() {
  local rc=$?
  trap - EXIT
  set +e
  echo "========== CAPTURAR ESTADO FRR ANTES DE LIMPIAR =========="
  if sudo docker container inspect "$NAME" >/dev/null 2>&1; then
    sudo docker inspect "$NAME" --format 'Estado={{.State.Status}} ExitCode={{.State.ExitCode}} Error={{.State.Error}}' || true
    echo "--- Procesos del contenedor ---"
    sudo docker top "$NAME" -eo pid,comm,args 2>&1 || true
    echo "--- Logs de arranque (últimas 120 líneas) ---"
    sudo docker logs --timestamps --tail 120 "$NAME" 2>&1 || true
    sudo docker rm -f "$NAME" >/dev/null || true
  fi
  if [[ "$TMP" == /tmp/nl360-smoke-v3.* ]]; then sudo rm -rf -- "$TMP"; fi
  if [[ "$(ip -4 -o address show dev ens33)" != "$IP_BEFORE" ]]; then
    echo "ALERTA: ens33 cambió"; rc=6
  fi
  if [[ "$(ip -4 route show table main)" != "$ROUTES_BEFORE" ]]; then
    echo "ALERTA: las rutas del anfitrión cambiaron"; rc=7
  fi
  echo "========== POSTCHECK =========="
  sudo docker ps -a --filter "name=$NAME" --format 'table {{.Names}}\t{{.Status}}'
  ip -4 -br address show ens33
  echo "LOG_LOCAL: $LOG"
  echo "RESULTADO_SMOKE_FRR_V3=$rc"
  exit "$rc"
}
trap cleanup EXIT
exec > >(tee "$LOG") 2>&1

echo "========== B2 FRR V3 | VERIFICACION DE ACCESO Y ARRANQUE AISLADO =========="
date -Is
hostname
echo "Snapshot base: confirmado por operador; no se inspecciona VMware."
echo "========== PREPARAR ARCHIVOS FRR =========="
sudo docker run --rm --network none --cap-drop ALL \
  --entrypoint /bin/cat "$IMAGE" /etc/frr/daemons > "$TMP/daemons"
sed -i 's/^ospfd=.*/ospfd=yes/' "$TMP/daemons"
cat > "$TMP/frr.conf" <<'EOF'
frr version 10.7.1
frr defaults traditional
hostname NL360-FRR-SMOKE-V3
log stdout
service integrated-vtysh-config
!
router ospf
 ospf router-id 10.79.0.254
!
line vty
!
EOF
sudo chown 100:101 "$TMP" "$TMP/daemons"
sudo chown 100:102 "$TMP/frr.conf"
sudo chmod 755 "$TMP"
sudo chmod 640 "$TMP/daemons"
sudo chmod 660 "$TMP/frr.conf"
echo "--- Permisos (frr UID100; frr GID101; frrvty GID102) ---"
stat -c '%a %u:%g %n' "$TMP" "$TMP/daemons" "$TMP/frr.conf"
# Tras chmod 640 y chown 100:101, el usuario rc-aa-ec no puede leer daemons.
# La inspección de este archivo es de solo lectura; no rebajar sus permisos.
sudo grep -E '^(ospfd|bgpd|vtysh_enable)=' "$TMP/daemons"

echo "========== VERIFICAR LECTURA REAL DE ARCHIVOS DENTRO DE DOCKER =========="
# En frrcommon.sh se evalúa -r para daemons; si falta permiso, el mensaje dice
# "does not exist" aunque el fichero sí esté montado. CAP_DAC_READ_SEARCH
# permite lectura al proceso inicial root sin modificar 0640/0660 de frr.
sudo docker run --rm --network none --cap-drop ALL \
  --cap-add DAC_READ_SEARCH --security-opt no-new-privileges \
  --pids-limit 32 --memory 128m \
  --mount "type=bind,source=$TMP,target=/etc/frr,readonly" \
  --entrypoint /bin/sh "$IMAGE" -ec '
    echo "--- identidad ---"
    id
    echo "--- permisos dentro del montaje ---"
    ls -ld /etc/frr
    ls -l /etc/frr/daemons /etc/frr/frr.conf
    test -r /etc/frr/daemons || { echo "ERROR: daemons no legible"; exit 31; }
    test -r /etc/frr/frr.conf || { echo "ERROR: frr.conf no legible"; exit 32; }
    echo "FRR_MOUNT_READABLE: SI"
  '
echo "========== ARRANQUE DOCKER SIN --rm =========="
# FRR watchfrr/zebra/mgmtd/ospfd necesitan capacidades concretas.
# CAP_SYS_ADMIN es poderosa, pero requerida por los procesos FRR indicados;
# CAP_SETPCAP es necesaria para gestionar capacidades tras bajar privilegios.
# DAC_READ_SEARCH es necesaria para que el lanzador root lea daemons 0640 frr:frr.
# Este contenedor carece de red y no comparte network namespace del anfitrion.
sudo docker run -d --name "$NAME" --network none \
  --cap-drop ALL --cap-add NET_ADMIN --cap-add NET_RAW \
  --cap-add SYS_ADMIN --cap-add NET_BIND_SERVICE --cap-add SETPCAP \
  --cap-add SETUID --cap-add SETGID --cap-add CHOWN --cap-add DAC_READ_SEARCH \
  --pids-limit 128 --memory 512m \
  --mount "type=bind,source=$TMP,target=/etc/frr" "$IMAGE"

echo "========== ESPERAR VTYSH (20 SEGUNDOS MAXIMO) =========="
READY=0
for TRY in $(seq 1 20); do
  STATUS="$(sudo docker inspect "$NAME" --format '{{.State.Status}}')"
  if [[ "$STATUS" != running ]]; then
    echo "Contenedor dejó de correr: $STATUS"; break
  fi
  if sudo docker exec "$NAME" vtysh -c 'show version' >/dev/null 2>&1; then
    READY=1; echo "VTYSH_DISPONIBLE: SI (intento $TRY)"; break
  fi
  sleep 1
done
if [[ "$READY" -ne 1 ]]; then
  echo "ERROR: vtysh no está disponible; ver inspect/logs en diagnóstico final."
  exit 4
fi

echo "========== APLICAR CONFIGURACION INTEGRADA =========="
sudo docker exec "$NAME" vtysh -b
echo "========== CONSULTAR OSPF =========="
sudo docker exec "$NAME" vtysh -c 'show ip ospf'
echo "========== PROCESOS E INTERFACES =========="
sudo docker top "$NAME" -eo pid,comm,args
sudo docker exec "$NAME" ip -4 -br address
echo "PRUEBA_SMOKE_FRR_V3: OK (sin WAN ni vecinos)."
