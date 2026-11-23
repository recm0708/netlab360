# S06 — Adquisición observacional y primera línea base

## Finalidad y alcance

La fase S06 utilizará mediciones **originadas en NETLAB360** para evaluar detección de anomalías, clasificación y predicción sin reutilizar cifras de ejercicios docentes como si se hubieran observado en la plataforma. El primer capturador es **solo lectura**, no genera fallas ni cambia interfaces y no produce etiquetas de entrenamiento.

Fuente técnica: S04 exporter (`127.0.0.1:9110`), topología NOC S05 (`127.0.0.1:9130`), Prometheus S04 (`127.0.0.1:9091`) y contador de eventos SQLite en modo de solo lectura. El acceso a estas fuentes está restringido a `127.0.0.1` y las rutas de API están fijadas en el programa.

## Datos actuales confirmados

- Prometheus versión 3.7.0, cinco familias de métricas S04: `netlab360_s04_source_up`, `netlab360_s04_router_running`, `netlab360_s04_topology_mode`, `netlab360_s04_vlan_admin_up`, `netlab360_s04_wan_admin_up`.
- Prometheus scrape (`up`), NOC con 18 nodos/21 enlaces, routing, estado HTTP HA, LACP por sede y estado SDN.
- SQLite S04 con tablas `active` y `events`. Al corte de S06-031, tres eventos en el histórico; cantidad insuficiente para afirmar desempeño ML.
- El estado administrativo de una interfaz no demuestra pérdida, latencia, jitter, rendimiento TCP/UDP o estado OSPF FULL; esas variables requerirán **fuentes adicionales y ensayos propios**.

## Primer procedimiento: línea base observacional

1. Verificar `main` limpio, kernel actual, red administrativa y estado activo de los servicios NOC/Prometheus, antes de capturar.
2. Ejecutar `python3 scripts/s06/capturar_baseline.py --check-only`; debe aprobar acceso local a fuentes, integridad de SQLite y disponibilidad de familias.
3. Capturar de forma limitada: `python3 scripts/s06/capturar_baseline.py --samples 12 --interval 2`. Límites en código: hasta 60 muestras, intervalos 1–30 s, timeout 2–10 s.
4. Los datos se escriben **fuera de Git** en `~/netlab360-bootstrap/s06/datasets/raw/S06_BASELINE_*/` (directorio privado, sin sobrescritura): `metadata.json` y `observaciones.jsonl`.
5. Verificar `samples_healthy`, contador de muestras, hash en metadatos, campos `recorded_at_utc` y `source_timestamps`, familias y valores observados, y preservación de la topología.
6. Etiquetar todas las muestras como `ground_truth_label=UNKNOWN`, `ground_truth_verified=false`. La condición `observed_healthy=true` solo acredita los criterios de disponibilidad del sistema de adquisición, **no** una etiqueta supervisada `NORMAL` ni garantía de rendimiento.

La calidad se marca `UNKNOWN` si falta una fuente, no hay scrape, la topología discrepa o el estado de HA/LACP/SDN difiere del escenario de referencia. No convertir `UNKNOWN` en falla de red ni en ejemplo válido de clasificación.

## Evolución prevista, todavía no implementada

- **Instrumentar mediciones de desempeño:** RTT, pérdida, variación temporal, throughput y tiempos HTTP con herramientas existentes y endpoints aislados del IPAM; medir antes y después de intervenciones reversibles.
- **Sesiones con ground truth:** escenarios independientes NORMAL / DEGRADED / FAULT / RECOVERY, con `session_id`, mecanismo de estímulo, timestamp de inicio/fin, severidad real y retorno verificado; UNKNOWN si el estímulo no se confirma.
- **Pipeline:** comparar ventanas, normalizar unidades, manejar duplicados y datos ausentes, establecer características, particionar por tiempo y sesión (TRAIN/VALIDATION/TEST) y comprobar fugas de información.
- **Modelos:** comparar reglas con detección no supervisada y modelos supervisados solo si el etiquetado permite calcular precision, recall, F1 y FP/FN; pronósticos con horizonte y MAE solo si existen series numéricas representativas.
- **S07/S08:** proveer API de inferencia de solo lectura y conservar autorización humana para cualquier acción que modifique el entorno.

## Criterios de aceptación de esta entrega parcial

- Capturador reproducible versionado, pruebas offline y consulta limitada a loopback.
- Al menos una sesión completa registrada en la VM con procedencia, tiempo, conteos y calidad, sin datos inventados.
- Sin modificar `ens33`, gateway, WAN, VLAN, HA, LACP, SDN, contenedores ni base TSDB.
- Los datos observacionales **no** cuentan todavía como dataset supervisado, modelo entrenado o S06 terminada.

Seguimiento: issues #6, #25 y #26; plan maestro `docs/diseno/s06-s08-plan-maestro-y-criterios.md`.
