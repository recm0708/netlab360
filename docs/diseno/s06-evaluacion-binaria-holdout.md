# Evaluación binaria exploratoria por sesiones

## Descripción y alcance

S06-043 tiene tres experimentos nuevos completos en el **cliente real existente HQ**; la corrección de lectura validó el registro de ciclos y el dataset. El acumulado S06-041–043 es de **60 ventanas NORMAL**, **16 DEGRADED** y **24 RECOVERY**. Se conservaron 21 namespaces originales, 4 contenedores, ruta de administración y `eth0` del cliente HQ con qdisc `noqueue`. Fuente de los eventos: `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T073108Z_344e1e/manifest.json`.

El nuevo `scripts/s06/evaluar_deteccion_binaria.py` **no ejecuta tc ni cambia interfaces**: lee exclusivamente los datasets privados ya capturados, valida estado root registrado, tokens por evento, rutas, controles antes/después, etiquetas y checksum de cada sesión, entrena y calcula métricas.

## Partición y prevención de fuga de información

| Subconjunto | NORMAL | DEGRADED | RECOVERY |
|---|---|---|---|
| Entrenamiento binario | Primera y segunda sesión S06-041, 40 ventanas por ruta | S06-042 inicial y ciclos 1 y 2 de S06-043, 12 ventanas por ruta | No se usa para entrenar |
| Test binario independiente | Tercera sesión NORMAL S06-041, 20 ventanas por ruta | Ciclo 3 de S06-043, 4 ventanas por ruta | Ciclo 3, 6 ventanas por ruta para analizar falsas alarmas posincidente |

No se mezclan ventanas de una sesión entre entrenamiento y prueba. Un evento `DEGRADED` y su `RECOVERY` comparten token: el test de recuperación procede del **mismo ciclo 3 reservado**; los ciclos 1 y 2 se usan solo en TRAIN DEGRADED y no se usan para test. Las sondas HQ→S1 y HQ→S2 pueden estar correlacionadas porque comparten experimento y transporte de red; se reportan por ruta, **no** como experimentos estadísticamente independientes.

**Importante:** esta partición es holdout **por sesión y evento**, no un holdout cronológico global: la sesión de prueba NORMAL ocurrió antes que algunas sesiones DEGRADED de entrenamiento. No afirmar que reproduce detección de eventos futuros de distinta naturaleza ni capacidad de predicción adelantada.

## Algoritmos evaluados y variables

- **Regla P95**: umbral de RTT promedio calibrado únicamente sobre NORMAL de TRAIN.
- **IsolationForest**: detección no supervisada entrenada exclusivamente con NORMAL de TRAIN.
- **LogisticRegression**: clasificador binario supervisado entrenado con NORMAL + DEGRADED de TRAIN, balanceo de clases y normalización de variables aprendida solo sobre TRAIN.

Cada método se evalúa sobre las mismas 20 ventanas NORMAL + 4 DEGRADED por ruta del TEST; calcula TP, FP, TN, FN, precisión, recall, F1 y especificidad. También se mide cuántas de las seis ventanas RECOVERY del test son marcadas erróneamente como degradadas. La lista de variables del modelo se limita a RTT medio, RTT P95, variación mdev y porcentaje de pérdida medidos por ICMP. No entran la qdisc, el token, el estado del controlador, la etiqueta, la fecha ni el ID de sesión como predictores.

## Limitaciones

Con solo **cuatro ventanas de degradación por ruta en TEST**, el recall varía en saltos de 25 puntos porcentuales. Hay únicamente un **tipo de fallo inyectado: retardo fijo de 40 ms** en el mismo cliente y misma topología. Un resultado excelente no demostraría generalización a pérdidas, congestión variable, falla WAN, OSPF, SDN, caída de HA ni incidentes desconocidos.

La clase RECOVERY registra un **estado operacional posterior al evento** y no tiene por qué ser separable de NORMAL usando RTT/pérdida: es correcto medir falsa alarma sobre RECOVERY, pero sería engañoso afirmar clasificación multiclase confiable sin otras señales causales. Los artefactos binarios generados no autorizan remediación automática ni despliegue.

La evaluación guarda `evaluacion.json`, modelos privados y un TXT para evidencia en `~/netlab360-bootstrap/s06/evaluaciones/S06_044_*/`. No subir datos originales ni modelos privados a Git. No abrir objetos de modelos de terceros no confiables.

## Resultados

Ejecutamos el evaluador sobre los datasets originales y aprobamos 23 pruebas específicas. Verificamos la separación por sesión entre TRAIN y TEST y recalculamos las matrices de confusión.

| Ruta | Método | TP | FP | TN | FN | Precisión | Recall | F1 | FP sobre RECOVERY (6) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| HQ_A_S1 | P95_RTT | 4 | 3 | 17 | 0 | 0.571 | 1.000 | 0.727 | 0 |
| HQ_A_S1 | IsolationForest | 4 | 1 | 19 | 0 | 0.800 | 1.000 | 0.889 | 0 |
| HQ_A_S1 | LogisticRegression | 4 | 0 | 20 | 0 | 1.000 | 1.000 | 1.000 | 0 |
| HQ_A_S2 | P95_RTT | 4 | 1 | 19 | 0 | 0.800 | 1.000 | 0.889 | 0 |
| HQ_A_S2 | IsolationForest | 4 | 1 | 19 | 0 | 0.800 | 1.000 | 0.889 | 0 |
| HQ_A_S2 | LogisticRegression | 4 | 0 | 20 | 0 | 1.000 | 1.000 | 1.000 | 0 |

**Conclusión restringida:** LogisticRegression fue superior entre los tres métodos **en este holdout concreto**, pero dos rutas comparten experimento, solo hay cuatro muestras positivas por ruta, el caso se limita a 40 ms fijos y **no hay holdout cronológico global**. No se autoriza inferencia en producción, remediación automática, ni afirmaciones de generalización a otras clases de fallas. Las seis muestras RECOVERY por ruta se midieron separadamente como falsas alarmas, no como una tercera clase.

**Estado de infraestructura tras ejecutar:** 21 namespaces, cuatro contenedores, `ens33`/gateway conservados, guardia HQ `NONE/BASELINE`, qdisc `noqueue`, Prometheus READY y NOC saludable; sin unidades fallidas. Los datos y modelos privados permanecen en la VM, no en GitHub. Evidencia textual `~/netlab360-bootstrap/s06/evidencias/informe/S06_F06_Evaluacion_Binaria_Modelos_HQ.txt`; evaluación `~/netlab360-bootstrap/s06/evaluaciones/S06_044_20261123T081627Z_2ade0e/` y bitácora `~/netlab360-bootstrap/s06/validacion-s06-044-20261123_031619/S06_044_Validacion_Completa.txt`.

[Inferencia histórica](s06-inferencia-hq-replay-readonly.md).
