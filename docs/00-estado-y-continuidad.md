**CORTE ACADEMICO VIGENTE — borrador 4.6, 27/10/2026:** informe único de **113 páginas** revisado frente a la guía docente `1457-Formato Proyecto Final.pdf`: portada, introducción, objetivos, problema, fundamento, diseño, implementación, pruebas, análisis, conclusiones, referencias y anexos técnicos remitidos al TAR separado previsto para la entrega final. Contiene **20 figuras (1–20), 13 tablas (1–13), 10 referencias** y **122 PNG oficiales** (S01=83, S02=9, S03=8, S04=22). Capítulos 7.10 y 8 actualizados al cierre técnico de S04; el SLO del 99 % sigue **candidato**, con muestra real 60 min 97,586 %. **Cierre editorial interno del texto hasta S04: validado; aprobación docente pendiente**. S01 conserva cierre SSH/compatibilidad/aceptación; S03 decisiones SoT y alcance de OpenTofu externo; S04 ratificación SLO y aceptación interna/docente. Fechas de revisión previstas: 30/10 y 13/11, no presumir realizadas. La VM se apagó ordenadamente, con sesión SSH cerrada; estado gráfico Powered Off aún por constatar.

*Las menciones posteriores a PDF 4.4/4.5 son registros históricos y no sustituyen este corte vigente.*

# NETLAB360 — Estado general y continuidad

**Fecha de corte: 27 de octubre de 2026.** Se trabaja sobre un repositorio privado único, fases S01–S08.

| Fase | Estado |
|---|---|
| S01 | Fundamentos técnicos comprobados; pendientes internos de aceptación/seguridad SSH |
| S02 | Cierre por alcance técnico documentado |
| S03 | Ansible FRR y OpenTofu declarativo validados; decisiones SoT/ciclo de vida abiertas |
| S04 | Observabilidad multisede G0–G4 y G6 técnicos aprobados, G5 SLI medido; aceptación académica/SLO pendiente |
| S05–S08 | Pendientes de implementación y demostración |

**Inventario oficial:** 122 PNG auténticas S01–S04 (83, 9, 8 y 22 respectivamente), protegidas con manifiestos y validaciones. El trabajo escrito **borrador 4.4 (110 pp)** contiene implementación 5.6 y pruebas 6.9, Figuras16–20 y Tabla13; pendiente interpretación S04 y adecuación de conclusiones, recomendaciones e inventario del Word.

**Operación de VM:** red de gestión `ens33 192.168.47.40/24`, gateway `192.168.47.2`; S04 respaldada y desmontada. Ubuntu recibió orden `sudo systemctl poweroff`, cerrando conexión SSH. Confirmar estado de VMware `Powered Off` desde el anfitrión antes de considerar completado el último control del apagado.

[Reanudar aquí](REANUDAR-AQUI.md) · [Tablero por fases](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [Control editorial](academico/s04-guion-de-actualizacion-del-informe.md).
