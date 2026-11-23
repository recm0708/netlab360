# NETLAB360 — Auditoría y reconciliación de milestones S01–S08

## Observación verificada en GitHub

El 23/11/2026 la API devuelve **S05 cerrada con contador 6 open / 1 closed**, aunque la consulta de sus issues asignadas y sus estados confirma **seis cerradas y cero abiertas** (#5, #23, #31, #32, #64, #105). Todas estas issues tienen criterios marcados como cumplidos y están cerradas como `completed`. Los contadores almacenados de la milestone no reflejan la realidad; no se debe fingir que tareas están abiertas ni reabrirlas para modificar un porcentaje.

La antigua issue [#24](https://github.com/recm0708/netlab360/issues/24) describía una propuesta de **cuarta sede/WireGuard no implementada**, cerrada correctamente como `not planned` en S05. Se reabrió, actualizó y movió a **S08**, con casillas nuevas **sin marcar** para decidir la ampliación cuando haya necesidad justificada. S05 no incluye ni requiere esa funcionalidad. S08 la considera una opción y no un entregable obligatorio aprobado por la docente.

Las ocho descripciones de milestones en GitHub estaban obsoletas o eran demasiado vagas: S01–S04 solo indicaban el cierre, y S05–S08 mostraban estados desactualizados. Se redactaron textos normalizados para cada una, con secciones **Propósito**, **Alcance y entregables**, **Criterio de aceptación** y **Estado**. Las descripciones están incorporadas como fuente editable en `scripts/operacion/reconciliar_milestones_netlab360.py`.

## Ejecución y seguridad

Los conectores de GitHub utilizados para esta auditoría permiten editar issues, pero **no exponen una acción de modificación de milestones**. Las ocho descripciones y el contador S05 deben aplicarse una sola vez por el operador usando `gh api` ya autenticado en la VM. No se almacena ni transmite un token; `gh` utiliza su autenticación existente.

El script ofrece dos modos:

- `--check`: GET de las ocho milestones, inventario de las seis issues S05 y verificación de #24 en S08; imprime diferencias sin modificar GitHub.
- `--apply`: modifica exclusivamente las ocho **descripciones** vía GitHub API conservando título, fecha, estado y dueños. Si el contador S05 sigue erróneo, aplica **un solo intento de recálculo**: retira temporalmente la asignación de la issue cerrada #5 y la restaura inmediatamente como S05, sin tocar estado, cuerpo ni checkbox. Verifica los seis estados cerrados y la asignación final. Si persiste la inconsistencia, informa `AUN_DESINCRONIZADO_REQUIERE_SOPORTE_GITHUB` sin repetir operaciones ni reclamar éxito de porcentaje.

El script aborta ante una nueva issue abierta en S05, un PR asignado inesperadamente, una cuarta sede realmente desplegada no documentada, un cambio de estado de milestone o si #24 deja de estar abierta en S08. Nunca reabre S01–S05 ni cierra S06–S08.

## Estado técnico por fase

| Milestone | Estado esperado | Criterio central |
|---|---|---|
| S01 | Cerrada | VM, IPAM, SSH, documentación y línea base |
| S02 | Cerrada | Tres sedes, FRR/OSPF, cuatro WAN, nueve VLAN, failover |
| S03 | Cerrada | SoT/Ansible/OpenTofu `terraform_data` y CI |
| S04 | Cerrada | Prometheus, observabilidad, incidentes y SLI/SLO experimentales |
| S05 | Cerrada | HA HTTP, LACP multisede, SDN, NOC y 71 PNG; sin cuarta sede |
| S06 | Abierta, ~90 % técnico estimado | TRAIN/VALIDATION/TEST V2 aprobados; resta FAULT independiente, cierre/figuras y redacción; pronóstico no evaluable sin horizonte |
| S07 | Abierta | AIOps supervisado y reversión autorizada |
| S08 | Abierta | Consola unificada, regresión, TAR, informe, presentación; ampliaciones solo condicionales |

**La barra de GitHub cuenta issues cerradas sobre issues asignadas; no mide automáticamente el avance técnico S06.** No marcar 90 % como completitud de su milestone.

## Criterio de aceptación de la operación

`MILESTONES_NETLAB360_RECONCILIADAS=OK`, las ocho descripciones cotejadas, issue #24 abierta en S08, seis issues S05 cerradas y ninguna abierta, fases S01–S05 cerradas y S06–S08 abiertas. El porcentaje nativo de S05 debe resultar 100 %; si GitHub mantiene contadores inconsistentes pese a la reasignación, conservar la evidencia y acudir a soporte de GitHub, **sin manipular checkboxes ni reaperturas**.

En el mismo bloque de terminal, después de los cambios de hitos, ejecutar las comprobaciones S06 de modelos V2, controlador `NONE/BASELINE`, qdisc `noqueue`, 21 namespaces, cuatro contenedores y NOC. Eso no reejecuta experimentos; el siguiente gate S06 es decidir qué falla distinta puede etiquetarse como FAULT sin afectar el host de administración.
