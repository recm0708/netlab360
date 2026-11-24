# Evaluación cronológica V2 con modelos congelados — Fase 06

## Entradas y separación cronológica

TRAIN V2 real: 40 NORMAL, 8 DEGRADED, 12 RECOVERY por ruta con tres ICMP; dos eventos recuperados autónomamente. Cuatro modelos V2 congelados, reportados por `~/netlab360-bootstrap/s06/estudio-uniforme-v2/modelos-v2/S06_V2_Training_Freeze.json`, umbrales P95 RTT HQ→S1 0.10405 ms y HQ→S2 0.11055 ms. La VALIDATION se capturó **después** de la congelación: NORMAL `S06_WINDOW_NORMAL_20261123T151633Z_973a31` y batch `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T151706Z_e1ca29/manifest.json` con 20 NORMAL, 8 DEGRADED y 12 RECOVERY por ruta, nuevamente tres paquetes. Test V2 futuro sigue **sin adquirir**.

## Evaluador de solo lectura

`scripts/s06/evaluar_v2_congelado.py` admite `--stage validation|test --save`. Verifica los cuatro modelos congelados y sus huellas, el corpus TRAIN original y el índice `VALIDATION_Manifest.json` o `TEST_Manifest.json`. Exige sesiones nuevas con fecha posterior al freeze, **TEST posterior a toda VALIDATION**, eventos con tokens distintos de TRAIN y de VALIDATION, dos watchdog `RESTORED`, las mismas dos rutas, tres paquetes por ventana y 20 NORMAL/8 DEGRADED/12 RECOVERY.

Califica los mismos métodos P95 RTT, IsolationForest y LogisticRegression, **sin llamar `fit` ni cambiar umbrales**. Por ruta y método registra TP/FP/TN/FN, precision, recall, F1, especificidad, falsas alarmas RECOVERY y cantidad de ventanas detectadas por cada uno de los **dos eventos**. Incluye promedio/mediana RTT NORMAL por etapa como insumo para análisis descriptivo posterior de data drift, no como validación automática de concept drift. Prohíbe atribuir al sistema pronóstico anterior al evento, cobertura real de FAULT/OSPF, despliegue productivo o generalización fuera del estímulo artificial de latencia fija 40 ms.

La evaluación se conserva una sola vez: `~/netlab360-bootstrap/s06/estudio-uniforme-v2/evaluaciones-v2/validation.json` o `test.json`; no sobreescribir/recalificar para mejorar métricas. Si una evaluación falla, se conserva intacto el freeze, el corpus y la red. No se exige captura académica adicional antes de disponer de resultados comparables de TEST.

## Procedimiento de evaluación

1. CI aprobada, ejecutar 15 pruebas específicas de scoring offline y puntuar VALIDATION desde sus datos existentes; comprobar 2 eventos/20+8+12 por ruta y congelación íntegra.
2. Capturar una nueva sesión NORMAL TEST de 20 ventanas × 3 ICMP, **después de todos los eventos VALIDATION y del scoring previo**. Si ya existe registro, no recapturar.
3. Con aprobación literal humana separada y guardia/watchdog verificados, capturar dos eventos controlados TEST (4 DEGRADED+6 RECOVERY por ciclo), 3 ICMP, sin tocar `ens33`.
4. Confirmar manifest `TEST_Manifest.json`, tokens disjuntos de TRAIN/VALIDATION, cada watchdog restaurado y qdisc `noqueue`. Evaluar TEST **una sola vez**, sin ajustar modelos, reportar FP/FN y resultados por evento.
5. Data drift: comparar distribuciones de RTT NORMAL por ruta entre TRAIN, VALIDATION y TEST con muestreo 3 uniforme; concept drift se limita a variación de errores en TEST posterior por eventos (dos eventos/poco poder estadístico). Distinguir **latencia de detección después del estímulo** de pronóstico con horizonte futuro, que permanece `NO_EVALUABLE` sin objetivo temporal ni eventos suficientes.



## Resultados

**Evidencia real:** `S06_V2_TEST_CRONOLOGICO_COMPLETO=OK`, `RESULTADO_RC=0`; 14 tests específicos VM OK. Cuatro modelos V2 congelados e idénticos en ambas etapas, sin reentrenamiento ni cambios de umbral; modelos históricos preservados. Corpus de 3 paquetes ICMP por ventana y ruta: TRAIN 40 NORMAL/8 DEGRADED/12 RECOVERY, VALIDATION 20/8/12, TEST 20/8/12, con dos eventos nuevos por etapa. TEST NORMAL `S06_WINDOW_NORMAL_20261123T153501Z_4d1e6c`; batch TEST `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T153534Z_36ea51/manifest.json`.

**VALIDATION** (TP/FP/TN/FN/F1/FP RECOVERY):
- HQ→S1: P95 `8/0/20/0/1.000/0`, IsolationForest `8/1/19/0/0.941/1`, LogisticRegression `8/0/20/0/1.000/0`.
- HQ→S2: P95 `8/1/19/0/0.941/2`, IsolationForest `8/1/19/0/0.941/2`, LogisticRegression `8/0/20/0/1.000/0`.

**TEST** (TP/FP/TN/FN/F1/FP RECOVERY):
- HQ→S1: P95 `8/1/19/0/0.941/0`, IsolationForest `8/1/19/0/0.941/0`, LogisticRegression `8/0/20/0/1.000/0`.
- HQ→S2: P95 `8/0/20/0/1.000/0`, IsolationForest `8/1/19/0/0.941/0`, LogisticRegression `8/0/20/0/1.000/0`.

Los tres métodos tuvieron **0 FN en TEST** y detectaron al menos una ventana en cada uno de los dos eventos por ruta. Cada TEST tiene 20 negativos y solo ocho positivos por ruta; ambos destinos comparten estímulo y no son eventos independientes entre rutas. Los resultados son válidos para retardo artificial HQ de 40 ms, no prueban pronóstico, fallas OSPF/WAN/HA/LACP/SDN ni generalización a otros tipos de perturbación.

**RTT NORMAL medio (ms):** HQ→S1 TRAIN `0.0780`, VALIDATION `0.0798`, TEST `0.0799` (+0.0018 desde TRAIN); HQ→S2 TRAIN `0.0796`, VALIDATION `0.0849`, TEST `0.0752` (−0.0044 desde TRAIN). Estos cambios son observaciones descriptivas, no evidencia de concept drift ni deterioro demostrado.

**Seguridad:** watchdog restauró dos ciclos TEST (RTT degradado/recuperado 40.476/0.075 ms y 40.469/0.073 ms), controlador `NONE/BASELINE`, qdisc `noqueue`, 21 namespaces, 4 Docker, NOC saludable y cero mutaciones permanentes. Salidas privadas `~/netlab360-bootstrap/s06/estudio-uniforme-v2/evaluaciones-v2/validation.json` y `test.json`. Bitácora `~/netlab360-bootstrap/s06/estudio-uniforme-v2/validacion-test-20261123_103455/S06_V2_Evaluacion_Test_Completa.txt`. No recapturar ni reajustar tras TEST.

[Auditoría de deriva y detección](s06-v2-deriva-deteccion-y-limitaciones-finales.md) · [Escenario HTTP independiente](s06-fault-http-hq-etiquetado-independiente.md).
