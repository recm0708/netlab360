# ADR-002 — IPv4 fija de administración para NETLAB360

**Fecha:** 2026-10-09 (Panamá). **Estado:** implementada y validada. IP fija y autenticación SSH por clave comprobadas después del reinicio. **Issues:** #39 y #38.

## Antecedentes y reserva

VMware VMnet8 usa `192.168.47.0/24`, con adaptador Windows `192.168.47.1/24`, puerta de enlace y DNS NAT `192.168.47.2`. El intervalo DHCP, comprobado visualmente en Virtual Network Editor, es **`192.168.47.128` hasta `192.168.47.254`**.

Las direcciones que el equipo declaró reservadas son: `.1`, `.2`, `.10`, `.129`, `.137`, `.145`, `.146`, `.149`, `.150`, `.151` dentro de la red 192.168.47.0/24. Algunas son históricas y pueden estar sujetas a DHCP; no reasignarlas.

Se eligió **`192.168.47.40/24`** porque está fuera del pool DHCP y de las reservas identificadas. `arping -D -I ens33 -c 3 192.168.47.40` emitió 3 solicitudes con 0 respuestas. Esto no prueba absolutamente que no exista un equipo apagado con la misma IP; se conserva una reserva administrativa para NETLAB360.

## Configuración realizada en Ubuntu

- Hostname `netlab360-lab` y cuenta Linux `rc-aa-ec`.
- Interfaz: `ens33`.
- Perfil nuevo NetworkManager `netlab360-gestion` con `ipv4.method manual`, IP `192.168.47.40/24`, gateway `192.168.47.2`, DNS `192.168.47.2` y `1.1.1.1`.
- Se deshabilitó `connection.autoconnect` del perfil anterior `netplan-ens33` sin eliminarlo, para facilitar la recuperación.
- Tras cambiar el perfil, `ip -4 -br address`, `ip route`, `nmcli connection show --active` y `resolvectl` confirmaron la configuración.
- Gateway: 4 respuestas ICMP de 4 (0 % pérdidas).
- Internet (`1.1.1.1`): 4 respuestas de 4 (0 % pérdidas).
- DNS: `getent ahostsv4 ubuntu.com` resolvió direcciones.

## Acceso remoto

La antigua dirección DHCP `192.168.47.130` tenía una clave SSH antigua en el `known_hosts` de Windows. **No se borró esa clave**, porque ya no se emplea esa dirección.

La huella ED25519 del servidor obtenida directamente desde Ubuntu coincidió con la mostrada por el nuevo cliente SSH en Windows para `192.168.47.40`. El usuario aceptó la huella y obtuvo exitosamente una consola remota autenticada con contraseña en `rc-aa-ec@netlab360-lab`.

## Estado y pruebas finales

- [x] Pool DHCP visualmente comprobado: `192.168.47.128–254`.
- [x] Dirección de administración elegida fuera del DHCP y de las reservas declaradas; sin respuestas ARP en pruebas.
- [x] Perfil NetworkManager estático activado; perfil DHCP conservado.
- [x] IP, ruta, DNS y pruebas de conectividad validadas.
- [x] Huella SSH comprobada y sesión remota de Windows lograda con contraseña.
- [x] Identificación y procedimiento documentados sin guardar secretos.
- [x] Después del reinicio, permanece `192.168.47.40/24`, ruta por `192.168.47.2`, perfil `netlab360-gestion` y acceso remoto operativo.
- [x] Acceso remoto con llave Ed25519, verificación de clave pública y alias `ssh netlab360` funcional desde PowerShell, también tras reinicio.

## Restauración (desde consola local VMware)

```bash
sudo nmcli connection modify netplan-ens33 connection.autoconnect yes
sudo nmcli connection down netlab360-gestion
sudo nmcli connection up netplan-ens33
```

El cambio de dirección puede cerrar una sesión SSH; ejecutar rollback desde consola VMware. Si cambia el pool DHCP u otra VM requiere la dirección, revaluar la IP y registrar la decisión.

**Seguridad:** no reutilizar ni publicar contraseñas privadas en este proyecto.
