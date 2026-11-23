# S06 V2 — Evaluación cronológica con modelos congelados (VALIDATION y TEST)

## Entradas confirmadas y secuencia sin fuga

TRAIN V2 real: 40 NORMAL, 8 DEGRADED, 12 RECOVERY por ruta con tres ICMP; dos eventos recuperados autónomamente. Cuatro modelos V2 congelados, reportados por `~/netlab360-bootstrap/s06/estudio-uniforme-v2/modelos-v2/S06_V2_Training_Freeze.json`, umbrales P95 RTT HQ→S1 0.10405 ms y HQ→S2 0.11055 ms. La VALIDATION se capturó **después** de la congelación: NORMAL `S06_WINDOW_NORMAL_20261123T151633Z_973a31` y batch `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T151706Z_e1ca29/manifest.json` con 20 NORMAL, 8 DEGRADED y 12 RECOVERY por ruta, nuevamente tres paquetes. Test V2 futuro sigue **sin adquirir**.

## Evaluador read-only

`scripts/s06/evaluar_v2_congelado.py` admite `--stage validation|test --save`. Verifica los cuatro modelos congelados y sus huellas, el corpus TRAIN original y el índice `VALIDATION_Manifest.json` o `TEST_Manifest.json`. Exige sesiones nuevas con fecha posterior al freeze, **TEST posterior a toda VALIDATION**, eventos con tokens distintos de TRAIN y de VALIDATION, dos watchdog `RESTORED`, las mismas dos rutas, tres paquetes por ventana y 20 NORMAL/8 DEGRADED/12 RECOVERY.

Califica los mismos métodos P95 RTT, IsolationForest y LogisticRegression, **sin llamar `fit` ni cambiar umbrales**. Por ruta y método registra TP/FP/TN/FN, precision, recall, F1, especificidad, falsas alarmas RECOVERY y cantidad de ventanas detectadas por cada uno de los **dos eventos**. Incluye promedio/mediana RTT NORMAL por etapa como insumo para análisis descriptivo posterior de data drift, no como validación automática de concept drift. Prohíbe atribuir al sistema pronóstico anterior al evento, cobertura real de FAULT/OSPF, despliegue productivo o generalización fuera del estímulo artificial de latencia fija 40 ms.

La evaluación se conserva una sola vez: `~/netlab360-bootstrap/s06/estudio-uniforme-v2/evaluaciones-v2/validation.json` o `test.json`; no sobreescribir/recalificar para mejorar métricas. Si una evaluación falla, se conserva intacto el freeze, el corpus y la red. No se exige captura académica adicional antes de disponer de resultados comparables de TEST.

## Orden operativo

1. CI aprobada, ejecutar 15 pruebas específicas de scoring offline y puntuar VALIDATION desde sus datos existentes; comprobar 2 eventos/20+8+12 por ruta y congelación íntegra.
2. Capturar una nueva sesión NORMAL TEST de 20 ventanas × 3 ICMP, **después de todos los eventos VALIDATION y del scoring previo**. Si ya existe registro, no recapturar.
3. Con aprobación literal humana separada y guardia/watchdog verificados, capturar dos eventos controlados TEST (4 DEGRADED+6 RECOVERY por ciclo), 3 ICMP, sin tocar `ens33`.
4. Confirmar manifest `TEST_Manifest.json`, tokens disjuntos de TRAIN/VALIDATION, cada watchdog restaurado y qdisc `noqueue`. Evaluar TEST **una sola vez**, sin ajustar modelos, reportar FP/FN y resultados por evento.
5. Data drift: comparar distribuciones de RTT NORMAL por ruta entre TRAIN, VALIDATION y TEST con muestreo 3 uniforme; concept drift se limita a variación de errores en TEST posterior por eventos (dos eventos/poco poder estadístico). Distinguir **latencia de detección después del estímulo** de pronóstico con horizonte futuro, que permanece `NO_EVALUABLE` sin objetivo temporal ni eventos suficientes.

No cerrar Fase S06 antes de auditar evidencia FAULT o exclusión razonada de alcance, detección temporal, deriva/robustez y el capítulo escrito actualizado. Conservar abiertas issues #6/#25/#26 y el milestone de S06.
