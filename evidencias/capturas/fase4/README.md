# NETLAB360 — Evidencias oficiales de la fase 4 (S04)

**22 PNG originales** agrupadas en tres lotes, con hashes SHA-256, tamaños y dimensiones comprobados. La supervisión se realizó sobre infraestructura FRRouting/OSPF multisede activa, con observación de HQ, S1 y S2.

| Identificadores | Contenido demostrado |
|---|---|
| S04_01–S04_06 | Colector, Prometheus y NOC en condición basal controlada |
| S04_07–S04_09 | Estado real de tres sedes, WAN y VLAN activas, métricas y vistas del NOC |
| S04_10–S04_11 | Incidente WAN HQ/s1p, alerta firing, respaldo s1b y recuperación |
| S04_12 | Persistencia histórica de métricas Prometheus tras reinicio |
| S04_13–S04_14 | Indisponibilidad del colector UNKNOWN y restauración sin falsas alarmas WAN/VLAN |
| S04_15–S04_16 | Historial de incidentes por sede y persistencia SQLite tras reinicio |
| S04_17 | Indicadores de éxito de recolección SLI en 15 y 60 minutos |

[Manifiesto lote 01](../../manifiestos/MANIFIESTO_SHA256_S04_LOTE01_2026-10-26.csv) · [Lote 02](../../manifiestos/MANIFIESTO_SHA256_S04_LOTE02_2026-10-27.csv) · [Lote 03](../../manifiestos/MANIFIESTO_SHA256_S04_LOTE03_2026-10-27.csv)

El NOC muestra estados locales y eventos; no se ha acreditado entrega externa de mensajes. El SLO académico del 99 % está **propuesto, pendiente de ratificación**; la ventana de 60 minutos obtuvo 97,586 % de éxito entre scrapes registrados. La aceptación académica queda sujeta al informe único y la revisión correspondiente.
