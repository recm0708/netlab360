#!/usr/bin/env bash
# NETLAB360 B2-L3: smoke FRR v5 con verificación explícita de acceso y rollback.
# Ensayo mínimo en VM aislada: CAP_SYS_ADMIN requerido por daemons FRR 10.7.1.
# /run/frr y /var/tmp/frr son tmpfs exclusivos del contenedor. NO usa --privileged.
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
NAME="nl360-frr-smoke-v5"
sudo -v
if sudo docker container inspect "$NAME" >/dev/null 2>&1; then
  echo "ERROR: $NAME ya existe. No se elimina ni modifica." >&2; exit 3
fi
sudo docker image inspect "$IMAGE" >/dev/null

DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$DIR"
LOG="$DIR/14-b2-frr-smoke-v5-$(date +%Y%m%d-%H%M%S).log"
TMP="$(mktemp -d /tmp/nl360-smoke-v5.XXXXXXXX)"
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
  if [[ "$TMP" == /tmp/nl360-smoke-v5.* ]]; then sudo rm -rf -- "$TMP"; fi
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
  echo "RESULTADO_SMOKE_FRR_V5=$rc"
  exit "$rc"
}
trap cleanup EXIT
exec > >(tee "$LOG") 2>&1

echo "========== B2 FRR V5 | VERIFICACION DE ACCESO Y ARRANQUE AISLADO =========="
date -Is
hostname
echo "Snapshot base: confirmado por operador; no se inspecciona VMware."
echo "========== PREPARAR ARCHIVOS FRR =========="
sudo docker run --rm --network none --cap-drop ALL \
  --entrypoint /bin/cat "$IMAGE" /etc/frr/daemons > "$TMP/daemons"
# Habilitar explicitamente ambos demonios requeridos por el smoke.
if grep -q '^zebra=' "$TMP/daemons"; then
  sed -i 's/^zebra=.*/zebra=yes/' "$TMP/daemons"
else
  printf 'zebra=yes\n' >> "$TMP/daemons"
fi
sed -i 's/^ospfd=.*/ospfd=yes/' "$TMP/daemons"
cat > "$TMP/frr.conf" <<'EOF'
frr version 10.7.1
frr defaults traditional
hostname NL360-FRR-SMOKE-V5
log stdout
service integrated-vtysh-config
!
router ospf
 ospf router-id 10.79.0.254
!
line vty
!
EOF
# vtysh.conf es independiente de frr.conf y no viene con la imagen.
cat > "$TMP/vtysh.conf" <<'EOF'
service integrated-vtysh-config
hostname NL360-FRR-SMOKE-V5
EOF
sudo chown 100:101 "$TMP" "$TMP/daemons"
sudo chown 100:102 "$TMP/frr.conf" "$TMP/vtysh.conf"
sudo chmod 755 "$TMP"
sudo chmod 640 "$TMP/daemons"
sudo chmod 660 "$TMP/frr.conf" "$TMP/vtysh.conf"
echo "--- Permisos (frr UID100; frr GID101; frrvty GID102) ---"
stat -c '%a %u:%g %n' "$TMP" "$TMP/daemons" "$TMP/frr.conf" "$TMP/vtysh.conf"
# Tras chmod 640 y chown 100:101, el usuario rc-aa-ec no puede leer daemons.
# La inspección de este archivo es de solo lectura; no rebajar sus permisos.
sudo grep -E '^(zebra|ospfd|bgpd|vtysh_enable)=' "$TMP/daemons"

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
    ls -l /etc/frr/daemons /etc/frr/frr.conf /etc/frr/vtysh.conf
    test -r /etc/frr/daemons || { echo "ERROR: daemons no legible"; exit 31; }
    test -r /etc/frr/frr.conf || { echo "ERROR: frr.conf no legible"; exit 32; }
    test -r /etc/frr/vtysh.conf || { echo "ERROR: vtysh.conf no legible"; exit 33; }
    echo "FRR_MOUNT_READABLE: SI"
  '
echo "========== COMPROBAR DIRECTORIO PID AISLADO =========="
# El propio watchfrr crea /var/run/frr/watchfrr.pid (=/run/frr/...)
# El tmpfs es EXCLUSIVO del contenedor y NO toca /run del anfitrion.
# UID0 (proceso inicial) y GID101 (grupo frr) pueden escribir.
PID_TMPFS="/run/frr:rw,nosuid,nodev,size=16m,uid=0,gid=101,mode=0770"
CRASH_TMPFS="/var/tmp/frr:rw,nosuid,nodev,size=16m,uid=100,gid=101,mode=0770"
echo "========== COMPROBAR DIRECTORIO LOG TEMPORAL COMO frr =========="
sudo docker run --rm --network none --cap-drop ALL \
  --user 100:101 --pids-limit 32 --memory 128m \
  --tmpfs "$CRASH_TMPFS" --entrypoint /bin/sh "$IMAGE" -ec '
    ls -ld /var/tmp/frr
    test -w /var/tmp/frr || { echo "ERROR: /var/tmp/frr no escribible"; exit 43; }
    : > /var/tmp/frr/nl360-write-check
    rm -f /var/tmp/frr/nl360-write-check
    echo "FRR_CRASHLOG_WRITABLE: SI"
  '
