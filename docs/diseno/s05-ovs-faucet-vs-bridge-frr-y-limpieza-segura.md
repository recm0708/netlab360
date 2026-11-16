# Diseño SDN — Open vSwitch y Faucet

## Descripción

Integramos un dominio de red definido por software para evaluar la segmentación y las políticas de comunicación mediante un controlador Faucet y un datapath Open vSwitch. Este dominio permanece independiente de los switches Linux y del encaminamiento OSPF que sostienen la red empresarial multisede.

## Arquitectura

| Elemento | Implementación |
|---|---|
| Bridge SDN | `br-s05-sdn` |
| Controlador | Contenedor `nl360-s05-faucet` |
| Puertos | `sdna0`, `sdnb0`, `sdnc0` |
| Namespaces | `nl360-s05-sdn-a`, `nl360-s05-sdn-b`, `nl360-s05-sdn-c` |
| VLAN 410 | Comunicación entre los hosts A y B |
| VLAN 420 | Aislamiento del host C |
| Protocolo de control | OpenFlow 1.3 |

Faucet establece reglas de conmutación en OVS. FRRouting conserva su función independiente de encaminamiento entre las tres sedes.

## Validación

Comprobamos que A y B podían comunicarse dentro de la VLAN 410 y que el host C permanecía aislado en la VLAN 420. También interrumpimos y restauramos el puerto `sdna0`, verificando posteriormente la conexión del controlador y la conservación de WAN, HTTP, LACP y administración.

Las reglas OpenFlow observadas indican la configuración del datapath en ese momento; no sustituyen las pruebas de conectividad ni representan una medida de capacidad del enlace.

## Limitaciones

La arquitectura dispone de un controlador Faucet en un solo entorno virtual. No se implementó redundancia física del controlador ni tolerancia a la caída del host. Las funciones de retirada selectiva de recursos permanecen protegidas para evitar la eliminación accidental del laboratorio activo.

## Documentación relacionada

[Arquitectura multisede](../arquitectura/arquitectura-multisede-implementada.md) · [Validación S05](../validacion/s05-integracion-y-aceptacion.md) · [Capturas S05](../../evidencias/capturas/fase5/README.md).
