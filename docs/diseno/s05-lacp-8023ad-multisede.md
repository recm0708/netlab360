# Diseño de agregación LACP

## Descripción

Implementamos agregación IEEE 802.3ad en HQ, S1 y S2 para analizar el comportamiento de enlaces redundantes en las LAN de servicios. Cada sede dispone de dos miembros virtuales asociados a un bond lógico.

## Arquitectura

| Sede | VLAN | Cliente virtual | IPv4 |
|---|---:|---|---|
| HQ | 120 | `nl360-s05-lacp-hq` | `10.70.20.40/24` |
| S1 | 220 | `nl360-s05-lacp-s1` | `10.71.20.40/24` |
| S2 | 320 | `nl360-s05-lacp-s2` | `10.72.20.40/24` |

Los bonds pertenecen a las redes de servicio y no reemplazan los enlaces WAN de FRRouting/OSPF.

## Validación

Comprobamos la operación inicial con dos miembros, la continuidad con un solo miembro durante una interrupción controlada y la recuperación posterior **2 → 1 → 2** en las tres sedes.

También evaluamos tráfico TCP con uno y varios flujos mediante pruebas iperf3. La distribución entre miembros depende de las características de los flujos y de la política del agregador; habilitar dos enlaces no implica duplicar la velocidad de una conexión individual.

### Ensayo piloto de distribución y continuidad P1

El 10 de noviembre de 2026 realizamos pruebas TCP con iperf3 en dos namespaces aislados, mediante un bond IEEE 802.3ad y dos pares veth. La política de distribución utilizó información de las capas 3 y 4.

El tráfico ofrecido se limitó a 120 Mb/s por flujo.

| Escenario | Flujos TCP | Caudal RX (Mb/s) | Retransmisiones |
|---|---:|---:|---:|
| Referencia con dos miembros | 1 | 120,06 | 0 |
| Distribución con dos miembros | 8 | 959,81 | 0 |
| Falla y retorno 2→1→2 | 8 | 960,31 | 553 |

En el escenario de ocho flujos, la distribución de bytes transmitidos fue aproximadamente 62,51 % y 37,49 % entre ambos miembros. Un único flujo utilizó predominantemente uno de los enlaces.

Durante la interrupción controlada, la transferencia pudo completarse y se recuperaron los dos miembros activos. Las 553 retransmisiones impiden afirmar continuidad perfecta o ausencia de perturbaciones.

El promedio de caudal no representa la duración exacta de una interrupción. Los límites de tráfico ofrecido tampoco equivalen a capacidad física máxima.

#### Procedencia de las mediciones

Los resultados anteriores corresponden exclusivamente a la ejecución original del 10 de noviembre. Una ejecución posterior produjo registros JSON diferentes y debe analizarse como una sesión independiente.

Se conserva el paquete técnico original en `~/netlab360-bootstrap/s05/evidencias/NETLAB360_S05_P1_LACP_EVIDENCIA_TECNICA_20261110.tar.gz`, junto con los procedimientos de auditoría y recuperación de registros.

Los análisis deben mantener separadas las ejecuciones P1 y P1B y evitar atribuir a una sesión los resultados de otra.

Procedimientos relacionados: [piloto LACP](../../scripts/laboratorio/s05-lacp-multistream-piloto.sh), [auditoría de procedencia](../../scripts/validacion/s05_auditar_origen_p1.py) y [recuperación de registros](../../scripts/validacion/s05_recuperar_p1_tar_historico.py).

### Ensayo comparativo de rendimiento P1B

El 10 de noviembre de 2026 realizamos un ensayo aislado de ocho segundos por escenario mediante iperf3 TCP, con afinidad diferenciada de CPU para cliente y servidor.

| Escenario | Miembros | Flujos | Caudal RX (Mb/s) | Retransmisiones |
|---|---:|---:|---:|---:|
| Referencia | 2 | 1 | 70205,77 | 2 |
| Agregación | 2 | 8 | 113299,56 | 178 |
| Degradación | 1 | 8 | 127389,56 | 243 |
| Restauración | 2 | 8 | 118303,70 | 75 |

Con ocho flujos, la distribución inicial entre miembros fue de 50,26 % y 49,74 %. Durante la degradación, el miembro restante transportó el 100 % del tráfico. Tras la restauración, la distribución fue de 69,61 % y 30,39 %.

El caudal medido con dos miembros fue inferior al observado con uno durante esta ejecución. Cada escenario se ejecutó una sola vez, de forma secuencial, bajo condiciones de virtualización y consumo elevado de CPU.

Los resultados demuestran agregación, distribución y continuidad dentro de una VM, pero no certifican capacidad física ni mejoras causales de rendimiento.

Los ensayos P1 y P1B conservan conjuntos de datos independientes. No deben mezclarse resultados de sesiones distintas.

## Limitaciones

Las mediciones proceden de interfaces virtuales sobre una VM. No describen el rendimiento máximo de enlaces físicos ni constituyen evidencia de alta disponibilidad de hardware.

## Documentación relacionada

[Validación de disponibilidad y SDN](../validacion/s05-integracion-y-aceptacion.md) · [Capturas de disponibilidad y SDN](../../evidencias/capturas/fase5/README.md).
