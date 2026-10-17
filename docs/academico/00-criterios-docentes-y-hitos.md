# NETLAB360 — Criterios docentes aplicables y entregas (actualizado 17/10/2026)

**Alcance de este archivo:** solamente instrucciones operativas y académicas aplicables a NETLAB360. Este repositorio **NO almacena archivos de clase, guías de la profesora, grabaciones, transcripciones ni sus huellas digitales**; no incorporar esos materiales como evidencia técnica del proyecto. El historial Git previo se conserva sin reescritura destructiva.

## Estructura y calidad del proyecto semestral

- **Dos partes del proyecto:** (a) un informe escrito de **al menos 40 páginas** y (b) presentación PowerPoint con **demostración en vivo**.
- El informe debe explicar el problema abordado, la arquitectura y diseño, **cómo se implementó**, cómo se verificó y qué resultados se observaron. Redacción académica propia del grupo, ordenada, sin repeticiones, con afirmaciones sustentadas y figuras contextualizadas; mantener APA 7 en citas y referencias según plantilla institucional.
- **Orden del informe:** 1 Portada; 2 Introducción; 3 Objetivos; 4 Planteamiento del problema; 5 Fundamento técnico; 6 Diseño de la solución; 7 Implementación; 8 Pruebas y validación; 9 Análisis de resultados; 10 Conclusiones y recomendaciones; 11 Referencias; 12 Anexos.
- Portada incluye universidad, facultad, carrera, asignatura, título, profesor, fecha y nombres/cédulas de integrantes; datos personales solo en el archivo institucional bajo control del equipo, **NO registrar cédulas en GitHub**.
- El título debe describir la **acción técnica, solución y finalidad**, sin ser genérico.
- Introducción: contexto→problema/relevancia→solución, no comandos.
- Objetivos: verbos en infinitivo, medibles y relacionados con pruebas finales.
- Planteamiento: necesidad, impacto/consecuencia y justificación de tecnología elegida.
- Fundamento: estándares, conceptos y herramientas realmente usados, con selección justificada; no copia extensa de definiciones ni historia ajena al proyecto.
- Diseño: topologías física/lógica según pertinencia, sedes, roles, VLAN/subredes, WAN, servicios, flujos, automatización/NOC, interacción entre componentes, distinción diseño/prototipo/despliegue.
- Implementación: recursos host/VM, sistema operativo y versiones verificadas, secuencia ordenada, configuraciones principales, scripts y automatizaciones explicadas. **Una imagen sin interpretación técnica NO acredita comprensión**.
- Pruebas: indicar propósito, condiciones, baseline, comportamiento esperado, resultado observado, evidencia y recuperación.
- Análisis: interpretar resultados, limitaciones, incidentes técnicos reales y mitigaciones. Las conjeturas no se presentan como causas probadas.
- Conclusiones: objetivos demostrados; recomendaciones: ampliaciones o mejoras futuras realistas.
- Referencias: preferencia por documentación oficial/estándares/artículos fiables, con citas usadas en el cuerpo.
- Anexos: scripts completos, configuraciones, salidas extensas, dataset y otros artefactos realmente utilizados.

## Entrega del título (prioridad inmediata)

- El grupo debe **enviar al chat de Teams** de la asignatura el título propuesto para revisión de la profesora. La indicación oral fue reiterada el 16/10/2026. **No está verificado** que el grupo NETLAB360 ya lo haya enviado ni que el título haya sido aprobado.
- La docente indicó que revisaría lo recibido y comunicaría eventuales ajustes del **título** durante el fin de semana o el lunes siguiente. Mantener título formal propuesto **sujeto a su respuesta**, no alterar plataforma/nombre interno por una sugerencia editorial.

## Entregas parciales del proyecto (fecha y alcance definidos)

