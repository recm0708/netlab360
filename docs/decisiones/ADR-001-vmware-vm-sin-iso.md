# ADR-001 — Máquina virtual base VMware sin ISO

- **Fecha:** 2026-10-09 (Panamá)
- **Estado:** decisión aplicada parcialmente: VM creada; inspección del anfitrión realizada; ajuste de CPU y revisión de firmware/CD pendientes.
- **Issues relacionadas:** #1, #10 ([002]), #34 ([026]) y #29 ([021]).
- **Decisión:** Crear desde cero una única máquina virtual Ubuntu Desktop en VMware Workstation Pro mediante asistente **Custom (Advanced)** y **I will install the operating system later**; no conectar imagen ISO ni iniciar la VM durante la preparación del hardware.

## Candidatos y recursos

| Parámetro | Selección propuesta |
|---|---|
| Nombre de VM | NETLAB360-Ubuntu-Desktop |
| Invitado | Linux → Ubuntu 64-bit |
| Distribución | Ubuntu Desktop 26.04.1 LTS, sujeto a comprobar soporte de Guest OS en la versión de VMware instalada |
| Hipervisor | **Verificado:** VMware Workstation Pro 26H1u1 (26.0.1, build 25688693) |
| Firmware | UEFI; Secure Boot según compatibilidad comprobada (preferente activado) |
| vCPU | **Objetivo:** 8 vCPU (1 procesador × 8 núcleos). **Observado:** 2 procesadores × 1 núcleo = 2 vCPU; pendiente corregir |
| RAM | **VM observada:** 16 GB; **host:** 63.70 GB; mantener configuración actual |
| Disco virtual | **VM observada:** 160 GB SCSI; aprovisionamiento y división de archivo no comprobados |
| Controladora | **Observada:** SCSI. Mantener salvo necesidad justificada |
| NIC inicial | **Observada:** una NIC NAT |
| ISO | Ninguna por ahora. CD/DVD sin imagen y sin conectar al encender. |
| Aceleración anidada | No habilitar VT-x/EPT/AMD-V/RVI dentro del invitado salvo evidencia de necesidad; Docker/FRR/OVS no la requieren por sí mismos |
| Servicios invitados | Docker, redes por contenedores/namespaces, OpenTofu, Ansible, observabilidad, dashboard |

## Fundamento técnico

- Separar el sistema operativo anfitrión, NAT de administración y los segmentos internos creados por Docker/OVS.
- No exponer accidentalmente los segmentos de laboratorio a la LAN real.
- Facilitar portabilidad y exportación OVA, verificar reimportación.
- No activar arranque sin instalador: ausencia de sistema de arranque es esperada.
- No asignar conectividad puente (Bridged) ni interfaces extra de la VM hasta disponer de una necesidad validada.
- Revisar hardware y características antes de finalizar. Documentar configuración final con capturas.

## Pendientes de aprobación operacional

- [x] Confirmar versión exacta y compilación VMware instalada (Help → About): 26H1u1, 26.0.1 build 25688693.
- [ ] Verificar CPU, RAM, almacenamiento disponible, VT-x/AMD-V, firmware y compatibilidad de host. **CPU/RAM/discos/firmware de virtualización verificados; falta UEFI del invitado y compatibilidad final.**
- [x] Confirmar ubicación general de almacenamiento (C:, carpeta Documents\\Virtual Machines), con 425.57 GB libres en C: según PowerShell.
- [ ] Capturar valores elegidos en el asistente, antes de pulsar Finish.
- [x] Crear VM y comprobar que está apagada; el usuario indica que fue creada sin ISO. Aún falta comprobar conexión CD/DVD.
- [ ] Instalar Ubuntu posteriormente usando ISO validada; mantenimiento y comprobaciones.
- [x] Registrar inventario en `docs/infraestructura/01-inventario-host-y-vmware.md` y enlazar a #10 y #34.

## Referencias oficiales consultadas

- Broadcom KB 332659: asistente Workstation, opción *I will install the Operating System later*: https://knowledge.broadcom.com/external/article/332659/creating-a-workstation-virtual-machine-u.html
- Broadcom KB 315434: creación y configuración de VM en Workstation: https://knowledge.broadcom.com/external/article/315434/create-virtual-machines-in-vmware-workst.html
- Aviso de seguridad Broadcom, versión corregida 26H1u1: https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/security-advisories/0/38288

**Inspección 2026-10-09:** la VM ya existe con 16 GB RAM, SCSI de 160 GB, NAT y 2 vCPU; faltan aplicar/verificar 1 × 8 núcleos, firmware y ausencia de ISO. Inventario detallado en `docs/infraestructura/01-inventario-host-y-vmware.md`.
