# NETLAB360 — LACP IEEE 802.3ad con dos enlaces: negociación, falla y restauración VERIFICADAS

**Fecha real:** 13/10/2026, 20:43:23–20:51:35, Panamá (UTC−05).  
**Fuente de prueba:** transcripción completa de comandos y salida de Ubuntu aportada por operador, pasos 105–114. **Los cuatro PNG LACP todavía no se han recibido**, solo salida de terminal y sus bloques de captura. **Lote 03** (B2-L2/L3/B3) sí recibió 20 PNG reales auditados, aún pendientes de push binario ([auditoría lote03](../evidencias/04-auditoria-visual-lote03-2026-10-13.md)).

## Precheck y arranque

- Operador hizo `git pull --ff-only` desde `6a3e50f` hasta `a8a9879`, limpio; `bash -n scripts/laboratorio/b2-lacp-8023ad-dos-enlaces.sh` = `RESULTADO_SINTAXIS_LACP=0`.
- Kernel `7.0.0-38-generic`; bonding NO estaba cargado antes de prueba, pero `modinfo bonding` indicó módulo disponible `/lib/modules/7.0.0-38-generic/kernel/drivers/net/bonding/bonding.ko.zst`. El arranque posterior creó `bond0` correctamente: **no faltaba instalar ningún programa**.
- Precheck Docker/netns vacíos, `ens33 UP 192.168.47.40/24`, GW `192.168.47.2 dev ens33`, Git limpio.

## Prueba real de negociación y servicio

Se crearon **solo** namespaces `nl360-lacpa` y `nl360-lacpb`, un bonding `bond0` IEEE802.3ad activo en cada uno, dos enlaces veth `a1↔b1` y `a2↔b2`. Subred aislada de benchmarking `198.18.250.0/30`, servidor HTTP Python en B `198.18.250.2:8080`, cliente A `198.18.250.1`. Velocidad veth reportada **10000 Mbps por esclavo** es dato de interfaz virtual, **no medición de ancho de banda ni velocidad de NIC real**.

| Bloque terminal | Hora | Puertos en agregador A/B | Estado de enlace | HTTP |
|---|---|---|---|---|
| `B2_LACP_01` | 20:43:32 | 2/2 | `a1,a2,b1,b2` MII up, Actor y Partner LACP activo, aggregator ID1 | `HTTP_LACP_DOS_ENLACES=OK`, primer sondeo |
| `B2_LACP_02` | 20:43:37 | 1/1 | `a1,b1` MII down, Link Failure Count 1; `a2,b2` up | `HTTP_LACP_UN_ENLACE=OK`, primer sondeo |
| `B2_LACP_03` | 20:43:44 | 2/2 | `a1,b1` MII up de nuevo con contador histórico 1; ambos activos | `HTTP_LACP_ENLACE_RESTAURADO=OK`, primer sondeo |

Todos los `/proc/net/bonding/bond0` mostraron `Bonding Mode: IEEE 802.3ad Dynamic link aggregation`, `LACP active: on`, `LACP rate: fast`, `MII Status: up`. Tráfico HTTP devolvió `NETLAB360_LACP_HTTP_OK` en los **tres estados estabilizados**.

**Resumen:** `LACP_8023AD_TRES_ESTADOS=OK`, `RESULTADO_B2_LACP=0`, `RESULTADO_EJECUCION_LACP=0` y `RED_GESTION_INTACTA=SI`. Log local real `~/netlab360-bootstrap/evidencias/b2-lacp-8023ad-20261013-204323.log`, todavía no archivado en GitHub.

## Evidencia del cierre B2_LACP_04_FINAL (20:51:35)

`sudo docker ps -a` sin contenedores, `sudo ip netns list` vacío, `ens33=192.168.47.40/24`, default `192.168.47.2` intactos, `systemctl is-active docker ssh open-vm-tools` devolvió tres `active`, Git `## main...origin/main` limpio respecto al último pull local **antes de los nuevos commits de esta actualización**.

**Faltan recibir y auditar visualmente:** `B2_LACP_01_Agregacion_Dos_Enlaces.png`, `B2_LACP_02_Falla_Un_Enlace.png`, `B2_LACP_03_Restauracion_Dos_Enlaces.png` y `B2_LACP_04_Postcheck_Final.png`. Como los bloques fueron emitidos, las fotos se presumen tomadas según convención del usuario, pero **no son PNG recibidos en esta conversación**, ni se consideran publicados.

## Puntuación y límites

**Matriz provisional S01:** 59→**63/100 (+4)** en bloque `Redundancia LAG/LACP, equipos, servidor dual-NIC` (0→4/10). Concedidos por comportamiento negociado de agregación y mantenimiento de servicio al apagar un miembro. Los otros 6 puntos de ese bloque siguen pendientes por redundancia de equipos/servidor dual-NIC e integración funcional; puntuación **no equivale a nota docente**.

**No se ha probado:** doble NIC física del host, bond sobre ens33, switch redundante, failover de equipo/router, zero-packet-loss HTTP durante la caída ni rendimiento agregado real. El laboratorio deliberadamente no modificó VMnet8, ens33, firewall ni tabla de rutas del host.

**Siguiente foco recomendado:** dual-NIC del **servidor dentro de namespaces aislados con pruebas de failover (active-backup)**, seguido de integración IaC. No ejecutar LACP otra vez solo para obtener fotos: los bloques existentes en el log son suficientes.
