# S06 — Estudio prospectivo uniforme: protocolo consolidado antes de nuevos datos

## Dictamen histórico que obliga a un estudio distinto

Las auditorías S06-049/S06-050/S06-051 demostraron que el TEST S06-044 estaba separado por IDs de sesión pero no por cronología global. Además, las 60 ventanas NORMAL y las 24 RECOVERY por ruta se midieron con **3 paquetes**; las 16 DEGRADED con **2 paquetes**. Es una confusión perfecta entre cantidad de paquetes y etiqueta binaria. No sabemos en qué proporción contribuyó al F1=1.000; por ello conservamos los resultados antiguos como exploratorios y **no los presentamos como generalización prospectiva**.

**El preregistro privado S06-050 queda inmutable y BLOQUEADO. Este protocolo es un estudio de generación V2 nuevo, no una corrección retroactiva ni un desbloqueo del acta anterior.** Su preregistro versionado en GitHub debe fusionarse *antes* de ejecutar cualquier sesión de este estudio. No reutilizar como TRAIN, VALIDATION o TEST ningún identificador previo.

## Muestreo uniforme y operaciones protegidas

- Origen único de cliente real `nl360-s02-h-hq-120/eth0`, rutas `HQ_A_S1` y `HQ_A_S2`. Una observación usa exactamente **3 paquetes ICMP por ruta**, en NORMAL, DEGRADED y RECOVERY, sin variar características, período, recursos o umbrales en función de la clase.
- Para NORMAL utilizar `scripts/s06/capturar_ventanas_normales.py --rounds 20 --packets 3`; etiquetas según `noqueue`, rutas, NOC y estado de infraestructura antes y después, no según RTT.
- Para DEGRADED/RECOVERY utilizar `scripts/s06/ejecutar_lote_hq.py --cycles 2 --packets 3 --approve-batch AUTORIZO_HQ_VLAN120_NETEM_40MS_35S`, únicamente después de **aprobación humana explícita en la terminal**. Cada ciclo conserva el controlador root, el watchdog independiente TTL 35 s, el retardo fijo 40 ms en egreso HQ y la restauración verificada; solo se modifica el cliente existente. Los dos ciclos producen 8 ventanas DEGRADED y 12 RECOVERY por ruta. La modificación de código conserva `--packets 2` como valor por defecto del orquestador histórico para no romper reproducibilidad.
- Las fases futuras que requieran estímulo de red tienen su propia autorización, se cancelan ante estado `ESCALATED` o mala recuperación, y jamás ejecutan `tc` ni alteran `ens33` desde un script de evaluación. No reinstalar controlador ni alterar sudoers.

## Orden cronológico bloqueado antes de la adquisición

| Etapa | NORMAL por ruta | DEGRADED por ruta | RECOVERY por ruta | Uso de los datos |
|---|---:|---:|---:|---|
| TRAIN | 2 sesiones de 20 = 40 | 2 eventos × 4 = 8 | 12 | Ajuste inicial de modelos **solo con TRAIN** |
| VALIDATION | 1 sesión de 20 | 2 eventos × 4 = 8 | 12 | Evaluación de calidad/FP sin contaminar TEST; no ajustar umbrales después |
| TEST | 1 sesión de 20 | 2 eventos × 4 = 8 | 12 | Métricas definitivas sobre sesiones posteriores nunca usadas |

Total previsto para el nuevo corpus: **80 NORMAL, 24 DEGRADED y 36 RECOVERY por ruta**, con **6 tokens de eventos distintos**; dos destinos del mismo evento se consideran correlacionados. Mantener estrictamente esta secuencia: NORMAL TRAIN → EVENTOS TRAIN → entrenar y congelar nuevos modelos V2 → NORMAL VALIDATION → EVENTOS VALIDATION → evaluar sin ajuste → NORMAL TEST → EVENTOS TEST → evaluar una sola vez. Si algo falla o un archivo queda parcial, no reetiquetar ni reutilizar el evento. La captura de TEST ocurre **después de la congelación de modelos**, con nueva etiqueta externa y timestamps posteriores a todo TRAIN/VALIDATION.

