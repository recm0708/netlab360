# S06 — Mediciones activas de rendimiento en NETLAB360

## Objetivo

Complementar la primera sesión observacional **S06-032**, validada con 12/12 muestras y 25 series de estado por consulta, con mediciones originales de **RTT, pérdida ICMP y latencia de respuesta HTTP** sobre endpoints reales y permitidos de HQ, S1 y S2. Estas mediciones se hacen con una carga pequeña y sin modificar interfaces, rutas ni servicios.

**Distinción esencial:** las cinco familias S04 de Prometheus observan principalmente estado y administración; no acreditan pérdida, jitter, throughput ni latencia. Los RTT proceden de sondas ICMP acotadas; **no son equivalentes a latencia de aplicación ni a jitter UDP**.

## Endpoints y límites

| Identificador | Origen (namespace) | Destino | Señal |
|---|---|---|---|
| HQ_A_S1 | nl360-s02-h-hq-120 | 10.71.20.20 | RTT por paquete, pérdida y P95 ICMP |
| HQ_A_S2 | nl360-s02-h-hq-120 | 10.72.20.20 | RTT por paquete, pérdida y P95 ICMP |
| S2_A_FRONTAL_HQ | nl360-s02-h-s2-320 | 10.70.20.23 | RTT por paquete, pérdida y P95 ICMP |
| S2_A_FRONTAL_HQ_HTTP | nl360-s02-h-s2-320 | http://10.70.20.23:8080/api/v1/service | Duración de petición, código HTTP y backend HA |

La sonda HTTP reproduce el origen y la URL del ensayo HTTP HA S05. No se introducen destinos externos ni entrada de IP libre. El script realiza **tres rondas** predeterminadas, **cinco ICMP por destino y por ronda**, y una petición HTTP por ronda. Límites: rondas 1–8, ICMP 2–10 por destino, pausa 0–10 segundos. Las acciones se ejecutan con argumentos enumerados de subprocess, no mediante bash -c o shell libre.

## Requisito previo

- Red administrativa ens33 192.168.47.40/24, gateway 192.168.47.2, repositorio main limpio.
- 21 namespaces, entre ellos los tres clientes seleccionados; exporter y NOC con fuentes correctas; FRRouting y HA operativos con backend principal HQ.
- Sesión original S06-032 íntegra, con metadata complete y etiqueta no supervisada UNKNOWN, que se enlaza como referencia por su identificador exacto.

## Procedimiento de prueba propuesto

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

El P95 calculado con cinco paquetes es solo una **estimación exploratoria**, no una prueba de SLO ni base estadística para detección de anomalías. Posteriormente usaremos ventanas mayores y sesiones separadas.

## Continuación de S06

1. Validar captura real, conteos por origen/destino, calidad, integridad de archivos y conectividad con la referencia S06-032.
2. Definir una estructura común para series de estado y resultados cuantitativos, preservando unidades y timestamps.
3. Diseñar escenarios autorizados de degradación con estímulo independiente de la señal predictora, registro de inicio/fin y recuperación verificada.
4. Incorporar throughput TCP/UDP con iperf3 **únicamente** después de verificar servidores, rutas, carga y limitaciones de la VM.
5. Dividir por sesión y tiempo, controlar fugas y comparar modelos con baseline explicable. No entrenar un clasificador con las muestras UNKNOWN.

Relacionadas: issues #25, #6 y #26; [protocolo de S06](s06-adquisicion-observacional.md).
