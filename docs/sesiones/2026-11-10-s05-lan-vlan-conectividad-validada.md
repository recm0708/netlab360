# NETLAB360 S05 — LAN multisede, evidencia 21A/21B/22/23 y preparación de failover

**Corte:** sesión de validación S05 de noviembre 2026, en `netlab360-lab` (Ubuntu). **Fuentes:** salida original de `09_Despliegue_LAN_S05.txt`, `10_Conectividad_LAN_InterSedes.txt`, cuatro capturas PNG compartidas y comprobadas visualmente. Los PNG fueron recibidos en esta conversación; **aún no están importados como binarios al repositorio**.

## Despliegue y conectividad verificados

- **Lote 54R:** `S02_VLAN_CREADA` para HQ 110/120/130, S1 210/220/230, S2 310/320/330, tres `S02_ROUTER_LAN_REAPLICADA`, `S02_SWITCHES=3 VLAN=9 HOSTS=9`, `S02_LAN_UP=OK`, `S02_LAN_ESTADO=OK`. Estado LAN JSON válido y namespaces requeridos (**3 switches + 9 hosts = 12**) presentes. `LOTE54R_LAN_COMPLETADA=OK`.
- **Lote 55R:** los nueve pings desde namespaces host a su gateway devolvieron `ESTADO=OK` y `S05_GATEWAYS_9_DE_9=OK`. Las comunicaciones HQ→S1 (`10.71.10.10`), HQ→S2 (`10.72.10.10`) y S1→S2 (`10.72.20.20`) se comprobaron mediante ICMP, `S05_CONECTIVIDAD_INTERSEDE=OK` y `LOTE55R_CONECTIVIDAD=OK`.
- **Enrutamiento:** tras reconfiguración LAN, `show ip route ospf` presentó rutas `O>*` a seis prefijos LAN remotos desde HQ, por `10.78.0.2 dev s1p` y `10.78.0.10 dev s2p`, y rutas intersede de retorno en S1/S2 por sus correspondientes WAN principales.
- **Gestión:** `ens33=192.168.47.40/24` y puerta de enlace `192.168.47.2` permanecieron intactas; `main...origin/main` limpio.
- **Entrada por terminal:** el pegado inicial del lote 55R tuvo una interrupción de terminal (secuencia de pegado), pero su ejecución posterior produjo resultados completos y correctos en el archivo original. **No invalida** la conectividad verificada.
- **VMware:** el usuario indicó que administra manualmente las instantáneas, borró las anteriores y conservó la creada manualmente como `NETLAB360_S05_PreLAN_20261110`. No crear nuevas instantáneas mediante comandos sin petición expresa, ni restaurar/eliminar la existente durante pruebas.

## Cuatro capturas originales auditadas

La versión recibida por chat de cada PNG se comprobó como imagen y tiene los siguientes **hashes SHA-256 de bytes recibidos** (son hashes del adjunto del chat, **no** un manifiesto todavía incorporado a la VM ni al repositorio):

| Identificador oficial | Verificación de la evidencia | SHA-256 de copia recibida |
|---|---|---|
| `S05_21A_Creacion_Nueve_VLAN_y_Tres_Switches` | INICIO→FIN, nueve VLAN, tres FRR, `S02_LAN_UP=OK` | `2a4171d36489fa790670a7631460b8a10986aece5f03373190177837e7c5791d` |
| `S05_21B_Inventario_LAN_y_Gestion_Intacta` | INICIO→FIN, 3/9/9/12, `ens33` intacta, lote 54R OK | `3c3bdab6bed147b47213a1058ca5dadcd6f308de230503c24760eaba59a3d121` |
| `S05_22_Conectividad_Nueve_Gateways_VLAN` | INICIO→FIN, nueve resultados OK, `S05_GATEWAYS_9_DE_9=OK` | `7183d7ce7e42b821d73252752c72b16763088a4293b5e67d244aaa65f9f527e8` |
| `S05_23_Conectividad_Entre_Tres_Sedes` | INICIO→FIN, tres comunicaciones OK, gestión y Git correctos | `a9d09052595ee22ec766238f13eec60b1fce532db1d590182a56b622a1d51e58` |

**Dictamen:** cuatro evidencias aceptadas en su alcance; no requieren rehacerse. Los filtros terminales reproducen literalmente las líneas del registro que el usuario ya había generado, sin volver a ejecutar pruebas ni alterar los resultados. La importación de los PNG a GitHub sigue pendiente.

## Siguiente etapa: conmutación WAN, separada de HA de equipos

El script existente `scripts/laboratorio/s02-failover-wan.py` acepta `S1` o `S2`. Comprueba `wan-links-state.json`, identificadores de los tres Docker FRR, `network_mode:none`, rutas FIB principales en ambos sentidos y red `ens33` antes de tocar una sola interfaz **WAN primaria del namespace de R-HQ**. Baja temporalmente `s1p` o `s2p`, espera la FIB por `s1b` o `s2b`, verifica tráfico ICMP hacia loopbacks, comprueba la ruta de la otra sucursal y vuelve a subir la primaria en `finally`; la FIB principal debe recuperarse antes de declarar prueba completa.

**Obligatorio:** preflight solo lectura, una sucursal por vez, salida guardada en log con `tee`, parada ante fallo, inspección de retorno y captura oficial con delimitadores desde/hasta. El exporter S04/NOC v6 solo informa estado administrativo de interfaces y presencia de procesos: **no puede acreditar** elección de rutas, contadores de tráfico o tiempos de failover basándose en flags. Los ensayos de failover de enlace no prueban por sí mismos alta disponibilidad de routers/switches/servicios.

**Próximos nombres de evidencias:**
`S05_24_Failover_WAN_S1_y_Restauracion`,
`S05_25_Failover_WAN_S2_y_Restauracion`,
`S05_26_Postcheck_Failover_OSPF_FIB_y_Gestion`.
