# Validación técnica de la infraestructura multisede — S02

**Alcance:** resultados comprobados de la topología de tres sedes que constituye la base de las fases siguientes.

| Componente | Prueba o criterio | Resultado |
|---|---|---|
| Routers | FRRouting en HQ, S1 y S2, tres contenedores con aislamiento de red | Comprobado |
| WAN | Cuatro enlaces de transporte S1/S2 y rutas OSPF principales/respaldo | Comprobado |
| OSPF | Adyacencias FULL HQ 4/4, S1 2/2 y S2 2/2 | Comprobado |
| Conectividad | Selección de FIB principal 6/6, loopbacks 6/6 | Comprobado |
| Segmentación LAN | Tres switches, nueve VLAN 802.1Q, nueve gateways y hosts de laboratorio | Comprobado |
| Aplicación HTTP | Comunicación intersede y restricciones ACL diferenciadas | Comprobado |
| Recuperación | Conmutación `s1p→s1b→s1p` y `s2p→s2b→s2p` | Comprobado |
| Gestión | Interfaz `ens33 192.168.47.40/24` y ruta administrativa conservadas | Comprobado |

## Evidencia

El conjunto S02 reúne **nueve imágenes PNG** originales bajo `evidencias/capturas/fase2/`, con manifestaciones SHA-256 y registros de validación de FRR, WAN, LAN y HTTP/ACL.

La infraestructura virtualizada **no equivale a redundancia física**. Los resultados de conmutación corresponden a los enlaces y fallas acotadas observadas. Durante S05 reutilizamos esta topología y validamos extensiones HTTP HA, LACP y SDN sin atribuirlas retroactivamente a S02.

[Topología implementada](../../topologias/s02-frr/README.md) · [IPAM](../../inventario/ipam/topologia-s02.yaml) · [Capturas S02](../../evidencias/capturas/fase2/README.md).
