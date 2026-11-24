# ADR-003 — Aislamiento de redes virtuales

## Contexto

Los experimentos de WAN, VLAN y control SDN deben funcionar sin alterar la interfaz administrativa ni interferir con otros laboratorios conectados a VMware VMnet8.

## Decisión

Implementamos los segmentos empresariales mediante namespaces Linux, contenedores FRRouting, enlaces virtuales, bridges y VLAN 802.1Q. El dominio SDN de la fase 05 emplea un bridge dedicado de Open vSwitch controlado por Faucet.

La interfaz `ens33` conserva `192.168.47.40/24` con puerta de enlace `192.168.47.2` y no participa en las pruebas de conmutación WAN ni de pérdida de enlaces internos.

## Resultados

Comprobamos rutas OSPF y recuperación WAN, conectividad entre sedes, segregación de VLAN, operación LACP y aislamiento del dominio SDN. Los ensayos mantuvieron la red administrativa operativa.

## Limitaciones

El aislamiento corresponde a recursos virtuales dentro de una VM. Su recuperación tras un apagado completo del sistema invitado requiere un proceso adicional que no se considera demostrado.

## Documentación relacionada

[Arquitectura multisede](../arquitectura/arquitectura-multisede-implementada.md) · [Implementación SDN](../diseno/s05-dominio-sdn-ovs-faucet.md).
