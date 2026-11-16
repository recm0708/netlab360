# Diseño de LACP multisede — S05

**Nota de trazabilidad:** este archivo conserva su nombre histórico de diseño candidato, pero la integración descrita **ya fue implementada y probada** en HQ, S1 y S2.

## Arquitectura

Agregamos dos enlaces virtuales `veth` por sede mediante IEEE 802.3ad entre un cliente dedicado y un switch Linux. En cada switch, el bond actúa como único puerto lógico de la VLAN de servicios. Los enlaces WAN enrutados por FRRouting/OSPF permanecen independientes: **no** forman parte de los bonds LACP.

| Sede | VLAN de servicio | Cliente de laboratorio | IPv4 |
|---|---:|---|---|
| HQ | 120 | `nl360-s05-lacp-hq` | `10.70.20.40/24` |
| S1 | 220 | `nl360-s05-lacp-s1` | `10.71.20.40/24` |
| S2 | 320 | `nl360-s05-lacp-s2` | `10.72.20.40/24` |

Conservamos las troncales, puertos de servicios, HA HTTP, FRR, rutas OSPF e interfaz de administración de la plataforma. Los recursos agregados por S05 tienen nombres y estados de propiedad propios, diferenciados de los objetos S02.

## Comprobaciones

Validamos la agregación de **dos miembros activos** por sede y el paso controlado a un miembro durante una falla local, seguido de restauración a dos miembros (**2→1→2**). Las pruebas incluyeron conectividad y regresión de WAN, HTTP HA y red de administración. Las capturas S05_45–S05_57 y el análisis de los pilotos P1/P1B se conservan como evidencia.

El rendimiento de un único flujo TCP no se duplica necesariamente al habilitar dos miembros LACP; el reparto depende del algoritmo de hashing y de las tuplas de cada flujo. Las cifras iperf3 obtenidas en una sola VM no equivalen a throughput de redes físicas.

## Límites de operación

El desmontaje selectivo solo debe afectar los recursos S05 expresamente identificados, sin borrar `br0`, las troncales o namespaces S02. No repetimos el despliegue ni los ensayos de caída para completar tareas editoriales. En caso de suspensión de VMware, comprobamos su línea base tras reanudar antes de iniciar otros experimentos.

Resultados S05 · Análisis académico.
