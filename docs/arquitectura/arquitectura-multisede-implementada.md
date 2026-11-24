# Arquitectura implementada de NETLAB360

## Descripción del sistema

Implementamos una red empresarial multisede sobre **una máquina virtual Ubuntu Desktop**. El laboratorio separa el plano administrativo de las redes virtuales, incorpora routers FRRouting con OSPF, switches Linux con VLAN 802.1Q y servicios de observabilidad que obtienen información de la infraestructura activa.

## Plano de administración y topología

La VM `netlab360-lab` utiliza `ens33 192.168.47.40/24`, puerta de enlace `192.168.47.2` y la red NAT VMnet8 exclusivamente para administración. Los segmentos del laboratorio no utilizan `ens33` como enlace WAN ni exponen directamente los dominios SDN experimentales a esa red.

| Dominio | Componentes implementados |
|---|---|
| HQ | Router FRRouting, switch virtual, VLAN110/120/130, backend HTTP y frontal, agregador LACP |
| S1 | Router FRRouting, switch virtual, VLAN210/220/230, backend alternativo HTTP y agregador LACP |
| S2 | Router FRRouting, switch virtual, VLAN310/320/330, cliente de observación HTTP y agregador LACP |
| WAN | Enlaces `s1p/s1b` y `s2p/s2b`, rutas OSPF preferidas/respaldo |
| SDN | Dominio independiente Open vSwitch y Faucet, VLAN410 y VLAN420 |
| NOC | API y vistas de topología, rutas FIB, estado HTTP, LACP y controlador OpenFlow |

Las direcciones, interfaces y parámetros declarativos se encuentran en [IPAM](../../inventario/ipam/topologia-s02.yaml), y la configuración FRR versionada en [topología S02](../../topologias/s02-frr/README.md).

## Encaminamiento y segmentación

FRRouting distribuye rutas entre HQ, S1 y S2 mediante OSPF. Comprobamos cuatro adyacencias FULL en HQ y dos en cada sucursal, con preferencia por los enlaces primarios y conmutación a enlaces de respaldo bajo falla controlada. Tres conmutadores Linux y nueve VLAN ofrecen segmentación por sede y servicio.

## Agregación y disponibilidad de aplicación

Cada sede utiliza un bond LACP IEEE 802.3ad con dos miembros virtuales sobre su VLAN de servicios. Verificamos pérdida de un miembro y recuperación **2→1→2** sin reemplazar los enlaces WAN enrutados.

Los servicios HTTP poseen dos backends lógicos: HQ (`10.70.20.21`) y S1 (`10.71.20.21`), con frontal en HQ (`10.70.20.23`) y observación desde S2. Un ensayo de interrupción del backend HQ acreditó la secuencia **HQ→S1→HQ** mediante 17 observaciones.

## Segmento definido por software

El bridge OVS `br-s05-sdn` trabaja separado de los switches S02. Faucet instala reglas OpenFlow para permitir A↔B en VLAN410 y aislar el host C en VLAN420. Comprobamos conectividad y aislamiento con ICMP, además de la restauración del puerto virtual `sdna0`.

## Observabilidad

El exportador S04, los registros Prometheus/SQLite y el NOC de S05 permiten consultar topología, salud de los servicios, rutas FIB, LACP y SDN. Los estados de fuente no disponible no se presentan como fallas de conectividad confirmadas.

## Alcance y limitaciones

La arquitectura está implementada en una sola VM. Las conmutaciones probadas acreditan recuperación lógica de enlaces o backends, **no** tolerancia a la pérdida del host, del hypervisor ni del almacenamiento. La reconstrucción automatizada tras reiniciar Ubuntu sigue sin validarse.

[Diseño HA](../diseno/s05-ha-servicios-multisede.md) · [LACP](../diseno/s05-lacp-8023ad-multisede.md) · [SDN](../diseno/s05-dominio-sdn-ovs-faucet.md) · [Acta S05](../gestion/s05-acta-aceptacion-tecnica.md).
