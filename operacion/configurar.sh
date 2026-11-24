#!/usr/bin/env bash
# NETLAB360: generación aislada de configuraciones de las fases 01–07.
# No instala ejecutores, no activa unidades y no modifica redes.
set -Eeuo pipefail
umask 077

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "$DIR/.." && pwd)"

usage() {
    cat <<'EOF'
NETLAB360 - Preparación de configuraciones

Uso:
  bash operacion/configurar.sh --plan
  bash operacion/configurar.sh --prepare /ruta/nueva

El destino debe ser nuevo y estar fuera del repositorio.
El paquete generado corresponde al perfil histórico de referencia.

No instala archivos en /etc ni /usr/local/libexec.
No configura sudoers, inicia servicios ni crea namespaces.
No genera identidades de ejecución ni copia estados históricos.
EOF
}

if (( $# == 0 )); then
    set -- --plan
fi

if [[ "$1" == --help && $# == 1 ]]; then
    usage
    exit 0
fi

if [[ "$1" == --plan && $# == 1 ]]; then
    echo "MODO=PLAN"
    echo "PERFIL=ubuntu-26.04-amd64"
    echo "1. Renderizar FRR desde el inventario S02."
    echo "2. Preparar 13 ejecutores protegidos."
    echo "3. Preparar seis unidades systemd existentes."
    echo "4. Generar configuración Prometheus y unidad candidata."
    echo "5. Preparar configuración SDN y regla limitada del observador."
    echo "6. Registrar permisos de destino."
    echo "7. Mantener estados e identidades de ejecución independientes."
    echo "INSTALACION_PRIVILEGIADA=NO"
    echo "PLAN_CONFIGURACION=OK"
    exit 0
fi

if [[ "$1" != --prepare || $# != 2 ]]; then
    usage >&2
    exit 2
fi

if [[ "$(id -u)" == 0 ]]; then
    echo "ERROR: generar como usuario normal." >&2
    exit 2
fi

exec python3 -B "$DIR/generar_configuracion.py" \
    --repo "$REPO" \
    --output "$2"
