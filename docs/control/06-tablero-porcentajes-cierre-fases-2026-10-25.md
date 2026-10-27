**CORTE ACADÉMICO VERIFICADO — PDF 4.5 (27/10/2026, 112 páginas).** Se auditaron en el PDF los rótulos y referencias de **20 figuras consecutivas (1–20)** y **13 tablas consecutivas (1–13)**, sin saltos ni duplicados. Los 33 elementos tienen título, nota y referencia en el texto. **Tabla 11**: indicadores SLI, p. 96; **Tabla 12**: comparación técnica S01/S02, pp. 98–99; **Tabla 13**: correspondencia de objetivos, pp. 104–105 y 122 PNG. **No existe Tabla 14 ni debe crearse** mientras no se agregue una nueva tabla. El apartado 7.10 ya consta en pp. 106–108; pendiente ajustar 7.6/7.9 y capítulo 8 (conclusiones/recomendaciones) que conserva afirmaciones anteriores a la ejecución S04. El PDF no fue editado automáticamente.

# NETLAB360 — Indicadores verificables y control de fases

**Corte 27/10/2026.** Distinguir el **porcentaje de milestone GitHub** (issues cerradas / total) de la aceptación técnica y académica. Los indicadores S01 72 % histórico y S03 ≈90 % estimado proceden de matrices propias; no equivalen al porcentaje de un milestone.

| Fase | Situación técnica al corte | Pendientes de su alcance |
|---|---|---|
| S01 | Laboratorios iniciales comprobados; 83 PNG oficiales | Decidir endurecimiento SSH con rollback; compatibilidad base y aceptación de línea fundacional |
| S02 | **Cerrada técnicamente**, 9 PNG | Ningún criterio propio de cierre pendiente |
| S03 | Ansible 8/8 y drift/reconciliación real, 17 metadatos OpenTofu, CI; 8 PNG | Ratificar contrato SoT candidate y alcance OpenTofu; aceptación interna |
| S04 | G0–G4 aprobados, G5 medido y G6 regresión correcta; 22 PNG | Ratificación del SLO candidato, capítulos 7–8/actualización final del Word y evaluación académica |
| S05 | Planificada | Redundancia/capacidad, OVS/Faucet, grafo vivo con señales reales |
| S06 | Planificada | Dataset fiable, reglas comparativas y evaluación ML |
| S07 | Planificada | Integración de componentes y recuperación coordinada |
| S08 | Planificada | TAR seguro, PowerPoint, defensa y aceptación final |

**Indicadores de observabilidad:** 15m 450/450 (100 %) y 60m 1698/1740 (97,586 %), 42 scrapes fallidos. El objetivo 99 % es un **SLO académico candidato no ratificado** y se incumple en la ventana de 60m. No se equipara scrape a disponibilidad de aplicaciones.

**Estado de issues por milestone:** S01 tiene 11/14 cerradas, S02 3/3, S03 3/6; en S04, los entregables #15 y #20 están cerrados con respaldo técnico y las tareas académicas/SLI mantienen seguimiento específico. La interfaz de GitHub puede mostrar un conteo retrasado: comprobarlo contra el estado individual de las issues. El porcentaje refleja cierre de issues, **no** tareas marcadas dentro de su cuerpo. No se ajusta manualmente ni se considera cumplimiento docente.

**Capturas actuales:** 83 S01 + 9 S02 + 8 S03 + 22 S04 = **122 PNG oficiales**, distribuidas por carpetas y asociadas a control criptográfico. No incorporar al informe resultados no medidos ni presentar como terminadas fases S05–S08.

**Operación al corte:** topología experimental desmontada, TSDB y SQLite respaldadas y verificadas, `sudo systemctl poweroff` ejecutado con cierre remoto SSH; estado Powered Off en VMware pendiente de confirmación externa. [Bitácora](../sesiones/2026-10-27-s04-poweroff-solicitado-borrador43.md).

**Tareas académicas:** borrador 4.4 de 110 pp. ya incluye 5.6 y 6.9, con Figura20 y Tabla13; falta ajustar análisis S04 en capítulo7, conclusiones/recomendaciones en capítulo8 y la la Tabla 13 de objetivos y resultados. Teams 30/10 y 13/11 aún no celebradas al corte. [Guion](../academico/s04-guion-de-actualizacion-del-informe.md).
