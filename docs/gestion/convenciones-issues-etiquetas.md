# Convenciones de issues, pull requests y metadatos de GitHub

## Descripción

Utilizamos issues, pull requests y milestones para gestionar capacidades, validaciones y entregables. Los campos de GitHub representan el estado; los títulos describen el objetivo.

## Títulos y clasificación

- Issues: `[SNN] Descripción concreta de la capacidad o actividad`, en español y con términos técnicos originales cuando corresponda.
- PR: título descriptivo con el código de la fase correspondiente.
- Etiquetas: una clasificación temática `tipo:<dominio>`, las etiquetas `fase:NN` que correspondan al alcance real y, solo cuando proceda, `alcance:opcional`, `prioridad:alta` o `estado:bloqueado`.
- Type nativo: `Feature` para una capacidad, `Task` para una actividad y `Bug` para un defecto. Es independiente de la etiqueta temática y no se asigna a PR.

No incorporar estados como CERRADA o PENDIENTE en los títulos. Las etiquetas deben conservar su significado y descripción en español; los tipos nativos conservan sus nombres oficiales.

## Metadatos obligatorios de pull requests

Cada PR, independientemente de su estado, debe tener al menos una etiqueta temática `tipo:<dominio>` y un responsable en Assignees. Los títulos `[SNN]` requieren su etiqueta de fase correspondiente; incorporamos etiquetas de otras fases únicamente cuando el alcance lo justifica. El prefijo `[GESTIÓN]` identifica cambios transversales o generales y permite prescindir de etiquetas de fase cuando no corresponden. Asignamos un milestone solo si existe un hito principal de aceptación inequívoco; si el cambio abarca varias fases sin un hito principal, dejamos ese campo vacío. Un milestone existente debe corresponder a una etiqueta de fase válida y a una aceptación documentada. Revisamos la pertinencia histórica a partir del propósito, los archivos modificados, las issues relacionadas y las validaciones, sin eliminar ni asignar hitos automáticamente por el número de etiquetas. No creamos fases ficticias ni reabrimos milestones solo para completar metadatos.

Antes de fusionar verificamos los metadatos y las comprobaciones CI; el mantenimiento histórico conserva títulos, estados, autores, cuerpo y criterios no afectados. Consultamos los valores vigentes en GitHub, no en contadores duplicados en documentos.


Denominamos los hitos de GitHub «Fase 1» a «Fase 8», conservando sus identificadores numéricos y asignaciones. En la documentación técnica utilizamos «Fase 01» y sucesivas. Los códigos de los ensayos, prefijos técnicos, rutas y registros originales mantienen su nomenclatura.

## Validación y mantenimiento

Las herramientas [normalización de issues](../../scripts/operacion/normalizar_issues_etiquetas.py), [auditoría de títulos PR](../../scripts/operacion/auditar_titulos_prs.py) y [auditoría de metadatos PR](../../scripts/operacion/auditar_metadatos_prs.py), además de [reconciliación de milestones](../../scripts/operacion/reconciliar_milestones_netlab360.py) permiten comprobar convenciones y diagnosticar inconsistencias. Los procedimientos de migración histórica no deben repetirse sobre un catálogo ya normalizado; antes de aplicar cambios se requiere revisar su alcance, inventario vigente y referencias.

Una etiqueta desconocida requiere revisión; no se borra por inferencia ni por falta de uso aparente. Una migración debe conservar las asignaciones de issues y PR y los campos no afectados. No cerrar una issue con criterios pendientes.

## Estado de aceptación

La normalización de títulos, etiquetas y tipos nativos fue verificada. El último inventario de clasificación registrado comprende 62 issues reales (34 Feature, 27 Task, una Bug), sin tipos faltantes. Los estados, criterios y milestones se consultan directamente en GitHub.

## Documentación relacionada

[Gestión de milestones](gestion-milestones-s01-s08.md) · [Convenciones del proyecto](../../.github/CONTRIBUTING.md).
