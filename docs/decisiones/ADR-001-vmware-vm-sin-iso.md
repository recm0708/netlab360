# ADR-001 — Entorno de virtualización

## Contexto

El proyecto requiere una infraestructura que permita ejecutar routers, switches virtuales y servicios de observabilidad en un entorno controlado. Para ello seleccionamos una máquina virtual Ubuntu Desktop en VMware Workstation, evitando introducir equipos físicos adicionales.

## Decisión

Utilizamos una única VM Ubuntu Desktop 26.04.1 LTS con ocho vCPU, 16 GiB de RAM y disco SCSI virtual de 160 GB. La interfaz de gestión opera mediante NAT VMnet8, separada de los dominios de laboratorio.

La configuración inicial del hardware virtual se realizó con el asistente avanzado de VMware. Posteriormente instalamos el sistema operativo y las dependencias necesarias de los componentes del proyecto.

## Justificación

La solución permite experimentar con FRRouting, OSPF, namespaces Linux, Docker, Open vSwitch, Ansible y herramientas de monitoreo sin intervenir la red física. También facilita la conservación del entorno entre sesiones.

## Limitaciones

La infraestructura se ejecuta sobre un único host y una única VM. Los escenarios de recuperación de enlaces y backends HTTP no constituyen redundancia del hipervisor ni tolerancia a la pérdida del equipo anfitrión.

## Documentación relacionada

[Infraestructura virtual](../infraestructura/01-inventario-host-y-vmware.md) · [Preparación de Ubuntu](../infraestructura/02-ubuntu-desktop-instalacion-ssh.md).
