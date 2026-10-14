# NETLAB360 — Cierre de documentos y aceptación S01

**Corte organizativo 14/10/2026.** La redacción de S01 se realizará en tres documentos maestros acumulativos S01–S08, bajo el formato institucional del usuario. Las primeras versiones Word/Markdown del 13/10 quedaron **descontinuadas** como formato de entrega. No se redactarán tres documentos independientes por fase; tampoco se avanzará a S02 antes de cerrar los correspondientes a S01.

## Documentos maestros únicos

- [00 — Política editorial y APA 7](../00-politica-editorial-y-entrega-acumulativa.md).
- [01 — Investigación/desarrollo del proyecto](../01-proyecto-investigacion-maestro.md).
- [02 — Memoria técnico-práctica/laboratorios](../02-informe-tecnico-maestro.md).
- [03 — Manual de usuario y operación](../03-manual-usuario-maestro.md).
- [Matriz oficial interna de S01](../../control/03-matriz-aceptacion-y-decisions-s01.md).

## Lista operativa de S01

- [x] Publicación y validación de 86 PNG planos y siete CSV SHA256; commit `b410548` local/remoto iguales.
- [x] Regresión offline 24/24 y GitHub Actions `38511477595` exitosa.
- [x] Recuperación de cuatro bloques de evidencia IaC 01/03/04/06 desde logs originales con exit0 (sin repetir apply).
- [x] Crear la política editorial acumulativa y los tres índices maestros (pendiente de aprobación final por el usuario).
- [x] Retirar de circulación editorial los borradores rechazados sin romper enlaces históricos.
- [ ] Confirmar con docente/guía cuáles son las exigencias **realmente obligatorias de S01** frente a temas S03/S06/S08, páginas, fecha y entregables.
- [ ] Recibir aprobación de los índices y datos de portada/plantilla institucional.
- [ ] Redactar Documento 01 **sección por sección** con citas autor-fecha y referencias APA 7 verificadas; integrar lo correspondiente a S01.
- [ ] Redactar Documento 02 con instrucciones, comandos reales, capturas comentadas, salidas, tablas y postchecks.
- [ ] Redactar Documento 03 según funciones disponibles del producto, con tutoriales por casos de uso y capturas de interfaz.
- [ ] Recibir/auditar las cuatro nuevas fotografías IaC y postcheck `LOTE06_Postcheck_Publicacion.png` sin repetir pruebas.
- [ ] Verificar si se exige una sola red L2→WAN→servicio/NOC y redundancia de equipo en S01; realizar únicamente pruebas rubricadas pendientes.
- [ ] Verificar exigencia de modelo IA/ML ya en S01 (issues #25/#26 asociadas S06); si obligatorio, diseño/adquisición/evaluación externa honestos.
- [ ] Determinar exigencia de sanitizar/exportar/reimportar OVA en S01; si corresponde ejecutarlo, obtener hash y evidencia.
- [ ] Preparar release/tag y cierre con la aceptación exigible; dejar issue #1 ABIERTA hasta terminar.

## Convenciones académicas

- **Un solo índice automático por documento**. Numeración única y continua de tablas y figuras por documento a lo largo de S01–S08.
- **Preambulo obligatorio** a toda tabla/figura, referencia en párrafo previo y Nota. conforme APA 7 cuando sea necesaria.
- **Única bibliografía final** por documento, sólo para trabajos citados en texto y verificados; sin inventar referencias.
- El asistente entregará texto por secciones, y el usuario lo incorporará en su propia plantilla institucional. No generar Word arbitrariamente ni exigir que copie los antiguos.
- No rellenar S02–S08 con trabajo todavía no realizado; por ahora sólo escribir S01 y las partes globales justificadas.

**Pendiente crítico antes de declarar S01 terminada:** cotejar la guía/rúbrica docente, porque 72/100 es un indicador propio y varios requisitos de S01 se solapan con fases de otras issues. [Checkpoint](../../REANUDAR-AQUI.md).
