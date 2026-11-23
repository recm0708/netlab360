# S06 V2 — Auditoría final de deriva y oportunidad temporal de detección

## Datos reales y conclusión legítima

El TEST V2 ya fue ejecutado y calificado con modelos congelados y protocolo común de tres paquetes ICMP. VALIDATION y TEST contienen **20 NORMAL, 8 DEGRADED y 12 RECOVERY por ruta**, con dos eventos de retardo 40 ms cada uno, capturados después de TRAIN. Los tres métodos reconocieron las ocho ventanas positivas de cada ruta en TEST; FP=0 para LogisticRegression, FP=0/1 para P95 según ruta y FP=1 por ruta para IsolationForest; FN=0 en los seis resultados de TEST. No hubo falsas alarmas en las 12 ventanas RECOVERY de TEST de cada ruta. La validez experimental se limita al egreso HQ sometido al mismo tipo de retardo artificial.

TRAIN por ruta: 40 NORMAL, 8 DEGRADED, 12 RECOVERY; los 4 modelos V2 se congelaron antes de VALIDATION y TEST. Se comprobó que el TEST es cronológicamente posterior a VALIDATION y usa nuevos tokens. Los 6 tokens son eventos diferentes en el tiempo, pero ambas rutas comparten cada perturbación; no representan 12 fallas independientes.

## Implementación del último análisis

`scripts/s06/auditar_resultados_v2_finales.py --save` **no vuelve a entrenar** ni modifica clases, modelos, qdisc, servicios ni ventanas. Primero coteja el TRAIN, la congelación V2, la procedencia de los dos resultados existentes `validation.json`/`test.json` y sus métricas. Después calcula las diferencias descriptivas en las cuatro features NORMAL (RTT medio, P95, mdev y pérdida) usando TRAIN n=40, VALIDATION n=20 y TEST n=20 por ruta. Informa diferencias de promedios y KS empírico para describir la distribución, **sin aplicar umbral de alarma ni atribuir significación estadística**.

Para estimar una **oportunidad retrospectiva de detección**, reconstruye únicamente los resultados por ventana de los tres métodos **ya congelados**, compara los conteos por evento con `test.json` y toma la primera ventana positiva posterior a `before.guard.applied_at_utc`. La latencia se mide hasta `recorded_at_utc` de esa ventana: abarca adquisición y toma de muestra, **no acredita inferencia en vivo, entrega de alerta al NOC ni predicción anticipada**. Es una auditoría de trazabilidad nueva sobre el mismo TEST, no otro TEST independiente ni oportunidad de optimizar umbrales.

Se guarda una sola vez en `~/netlab360-bootstrap/s06/estudio-uniforme-v2/evaluaciones-v2/auditoria-cientifica-final.json`; no sobrescribir si existe. Las pruebas `tests/test_s06_v2_final_audit.py` verifican estadística descriptiva, rechazo de fechas inconsistentes, tratamiento de no detección, trazabilidad temporal y ausencia de cambios de red.

## Decisiones de alcance que no deben omitirse

- **Data drift:** comparar normalidad de tres sesiones cronológicamente separadas con protocolo homogéneo; no inferir alarma de drift por una diferencia pequeña ni mezclar `NORMAL` con `DEGRADED`.
- **Concept drift:** dos eventos positivos por cada split de prueba aportan baja potencia; puede describirse estabilidad de los errores, pero **no hay prueba confiable de un cambio de relación entre telemetría y verdad de terreno**. Estado `NO_EVALUABLE` como conclusión inferencial.
- **Detección temporal vs pronóstico:** la primera ventana clasificada positiva ocurre después de aplicar `netem`. No hay ventana objetivo `t+h` ni horizonte futuro anticipado; **MAE de pronóstico y tiempo de alerta previa** permanecen `NO_EVALUABLE`. No escribir cero ni atribuir una alerta en producción.
- **FAULT adicional:** la clase FAULT no fue creada ni verificada por un segundo mecanismo de fallo; 40 ms de latencia es DEGRADED. Se necesita diseño independiente y autorización específica de un escenario realmente distinto, o dejar **explícita** la exclusión de FAULT de la versión exploratoria sin afirmar que se cumplió ese requisito general del plan. No inducir pérdida real en `ens33`, WAN, OSPF, LACP o Faucet por iniciativa del evaluador.
- **Costo operativo:** presentar FP en NORMAL, FP en RECOVERY, FN en DEGRADED y tasa de detección por evento; una sola ruta/estímulo no prueba confiabilidad universal.

## Cierre técnico después de ejecutar en VM

Ejecutar los 16 tests específicos y el auditor privado `--save` una vez; verificar su JSON contra TRAIN/VALIDATION/TEST ya guardados. Revisar que los cuatro modelos V2 siguen congelados, S06-050 no fue alterado, qdisc cliente `noqueue`, controlador `NONE/BASELINE`, 21 namespaces, cuatro contenedores, NOC y observador LACP/SDN sanos, Git limpio. Registrar los resultados numéricos reales en el informe y preparar capturas académicas solo cuando correspondan a las tablas/figuras finales.

Esta auditoría no cierra automáticamente S06: se debe resolver la cobertura FAULT frente al plan original y cerrar la documentación; S07 no requiere que se afirme una generalización inexistente.
