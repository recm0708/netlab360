# Topología FRRouting dual-WAN — S01

Construimos un escenario inicial de **dos routers HQ/S1** con configuraciones FRRouting 10.7.1 versionadas en [`configs/`](configs/). Evaluamos preferencia OSPF, caída de WAN principal, conmutación y restauración de enlace.

| Enlace | Prefijo | Costo OSPF |
|---|---|---:|
| HQ–S1 principal | `10.78.0.0/30` | 10 |
| HQ–S1 respaldo | `10.78.0.4/30` | 100 |

Las loopbacks fueron `10.79.0.1/32` (HQ) y `10.79.0.2/32` (S1). Registramos adyacencias Full, rutas preferidas y comunicación HTTP en estados estables. No extrapolamos esa prueba a disponibilidad continua.

Este prototipo es distinto del [despliegue integrado S02](../s02-frr/README.md). Mantuvimos separado `ens33` y la red de gestión VMware durante las pruebas.
