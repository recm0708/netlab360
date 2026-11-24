# Preparación reproducible de Ubuntu y acceso SSH

Se instaló y validó **Ubuntu Desktop 26.04.1 LTS** como entorno único de laboratorio NETLAB360. VMware Workstation proporciona NAT de administración; los dominios FRRouting, VLAN y SDN permanecen aislados dentro del invitado.

## Sistema y conectividad

| Parámetro | Configuración |
|---|---|
| Nombre de host | `netlab360-lab` |
| Interfaz administrativa | `ens33` |
| IPv4 fija | `192.168.47.40/24` |
| Gateway | `192.168.47.2` |
| Zona horaria | `America/Panama` |
| Servicios administrativos | SSH y open-vm-tools |
| Autenticación SSH | Par de claves Ed25519; claves privadas fuera de Git |

Las comprobaciones de instalación incluyeron `hostnamectl`, `/etc/os-release`, `ip -br address`, `ip route`, `nproc`, estado de servicios y acceso SSH desde Windows. La IP administrativa debe permanecer independiente de los ensayos de falla de WAN/OSPF, LACP y OVS/Faucet.

## Dependencias utilizadas

Instalamos herramientas de administración de redes Linux, Docker, FRRouting mediante contenedores, Ansible, OpenTofu, Python, Prometheus y Open vSwitch según los módulos. El inventario del proyecto mantiene las configuraciones e imágenes necesarias para repetir las pruebas; las bases de datos, el estado operativo y las credenciales se conservan fuera de Git.

## Seguridad y alcance de recuperación

Comprobamos autenticación SSH por clave, acceso de usuario no privilegiado y operaciones específicas con `sudo`. El sistema está diseñado para un entorno académico aislado; no se configuró como infraestructura productiva.

Una suspensión de VMware preserva temporalmente los recursos en memoria, pero un apagado del invitado no conserva automáticamente los namespaces efímeros. La recuperación tras reinicio requiere un procedimiento adicional de reconstrucción que no se considera validado.

[Inventario VMware](inventario-host-y-vmware.md) · [Red multisede](../../topologias/s02-frr/README.md) · [Acta S05](../gestion/s05-acta-aceptacion-tecnica.md).
