#!/usr/bin/env bash
# NETLAB360: instalador de dependencias para un anfitrión dedicado.
# El modo predeterminado no modifica el sistema.
set -Eeuo pipefail
umask 077

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd -- "$DIR/.." && pwd)"

MODE=plan
CONFIRM=0
OPTIONAL=0
EXACT=0

usage() {
    cat <<'EOF'
NETLAB360 - Instalación de dependencias

Uso:
  bash operacion/instalar.sh --plan
  bash operacion/instalar.sh --apply --confirm-clean-host

Opciones:
  --plan                 Mostrar el procedimiento sin ejecutarlo.
  --apply                Instalar dependencias.
  --confirm-clean-host   Confirmar que se utiliza una VM dedicada.
  --with-optional        Incluir utilidades auxiliares.
  --exact-versions       Exigir versiones APT del manifiesto.
  --help                 Mostrar esta ayuda.

Perfil: Ubuntu 26.04 amd64.
No modifica deliberadamente la IP, gateway o hostname.
No despliega la topología ni ejecuta escenarios de falla.
No ejecuta apt upgrade, autoremove, purge ni Docker prune.
EOF
}

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

while (( $# > 0 )); do
    case "$1" in
        --plan) MODE=plan ;;
        --apply) MODE=apply ;;
        --confirm-clean-host) CONFIRM=1 ;;
        --with-optional) OPTIONAL=1 ;;
        --exact-versions) EXACT=1 ;;
        --help) usage; exit 0 ;;
        *) fail "Argumento no reconocido: $1" ;;
    esac
    shift
done

if [[ "$MODE" == apply && "$CONFIRM" != 1 ]]; then
    fail "Se requiere --confirm-clean-host."
fi

[[ "$(id -u)" != 0 ]] ||
    fail "Ejecutar como usuario normal."

source /etc/os-release

[[ "${ID:-}" == ubuntu &&
   "${VERSION_ID:-}" == 26.04 &&
   "$(uname -m)" == x86_64 ]] ||
    fail "Perfil de sistema operativo no validado."

PROFILE="$DIR/perfiles/ubuntu-26.04-amd64"
BOOT="$HOME/netlab360-bootstrap"
VENV="$BOOT/entornos/netlab360-s06-s08"

MANIFEST="$PROFILE/paquetes.tsv"
IMAGES="$DIR/imagenes.tsv"
REQUIREMENTS="$REPO/requirements-cientifico.txt"

for file in "$MANIFEST" "$IMAGES" "$REQUIREMENTS"; do
    [[ -f "$file" ]] || fail "Manifiesto ausente: $file"
done

declare -a BASE_PACKAGES=()
declare -a EXTERNAL_PACKAGES=()
declare -a OPTIONAL_PACKAGES=()

# Utilizamos los manifiestos como fuente de dependencias.
# Las versiones observadas no siempre estarán disponibles.

while IFS=$'\t' read -r name version category; do
    [[ "$name" == paquete ]] && continue

    [[ "$name" =~ ^[a-z0-9][a-z0-9+.-]*$ ]] ||
        fail "Nombre de paquete inválido."

    [[ "$version" =~ ^[a-zA-Z0-9.+:~_-]+$ ]] ||
        fail "Versión inválida."

    package="$name"

    if (( EXACT == 1 )); then
        package="$name=$version"
    fi

    case "$category" in
        base)
            BASE_PACKAGES+=("$package")
            ;;
        externo)
            EXTERNAL_PACKAGES+=("$package")
            ;;
        opcional)
            # Las herramientas de integración VMware
            # dependen del hipervisor y del tipo de escritorio.
            case "$name" in
                open-vm-tools|open-vm-tools-desktop|bpftool)
                    continue
                    ;;
            esac
            if (( OPTIONAL == 1 )); then
                OPTIONAL_PACKAGES+=("$package")
            fi
            ;;
        *)
            fail "Categoría no reconocida: $category"
            ;;
    esac
done < "$MANIFEST"

