# ADR-003 — Estrategia de redes virtuales aisladas

**Fecha:** 2026-10-12. **Estado:** Propuesta, pendiente de aceptación y pruebas.

En NETLAB360, la administración de Ubuntu utiliza VMnet8, IP 192.168.47.40/24 en ens33. La red empresarial utilizará subredes privadas distintas, declaradas en inventario/ipam/topologia-b1.yaml.

El precheck del 12 de octubre confirmó los módulos 8021q, bonding, openvswitch, veth y bridge disponibles en el kernel Linux 7.0.0-38. Únicamente bridge estaba cargado; FRR, OVS CLI y Containerlab no se han instalado.

## Alternativas de laboratorio

1. **Namespaces Linux + veth + Linux bridge:** buen primer ejercicio porque las utilidades del kernel ya existen; permite explorar aislamiento, VLAN y conexiones L2. No demuestra automáticamente OSPF, LACP ni SDN.
2. **Open vSwitch:** candidato para el plano L2 cuando se implemente Faucet; requiere instalar utilidades y verificar aislamiento de ens33.
3. **Containerlab:** candidato a topología declarativa y repetible, sujeto a verificación de compatibilidad de Ubuntu, Docker y soporte del tipo de nodo.

## Elección preliminar

Realizar primero una prueba corta aislada de namespace/veth/bridge con procedimiento de limpieza; después añadir FRRouting en routers aislados para demostrar OSPF con las WAN 10.78.0.0/30 y 10.78.0.4/30. Introducir OVS y LACP en la etapa específica de switches/SDN, sin llamar LACP a dos rutas WAN.

**Condición previa:** confirmar una instantánea VMware denominada NETLAB360-BASE-HERRAMIENTAS; no conectar ens33 a bridges ni cambiar IP/rutas del sistema anfitrión. Los controles y resultados deberán registrarse en la issue #11 y en el estado de continuidad.

**No se ha creado ningún namespace, router ni switch del proyecto.**
