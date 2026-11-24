# Contrato de eventos e incidentes multisede S07

## Objetivo y alcance

La issue [#190](https://github.com/recm0708/netlab360/issues/190) establece la capa de normalización de observaciones para la correlación y el diagnóstico RCA. Esta primera implementación S07-001A es una biblioteca sin I/O y pruebas unitarias sintéticas. No incorpora todavía adquisición de fuentes reales ni confirma incidentes.

## Esquema de observación

| Campo | Significado |
|---|---|
| schema, event_id | Versión del contrato e identidad determinista |
| source, kind, subject | Fuente, observación/inferencia y tipo de señal |
| resource_id, site, peer_site | Recurso y contexto multisede |
| observed_at_utc, received_at_utc, age_seconds | Tiempo de origen, recepción y antigüedad; nunca inventar una fecha de medición |
| quality | VALID, MISSING, INVALID, STALE o FUTURE |
| state | NORMAL, DEGRADED, FAULT, RECOVERY o UNKNOWN, limitado a la señal |
| ground_truth | UNKNOWN; la observación no es una etiqueta experimental independiente |
| evidence, details | Referencia al endpoint y recurso, más escalares acotados |
| network_mutations_authorized | Siempre false |

La antigüedad máxima inicial es 60 segundos para observaciones NOC/Prometheus y 30 segundos para IA S06. Son límites de diseño, no SLO ni valores de rendimiento acreditados. Una señal ausente, inválida, vencida o futura se representa como UNKNOWN. Una señal vigente puede ser UNKNOWN por incertidumbre. El consenso DEGRADED de IA S06 se conserva como detalle de inferencia, no como falla confirmada.

## Fuentes autorizadas y límites

- NOC S05: topología, WAN, OSPF/FIB, VLAN, LACP, SDN y HTTP HA, según sus contratos y edad de cada fuente.
- Prometheus S04: métricas seleccionadas mediante consultas locales predefinidas; no se acepta PromQL libre.
- IA S06: las dos rutas ICMP previstas en el adaptador del NOC; no generalizar a HTTP ni a toda la topología.

Los adaptadores posteriores deberán validar cada contrato y conservar su timestamp real. El timestamp global del grafo no sustituye el de una señal individual. No se inicia adquisición ni se autoriza tráfico de prueba, intervención, shell ni cambios.

## Orden y duplicados

La identidad determinista corresponde al contenido normalizado, excluyendo la hora de recepción y la edad cuando existe un timestamp de observación. Los duplicados se contabilizan; señales contradictorias con identidad diferente se conservan. Se detecta recepción fuera de orden por fuente y recurso, conservando los registros para análisis cronológico. El contrato de incidente se definirá después, sin inferir causalidad a partir de estas señales por sí solas.

## Aceptación incremental

S07-001A implementa y prueba el contrato de observaciones en modo offline. S07-001B incorpora adaptadores de lectura NOC/IA, pendientes de aceptación en la VM al publicar el código. S07-001C incorporará Prometheus; la persistencia y el contrato de incidente se validarán por separado. La issue #190 permanece abierta hasta completar todas sus condiciones de aceptación. La correlación y el RCA pertenecen a #191.

Código: [contrato de eventos](../../scripts/s07/contrato_eventos.py) y [pruebas unitarias](../../tests/test_s07_contrato_eventos.py).

## Adaptadores NOC e IA

S07-001B implementa [adaptadores NOC e IA](../../scripts/s07/adaptadores_noc.py) y [pruebas sintéticas](../../tests/test_s07_adaptadores_noc.py). Consulta exclusivamente los endpoints locales fijos del NOC, sin proxy, redirecciones ni comandos. Se proyectan 19 señales de observación (topología, cuatro WAN, nueve VLAN, tres LACP, SDN y frontal HTTP) y dos inferencias ICMP.

La marca temporal de la telemetría se utiliza para las señales administrativas WAN/VLAN. Estas conservan el estado administrativo como detalle y el estado operacional UNKNOWN: no prueban tráfico ni vecindades OSPF. LACP, SDN y HTTP conservan sus propias fechas de observación. FIB y OSPF requieren fuentes temporales verificables adicionales y no se simulan mediante la hora de generación del grafo.

La pérdida de una fuente no invalida otra fuente independiente. Una respuesta fuera de contrato se excluye de la proyección útil (MISSING/UNKNOWN); fechas inválidas, futuras o vencidas se clasifican mediante el contrato. Los identificadores no previstos o duplicados no se eligen arbitrariamente. Una respuesta HTTP correcta no prueba vigencia ni disponibilidad de las señales que contiene.

El estado DEGRADED del frontal con backend de respaldo indica selección alternativa, no interrupción HTTP. La desconexión de Faucet representa el plano de control y no prueba pérdida de tráfico. El consenso IA se verifica frente a los tres métodos y no autoriza intervención.

## Adaptador Prometheus S04

S07-001C1 implementa [adquisición Prometheus](../../scripts/s07/adaptador_prometheus.py) y [pruebas sintéticas](../../tests/test_s07_adaptador_prometheus.py). Una consulta fija de rango de 120 segundos contra el endpoint local permite seleccionar el último scrape de cada serie esperada del target S04. No utiliza la hora de evaluación de una consulta instantánea como fecha del scrape.

Se normalizan 23 señales: dos de adquisición (scrape y lectura del colector), una de topología, tres de existencia de routers, ocho extremos WAN y nueve VLAN. Los valores de los recursos solo se proyectan cuando corresponden al mismo scrape exitoso y el colector reporta lectura correcta. No se recuperan valores de scrapes anteriores para aparentar disponibilidad. Las series duplicadas o ajenas no se seleccionan.

El timestamp de Prometheus acredita el scrape, no la hora exacta de adquisición interna del exporter, que mantiene un snapshot cacheado. La calidad VALID en esta fuente indica un scrape vigente y utilizable, no vigencia independiente de la medición interna ni confirmación de forwarding. Las señales administrativas y de existencia conservan UNKNOWN operacional. El valor -1 representa desconocimiento, no DOWN. El estado FAULT del exporter se limita a su scrape fallido, no a la red.

OSPF y FIB se incorporarán mediante lectura explícita de los routers en S07-001C2, porque el exporter S04 no publica estas métricas. No se modifican sus procesos ni reglas. La aceptación en la VM permanece pendiente al publicar este componente.

## Lectura directa de OSPF y FIB

S07-001C2 implementa [adaptador FRR S02](../../scripts/s07/adaptador_frr.py) y [pruebas](../../tests/test_s07_adaptador_frr.py). Incorpora una fuente independiente FRR_S02, ocho extremos de adyacencia OSPF y seis selecciones FIB entre loopbacks. La ejecución es puntual por un operador con sudo previamente autenticado, no un servicio privilegiado ni una API de ejecución. Las consultas son fijas: inspección Docker, show ip ospf neighbor e ip route get. No genera pings ni cambios de configuración.

Antes y después de la lectura por router se verifica la identidad del contenedor y su PID contra el estado de propiedad S02; se comprueba la red administrativa antes y después del lote. El registro de fecha corresponde a la finalización de cada consulta, no a una medición simultánea de todas las fuentes. La información no disponible o sin identidad verificable permanece UNKNOWN.

OSPF Full confirma únicamente la adyacencia observada; una fila no Full es una desviación de la línea base. La ausencia de fila no se declara automáticamente FAULT. La FIB principal o de respaldo se clasifica respecto al diseño esperado, sin afirmar tráfico real. La aceptación operativa queda pendiente de prueba en la VM. No se alteran los servicios existentes.

## Persistencia histórica SQLite

S07-001D incorpora [almacén de eventos](../../scripts/s07/almacen_eventos.py) y [pruebas de persistencia](../../tests/test_s07_almacen_eventos.py). El almacenamiento mantiene la observación original normalizada, sus fechas, calidad y estado en recepción, la identidad de flujo y un indicador de llegada tardía. La validación reconstruye el contrato y el identificador antes de insertar. Cada lote es transaccional; las consultas SQL usan parámetros. La clave única permite reimportar sin duplicar ni reemplazar el registro original; discrepancias con identidades distintas se conservan.

La llegada tardía se comprueba respecto a la máxima fecha de observación válida o vencida ya almacenada en el mismo flujo. Los datos futuros, ausentes o inválidos no desplazan esa frontera. El orden de consulta histórico es independiente del orden de inserción. El indicador representa orden de importación, no latencia de transporte. Los lotes normalizados previamente pueden haber descartado su orden de recepción interno; este almacén no lo reconstruye.

La base local se conserva bajo el directorio de ejecución de S07 fuera de Git; los ensayos sintéticos usan bases temporales independientes. Los estados almacenados son históricos, nunca salud en tiempo real. La vigencia para RCA se evaluará nuevamente al consultar una ventana operacional. Las adquisiciones separadas de S07-001B/C1/C2 no se convierten en una ventana simultánea. La aceptación en VM queda pendiente al publicar este componente.
