#!/usr/bin/env bash
# Presentamos la secuencia de reconstrucción del laboratorio.
# No disponemos todavía de aceptación para el despliegue automático.
set -Eeuo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$#" -ne 1 || "${1:-}" != "--plan" ]]; then
    echo "Uso: bash operacion/desplegar.sh --plan" >&2
    exit 2
fi

exec python3 "$DIR/ciclo_vida.py" deploy-plan
