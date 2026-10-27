# NETLAB360 — S04 G5: criterios y decisión acotada de observabilidad

**Fecha:** 2026-10-27 (Panamá), basado en mediciones de la VM y NOC verdaderas. **Tipo:** propuesta de aceptación **técnica interna**, sin certificar aprobación docente, SLA contractual ni SLO formal autorizado por el usuario.

## Indicadores comprobados

1. **SLI de scrape exitoso:** `100 × sum_over_time(up{job="netlab360-s04-multisede"}[ventana]) / count_over_time(up{job="netlab360-s04-multisede"}[ventana])`. Denominador: oportunidades con muestras presentes, no cada intervalo físico.
2. **SLI condicional de fuente confiable:** `100 × sum_over_time(netlab360_s04_source_up[ventana]) / count_over_time(netlab360_s04_source_up[ventana])`. **No medir con él disponibilidad global del exporter**, pues en scrapes fallidos la muestra `source_up` puede faltar.
3. Se declara separadamente el número de posiciones **nominales aproximadas** según `scrape_interval=2s`; una diferencia entre posiciones y muestras presentes **no se clasifica** como downtime sin inspección de causas. No se extrapola a pérdida de usuarios, latencia, jitter, conectividad HTTP, disponibilidad OSPF, ni SLA.

| Ventana de medición | Scrapes exitosos | SLI scrape | Fuente condicional | Fallos scrape | Error budget al 99 % candidato | Remanente | Evaluación del objetivo candidato |
|---|---:|---:|---:|---:|---:|---:|---|
| 15 minutos, 2026-10-27 07:51:08Z | 450/450 | 100.000 % | 450/450 (100 %) | 0 | 4 | +4 | Cumpliría |
| 60 minutos, 2026-10-27 07:51:08Z | 1698/1740 | **97.586 %** | 1698/1698 (100 %) | **42** | 17 | **−25** | **No cumpliría** |

El presupuesto de errores observados se computa `floor(N × (1 - SLO))` y el remanente `presupuesto - errores`, ambos discretos. Con ~1800 posiciones nominales cada 60 minutos y 1740 scrapes existentes no es válido declarar fallidas las 60 oportunidades no representadas. Tampoco se puede atribuir sin traza específica la totalidad de 42 fallos al corte de exporter; hubo tal ensayo durante la ventana amplia, pero no se demuestra aquí correspondencia uno a uno.

## Decisión de alcance de G5 propuesta para S04

**Alcance mínimo defendible para cierre técnico S04:**

- **Alertas y notificación local:** Prometheus evalúa reglas de colector/WAN/VLAN; el NOC muestra estados en vivo y transiciones/historial SQLite, con CSV por sede; esto es una **notificación visual local dentro del tablero**, no entrega asincrónica fuera de la aplicación.
- **Sin canal externo en S04:** Alertmanager, correo, Telegram, WhatsApp, SMS y webhooks **no implementados ni acreditados** en esta fase. Registrar como ampliación independiente en S05–S07 si se incorpora receptor, suscripción, reintentos y prueba real de recepción.
- **SLO académico candidato:** adoptar **99 % de éxito de scrape entre muestras existentes** como objetivo de diseño **sujeto a ratificación**; ventana de evaluación exploratoria **15 y 60 minutos**. El caso de 60 minutos **incumple** el candidato y demuestra sensibilidad a interrupciones controladas. No ajustar el objetivo a 97 % para ocultarlo, ni excluir fallos auténticos.
- Los resultados de G5 prueban el **método de medición y evaluación**; la aceptación de un sistema de observabilidad en fase S04 **no exige que jamás se supere el presupuesto** durante pruebas intencionales de fallas. Exige reportar fallos y recuperación verificables.
- La política operacional necesita un paso posterior de **revisión/ratificación** por el equipo/operador antes de llamarse SLO aprobado. Hasta entonces `S04_G5_SLO_ESTADO=PROPUESTA_NO_APROBADA`.

## Evidencias y conservación

- Dos JSON originales de G5 disponibles solo en VM, fuera de Git, en `~/netlab360-bootstrap/s04/evidencias/S04_G5_SLI_2026-10-27T0751080000_{15m,60m}.json`.
- S04_17 es la captura genuina del resultado, publicada en [PR #75](https://github.com/recm0708/netlab360/pull/75) con los lotes S04_12–16 (S04_15 en 2 partes).
- El único incidente WAN de prueba S04 G3 se recuperó sin afectación de ens33; se conservan log, JSON de TSDB y base SQLite original más respaldo de integridad SHA-256 fuera de Git.
- **G6** debe integrar tabla de comparación 15/60m, límites SLI, alcance de avisos locales, incidentes G3, validaciones G4 y prueba final G6. No crear apartado de anexos dentro del informe académico; material ampliado quedará en TAR técnico independiente.

## Estado de aceptación

**G5: criterios medidos, decisión técnica de alcance propuesta; pendiente ratificación interna y escrito.** No se pone la milestone S04 a 100 % por mera cantidad de PNG ni se cierra la issue transversal #47 antes de la reunión del 30/10.
