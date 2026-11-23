# S06-037 — Simulación reproducible de seguridad y restauración

## Contexto acreditado

S06-036 completó en Ubuntu 16 pruebas específicas y 457 offline, validó un temporizador transitorio de systemd que ejecutó /usr/bin/touch y creó un marcador privado. Confirmó qdisc noqueue en el cliente HQ y conservación de ens33, gateway y NOC. La tarea de temporizador fue independiente del script que la programó, **pero no realizó rollback de red**.

## Objetivo

Validar antes de cualquier intervención real la lógica de protección de un procedimiento de degradación controlado sobre el cliente de HQ VLAN120. El nuevo script scripts/s06/simular_rollback.py es un **simulador puro** que no usa sudo, no ejecuta tc, no cambia rutas, no tiene acceso a la interfaz ni al temporizador real. Su reloj, qdisc, autorización y exclusión mutua son objetos simulados en memoria.

## Política propuesta

- Target fijo: namespace nl360-s02-h-hq-120, interfaz eth0, IP 10.70.20.20/24 y gateway 10.70.20.1.
- Gestión protegida: ens33 192.168.47.40/24, gateway 192.168.47.2.
- La autorización requiere rol operator, aprobación explícita, target autorizado y qdisc original noqueue.
- TTL simulado entre 10 y 60 segundos; reloj virtual, no corresponde a segundos medidos de ejecución real.
- El watchdog lógico debe estar armado ANTES de simular cualquier cambio.
- Un experimento activo retiene el lock; se impide concurrencia.
- El rollback lógico solo restaura una qdisc con dueño coincidente; las ajenas se bloquean y escalan a intervención humana.
- Fallar al restaurar mantiene el lock y produce ESCALATED; no se simula recuperación exitosa.
- Las etiquetas permanecen UNKNOWN porque son pruebas de lógica, no datos de entrenamiento.

## Matriz inicial de fallos

| Caso | Estado final lógico | Comportamiento comprobado por simulación |
|---|---|---|
| success | RESTORED | secuencia normal de autorización, armado, simulación y retorno |
| expired_ttl | RESTORED | recuperación al vencer el TTL virtual |
| controller_crash | RESTORED | un evento virtual de watchdog actúa tras la caída simulada |
| apply_failure | ABORTED | no se aplica cambio y se libera el lock |
| foreign_owner | ESCALATED | nunca elimina configuración de otro dueño |
| rollback_failure | ESCALATED | reconoce falla, conserva el lock y exige revisión |
| double_restore | RESTORED | idempotencia de recuperación |
| no_approval | NEW | bloqueo sin autorización humana |
| watchdog_missing | APPROVED | impide ejecutar sin watchdog armado |
| concurrency | APPROVED | segundo experimento rechazado |
| wrong_target | NEW | rechaza ens33 o target fuera del catálogo |
| wrong_qdisc | NEW | rechaza qdisc preexistente |
| wrong_management | NEW | rechaza gateway administrativo distinto |
| bad_ttl | NEW | rechaza duración desproporcionada |

Estos son **estados lógicos simulados**, no resultados de red. El nombre de escenario no se usa como etiqueta de entrenamiento.

## Ejecución prevista

Desde el repositorio:

    python3 scripts/s06/simular_rollback.py --all --save-report

Salida privada en netlab360-bootstrap/s06/rollback-simulaciones/S06_037_*/simulacion_rollback.json. El reporte guarda todos los eventos y resultados por escenario, con network_changes_executed=false y real_rollback_implemented=false.

Criterio de aprobación parcial: CI y pruebas en VM completadas, todos los casos con resultados esperados, integridad de reporte, directorio privado, infraestructura intacta.

## Qué falta antes de un ensayo real

1. Implementar ejecutor del sistema instalado como archivo propiedad de root y no escribible por el usuario del NOC.
2. Implementar reloj/TTL **real**, watchdog independiente que ejecute un procedimiento de restauración real, reintentos y alarmas.
3. Armar el temporizador y verificarlo antes de modificar qdisc; conservar evidencia de propiedad y estado anterior.
4. Probar protección de interfaces, concurrencia y fallos de arranque/restauración con un entorno aislado, sin provocar pérdida de acceso.
5. Ejecutar el primer ensayo controlado solamente después de aprobar estos controles; medir baseline, intervención y recuperación.
6. Etiquetar ground truth a partir de comprobación independiente del estímulo y de su retirada; no a partir del modelo o del nombre del caso.

No se declarará un watchdog real ni se cerrará S06 por superar la simulación.
