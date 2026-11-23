# S06 — Normalización, calidad y procedencia del dataset

## Objetivo

Unificar las observaciones S06-032 (estados S04/NOC/Prometheus) con las mediciones S06-033 (ICMP y HTTP), de forma que se puedan auditar las fuentes, unidades, marcas de tiempo, identidad de sondas, cobertura, duplicados y ausencias. El producto de este paso es un **conjunto analítico preliminar**, NO un dataset supervisado ni un modelo entrenado.

## Fuentes ya acreditadas

| Referencia | Sesión | Resultado observado |
|---|---|---|
| S06-032 | S06_BASELINE_20261123T043741Z_39a268 | 12 observaciones de telemetría, 25 series por consulta, cinco familias |
| S06-033 | S06_PERF_20261123T044532Z_cea2dc | 9 mediciones ICMP de tres rutas y 3 HTTP HA, todas válidas |

En S06-033 hubo pérdida ICMP observada de 0 % y RTT medio de HQ a S1 0.084 ms, de HQ a S2 0.074 ms, de S2 al frontal HQ 0.081 ms y latencia HTTP promedio 7.594 ms; tres respuestas con BACKEND_HQ. Son mediciones dentro de VMware y no deben extrapolarse a enlaces WAN reales.

## Procedimiento

Desde el repositorio principal, con la VM y las fuentes originales intactas:

    python3 scripts/s06/normalizar_sesiones.py \
      --baseline S06_BASELINE_20261123T043741Z_39a268 \
      --performance S06_PERF_20261123T044532Z_cea2dc \
      --check-only

    python3 scripts/s06/normalizar_sesiones.py \
      --baseline S06_BASELINE_20261123T043741Z_39a268 \
      --performance S06_PERF_20261123T044532Z_cea2dc

Salida privada bajo netlab360-bootstrap/s06/datasets/curated/S06_QA_*/ con los archivos metricas_normalizadas.jsonl y reporte_calidad.json. El programa opera sobre copias **de lectura** de los archivos raw y no altera red, Docker, histórico SQLite, Prometheus, NOC ni datos originales.

## Validaciones de calidad

- Comprobar la huella de integridad declarada en cada metadata original; rechazar manipulación, archivos incompletos o enlaces simbólicos.
- Validar identidad de sesión, esquema, etiquetas UNKNOWN, indicadores de ground truth no verificado, índices y orden temporal UTC.
- Conservar para cada valor: fuente S04, ICMP o HTTP; sesión; índice; tiempo observado; tiempo de adquisición; señal; valor; unidad; contexto de etiquetas Prometheus o sonda.
- Mantener unidades distintas: estado/administración, paquetes, porcentaje, milisegundos. No mezclar eventos de servicio con rendimiento ICMP.
- Reportar valores nulos explícitamente; en ausencia de respuestas ICMP, no inventar RTT = 0.
- Contar repeticiones de scrapes Prometheus con la misma identidad/fecha. Una repetición de muestra no aumenta la cantidad efectiva de observaciones independientes.
- Verificar cobertura por familia, sonda y duración. No eliminar duplicados arbitrariamente ni reinterpretar muestras de seguimiento como entrenamiento.
- El informe muestra cuántos valores y fuentes existen realmente; esta fase no construye TRAIN/VALIDATION/TEST ni etiqueta NORMAL, DEGRADED, FAULT o RECOVERY.

## Criterios de aprobación S06-034

1. El código y sus tests offline pasan GitHub CI.
2. El operador ejecuta el precheck y la normalización en Ubuntu usando las sesiones originales verificadas.
3. Los derivados y el informe se crean fuera de Git, con integridad, permisos privados, metadatos completos, conteos y trazabilidad.
4. Los originales siguen inalterados, la red de gestión conserva ens33 192.168.47.40/24 y gateway 192.168.47.2.
5. El estado del resultado indica ground_truth_labels_available=0 y training_ready=false; no se atribuye avance de modelado a la normalización.

Después se diseñarán ensayos controlados de degradación/falla/recuperación, con estímulos verificables y mediciones más amplias, antes de crear modelos o métricas de clasificación. Relación: issues #25, #6 y #26.
