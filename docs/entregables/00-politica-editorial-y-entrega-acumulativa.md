# NETLAB360 — Política documental acumulativa y estructura de entrega S01–S08

**Vigente desde:** 14/10/2026. **Naturaleza:** instrucción de trabajo del usuario, propuesta de índices todavía sujeta a aprobación y formato institucional. **NO es rúbrica docente ni declara S01 finalizada.**

## 1. Tres únicos documentos principales

Durante las ocho fases semanales se mantendrán **tres documentos maestros**, no tres documentos finales nuevos cada semana:

1. **Documento de investigación y desarrollo del proyecto**, identificado como 01.
2. **Informe técnico de implementación y laboratorios**, identificado como 02.
3. **Manual de usuario, administración y operación de NETLAB360**, identificado como 03.

Cada uno posee portada institucional proporcionada por el usuario, **un único índice automático de contenido** mediante estilos de Word, paginación, numeración jerárquica, desarrollo gradual y una sección final de referencias cuando corresponda. Se entregarán los tres documentos completos al finalizar las ocho fases; durante S01 se redacta exclusivamente lo demostrado/propuesto de esa fase, incorporando luego capítulos S02–S08 a **los mismos maestros**. Archivos Markdown de índice y control en GitHub no son sustitutos de los Word institucionales.

**Los borradores Word y Markdown V0.1 del 13/10 fueron rechazados por el usuario como base editorial final**. Deben considerarse histórico descartado; no reciclar sus índices o maquetación como formato aprobado. No generar nuevos Word automáticamente: el asistente entregará texto **sección por sección** para que el usuario lo copie en su propia plantilla institucional, y sólo cuando lo solicite se convertirán los maestros a archivos.

## 2. Reglas académicas y APA 7

- **Un solo índice de contenido automático** por documento, con Título 1/2/3, sin repetir índices por fase. No crear lista de figuras/tablas como segundo índice salvo que la institución lo exija.
- Para **cada figura o tabla**, redactar antes uno o más párrafos de contexto o preámbulo que expliquen por qué se muestra y qué demuestra; referirse expresamente a su número. Poner número y título según APA 7, y debajo la **Nota.** cuando haga falta aclarar alcance, fuente, abreviaturas, adaptación, autoría o límites. No colocar imágenes decorativas ni tablas sin interpretación técnica.
- Citas autor-fecha dentro del texto del documento 01 y referencias completas, verificadas, en la **única lista final**. Evitar obras, fechas, DOI, normas o páginas inventadas. Distinguir fuentes oficiales de referencias internas de GitHub. En bitácora/manual, citar fuentes externas si se hacen afirmaciones técnicas basadas en terceros.
- Uso de fuentes primarias: comandos, terminales, hashes, commit, versiones, fotografías, logs, CI. **Nunca** declarar ejecutado algo solo porque el script existe. Marcar como planeado, ejecutado y verificado, o pendiente. Las 76 ICMP pertenecen a un ensayo; 12 eventos JSONL a otros, no sumarlos como filas de entrenamiento.
- No divulgar secretos, contraseñas, claves, token GH, estado Terraform con secretos o identificadores privados en PDF, Word o capturas.
- Los objetivos, conclusiones y recomendaciones generales se actualizarán acumulativamente al final del semestre, sin abrir ocho introducciones ni ocho bibliografías.

## 3. Reparto de contenido, sin duplicación

**Documento 01 (qué, por qué, fundamentos, diseño y resultados):** problema, justificación, objetivos, alcance, metodología, arquitectura, decisiones técnicas, análisis de resultados, discusión y fundamentos teóricos con referencias.

**Documento 02 (qué se hizo exactamente y cómo se demostró):** infraestructura, topologías efectivas, versiones, comandos completos pertinentes, archivos configurados, prechecks, ejecución secuencial, resultados realmente observados, pruebas positivas/negativas, evidencias, rollback, integridad y reproducibilidad. Registros extensos irán a anexos sólo si aportan valor.

**Documento 03 (cómo usar el producto):** requisitos, acceso, interfaz gráfica y CLI, inicio/parada, funciones por sede, paneles, alertas, simulación de falla segura, interpretación de estados, resolución de problemas, respaldo y mantenimiento. No copiar como manual los scripts de implementación ni documentar funciones todavía inexistentes como disponibles.

## 4. Estructura y trazabilidad

Propuestas de índices maestros:
- [01 — Proyecto](01-proyecto-investigacion-maestro.md)
- [02 — Informe técnico](02-informe-tecnico-maestro.md)
- [03 — Manual de usuario](03-manual-usuario-maestro.md)

Carpetas existentes se conservan por función:
- **inventario/**, **topologias/**, **iac/**, **ansible/**, **scripts/**, **servicios/** y **tests/**: código y fuente real.
- **evidencias/capturas/**: únicamente PNG planos, nombres únicos; **evidencias/manifiestos/**: hash e inventario.
- **docs/sesiones/**, **docs/evidencias/**, **docs/decisiones/**: historial fuente inmutable de pruebas, auditorías y decisiones.
- **docs/control/** y **backlog/**: aceptación y seguimiento interno; no se convierten en capítulos de documentos.
- **docs/entregables/**: índices maestros y política editorial; **docs/entregables/s01/**: checklist fase y enlaces históricos, no 3 entregas paralelas.

## 5. Condición de avance a S02

El usuario ha ordenado **no avanzar a S02** hasta dejar listos los documentos correspondientes a S01 y resolver su cierre técnico. Aunque se dispone de subpruebas B0–B4 funcionales, S01 sigue ABIERTA por los criterios existentes y sólo puede declararse cerrada tras contrastar la guía docente o aceptación de alcance modificada: integración L2↔WAN, redundancia de equipo, NOC/alertas y IA evaluable cuando exigibles, release/OVA verificados si corresponden y documentos finales. La cifra actual de 72/100 es una ponderación **interna** no equivalente a aprobación.

**Prioridad actual:** acordar índices con el usuario, escribir el documento 01 empezando por introducción, luego secciones consecutivas; avanzar en paralelo con los otros dos maestros y confirmar rúbrica oficial sin detener la redacción. **Un bloque sustancial de texto por turno**, sin reanudar desarrollo B4/AIOps en esta etapa.
