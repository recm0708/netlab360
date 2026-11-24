# S06-041 — Captura de ventanas normales verificadas por estado independiente

## Hechos que habilitan este incremento

S06-040B **aprobado en VM real**: el proceso controlador de un par veth aislado terminó intencionalmente con SIGKILL (RC 137), pero el timer independiente restauró `netem` a `noqueue`. RTT medido `0.058 ms → 40.556 ms → 0.034 ms`, 0 % de pérdida en los tres lotes. Se eliminaron exclusivamente los namespaces efímeros y se recuperó el inventario a 21, sin tocar el cliente HQ ni `ens33`. La bitácora quedó bajo `S06_040B_FINAL_20261123_011831`.

## Qué medirá S06-041

`scripts/s06/capturar_ventanas_normales.py` registra muestras de bajo tráfico ICMP desde `nl360-s02-h-hq-120` hacia dos destinos reales:

- S1: `10.71.20.20`
- S2: `10.72.20.20`

Por cada ventana se comprueba, antes y después de medir, la qdisc `noqueue` del cliente, ruta y gateway `10.70.20.1`, siete servicios, NOC con 18 nodos y 21 enlaces, rutas y servicio HA en su estado esperado. El RTT es la variable predictora futura y **no** se utiliza para inventar la etiqueta.

## Semántica exacta de ground truth

La etiqueta `NORMAL` solo significa **condición de egreso normal verificada del cliente HQ**: qdisc noqueue, rutas esperadas, sin intervención netem y servicios/NOC consistentes en los límites de la ventana. NO demuestra que toda la red esté libre de cualquier degradación ajena o error indetectable. El campo `label_scope=HQ_CLIENT_EGRESS_NETWORK_STATE` debe conservarse al generar features y al evaluar el modelo.

Si cualquier condición, sonda o fuente no es verificable, la ventana se marca `UNKNOWN` y no puede entrar en entrenamiento supervisado. La comprobación es independiente del RTT y de pérdidas y se guarda en `before` y `after`. La sesión nunca reetiqueta los JSONL originales S06-032/033/034.

El programa funciona como usuario sin privilegios de root global; solo realiza comandos de consulta `sudo -n` restringidos al namespace y sondas existentes. No ejecuta netem, no detiene servicios y no cambia redes.

## Arquitectura de datos y criterio de aceptación

- Cada sesión crea `~/netlab360-bootstrap/s06/datasets/raw/S06_WINDOW_NORMAL_<UTC>_<id>/` con `ventanas.jsonl` y `metadata.json`, permisos privados.
- Se admiten de 2 a 80 ventanas, entre 2 y 6 paquetes por sonda, pausas de 0 a 5 segundos.
- El archivo registra timestamps UTC, sesión, número de ventana, sondas, estado independiente y evidencia de etiqueta; la metadata registra procedencia, digest, número de ventanas completas/verificadas y `training_ready=false`.
- Para la primera operación se proponen **tres sesiones independientes** de 20 ventanas × 2 rutas, hasta 120 observaciones ICMP con etiqueta operacional scoped, sin contar las comprobaciones de qdisc como características predictoras.
- Validar integridad, ausencia de UNKNOWN, 21 namespaces, cuatro contenedores, qdisc noqueue, siete servicios, Prometheus y NOC. Si hay ventanas UNKNOWN, conservar la sesión y analizarla; **no convertirla artificialmente a NORMAL**.
- Las sesiones de captura se separarán por sesión/tiempo al construir TRAIN/VALIDATION/TEST, no con filas contiguas aleatorias. **Solo la clase NORMAL no alcanza para evaluar clasificación binaria**.

## Siguiente resultado S06-042

Implementar un ejecutor **específico para el cliente de laboratorio real** root-owned con aprobación explícita, watchdog systemd comprobado ANTES del cambio, propiedad/identidad de qdisc, TTL, lock y pre/postchecks de `ens33` y rutas. Luego medir múltiples ventanas DEGRADED y RECOVERY con referencia independiente de los eventos del ejecutor. No registrar etiquetas por solamente observar RTT alto; registrar el estímulo y la restauración con marcas UTC.

Después construir características a partir de RTT/pérdida/telemetría separando información de etiqueta y observaciones de modelo, evaluar reglas e IsolationForest/algoritmos supervisados solo con al menos dos clases genuinas. No afirmar métricas F1 antes de test no visto.

Esta etapa representa una adquisición con clase NORMAL operacional scoped, no un modelo completo ni intervención real.
