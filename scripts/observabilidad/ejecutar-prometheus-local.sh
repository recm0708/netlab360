#!/usr/bin/env bash
# NETLAB360 | Observabilidad: ejecutar prometheus local
# Alcance: recursos propios del módulo, sin alterar la red administrativa.

# NETLAB360 — Prometheus como usuario normal y exclusivamente localhost.
set -Eeuo pipefail
REPO="$HOME/proyectos/netlab360"
BASE="$HOME/netlab360-bootstrap/prometheus"
BIN="$BASE/bin"
[[ "$(hostname)" == netlab360-lab ]] || { echo "ERROR: hostname inesperado"; exit 3; }
[[ "$(id -u)" != 0 ]] || { echo "ERROR: usuario root no permitido"; exit 3; }
cd "$REPO"
ip -4 -br address show ens33 | grep -Fq '192.168.47.40/24' ||
  { echo "ERROR: ens33 IP cambiada"; exit 3; }
ip -4 route show default | grep -Fq 'default via 192.168.47.2 dev ens33' ||
  { echo "ERROR: default gateway cambiado"; exit 3; }
[[ -x "$BIN/prometheus" && -x "$BIN/promtool" ]] ||
  { echo "ERROR: ejecutar antes preparar-prometheus-local.sh"; exit 3; }
if ss -H -ltn '( sport = :9090 )' | grep -q .; then
  echo "ERROR: puerto 9090 ocupado; no duplicar servidor"; exit 3
fi
# Renderizar la ruta de las reglas como ABSOLUTA en configuracion runtime.
# Evita reglas no cargadas si Prometheus interpreta glob desde otro directorio.
# El template Git sigue siendo portable y no se modifica.
mkdir -p "$BASE/data"
RUNTIME_CONFIG="$BASE/prometheus-runtime.yml"
python3 - "$REPO" "$RUNTIME_CONFIG" <<'PY'
import sys
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
dst = Path(sys.argv[2])
template = repo / "servicios/observabilidad/prometheus/prometheus.yml"
rulefile = repo / "servicios/observabilidad/prometheus/rules/wan-alerts.yml"
if not rulefile.is_file():
    raise SystemExit("ERROR: reglas WAN no encontradas")
text = template.read_text(encoding="utf-8")
needle = "servicios/observabilidad/prometheus/rules/*.yml"
if text.count(needle) != 1:
    raise SystemExit("ERROR: glob de reglas inesperado en template")
glob = str(rulefile.parent / "*.yml")
text = text.replace(needle, glob)
dst.write_text(text, encoding="utf-8")
print("PROMETHEUS_RULES_ABSOLUTE=" + glob)
print("PROMETHEUS_RUNTIME_CONFIG=" + str(dst))
PY
"$BIN/promtool" check config "$RUNTIME_CONFIG"
"$BIN/promtool" check rules "$REPO/servicios/observabilidad/prometheus/rules/wan-alerts.yml"
# Validacion independiente: no permitir inicio si falta cualquiera de las alertas.
grep -Fq 'NETLAB360WANPrimaryDown' "$REPO/servicios/observabilidad/prometheus/rules/wan-alerts.yml"
grep -Fq 'NETLAB360ExporterUnavailable' "$REPO/servicios/observabilidad/prometheus/rules/wan-alerts.yml"
grep -Fq 'NETLAB360WanBackupSelected' "$REPO/servicios/observabilidad/prometheus/rules/wan-alerts.yml"
echo "PROMETHEUS_RULES_SOURCE: 3 previstas"
echo "PROMETHEUS_LOCAL_URL=http://127.0.0.1:9090/"
echo "PROMETHEUS_SCRAPE_TARGET=127.0.0.1:9108"
echo "PROMETHEUS_MODO=TSDB_LOCAL_REAL | CTRL_C_DETIENE"
exec "$BIN/prometheus" \
  --config.file="$RUNTIME_CONFIG" \
  --storage.tsdb.path="$BASE/data" \
  --storage.tsdb.retention.time=1d \
  --web.listen-address=127.0.0.1:9090 \
  --log.level=info
