# Evidencias fotográficas del proyecto

Conservamos en este directorio únicamente las capturas **versionadas y verificadas** de los ensayos de NETLAB360. Se seleccionan para sustentar el informe y la demostración; no incorporamos capturas rutinarias de administración SSH, firmware ni salidas duplicadas.

| Fase | Imágenes PNG | Índice |
|---|---:|---|
| S01 | 83 | [Laboratorio inicial](fase1/README.md) |
| S02 | 9 | [Red multisede](fase2/README.md) |
| S03 | 8 | [Automatización](fase3/README.md) |
| S04 | 22 | [Observabilidad](fase4/README.md) |
| **Total verificado** | **122** | |

Cada imagen cuenta con una entrada de procedencia en [`evidencias/manifiestos/`](../manifiestos/). Verificamos ruta, tamaño y SHA-256 mediante [`validar-capturas-unificadas.py`](../../scripts/validacion/validar-capturas-unificadas.py). **No renombramos ni eliminamos imágenes respaldadas por manifiestos sin actualizar y probar el control de integridad.**

Para S05–S08 reservamos directorios de evidencia vacíos hasta contar con ejecuciones reales. El ciclo GitOps S03 se documenta en [un registro Markdown](../../docs/evidencias/S03_09_GitOps_CI_Regresion_PullRequest.md), no como una novena PNG.
