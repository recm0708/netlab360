# Entrenamiento y congelación de modelos V2 — Fase 06

## Prerregistro y entradas
El estudio V2 ya obtuvo, con fuente independiente de la etiqueta, **40 NORMAL, 8 DEGRADED y 12 RECOVERY por ruta**, todas con exactamente tres paquetes ICMP por ventana. Dos tokens de eventos distintos fueron activados con aprobación humana, restaurados de forma autónoma por watchdog y terminados en qdisc `noqueue` y guardia `NONE/BASELINE`. La carpeta de datos es `~/netlab360-bootstrap/s06/estudio-uniforme-v2`, su índice de sesiones `TRAIN_Manifest.json` y el origen de controles `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T150227Z_b399ae/manifest.json`.

Los identificadores NORMAL TRAIN que deben permanecer fijos son:

- `S06_WINDOW_NORMAL_20261123T143842Z_1e1812`
- `S06_WINDOW_NORMAL_20261123T143913Z_b5d57c`

**El acta legacy S06-050 sigue bloqueada y no se modifica.** No se reinterpreta el TEST histórico, no se usan observaciones VAL/TEST como entrenamiento y el alcance es exclusivamente el egreso HQ.

## Validaciones de entrada

`scripts/s06/entrenar_y_congelar_v2.py` realiza **una única operación de entrenamiento** (`--freeze`) y una verificación posterior sin reentrenamiento (`--check`). Antes de ajustar modelos comprueba:

- identidad y cronología de sesiones NORMAL/DEGRADED/RECOVERY, sin duplicados ni sustituciones;
- exactamente 40 NORMAL, 8 DEGRADED y 12 RECOVERY por ruta; ninguna pérdida y metadatos de tres paquetes realmente enviados y recibidos;
- dos eventos `complete` con tokens distintos, aprobación humana, objetivo exclusivo `nl360-s02-h-hq-120/eth0`, y archivo de watchdog en estado `RESTORED` por evento;
- validadores originales de las etiquetas independientes de las medidas RTT y el acta legacy S06-050 original sin modificaciones;
- separación de datos y ubicación privada, sin cargar modelos legacy.

La configuración de modelos es la preregistrada: regla P95 del RTT promedio de NORMAL TRAIN, IsolationForest con `n_estimators=100`, `contamination=0.05`, `random_state=42`, `n_jobs=1`, y LogisticRegression con `StandardScaler`, `class_weight=balanced`, `max_iter=1500` y `random_state=42`. Cada ruta tiene un IsolationForest, una regresión logística y un umbral P95; hay **cuatro archivos de modelo** y dos umbrales. El ajuste de los clasificadores usa NORMAL y DEGRADED **solo TRAIN**; RECOVERY se conserva como fuente excluida del ajuste.

## Artefactos de salida

La ejecución `--freeze` crea una sola carpeta privada `~/netlab360-bootstrap/s06/estudio-uniforme-v2/modelos-v2/` con cuatro `.joblib` y `S06_V2_Training_Freeze.json`, permisos 0700/0600 y huellas de contenido por modelo. El archivo informa `training_complete=true`, `validation_data_used=false`, `test_data_used=false`, `independent_test_completed=false`, `generalization_demonstrated=false`, `forecast_horizon_defined=false` y prohibición de despliegue operacional. `--check` comprueba fuente original/modelos contra el acta, sin crear otros artefactos.

El entrenamiento excluye VALIDATION y TEST. La evaluación posterior utiliza sesiones nuevas y separadas cronológicamente.

## Seguridad y validación

El módulo de entrenamiento no dispone de funciones para ejecutar ping, `sudo`, modificar qdisc, OSPF, LACP/SDN, Docker o systemd. Si falla la validación de procedencia **no crea modelos**; si se produce una escritura parcial, aborta y exige inspección, sin eliminar archivos ni reintentar `--freeze` sobre la carpeta. No copiar al repositorio modelos privados o informes con rutas personales.

La verificación de integridad es de solo lectura. Los modelos históricos permanecen independientes.

## Resultados

TRAIN se obtuvo con 60 ventanas por ruta (40 NORMAL, 8 DEGRADED y 12 RECOVERY), tres paquetes por ventana, dos eventos verificados y retorno autónomo. Se congelaron los cuatro modelos V2 antes de VALIDATION y TEST; umbrales P95 HQ→S1 0,10405 ms y HQ→S2 0,11055 ms. La evaluación cronológica posterior se efectuó sin ajustar parámetros. [Evaluación V2](s06-v2-evaluacion-cronologica-congelada.md).
