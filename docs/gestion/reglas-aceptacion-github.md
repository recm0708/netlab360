# Reglas de aceptación y metadatos de GitHub

## Pull requests

Cada PR debe identificar su alcance, issues relacionadas, etiquetas pertinentes y al menos un responsable. La milestone es obligatoria si el alcance pertenece a un hito inequívoco; para trabajo transversal se documenta la ausencia de milestone. Las etiquetas de fase no sustituyen esta decisión.

La fusión requiere una lista de tareas completa, evidencia de las comprobaciones aplicables y CI satisfactoria sobre la revisión final. Las verificaciones omitidas deben justificarse. Un commit nuevo que afecte un criterio obliga a revalidarlo. No cerramos un PR como completado ni lo fusionamos con tareas pendientes o comprobaciones exigibles fallidas. Un PR abandonado se cierra sin afirmar que fue implementado, con motivo explícito.

## Issues

Toda issue debe tener título y alcance, criterios de aceptación, etiquetas, al menos un responsable, milestone y Type nativo. Task representa trabajo acotado o validación; Feature, funcionalidad nueva; Bug, defecto reproducible. Usamos los tipos disponibles en GitHub, no creamos tipos nuevos sin una decisión explícita. Las etiquetas tipo:* clasifican el dominio técnico y no sustituyen Type. El cierre como completada exige todos los criterios aplicables; duplicadas o descartadas conservan su motivo real mientras se revisa su depuración.

## Depuración del seguimiento

Eliminamos una issue duplicada únicamente después de identificar la original, trasladar los criterios o información vigente que falten y corregir las referencias activas. Eliminamos una actividad no planificada solo cuando el equipo confirma que queda definitivamente fuera del alcance; una actividad aplazada se conserva en su hito. Antes de la eliminación definitiva conservamos una copia privada fuera del repositorio y verificamos que no se pierdan tareas vigentes. Las issues completadas y los PR fusionados se conservan. No se reutilizan números ni se elimina documentación técnica propia de los componentes. La eliminación de una issue no equivale a completar sus criterios.

## Conciliación histórica

Conservamos estados, autores, commits, fechas, descripciones y resultados originales. Las tareas reconstruidas acreditan integración, no pruebas no documentadas. Una ejecución fallida no se convierte en satisfactoria por normalizar las tareas. Auditamos el fallo, conservamos su registro y documentamos la comprobación correctiva en una revisión posterior, sin reescribir el historial.

## Aplicación

Consultamos metadatos antes de fusionar o cerrar. La plantilla y la auditoría apoyan este procedimiento; no constituyen por sí solas un bloqueo de protección de ramas. Los resultados ambiguos se resuelven por alcance y evidencia, no por asignaciones masivas arbitrarias.
