# S06-045 — Inferencia exploratoria HQ en replay, auditoría FP/FN y API de solo lectura

## Estado y objetivo

Incremento posterior a S06-044, que **sí se ejecutó en VM**: F06 aprobada, 23 pruebas locales, TRAIN/TEST separados por sesión y modelos privados íntegros. S06-045 introduce código nuevo; **aceptado técnicamente en VM el 23/11/2026**, tras validaciones completas de los modelos y API temporal.

No se intenta "predecir" estados futuros: la API reproduce inferencias sobre el TEST histórico reservado de S06-044. Son **las mismas muestras evaluadas anteriormente**, por lo que la reproducción NO constituye una segunda validación independiente ni evidencia de generalización. La siguiente integración de telemetría fresca y NOC requerirá fuentes comprobadas, age gates y otra aceptación.

## Implementación

- `scripts/s06/inferencia_hq_readonly.py` contiene validador de reporte, comprobación integridad criptográfica de los cuatro artefactos privados **antes** de llamar a `joblib.load`, comparación P95 / IsolationForest / LogisticRegression, auditoría exacta de las ventanas FP/FN y backend FastAPI opcional.
- `tests/test_s06_inferencia_readonly.py` tiene pruebas unitarias offline de integridad, fuentes autorizadas, consenso, UNKNOWN y métricas; no necesita una topología funcional ni scikit-learn para las pruebas centrales.
- Artefactos privados **fijados**: `~/netlab360-bootstrap/s06/evaluaciones/S06_044_20261123T081627Z_2ade0e/`; el endpoint jamás acepta una ruta de archivo, nombre de modelo, comando, IP ni namespace arbitrario. **Solo cargar modelos propios confiables**: integridad criptográfica dentro de un reporte local no defiende frente a alguien que pueda reemplazar a la vez modelos y informe de integridad.
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

## Ejecución y criterios de aceptación en VM (VALIDADA)

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

1. CI y validación local aceptadas; el TXT y PNG F07 verificados y aprobados en el chat.
2. Diseñar lectura de telemetría fresca y conexión no invasiva al NOC existente, con límites por edad, calidad y permisos.
3. Mantener abiertas las issues #6, #25, #26 y las fases S07–S08 hasta demostrar los requisitos faltantes.

## Aceptación en VM — 23/11/2026

PR [#170](https://github.com/recm0708/netlab360/pull/170) fusionado en `fedd89e`; CI completa **709 pruebas**, 708 aprobadas y una omitida por FastAPI ausente en CI mínima. La VM ejecutó 20 pruebas específicas, 19 aprobadas y una omitida, más la misma regresión integral de 709. El paquete FastAPI sí estaba disponible en el entorno científico; la API temporal funcionó en loopback.

**Incidencia de ejecución corregida, sin repetir los modelos ni experimentos:** el primer wrapper terminó RC 1 por un delimitador Python/here-document que interpretó una línea de `tee` como Python después de guardar la auditoría. Los resultados originales permanecieron y se reutilizaron desde `~/netlab360-bootstrap/s06/validacion-s06-045-20261123_033350/05_Auditoria_Errores.txt`. La reanudación validó las métricas y terminó `S06-045_VALIDACION_COMPLETA=OK`, `RESULTADO_RC=0`. Bitácora final: `~/netlab360-bootstrap/s06/validacion-s06-045-20261123_033350/S06_045_Reanudacion_Completa.txt`.

**Falsas alarmas reconstruidas (mismas ventanas de TEST, no nuevas muestras):** HQ→S1 P95=3 (índices 3/17/19), IsolationForest=1 (índice 3), LogisticRegression=0; HQ→S2 P95=1 e IsolationForest=1 (índice 16), LogisticRegression=0. FN DEGRADED=0 y FP RECOVERY=0 para todos. `S06_045_METRICAS_REPRODUCIDAS=OK`, `S06_045_ERROR_AUDIT=OK_REPLAY_ONLY`.

**API temporal:** `API_HEALTH=OK`, `API_LIVE=UNKNOWN_CORRECTO`, `API_REPLAY_NORMAL=NORMAL`, `API_REPLAY_DEGRADED=DETECTADO_3_MODELOS`, `API_REPLAY_RECOVERY=UNKNOWN_CORRECTO`, `API_AUDITORIA=OK`, ruta no autorizada rechazada (422), POST rechazado (405), `S06_045_API_SMOKE=OK`. Se verificó `API_TEMPORAL=DETENIDA`; ningún servicio permanente instalado. Es inferencia **histórica reproducida**, no clasificación sobre tráfico en vivo ni validación prospectiva.

**Poscondiciones:** 21 namespaces, 4 contenedores, `ens33 192.168.47.40/24` y gateway `192.168.47.2`, controlador HQ `NONE/BASELINE`, `qdisc noqueue`, Prometheus READY, NOC saludable y Git limpio. No hubo intervención de red ni reentrenamiento. TXT `~/netlab360-bootstrap/s06/evidencias/informe/S06_F07_Inferencia_Historica_API_Unknown_HQ.txt` preparado y verificado en la VM; **captura PNG F07 recibida, inspeccionada y aprobada en el chat**.

**Siguiente fase incremental:** S06-046, adaptar telemetría fresca con timestamps, contexto de ruta/ventana, estado de calidad, obsolescencia y UNKNOWN ante fallas, sin alterar S05 ni equiparar un resultado exploratorio con servicio productivo.
