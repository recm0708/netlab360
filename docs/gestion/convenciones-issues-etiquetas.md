# Convenciones de issues, etiquetas y tipos de GitHub

## Descripción

El repositorio utiliza issues y milestones para gestionar capacidades, validaciones y entregables. Los campos de GitHub representan el estado; los títulos describen el objetivo.

## Títulos y clasificación

- Issues: `[SNN] Descripción concreta de la capacidad o actividad`, en español y con términos técnicos originales cuando corresponda.
- PR: título descriptivo con el código de la fase correspondiente.
- Etiquetas: una `fase:NN`, una clasificación temática `tipo:<dominio>` y, solo cuando corresponda, `alcance:opcional`, `prioridad:alta` o `estado:bloqueado`.
- Type nativo: `Feature` para una capacidad, `Task` para una actividad y `Bug` para un defecto. Es independiente de la etiqueta temática y no se asigna a PR.

No incorporar estados como CERRADA o PENDIENTE en los títulos. Las etiquetas deben conservar su significado y descripción en español; los tipos nativos conservan sus nombres oficiales.

## Validación y mantenimiento

Las herramientas [normalización de issues](../../scripts/operacion/normalizar_issues_etiquetas.py), [auditoría de títulos PR](../../scripts/operacion/auditar_titulos_prs.py) y [reconciliación de milestones](../../scripts/operacion/reconciliar_milestones_netlab360.py) permiten comprobar convenciones y diagnosticar inconsistencias. Los procedimientos de migración histórica no deben repetirse sobre un catálogo ya normalizado; antes de aplicar cambios se requiere revisar su alcance, inventario vigente y referencias.

Una etiqueta desconocida requiere revisión; no se borra por inferencia ni por falta de uso aparente. Una migración debe conservar las asignaciones de issues y PR y los campos no afectados. No cerrar una issue con criterios pendientes.

## Estado de aceptación

La normalización de títulos, etiquetas y tipos nativos fue verificada. El último inventario de clasificación registrado comprende 62 issues reales (34 Feature, 27 Task, una Bug), sin tipos faltantes. Los estados, criterios y milestones se consultan directamente en GitHub.

## Documentación relacionada

[Gestión de milestones](s01-s08-hitos-descripciones-y-contador-s05.md) · [Convenciones del proyecto](../../.github/CONTRIBUTING.md).