| Fecha | Trabajo grupal a presentar | Modalidad |
|---|---|---|
| **30/10/2026** | Borrador de **introducción, objetivo general, objetivos específicos y planteamiento del problema** | **Mostrar documento en Teams**, no visita física ni diapositivas; un representante asignado por el grupo |
| **13/11/2026** | Borrador de **fundamento técnico y diseño de la solución** | Continuidad del mismo documento, siguiendo indicaciones publicadas en Teams/campus |

- **Representante del grupo:** debe designarse previamente y tener acceso al borrador vigente.
- La presentación del 30/10 exige **mostrar el documento**, no preparar exposición PowerPoint adicional. Si la plataforma de entrega pide adjuntar un archivo, comprobar allí el formato antes de subir; la reunión no fijó una extensión informática obligatoria para esas dos revisiones.
- Estas son **revisiones parciales**, NO fecha final confirmada del informe o de la demostración semestral.

## Anexos como archivo independiente — decisión resuelta

- Se preguntó expresamente si el código y los artefactos pueden presentarse en un archivo aparte. **La docente respondió que sí, junto con el informe.** Se acepta preparar ZIP de anexos técnicos para NETLAB360.
- ZIP debe contener exclusivamente archivos **del proyecto** realmente utilizados o necesarios para reproducirlo, con README, estructura por tipo, manifiesto SHA256 de los artefactos del proyecto, sin secretos/tokens/llaves privadas ni archivos personales/de clase.
- La modalidad concreta de carga, peso máximo y si se solicita algún índice de anexos dentro del informe deben confirmarse en la plataforma de entrega; no extrapolar límites del parcial al semestral.
- No trasladar el texto integral de código al informe; describir lógica, principales parámetros, resultados y vínculo a anexos.

## Presentación y demostración final

- PowerPoint **derivado del informe**: portada/título y finalidad, introducción, objetivos, problema, diseño/arquitectura, demostración, conclusiones y referencias principales (la docente mencionó como ejemplos 5, 6 o 10 referencias en diapositivas, no un número fijo obligatorio).
- Incluir topología física y lógica si tiene sentido, funciones de los componentes, interacciones y pruebas representativas.
- **Demostración en vivo, directamente desde el entorno desarrollado** (puede ser VM local o nube). Validar realmente escenarios de estado inicial→falla controlada→resultado observado→restauración. Capturas no sustituyen ejecución viva.
- PPT se prepara **después de consolidar el informe**; desde ahora se diseñan ensayos estables y un procedimiento de recuperación para proteger la gestión `ens33`/VMnet8.

## Separación del Parcial 1 (NO es el semestral)

- El Parcial 1 se desarrolla **individualmente** y en **otro chat**, separado de este repositorio de NETLAB360.
- Tiene plazo comunicado **25/10/2026** y también constituye **Laboratorio 5**: **una sola entrega en espacio del parcial**, pero dos notas. No duplicar entrega.
- Su caso de degradación WAN, OSPF, Docker, Kubernetes, observabilidad, mediciones normal/degradado/recuperado y dataset sirve **solo como referencia técnica de complejidad** para planificar NETLAB360; no copiar requisitos del parcial como obligación académica del proyecto final.
- El proyecto semestral puede incorporar ideas adicionales **solo** si se implementan/validan en la plataforma propia.

## Dudas que continúan abiertas

- Fecha final de entrega del informe y exposición, tiempo máximo/minimo de presentación y rúbrica de ponderación detallada.
- ¿Se exige entregar/exportar una OVA? No hay confirmación afirmativa en indicaciones revisadas; demostrar en vivo sí es obligatorio.
- Tamaño máximo de anexos, ubicación de subida para el proyecto final y quién presenta la defensa final.
- Estado de revisión/aprobación del título por la profesora.
- Extensión exacta de cómputo de las 40 páginas (preliminares y anexos); la instrucción «mínimo 40» sí está confirmada.

**Regla de confidencialidad y trazabilidad:** copiar únicamente decisiones de trabajo que afectan el proyecto, nunca material docente original ni transcripción textual con nombres y conversaciones ajenas.