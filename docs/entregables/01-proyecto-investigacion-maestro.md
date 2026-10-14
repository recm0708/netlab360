# NETLAB360 — Documento 01: Diseño, desarrollo y evaluación del proyecto

**Índice V0.2 APROBADO por el usuario el 14/10/2026, sujeto a indicaciones futuras de la profesora.** Documento académico ÚNICO, acumulativo desde S01 hasta la última fase efectivamente completada. **La portada institucional la prepara el usuario**. Índice general automático único en Word. Redacción académica desde el trabajo del equipo y referencias APA 7 que efectivamente se citan.

## Preliminares
- Portada de la institución (responsabilidad del usuario).
- Resumen y palabras clave; sintetizar alcance comprobado, metodología y resultados del **corte final**, actualizable durante el semestre.
- Índice general automático único.

## Índice general propuesto

1. **Introducción.** Presentación del proyecto, motivación y vínculo entre redes multisede, automatización, observabilidad y diagnóstico; anticipar lo que se ha implementado, sin prometer que lo futuro funciona.
2. **Planteamiento del problema.**
   - 2.1 Contexto y situación problemática.
   - 2.2 Problema que busca atender NETLAB360.
   - 2.3 Pregunta orientadora del proyecto.
3. **Justificación.**
   - 3.1 Justificación técnica.
   - 3.2 Justificación académica y formativa.
   - 3.3 Viabilidad y beneficios esperados, diferenciados de beneficios probados.
4. **Objetivos del proyecto.**
   - 4.1 Objetivo general único.
   - 4.2 Objetivos específicos medibles, adaptables al corte real del proyecto.
5. **Alcance, delimitaciones y requisitos.**
   - 5.1 Alcance funcional de la plataforma.
   - 5.2 Alcance del prototipo virtualizado y supuestos.
   - 5.3 Requisitos funcionales y no funcionales.
   - 5.4 Delimitaciones, riesgos y criterios de aceptación.
6. **Marco teórico y tecnológico.** Integrar fuentes verificadas APA7 en cada tópico:
   - 6.1 Virtualización, redes virtuales y contenedores.
   - 6.2 Redes empresariales multisede, VLAN y switching 802.1Q.
   - 6.3 Enrutamiento dinámico, OSPF y redundancia de WAN.
   - 6.4 Agregación de enlaces LACP y active-backup.
   - 6.5 Source of Truth, infraestructura como código y automatización (OpenTofu/Ansible).
   - 6.6 Observabilidad, métricas, telemetría, Prometheus y alertas.
   - 6.7 Diagnóstico por reglas, análisis de datos y fundamentos de AIOps; añadir modelos ML SOLO cuando existan implementados/evaluados.
   - 6.8 Nuevas tecnologías realmente incorporadas en fases posteriores (no rellenar anticipadamente).
7. **Metodología de diseño, implementación y evaluación.**
   - 7.1 Enfoque incremental, fases y gestión de cambios.
   - 7.2 Selección de herramientas y entorno controlado.
   - 7.3 Procedimiento de precheck, ejecución, medición y postcheck.
   - 7.4 Gestión de riesgos, calidad, trazabilidad y tratamiento de evidencias.
8. **Diseño y arquitectura de NETLAB360.**
   - 8.1 Arquitectura general y componentes.
   - 8.2 Topología de sedes HQ, S1 y sedes incorporadas.
   - 8.3 Plan de direccionamiento, VLAN, WAN y segmentación de gestión.
   - 8.4 Arquitectura de automatización, NOC, telemetría y analítica.
   - 8.5 Decisiones de arquitectura y justificación.
9. **Desarrollo del proyecto y decisiones técnicas.** Organizar en subcapítulos por las fases **realmente ejecutadas**; no crear ocho informes separados.
   - 9.1 Fase S01 — Preparación inicial y arquitectura de referencia, IPAM, pruebas de segmentación, FRRouting/OSPF, redundancia virtual, IaC inicial, observabilidad y diagnóstico de referencia.
   - 9.2 Fases posteriores **realmente completadas**, añadidas secuencialmente hasta el corte final; no reservar capítulos vacíos en el documento que se entregue.
   - **Dentro de cada subcapítulo correspondiente, integrar incidentes técnicos REALES y mitigaciones pertinentes**: contexto, síntoma, impacto, causa comprobada (o hipótesis señalada), decisión correctiva y verificación de la resolución. NO recopilar errores personales ni relegarlos a un anexo de incidentes.
10. **Resultados obtenidos y evaluación.**
    - 10.1 Resultados técnicos por criterio/objetivo, métricas y evidencias.
    - 10.2 Comparación diseño previsto–resultado realmente probado.
    - 10.3 Valoración de seguridad, reproducibilidad y cobertura funcional.
11. **Discusión y limitaciones.** Interpretación crítica, consideraciones de validez interna, restricciones reales y oportunidades de evolución justificadas.
12. **Recomendaciones.** Acciones recomendadas a partir de hallazgos, sin afirmar que ya fueron implementadas.
13. **Conclusiones.** Cumplimiento de objetivos del alcance final, síntesis respaldada por evidencia.
14. **Referencias.** Lista única APA 7 de todas y sólo las fuentes externas citadas dentro del documento.
15. **Anexos, únicamente si resultan necesarios.** Diagramas de lectura compleja, matrices extensas o inventarios; no desviar aquí las mitigaciones.

## Reglas editoriales específicas del Documento 01

- Redactar como producto del equipo: «el equipo implementó», «se verificó», «se estableció», «nuestra propuesta» cuando corresponda. No voz de IA, tampoco confesiones personales.
- Documentar incidentes técnicos reales durante el desarrollo **inmediatamente después del procedimiento/decisión afectado**, sin reescribir comandos completos ni narrar descuidos de operador. Marcar las causas no demostradas como hipótesis, no certezas.
- Explicar POR QUÉ se eligieron configuraciones y qué resultados se obtuvieron; comandos paso a paso y guía de usuario van al Documento 02.
- Figuras y tablas con preámbulo y referencia textual previa, título, número y **Nota.** si es pertinente; numeración continua.
- S01: distinguir que las pruebas L2, OSPF, LACP, bonding, IaC y B4 se desarrollaron en subtopologías o sesiones diferentes; no presentar como arquitectura única integrada si no se validó.
- En caso de que el semestre se cierre en la última fase completada (p. ej. S06), escribir el documento final con **cobertura real S01–S06**, sin anexar subcapítulos ficticios S07/S08 ni mentir sobre planes históricos o exigencias docentes.
- Cotejar y aprobar referencias antes de introducir citas APA7; no inventar bibliografía.

**Índices aprobados.** La redacción comenzará cuando el usuario indique «comencemos»; primera sección: 1. Introducción.
