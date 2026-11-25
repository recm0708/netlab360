# Infraestructura FRRouting multisede

## Descripción

Implementamos una topología virtual de tres sedes, HQ, S1 y S2, mediante contenedores FRRouting y enlaces aislados en Ubuntu.

## Componentes

- [Declaración Docker](docker-compose.yml) con tres routers FRRouting.
- [Inventario IPAM](../../inventario/ipam/topologia-s02.yaml).
- Cuatro enlaces WAN: `s1p`, `s1b`, `s2p`, `s2b`.
- Nueve VLAN de servicio repartidas entre las sedes.
- [Scripts del laboratorio](../../scripts/laboratorio/) para la creación y validación de enlaces.

## Resultados

Comprobamos adyacencias OSPF FULL **4/2/2**, seis rutas principales, seis pruebas entre loopbacks, nueve gateways de VLAN, conectividad LAN y restricciones HTTP/ACL. La conmutación WAN seleccionó los enlaces alternativos y posteriormente regresó a las rutas preferidas.

## Limitaciones

El entorno utiliza `network_mode: none` para los routers, de manera que los enlaces experimentales son creados explícitamente por el laboratorio. La interfaz de administración VMware no forma parte de las WAN.

## Documentación relacionada

[Validación de entorno, red y observabilidad](../../docs/validacion/s01-s04-resultados.md) · [Ansible](../../ansible/s03/README.md) · [NOC de observabilidad](../../servicios/noc-s04/README.md).
