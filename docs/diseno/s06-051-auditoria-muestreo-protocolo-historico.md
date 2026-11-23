# S06-051 — Auditoría del protocolo ICMP por sesión, clase y split

## Problema detectado y alcance

La VM ejecutó S06-050 correctamente (12 pruebas, `S06-050_PRERREGISTRO_VALIDADO=OK`, RC=0), pero el preregistro identificó **dos protocolos ICMP, de 2 y 3 paquetes por ventana**, y mantuvo `BLOCKED_INCOMPATIBLE_SAMPLING`. No es una falla de la topología ni un resultado negativo de rendimiento. El acta privada `~/netlab360-bootstrap/s06/preregistros/S06_050_Prerregistro_Prospectivo.json` **no debe reemplazarse ni editarse**.

Como el número de paquetes puede influir en `rtt_avg_ms`, `rtt_p95_ms`, `rtt_mdev_ms` y pérdida, necesitamos saber si se relaciona con la clase NORMAL/DEGRADED y el rol TRAIN/TEST. No corresponde atribuirle de antemano el resultado F1=1.000.

## Implementación

- `scripts/s06/auditar_muestreo_historico.py` lee únicamente el corpus original con los validadores ya existentes, comprueba el acta S06-050 intacta, identifica tres sesiones NORMAL, cuatro DEGRADED y cuatro RECOVERY, y contrasta los paquetes solicitados con el contador `sent` de cada medición ICMP.
- El reporte ofrece desgloses por clase y rol TRAIN/TEST/RECOVERY_ANALYSIS/HISTORICAL_OTHER. Los tamaños esperados son 60 NORMAL, 16 DEGRADED, 24 RECOVERY **por ruta**; HQ→S1 y HQ→S2 comparten estímulos y no son eventos independientes.
- `tests/test_s06_auditoria_muestreo.py` incluye casos de conteos, contaminación potencial por protocolo, integridad, fuente congelada y lectura no mutadora.
- El JSON privado queda bajo `~/netlab360-bootstrap/s06/auditorias-muestreo/S06_051_.../auditoria-muestreo.json`. No se versionan los datasets crudos ni se reentrenan o vuelven a calificar modelos.

## Interpretación

Si NORMAL y DEGRADED usan tamaños de muestra disjuntos, se marca `HIGH_IF_PACKET_SIZES_DISJOINT`: posible confusión fuerte entre protocolo de medición y etiqueta, **sin afirmar que esté probada su causalidad sobre las predicciones**. Si hay tamaños compartidos, se marca `POSSIBLE_SAMPLING_BIAS_REQUIRES_CONTROL`. En ambos casos se mantiene el preregistro bloqueado.

La solución no consiste en reetiquetar sesiones antiguas ni modificar el archivo congelado. Se deberá diseñar un estudio separado con muestreo uniforme y justificación experimental. Los nuevos modelos, si fueran necesarios, tendrían que registrarse como una versión distinta, sin sustituir los modelos originales ni presentar las observaciones ya vistas como TEST nuevo. Cualquier perturbación de red futura requerirá autorización específica y watchdog.

## Aceptación en VM

Tras aprobar CI, ejecutar las pruebas específicas y el auditor con `--save`. Corroborar once sesiones originales, coherencia entre metadatos y transmisiones, el desglose por clase/split y `S06_051_AUDITORIA_READONLY=OK`. El gate esperado es `INDEPENDENT_COMPARABILITY_PROTOCOL_BEFORE_NEW_LABELED_TEST`, **no** `PLAN_READY`.

Al terminar, verificar 21 namespaces, cuatro contenedores, ens33 .40/24 con gateway .2, guardia `NONE/BASELINE`, qdisc `noqueue`, NOC 18/21, LACP/SDN y Prometheus. Ninguna nueva captura académica hasta conocer resultados. F01–F09B siguen válidas como evidencia de lo que se ejecutó, con limitaciones metodológicas claramente declaradas.

**Estado:** CI y ejecución VM pendientes. S06 permanece en 80 % técnico validado mientras no exista evidencia prospectiva independiente.
