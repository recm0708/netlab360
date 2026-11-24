# Infraestructura de virtualización de NETLAB360

El laboratorio se ejecuta sobre una VM Ubuntu Desktop alojada en VMware Workstation Pro, con recursos del equipo anfitrión asignados de forma aislada de otras prácticas. Los datos siguientes corresponden al inventario técnico comprobado durante la preparación inicial del entorno.

| Recurso | Configuración observada |
|---|---|
| Sistema operativo anfitrión | Windows 11 Pro x64 |
| Procesador anfitrión | Intel Core i9-12900H |
| Memoria física anfitrión | Aproximadamente 64 GiB |
| Hipervisor | VMware Workstation Pro |
| Sistema operativo invitado | Ubuntu Desktop 26.04.1 LTS |
| Procesamiento virtual | 8 vCPU |
| Memoria de la VM | 16 GiB |
| Disco virtual | 160 GB SCSI |
| Adaptador VM | NAT, segmento VMware VMnet8 |
| Hostname Ubuntu | `netlab360-lab` |
| Red de gestión | `ens33 192.168.47.40/24` |
| Puerta de enlace | `192.168.47.2` |
| Zona horaria | `America/Panama` |

El laboratorio integra contenedores Docker, namespaces Linux y switches virtuales. Los recursos de red y aplicaciones se ejecutan en el mismo invitado, por lo que **no se considera validada tolerancia a pérdida del anfitrión ni reconstrucción automática tras apagar Ubuntu**.

Preservamos el tráfico de administración fuera de las WAN y VLAN simuladas. El acceso SSH desde Windows utiliza claves ED25519 y se restringe a la red administrativa autorizada; no versionamos contraseñas, llaves privadas ni tokens.

[Configuración de Ubuntu y acceso SSH](ubuntu-desktop-y-ssh.md) · [ADR de IP fija](../decisiones/adr-002-direccion-administrativa.md) · [Arquitectura implementada](../arquitectura/arquitectura-multisede-implementada.md).
