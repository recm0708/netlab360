# Inventario inicial del anfitrión y de la VM NETLAB360

**Fecha de inspección:** 2026-10-09 (hora local de Panamá).
**Origen:** dos capturas facilitadas por el usuario (VMware) y salida de PowerShell 7.6.6 (Windows).
**Estado:** entorno de invitado aún sin instalar; CPU virtual pendiente de corregir.

## Anfitrión Windows

| Parámetro | Valor observado |
|---|---|
| Sistema operativo | Windows 11 Pro, x64, compilación 26300 (captura VMware: 26300.9550) |
| CPU | Intel Core i9-12900H |
| Núcleos / procesadores lógicos | 14 / 20 |
| VirtualizationFirmwareEnabled | True |
| RAM instalada | 63.70 GB (VMware muestra 65228 MB) |
| VMware Workstation Pro | 26H1u1; versión 26.0.1, build 25688693 |
| C: libre | 425.57 GB |
| D: libre | 257.18 GB |
| Z: libre | 132.54 GB |
| Y: libre | 12.68 GB |
| HypervisorLaunchType / VSM | La consulta filtrada por `bcdedit` no devolvió coincidencias; esto no prueba que estén deshabilitados. |

## Máquina virtual existente

| Parámetro | Situación observada | Acción |
|---|---|---|
| Identificador | `NETLAB360-Ubuntu-Desktop` | Mantener |
| Encendido | VMware ofrece «Enciende esta máquina virtual»: apagada | No arrancar antes de verificar ISO |
| RAM | 16 GB | Mantener para MVP |
| CPU | **2 procesadores × 1 núcleo = 2 vCPU** | **Modificar a 1 procesador × 8 núcleos = 8 vCPU** |
| Disco | 160 GB, **SCSI** | Mantener; no convertir sin necesidad |
| Red | NAT | Mantener, sin Bridged |
| CD/DVD | SATA con detección automática | Verificar que no hay ISO asignada y que no está conectado al encender |
| Ubicación | `C:\Users\ruben\Documents\Virtual Machines\NETLAB360-Ubuntu-Desktop\...` visible en captura | Confirmar ruta exacta y espacio libre suficiente |
| Firmware UEFI | No mostrado | Revisar `Options → Advanced` |
| Ubuntu Desktop | Aún sin ISO ni sistema instalado | Instalación posterior |

## Protocolo de comprobación

- [x] Inspección visual de versión VMware, procesador/RAM/disco del anfitrión.
- [x] Comprobación de que existe la VM y su CPU actual está en 2 vCPU.
- [ ] Cambiar CPU a 1 socket × 8 cores (8 vCPU) y comprobar que se guardó.
- [ ] Comprobar firmware UEFI, configuración de CD/DVD, red NAT y ubicación.
- [ ] Captura final de configuración de la VM apagada.
- [ ] Descargar/verificar imagen Ubuntu Desktop compatible y continuar con instalación.
- [ ] Probar arranque e inventario real del sistema invitado antes de cerrar #10.

## Restricciones

- No afirmar que hay 8 vCPU configuradas antes de recibir captura posterior.
- No activar virtualización anidada para Docker/FRR/OVS salvo una necesidad comprobada.
- No introducir credenciales, UUID, MACs reales o imágenes completas de disco en Git.
- No declarar completa la fase S01: todavía no hay implementación de red ni pruebas funcionales.

**Trazabilidad:** [ADR-001](../decisiones/ADR-001-vmware-vm-sin-iso.md), [issue #10](https://github.com/recm0708/netlab360/issues/10), [issue #34](https://github.com/recm0708/netlab360/issues/34).
