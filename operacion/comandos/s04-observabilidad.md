# Observabilidad

## Descripción

Consultamos la telemetría multisede mediante el exporter
local, Prometheus y sus reglas de alerta.

## Consulta operacional

```bash
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9110/healthz
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9091/-/ready
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9091/api/v1/targets
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9091/api/v1/rules
```

## Indicadores de observabilidad

```bash
python3 scripts/observabilidad/s04_sli_slo_observabilidad.py --minutes 15
```

La interpretación del indicador requiere suficiente
cobertura de muestras y fuentes disponibles.

## Validación de reglas y regresión

```bash
"$HOME/netlab360-bootstrap/prometheus/bin/promtool" check config "$HOME/netlab360-bootstrap/prometheus/s04/prometheus-runtime.yml"
"$HOME/netlab360-bootstrap/prometheus/bin/promtool" test rules servicios/observabilidad/prometheus/tests/s04-alertas.test.yml
python3 -m unittest discover -s tests -p 'test_s04_*.py' -v
```

## Instalación y ensayos

- [Exporter multisede](../../servicios/observabilidad/s04_exporter_multisede.py).
- [Configuración Prometheus](../../servicios/observabilidad/prometheus/s04-prometheus.yml).
- [Reglas de alerta](../../servicios/observabilidad/prometheus/rules/s04-alerts.yml).
- [Ensayo de incidente WAN](../../scripts/observabilidad/s04_incidente_wan.py).
- [Verificación de persistencia TSDB](../../scripts/observabilidad/s04_verificar_persistencia_tsdb.py).

La preparación del runtime y la instalación de servicios
se realizan mediante los instaladores centrales. Los ensayos
de incidente y persistencia requieren revisión previa,
puesto que pueden intervenir recursos activos.

## Documentación relacionada

- [Observabilidad](../../servicios/observabilidad/README.md).
- [Validación de indicadores](../../docs/validacion/s01-s04-resultados.md).
- [Instalación y operación](../README.md).
