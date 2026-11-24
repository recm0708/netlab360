# Deriva descriptiva y oportunidad de detección V2 — Fase 06

## Alcance del análisis

El TEST V2 ya fue ejecutado y calificado con modelos congelados y protocolo común de tres paquetes ICMP. VALIDATION y TEST contienen **20 NORMAL, 8 DEGRADED y 12 RECOVERY por ruta**, con dos eventos de retardo 40 ms cada uno, capturados después de TRAIN. Los tres métodos reconocieron las ocho ventanas positivas de cada ruta en TEST; FP=0 para LogisticRegression, FP=0/1 para P95 según ruta y FP=1 por ruta para IsolationForest; FN=0 en los seis resultados de TEST. No hubo falsas alarmas en las 12 ventanas RECOVERY de TEST de cada ruta. La validez experimental se limita al egreso HQ sometido al mismo tipo de retardo artificial.

TRAIN por ruta: 40 NORMAL, 8 DEGRADED, 12 RECOVERY; los 4 modelos V2 se congelaron antes de VALIDATION y TEST. Se comprobó que el TEST es cronológicamente posterior a VALIDATION y usa nuevos tokens. Los 6 tokens son eventos diferentes en el tiempo, pero ambas rutas comparten cada perturbación; no representan 12 fallas independientes.

## Implementación

`scripts/s06/auditar_resultados_v2_finales.py --save` **no vuelve a entrenar** ni modifica clases, modelos, qdisc, servicios ni ventanas. Primero coteja el TRAIN, la congelación V2, la procedencia de los dos resultados existentes `validation.json`/`test.json` y sus métricas. Después calcula las diferencias descriptivas en las cuatro features NORMAL (RTT medio, P95, mdev y pérdida) usando TRAIN n=40, VALIDATION n=20 y TEST n=20 por ruta. Informa diferencias de promedios y KS empírico para describir la distribución, **sin aplicar umbral de alarma ni atribuir significación estadística**.

Para estimar una **oportunidad retrospectiva de detección**, reconstruye únicamente los resultados por ventana de los tres métodos **ya congelados**, compara los conteos por evento con `test.json` y toma la primera ventana positiva posterior a `before.guard.applied_at_utc`. La latencia se mide hasta `recorded_at_utc` de esa ventana: abarca adquisición y toma de muestra, **no acredita inferencia en vivo, entrega de alerta al NOC ni predicción anticipada**. Es una auditoría de trazabilidad nueva sobre el mismo TEST, no otro TEST independiente ni oportunidad de optimizar umbrales.

Se guarda una sola vez en `~/netlab360-bootstrap/s06/estudio-uniforme-v2/evaluaciones-v2/auditoria-cientifica-final.json`; no sobrescribir si existe. Las pruebas `tests/test_s06_v2_final_audit.py` verifican estadística descriptiva, rechazo de fechas inconsistentes, tratamiento de no detección, trazabilidad temporal y ausencia de cambios de red.

## Limitaciones

- **Data drift:** comparar normalidad de tres sesiones cronológicamente separadas con protocolo homogéneo; no inferir alarma de drift por una diferencia pequeña ni mezclar `NORMAL` con `DEGRADED`.
- **Concept drift:** dos eventos positivos por cada split de prueba aportan baja potencia; puede describirse estabilidad de los errores, pero **no hay prueba confiable de un cambio de relación entre telemetría y verdad de terreno**. Estado `NO_EVALUABLE` como conclusión inferencial.
- **Detección temporal vs pronóstico:** la primera ventana clasificada positiva ocurre después de aplicar `netem`. No hay ventana objetivo `t+h` ni horizonte futuro anticipado; **MAE de pronóstico y tiempo de alerta previa** permanecen `NO_EVALUABLE`. No escribir cero ni atribuir una alerta en producción.
- **FAULT independiente:** la degradación ICMP de 40 ms no equivale a FAULT. La [falla del backend HTTP HQ](s06-fault-http-hq-etiquetado-independiente.md) se verificó aparte, sin mezclar datos ni atribuir al modelo ICMP capacidad de detectarla.
- **Costo operativo:** presentar FP en NORMAL, FP en RECOVERY, FN en DEGRADED y tasa de detección por evento; una sola ruta/estímulo no prueba confiabilidad universal.

## Resultados de la auditoría

S06_V2_CIERRE_CIENTIFICO=OK: 16 pruebas específicas aprobadas. Se verificaron los cuatro modelos V2 congelados y los cuatro modelos históricos originales.

| Ruta | RTT medio TRAIN (ms) | VALIDATION (ms) | TEST (ms) | KS TRAIN–TEST |
|---|---:|---:|---:|---:|
| HQ→S1 | 0,0780 | 0,0798 | 0,0799 | 0,200 |
| HQ→S2 | 0,0796 | 0,0849 | 0,0752 | 0,125 |

La primera oportunidad retrospectiva de detección fue 1416 y 1402 ms en los dos eventos TEST, coincidente en ambas rutas y los tres métodos. El intervalo comienza después de aplicar el estímulo; no acredita alerta en vivo ni predicción. Se conservaron guardia NONE/BASELINE, qdisc noqueue, NOC, Prometheus, LACP/SDN, 21 namespaces y cuatro contenedores. El resultado privado se conserva en auditoria-cientifica-final.json. [Evaluación cronológica](s06-v2-evaluacion-cronologica-congelada.md) · [Evidencias](../../evidencias/capturas/fase6/README.md).