(( ${#BASE_PACKAGES[@]} > 0 )) ||
    fail "Manifiesto base vacío."

(( ${#EXTERNAL_PACKAGES[@]} == 8 )) ||
    fail "Manifiesto externo incompleto."

echo "NETLAB360_MODO=$MODE"
echo "PERFIL=ubuntu-26.04-amd64"
echo "VERSIONES_APT_EXACTAS=$EXACT"
echo "PAQUETES_BASE=${#BASE_PACKAGES[@]}"
echo "PAQUETES_EXTERNOS=${#EXTERNAL_PACKAGES[@]}"
echo "OPCIONALES_SELECCIONADOS=${#OPTIONAL_PACKAGES[@]}"

printf 'BASE: %s\n' "${BASE_PACKAGES[@]}"
printf 'EXTERNO: %s\n' "${EXTERNAL_PACKAGES[@]}"

if (( ${#OPTIONAL_PACKAGES[@]} > 0 )); then
    printf 'OPCIONAL: %s\n' "${OPTIONAL_PACKAGES[@]}"
fi

echo "ENTORNO_CIENTIFICO=$VENV"

echo "--- FUENTES APT EXTERNAS ---"
echo "https://cli.github.com/packages"
echo "https://download.docker.com/linux/ubuntu"
echo "https://packages.opentofu.org/opentofu/tofu/any/"
echo "https://deb.nodesource.com/node_24.x"

echo "--- IMAGENES OCI ---"
cat "$IMAGES"

echo "--- PROCEDIMIENTO ---"
echo "1. Comprobar anfitrión dedicado y conflictos."
echo "2. Instalar dependencias base."
echo "3. Incorporar fuentes APT oficiales firmadas."
echo "4. Instalar herramientas externas."
echo "5. Preparar entorno virtual científico."
echo "6. Descargar imágenes OCI por digest."
echo "7. Validar herramientas y versiones."
echo "8. Conservar la configuración de gestión."

if [[ "$MODE" == plan ]]; then
    echo "INSTALACION_EJECUTADA=NO"
    echo "PLAN_INSTALACION=OK"
    exit 0
fi

# A partir de este punto comienza el modo modificador.
# Nunca se ejecuta durante una comprobación --plan.

command -v sudo >/dev/null ||
    fail "Se requiere sudo."

sudo -v

# Rechazamos entornos que ya contienen componentes
# instalados de NETLAB360.

for path in \
    "$BOOT/s02" \
    "$BOOT/s05" \
    "$BOOT/s06" \
    "$BOOT/s07" \
    "$VENV" \
    /usr/local/libexec/netlab360 \
    /usr/local/libexec/netlab360-observer \
    /var/lib/netlab360
do
    if sudo test -e "$path"; then
        fail "Entorno existente detectado: $path"
    fi
done

if command -v ip >/dev/null; then
    namespaces="$(sudo ip netns list)"
    [[ -z "$namespaces" ]] ||
        fail "Existen namespaces previos."
fi

if command -v docker >/dev/null; then
    containers="$(sudo docker ps -aq)" ||
        fail "No se puede verificar Docker existente."

    [[ -z "$containers" ]] ||
        fail "Existen contenedores previos."
fi

for conflict in \
    docker.io \
    docker-compose \
    docker-compose-v2 \
    podman-docker \
    containerd \
    runc
do
    status="$(dpkg-query -W -f='${Status}' "$conflict" \
        2>/dev/null || true)"

    if [[ "$status" == "install ok installed" ]]; then
        fail "Paquete incompatible instalado: $conflict"
    fi
done

# No sobrescribimos configuraciones previas de repositorios.
# Una VM con fuentes externas existentes requiere revisión.

if sudo grep -rEq \
    'cli\.github\.com/packages|download\.docker\.com/linux/ubuntu|packages\.opentofu\.org|deb\.nodesource\.com' \
    /etc/apt/sources.list /etc/apt/sources.list.d \
    2>/dev/null
then
    fail "Existen fuentes externas; revisar antes de continuar."
fi

for key in \
    githubcli-archive-keyring.gpg \
    docker.asc \
    opentofu.gpg \
    opentofu-repo.gpg \
    nodesource.gpg
do
    if sudo test -e "/etc/apt/keyrings/$key"; then
        fail "Llave APT preexistente: $key"
    fi
done

for source in \
    netlab360-github-cli.list \
    netlab360-docker.list \
    netlab360-opentofu.list \
    netlab360-nodesource.list
do
    if sudo test -e "/etc/apt/sources.list.d/$source"; then
        fail "Fuente APT preexistente: $source"
    fi
done

echo "ANFITRION_DEDICADO=PRECHECK_OK"

# APT debe resolver todas las dependencias sin eliminar
# paquetes existentes. No efectuamos upgrade general.

install_apt() {
    (( $# > 0 )) || return 0

    sudo apt-get -s --no-remove install "$@"

    sudo env DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-remove "$@"
}

sudo apt-get update

# Herramientas necesarias para incorporar repositorios.
install_apt ca-certificates curl gnupg

TMP="$(mktemp -d)"

trap 'rm -rf -- "$TMP"' EXIT

mkdir -m 700 "$TMP/gnupg"

export GNUPGHOME="$TMP/gnupg"

# Las llaves se obtienen de los sitios oficiales.
# No desactivamos la validación TLS ni las firmas APT.

download() {
    curl --fail --silent --show-error --location \
        --proto '=https' \
        --proto-redir '=https' \
        --connect-timeout 15 \
        --max-time 120 \
        "$1" -o "$2"

    [[ -s "$2" ]] ||
        fail "Descarga vacía."
}

download \
    https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    "$TMP/githubcli-archive-keyring.gpg"

download \
    https://download.docker.com/linux/ubuntu/gpg \
    "$TMP/docker.asc"

download \
    https://get.opentofu.org/opentofu.gpg \
    "$TMP/opentofu.gpg"

download \
    https://packages.opentofu.org/opentofu/tofu/gpgkey \
    "$TMP/opentofu-repo.asc"

download \
    https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
    "$TMP/nodesource.asc"

gpg --batch --dearmor \
    -o "$TMP/opentofu-repo.gpg" \
    "$TMP/opentofu-repo.asc"

gpg --batch --dearmor \
    -o "$TMP/nodesource.gpg" \
    "$TMP/nodesource.asc"

echo "--- LLAVES DE FIRMA ---"

for key in \
    githubcli-archive-keyring.gpg \
    docker.asc \
    opentofu.gpg \
    opentofu-repo.gpg \
    nodesource.gpg
do
    echo "LLAVE=$key"

    gpg --batch --show-keys --fingerprint "$TMP/$key"
done

# La confianza inicial se confirma de forma explícita.
# El administrador debe contrastar las huellas con las
# publicaciones oficiales antes de continuar.

echo "Verifique las huellas de las llaves oficiales."
echo "Escriba CONFIAR para autorizar estas fuentes."

read -r answer

[[ "$answer" == CONFIAR ]] ||
    fail "Fuentes externas no autorizadas."

sudo install -d -m 0755 /etc/apt/keyrings

for key in \
    githubcli-archive-keyring.gpg \
    docker.asc \
    opentofu.gpg \
    opentofu-repo.gpg \
    nodesource.gpg
do
    sudo install -o root -g root -m 0644 \
        "$TMP/$key" "/etc/apt/keyrings/$key"
done

# Las llaves quedan restringidas a sus repositorios.
cat > "$TMP/netlab360-github-cli.list" <<'EOF'
deb [arch=amd64 signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main
EOF

cat > "$TMP/netlab360-docker.list" <<'EOF'
deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu resolute stable
EOF

cat > "$TMP/netlab360-opentofu.list" <<'EOF'
deb [signed-by=/etc/apt/keyrings/opentofu.gpg,/etc/apt/keyrings/opentofu-repo.gpg] https://packages.opentofu.org/opentofu/tofu/any/ any main
EOF

cat > "$TMP/netlab360-nodesource.list" <<'EOF'
deb [arch=amd64 signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_24.x nodistro main
EOF

for source in \
    netlab360-github-cli.list \
    netlab360-docker.list \
    netlab360-opentofu.list \
    netlab360-nodesource.list
do
    sudo install -o root -g root -m 0644 \
        "$TMP/$source" "/etc/apt/sources.list.d/$source"
done

sudo apt-get update

install_apt \
    "${BASE_PACKAGES[@]}" \
    "${EXTERNAL_PACKAGES[@]}" \
    "${OPTIONAL_PACKAGES[@]}"

echo "PAQUETES_INSTALADOS=OK"

# Docker Engine es una dependencia del laboratorio.
# No incorporamos al usuario al grupo docker.

sudo systemctl start docker.service

sudo docker version
sudo docker compose version
sudo docker buildx version

[[ "$(node --version)" == v24.* ]] ||
    fail "Node.js no corresponde a la rama 24."

tofu version
ansible --version

# Instalamos las distribuciones científicas en un
# entorno virtual nuevo, nunca en Python del sistema.

python3 -c '
import sys
assert sys.version_info[:2] == (3, 14)
'

[[ ! -e "$VENV" ]] ||
    fail "El entorno científico ya existe."

mkdir -p "$(dirname "$VENV")"

python3 -m venv "$VENV"

PIP_CONFIG_FILE=/dev/null \
    "$VENV/bin/python" -m pip --isolated install \
    --index-url https://pypi.org/simple \
    --only-binary=:all: \
    -r "$REQUIREMENTS"

"$VENV/bin/python" -m pip check

# Verificamos las versiones declaradas sin importar
# ni ejecutar código científico del laboratorio.

"$VENV/bin/python" - "$REQUIREMENTS" <<'PY'
from importlib import metadata
from pathlib import Path
import sys

for line in Path(sys.argv[1]).read_text().splitlines():
    line = line.strip()

    if not line or line.startswith("#"):
        continue

    name, version = line.split("==", 1)

    assert metadata.version(name) == version, name

print("DEPENDENCIAS_CIENTIFICAS=VERIFICADAS")
PY

# Descargamos imágenes por identidad inmutable.
# Las etiquetas existentes de los ejecutores históricos
# se conservan únicamente si apuntan a la misma imagen.

while IFS=$'\t' read -r component tag digest architecture; do
    [[ "$component" == componente ]] && continue

    [[ "$architecture" == amd64 ]] ||
        fail "Arquitectura OCI no autorizada."

    case "$component" in
        frr|faucet|prometheus) ;;
        *) fail "Componente OCI desconocido." ;;
    esac

    [[ "$digest" =~ ^[a-z0-9./_-]+@sha256:[0-9a-f]{64}$ ]] ||
        fail "Referencia OCI inválida."

    sudo docker pull --platform linux/amd64 "$digest"

    [[ "$(sudo docker image inspect "$digest" \
        --format '{{.Architecture}}')" == amd64 ]] ||
        fail "Arquitectura OCI incompatible."

    sudo docker image inspect "$digest" \
        --format '{{range .RepoDigests}}{{println .}}{{end}}' |
        grep -Fx "$digest"

    if sudo docker image inspect "$tag" >/dev/null 2>&1; then
        before="$(sudo docker image inspect "$tag" \
            --format '{{.Id}}')"

        expected="$(sudo docker image inspect "$digest" \
            --format '{{.Id}}')"

        [[ "$before" == "$expected" ]] ||
            fail "Etiqueta OCI en conflicto: $tag"
    else
        sudo docker tag "$digest" "$tag"
    fi

    echo "IMAGEN_VERIFICADA=$component"

done < "$IMAGES"

bash "$DIR/verificar.sh"

echo "INSTALACION_DEPENDENCIAS=OK"
echo "RECONSTRUCCION_INTEGRAL=PENDIENTE"
echo "TOPOLOGIA_DESPLEGADA=NO"
