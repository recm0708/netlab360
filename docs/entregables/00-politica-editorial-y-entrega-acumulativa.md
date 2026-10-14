# NETLAB360 — Política editorial vigente: DOS documentos únicos acumulativos

**Fecha de decisión:** 14/10/2026. **Fuente:** instrucciones directas del usuario. **Estado:** estructura APROBADA por el usuario el 14/10/2026 como línea base editorial, sujeta a cualquier indicación posterior de la profesora. Pendiente de empezar redacción hasta la orden del usuario. **Portadas:** las confecciona el usuario usando su formato institucional. No emitir documentos Word por iniciativa propia.

## 1. Entregables finales: exactamente dos documentos

| Nº | Documento único | Función |
|---|---|---|
| 01 | **Diseño, desarrollo y evaluación del proyecto NETLAB360** | Investigación y memoria académica del proyecto: problema, justificación, objetivos, bases teóricas, metodología, arquitectura, decisiones, desarrollo, resultados e incidentes técnicos REALES y su mitigación, discusión, recomendaciones, conclusiones y bibliografía |
| 02 | **Manual técnico integral de implementación, administración y uso de NETLAB360** | Reproducción de la plataforma desde cero; VM, SO, dependencias, instalación, configuración, scripts, comandos comprobados, salidas esperadas, pruebas, capturas, funciones de usuario, monitoreo, operación, recuperación, seguridad y mantenimiento |

**El antiguo Documento 03 de manual de usuario deja de existir como entregable independiente**. Su contenido funcional se incorpora al 02. No generar 16 ni 24 informes por semana; al final habrá **un Documento 01 y un Documento 02** que consolidarán las fases realmente completadas.

## 2. Período de cobertura y honestidad del cierre

La planificación técnica interna original contempla S01–S08, pero el usuario podrá fijar el corte efectivo del trabajo académico en la última fase realmente implementada (p. ej. S06 si ese fuera el avance logrado). Las versiones finales describirán coherentemente **el alcance efectivamente ejecutado y verificado** hasta ese corte, sin capítulos vacíos titulados «fases que faltaron» ni repetir la planificación inconclusa dentro de la narrativa académica.

**No afirmar que el proyecto siempre fue planeado para seis semanas si el repositorio demuestra ocho, ni ocultar requisitos oficiales no satisfechos.** Distinguir lo planeado del alcance final realmente entregado cuando sea necesario académicamente. Los compromisos docentes no se modifican sin aceptación. GitHub puede preservar el roadmap S01–S08, cancelaciones o alcance reducido como historial de gestión interno. No inventar funciones, resultados o cierres.

En este momento S01 sigue **ABIERTA (72/100 técnico estimado)** según matriz interna, con guía/rúbrica oficial pendiente. Por instrucción del usuario, no avanzar a S02 hasta cerrar la parte técnica exigible de S01 y tener redactada/revisada la parte S01 de ambos documentos.

## 3. Ubicación editorial de incidentes y mitigaciones

**Documento 01 — incidentes técnicos que realmente ocurrieron:** presentarlos en el capítulo del desarrollo, dentro de la subsección de la fase/componente afectado o en un apartado local «Incidentes técnicos y medidas de mitigación»; relatar el síntoma observado, contexto, causa confirmada o hipótesis identificada como tal, efecto, corrección/medida y verificación de resolución. Incluir únicamente incompatibilidades, fallos de infraestructura, limitaciones reales de software/entorno o incidencias técnicas relevantes para comprender decisiones y resultados. No narrar descuidos personales, comandos introducidos incorrectamente ni pasos saltados por el operador. No crear un anexo general de errores históricos.

**Documento 02 — guía limpia, corregida y reproducible:** no reconstruir el historial de errores realmente sufridos por el equipo. Presentar desde cero el procedimiento correcto y comprobado; al lado de la sección pertinente incluir «Problemas posibles y acciones correctivas», síntoma, causas posibles y ruta segura de diagnóstico/mitigación. Diferenciar remedios ya validados de recomendaciones aún no probadas; no introducir comandos peligrosos, eliminación global de recursos, cambios sobre ens33/VMnet8 ni secuencias no verificadas como si funcionaran. Si un fallo real motivó una solución, mostrar sólo la versión final estable en el flujo de instalación. Incluye uso cotidiano y operaciones de interfaz/CLI, no otro manual aparte.

