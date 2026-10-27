# NETLAB360 — Evidencias de la fase 4 (S04)

**Corte técnico: 26/10/2026.** El NOC inicial central/HQ/S1/S2, el exporter S04 y Prometheus fueron comprobados sobre la **topología intencionalmente desmontada**. No representa todavía la supervisión de WAN desplegadas ni una prueba de incidente y restauración.

## Primer lote de evidencias S04 — auditado y publicado

Se recibieron **siete capturas PNG originales** y se inspeccionaron visualmente contra las salidas de terminales. La [auditoría y los SHA-256 auténticos se registraron en la issue #4](https://github.com/recm0708/netlab360/issues/4#issuecomment-6433141415). **Las siete imágenes están versionadas en esta carpeta**, fusionadas mediante [PR #58](https://github.com/recm0708/netlab360/pull/58), junto con el [manifiesto SHA-256](../../manifiestos/MANIFIESTO_SHA256_S04_LOTE01_2026-10-26.csv). El inventario remoto contiene **114 PNG** entre S01–S04, de los cuales **7** corresponden a S04.

| Archivo previsto | Clasificación | Criterio demostrado |
|---|---|---|
| `S04_01_API_Telemetria_Real_Tres_Sedes_Offline.png` | Obligatoria | API Docker fiable; HQ/S1/S2, 8 WAN, 9 VLAN, 25 series |
| `S04_02_Prometheus_Scrape_Real_Sin_Falsas_Alertas.png` | Obligatoria | Scrape UP, fuente UP, cero falsas alarmas |
| `S04_03_NOC_Central_Tres_Sedes_Offline-1.png` | Obligatoria (parte 1) | Vista central de tres sedes |
| `S04_03_NOC_Central_Tres_Sedes_Offline-2.png` | Obligatoria (parte 2) | Sección de alertas del mismo NOC |
| `S04_04_NOC_Sucursal_Estados_WAN_VLAN.png` | Obligatoria | Vista S1 WAN/VLAN y frescura |
| `S04_05_NOC_API_Agregada_Fuentes_Confiables.png` | Complementaria | Agregación API de exporter y Prometheus |
| `S04_06_Postcheck_NOC_Prometheus_Exporter.png` | Complementaria | Puertos liberados; red de gestión intacta; Docker y Git limpios |

Las dos partes de S04_03 se conservan por separado sin recomprimir. No sustituir su contenido por reconstrucciones o imágenes generadas. Publicación completada: hashes de los PNG validados en Ubuntu antes del push; PR revisado con exactamente siete PNG y un CSV, normalización exclusiva de saltos de línea del CSV y fusión remota confirmada. No regenerar ni recomprimir las capturas.

**Estado de la fase 4:** abierta. Faltan topología activa, OSPF/servicios, alertas de fallas/restituciones reales, histórico, indicadores SLI/SLO, decisiones de notificación y documentación final.
