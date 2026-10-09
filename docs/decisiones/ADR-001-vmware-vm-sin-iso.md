# ADR-001 — Máquina virtual base VMware sin ISO

- **Fecha:** 2026-10-09 (Panamá)
- **Estado:** aprobada para planificación, pendiente de comprobación del anfitrión.
- **Issues relacionadas:** #1, #10 ([002]), #34 ([026]) y #29 ([021]).
- **Decisión:** Crear desde cero una única máquina virtual Ubuntu Desktop en VMware Workstation Pro mediante asistente **Custom (Advanced)** y **I will install the operating system later**; no conectar imagen ISO ni iniciar la VM durante la preparación del hardware.

## Candidatos y recursos

| Parámetro | Selección propuesta |
|---|---|
| Nombre de VM | NETLAB360-Ubuntu-Desktop |
| Invitado | Linux → Ubuntu 64-bit |
| Distribución | Ubuntu Desktop 26.04.1 LTS, sujeto a comprobar soporte de Guest OS en la versión de VMware instalada |
| Hipervisor | Preferir VMware Workstation Pro 26H1u1 por correcciones de seguridad; verificar Help → About |
| Firmware | UEFI; Secure Boot según compatibilidad comprobada (preferente activado) |
| vCPU | 8 vCPU (1 processor × 8 cores), revisar disponibilidad del host |
| RAM | 16 GiB (16384 MiB), revisar disponibilidad del host |
| Disco virtual | 160 GiB, aprovisionamiento dinámico, dividir en varios archivos para transferencia |
| Controladora | NVMe o LSI Logic SAS según compatibilidad/autoselección del asistente |
| NIC inicial | Una NIC virtual NAT (VMnet8 por defecto), conectar al encender tras instalar SO |
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

- [ ] Confirmar versión exacta y compilación VMware instalada (Help → About).
- [ ] Verificar CPU, RAM, almacenamiento disponible, VT-x/AMD-V, firmware y compatibilidad de host.
- [ ] Confirmar ruta de almacenamiento y espacio suficiente; no asumir unidad C:\.
- [ ] Capturar valores elegidos en el asistente, antes de pulsar Finish.
- [ ] Crear la VM y comprobar que está apagada, sin ISO.
- [ ] Instalar Ubuntu posteriormente usando ISO validada; mantenimiento y comprobaciones.
- [ ] Registrar inventario en `docs/infraestructura/` y enlazar evidencia a #10 y #34.

## Referencias oficiales consultadas

- Broadcom KB 332659: asistente Workstation, opción *I will install the Operating System later*: https://knowledge.broadcom.com/external/article/332659/creating-a-workstation-virtual-machine-u.html
- Broadcom KB 315434: creación y configuración de VM en Workstation: https://knowledge.broadcom.com/external/article/315434/create-virtual-machines-in-vmware-workst.html
- Aviso de seguridad Broadcom, versión corregida 26H1u1: https://support.broadcom.com/web/ecx/support-content-notification/-/external/content/security-advisories/0/38288

**Nota:** Los recursos son objetivos preliminares, no valores ya aplicados. Se documentará configuración real del anfitrión antes de concretarlos.
