# Protocolo experimental uniforme V2

## Motivación y alcance

La [auditoría histórica](s06-auditoria-muestreo-protocolo-historico.md) identificó un factor de confusión entre el número de paquetes ICMP y las etiquetas NORMAL/DEGRADED, además de la ausencia de separación cronológica global. El estudio V2 constituye una generación experimental independiente, no una modificación retroactiva del corpus histórico ni del [prerregistro bloqueado](s06-preregistro-futuro-modelos-congelados.md).

## Protocolo de adquisición

- Cliente existente `nl360-s02-h-hq-120/eth0`, rutas HQ_A_S1 y HQ_A_S2.
- Exactamente tres paquetes ICMP por ventana y ruta para todas las clases.
- NORMAL: [captura con etiquetas independientes](../../scripts/s06/capturar_ventanas_normales.py), verificación de qdisc, rutas y servicios antes y después de cada ventana.
- DEGRADED y RECOVERY: [orquestador multisesión](../../scripts/s06/ejecutar_lote_hq.py), dos eventos por partición, retardo fijo de 40 ms, watchdog de 35 s armado antes del estímulo, autorización humana específica y retorno verificado.
- Las mediciones utilizan solamente el cliente permitido. No se modifica la red administrativa, se preserva el estado original y se aborta ante conflicto o recuperación no verificada.

## Particiones y trazabilidad

| Partición | NORMAL por ruta | DEGRADED por ruta | RECOVERY por ruta | Finalidad |
|---|---:|---:|---:|---|
| TRAIN | 40 | 8 | 12 | Ajuste y congelación de modelos |
| VALIDATION | 20 | 8 | 12 | Evaluación sin ajuste |
| TEST | 20 | 8 | 12 | Evaluación de sesiones posteriores |
| Total | 80 | 24 | 36 | 140 ventanas por ruta |

Las cuatro sesiones normales y los seis eventos de degradación pertenecen a una secuencia cronológica estricta: TRAIN → congelación → VALIDATION → TEST. Las dos rutas comparten cada estímulo y no constituyen eventos estadísticamente independientes. Se conservaron los cuatro modelos históricos y se generaron cuatro modelos V2 separados.

## Validación de estímulos y retorno

| Partición | Evento | RTT DEGRADED (ms) | RTT RECOVERY (ms) |
|---|---:|---:|---:|
| TRAIN | 1 | 40,494 | 0,088 |
| TRAIN | 2 | 40,456 | 0,078 |
| VALIDATION | 1 | 40,522 | 0,078 |
| VALIDATION | 2 | 40,396 | 0,093 |
| TEST | 1 | 40,476 | 0,075 |
| TEST | 2 | 40,469 | 0,073 |

Los seis eventos se completaron con recuperación verificada. Se conservaron 21 namespaces, cuatro contenedores, administración, NOC y qdisc basal. Una autorización inicial incorrecta fue rechazada sin ejecutar estímulos; las sesiones normales originales se conservaron.

## Evaluación y límites

El protocolo se ejecutó y validó en la VM. El entrenamiento, matrices de confusión, análisis temporal y escenario HTTP se documentan por separado para evitar duplicación de resultados. La detección del retardo artificial no acredita pronóstico, generalización a otros tipos de falla ni remediación autónoma.

## Documentación relacionada

[Entrenamiento y congelación](s06-v2-train-freeze-modelos.md) · [Evaluación cronológica](s06-v2-evaluacion-cronologica-congelada.md) · [Deriva descriptiva y detección](s06-v2-deriva-deteccion-y-limitaciones-finales.md) · [Falla HTTP independiente](s06-fault-http-hq-etiquetado-independiente.md) · [Evidencias de la fase 06](../../evidencias/capturas/fase6/README.md).