## 4. Redacción, voz y formato

**Documento 01:** voz académica que atribuya decisiones y trabajo al equipo («el equipo diseñó», «se implementó», «se verificó», «nuestro proyecto» cuando sea natural); evitar voz de un asistente artificial o repetir «los estudiantes». Lenguaje técnico, evidencia y análisis crítico. El objetivo general es único/global; objetivos específicos compatibles con todo el alcance efectivamente desarrollado. Una introducción, recomendaciones y conclusiones generales, actualizables al cierre.

**Documento 02:** tercera persona técnica impersonal y estilo normativo/operativo («se debe comprobar», «ejecute», «el sistema mostrará» cuando se haya verificado), uniforme como manual de empresa. Procedimientos exactos, objetivos, prerrequisitos, entradas, scripts, comandos válidos, resultados esperados y verificación observada; advertencias y reversión. No primera persona narrativa.

**En ambos:**
- Portadas confeccionadas por el usuario conforme a su plantilla.
- **UN índice general automático por documento**, mediante estilos Título 1/2/3; sin índices independientes por fase. Listas auxiliares de figuras/tablas solo si la institución exige.
- APA 7: citas autor-fecha de fuentes externas en texto, correspondencia con **UNA lista final de referencias** por documento, autoría/fecha/URL/DOI verificables; no fabricar referencias.
- Antes de **toda figura o tabla**, un preámbulo explicativo y llamada textual «Figura N» o «Tabla N». Rotulación con número, título y **Nota.** cuando fuente, método, autoría o aclaración lo requiera. Numeración continua por documento durante todas las fases.
- No inundar Word con los 86 PNG; seleccionar figuras probatorias y mantener el inventario original/manifiestos SHA-256 en GitHub.
- No compartir secretos, llaves SSH, tokens, credenciales ni archivos de estado privado de IaC.
- Documentar siempre distinción entre **implementado**, **probado**, **planeado**, **pendiente** y **no soportado**.

## 5. Fuentes y almacenamiento

- [01 — Índice maestro de investigación](01-proyecto-investigacion-maestro.md).
- [02 — Índice maestro técnico/uso](02-informe-tecnico-maestro.md).
- [Selección de figuras revisada para dos documentos](04-seleccion-figuras-y-tablas-s01.md).
- [Checklist de S01](s01/00-checklist-cierre-y-entrega.md).
- Archivos originales y código fuente: `inventario/`, `scripts/`, `servicios/`, `ansible/`, `iac/`, `tests/`.
- Capturas PNG directas: `evidencias/capturas/`; manifiestos hash: `evidencias/manifiestos/`.
- Registros históricos: `docs/sesiones/`, `docs/evidencias/`, `docs/decisiones/` y Git commits; **conservar trazabilidad** aun al limpiar índices/documentos obsoletos.
- Los borradores DOCX previos del 13/10 fueron rechazados por el usuario, no se reutilizarán como contenido final. El asistente entregará cada sección completa en chat y el usuario la copiará a su propio documento institucional Word.

## 6. Estado y próximas decisiones

- El usuario APROBÓ los dos índices como línea base de trabajo el 14/10/2026; si la profesora comunica nuevos requisitos se revisarán conservando trazabilidad.
- Luego comenzar por **Documento 01, Introducción**, y avanzar sección por sección según aprobaciones; desarrollar posteriormente Documento 02 en paralelo con las pruebas verificadas.
- No iniciar tareas técnicas nuevas ni S02 por impulso; solo pruebas de cierre S01 que la guía docente realmente exija.
- **Cierre académico final:** dos documentos consolidados que describen el proyecto hasta la última fase terminada, sin afirmar implementado lo no realizado. El estado interno histórico permanece en GitHub.
