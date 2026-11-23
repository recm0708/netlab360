# S06-044 — Evaluación binaria por sesiones independientes, sin modificar redes

## Fuentes verificadas y alcance

S06-043 tiene tres experimentos nuevos completos en el **cliente real existente HQ**; la corrección de lectura validó el registro de ciclos y el dataset. El acumulado S06-041–043 es de **60 ventanas NORMAL**, **16 DEGRADED** y **24 RECOVERY**. La captura académica F05 ya fue entregada, revisada y aprobada, con delimitadores INICIO/FIN. Se conservaron 21 namespaces originales, 4 contenedores, ruta de administración y `eth0` del cliente HQ con qdisc `noqueue`. Fuente de los eventos: `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T073108Z_344e1e/manifest.json`.

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

## Interpretación obligatoria

Con solo **cuatro ventanas de degradación por ruta en TEST**, el recall varía en saltos de 25 puntos porcentuales. Hay únicamente un **tipo de fallo inyectado: retardo fijo de 40 ms** en el mismo cliente y misma topología. Un resultado excelente no demostraría generalización a pérdidas, congestión variable, falla WAN, OSPF, SDN, caída de HA ni incidentes desconocidos.

La clase RECOVERY registra un **estado operacional posterior al evento** y no tiene por qué ser separable de NORMAL usando RTT/pérdida: es correcto medir falsa alarma sobre RECOVERY, pero sería engañoso afirmar clasificación multiclase confiable sin otras señales causales. Los artefactos binarios generados no autorizan remediación automática ni despliegue.

La evaluación guarda `evaluacion.json`, modelos privados y un TXT para evidencia en `~/netlab360-bootstrap/s06/evaluaciones/S06_044_*/`. No subir datos originales ni modelos privados a Git. No abrir objetos de modelos de terceros no confiables.

## Captura académica y continuidad

El script escribe una evidencia independiente con marcadores `========== INICIO CAPTURA S06_F06_Evaluacion_Binaria_Modelos_HQ ==========` y `========== FIN CAPTURA S06_F06_Evaluacion_Binaria_Modelos_HQ ==========`. **Tomar F06 solo después de ejecutar el script en VM y validar los resultados reales**. Contiene matriz TP/FP/TN/FN, precisión, recall, F1 y falsas alarmas RECOVERY para tres métodos y dos destinos.

Siguiente lote tras aprobar S06-044: informe técnico de análisis de error/limitaciones, API de inferencia **solo lectura**, comportamiento UNKNOWN para datos insuficientes, explicación de alertas y conexión a NOC; luego S07/S08 deberán respetar el catálogo de acciones autorizadas. No sumar un nuevo experimento ni crear interfaces ficticias para este incremento.

Esta documentación describe una implementación pendiente de ejecución en VM; las métricas no deben inventarse ni declararse exitosas antes de observarlas.
