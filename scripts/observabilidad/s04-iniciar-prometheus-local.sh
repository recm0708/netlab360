#!/usr/bin/env bash
# NETLAB360 S04: Prometheus independiente, solo localhost 9091, sin alterar B3.
set -Eeuo pipefail

REPO="$HOME/proyectos/netlab360"
BASE="$HOME/netlab360-bootstrap/prometheus/s04"
BIN="$HOME/netlab360-bootstrap/prometheus/bin"
TEMPLATE="$REPO/servicios/observabilidad/prometheus/s04-prometheus.yml"
RULES="$REPO/servicios/observabilidad/prometheus/rules/s04-alerts.yml"
RUNTIME="$BASE/prometheus-runtime.yml"

[[ "$(hostname)" == "netlab360-lab" ]] || { echo "S04_ERROR=HOSTNAME"; exit 3; }
[[ "$(id -u)" != 0 ]] || { echo "S04_ERROR=NO_USAR_ROOT"; exit 3; }
cd "$REPO"
ip -4 -br address show ens33 | grep -Fq '192.168.47.40/24' ||
  { echo "S04_ERROR=ADMIN_IP"; exit 3; }
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' ||
  { echo "S04_ERROR=ADMIN_GW"; exit 3; }

[[ -x "$BIN/prometheus" && -x "$BIN/promtool" ]] ||
  { echo "S04_ERROR=BINARIOS_PROMETHEUS"; exit 3; }
[[ -f "$TEMPLATE" && -f "$RULES" ]] || { echo "S04_ERROR=CONFIGURACION"; exit 3; }
if ss -H -ltn '( sport = :9091 )' | grep -q .; then
  echo "S04_ERROR=PUERTO_9091_OCUPADO"
  exit 3
fi
if ss -H -ltn '( sport = :9110 )' | grep -qv '127.0.0.1:9110'; then
  echo "S04_ERROR=COLECTOR_EXPUESTO_FUERA_LOOPBACK"
  exit 3
fi

echo "========== S04 VALIDAR COLECTOR =========="
python3 - <<'PY'
import json
from urllib.request import urlopen
with urlopen("http://127.0.0.1:9110/healthz", timeout=3) as r:
    item = json.load(r)
if item.get("service") != "s04-exporter" or item.get("source_ok") is not True:
    raise SystemExit("S04_ERROR=FUENTE_NO_CONFIABLE")
print("S04_COLECTOR=RESPONDE_FUENTE_OK")
print("S04_TOPOLOGIA=" + item["topology"])
PY

mkdir -p "$BASE/data"
python3 - "$TEMPLATE" "$RULES" "$RUNTIME" <<'PY'
from pathlib import Path
import sys
template, rule, output = (Path(v) for v in sys.argv[1:])
source = template.read_text(encoding="utf-8")
target = "servicios/observabilidad/prometheus/rules/s04-alerts.yml"
if source.count(target) != 1 or rule.is_symlink() or output.is_symlink():
    raise SystemExit("S04_ERROR=PLANTILLA_REGLAS_O_SYMLINK")
output.write_text(source.replace(target, str(rule.resolve())), encoding="utf-8")
print("S04_CONFIG_RUNTIME=" + str(output))
print("S04_REGLAS_RUNTIME=" + str(rule.resolve()))
PY

echo "========== S04 VALIDACION PROMETHEUS =========="
"$BIN/promtool" check config "$RUNTIME"
"$BIN/promtool" check rules "$RULES"
"$BIN/promtool" test rules "$REPO/servicios/observabilidad/prometheus/tests/s04-alertas.test.yml"

echo "S04_PROMETHEUS_LOCAL=http://127.0.0.1:9091"
echo "S04_PROMETHEUS_SCRAPE=127.0.0.1:9110"
echo "S04_INSTANCIA_B3_INTACTA=SI"
echo "S04_CTRL_C_DETIENE_PROCESO=SI"

exec "$BIN/prometheus" \
  --config.file="$RUNTIME" \
  --storage.tsdb.path="$BASE/data" \
  --storage.tsdb.retention.time=1d \
  --web.listen-address=127.0.0.1:9091 \
  --log.level=info
