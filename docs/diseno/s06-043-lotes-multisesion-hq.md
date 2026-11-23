# S06-043 — Lotes multisesión sobre el cliente HQ real, sin interfaces ficticias

## Punto de partida verificado

El proyecto NETLAB360 cuenta con 21 namespaces originales y cuatro contenedores. Los namespaces temporales S06 usados para ensayos de watchdog/dummy/veth fueron eliminados y la auditoría S06-042 detectó cero interfaces dummy. La administración `ens33 192.168.47.40/24`, gateway `192.168.47.2` y el cliente `nl360-s02-h-hq-120/eth0` (veth conectada al switch de HQ, `10.70.20.20/24`, gateway `10.70.20.1`) están conservados. No recrear interfaces ni namespaces en S06-043.

**S06-041:** 60 ventanas NORMAL verificadas, 120 mediciones ICMP y dos modelos exploratorios IsolationForest con test por sesión. **S06-042:** intervención controlada real `netem delay 40ms`, TTL 35 s con watchdog previo, 4 ventanas DEGRADED RTT medio 40.440 ms y 6 RECOVERY RTT medio 0.070 ms. `RESTORED`, `noqueue`, `cleanup NONE`. Las capturas académicas F01–F04 ya están tomadas y revisadas. Rutas de evidencia y sesiones completas: [§4.11 plan maestro](s06-s08-plan-maestro-y-criterios.md).

## Objetivo técnico inmediato

Conseguir **tres sesiones experimentales adicionales** y estrictamente independientes en el **mismo cliente real** para habilitar después una división TRAIN/TEST por sesión de evento. Solo repetir el estímulo que ya funcionó con TTL corto y guardar evidencia independiente del RTT de cada transición. No crear otro experimento artificial; no modificar equipos, bridges ni routers.

El script `scripts/s06/ejecutar_lote_hq.py` acepta exclusivamente `--cycles 2` o `--cycles 3`, y la autorización de lote `--approve-batch AUTORIZO_HQ_VLAN120_NETEM_40MS_35S`. La ejecución del comando con tres ciclos autoriza explícitamente **tres intervenciones breves**, cada una por separado, sobre `nl360-s02-h-hq-120/eth0`, con timer root autónomo. Los ciclos son secuenciales: **nunca se ejecutan dos a la vez**.

Por cada ciclo:

1. Requiere que el controlador existente `/usr/local/libexec/netlab360/s06-hq-controlador.py` esté `STATE=NONE`, qdisc `BASELINE` y `audit` root seguro.
2. Ejecuta `start` con la cadena literal de aprobación; el controlador verifica gestión, namespace, peer, IPAM, NOC y temporizador systemd activo **ANTES** de aplicar netem.
3. Captura **cuatro ventanas DEGRADED**, dos sondas ICMP por ventana, mientras el timer sigue armado. Rechaza UNKNOWN, cambios de token, rutas incorrectas, estados distintos de APPLIED/qdisc OWN_NETEM, metadata o checksum incoherente.
4. Espera confirmación explícita `RESTORED` del watchdog independiente, `final_qdisc_state=BASELINE`, `restoration_trigger=WATCHDOG` y token correspondiente. Ante ESCALATED o timeout no ejecuta cleanup y no inicia otro ciclo; exige revisión.
5. Captura **seis ventanas RECOVERY** con tres paquetes por sonda, estado RESTORED/qdisc BASELINE y token del mismo ciclo.
6. Al comprobar las capturas, diferencias observables de RTT y retorno a noqueue, archiva evidencia root y ejecuta `cleanup`; verifica `STATE=NONE` y qdisc BASELINE antes del siguiente ciclo.

El orquestador es un cliente no privilegiado que invoca comandos del controlador root **fijos y permitidos**. No contiene operaciones `tc`, `ip link add/del` o `ip netns add/del`, no necesita cambios sudoers y no altera `ens33`. No se ejecuta en segundo plano. Si falla un ciclo, el watchdog sigue programado de forma independiente, el registro JSON queda con `status=stopped_requires_review` y no se inicia otro experimento. **No repetir el lote ni borrar archivos de estado sin diagnóstico.**

## Archivos de salida y aceptación

Directorio privado `~/netlab360-bootstrap/s06/experimentos/S06_043_<UTC>_<id>/`, con `manifest.json`, inicios del controlador, logs de captura DEGRADED/RECOVERY y estados del watchdog de cada ciclo. Sesiones JSONL/metadata permanecen bajo `~/netlab360-bootstrap/s06/datasets/raw/S06_WINDOW_DEGRADED_*` y `S06_WINDOW_RECOVERY_*`; no se borran ni reetiquetan las sesiones anteriores.

