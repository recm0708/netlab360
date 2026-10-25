# NETLAB360 — Política académica vigente tras guías oficiales (16/10/2026)

**Esta versión REV0.3 sustituye la decisión anterior de DOS informes entregables.** Fundamento: tres criterios docentes recibidos en la documentación técnica el 16/10 y decisión explícita del mismo. En caso de conflicto consultar [requisitos docentes](../academico/00-criterios-docentes-y-hitos.md). Las instrucciones orales ya están convertidas a criterios operativos sin publicar la transcripción. Las revisiones grupales del escrito están fechadas **30/10 y 13/11**; la demostración final será en vivo.

## Entrega principal obligatoria: UN solo informe escrito

[Índice vigente](01-proyecto-investigacion-maestro.md): 1 Portada; 2 Introducción; 3 Objetivos; 4 Planteamiento del problema (justificación integrada); 5 Fundamento técnico; 6 Diseño de la solución; 7 Implementación; 8 Pruebas y validación; 9 Análisis de resultados (incidentes reales/mitigación); 10 Conclusiones y recomendaciones; 11 Referencias; 12 Anexos. **Mínimo 40 páginas**. La portada la crea el usuario. Debe explicar cómo se realizó y verificó lo implementado, **no solo teoría**, ni copiar íntegramente scripts o outputs interminables.

El borrador anterior del Documento 01 tiene **65 páginas**, revisadas previamente en PDF institucional; requiere **reubicación según estructura docente y refuerzo** de implementación y pruebas. No se ha editado el Word del usuario por GitHub ni se considera entregado. La profesora puede precisar extensión y otros aspectos mediante transcripción futura.

## Entregas adicionales

- **PowerPoint y demostración técnica obligatorios**, diseñados **después** de cerrar el informe principal; los escenarios deben mostrar baseline, operación/falla y contraste esperado/real, con razonamiento técnico. [Plan](../academico/03-anexos-y-demostracion.md).
- **Anexos técnicos**: fuente de código completo, YAML, OpenTofu, Ansible, Python, scripts, configuraciones y salidas relevantes. Se permite un ZIP de anexos separado, junto al informe, con manifiesto de integridad y estructura interna; confirmar solo límites de tamaño y carga.
- [Documento 02 — manual técnico integral](02-informe-tecnico-maestro.md): **DIFERIDO para después del proyecto**; no es requerido en las tres guías y no bloquea S02, informe, demo ni entrega. Conservar issue #28 como proyecto futuro, sin crear contenido nuevo por ahora.

## Reglas editoriales

- Informe en voz académica del equipo, evidencias reales, no manipular resultados. APA7 híbrido con plantilla institucional; un solo índice automático, citas autor-año y bibliografía donde coincidan referencias y citas.
- Toda figura o tabla: preámbulo con mención en texto, numeración secuencial, título, **Nota.** cuando proceda; tamaño legible. Capturas solo representativas; archivo ZIP para código/extensiones, si se autoriza.
- **Incidentes técnicos reales y verificables** en sección 9 (causa cuando es comprobable, mitigación, verificación), vinculados a la implementación del punto 7. No incluir descuidos personales ni fallas artificiales como incidentes reales. En implementación se presentan configuraciones finales limpias.
- Título formal descriptivo de la plataforma en portada; encabezado corto `NETLAB360 | Redes Empresariales Multisede`. El alumno proporciona y edita Word institucional.
- Si el alcance final se recorta, se describe SOLO lo efectivamente implementado, sin capítulos de fases inexistentes ni falsificar cronología o requisitos docentes. Mantener trazabilidad en issues/commits.
- Registrar el estado «implementado/probado/pendiente» y no confundir reglas con IA entrenada, veth con NIC físicas ni subtopologías separadas con integración total.

## Prioridad de ejecución (revisada)

1. Comprobar envío del título a Teams y preparar con el grupo la revisión del **30/10** de Introducción, Objetivos y Planteamiento del problema.
2. **Retomar implementación técnica integrada S02** usando prácticas S01 probadas y la VM protegida; dejar la issue original S01 abierta por brechas sin usarla como bloqueo global.
3. Incorporar progresivamente contenido verificado al ÚNICO informe académico-técnico; reestructurar Word vigente con el mapa oficial.
4. Preparar anexos y verificación final; luego PPT+demo. Manual 02 después.

**No añadir páginas por rellenar: la calidad de las 40+ páginas depende de diseño, implementación, baseline, resultados, análisis y citas pertinentes.**
