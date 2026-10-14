# NETLAB360 — Documento 01: investigación y desarrollo del proyecto

**Propuesta de índice V0.1 para aprobación del usuario.** **Documento único y acumulativo S01–S08.** La presentación final se hará en la plantilla institucional aportada por el usuario, no en este Markdown. Insertar UN SOLO índice automático en Word. Toda cita externa tendrá referencia APA 7 comprobada.

## Preliminares (no repetir por fase)
- Portada institucional: universidad, facultad/carrera, asignatura, proyecto, integrantes, docente, grupo, lugar y fecha, según plantilla aportada.
- Resumen y palabras clave (en versión global actualizable).
- Índice general automático único.

## Cuerpo general del proyecto
1. **Introducción** (visión del semestre completo; describir S01 como MVP inicial).
2. **Planteamiento del problema** (contexto, problema central, pregunta orientadora).
3. **Justificación** (académica, técnica, operativa y viabilidad).
4. **Objetivos**
   - 4.1 Objetivo general (uno, permanente).
   - 4.2 Objetivos específicos (medibles y compatibles con S01–S08).
5. **Alcance, delimitaciones y criterios de éxito**
   - 5.1 Alcance global del proyecto semestral.
   - 5.2 Alcance efectivamente ejecutado S01; no equiparar diseño a despliegue.
   - 5.3 Supuestos, riesgos y límites.
6. **Marco conceptual y tecnológico** (se amplía al utilizar realmente tecnologías)
   - 6.1 Virtualización, contenedores, namespaces y redes definidas por software.
   - 6.2 VLAN, switching L2 y enrutamiento OSPF.
   - 6.3 Redundancia WAN, LACP y active-backup (diferencias y límites).
   - 6.4 Source of Truth, IaC, OpenTofu y Ansible.
   - 6.5 Observabilidad, Prometheus, API y telemetría.
   - 6.6 Diagnóstico determinista versus IA/AIOps (sin atribuir modelos).
   - 6.7 Tecnologías adicionales S02–S08: incluir sólo cuando corresponda.
7. **Metodología y criterios de validación**
   - 7.1 Enfoque de prototipo incremental y evidencia.
   - 7.2 Diseño por fases S01–S08 y trazabilidad.
   - 7.3 Variables, métricas, precheck/postcheck y límites de medición.
8. **Diseño general de la plataforma NETLAB360**
   - 8.1 Arquitectura lógica/física virtualizada y segregación de gestión.
   - 8.2 Red empresarial HQ–S1, S2 prevista y direccionamiento.
   - 8.3 Componentes de automatización, observabilidad, NOC y analítica.
   - 8.4 Seguridad, recuperación, decisiones de arquitectura.
9. **Desarrollo e integración por fases** (un capítulo, ocho subcapítulos crecientes; NO 8 informes separados)
   - 9.1 Fase S01: fundamentos operativos, segmento mínimo multisede y validaciones iniciales.
   - 9.2 Fase S02: reservado según desarrollo y rúbrica.
   - 9.3 Fase S03: reservado según desarrollo y rúbrica.
   - 9.4 Fase S04: reservado.
   - 9.5 Fase S05: reservado.
   - 9.6 Fase S06: reservado.
   - 9.7 Fase S07: reservado.
   - 9.8 Fase S08: reservado.
10. **Resultados y análisis crítico**
    - 10.1 Resultados comprobados de S01 (OSPF, ACL, LACP, IaC, NOC, reglas).
    - 10.2 Resultados adicionales de S02–S08 (se completan progresivamente).
    - 10.3 Comparación entre objetivos, observaciones y límites.
11. **Recomendaciones** (globales y revisables).
12. **Conclusiones** (globales y revisables).
13. **Referencias** (única lista global, APA 7, obras citadas en el texto).
14. **Anexos pertinentes** (solo si la institución los permite; enlazar inventarios/figuras).

## Reglas específicas

- No repetir los mismos comandos extensos del Documento 02; aquí se explica el sentido técnico y se analizan resultados.
- Describir OpenTofu como metadata/manifest, no aprovisionador de contenedores; Ansible produjo configs FRR usadas en B2.
- Precisar que las pruebas VLAN-L2, WAN-L3, LACP y active-backup fueron subtopologías separadas y que S2 está reservada.
- **Figuras/tablas:** siempre párrafo introductorio, mención explícita Figura N/Tabla N, número y título APA 7, **Nota.** de interpretación/fuente cuando proceda. Numeración continua por documento.
- No completar una bibliografía con obras no consultadas ni inventar DOI.
- No escribir todavía contenido S02–S08; sólo se reservan estos apartados como esquema editorial para futuras fases.
- El usuario copiará cada sección a su plantilla institucional después de revisar el texto entregado en el chat.

**Próxima sección a redactar con el usuario:** 1. Introducción de NETLAB360, con contexto del proyecto completo y alcance inicial de S01.