**Objetivo medible si se completan 3 ciclos:** 3×4 = **12 ventanas DEGRADED nuevas**, 3×6 = **18 RECOVERY nuevas**; acumulado con S06-042 inicial: **16 DEGRADED**, **24 RECOVERY**, además de las 60 NORMAL ya verificadas. Cada ventana contiene dos rutas HQ→S1 y HQ→S2. Los totales finales deben verificarse desde el registro JSON, no presumirse.

## Siguiente etapa: evaluación ML honesta

Dividir los datos por **sesión independiente de estímulo**, nunca mezclando ventanas del mismo token entre TRAIN y TEST. Un posible conjunto: DEGRADED histórico S06-042 + primeros dos ciclos S06-043 para TRAIN; último ciclo S06-043 para TEST. En NORMAL, dos sesiones S06-041 para TRAIN y una para TEST. Evaluar detección binaria **NORMAL vs DEGRADED** comparando regla RTT P95 de entrenamiento, IsolationForest entrenado con NORMAL y un clasificador supervisado pequeño de sklearn. RECOVERY se analiza como **postevento restablecido** y se evalúa su tasa de falsas alarmas: sus valores de RTT pueden ser similares a NORMAL y no tiene por qué ser separable como una tercera clase desde métricas de red solamente.

El período de recuperación debe mantenerse como clase/estado operacional independiente en los raw, aunque el modelo binario lo interprete como tráfico no degradado. No usar `qdisc`, tokens root, timestamps del evento o etiquetas como características del modelo. Sin múltiples eventos y TEST independientes, abstenerse de prometer generalización o predicción anticipada.

## Evidencia y capturas académicas

F01–F04 están aprobadas y no deben repetirse. Para nuevas evidencias, cada comando muestra `========== INICIO CAPTURA <nombre> ==========` y `========== FIN CAPTURA <nombre> ==========`; tomar solo la región entre ambas marcas, y usar nombre descriptivo sin extensión. El siguiente candidato es `S06_F05_Dataset_Multisesion_Real_HQ` al verificar nuevos ciclos. La captura comparativa de modelos debería denominarse `S06_F06_Evaluacion_Binaria_Modelos_HQ` y solo tomarse tras ejecutar y auditar una evaluación con holdout real; no titularla «multiclase» si no se ha demostrado esa capacidad.

## Aceptación real S06-043 y evidencia F05 (23/11/2026)

**Tres ciclos completados en VM sobre el cliente HQ real existente**, cada uno con cuatro ventanas DEGRADED y seis RECOVERY verificadas por qdisc y control root. RTT degradación 40.419, 40.376, 40.381 ms; RTT recuperación 0.071, 0.075, 0.068 ms, watchdog RESTORED en todos y cleanup STATE=NONE. `S06_043_SESIONES_MULTIPLES=OK` se emitió antes de un **error posterior del wrapper en el here-doc que generaba F05**, que hizo que el wrapper global terminara RC 1. Esa incidencia de presentación se corrigió **sin repetir experimentos** con validación de solo lectura `S06-043_AUDITORIA_FINAL_CORREGIDA=OK`: integridad de registros/datos, 21 namespaces, 4 contenedores, gestión intacta, qdisc noqueue, NOC/Prometheus/7 servicios activos, sin interfaces ficticias.

Registro local validado `~/netlab360-bootstrap/s06/experimentos/S06_043_20261123T073108Z_344e1e/manifest.json`; TXT de evidencia `~/netlab360-bootstrap/s06/evidencias/informe/S06_F05_Dataset_Multisesion_Real_HQ.txt`. La captura F05 con INICIO/FIN fue entregada en el chat, revisada y aprobada. Totales **100 ventanas reales**, 60 NORMAL, 16 DEGRADED y 24 RECOVERY; la imagen no está versionada en Git ni se afirma copiada a la VM. **S06-044: evaluación por sesiones separadas, sin nuevas intervenciones**. Progreso S06 ~65 % estimado.

## Continuidad en otro chat

La fuente canónica de reanudación es [§4.11 del plan maestro](s06-s08-plan-maestro-y-criterios.md). El estado de GitHub/CI solo valida código; las cifras de nuevas sesiones no deben marcarse como realizadas hasta ver la bitácora `S06_043_SESIONES_MULTIPLES=OK` y el registro JSON real de VM. Mantener las issues S06 #6, #25 y #26 abiertas hasta completar sus criterios.
