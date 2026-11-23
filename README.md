# NETLAB360

**Plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede**

## Descripción

NETLAB360 es una plataforma de laboratorio desarrollada para diseñar, implementar y evaluar una red empresarial de tres sedes: HQ, S1 y S2. Integramos enrutamiento dinámico, segmentación, automatización de configuraciones, observabilidad y escenarios controlados de recuperación de servicios.

## Arquitectura y tecnologías

El laboratorio funciona sobre Ubuntu Desktop en VMware Workstation. La red administrativa está separada de los segmentos experimentales. Las WAN y VLAN virtuales utilizan FRRouting, OSPF, namespaces Linux y contenedores Docker; la plataforma incorpora OpenTofu, Ansible, Prometheus, Open vSwitch y Faucet.

| Componente | Función |
|---|---|
| FRRouting / OSPF | Encaminamiento dinámico y recuperación WAN multisede |
| VLAN / switching | Segmentación de tráfico por sede y servicio |
| OpenTofu / Ansible | Declaración de metadatos, configuración y reconciliación de FRR |
| Prometheus / NOC | Métricas, incidentes y representación del estado de la red |
| LACP 802.3ad | Agregación y recuperación de enlaces en las tres sedes |
| Open vSwitch / Faucet | Segmentación y control SDN de un dominio aislado |
| HTTP HA | Selección de backend principal y alternativo |

## Resultados de las fases

| Fase | Alcance realizado |
|---|---|
| S01 | Preparación del entorno, conectividad inicial y pruebas de referencia |
| S02 | Infraestructura multisede con cuatro enlaces WAN y nueve VLAN |
| S03 | Automatización de FRR, reconciliación y recursos locales OpenTofu |
| S04 | Métricas, incidentes y observabilidad de la red multisede |
| S05 | HTTP HA, LACP, SDN con Faucet y NOC integrado |
| S06–S08 | Funciones avanzadas y entrega final, sujetas a sus propias validaciones |

La validación final de S05 comprobó 21 namespaces, cuatro contenedores y seis servicios activos, así como la conmutación lógica HTTP **HQ → S1 → HQ**. Estas pruebas se realizaron dentro de una máquina virtual; no se atribuye a ellas redundancia física de servidores.

## Estructura del proyecto

- [Arquitectura implementada](docs/arquitectura/arquitectura-multisede-implementada.md)
- [Diseño de disponibilidad HTTP](docs/diseno/s05-ha-servicios-multisede.md)
- [Diseño de agregación LACP](docs/diseno/s05-lacp-8023ad-multisede.md)
- [Diseño SDN](docs/diseno/s05-ovs-faucet-vs-bridge-frr-y-limpieza-segura.md)
- [Validación S01–S04](docs/validacion/s01-s04-resultados.md)
- [Validación S05](docs/validacion/s05-integracion-y-aceptacion.md)
- [Evidencias gráficas](evidencias/capturas/README.md)
- [Topología FRRouting](topologias/s02-frr/README.md)
- [Automatización Ansible](ansible/s03/README.md)
- [Infraestructura declarativa OpenTofu](iac/s03/README.md)
- [NOC multisede](servicios/topologia-s05/README.md)
- [Plan maestro S06–S08, objetivos y criterios de aceptación](docs/diseno/s06-s08-plan-maestro-y-criterios.md)
- [Adquisición de telemetría S06 y diseño de sesiones de observación](docs/diseno/s06-adquisicion-observacional.md)
- [Pruebas de rendimiento RTT, pérdidas y HTTP S06](docs/diseno/s06-mediciones-rendimiento.md)
- [Diseño del programa interactivo S08 y catálogo de acciones](docs/diseno/s08-consola-interactiva-y-acciones.md)

## Alcance

El repositorio contiene el código y los documentos técnicos que describen el sistema desarrollado y sus resultados. Los registros privados y los recursos de ejecución propios de la VM se mantienen fuera del código fuente. Las ampliaciones no implementadas no se presentan como funcionalidades terminadas.
