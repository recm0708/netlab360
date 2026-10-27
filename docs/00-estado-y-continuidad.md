**CONTROL DE TABLAS PDF 4.4 (27/10):** La Tabla 12 (p. 98) compara capacidades de S01/S02 y se conserva. Hay dos rótulos «Tabla 13»: la tabla SLI de capítulo 6 mantiene el 13; la segunda, en 7.8 (p. 104), debe renumerarse a Tabla 14 y su fila de 107 capturas debe actualizarse a 122 (83/9/8/22). Revisar también cifras en 6.6 (p. 81), 6.9.6 (p. 97) y 7.7.1 (p. 103). No se ha editado el PDF; la corrección corresponde al Word del equipo.

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
