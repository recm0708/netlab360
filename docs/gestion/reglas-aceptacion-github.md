# Reglas de aceptación y metadatos de GitHub

## Pull requests

Cada PR debe identificar su alcance, issues relacionadas, etiquetas pertinentes y al menos un responsable. La milestone es obligatoria si el alcance pertenece a un hito inequívoco; para trabajo transversal se documenta la ausencia de milestone. Las etiquetas de fase no sustituyen esta decisión.

La fusión requiere una lista de tareas completa, evidencia de las comprobaciones aplicables y CI satisfactoria sobre la revisión final. Las verificaciones omitidas deben justificarse. Un commit nuevo que afecte un criterio obliga a revalidarlo. No cerramos un PR como completado ni lo fusionamos con tareas pendientes o comprobaciones exigibles fallidas. Un PR abandonado se cierra sin afirmar que fue implementado, con motivo explícito.

## Issues

Toda issue debe tener título y alcance, criterios de aceptación, etiquetas, al menos un responsable, milestone y Type nativo. Task representa trabajo acotado o validación; Feature, funcionalidad nueva; Bug, defecto reproducible. Usamos los tipos disponibles en GitHub, no creamos tipos nuevos sin una decisión explícita. Las etiquetas tipo:* clasifican el dominio técnico y no sustituyen Type. El cierre como completada exige todos los criterios aplicables; duplicadas o descartadas conservan su motivo real.

## Conciliación histórica

Conservamos estados, autores, commits, fechas, descripciones y resultados originales. Las tareas reconstruidas acreditan integración, no pruebas no documentadas. Una ejecución fallida no se convierte en satisfactoria por normalizar las tareas. Auditamos el fallo, conservamos su registro y documentamos la comprobación correctiva en una revisión posterior, sin reescribir el historial.

## Aplicación

Consultamos metadatos antes de fusionar o cerrar. La plantilla y la auditoría apoyan este procedimiento; no constituyen por sí solas un bloqueo de protección de ramas. Los resultados ambiguos se resuelven por alcance y evidencia, no por asignaciones masivas arbitrarias.
