# Temporizador independiente y requisitos de rollback — Fase 06

## Precondiciones

S06-035 confirmó en VM real: cliente HQ VLAN120 nl360-s02-h-hq-120, interfaz eth0 UP con dirección 10.70.20.20/24 y gateway 10.70.20.1. La disciplina de colas actual es noqueue 0: root, sin netem previo. La red administrativa ens33 192.168.47.40/24 y el gateway 192.168.47.2, NOC, HA/LACP/SDN y la topología están intactos. Hubo 441 tests offline correctos.

**Advertencia:** que la interfaz tenga noqueue únicamente la hace candidata; no concede permiso para modificarla.

## Ensayo de temporizador

Comprobar que un temporizador systemd puede ejecutar una tarea independiente del proceso de Python que lo programó. El único efecto permitido es crear un archivo marcador privado con /usr/bin/touch mediante una unidad transitoria de systemd. NO se aplicará tc netem, ni se alterarán qdiscs, rutas o servicios.

Programa: scripts/s06/verificar_watchdog.py.

- Opción --check-only: revisa gestión, namespaces, IPAM y qdisc sin realizar cambios.
- Opción --test-timer: repite los prechecks y programa con sudo -n systemd-run una tarea que crea un marcador en el directorio privado ~/netlab360-bootstrap/s06/watchdog-tests/.
- Se verifican archivo marcador, qdisc original, red administrativa y reporte JSON.

La aparición del marcador verifica la programación y ejecución fuera del proceso Python. **NO** acredita que un rollback real ya funcione, que sobreviva a reinicios, ni que se pueda revertir un namespace eliminado.

## Requisitos de seguridad

1. **Permisos:** archivo ejecutor root-owned y no editable por el usuario de la aplicación; el usuario solo elige un ID de escenario allowlisted, no una ruta, comando ni shell libre.
2. **Exclusión mutua:** solamente una intervención activa, lock y estado persistido con escritura atómica.
3. **Precheck:** identidad de namespace, eth0, IP, gateway, estado qdisc original, NOC/OSPF y ens33. Abortar si los datos no coinciden.
4. **Temporizador previo:** armar watchdog independiente ANTES de aplicar cualquier qdisc. TTL estricto, verificación del armado y protección ante carreras.
5. **Cambio acotado:** si se habilita más adelante, modificar exclusivamente eth0 del cliente permitido; jamás ens33, interfaces Docker de gestión, bridges LACP, routers ni Faucet.
6. **Rollback con propiedad:** restaurar exclusivamente una qdisc del propio experimento que coincida con su identidad y estado; no borrar configuraciones ajenas ni alterar la propiedad de otros servicios.
7. **Pruebas adversas:** expiración del TTL, caída del proceso principal, bloqueo, reintento, fallo al aplicar, fallo al restaurar y retorno de servicios, todos primero mediante simulación.
8. **Ground truth:** registrar confirmación del estímulo independiente del predictor; no etiquetar datos UNKNOWN como NORMAL, DEGRADED o RECOVERY sin observación verificable.
9. **Evidencias:** conservar bitácoras privadas, cambios aprobados, estado anterior/posterior y comprobación de red administrativa y topología.

## Validación y límites

S06-036 verificó la creación independiente del marcador privado, 16 pruebas específicas y 457 offline. Conservó qdisc, gestión e infraestructura; no restauró una qdisc real. Las pruebas posteriores de [simulación](s06-rollback-simulacion.md), [guardia](s06-guardia-root-y-watchdog-noop.md) y [restauración aislada](s06-restauracion-aislada.md) acreditan capacidades distintas.
