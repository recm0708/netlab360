# Auditoría de muestreo ICMP del corpus histórico

## Descripción y alcance

Ejecutamos S06-050 correctamente en la VM (12 pruebas, `S06-050_PRERREGISTRO_VALIDADO=OK`, RC=0), pero el preregistro identificó **dos protocolos ICMP, de 2 y 3 paquetes por ventana**, y mantuvo `BLOCKED_INCOMPATIBLE_SAMPLING`. No es una falla de la topología ni un resultado negativo de rendimiento. El acta privada `~/netlab360-bootstrap/s06/preregistros/S06_050_Prerregistro_Prospectivo.json` **no debe reemplazarse ni editarse**.

Como el número de paquetes puede influir en `rtt_avg_ms`, `rtt_p95_ms`, `rtt_mdev_ms` y pérdida, necesitamos saber si se relaciona con la clase NORMAL/DEGRADED y el rol TRAIN/TEST. No corresponde atribuirle de antemano el resultado F1=1.000.

## Implementación

- `scripts/s06/auditar_muestreo_historico.py` lee únicamente el corpus original con los validadores ya existentes, comprueba el acta S06-050 intacta, identifica tres sesiones NORMAL, cuatro DEGRADED y cuatro RECOVERY, y contrasta los paquetes solicitados con el contador `sent` de cada medición ICMP.
- El reporte ofrece desgloses por clase y rol TRAIN/TEST/RECOVERY_ANALYSIS/HISTORICAL_OTHER. Los tamaños esperados son 60 NORMAL, 16 DEGRADED, 24 RECOVERY **por ruta**; HQ→S1 y HQ→S2 comparten estímulos y no son eventos independientes.
- `tests/test_s06_auditoria_muestreo.py` incluye casos de conteos, contaminación potencial por protocolo, integridad, fuente congelada y lectura no mutadora.
- El JSON privado queda bajo `~/netlab360-bootstrap/s06/auditorias-muestreo/S06_051_.../auditoria-muestreo.json`. No se versionan los datasets crudos ni se reentrenan o vuelven a calificar modelos.

## Interpretación

Si NORMAL y DEGRADED usan tamaños de muestra disjuntos, se marca `HIGH_IF_PACKET_SIZES_DISJOINT`: posible confusión fuerte entre protocolo de medición y etiqueta, **sin afirmar que esté probada su causalidad sobre las predicciones**. Si hay tamaños compartidos, se marca `POSSIBLE_SAMPLING_BIAS_REQUIRES_CONTROL`. En ambos casos se mantiene el preregistro bloqueado.

La solución no consiste en reetiquetar sesiones antiguas ni modificar el archivo congelado. Diseñamos un estudio separado con muestreo uniforme y justificación experimental. Los nuevos modelos se registraron como una versión distinta, sin sustituir los modelos originales ni presentar las observaciones ya vistas como TEST nuevo. Cualquier perturbación de red futura requerirá autorización específica y watchdog.

## Resultados

13 pruebas unitarias específicas OK y `S06-051_AUDITORIA_VALIDADA=OK` / `RESULTADO_RC=0`. La lectura de once sesiones verificó que **NORMAL tiene 60 ventanas de 3 paquetes, DEGRADED 16 de 2 y RECOVERY 24 de 3 por ruta**, sin discrepancias entre `requested_packets`, `sent` y metadatos. En TRAIN: NORMAL 40 ventanas × 3 paquetes y DEGRADED 12 × 2; en TEST: NORMAL 20 × 3 y DEGRADED 4 × 2. El tamaño muestral separa perfectamente las etiquetas NORMAL/DEGRADED, lo que constituye un **factor de confusión de protocolo** y limita el F1 histórico; no demuestra causalidad individual sobre las predicciones.

Acta S06-050 intacta y bloqueada, modelos sin reentrenar ni revaluar, `GATE_S06_051=INDEPENDENT_COMPARABILITY_PROTOCOL_BEFORE_NEW_LABELED_TEST`. Reporte privado `~/netlab360-bootstrap/s06/auditorias-muestreo/S06_051_20261123T112245Z_290a26/auditoria-muestreo.json`; bitácora `~/netlab360-bootstrap/s06/validacion-s06-051-20261123_062243/S06_051_Validacion_Completa.txt`. Quedaron 21 namespaces, cuatro contenedores, controlador `NONE/BASELINE`, qdisc `noqueue`, Prometheus y NOC/LACP/SDN saludables, sin cambios de red. El [protocolo V2 uniforme](s06-protocolo-uniforme-v2.md) se ejecutó como generación separada, preservando la evaluación histórica.
