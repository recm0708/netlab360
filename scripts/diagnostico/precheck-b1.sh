#!/usr/bin/env bash
# NETLAB360 B1: inventario de host/red (solo lectura; NO cambia red/VM).
set -Eeuo pipefail
if [[ $(hostname) != netlab360-lab ]]; then
  echo "ERROR: se esperaba netlab360-lab" >&2
  exit 1
fi
if [[ ! -d "$HOME/proyectos/netlab360/.git" ]]; then
  echo "ERROR: falta repositorio ~/proyectos/netlab360" >&2
  exit 1
fi
R="$HOME/netlab360-bootstrap/evidencias"
mkdir -p "$R"
FILE="$R/03-b1-preflight-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$FILE") 2>&1

echo "========== NETLAB360 B1 PRECHECK (SOLO LECTURA) =========="
date -Is
hostname
echo "========== RED ADMIN =========="
ip -4 -br addr show ens33
ip -4 route show default
echo "========== TODAS LAS RUTAS IPv4 (TABLA MAIN) =========="
ip -4 route show table main
echo "========== REDES DOCKER =========="
sudo -v
sudo docker network ls --format '{{.Name}}' | while IFS= read -r net; do
  subnet=$(sudo docker network inspect "$net" --format '{{range .IPAM.Config}}{{.Subnet}} {{end}}')
  echo "$net : $subnet"
done
echo "========== SERVICIOS =========="
systemctl is-active docker ssh open-vm-tools
systemctl --failed --no-pager
echo "========== RECURSOS =========="
nproc
free -h
df -h /
echo "========== CONTENEDORES =========="
sudo docker ps -a --format 'table {{.Names}}\t{{.Status}}'
echo "========== PYTHON Y PYYAML =========="
python3 -c 'import yaml; print("PyYAML:", yaml.__version__)'
echo "========== ESTADO GIT =========="
cd "$HOME/proyectos/netlab360"
git status --short --branch
echo "========== VALIDAR IPAM PRELIMINAR =========="
python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml
echo "========== COMPROBAR COLISIONES DE SUBREDES (HOST + DOCKER) =========="
python3 - <<'PY'
import ipaddress
import json
import subprocess
import yaml

with open("inventario/ipam/topologia-b1.yaml", encoding="utf-8") as f:
    spec = yaml.safe_load(f)
proposed = []
for site, data in spec["sites"].items():
    proposed.extend((f"{site}-VLAN{v['id']}", ipaddress.ip_network(v["subnet"])) for v in data["vlans"])
    proposed.append((f"{site}-loopback", ipaddress.ip_network(data["loopback"])))
for link in spec["wan_links"]:
    proposed.append((link["id"], ipaddress.ip_network(link["subnet"])))

existing = []
for entry in json.loads(subprocess.check_output(["ip", "-j", "-4", "route", "show", "table", "main"], text=True)):
    dst = entry.get("dst")
    if dst and dst != "default":
        existing.append(("host:"+entry.get("dev", "?"), ipaddress.ip_network(dst, strict=False)))
names = subprocess.check_output(
    ["sudo", "docker", "network", "ls", "--format", "{{.Name}}"], text=True
).splitlines()
for name in names:
    data = json.loads(subprocess.check_output(["sudo", "docker", "network", "inspect", name], text=True))
    for item in data:
        for subnet in item.get("IPAM", {}).get("Config", []) or []:
            if subnet.get("Subnet"):
                existing.append((f"docker:{name}", ipaddress.ip_network(subnet["Subnet"], strict=False)))

conflicts = [
    (pname, str(pnet), ename, str(enet))
    for pname, pnet in proposed
    for ename, enet in existing
    if pnet.overlaps(enet)
]
if conflicts:
    for row in conflicts:
        print("CONFLICTO:", *row)
    raise SystemExit(3)
print(f"SIN CONFLICTOS DETECTADOS: {len(proposed)} redes propuestas contra {len(existing)} rutas/subredes actuales.")
print("Advertencia: no detecta rutas de VPN o sistemas apagados que no estén presentes.")
PY

echo "========== REVISIÓN TERMINADA =========="
echo "NO SE MODIFICARON REDES NI CONTENEDORES."
echo "EVIDENCIA_LOCAL: $FILE"
