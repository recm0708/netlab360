# Topología de referencia FRRouting — Fase 01

## Descripción

Construimos un escenario inicial de dos routers virtuales HQ y S1 con enlaces WAN principal y alternativo para evaluar la preferencia de rutas OSPF y su recuperación.

## Componentes

| Enlace | Red | Costo OSPF |
|---|---|---:|
| Principal HQ–S1 | `10.78.0.0/30` | 10 |
| Alternativo HQ–S1 | `10.78.0.4/30` | 100 |

Las interfaces de loopback se configuraron como `10.79.0.1/32` y `10.79.0.2/32`. Las configuraciones de los routers están disponibles en [configs](configs/).

## Resultados

Comprobamos el establecimiento de adyacencias OSPF FULL, el uso preferido del enlace principal y la transición al respaldo durante un ensayo controlado, seguido de recuperación.

## Limitaciones

El escenario es un prototipo de dos sedes. No representa la integración HQ/S1/S2 desarrollada en la fase 02 ni garantiza disponibilidad continua de enlaces físicos.

## Documentación relacionada

[Topología multisede de la fase 02](../s02-frr/README.md) · [Resultados de las fases 01–04](../../docs/validacion/s01-s04-resultados.md).
