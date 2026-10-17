# NETLAB360 — Requisitos académicos oficiales recibidos el 16/10/2026

**Prioridad documental:** estas guías docentes prevalecen sobre índices de trabajo y matrices internas anteriores. **Estado:** fuentes recibidas y revisadas; transcripción de la reunión y ejemplo de parcial anunciados, pero **todavía NO recibidos en esta revisión**. Cualquier interpretación añadida aparece diferenciada de lo que dicen los archivos.

## Documentos oficiales originales

| Documento proporcionado por el estudiante | Páginas | SHA-256 del archivo original | Contenido |
|---|---:|---|---|
| `1457-Formato Proyecto Final.pdf` | 3 | `525f50986abe7dd5345cf800d84da5effca7732fa4a533bd033914dab46ec49e` | Guía de informe escrito, presentación y demostración |
| `1457-Elaboración del Trabajo Escrito.pdf` | 25 | `2a9c25159dffcf68bb1b321fc7a0de29c3057d565812d42d3aec07e81993b4c5` | Explicación con esquemas de los 12 apartados |
| `1457-Formato de Presentación.pdf` | 15 | `a4f18c3cde91543f151111893983b0f27f1da0754f250f400a6cc1106311124a` | Guía/ejemplos de PowerPoint y demostración |

Los originales se recibieron como adjuntos de conversación; **sus archivos PDF binarios NO están incorporados físicamente al repositorio GitHub**. Registrar esta situación y no construir enlaces falsos a ellos.

## Requisitos EXPLÍCITOS del informe principal

**Una única entrega de informe escrito**, que documente problema, diseño, implementación y resultados. **Mínimo 40 páginas**. Estructura en orden indicada literalmente por el archivo oficial:

1. **Portada**: universidad, facultad/carrera, asignatura, título, integrantes **con nombre y cédula**, profesor y fecha.
2. **Introducción**: contexto, relevancia para redes modernas y síntesis de la solución.
3. **Objetivos**: general y específicos, redactados como resultados verificables (diapositivas de ampliación).
4. **Planteamiento del problema**: situación, limitaciones/necesidades y justificación de la solución.
5. **Fundamento técnico**: conceptos, tecnologías, protocolos/herramientas, arquitectura/enfoque y fuentes.
6. **Diseño de la solución**: arquitectura, topología, componentes, IP, servicios, protocolos, flujos/políticas e interacciones.
7. **Implementación**: entorno, hardware, software/versiones, configuraciones principales, secuencia de implementación, scripts y automatizaciones; **explicar lógica**, sin incluir por defecto todo el código en el cuerpo (guía ampliada, láminas 14–15 y 24–25).
8. **Pruebas y validación**: baseline, escenarios normales/falla, resultados esperados frente a observados y evidencias contextualizadas.
9. **Análisis de resultados**: interpretación técnica, problemas reales y mitigaciones, limitaciones, mejoras.
10. **Conclusiones y recomendaciones**: grado verificable de logro de objetivos, limitaciones y recomendaciones de mejora futura.
11. **Referencias**: fuentes citadas; guía dice «preferiblemente formato APA» y el usuario ha escogido **APA 7 + formato institucional**.
12. **Anexos**: código/scripts, configuraciones, salidas relevantes, YAML, JSON, OpenTofu/Terraform, Ansible, Python y demás fuentes útiles.

**Sin mínimo o máximo separado de páginas para la presentación**, sin cantidad de diapositivas, sin fecha exacta de entrega y **sin exigencia textual de un manual técnico independiente** en las tres guías analizadas. No inventar tales requisitos.

## Presentación y demostración EXPLÍCITAS

- PowerPoint: título del proyecto, introducción, objetivo general y específicos, planteamiento del problema, diseño de la solución, demostración, conclusión y referencias.
- Las diapositivas de orientación ilustran jerarquía de títulos, objetivos medibles, arquitectura por componentes/protocolos y una demostración técnica comprensible.
- La demostración **no se limita a mostrar «funciona»**: presentar condiciones iniciales, estímulo/cambio y contraste esperado vs. observado, explicando la solución y validando técnicamente el comportamiento.

**La presentación se preparará DESPUÉS de completar y estabilizar el informe**, según instrucción del usuario.

## Interpretaciones/decisiones del usuario — NO son mandatos literales del PDF

1. **Un solo informe académico-técnico como entregable escrito obligatorio**; el antiguo Documento 02 de manual operativo se pospone a después de que la plataforma/informe funcionen y finalicen, como documento voluntario/futuro. Conservar issue #28 y archivo índice como historial posentrega.
2. **Anexos en un paquete ZIP separado** con TXT/YAML/PY/scripts/configuraciones y manifiesto es una opción propuesta por el usuario, coherente con la sección 12, **pendiente de confirmación de aceptación y forma de entrega en reunión/docente**. El cuerpo debe contener explicación técnica y evidencias suficientes por sí mismo, no una mera referencia al ZIP.
3. Mantener portada institucional del usuario, un índice automático, y numeración continua de tablas/figuras, con preámbulo, título y nota cuando corresponda.
4. Registrar incidentes técnicos reales y su mitigación **en 9. Análisis**, con referencias cruzadas a los pasos de implementación afectados; excluir errores de descuido del operador, no inventar causas ni soluciones.
5. El título completo de NETLAB360 puede figurar en portada y el encabezado corto acordado `NETLAB360 | Redes Empresariales Multisede`.
6. La continuidad técnica no debe bloquearse hasta escribir un manual posentrega. El reporte único se actualizará al finalizar pruebas e integración reales.

## Pendiente de aclaración con la transcripción docente

Fecha exacta de presentación/entrega, si la extensión mínima incluye/excluye portada/índice/anexos; si admite ZIP separado y con qué estructura y restricciones; si exige OVA/VM exportada, demo en vivo/offline, número/duración de diapositivas, requisitos de IA/SDN, criterios de evaluación y compatibilidad de VM.

**Regla de interpretación:** las diapositivas contienen *ejemplos pedagógicos*, como sistema de monitoreo o sistema de usuarios, **NO una exigencia de que NETLAB360 copie literalmente esas soluciones**.
