# S06 — Diseño de escenarios y etiquetado comprobable

## Contexto comprobado

- S06-032: referencia de 12 observaciones reales en S04/Prometheus/NOC con etiqueta UNKNOWN.
- S06-033: nueve sondas ICMP y tres HTTP sin fallas inducidas, tres rondas; valores medidos de RTT, pérdida y respuesta HA.
- S06-034: 375 filas normalizadas procedentes de 2 sesiones, fuentes y unidades tipadas, sin valores faltantes ni scrapes repetidos detectados; raw intacto. **No son 375 incidentes ni un dataset supervisado**.
- S06 en avance funcional estimado **35 %**; modelos, ventanas suficientes, dataset etiquetado y pronósticos todavía pendientes.

## Primer escenario candidato: degradación aislada de un cliente S02

**Objetivo:** verificar si puede inducirse una degradación de latencia/pérdida con control estricto dentro de un cliente LAN de HQ, para contrastar medidas antes, durante y después sin tocar la gestión del host.

- Namespace candidato: nl360-s02-h-hq-120.
- Interfaz candidata: eth0, IPv4 10.70.20.20/24, gateway 10.70.20.1.
- Rutas de medición: HQ→S1 (10.71.20.20) y HQ→S2 (10.72.20.20), usando catálogo S06 existente.
- Interfaz protegida: ens33 192.168.47.40/24, gateway 192.168.47.2. La aplicación no puede inducir condiciones en ens33, Docker, routers WAN, backend HTTP HA, puentes LACP, controlador Faucet ni otros clientes.
- Estado operativo de referencia: 21 namespaces, cuatro contenedores, 18 nodos/21 enlaces NOC y backend HQ.

Este cliente es una **candidatura, no una autorización para ejecutar tc**. Primero hay que inspeccionar el estado real de la qdisc, los privilegios, el alcance de interfaz y la ruta default del namespace. Si existe una qdisc configurada, una interfaz no reconocida, alguna ruta administrativa inconsistente o faltan herramientas, suspender cambios y revisar.

## S06-035: precheck de solo lectura

El script scripts/s06/precheck_escenarios.py realiza únicamente consultas a IPAM esperado, interfaces/namespaces, qdisc actual y APIs locales. No incluye operaciones qdisc add, change, replace, del; tampoco modifica rutas, servicios ni procesos. Produce un reporte JSON privado bajo netlab360-bootstrap/s06/planes/S06_035_*.

Comando:

    python3 scripts/s06/precheck_escenarios.py --save-plan

Salida esperada: S06_035_PRECHECK=OK_SOLO_LECTURA, S06_035_CAMBIOS_DE_RED=NINGUNO y S06_035_PLANIFICACION=LISTA_PARA_REVISION_NO_EJECUTAR_NETEM. El valor S06_035_QDISC_ESTADO requiere inspección: CANDIDATE_NOQUEUE solo identifica una configuración inicialmente compatible, **no** implica que el ensayo sea seguro sin watchdog y rollback verificados.

## Protocolo de experimentación futuro — no implementado en S06-035

1. NORMAL provisional: comprobar infraestructura, qdisc original, IPAM, salud del NOC, OSPF/FIB y mediciones completas sin intervención. Solo etiquetar NORMAL si la ausencia de estímulo y condiciones operativas están comprobadas independientemente del modelo.
2. DEGRADED provisional: crear un experimento acotado mediante un ejecutor privilegiado root-owned, con interfaz allowlisted, duración limitada, bloqueo de concurrencia y watchdog de restauración independiente del proceso de prueba. Verificar la qdisc y el estímulo realmente aplicados; observar pérdida/latencia en serie separada. Si el estímulo no se confirma, etiquetar UNKNOWN.
3. RECOVERY provisional: retirar exclusivamente la qdisc introducida por el experimento, nunca una configuración ajena, confirmar restablecimiento de interfaz, rutas, PING, OSPF, HA/LACP/SDN/NOC y registrar tiempos. Eliminar una qdisc no identificada queda prohibido.
4. FAULT: no habilitado en este primer escenario; requerirá experimento adicional con alcance y autorización independientes.
5. Trazabilidad: guardar session_id, parent_session, escenario, UTC de inicio/aplicación/restauración, identificador de estímulo, evidencia externa, labels por fase y motivación, mediciones crudas y normalizadas; datos privados fuera de Git.
6. Anti-leakage: nunca introducir el nombre de escenario, el estímulo aplicado, la etiqueta o el timestamp de inicio de intervención como predictor que haga trivial reconocer la clase; tampoco separar puntos del mismo experimento entre TRAIN y TEST.

**Criterios previos para una ejecución perturbadora:** permisos mínimos y propietario root del ejecutor, state precheck/postcheck idempotente, TTL obligatorio con restaurador independiente, pruebas unitarias de fallo/interrupción y procedimiento de emergencia comprobado. Hasta entonces S06-035 es exclusivamente planificación.

## Próximas necesidades

- Diseñar captura más larga y de mayor frecuencia para permitir análisis estadístico robusto de latencia/pérdida y variaciones temporales.
- Medir TCP/UDP con iperf3 restringido en namespaces permitidos, con límite de tráfico y duración; validar servidor, puertos y limpieza de procesos.
- Confirmar ground truth con una evidencia de estado de la intervención independiente de las señales predictoras; no etiquetar muestras históricas UNKNOWN retrospectivamente.
- Diseñar particiones por sesiones y cronología y comparar reglas/Isolation Forest/modelos supervisados solo cuando la cantidad y variedad de experimentos lo justifique.

Seguimiento: issues #6, #25, #26 y el plan maestro S06–S08.