Los modelos V2 usarán las mismas cuatro variables (RTT medio, P95, mdev y pérdida), regla P95 sobre NORMAL TRAIN, IsolationForest y regresión logística con configuración fijada previa a nuevas observaciones; sklearn `random_state=42`, `contamination=0.05`, `n_estimators=100`, `class_weight=balanced`, normalización StandardScaler, sin optimización sobre TEST. Los **cuatro modelos legacy permanecen intactos**; V2 usa archivos y reporte privados separados y no sustituye sus hashes ni el preregistro S06-050.

## Criterios de análisis que deben aparecer en el informe final de S06

1. Por ruta y por sesión/evento: matriz de confusión, precisión, recall, F1, especificidad, FP/FN, falsas alarmas de RECOVERY, comparación contra P95 y costo operativo de alarmas. No usar dos rutas del mismo estímulo como 2 eventos independientes.
2. Detección temporal: registrar `applied_at_utc` y tiempo hasta primera señal DEGRADED **posterior** al inicio; esto es latencia de detección, **no** pronóstico anticipado. Si no existen features anteriores predictivas, `MAE`, horizonte futuro y anticipación se consignan `NO_EVALUABLE`, no cero ni mejoría inventada.
3. Drift de datos: comparar TRAIN NORMAL de 3 paquetes contra NORMAL VALIDATION y TEST (medidas descriptivas por ruta, muestra pequeña); para concept drift utilizar etiquetas posteriores y cambios de tasa de error por eventos, reportar intervalos y baja potencia.
4. Escenario FAULT independiente: no confundir 40 ms de latencia con falla WAN/OSPF, HA, LACP, Faucet o pérdida. Si se exige FAULT genuino, diseñar un **segundo estímulo con controlador/watchdog y aprobación separados** antes de intervenir; hasta esa verificación `FAULT=NO_EVALUABLE`. No cerrar la obligación sin registrar exclusión, justificación o experimento real.
5. Demostrar alcance HQ real, calidad, origen UTC, split cronológico, incertidumbre UNKNOWN, API/NOC de solo lectura, seguridad del controlador, recuperación y reproducibilidad. Resultados históricos y resultados V2 deben estar **claramente separados** en el Word/PDF académico.

## Gate operativo

Primero fusionar la adaptación del orquestador con CI aprobada y ejecutar dos sesiones NORMAL TRAIN (3 paquetes). Verificar IDs nuevos y metadatos de ambas sesiones. La primera intervención controlada solo se inicia después de aprobación literal humana, `sudo -v`, control root `NONE/BASELINE`, ausencia de qdisc ajena, NOC/Prometheus saludables y auditoría del watchdog; antes de la intervención debe poder abortarse sin cambios. El siguiente bloque planificado reutiliza el orquestador para **dos** eventos TRAIN y conserva sus registros en `~/netlab360-bootstrap/s06/experimentos/`. Después entrenar y congelar V2 antes de reunir VALIDATION/TEST.

**No se declarará S06 concluida por pasar pruebas CI, aprobar la preparación o repetir el retardo 40 ms.** La aceptación requiere resultados verdaderamente posteriores y comparables, además del alcance/limitaciones de FAULT y pronóstico y las evidencias del informe. La Fase 6 permanece al 80 % técnico estimado hasta obtener evidencia de los gates pendientes.

## Aprobación del código antes de nuevas sesiones

