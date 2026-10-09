# Inventario inicial del anfitrión y de la VM NETLAB360

**Fecha de inspección:** 2026-10-09 (hora local de Panamá).
**Origen:** dos capturas facilitadas por el usuario (VMware) y salida de PowerShell 7.6.6 (Windows).
**Estado al 2026-10-09:** 8 vCPU visibles en VMware; VM encendida por el usuario y proceso de instalación Ubuntu iniciado. Sistema invitado y acceso SSH aún sin verificar.

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
| Encendido | El usuario confirma que **ya encendió** la VM para instalar Ubuntu | Esperar resultado de instalación y hacer post-check |
| RAM | 16 GB | Mantener para MVP |
| CPU | **8 vCPU reconocidas por VMware** en captura posterior (previamente 2 vCPU) | Verificar `nproc=8` en Ubuntu; distribución socket/core no visible en esta captura |
| Disco | 160 GB, **SCSI** | Mantener; no convertir sin necesidad |
| Red | NAT | Mantener, sin Bridged |
| CD/DVD | En captura posterior se ve CD/DVD (SATA): `Archivo C:\\Users...` | ISO al parecer montada para instalación; desmontar imagen o quitar `Connect at power on` tras instalar y reiniciar |
| Ubicación | `C:\Users\ruben\Documents\Virtual Machines\NETLAB360-Ubuntu-Desktop\...` visible en captura | Confirmar ruta exacta y espacio libre suficiente |
| Firmware UEFI | No mostrado | Revisar `Options → Advanced` |
| Ubuntu Desktop | Usuario informa que inició la instalación | Confirmar `VERSION_ID` y release efectivo al concluir |

## Protocolo de comprobación

- [x] Inspección visual de versión VMware, procesador/RAM/disco del anfitrión.
- [x] Comprobación de que existe la VM y su CPU actual está en 2 vCPU.
- [x] VMware muestra 8 vCPU tras el ajuste (captura verificada). Falta verificar su distribución exacta y `nproc` en Ubuntu.
- [ ] Comprobar firmware UEFI y unidad CD/DVD; NAT ya observada, ubicación de la VM identificada.
- [ ] Captura final de configuración de la VM apagada.
- [ ] Verificar versión y hash de ISO Ubuntu Desktop; el usuario ya inició instalación.
- [ ] Probar arranque e inventario real del sistema invitado antes de cerrar #10.

## Restricciones

- No afirmar que hay 8 vCPU configuradas antes de recibir captura posterior.
- No activar virtualización anidada para Docker/FRR/OVS salvo una necesidad comprobada.
- No introducir credenciales, UUID, MACs reales o imágenes completas de disco en Git.
- No declarar completa la fase S01: todavía no hay implementación de red ni pruebas funcionales.

**Guía de continuación:** [Instalación Ubuntu Desktop y SSH](02-ubuntu-desktop-instalacion-ssh.md), issue #38.

**Trazabilidad:** [ADR-001](../decisiones/ADR-001-vmware-vm-sin-iso.md), [issue #10](https://github.com/recm0708/netlab360/issues/10), [issue #34](https://github.com/recm0708/netlab360/issues/34).
