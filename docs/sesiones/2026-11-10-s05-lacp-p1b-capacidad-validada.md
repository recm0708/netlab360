# NETLAB360 S05/P1B — Rendimiento LACP bajo afinidad CPU

**Ejecución reportada:** 10/11/2026, 11:22 (Panamá, UTC−05). **Fuente:** salidas de Ubuntu aportadas por el operador, lotes 24–26. **Estado:** ensayo aislado completo y validado por sus marcadores, cuatro JSON y SHA-256 local. Se confirmaron cinco capturas tomadas; los PNG no han sido recibidos ni auditados aquí. No afirmar superioridad física de LACP.

## Método

Script: [`s05-lacp-capacidad-comparativa.sh`](../../scripts/laboratorio/s05-lacp-capacidad-comparativa.sh), con `--precheck` y `--run`. Dos namespaces `nl360-s05-ca/cb`, bonds IEEE 802.3ad L3+L4, pares `veth` aislados en `198.18.252.0/30`, TCP `iperf3` 8 segundos por ensayo sin `-b`. Afinidad **servidor CPU 0,1 y cliente CPU 2,3**, prioridad `nice +10`, timeout y limpieza exclusiva. La velocidad medida pertenece a **transferencia memoria/kernel dentro de la misma VM**, no a puerto Ethernet o interfaz física VMware.

## Medidas comprobadas

| Prueba | Miembros | Flujos TCP | Caudal RX (Mb/s) | RX (Gb/s) | Retransmisiones TCP | CPU iperf local % | CPU remota % |
|---|---:|---:|---:|---:|---:|---:|---:|
| P1B-01, referencia | 2 | 1 | 70 205,77 | 70,206 | 2 | 98,32 | 71,07 |
| P1B-02, ocho flujos | 2 | 8 | 113 299,56 | 113,300 | 178 | 178,88 | 123,80 |
| P1B-03, degradado | 1 | 8 | 127 389,56 | 127,390 | 243 | 199,58 | 140,75 |
| P1B-04, restaurado | 2 | 8 | 118 303,70 | 118,304 | 75 | 186,04 | 131,32 |

Contadores TX de cada miembro en pruebas de 8 flujos:
- P1B-02: C1 = 64 864 197 868 B, C2 = 64 184 970 447 B → **50,26 % / 49,74 %**.
- P1B-03: C1 = 0 B, C2 = 144 064 657 356 B → **0 % / 100 %** (un miembro disponible).
- P1B-04: C1 = 94 737 868 740 B, C2 = 41 357 697 778 B → **69,61 % / 30,39 %**.

### Análisis y límites

Comparación con la misma cantidad de flujos: dos miembros activos 113 299,56 Mb/s frente a un miembro 127 389,56 Mb/s. **Relación 0,889** y variación **−11,06 %**, calculadas por el validador local. No demuestra que el bond de un miembro sea intrínsecamente más eficiente: cada escenario se midió una sola vez, de manera secuencial, sin diseño de repeticiones aleatorizadas, y el cliente `iperf3` alcanzó alrededor del **179–200 %** de CPU sobre un conjunto de dos vCPU. Por ello el resultado pudo estar limitado por CPU, scheduler, virtualización/cola, caché o variaciones de los flujos.

Un flujo con bond de dos miembros transportó todos los bytes de datos por C1 (C2 2 541 B); ocho flujos con dos miembros sí distribuyeron tráfico. La tasa sin `-b` no equivale a «capacidad máxima certificada» ni a rendimiento físico. Se registraron retransmisiones (2/178/243/75), por lo que no se declara transferencia sin pérdidas. La variación tras restauración es consistente con un escenario no perfectamente estable y necesita replicaciones antes de conclusiones causales.

## Integridad, red y evidencias

- `S05_P1B_PRECHECK=OK_SIN_CAMBIOS`; CPU fijadas 0,1/2,3; namespaces inicialmente libres.
- El agregador pasó **2→1→2** miembros activos en ambas puntas; en estado degradado el enlace C1 contabilizó 0 bytes TX, C2 transportó todo.
- `S05_RESULTADO_P1B=0`, `S05_P1B_RED_GESTION_INTACTA=SI` y `S05_P1B_LIMPIEZA=OK`. `ens33=192.168.47.40/24` y puerta de enlace `192.168.47.2` sin cambios; rama Git limpia; no quedaron namespaces de S05.
- Los **cuatro JSON** pasaron `python3 -m json.tool`. El manifiesto `MANIFIESTO_SHA256_S05_P1B_20261110.txt` pasó la comprobación local `sha256sum -c` para log+cuatro JSON (5/5 OK); **SHA numéricos no se adjuntaron en la transcripción**.
- Evidencia primaria local: `~/netlab360-bootstrap/s05/evidencias/lacp-p1b/S05_P1B_20261110-112215.log` y `UN_FLUJO_DOS.json`, `OCHO_DOS.json`, `OCHO_UNO.json`, `OCHO_RETORNO.json`. Los registros primarios binarios no están aún en GitHub.
- Capturas confirmadas: `S05_05_LACP_Referencia_Un_Flujo`, `S05_06_LACP_Capacidad_Ocho_Flujos_Dos_Enlaces`, `S05_07_LACP_Capacidad_Con_Un_Solo_Enlace`, `S05_08_LACP_Capacidad_Despues_Restauracion`, `S05_09_LACP_Limpieza_Final`.

## Próxima ruta

Acreditar la **ejecución de P1B**, con reservas metodológicas; conservar abierto el criterio de capacidad cuantitativa definitiva hasta disponer de varias repeticiones, perfiles CPU/host/VM, intervalos y variación. Priorizar integración real de redundancia de equipos (#32) y el diagrama S05/NOC (#64) con infraestructura multisede, en lugar de repetir pruebas LACP sin necesidad.