PR [#177](https://github.com/recm0708/netlab360/pull/177) fusionado a `main` mediante `f4612a0`, CI general **792 pruebas (791 aprobadas y una omitida)**. Se mantiene el valor por defecto histórico de dos paquetes y se permite elegir tres en el orquestador protegido con `--packets 3`; nuevos controles cotejan metadatos y paquetes reales enviados/recibidos. **Todavía no se ha ejecutado una sola sesión V2 ni autorizado otro estímulo de red.**

## Primera ejecución real V2 — NORMAL TRAIN aceptado, estímulo pendiente (23/11/2026)

La VM sincronizó `main` en `e6b519a`, ejecutó 25/25 pruebas del orquestador y aprobó la guardia `NONE/BASELINE`, `noqueue` y 21 namespaces. Se obtuvieron **dos sesiones NORMAL TRAIN nuevas de 20 ventanas verificadas cada una, con 3 paquetes por ruta**: `S06_WINDOW_NORMAL_20261123T143842Z_1e1812` (A) y `S06_WINDOW_NORMAL_20261123T143913Z_b5d57c` (B). `NORMAL_TRAIN_VERIFICADO=OK`; registros bajo `~/netlab360-bootstrap/s06/estudio-uniforme-v2/TRAIN_Normal_A.txt` y `TRAIN_Normal_B.txt`, además de `TRAIN_Normal_Sesiones.json`. No duplicar estas sesiones.

En la solicitud de aprobación, el operador introdujo `AUTORIZACION` en lugar de la cadena literal del controlador, por lo que el bloque concluyó en **`EVENTOS_TRAIN=NO_AUTORIZADOS`** y RC 0 sin ejecutar DEGRADED/RECOVERY. Esta salida segura no equivale a TRAIN V2 completo. Próximo paso: verificar las sesiones conservadas y estado HQ, requerir aprobación humana literal antes de `--cycles 2 --packets 3`; si no se autoriza, no modificar red ni inventar etiquetas. Los modelos V2 aún no se han entrenado.

## TRAIN V2 real: confirmación de adquisición y código de entrenamiento

Dos ciclos aprobados con la cadena humana exacta, watchdog autónomo y recuperación verificada. Ciclo 1 RTT DEGRADED 40.494 ms y RECOVERY 0.088 ms; ciclo 2 40.456 ms y 0.078 ms. Por ruta: 40 NORMAL, 8 DEGRADED, 12 RECOVERY, todos de 3 paquetes. `S06_V2_TRAIN_COMPLETO=OK`, `RESULTADO_RC=0`; batch privado `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T150227Z_b399ae/manifest.json`. PR [#178](https://github.com/recm0708/netlab360/pull/178) fusionado en `9ff338f` con CI 807 tests (806 OK, una omitida). La congelación real `--freeze` en VM y siguientes VALIDATION/TEST están pendientes; no tratar CI como ejecución experimental.

## VALIDATION V2 real y modelos congelados (23/11/2026)

15 tests de entrenamiento OK; `--freeze` y `--check` confirmaron cuatro modelos V2 privados, P95 de HQ→S1 **0.10405 ms** y HQ→S2 **0.11055 ms**. Las muestras VALIDATION fueron posteriores a TRAIN y a la congelación: NORMAL `S06_WINDOW_NORMAL_20261123T151633Z_973a31` (20 ventanas) y dos eventos controlados en `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T151706Z_e1ca29/manifest.json` (8 DEGRADED, 12 RECOVERY por ruta); las tres clases usan 3 paquetes ICMP. Watchdog restauró ambos ciclos (RTT DEGRADED/RECOVERY 40.522/0.078 ms y 40.396/0.093 ms), controlador NONE/BASELINE, qdisc noqueue, NOC, 21 namespaces y 4 contenedores conservados. `S06_V2_VALIDATION_COMPLETA=OK`, RC0.

**VALIDATION se adquirió, pero aún no se puntuó**. No repetir TRAIN/VALIDATION ni ajustar modelos. El siguiente gate es puntuar VALIDATION con pesos congelados, después adquirir TEST posterior e independiente, puntuarlo una sola vez y analizar falsas alarmas, deriva, latencia de detección, FAULT y límites del pronóstico.

## Estudio V2: VALIDATION y TEST prospectivo verificados (23/11/2026)

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

**Pendiente S06:** informe final de deriva descriptiva y costo operativo, latencia retrospectiva de oportunidad de detección, limitación o escenario FAULT independientemente verificado, horizonte futuro y MAE si son evaluables, evidencias académicas y revisión del capítulo del informe. El gate de detección prospectiva bajo 40 ms está verificado; la generalización de fallas diferentes no.
