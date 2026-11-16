#!/usr/bin/env bash
# NETLAB360 | Validación: auditar dependencias netlab360
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# NETLAB360: auditoria de dependencias de B0/B1/B2/B3 y fases futuras.
# Solo lectura: NO instala paquetes, NO cambia rutas, NO arranca contenedores.
set -uo pipefail
FAIL=0
WARN=0
echo "========== AUDITORIA DE DEPENDENCIAS NETLAB360 =========="
date -Is
hostname
printf 'USUARIO=%s\n' "$(id -un)"
required() {
  local label="$1" binary="$2"
  if command -v "$binary" >/dev/null 2>&1; then
    printf 'REQUERIDO_OK: %-18s %s\n' "$label" "$(command -v "$binary")"
  else
    printf 'REQUERIDO_FALTA: %-18s comando=%s\n' "$label" "$binary"
    FAIL=$((FAIL+1))
  fi
}
planned() {
  local label="$1" binary="$2"
  if command -v "$binary" >/dev/null 2>&1; then
    printf 'PLANIFICADO_DISPONIBLE: %-18s %s\n' "$label" "$(command -v "$binary")"
  else
    printf 'PLANIFICADO_NO_INSTALADO: %-18s %s\n' "$label" "$binary"
    WARN=$((WARN+1))
  fi
}
echo "========== REQUERIDOS YA PARA B1/B2/B3 =========="
for c in bash git python3 sudo docker ip nsenter curl ss grep awk sed sha256sum; do
  required "$c" "$c"
done
echo "========== MODULOS PYTHON YA NECESARIOS =========="
if python3 -c 'import ast, csv, hashlib, http.server, json, subprocess, yaml' >/dev/null 2>&1; then
  echo "PYTHON_MODULOS_BASE: OK (incluye PyYAML de IPAM)"
else
  echo "PYTHON_MODULOS_BASE: FALTA o error de importacion (revisar PyYAML)"
  FAIL=$((FAIL+1))
fi
echo "========== CONTENEDORES Y SERVICIOS =========="
if command -v docker >/dev/null 2>&1; then
  docker --version || true
  if sudo -n docker info --format 'DOCKER_ENGINE: {{.ServerVersion}}' 2>/dev/null; then
    if sudo -n docker image inspect 'quay.io/frrouting/frr:10.7.1' --format 'FRR_IMAGE_LOCAL: {{.Id}}' 2>/dev/null; then
      :
    else
      echo "FRR_IMAGE_LOCAL: NO VERIFICADA (imagen ausente o permisos)"
      WARN=$((WARN+1))
    fi
  else
    echo "DOCKER_ENGINE: NO VERIFICABLE sin sudo valido o daemon disponible"
    WARN=$((WARN+1))
  fi
  if docker compose version >/dev/null 2>&1; then
    docker compose version
  else
    echo "DOCKER_COMPOSE: NO DISPONIBLE (necesario para fases de stack)"
    WARN=$((WARN+1))
  fi
fi
for service in docker ssh open-vm-tools; do
  printf 'SERVICIO_%s: ' "$service"
  systemctl is-active "$service" || true
done
echo "========== RED DE GESTION SOLO LECTURA =========="
ip -4 -br address show ens33
ip -4 route show default
if ip -4 -br address show ens33 | grep -Fq '192.168.47.40/24' &&
   ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33'; then
  echo "RED_ADMIN_PROTEGIDA: SI"
else
  echo "RED_ADMIN_PROTEGIDA: NO / revisar antes de cualquier despliegue"
  FAIL=$((FAIL+1))
fi
echo "========== HERRAMIENTAS DE FASES POSTERIORES =========="
planned "OpenTofu-IaC" tofu
planned "Ansible-IaC" ansible
planned "GitHub-CLI" gh
planned "NodeJS" node
planned "NPM" npm
echo "PROMETHEUS/ALERTMANAGER: NO EXIGIDOS EN ESTE PREFLIGHT"
echo "NOTA: sus imagenes/configuracion deben versionarse y validarse en B3;"
echo "      no instalar todos los programas futuros a nivel del host."
echo "========== RESULTADO =========="
echo "DEPENDENCIAS_REQUERIDAS_FALTANTES=$FAIL"
echo "DEPENDENCIAS_PLANIFICADAS_POR_VERIFICAR=$WARN"
if (( FAIL > 0 )); then
  echo "RESULTADO_AUDITORIA_DEPENDENCIAS=1"
  exit 1
fi
echo "RESULTADO_AUDITORIA_DEPENDENCIAS=0"
