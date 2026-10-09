# Inventario inicial del anfitrión y de la VM NETLAB360

**Fecha de inspección:** 2026-10-09 (hora local de Panamá).
**Origen:** dos capturas facilitadas por el usuario (VMware) y salida de PowerShell 7.6.6 (Windows).
**Estado al 2026-10-09:** Ubuntu Desktop 26.04.1 LTS instalado y reiniciado; 8 vCPU verificadas dentro del invitado; servicio SSH activo. La autenticación remota aún no está validada.

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
| Encendido | Instalación completada y reinicio gráfico verificado con nuevo Boot ID | Validar conexión remota |
| RAM | 16 GB | Mantener para MVP |
| CPU | **8 vCPU** en VMware y **`nproc=8`** dentro de Ubuntu | Verificado |
| Disco | 160 GB, **SCSI** | Mantener; no convertir sin necesidad |
| Red | NAT | Mantener, sin Bridged |
| CD/DVD | En captura posterior se ve CD/DVD (SATA): `Archivo C:\\Users...` | ISO al parecer montada para instalación; desmontar imagen o quitar `Connect at power on` tras instalar y reiniciar |
| Ubicación | `C:\Users\ruben\Documents\Virtual Machines\NETLAB360-Ubuntu-Desktop\...` visible en captura | Confirmar ruta exacta y espacio libre suficiente |
| Firmware UEFI | No mostrado | Revisar `Options → Advanced` |
| Ubuntu Desktop | **26.04.1 LTS (Resolute Raccoon)**; kernel **7.0.0-38-generic** | Verificado |

## Protocolo de comprobación

- [x] Inspección visual de versión VMware, procesador/RAM/disco del anfitrión.
- [x] Comprobación de que existe la VM y su CPU actual está en 2 vCPU.
- [x] VMware muestra 8 vCPU y el invitado confirma `nproc=8`.
- [ ] Comprobar firmware UEFI y unidad CD/DVD; NAT ya observada, ubicación de la VM identificada.
- [ ] Captura final de configuración de la VM apagada.
- [ ] Verificar versión y hash de ISO Ubuntu Desktop; el usuario ya inició instalación.
- [x] Probar arranque e inventario real del sistema invitado; falta acceso SSH desde Windows.

## Restricciones

- No afirmar que hay 8 vCPU configuradas antes de recibir captura posterior.
- No activar virtualización anidada para Docker/FRR/OVS salvo una necesidad comprobada.
- No introducir credenciales, UUID, MACs reales o imágenes completas de disco en Git.
- No declarar completa la fase S01: todavía no hay implementación de red ni pruebas funcionales.

## Inventario de Ubuntu instalado (2026-10-09)

| Parámetro | Evidencia |
|---|---|
| Hostname | `netlab360-lab` |
| Usuario local (cuenta grupal) | `rc-aa-ec` |
| Nombre visible | Proyecto Semestral TE2 |
| Idioma de instalación | Español de España |
| Teclado | Inglés US |
| Timezone | `America/Panama`; NTP sincronizado |
| Kernel | `7.0.0-38-generic` |
| Memoria detectada | 15 GiB; swap 4.0 GiB |
| Volumen raíz | `/dev/sda2`, 157 GB, 138 GB disponibles tras reinicio |
| Interfaces | `ens33` UP, `192.168.47.130/24`; `lo` |
| Gateway por DHCP | `192.168.47.2` |
| VMware VMnet8 (Windows) | `192.168.47.1/24`, interfaz Up |
| SSH | `openssh-server` instalado y servicio activo; escucha en `0.0.0.0:22` y `[::]:22` |
| VMware Tools | `open-vm-tools` activo; `open-vm-tools-desktop` instalado |
| Sistema | `apt update`, `apt upgrade`, paquetes básicos y `autoremove --purge` ejecutados; 7 paquetes de kernel antiguo eliminados |

**Estado de SSH remoto:** Windows rechazó la huella de host para una IP reutilizada (`REMOTE HOST IDENTIFICATION HAS CHANGED`). Además se intentó `root`; el usuario correcto es `rc-aa-ec`. Pendiente comparar huella desde consola de VMware, limpiar **solo** el registro antiguo de la IP, conectar correctamente y después preparar clave Ed25519. No desactivar verificaciones de host SSH.

**Cuentas y secretos:** nombres/grupo pueden documentarse; ninguna contraseña real se registrará en Git, capturas o manual. Se recomienda rotar la contraseña que fue compartida en el chat.

**Guía de continuación:** [Instalación Ubuntu Desktop y SSH](02-ubuntu-desktop-instalacion-ssh.md), issue #38.

**Trazabilidad:** [ADR-001](../decisiones/ADR-001-vmware-vm-sin-iso.md), [issue #10](https://github.com/recm0708/netlab360/issues/10), [issue #34](https://github.com/recm0708/netlab360/issues/34).
