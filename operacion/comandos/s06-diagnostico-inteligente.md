# Diagnóstico inteligente — Fase 06

## Descripción

Separamos la adquisición de telemetría, el etiquetado,
el entrenamiento, la evaluación y la inferencia.

Los resultados históricos requieren sus datos originales.
Una instalación nueva debe generar sus propias sesiones
y no atribuirse las métricas de otro experimento.

## Entorno científico

```bash
PY="$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python"
"$PY" --version
"$PY" -m pip check
"$PY" -m unittest discover -s tests -p 'test_s06_*.py' -v
```

## Comprobaciones y adquisición observacional

```bash
sudo -v
python3 scripts/s06/capturar_baseline.py --check-only
python3 scripts/s06/precheck_escenarios.py --save-plan
```

Para adquirir una línea base nueva, después de validar
la infraestructura y sin un experimento concurrente:

```bash
python3 scripts/s06/capturar_baseline.py --samples 12 --interval 2
```

Esta adquisición genera registros privados nuevos.

## Inferencia sobre artefactos existentes

```bash
PY="$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python"
"$PY" scripts/s06/inferencia_hq_readonly.py --audit
```

El comando requiere los modelos y datos válidos del
protocolo correspondiente.

Para iniciar una API temporal de lectura, si el puerto
9145 está libre y las fuentes han sido verificadas:

```bash
"$PY" -u scripts/s06/inferencia_hq_readonly.py --serve
```

Desde otra sesión:

```bash
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9145/healthz
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9145/api/v1/s06/live
```

Detener la API temporal con Ctrl+C en su propia terminal.
No incorporamos esta instancia al arranque automático.

## Entrenamiento y evaluación

Conservamos separados los siguientes componentes:

- [Mediciones de rendimiento](../../scripts/s06/medir_rendimiento.py).
- [Normalización](../../scripts/s06/normalizar_sesiones.py).
- [Línea base de anomalías](../../scripts/s06/entrenar_baseline_anomalias.py).
- [Entrenamiento y congelación V2](../../scripts/s06/entrenar_y_congelar_v2.py).
- [Evaluación cronológica V2](../../scripts/s06/evaluar_v2_congelado.py).
- [Auditoría de resultados](../../scripts/s06/auditar_resultados_v2_finales.py).

Los comandos que requieren identificadores de sesión
deben utilizar únicamente sesiones nuevas verificadas
o los artefactos históricos originales correspondientes.

## Intervención experimental

- [Simulación de rollback](../../docs/diseno/s06-rollback-simulacion.md).
- [Controlador y watchdog HQ](../../docs/diseno/s06-experimentos-hq-reales-y-watchdog.md).
- [Adquisición multisesión](../../docs/diseno/s06-lotes-multisesion-hq.md).
- [Falla HTTP independiente](../../docs/diseno/s06-fault-http-hq-etiquetado-independiente.md).

No incluimos intervenciones automáticas dentro de la
reconstrucción ni reutilizamos tokens de autorización.

## Documentación relacionada

- [Dependencias científicas](../../requirements-cientifico.txt).
- [Protocolo uniforme V2](../../docs/diseno/s06-protocolo-uniforme-v2.md).
- [Inferencia de solo lectura](../../docs/diseno/s06-inferencia-hq-replay-readonly.md).
- [Telemetría reciente](../../docs/diseno/s06-telemetria-reciente-inferencia-hq.md).
