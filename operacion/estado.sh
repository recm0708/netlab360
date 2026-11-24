#!/usr/bin/env bash
# Consultamos la infraestructura activa sin reconstruirla.
# No se inicia, detiene ni modifica ningún servicio de red.
set -Eeuo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

cd "$DIR/.."

if [[ "$#" -ne 0 ]]; then
    echo "Uso: bash operacion/estado.sh" >&2
    exit 2
fi

if [[ "$(id -u)" -eq 0 ]]; then
    echo "Ejecutar como operador, no como root." >&2
    exit 3
fi

export LC_ALL=C.UTF-8
export PYTHONDONTWRITEBYTECODE=1

sudo -n true

echo "========== NETLAB360 ESTADO OPERACIONAL =========="

echo "========== ADMINISTRACION =========="

python3 -B - <<'PY'
import json
import subprocess

def command(*args):
    return json.loads(
        subprocess.check_output(args, text=True, timeout=10)
    )

addresses = command(
    "ip", "-j", "-4", "addr", "show", "dev", "ens33"
)

routes = command(
    "ip", "-j", "-4", "route", "show", "default"
)

assert len(addresses) == 1

assert any(
    item["local"] == "192.168.47.40"
    and item["prefixlen"] == 24
    for item in addresses[0]["addr_info"]
)

assert len(routes) == 1
assert routes[0]["gateway"] == "192.168.47.2"
assert routes[0]["dev"] == "ens33"

print("ADMINISTRACION=OK")
PY

echo "========== CONTENEDORES Y NAMESPACES =========="

python3 -B - <<'PY'
import subprocess
import sys

sys.path.insert(0, "operacion")

from ciclo_vida import CONTAINERS

def cmd(*args):
    return subprocess.check_output(
        args, text=True, timeout=15
    ).splitlines()

active = set(cmd(
    "sudo", "-n", "docker", "ps",
    "--format", "{{.Names}}"
))

assert active == set(CONTAINERS), sorted(active)

namespaces = {
    line.split()[0]
    for line in cmd("sudo", "-n", "ip", "netns", "list")
    if line.strip()
}

expected = {
    f"nl360-s02-sw-{site}"
    for site in ("hq", "s1", "s2")
}

expected.update(
    f"nl360-s02-h-{site}-{vid}"
    for site, vlans in (
        ("hq", (110, 120, 130)),
        ("s1", (210, 220, 230)),
        ("s2", (310, 320, 330)),
    )
    for vid in vlans
)

expected.update({
    "nl360-s05-ha-hq",
    "nl360-s05-ha-s1",
    "nl360-s05-ha-fe",
})

expected.update(
    f"nl360-s05-lacp-{site}"
    for site in ("hq", "s1", "s2")
)

expected.update(
    f"nl360-s05-sdn-{site}"
    for site in ("a", "b", "c")
)

assert namespaces == expected, {
    "faltantes": sorted(expected - namespaces),
    "adicionales": sorted(namespaces - expected),
}

print("CONTENEDORES_ACTIVOS=4/4")
print("NAMESPACES_VERIFICADOS=21/21")
PY

echo "========== SERVICIOS =========="

python3 -B - <<'PY'
import subprocess
import sys

sys.path.insert(0, "operacion")

from ciclo_vida import UNITS

for name in UNITS:
    subprocess.run(
        ["systemctl", "is-active", "--quiet", name],
        check=True,
        timeout=10,
    )
    print(f"SERVICIO_ACTIVO={name}")

print("SERVICIOS_ACTIVOS=7/7")
PY

echo "========== OSPF E IDENTIDAD =========="

sudo -n /usr/bin/python3 -I \
    /usr/local/libexec/netlab360/s07-preflight.py check |
python3 -c '
import json, sys
r = json.load(sys.stdin)
assert r["ok"] is True
assert r["identity_verified"] is True
assert r["configuration_status"] == "MET"
assert r["execution_authorized"] is False
assert r["network_mutations_authorized"] is False
print("IDENTIDAD_ROUTERS=VERIFICADA")
print("PREFLIGHT=MET")
print("AUTORIZACION_MUTACIONES=NO")
'

echo "========== OBSERVABILIDAD =========="

curl -fsS --max-time 10 \
    http://127.0.0.1:9091/-/ready

echo

curl -fsS --max-time 10 \
    http://127.0.0.1:9130/healthz |
python3 -c '
import json, sys
r = json.load(sys.stdin)
assert r["healthy"] is True
assert r["service"] == "netlab360-s05-topologia"
print("NOC_S05=SALUDABLE")
'

curl -fsS --max-time 10 \
    http://127.0.0.1:9091/api/v1/targets |
python3 -c '
import json, sys
r = json.load(sys.stdin)
assert r["status"] == "success"
targets = r["data"]["activeTargets"]
found = [
    t for t in targets
    if t.get("labels", {}).get("job")
    == "netlab360-s04-multisede"
]
assert len(found) == 1
assert found[0]["health"] == "up"
print("PROMETHEUS_TARGET_S04=UP")
'

echo "MUTACIONES_RED=NO"
echo "SERVICIOS_MODIFICADOS=NO"
echo "ESTADO_OPERACIONAL=OK"
