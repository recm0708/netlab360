#!/usr/bin/env bash
# NETLAB360: entrada para instalar ejecutores en una VM nueva.
# El modo plan no requiere root ni realiza cambios.
set -Eeuo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

exec /usr/bin/python3 -I \
    "$DIR/instalar_protegidos.py" "$@"
