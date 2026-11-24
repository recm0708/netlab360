#!/usr/bin/env bash
# NETLAB360 B2-L3: prueba efimera de arranque de FRR, SIN redes WAN.
# No vincular ens33, no modificar rutas del anfitrion.
set -Eeuo pipefail

if [[ "$#" -ne 1 || "$1" != "--snapshot-confirmado" ]]; then
  echo "Uso: bash $0 --snapshot-confirmado"
  echo "Necesita snapshot NETLAB360-BASE-HERRAMIENTAS verificado por el operador."
  exit 2
fi
[[ "$(hostname)" == "netlab360-lab" ]] || { echo "Host no esperado"; exit 2; }
ip -4 -o addr show ens33 | grep -q '192\.168\.47\.40/24' || { echo "IP ens33 inesperada"; exit 2; }
ip -4 route show default | grep -q 'default via 192\.168\.47\.2 dev ens33' || { echo "Ruta de gestion inesperada"; exit 2; }
cd "$HOME/proyectos/netlab360"
python3 scripts/validacion/validar_ipam.py inventario/ipam/topologia-b1.yaml

IMAGE="quay.io/frrouting/frr:10.7.1"
NAME="nl360-frr-smoke"
sudo -v
if sudo docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "Ya existe $NAME, no se eliminara un recurso preexistente."; exit 3
fi
DIR="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$DIR"
LOG="$DIR/09-b2-frr-smoke-$(date +%Y%m%d-%H%M%S).log"
TMP="$(mktemp -d)"
ORIG_IP="$(ip -4 -o addr show ens33)"
ORIG_ROUTES="$(ip -4 route show table main)"

cleanup() {
  RC=$?
  trap - EXIT
  echo "========== LIMPIEZA CONTENEDOR SMOKE =========="
  if sudo docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
    sudo docker logs --tail 50 "$NAME" 2>&1 || true
    sudo docker rm -f "$NAME" >/dev/null || true
  fi
  rm -rf -- "$TMP"
  if [[ "$(ip -4 -o addr show ens33)" != "$ORIG_IP" ]]; then
    echo "ALERTA: ens33 ha cambiado"; RC=4
  fi
  if [[ "$(ip -4 route show table main)" != "$ORIG_ROUTES" ]]; then
    echo "ALERTA: rutas de anfitrion cambiaron"; RC=5
  fi
  echo "LOG_LOCAL: $LOG"
  echo "RESULTADO_SMOKE_FRR=$RC"
  exit "$RC"
}
trap cleanup EXIT
exec > >(tee "$LOG") 2>&1

echo "========== B2 | ARRANQUE FRR SIN WAN =========="
date -Is
hostname
echo "Imagen: $IMAGE"
sudo docker image inspect "$IMAGE" --format 'OS={{.Os}} Arch={{.Architecture}} Digest={{json .RepoDigests}}'
echo "========== EXTRAER DAEMONS ORIGINAL =========="
sudo docker run --rm --network none --cap-drop ALL --entrypoint /bin/cat "$IMAGE" /etc/frr/daemons > "$TMP/daemons"
if grep -q '^zebra=' "$TMP/daemons"; then
  sed -i 's/^zebra=.*/zebra=yes/' "$TMP/daemons"
else
  printf '\nzebra=yes\n' >> "$TMP/daemons"
fi
if grep -q '^ospfd=' "$TMP/daemons"; then
  sed -i 's/^ospfd=.*/ospfd=yes/' "$TMP/daemons"
else
  printf '\nospfd=yes\n' >> "$TMP/daemons"
fi
cat > "$TMP/frr.conf" <<'EOF'
frr version 10.7.1
frr defaults traditional
hostname NL360-FRR-SMOKE
log stdout
service integrated-vtysh-config
!
router ospf
 ospf router-id 10.79.0.254
!
line vty
!
EOF
chmod 755 "$TMP"
chmod 644 "$TMP/daemons" "$TMP/frr.conf"
echo "========== DAEMONS PROPUESTOS =========="
grep -E '^(zebra|ospfd|bgpd|vtysh_enable)=' "$TMP/daemons" || true
echo "========== ARRANCAR CONTENEDOR AISLADO =========="
sudo docker run --rm -d --name "$NAME" \
  --network none --cap-drop ALL --cap-add NET_ADMIN --cap-add NET_RAW \
  --security-opt no-new-privileges --pids-limit 128 --memory 256m \
  -v "$TMP:/etc/frr:rw" "$IMAGE"

echo "========== ESPERAR DISPONIBILIDAD DEL CONTROL PLANE =========="
READY=0
for TRY in 1 2 3 4 5 6 7 8 9 10; do
  if sudo docker exec "$NAME" vtysh -c 'show ip ospf' >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done
if [[ "$READY" -ne 1 ]]; then
  echo "ERROR: ospfd/vtysh no respondieron a tiempo."
  exit 4
fi

echo "========== VERSION / OSPF =========="
sudo docker exec "$NAME" vtysh -c 'show version'
sudo docker exec "$NAME" vtysh -c 'show ip ospf'
echo "========== LOGS DE ARRANQUE =========="
sudo docker logs --tail 70 "$NAME"
echo "========== COMPROBAR AUSENCIA DE WAN =========="
sudo docker exec "$NAME" ip -4 -br address
sudo docker ps --filter "name=$NAME" --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "PRUEBA DE ARRANQUE: OK (solo demonios FRR; sin vecinos ni WAN)."
