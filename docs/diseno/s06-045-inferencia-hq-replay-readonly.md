# S06-045 — Inferencia exploratoria HQ en replay, auditoría FP/FN y API de solo lectura

## Estado y objetivo

Incremento posterior a S06-044, que **sí se ejecutó en VM**: F06 aprobada, 23 pruebas locales, TRAIN/TEST separados por sesión y modelos privados íntegros. S06-045 introduce código nuevo; **no se declara aceptado en VM hasta ejecutar las pruebas y auditoría reales**.

No se intenta "predecir" estados futuros: la API reproduce inferencias sobre el TEST histórico reservado de S06-044. Son **las mismas muestras evaluadas anteriormente**, por lo que la reproducción NO constituye una segunda validación independiente ni evidencia de generalización. La siguiente integración de telemetría fresca y NOC requerirá fuentes comprobadas, age gates y otra aceptación.

## Implementación

- `scripts/s06/inferencia_hq_readonly.py` contiene validador de reporte, comprobación SHA-256 de los cuatro artefactos privados **antes** de llamar a `joblib.load`, comparación P95 / IsolationForest / LogisticRegression, auditoría exacta de las ventanas FP/FN y backend FastAPI opcional.
- `tests/test_s06_inferencia_readonly.py` tiene pruebas unitarias offline de integridad, fuentes autorizadas, consenso, UNKNOWN y métricas; no necesita una topología funcional ni scikit-learn para las pruebas centrales.
- Artefactos privados **fijados**: `~/netlab360-bootstrap/s06/evaluaciones/S06_044_20261123T081627Z_2ade0e/`; el endpoint jamás acepta una ruta de archivo, nombre de modelo, comando, IP ni namespace arbitrario. **Solo cargar modelos propios confiables**: SHA-256 dentro de un reporte local no defiende frente a alguien que pueda reemplazar a la vez modelos y manifiesto.
- El contrato es binario NORMAL/DEGRADED y su **consenso** entre tres métodos. Si discrepan, `operational_state=UNKNOWN` en lugar de forzar predicción. Las muestras RECOVERY nunca se presentan como una clase ML aprendida: aunque el consenso binario sea NORMAL, `operational_state=UNKNOWN` porque RTT/pérdida solos no demuestran estado de recuperación.
- Todas las respuestas declaran `production_deployment_authorized=false`, `network_mutations_authorized=false` y `new_independent_validation=false`. Se omiten probabilidades como "confianza calibrada".
- Si faltan archivos, metadatos verificables, modelo, integridad o suficientes ventanas, se devuelve UNKNOWN. La API `/api/v1/s06/live` devuelve **siempre** UNKNOWN con razón `LIVE_TELEMETRY_NOT_INTEGRATED` hasta disponer de un colector en vivo comprobado.
- No se modifican el NOC S05, FRR, qdisc, namespaces, interfaz administrativa, Docker, Prometheus, servicio systemd ni el dataset.

## Endpoints (solo GET)

Servicio temporal en `127.0.0.1:9145` dentro de la VM. No se instala daemon, se expone externamente ni se habilita automáticamente.

| Recurso | Semántica |
|---|---|
| `GET /healthz` | Proceso API disponible; no equivale a calidad del modelo |
| `GET /api/v1/s06/live` | UNKNOWN hasta integración real futura |
| `GET /api/v1/s06/replay?route=HQ_A_S1&scenario=DEGRADED&window_index=1` | Predicciones sobre muestra histórica permitida |
| `GET /api/v1/s06/error-audit` | Ventanas FP/FN por ruta y método, comprobadas frente al reporte S06-044 |

`route` es exclusivamente `HQ_A_S1` o `HQ_A_S2`. `scenario` es `NORMAL`, `DEGRADED` o `RECOVERY` y `window_index` entero entre 1 y 20, limitado adicionalmente al tamaño real de la sesión. Son categorías de selección de datos históricamente verificados, **no características de entrada del modelo**. No hay métodos POST/PUT/PATCH/DELETE de cambio de estado.

## Ejecución y criterios de aceptación en VM (PENDIENTE)

```bash
cd ~/proyectos/netlab360
python3 -m py_compile scripts/s06/inferencia_hq_readonly.py
python3 -m unittest discover -s tests -p 'test_s06_inferencia_readonly.py' -v
"$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python" -u scripts/s06/inferencia_hq_readonly.py --audit
```

La auditoría debe terminar con `S06_045_ERROR_AUDIT=OK_REPLAY_ONLY` y reproducir los falsos positivos S06-044 (**HQ→S1** P95=3, IF=1, Logistic=0; **HQ→S2** P95=1, IF=1, Logistic=0), sin FN DEGRADED ni FP RECOVERY. La prueba **no reentrena modelos**. Control posterior: 21 namespaces, 4 Docker, `ens33` y gateway intactos, HQ `qdisc noqueue`, NOC/Prometheus saludables.

La API se puede iniciar de manera temporal y supervisada con el Python del venv:
```bash
"$HOME/netlab360-bootstrap/entornos/netlab360-s06-s08/bin/python" -u scripts/s06/inferencia_hq_readonly.py --serve
```
Desde otra terminal en VM comprobar `curl --noproxy '*' http://127.0.0.1:9145/healthz`, `/api/v1/s06/live`, `/api/v1/s06/replay?route=HQ_A_S1&scenario=DEGRADED&window_index=1` y `/api/v1/s06/error-audit`. Detener con Ctrl+C de **esa** terminal. La opción `--serve` obliga loopback, no debe ejecutarse bajo sudo y no se agrega aún al arranque automático.

## Riesgos y límites

El experimento contiene solo un retardo de 40 ms, cuatro ventanas positivas por ruta en TEST, dos rutas correlacionadas y partición por sesión no cronológica global. No se valida degradación por pérdida, OSPF, WAN, HA, LACP ni SDN. La auditoría por ventana **reutiliza el test ya visto** para análisis de errores; no emplearla para retocar hiperparámetros y afirmar un nuevo TEST válido. Para inferencia en vivo se necesitarán ventanas con medidas recientes, procedencia verificable, contrato de muestreo y un gate de obsolescencia.

## Próximos pasos

1. Revisar CI de PR S06-045 y aceptar ejecución local en VM; tomar futura evidencia F07 únicamente después del gate completo.
2. Diseñar lectura de telemetría fresca y conexión no invasiva al NOC existente, con límites por edad, calidad y permisos.
3. Mantener abiertas las issues #6, #25, #26 y las fases S07–S08 hasta demostrar los requisitos faltantes.
