# Mediciones activas de rendimiento

## Descripción

Complementamos la primera sesión observacional **S06-032**, validada con 12/12 muestras y 25 series de estado por consulta, con mediciones originales de **RTT, pérdida ICMP y latencia de respuesta HTTP** sobre endpoints reales y permitidos de HQ, S1 y S2. Realizamos estas mediciones con una carga pequeña y sin modificar interfaces, rutas ni servicios.

**Distinción esencial:** las cinco familias de métricas del exportador de Prometheus observan principalmente estado y administración; no acreditan pérdida, jitter, throughput ni latencia. Los RTT proceden de sondas ICMP acotadas; **no son equivalentes a latencia de aplicación ni a jitter UDP**.

## Endpoints y límites

| Identificador | Origen (namespace) | Destino | Señal |
|---|---|---|---|
| HQ_A_S1 | nl360-s02-h-hq-120 | 10.71.20.20 | RTT por paquete, pérdida y P95 ICMP |
| HQ_A_S2 | nl360-s02-h-hq-120 | 10.72.20.20 | RTT por paquete, pérdida y P95 ICMP |
| S2_A_FRONTAL_HQ | nl360-s02-h-s2-320 | 10.70.20.23 | RTT por paquete, pérdida y P95 ICMP |
| S2_A_FRONTAL_HQ_HTTP | nl360-s02-h-s2-320 | http://10.70.20.23:8080/api/v1/service | Duración de petición, código HTTP y backend HA |

La sonda HTTP reproduce el origen y la URL del ensayo HTTP HA. No se introducen destinos externos ni entrada de IP libre. El script realiza **tres rondas** predeterminadas, **cinco ICMP por destino y por ronda**, y una petición HTTP por ronda. Límites: rondas 1–8, ICMP 2–10 por destino, pausa 0–10 segundos. Las acciones se ejecutan con argumentos enumerados de subprocess, no mediante bash -c o shell libre.

## Requisito previo

- Red administrativa ens33 192.168.47.40/24, gateway 192.168.47.2, repositorio main limpio.
- 21 namespaces, entre ellos los tres clientes seleccionados; exporter y NOC con fuentes correctas; FRRouting y HA operativos con backend principal HQ.
- Sesión original S06-032 íntegra, con metadata complete y etiqueta no supervisada UNKNOWN, que se enlaza como referencia por su identificador exacto.

## Procedimiento de medición

Ejecutar desde el directorio principal del repositorio:

    python3 scripts/s06/medir_rendimiento.py \
        --reference-session S06_BASELINE_20261123T043741Z_39a268 \
        --check-only

    python3 scripts/s06/medir_rendimiento.py \
        --reference-session S06_BASELINE_20261123T043741Z_39a268 \
        --rounds 3 --packets 5 --pause 1

Cada sesión se escribe bajo el subdirectorio privado netlab360-bootstrap/s06/datasets/raw/S06_PERF_* con metadata.json y mediciones.jsonl, con procedencia, identificador, asociación al baseline, timestamps UTC, calidad por sonda, valores ICMP/HTTP y contador de lecturas. Los archivos son privados y **no forman parte de Git ni del TAR docente bruto sin revisión previa**.

## Modelo de resultados

- sent, received, loss_pct: paquetes transmitidos, respuestas y porcentaje de pérdida. Una pérdida del 100 % sigue siendo una medición válida si el resumen ICMP pudo observarse; no se etiqueta automáticamente como falla.
- rtt_min_ms, rtt_avg_ms, rtt_max_ms, rtt_mdev_ms, rtt_p95_ms, rtt_samples_ms: números obtenidos exclusivamente de las respuestas ICMP. Si no hubo respuestas, RTT es nulo, no cero.
- elapsed_ms, http_status, availability, active_backend, selected_path: medición real HTTP desde S2 con frontend HQ.
- measurement_valid=false y quality_warnings: fallo de medición, timeout o respuesta incompatible con el contrato; no se sustituye por ceros ni por datos sintéticos.
- ground_truth_label=UNKNOWN y ground_truth_verified=false para **todas** las observaciones. Las métricas cuantitativas no determinan por sí solas la causa del comportamiento.

El P95 calculado con cinco paquetes es solo una **estimación exploratoria**, no una prueba de SLO ni base estadística para detección de anomalías. Los ensayos etiquetados posteriores emplearon un protocolo separado.

## Validación y limitaciones

S06-033 registró nueve mediciones ICMP y tres HTTP válidas. Pérdida ICMP observada: 0 %. RTT medio HQ→S1: 0,084 ms; HQ→S2: 0,074 ms; S2→frontal HQ: 0,081 ms. Latencia HTTP media: 7,594 ms, con BACKEND_HQ en las tres peticiones. Las medidas son puntuales, proceden de una VM y no acreditan SLO ni rendimiento de WAN físicas. Todas las etiquetas permanecen UNKNOWN. [Normalización](s06-normalizacion-y-calidad.md).
