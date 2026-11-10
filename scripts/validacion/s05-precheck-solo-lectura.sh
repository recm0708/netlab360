#!/usr/bin/env bash
# NETLAB360 S05/P0 - Auditoria PREVIA, sin cambios en red, Docker ni SO.
# Ejecutar como usuario regular: bash scripts/validacion/s05-precheck-solo-lectura.sh
set -uo pipefail

FALLOS=0
AVISOS=0
ROOT="$HOME/proyectos/netlab360"
BASE="$HOME/netlab360-bootstrap"

seccion() { printf '\n========== %s ==========\n' "$1"; }
fallo() { printf 'FALLO: %s\n' "$1"; FALLOS=$((FALLOS+1)); }
aviso() { printf 'AVISO: %s\n' "$1"; AVISOS=$((AVISOS+1)); }

seccion "NETLAB360 S05/P0 PRECHECK SOLO LECTURA"
date -Is
printf 'HOSTNAME=%s\nUSUARIO=%s\n' "$(hostname)" "$(id -un)"
if [ "$(hostname)" != "netlab360-lab" ]; then fallo "Nombre de host distinto al esperado"; fi
if [ "$(id -u)" = 0 ]; then fallo "No ejecutar como root"; fi
for bin in ip git python3 ss systemctl df free; do
  command -v "$bin" >/dev/null 2>&1 || fallo "Comando requerido ausente: $bin"
done

seccion "IDENTIFICACION Y RECURSOS"
sed -n '1,8p' /etc/os-release 2>/dev/null || aviso "No se pudo leer /etc/os-release"
uname -r
free -h 2>/dev/null || true
df -h / 2>/dev/null || true

seccion "GESTION VMnet8 - NO TOCAR ens33"
if command -v ip >/dev/null 2>&1; then
  ip -4 -br addr show dev ens33 2>&1 || fallo "Interfaz ens33 no identificada"
  ip -4 route show default
  if ip -4 -o addr show dev ens33 2>/dev/null | grep -Fq '192.168.47.40/24'; then
    echo "S05_IP_GESTION=OK"
  else
    fallo "La IP 192.168.47.40/24 no consta en ens33"
  fi
  if ip -4 route show default 2>/dev/null | grep -Fq 'default via 192.168.47.2 dev ens33'; then
    echo "S05_GATEWAY=OK"
  else
    fallo "La ruta por defecto no coincide con 192.168.47.2 por ens33"
  fi
fi

seccion "REPOSITORIO Y RAMA"
if [ -d "$ROOT/.git" ]; then
  git -C "$ROOT" status --short --branch
  git -C "$ROOT" log -1 --format='S05_COMMIT=%h %cs %s'
  cambios="$(git -C "$ROOT" status --porcelain 2>/dev/null || true)"
  if [ -n "$cambios" ]; then
    aviso "Hay cambios locales; NO ejecutar git pull sin revisarlos"
  else
    echo "S05_ARBOL_LOCAL=LIMPIO"
  fi
else
  fallo "No existe repositorio Git en $ROOT"
fi

seccion "SERVICIOS Y PUERTOS DE OBSERVABILIDAD"
for srv in docker ssh.service ssh.socket open-vm-tools; do
  if command -v systemctl >/dev/null 2>&1; then
    printf 'S05_SERVICIO_%s=%s\n' "$srv" "$(systemctl is-active "$srv" 2>/dev/null || echo no-verificado)"
  fi
done
if command -v ss >/dev/null 2>&1; then
  ss -lnt | grep -E '(:9091|:9110|:9120)([[:space:]]|$)' || echo "S05_PUERTOS_9091_9110_9120=SIN_LISTEN_OBSERVADO"
fi

seccion "TOPOLOGIA S02 - INVENTARIO, NO ALTERAR"
if command -v docker >/dev/null 2>&1; then
  docker --version
  if docker ps -a --filter name=nl360-s02 --format 'CONTENEDOR {{.Names}} ESTADO={{.Status}}' 2>/dev/null; then
    echo "S05_DOCKER_INVENTARIO=CONSULTADO"
  else
    aviso "Docker no accesible sin privilegios; comprobar permisos antes de desplegar"
  fi
else
  aviso "Docker no disponible en PATH"
fi
if command -v ip >/dev/null 2>&1; then
  ip netns list 2>/dev/null | sed -n '1,35p' || aviso "No se pudieron consultar namespaces"
fi
for f in "$BASE/s02/wan-links-state.json" "$BASE/s02/lan-vlan-state.json"; do
  if [ -f "$f" ]; then
    echo "S05_ESTADO_OPERATIVO_PRESENTE=$(basename "$f")"
  else
    echo "S05_ESTADO_OPERATIVO_AUSENTE=$(basename "$f")"
  fi
done

seccion "RESPALDOS E HISTORIAL S04 - VERIFICACION NO DESTRUCTIVA"
for d in "$BASE/s04" "$BASE/s04/evidencias" "$BASE/prometheus/s04/data"; do
  if [ -d "$d" ]; then
    printf 'S05_DIRECTORIO_EXISTE=%s\n' "$d"
  else
    aviso "No consta directorio $d"
  fi
done
if [ -f "$BASE/s04/historial/incidentes.sqlite3" ]; then
  python3 - <<'PY'
from pathlib import Path
import sqlite3
p = Path.home() / "netlab360-bootstrap/s04/historial/incidentes.sqlite3"
try:
    con = sqlite3.connect(p.as_uri() + "?mode=ro", uri=True)
    ok = con.execute("PRAGMA quick_check").fetchone()[0]
    con.close()
    print("S05_SQLITE_INTEGRIDAD=" + str(ok))
except Exception as exc:
    print("S05_SQLITE_NO_VERIFICABLE=" + type(exc).__name__)
PY
else
  aviso "No aparece SQLite S04 en su ruta prevista; revisar respaldo"
fi

seccion "HERRAMIENTAS S05 - SOLO DETECCION"
for bin in iperf3 ovs-vsctl faucet ansible tofu; do
  if command -v "$bin" >/dev/null 2>&1; then
    printf 'S05_HERRAMIENTA_%s=DISPONIBLE\n' "$bin"
  else
    printf 'S05_HERRAMIENTA_%s=NO_INSTALADA_O_NO_EN_PATH\n' "$bin"
  fi
done
seccion "DICTAMEN PRELIMINAR"
printf 'S05_FALLOS=%d\nS05_AVISOS=%d\n' "$FALLOS" "$AVISOS"
echo "S05_CAMBIOS_REALIZADOS_EN_INFRAESTRUCTURA=NINGUNO"
echo "S05_DESPLIEGUE_AUTORIZADO=PENDIENTE_REVISION"
if [ "$FALLOS" -gt 0 ]; then
  echo "S05_PRECHECK_RESULTADO=REVISAR"
  exit 2
fi
echo "S05_PRECHECK_RESULTADO=OK_CON_VALIDACION_PENDIENTE"