sudo docker run --rm --network none --cap-drop ALL \
  --cap-add DAC_READ_SEARCH --pids-limit 32 --memory 128m \
  --tmpfs "$PID_TMPFS" \
  --mount "type=bind,source=$TMP,target=/etc/frr,readonly" \
  --entrypoint /bin/sh "$IMAGE" -ec '
    echo "--- directorio de PID dentro del contenedor ---"
    ls -ld /run/frr /var/run/frr
    echo "--- escritura real del proceso de arranque ---"
    test -w /run/frr || { echo "ERROR: /run/frr no escribible"; exit 41; }
    : > /run/frr/nl360-pid-test.lock
    rm -f /run/frr/nl360-pid-test.lock
    test -r /etc/frr/daemons || { echo "ERROR: daemons no legible"; exit 42; }
    echo "FRR_PID_DIR_WRITABLE: SI"
  '
echo "========== ARRANQUE DOCKER SIN --rm =========="
# Los mensajes reales de mgmtd/zebra/ospfd solicitan CAP_SYS_ADMIN.
# Añadimos SYS_ADMIN y DAC_OVERRIDE SOLO en este contenedor efímero con
# --network none; no emplear --privileged, --network host ni compartir ens33.
# DAC_OVERRIDE es necesario para permisos de sockets FRR en modo root.
sudo docker run -d --name "$NAME" --network none \
  --cap-drop ALL --cap-add NET_ADMIN --cap-add NET_RAW \
  --cap-add NET_BIND_SERVICE --cap-add SETPCAP --cap-add SYS_ADMIN \
  --cap-add SETUID --cap-add SETGID --cap-add CHOWN \
  --cap-add DAC_READ_SEARCH --cap-add DAC_OVERRIDE \
  --pids-limit 128 --memory 512m \
  --tmpfs "$PID_TMPFS" --tmpfs "$CRASH_TMPFS" \
  --mount "type=bind,source=$TMP,target=/etc/frr" "$IMAGE"

echo "========== ESPERAR VTYSH (20 SEGUNDOS MAXIMO) =========="
READY=0
for TRY in $(seq 1 20); do
  STATUS="$(sudo docker inspect "$NAME" --format '{{.State.Status}}')"
  if [[ "$STATUS" != running ]]; then
    echo "Contenedor dejó de correr: $STATUS"; break
  fi
  # vtysh puede responder aunque ospfd y zebra hayan fallado:
  # verificar ambos ejecutables como procesos reales usando /proc/comm.
  if sudo docker exec "$NAME" /bin/sh -ec '
    zebra=0; ospfd=0
    for f in /proc/[0-9]*/comm; do
      IFS= read -r proc < "$f" || continue
      [ "$proc" = zebra ] && zebra=1
      [ "$proc" = ospfd ] && ospfd=1
    done
    [ "$zebra" -eq 1 ] && [ "$ospfd" -eq 1 ]
  ' >/dev/null 2>&1; then
    READY=1; echo "FRR_DAEMONS_ACTIVOS: SI (zebra, ospfd; intento $TRY)"; break
  fi
  sleep 1
done
if [[ "$READY" -ne 1 ]]; then
  echo "ERROR: vtysh no está disponible; ver inspect/logs en diagnóstico final."
  exit 4
fi

echo "========== VALIDAR VTYSH Y CARGAR CONFIGURACION =========="
sudo docker exec "$NAME" vtysh -c 'show version'
APPLY="$(sudo docker exec "$NAME" vtysh -b 2>&1)" || { printf '%s\n' "$APPLY"; exit 5; }
printf '%s\n' "$APPLY"
if printf '%s\n' "$APPLY" | grep -qE 'processing failure|failed to connect'; then
  echo "ERROR: carga de configuración integrada no válida"
  exit 5
fi
echo "========== CONSULTAR OSPF ACTIVO =========="
OSPF="$(sudo docker exec "$NAME" vtysh -c 'show ip ospf' 2>&1)" || { printf '%s\n' "$OSPF"; exit 6; }
printf '%s\n' "$OSPF"
if printf '%s\n' "$OSPF" | grep -qiE 'ospfd is not running|failed to connect'; then
  echo "ERROR: ospfd no disponible realmente"
  exit 6
fi
if ! printf '%s\n' "$OSPF" | grep -qiE 'OSPF Routing Process|Router ID:|Routing Process.*ospf'; then
  echo "ERROR: respuesta OSPF sin evidencia suficiente de proceso activo"
  exit 6
fi
echo "OSPF_CONTROL_PLANE: OK"
echo "========== PROCESOS E INTERFACES =========="
sudo docker top "$NAME" -eo pid,comm,args
sudo docker exec "$NAME" ip -4 -br address
echo "PRUEBA_SMOKE_FRR_V5: OK (demonios, vtysh y OSPF sin WAN/vecinos)."
