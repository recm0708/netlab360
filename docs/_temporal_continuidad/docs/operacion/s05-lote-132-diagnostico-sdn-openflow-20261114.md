# S05 · Lote 129 parcial, diagnóstico OpenFlow sin repetir despliegue

Corte 14/11/2026. Lote 128: 16/16 pruebas OK. Lote 129: UP creó state-sdn.json, contenedor nl360-s05-faucet, puente OVS br-s05-sdn, namespaces y puertos A/B/C, pero no confirmó conexión Faucet/OVS a tcp:127.0.0.1:16653 en 15 observaciones. El script registra needs_inspection y NO autoriza repetir UP. SSH se desconectó después; un segundo UP rechazado por el estado preexistente. No se ejecutaron lotes 130–131. La causa de la desconexión del controlador no está demostrada.

Hasta inspeccionar: NO repetir up, no ejecutar down, docker rm/restart, ovs del-br, apt ni reboot. Los diagnósticos siguientes son exclusivamente consultas. El puerto oficial Faucet interno es TCP 6653; Docker debe publicar 127.0.0.1:16653→6653. Comprobar is_connected, status/last_error de la tabla Controller en OVS, estado del contenedor, Docker port y logs antes de decidir el arreglo. Los marcadores CONSULTAS_COMPLETADAS no afirman que el sistema esté sano.

## Lote 132A — estado, contenedor y conexión TCP (pasos 691–698)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
mkdir -p "$DIR"
sudo -v
{
echo "========== 691 VERSION Y GESTION =========="
git status --short --branch
git log -1 --oneline
ip -4 -br address show ens33
ip -4 route show default
echo "========== 692 ESTADO SDN =========="
python3 - <<'PY'
import json
from pathlib import Path
p=Path.home()/"netlab360-bootstrap/s05/sdn-faucet/state-sdn.json"
print("STATE_EXISTS=",p.is_file(),"IS_SYMLINK=",p.is_symlink())
if p.is_file() and not p.is_symlink():
 d=json.loads(p.read_text())
 for k in ("owner","bridge","status","error","image"):
  print(f"STATE_{k.upper()}={d.get(k)}")
 print("BASELINE_NAMESPACES=",len(d.get("before",{}).get("namespaces",[])))
 print("BASELINE_CONTAINERS=",len(d.get("before",{}).get("docker",[])))
PY
echo "========== 693 INSPECTOR SDN =========="
if python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py inspect; then
 echo "INSPECTOR=CONSULTADO"
else
 echo "INSPECTOR=ERROR_VER_SALIDA"
fi
echo "========== 694 ESTADO DOCKER FAUCET =========="
sudo -n docker ps -a --filter 'name=nl360-s05-faucet' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
if sudo -n docker inspect nl360-s05-faucet --format 'STATUS={{.State.Status}} RUNNING={{.State.Running}} EXIT={{.State.ExitCode}} RESTARTS={{.RestartCount}}'; then
 echo "DOCKER_INSPECT=OK"
else
 echo "DOCKER_INSPECT=NO_DISPONIBLE"
fi
echo "========== 695 PUERTOS PUBLICADOS =========="
sudo -n docker port nl360-s05-faucet || true
echo "========== 696 PUERTOS ESCUCHANDO =========="
sudo -n ss -ltnp | grep -E '(:16653|:6653)([[:space:]]|$)' || true
echo "========== 697 TCP LOCAL =========="
if timeout -k 1s 4s bash -c ': > /dev/tcp/127.0.0.1/16653' 2>/dev/null; then
 echo "TCP_16653_LOOPBACK=CONECTA"
else
 echo "TCP_16653_LOOPBACK=NO_CONECTA"
fi
echo "========== 698 OVS CONTROLLER =========="
sudo -n ovs-vsctl --timeout=12 --format=table --columns=target,is_connected,status list Controller
sudo -n ovs-vsctl --timeout=12 show
echo "========== LOTE132A_CONSULTAS=COMPLETADAS =========="
} 2>&1 | tee "$DIR/06_Diagnostico_OpenFlow_Estado_y_TCP.txt"
BASH
~~~

## Lote 132B — logs, recursos exclusivos y regresión (pasos 699–705)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
BASE="$HOME/netlab360-bootstrap/s05/sdn-faucet"
sudo -v
{
echo "========== 699 DOCKER LOGS =========="
if sudo -n docker logs --timestamps --tail 90 nl360-s05-faucet; then
 echo "DOCKER_LOGS=CONSULTADOS"
else
 echo "DOCKER_LOGS=NO_DISPONIBLES"
fi
echo "========== 700 ARCHIVOS FAUCET =========="
find "$BASE/logs" -maxdepth 2 -type f -printf '%P: %s bytes\n' | sort
for file in "$BASE/logs/faucet.log" "$BASE/logs/faucet_exception.log"; do
 if [[ -f "$file" ]]; then
  echo "========== $(basename "$file") =========="
  tail -n 50 "$file"
 fi
done
echo "========== 701 OVS BRIDGE Y PORTS =========="
if sudo -n ovs-vsctl --timeout=12 br-exists br-s05-sdn; then
 sudo -n ovs-vsctl --timeout=12 list-ports br-s05-sdn
 for port in sdna0 sdnb0 sdnc0; do
  echo "OFPORT_$port=$(sudo -n ovs-vsctl --timeout=12 get Interface "$port" ofport 2>/dev/null || echo ERROR)"
 done
else
 echo "BRIDGE_SDN=NO_EXISTE"
fi
echo "========== 702 NAMESPACES SDN =========="
for site in a b c; do
 ns="nl360-s05-sdn-$site"
 if sudo -n ip netns list | awk '{print $1}' | grep -Fxq "$ns"; then
  echo "NAMESPACE_$site=EXISTE"
  sudo -n ip -n "$ns" -4 -br address
 else
  echo "NAMESPACE_$site=NO_EXISTE"
 fi
done
echo "========== 703 CONTENEDORES Y GESTION =========="
sudo -n docker ps --format 'table {{.Names}}\t{{.Status}}'
ip -4 -br address show ens33
ip -4 route show default
echo "========== 704 SERVICIOS S04 S05 =========="
for unit in netlab360-s04-exporter netlab360-s05-noc \
 netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 \
 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
 printf '%s=%s\n' "$unit" "$(systemctl is-active "$unit" || true)"
done
echo "========== 705 GIT =========="
git status --short --branch
echo "========== LOTE132B_CONSULTAS=COMPLETADAS =========="
} 2>&1 | tee "$DIR/07_Diagnostico_Logs_Puertos_y_S02.txt"
BASH
~~~

Tras ambos lotes, analizar error real y planear recuperación selectiva con ownership; no declarar OpenFlow conectado ni capturas 58–60 hasta demostrarlo. No reiniciar VM/Windows, mantener HA/LACP/FRR intactos.
