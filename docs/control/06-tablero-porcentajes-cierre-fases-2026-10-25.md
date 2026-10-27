**CORTE ACADEMICO VIGENTE — borrador 4.6, 27/10/2026:** informe único de **113 páginas** revisado frente a la guía docente `1457-Formato Proyecto Final.pdf`: portada, introducción, objetivos, problema, fundamento, diseño, implementación, pruebas, análisis, conclusiones, referencias y anexos técnicos remitidos al TAR separado previsto para la entrega final. Contiene **20 figuras (1–20), 13 tablas (1–13), 10 referencias** y **122 PNG oficiales** (S01=83, S02=9, S03=8, S04=22). Capítulos 7.10 y 8 actualizados al cierre técnico de S04; el SLO del 99 % sigue **candidato**, con muestra real 60 min 97,586 %. **Cierre editorial interno del texto hasta S04: validado; aprobación docente pendiente**. S01 conserva cierre SSH/compatibilidad/aceptación; S03 decisiones SoT y alcance de OpenTofu externo; S04 ratificación SLO y aceptación interna/docente. Fechas de revisión previstas: 30/10 y 13/11, no presumir realizadas. La VM se apagó ordenadamente, con sesión SSH cerrada; estado gráfico Powered Off aún por constatar.

*Las menciones posteriores a PDF 4.4/4.5 son registros históricos y no sustituyen este corte vigente.*

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
