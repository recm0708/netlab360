# Escenarios experimentales y etiquetado verificable

## Antecedentes observacionales

- S06-032: referencia de 12 observaciones reales del exportador de telemetría, Prometheus y NOC con etiqueta UNKNOWN.
- S06-033: nueve sondas ICMP y tres HTTP sin fallas inducidas, tres rondas; valores medidos de RTT, pérdida y respuesta HA.
- S06-034: 375 filas normalizadas procedentes de 2 sesiones, fuentes y unidades tipadas, sin valores faltantes ni scrapes repetidos detectados; raw intacto. **No son 375 incidentes ni un dataset supervisado**.


## Escenario ICMP del cliente HQ

**Objetivo:** verificar si puede inducirse una degradación de latencia/pérdida con control estricto dentro de un cliente LAN de HQ, para contrastar medidas antes, durante y después sin tocar la gestión del host.

- Namespace candidato: nl360-s02-h-hq-120.
- Interfaz candidata: eth0, IPv4 10.70.20.20/24, gateway 10.70.20.1.
- Rutas de medición: HQ→S1 (10.71.20.20) y HQ→S2 (10.72.20.20), usando catálogo de mediciones existente.
- Interfaz protegida: ens33 192.168.47.40/24, gateway 192.168.47.2. La aplicación no puede inducir condiciones en ens33, Docker, routers WAN, backend HTTP HA, puentes LACP, controlador Faucet ni otros clientes.
- Estado operativo de referencia: 21 namespaces, cuatro contenedores, 18 nodos/21 enlaces NOC y backend HQ.

Este cliente es una **candidatura, no una autorización para ejecutar tc**. Primero hay que inspeccionar el estado real de la qdisc, los privilegios, el alcance de interfaz y la ruta default del namespace. Si existe una qdisc configurada, una interfaz no reconocida, alguna ruta administrativa inconsistente o faltan herramientas, suspender cambios y revisar.

## Precheck de solo lectura

El script scripts/s06/precheck_escenarios.py realiza únicamente consultas a IPAM esperado, interfaces/namespaces, qdisc actual y APIs locales. No incluye operaciones qdisc add, change, replace, del; tampoco modifica rutas, servicios ni procesos. Produce un reporte JSON privado bajo netlab360-bootstrap/s06/planes/S06_035_*.

Comando:

    python3 scripts/s06/precheck_escenarios.py --save-plan

Salida esperada: S06_035_PRECHECK=OK_SOLO_LECTURA, S06_035_CAMBIOS_DE_RED=NINGUNO y S06_035_PLANIFICACION=LISTA_PARA_REVISION_NO_EJECUTAR_NETEM. El valor S06_035_QDISC_ESTADO requiere inspección: CANDIDATE_NOQUEUE solo identifica una configuración inicialmente compatible, **no** implica que el ensayo sea seguro sin watchdog y rollback verificados.

## Protocolo de etiquetado

1. NORMAL provisional: comprobar infraestructura, qdisc original, IPAM, salud del NOC, OSPF/FIB y mediciones completas sin intervención. Solo etiquetar NORMAL si la ausencia de estímulo y condiciones operativas están comprobadas independientemente del modelo.
2. DEGRADED provisional: crear un experimento acotado mediante un ejecutor privilegiado root-owned, con interfaz allowlisted, duración limitada, bloqueo de concurrencia y watchdog de restauración independiente del proceso de prueba. Verificar la qdisc y el estímulo realmente aplicados; observar pérdida/latencia en serie separada. Si el estímulo no se confirma, etiquetar UNKNOWN.
3. RECOVERY provisional: retirar exclusivamente la qdisc introducida por el experimento, nunca una configuración ajena, confirmar restablecimiento de interfaz, rutas, PING, OSPF, HA/LACP/SDN/NOC y registrar tiempos. Eliminar una qdisc no identificada queda prohibido.
4. FAULT: no pertenece al escenario ICMP; se evaluó separadamente mediante falla del backend HTTP HQ.
5. Trazabilidad: guardar session_id, parent_session, escenario, UTC de inicio/aplicación/restauración, identificador de estímulo, evidencia externa, labels por fase y motivación, mediciones crudas y normalizadas; datos privados fuera de Git.
6. Anti-leakage: nunca introducir el nombre de escenario, el estímulo aplicado, la etiqueta o el timestamp de inicio de intervención como predictor que haga trivial reconocer la clase; tampoco separar puntos del mismo experimento entre TRAIN y TEST.

**Criterios previos para una ejecución perturbadora:** permisos mínimos y propietario root del ejecutor, state precheck/postcheck idempotente, TTL obligatorio con restaurador independiente, pruebas unitarias de fallo/interrupción y procedimiento de emergencia comprobado. S06-035 acredita solo planificación y lectura, no autorización.

## Validación y alcance

El precheck S06-035 identificó el cliente HQ, estado CANDIDATE_NOQUEUE y rutas esperadas, sin autorizar cambios. El estímulo de 40 ms y su retorno se verificaron posteriormente mediante el [ejecutor protegido](s06-experimentos-hq-reales-y-watchdog.md). La [falla HTTP](s06-fault-http-hq-etiquetado-independiente.md) constituye un escenario independiente; no se añade al corpus ICMP. El diseño no cubre automáticamente otras clases de falla.
