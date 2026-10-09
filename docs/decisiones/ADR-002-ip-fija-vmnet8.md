# ADR-002 — Direccionamiento IPv4 estable de la VM de administración NETLAB360

**Fecha:** 2026-10-09 (Panamá). **Estado:** propuesta condicionada; la IP fija todavía **NO ha sido aplicada**. **Issue:** #39, vinculada a #38, #10, #1.

## Problema

`netlab360-lab` recibe `192.168.47.130/24` por DHCP en VMware NAT/VMnet8. Esta red se comparte con VMs de otras materias y se han reutilizado direcciones IP; Windows conserva claves antiguas SSH para `.130`. Es preferible una IP estable, sin deshabilitar la validación de identidad del servidor.

## Observaciones verificadas

| Componente | Valor |
|---|---|
| Red | `192.168.47.0/24` |
| Interfaz Windows VMware VMnet8 | `192.168.47.1/24` |
| VMware NAT gateway | `192.168.47.2` |
| Ubuntu `ens33` antes del cambio | `192.168.47.130/24` por DHCP |
| Hostname | `netlab360-lab` |
| Cuenta | `rc-aa-ec` |
| DHCP pool VMware | PENDIENTE comprobar en Virtual Network Editor |
| DNS de DHCP | PENDIENTE registrar desde NetworkManager |

## Decisión propuesta

- Candidata `192.168.47.40/24`, **sujeta a comprobación**: fuera del intervalo DHCP, no asignada ni reservada para otra VM.
- Mantener `192.168.47.2` como ruta predeterminada si la configuración del NAT sigue igual.
- Usar `nmcli` de Ubuntu Desktop NetworkManager para fijar IPv4 manual y DNS obtenido/validado del perfil DHCP vigente. No editar simultáneamente Netplan o archivos de NetworkManager por diferentes mecanismos.
- Mantener el usuario SSH `rc-aa-ec`; el usuario `root` no es el esperado.
- Conservar/restablecer el perfil DHCP previo si falla el cambio. Aplicar desde la consola local de la VM, no mediante SSH durante el cambio.
- El host físico de Windows debe poder establecer sesión por VMnet8 sin port forwarding en el NAT.

## Comprobaciones previas obligatorias

1. VMware Workstation → **Edit → Virtual Network Editor → VMnet8 → DHCP Settings**, verificar `Start IP address` y `End IP address`; no modificar otros pools ni rangos.
2. VMware → NAT Settings, verificar gateway.
3. Revisar inventario de VMs y direcciones estáticas; desde Windows revisar si candidata responde y datos ARP, sin considerar una falta de respuesta prueba definitiva de disponibilidad.
4. En Ubuntu: `nmcli -t -f NAME,DEVICE,TYPE connection show --active`; `nmcli -f IP4.DNS,IP4.GATEWAY device show ens33`.

## Seguimiento

- [ ] Rango DHCP validado.
- [ ] IP candidata seleccionada y sin conflicto.
- [ ] Configuración manual guardada y aplicada.
- [ ] Dirección/ruta/DNS validados tras reconectar.
- [ ] SSH al nuevo IP confirmado con identidad verificada y claves del cliente.
- [ ] Documentación actualizada con el resultado real y procedimiento de rollback.

**Nota de seguridad:** no reutilizar ni registrar la contraseña que fue revelada en el chat. Documentar únicamente procedimiento de credenciales.
