# NETLAB360 — Plan de recuperación de cronograma S01

**Corte operativo de referencia:** 13/10/2026 23:35 Panamá. **Revisión del plan:** 14/10/2026. S01 programada internamente para 5–11/10 sigue ABIERTA; la etiqueta semanal GitHub no coincide necesariamente con semana académica real. No desplazar fechas oficiales de S02–S08 por iniciativa propia.

## Situación
B0–B4 cuentan con pruebas técnicas parciales satisfactorias, 86 PNG/7 CSV SHA, 24 tests CI/locales y VM limpia. La puntuación técnica interna 72/100 no implica aceptación de los once requisitos. Se inició política editorial acumulativa; borradores anteriores rechazados y dos índices maestros aprobados provisionalmente por el usuario el 14/10/2026 (modificables ante nuevas indicaciones docentes).

## Recuperación priorizada, sin expansión funcional
| Orden | Trabajo | Cierre verificable |
|---|---|---|
| P0 | Confirmar guía/rúbrica y relación S01↔S03/S06/S08 | Respuesta de la docente sobre alcance, formatos, páginas, fechas, OVA e IA |
| P0 | Acordar índices de 2 documentos maestros | **COMPLETADO** por aprobación del usuario; formato Word institucional, un índice por documento, APA 7 |
| P1 | Redactar Documento 01 de S01 | Introducción, objetivos, contexto, fundamentos y desarrollo con citas/referencias verificables |
| P1 | Redactar Documento 02 de S01 | Instalación desde cero, comandos correctos, capturas, pruebas, recuperación, operación y uso |
| P1 | Incorporar 4 fotos IaC desde log y postcheck lote06 | SHA256, carpeta plana, sin repetir tofu apply |
| P2 | Ejecutar únicamente pruebas técnicas rubricadas faltantes | Precheck→prueba integral mínima→postcheck→evidencia sin afectar VMnet8 |
| P2 | Sanitizar/exportar/reimportar OVA y release, si fecha S01 | SHA256 y entrega controlada; aceptación registrada |
| P3 | Cerrar S01 y permitir S02 | Issue #1 documentada contra guía oficial, dos textos consolidados S01 aprobados |

No añadir módulos nuevos B4 ni repetir convergencia/Prometheus/LACP sólo para subir porcentaje. No convertir análisis por reglas en IA evaluada. [Checklist S01](../entregables/s01/00-checklist-cierre-y-entrega.md) · [Matriz](03-matriz-aceptacion-y-decisions-s01.md).

**Historial anterior de esta página:** disponible en Git, con fecha y hash de cada actualización; sus órdenes de realizar LACP o IaC ahora ya están superadas por pruebas verificadas.
