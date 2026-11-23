# S06-039 — Auditoría de seguridad y dependencias antes de intervenir un cliente real

## Estado comprobado hasta S06-038B

El usuario ejecutó S06-038B en Ubuntu y obtuvo `S06-038B_ROLLBACK_AISLADO_VALIDADO=OK`, RC 0; 24 tests específicos y 523 globales correctos. En el namespace temporal `nl360-s06-isotest`, la interfaz `dummy0` no recibió direcciones IP ni ruta default. Se comprobó que un temporizador systemd de 20 segundos, armado **antes** de netem 106:, eliminó esta qdisc de prueba y devolvió el estado `noqueue`. El estado `RESTORED` fue verificado; luego `cleanup` regresó el inventario a 21 namespaces. No se modificó el cliente HQ, el host VMware, FRR, HA, LACP, SDN ni los servicios de observabilidad. Bitácora privada: `~/netlab360-bootstrap/s06/rollback-aislado-20261123_004737/S06_038B_Rollback_Aislado.txt`.

**Un dummy sin conectividad y un cliente veth integrado a la topología no tienen el mismo riesgo.** El resultado demuestra restitución de qdisc aislada, no seguridad automática de cambios en el cliente productivo ni etiquetas reales de degradación.

## Propósito limitado de S06-039

Revisar por lectura la interfaz real candidata `nl360-s02-h-hq-120/eth0`, IP `10.70.20.20/24`, puerta de enlace `10.70.20.1`, y rutas hacia `10.71.20.20` (S1) y `10.72.20.20` (S2). El programa `scripts/s06/auditar_cliente_productivo.py` reutiliza las invariantes S06-035 y añade auditoría de:

- Tipo de enlace y datos de identificación del peer; lo observado no equivale a permiso para intervenir.
- Ruta efectiva hacia cada destino y gateway esperado, fuente e interfaz de salida.
- `qdisc noqueue` actual y ausencia de netem preexistente.
- Ningún namespace ni archivo de estado temporal sobrante de S06-038B.
- Siete servicios activos, NOC (18 nodos y 21 enlaces), HA/LACP/SDN, salud de fuentes y dataset S06-034 de 375 filas aún sin etiquetas.

Solo hace consultas con `ip`, `tc qdisc show`, `systemctl is-active` y APIs locales; puede guardar un JSON privado bajo `~/netlab360-bootstrap/s06/planes/S06_039_*/auditoria_preintervencion.json`. No requiere instalar nuevos ejecutores root, no crea ni elimina interfaces, no programa temporizadores y no aplica qdisc.

## Criterios de aceptación

1. Tests específicos y regresión general en GitHub CI y VM aprobados.
2. Confirmación de red administrativa `ens33 192.168.47.40/24`, gateway `192.168.47.2`, 21 namespaces y 4 Docker antes/después.
3. Ruta de HQ a S1/S2 con `eth0`, fuente `10.70.20.20`, gateway `10.70.20.1`; no se interpretan cambios como funcionamiento normal.
4. Interfaz activa y qdisc basal `noqueue`. Si el tipo de enlace no queda claro, indicar `UNKNOWN_REVIEW` y no proceder a intervención.
5. No existe `nl360-s06-isotest` ni `/run/netlab360-s06-isotest/state.json` tras S06-038B.
6. Archivo JSON de precheck con `read_only=true`, `production_change_authorized=false`, `ground_truth_verified=false` y seis gates pendientes.
7. NOC, Prometheus y los siete servicios continúan activos; no hay errores systemd ni alteraciones de Git.
8. La tarea **no ejecuta netem** y **no autoriza** cambios productivos.

## Gates pendientes tras S06-039

- Implementar y revisar **separadamente** un ejecutor root-owned que funcione solo sobre el cliente fijado por catálogo, sin permitir inyección de comandos o interfaces arbitrarias.
- Demostrar previamente con pruebas adversas que una muerte del controlador **no impide** al temporizador recuperar la qdisc; supervisar estado de rutas, tráfico y servicios en todos los desenlaces.
- Resolver semántica de pertenencia de qdisc en veth real (la qdisc no contiene dueño del experimento), incluyendo conflictos y modificaciones ajenas.
- Exigir aprobación humana por intervención, TTL limitado, bloqueo y protección de SSH y ens33.
- Diseñar mediciones antes, durante y después y un ground truth **independiente** de los datos predictivos. Nunca convertir el caso simulado S06-037 o dummy S06-038B en etiquetas supervisadas de una sede.
- Preparar rollback manual y gate de aborto, sin tocar datos originales S06-032/033/034.

**El resultado S06-039 será una auditoría de viabilidad, no autorización de intervención.** Milestone S06 e issues #6, #25, #26 permanecerán abiertos hasta completar los criterios correspondientes. Esta es también una dependencia de las acciones controladas S07 y futura GUI S08.
