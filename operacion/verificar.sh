#!/usr/bin/env bash
# NETLAB360: comprobación de requisitos sin instalar paquetes.
# Las diferencias de versión se informan para revisión.
set -Eeuo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if (( $# != 0 )); then
    echo "Uso: bash operacion/verificar.sh" >&2
    exit 2
fi

if [[ ! -r /etc/os-release ]]; then
    echo "ERROR: sistema operativo no identificable." >&2
    exit 2
fi

source /etc/os-release

echo "SISTEMA=${PRETTY_NAME:-desconocido}"
echo "ARQUITECTURA=$(uname -m)"

# Solo habilitamos el perfil auditado.
# Las demás distribuciones requieren validación independiente.

if [[ "${ID:-}" != ubuntu ||
      "${VERSION_ID:-}" != 26.04 ||
      "$(uname -m)" != x86_64 ]]; then
    echo "PERFIL=NO_VALIDADO"
    exit 2
fi

echo "PERFIL=ubuntu-26.04-amd64"

manifest="$DIR/perfiles/ubuntu-26.04-amd64/paquetes.tsv"

test -f "$manifest"

missing=0
optional=0
different=0
present=0

while IFS=$'\t' read -r package version category; do
    [[ "$package" == paquete ]] && continue

    if actual="$(dpkg-query -W \
        -f='${Version}\t${Status}' "$package" 2>/dev/null)" &&
        [[ "$actual" == *$'\tinstall ok installed' ]]
    then
        observed="${actual%%$'\t'*}"

        present=$((present + 1))

        if [[ "$observed" == "$version" ]]; then
            echo "PAQUETE_OK=$package | $observed"
        else
            different=$((different + 1))
            echo "VERSION_DIFERENTE=$package | actual=$observed | referencia=$version"
        fi
    else
        if [[ "$category" == opcional ]]; then
            optional=$((optional + 1))
            echo "OPCIONAL_FALTANTE=$package"
        else
            missing=$((missing + 1))
            echo "REQUERIDO_FALTANTE=$package"
        fi
    fi

done < "$manifest"

# Verificamos también los comandos básicos que pueden
# proceder de paquetes ya incluidos por la distribución.

for command in \
    bash sudo git python3 docker ip bridge tc \
    nsenter systemctl systemd-run \
    curl ansible-playbook tofu ovs-vsctl
do
    if ! command -v "$command" >/dev/null; then
        missing=$((missing + 1))
        echo "COMANDO_FALTANTE=$command"
    fi
done

if command -v python3 >/dev/null; then
    if python3 -c \
        'import sys, venv, yaml; assert sys.version_info[:2] == (3, 14)'
    then
        echo "PYTHON_BASE=OK"
    else
        missing=$((missing + 1))
        echo "PYTHON_BASE=INCOMPATIBLE"
    fi
fi

echo "PAQUETES_PRESENTES=$present"
echo "REQUISITOS_FALTANTES=$missing"
echo "OPCIONALES_FALTANTES=$optional"
echo "VERSIONES_DIFERENTES=$different"

if (( missing > 0 )); then
    echo "REQUISITOS_BASE=INCOMPLETOS"
    exit 1
fi

echo "REQUISITOS_BASE=DISPONIBLES"
echo "COMPATIBILIDAD_INTEGRAL=REQUIERE_VALIDACION"
echo "VERIFICACION_SOLO_LECTURA=OK"
