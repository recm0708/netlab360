# Capturas S04 — Observabilidad multisede

Versionamos **22 PNG auténticas**, distribuidas en tres lotes con SHA-256. Documentamos los estados de HQ/S1/S2, el incidente WAN y la persistencia de datos.

| Identificadores | Evidencia principal |
|---|---|
| S04_01–S04_06 | Exportador, Prometheus y NOC en estado basal |
| S04_07–S04_09 | Métricas y vistas activas de tres sedes |
| S04_10–S04_11 | Caída de HQ/s1p, conmutación al respaldo y resolución |
| S04_12 | TSDB Prometheus conservada tras reinicio |
| S04_13–S04_14 | Indisponibilidad `UNKNOWN` y recuperación de fuente |
| S04_15–S04_16 | Historial de incidentes y persistencia SQLite |
| S04_17 | SLI de recolección de 15m y 60m |

**Resultados de SLI:** 450/450 (100 %) en 15m y 1698/1740 (97,586 %) en 60m. El 99 % fue adoptado como referencia experimental interna de comparación y no se alcanzó en la ventana mayor; no lo presentamos como SLA contractual ni como aprobación específica de la docente. El NOC registra avisos locales; no acreditamos envíos a servicios externos.

**Selección:** las imágenes S04_16 y S04_17 ya están incluidas y verificadas. Los controles de preapagado/desmontaje S04_18 y S04_19 se conservaron como resultados operativos, **sin agregarse al catálogo PNG académico**.

[Manifiesto lote 1](../../manifiestos/MANIFIESTO_SHA256_S04_LOTE01_2026-10-26.csv) · [Lote 2](../../manifiestos/MANIFIESTO_SHA256_S04_LOTE02_2026-10-27.csv) · [Lote 3](../../manifiestos/MANIFIESTO_SHA256_S04_LOTE03_2026-10-27.csv).
