# NETLAB360 — Estado actual y continuidad

> **Actualización de control 14/10:** auditoría íntegra de issues y milestones ([informe](control/04-auditoria-issues-milestones-2026-10-14.md)): 43 totales, 38 abiertas, 5 cerradas, 0 abiertas sin milestone. Cerradas ahora #33 (CI offline) y #42 (FRR/OSPF dual-WAN). Sigue abierta #38 SSH hasta validar hardening y recuperación, sin reconfiguraciones a ciegas. Índices de dos documentos aprobados por usuario. Ubuntu aún pendiente de sincronizar.


**Revisión editorial 14/10/2026.** Fuentes canónicas: [REANUDAR AQUÍ](REANUDAR-AQUI.md) y [matriz de aceptación S01](control/03-matriz-aceptacion-y-decisions-s01.md).

## Estado operativo

S01 ABIERTA, 72/100 interno, guía/rúbrica docente pendiente. El usuario prohíbe iniciar S02 hasta terminar los textos S01 y las exigencias técnicas verificables. Los bloques B0–B4 tienen subpruebas funcionales; no presentar topologías separadas como una red integral ni detector por reglas como IA entrenada.

Evidencia: 86 PNG planos, 7 CSV hash, commit lote06 b410548, 24/24 tests y CI run 38511477595. Último postcheck sin Docker/netns, gestión ens33 192.168.47.40/24 y gateway .2, tres servicios activos. Commits editoriales posteriores requieren pull ff-only de Ubuntu.

## Entregables oficiales del trabajo: dos documentos

1. [Documento 01 — Diseño, desarrollo y evaluación académica](entregables/01-proyecto-investigacion-maestro.md): fundamentos, arquitectura, resultados e incidentes técnicos reales con su mitigación **dentro del desarrollo**.
2. [Documento 02 — Manual técnico integral](entregables/02-informe-tecnico-maestro.md): instalación desde cero, requisitos, comandos corregidos, pruebas, capturas, puesta en marcha, uso y administración; **posibles fallos y solución preventiva**, sin cronología de equivocaciones históricas.

Portadas hechas por usuario. Redacción por secciones; un índice automático por documento, APA7 y referencias realmente citadas, figuras y tablas presentadas/interpretadas. Al finalizar, describir fases realmente completadas sin capítulos ficticios ni ocultar roadmap original.

## Pendientes

Dos índices aprobados el 14/10/2026; comenzar Documento 01 sólo cuando el usuario lo indique; confirmar guía/rúbrica oficial, completar S01 y fotografías IaC pendientes, no crear nuevos laboratorios salvo aceptación estricta. Documento 03 de manual separado fue retirado y su contenido incorporado al 02.
