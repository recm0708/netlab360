# NETLAB360 — Plan de recuperación del desfase (actualizado 16/10/2026)

**Prevalencia:** [guías oficiales](../academico/00-requisitos-oficiales-2026-10-16.md) y [nuevo plan S02–S08](../academico/02-plan-operativo-s02-s08-repriorizado.md). Este documento sustituye recomendaciones antiguas de elaborar dos o tres informes.

## Situación
- Desfase identificado por el usuario: aproximadamente **una semana** respecto a su planificación interna.
- S01 produjo piezas verificadas y trazables; 72/100 es **métrica histórica de gestión**, no nota ni rúbrica docente.
- La guía exige **un solo informe escrito de >=40 páginas**; borrador S01 del usuario tiene ~65 páginas, pero requiere estructura docente 1–12 y secciones 7/8 más demostrativas.
- Presentación PowerPoint y demostración técnica final; anexos de fuentes, ZIP separado pendiente confirmación.
- Manual técnico independiente pospuesto; no volver a bloquear fase S02 por redactarlo.

## Ruta crítica propuesta
1. **Hoy:** registrar requisitos oficiales, reestructurar índice, issues y matriz sin destruir evidencia, fijar aclaraciones tras la transcripción.
2. **Próxima sesión Ubuntu:** precheck seguro y plan integrador HQ–S1–S2 con al menos dos enlaces WAN y servicios; no reconstruir ensayos aprobados.
3. **S02 integración prioritaria:** VLAN→WAN→servicio, failover y recuperación en una sola topología; solo después reforzar capacidad LACP/roles físicos por alcance.
4. **S03–S04:** IaC en la red realmente integrada y NOC/alertas con evidencias de estado y correlación; actualizar informe en paralelo.
5. **S05–S07:** redundancia adicional, SDN si se exige, dataset/IA si son objetivos definitivos; no atribuir capacidades no probadas.
6. **S08 o fecha final confirmada:** ejecutar regresión, cierre de incidentes, anexos ZIP si permitido, sanitización/exportación VM según requisitos, revisión APA7; DESPUÉS preparar PowerPoint y demo.

## Regla de no duplicación
- Usar 86 PNG y 7 CSV ya auditados; reencuadrar evidencia en el capítulo 8, no repetir laboratorios para nuevos screenshots.
- Reutilizar borrador institucional de 65 páginas, reorganizándolo según el [mapa oficial](../academico/01-migracion-borrador-a-formato-docente.md).
- Llevar código completo, logs extensos y outputs a anexos externos si se autorizan; el cuerpo debe explicar proceso y resultado.
- No mantener issue S01 bloqueada por requisitos S03/S06/S08; gestionar cierre de elementos pendientes en issues originales, sin declarar S01 formalmente cerrada.

## Bloqueos informativos
- Fecha oficial y duración final, formato ZIP, OVA, IA/SDN obligatoria, duración y modalidad de demo.
- La transcripción de reunión y el ejemplo de parcial **todavía están anunciados pero no analizados**.
- La VM Ubuntu está apagada tras shutdown seguro; pendiente confirmar estado visual en VMware. GitHub cambió desde el último `git pull` Ubuntu.

**Próxima autorización técnica:** el usuario decide el momento de arrancar Ubuntu; después dar varios pasos por respuesta para ahorrar tiempo.
