# S06-041B — Primera línea base ML, comparada con regla P95

## Objetivo

Comprobar de manera reproducible que el entorno S06 ejecuta un pipeline **real** de entrenamiento y evaluación de un método no supervisado, pero **sin atribuirle capacidad de detectar degradaciones que aún no se han probado**.

`scripts/s06/entrenar_baseline_anomalias.py` consume **tres sesiones S06-041A distintas** con clase NORMAL restringida a `HQ_CLIENT_EGRESS_NETWORK_STATE`. Las sesiones se generan con observación independiente de la qdisc noqueue, rutas y NOC antes/después de cada ventana y son datos reales de ICMP HQ→S1/S2, nunca muestras sintéticas.

## Controles de integridad y no leakage

- No modificar raw original ni usar archivos/sesiones de desconocida procedencia.
- Comprobar formato exacto de IDs de sesión, metadata/schema y checksum del JSONL.
- Rechazar ventanas `UNKNOWN`, medidas inválidas, sesiones parciales, rutas ajenas, falsos flags, symlinks o valores no finitos.
- División cerrada por sesión: dos sesiones completas para TRAIN, tercera sesión posterior completa para TEST. No barajar registros contiguos entre TRAIN y TEST ni ajustar umbrales en TEST.
- Features únicamente numéricas de RTT medio, P95 de paquetes, variabilidad mdev y pérdida; **excluir qdisc, ground truth, session_id, operador y condición de intervención** como variables predictoras.
- Entrenar un `IsolationForest` separado por ruta para no mezclar distintos RTT estructurales de S1/S2. `random_state=42`, 100 árboles, contaminación exploratoria 0.05.
- Comparar la **tasa de falsas alarmas sobre NORMAL** frente a una regla simple basada en P95 del RTT de entrenamiento. Ambos se evalúan sobre la misma sesión TEST sin verla previamente.

## Limitaciones relevantes

- Con 3 sesiones de 20 ventanas hay solo 40 observaciones de entrenamiento y 20 de test **por ruta**. Es una demostración de pipeline, no evidencia estadísticamente robusta de calidad generalizable.
- `IsolationForest` detecta outliers respecto al baseline normal. No equivale a clasificador supervisado, diagnóstico de causa ni predicción con horizonte.
- Como TEST contiene solo NORMAL, se calcula tasa de falsas alarmas, pero **NO** se calcula recall, F1 o precisión para DEGRADED; estas métricas necesitan estímulos reales etiquetados y test no visto con dos clases.
- Los resultados se guardan localmente bajo `~/netlab360-bootstrap/s06/modelos/S06_IFOREST_NORMAL_*/` como .joblib y un reporte JSON privado. Esos archivos derivados pueden auditarse, pero no se incorporan al repositorio ni se marcan como modelo aprobado para producción.
- **Advertencia de seguridad:** no abrir ni cargar archivos .joblib de terceros no confiables. El entrenamiento crea sus propios artefactos.

## Después de S06-041B

S06-042: ejecutar un programa de degradación deliberada y reversible **solo** sobre la veth del cliente HQ del laboratorio con guard root, timer real, autorización humana y mediciones de estado y RTT; registrar marcas de estímulo y restauración independientes del algoritmo para la clase DEGRADED/RECOVERY.

S06-043: construir dataset multisesión, split temporal/sesión, comparar reglas e IsolationForest y entrenar clasificadores supervisados con métricas sobre TEST sin fuga. Agregar API de inferencia solo lectura y preparar integración a NOC y luego S07/S08.

No cerrar issues S06, ni afirmar resultados de IA antes de ejecución real de los modelos.
