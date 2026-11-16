# Diseño de agregación LACP — Fase 05

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

## Limitaciones

Las mediciones proceden de interfaces virtuales sobre una VM. No describen el rendimiento máximo de enlaces físicos ni constituyen evidencia de alta disponibilidad de hardware.

## Documentación relacionada

[Validación S05](../validacion/s05-integracion-y-aceptacion.md) · [Capturas S05](../../evidencias/capturas/fase5/README.md).
