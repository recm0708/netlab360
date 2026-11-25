# Línea base no supervisada y regla P95

## Objetivo

Implementamos un pipeline reproducible de entrenamiento y evaluación de un método no supervisado. Este ensayo inicial utiliza exclusivamente datos NORMAL y no acredita detección de degradaciones.

`scripts/s06/entrenar_baseline_anomalias.py` consume **tres sesiones S06-041A distintas** con clase NORMAL restringida a `HQ_CLIENT_EGRESS_NETWORK_STATE`. Las sesiones se generan con observación independiente de la qdisc noqueue, rutas y NOC antes/después de cada ventana y son datos reales de ICMP HQ→S1/S2, nunca muestras sintéticas.

## Control de integridad y fuga de información

- No modificar raw original ni usar archivos/sesiones de desconocida procedencia.
- Comprobar formato exacto de IDs de sesión, metadata/schema y checksum del JSONL.
- Rechazar ventanas `UNKNOWN`, medidas inválidas, sesiones parciales, rutas ajenas, falsos flags, symlinks o valores no finitos.
- División cerrada por sesión: dos sesiones completas para TRAIN, tercera sesión posterior completa para TEST. No barajar registros contiguos entre TRAIN y TEST ni ajustar umbrales en TEST.
- Features únicamente numéricas de RTT medio, P95 de paquetes, variabilidad mdev y pérdida; **excluir qdisc, ground truth, session_id, operador y condición de intervención** como variables predictoras.
- Entrenar un `IsolationForest` separado por ruta para no mezclar distintos RTT estructurales de S1/S2. `random_state=42`, 100 árboles, contaminación exploratoria 0.05.
- Comparar la **tasa de falsas alarmas sobre NORMAL** frente a una regla simple basada en P95 del RTT de entrenamiento. Ambos se evalúan sobre la misma sesión TEST sin verla previamente.

## Limitaciones

- Con 3 sesiones de 20 ventanas hay solo 40 observaciones de entrenamiento y 20 de test **por ruta**. Es una demostración de pipeline, no evidencia estadísticamente robusta de calidad generalizable.
- `IsolationForest` detecta outliers respecto al baseline normal. No equivale a clasificador supervisado, diagnóstico de causa ni predicción con horizonte.
- Como TEST contiene solo NORMAL, se calcula tasa de falsas alarmas, pero **NO** se calcula recall, F1 o precisión para DEGRADED; estas métricas necesitan estímulos reales etiquetados y test no visto con dos clases.
- Los resultados se guardan localmente bajo `~/netlab360-bootstrap/s06/modelos/S06_IFOREST_NORMAL_*/` como .joblib y un reporte JSON privado. Esos archivos derivados pueden auditarse, pero no se incorporan al repositorio ni se marcan como modelo aprobado para producción.
- **Advertencia de seguridad:** no abrir ni cargar archivos .joblib de terceros no confiables. El entrenamiento crea sus propios artefactos.

## Validación

Dos sesiones TRAIN y una TEST, 40/20 ventanas NORMAL por ruta. En HQ→S1 IsolationForest marcó 1/20 (5 %) y P95 3/20 (15 %); en HQ→S2 ambos marcaron 1/20 (5 %). La regresión comprendió 602 pruebas. El resultado mide falsas alarmas sobre NORMAL, no recall/F1 en degradaciones. [Evaluación binaria histórica](s06-evaluacion-binaria-holdout.md).
