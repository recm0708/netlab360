#!/usr/bin/env bash
# Preparamos archivos de ejecución únicamente en una VM nueva.
# No iniciamos servicios, routers ni redes virtuales.

set -Eeuo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE="$HOME/netlab360-bootstrap"

cd "$ROOT"

fail() {
    printf 'RUNTIME_ERROR=%s\n' "$*" >&2
    exit 3
}

if [[ "$#" -eq 1 && "$1" == "--plan" ]]; then
    echo "MODO=PLAN"
    echo "1. Verificar identidad y ausencia de recursos anteriores."
    echo "2. Generar configuraciones en un directorio independiente."
    echo "3. Preparar configuraciones FRR de los tres routers."
    echo "4. Preparar configuración y directorio de logs Faucet."
    echo "5. Verificar la imagen local fijada de Prometheus."
    echo "6. Extraer binarios sin iniciar contenedores."
    echo "7. Preparar configuración y almacenamiento Prometheus."
    echo "8. Validar configuración y reglas de alertas."
    echo "SERVICIOS_INICIADOS=NO"
    echo "PLAN_RUNTIME=OK"
    exit 0
fi

[[ "$#" -eq 2 && "$1" == "--apply" &&
   "$2" == "--confirm-clean-host" ]] ||
    fail "Usar --plan o --apply --confirm-clean-host"

[[ "$(id -u)" != 0 ]] ||
    fail "Ejecutar como usuario ordinario"

sudo -n true

# Reutilizamos las comprobaciones de reconstrucción,
# sin invocar su modalidad de despliegue.

python3 -B - <<'PY'
import sys

sys.path.insert(0, "operacion")

import reconstruir

reconstruir.check_management()
reconstruir.check_empty_resources()
reconstruir.check_images()

if reconstruir.read("git", "status", "--porcelain"):
    raise SystemExit("REPOSITORY_NOT_CLEAN")

print("RUNTIME_PRECHECK=OK")
PY

# No reemplazamos configuraciones ni almacenamiento anterior.

for path in \
    "$BASE/s02/rendered" \
    "$BASE/s05/sdn-faucet" \
    "$BASE/prometheus"
do
    [[ ! -e "$path" && ! -L "$path" ]] ||
        fail "Destino preexistente: $path"
done

for port in 9090 9091 9110 9130 16653; do
    [[ -z "$(ss -H -ltn "sport = :$port")" ]] ||
        fail "Puerto ocupado: $port"
done

# La configuración se genera desde el repositorio,
# no desde estados históricos de otro laboratorio.

WORK="$(mktemp -d "$HOME/netlab360-configuracion.XXXXXXXX")"
BUNDLE="$WORK/bundle"

bash operacion/configurar.sh --prepare "$BUNDLE"

python3 -B - "$BUNDLE" "$BASE" <<'PY'
from pathlib import Path
import shutil
import sys

bundle, base = map(Path, sys.argv[1:])

def unique(name):
    matches = [
        p for p in bundle.rglob(name)
        if p.is_file() and not p.is_symlink()
    ]

    if len(matches) != 1:
        raise RuntimeError(f"Fuente ambigua o ausente: {name}")

    return matches[0]

# Validamos primero todas las fuentes requeridas.

routers = {
    name: unique(name + ".frr.conf")
    for name in ("R-HQ", "R-S1", "R-S2")
}

faucet = unique("faucet.yaml")

rendered = base / "s02/rendered"
sdn = base / "s05/sdn-faucet"

for path in (rendered, sdn):
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"Destino preexistente: {path}")

rendered.mkdir(parents=True, mode=0o700)
(sdn / "config").mkdir(parents=True, mode=0o700)
(sdn / "logs").mkdir(mode=0o700)

for name, source in routers.items():
    shutil.copyfile(
        source,
        rendered / (name + ".frr.conf"),
    )

shutil.copyfile(
    faucet,
    sdn / "config/faucet.yaml",
)

print("FRR_PREPARADO=3/3")
print("FAUCET_PREPARADO=OK")
PY

# El extractor existente utiliza una imagen local verificada
# previamente por su referencia inmutable.
# Crea un contenedor temporal sin iniciarlo.

# Reproducimos la propiedad y los permisos del runtime Faucet validado.
# Solo se alcanza esta etapa tras las comprobaciones de VM limpia.
FAUCET_LOGS="$BASE/s05/sdn-faucet/logs"

test -d "$FAUCET_LOGS"
test ! -L "$FAUCET_LOGS"

sudo -n chown "0:$(id -g)" -- "$FAUCET_LOGS"
sudo -n chmod 0750 -- "$FAUCET_LOGS"

test "$(stat -c '%u:%g:%a' "$FAUCET_LOGS")" = "0:$(id -g):750"

echo "FAUCET_LOGS_PERMISOS=OK"

bash scripts/observabilidad/preparar-prometheus-local.sh

mkdir -p "$BASE/prometheus/s04/data"
mkdir -p "$BASE/prometheus/s04/rules"

cp --no-clobber \
    servicios/observabilidad/prometheus/s04-prometheus.yml \
    "$BASE/prometheus/s04/prometheus-runtime.yml"

cp --no-clobber \
    servicios/observabilidad/prometheus/rules/s04-alerts.yml \
    "$BASE/prometheus/s04/rules/s04-alerts.yml"

"$BASE/prometheus/bin/promtool" check config \
    "$BASE/prometheus/s04/prometheus-runtime.yml"

"$BASE/prometheus/bin/promtool" check rules \
    "$BASE/prometheus/s04/rules/s04-alerts.yml"

"$BASE/prometheus/bin/promtool" test rules \
    servicios/observabilidad/prometheus/tests/s04-alertas.test.yml

echo "CONFIGURACION_GENERADA=$BUNDLE"
echo "RUNTIME_PREPARADO=OK"
echo "SERVICIOS_INICIADOS=NO"
echo "TOPOLOGIA_DESPLEGADA=NO"
