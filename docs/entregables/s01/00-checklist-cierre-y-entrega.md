# NETLAB360 — Checklist S01: dos documentos consolidados y cierre técnico

**Estado 14/10/2026:** S01 ABIERTA; **72/100 estimación técnica interna**, no nota ni aceptación docente. Portadas: las prepara el usuario. Documento 03 manual independiente ELIMINADO; sus temas se integran al 02. No comenzar S02 hasta cerrar contenido S01 y brechas técnicas exigibles.

## Documentos maestros únicos

- [01 — Diseño, desarrollo y evaluación del proyecto](../01-proyecto-investigacion-maestro.md): investigación académica, fundamentos, arquitectura, resultados e **incidentes técnicos reales y medidas de mitigación**, narrados dentro del desarrollo de cada componente.
- [02 — Manual técnico integral de implementación, administración y uso](../02-informe-tecnico-maestro.md): instalación desde cero, máquina virtual, SO, herramientas, scripts, comandos exitosos, salidas, figuras, pre/postchecks, utilización, seguridad, mantenimiento, y **posibles problemas y acciones correctivas** dentro de la sección aplicable; NO historial de errores reales sufridos.

[Política editorial](../00-politica-editorial-y-entrega-acumulativa.md) · [Figuras](../04-seleccion-figuras-y-tablas-s01.md).

## Logros de soporte verificados

- [x] 86 PNG planos + 7 CSV de manifiestos SHA-256, importados y publicados en Git, lote06 commit `b410548`.
- [x] Regresión local 24/24 tests, GitHub Actions run `38511477595` exitosa.
- [x] Último postcheck (13/10 23:35:02): sin Docker/netns residuales, gestión ens33 `192.168.47.40/24`, gateway `192.168.47.2`, tres servicios activos.
- [x] Cuatro resúmenes IaC 01/03/04/06 recuperados desde logs con exit0, sin repetir `tofu apply`; fotos definitivas aún pendientes.
- [x] Política y **dos** índices maestros V0.2 versionados y APROBADOS por el usuario el 14/10/2026; ajustes docentes posteriores permanecen posibles.
- [x] Borradores de tres documentos del 13/10 declarados rechazados y descontinuados; no constituyen entregables.

## Pendientes de S01

- [x] Aprobar los dos índices con el usuario (14/10/2026). **Pendiente de redacción:** comenzar por Introducción del Documento 01 cuando confirme «comencemos».
- [ ] Confirmar guía/rúbrica oficial: número de páginas, exigencia IA y OVA en S01 o más adelante, formato final y fecha.
- [ ] Redactar en plantilla institucional todo el contenido S01 del Documento 01: citas APA 7 reales, referencias cruzadas y resultados evidenciados; incidentes solo confirmados.
- [ ] Redactar en la misma plantilla institucional todo el contenido S01 del Documento 02, desde preparar host/VM hasta ejecutar, verificar, operar y cerrar NETLAB360; troubleshooting preventivo junto a cada procedimiento.
- [ ] Incluir preámbulos, figuras/tablas y notas APA 7 necesarias, índice automático único por documento, bibliografía final coherente.
- [ ] Auditar/publicar cuatro fotos IaC nuevas y postcheck LOTE06; no repetir laboratorios solo por fotos.
- [ ] Determinar y cubrir únicamente las brechas técnicas rubricadas como S01: integración L2–WAN, redundancia equipo, NOC, ML evaluable o release/OVA según corresponda.
- [ ] Registrar validación de entregables S01, resultados finales, Git commit/release requerido y decisión de aceptación antes de iniciar S02.

## Cierre final flexible

El usuario puede concluir el proyecto en la última fase realmente completada si el tiempo/alcance lo exige (por ejemplo S06). Se producirán **exactamente dos documentos consolidados que reflejen SOLO las fases implementadas**; no crear capítulos vacíos S07/S08 ni afirmar falsamente que el plan original era de seis semanas. Los compromisos rubricados y el roadmap histórico siguen identificables en Git; el documento final expondrá el alcance real aprobado.

No confundir la conclusión de una práctica con cierre S01. No sumar puntos por redacción preliminar ni presentar como IA entrenada el diagnóstico B4 por reglas.
