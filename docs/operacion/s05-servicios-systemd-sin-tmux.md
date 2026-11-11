# NETLAB360 · Operación estable sin tmux ni seis sesiones SSH

**Preparación en GitHub:** 11/11/2026. **Estado:** código probado offline (CI) y pendiente de instalación y prueba EN VM. La VM está actualmente con NOC 9110/9130 **detenidos intencionalmente** tras `REINICIO_LIMPIO_PREPARADO=OK`. Los tres FRR siguen activos, `ens33=192.168.47.40/24`, default `.2`, HA sin estado ni despliegue. **No ejecutar lotes HA 84–86** hasta que las fuentes vuelvan a estar verificables.

## Objetivo

Reemplazar los procesos Python atados a sesiones SSH por dos servicios de sistema independientes:

- `netlab360-s04-exporter.service` ejecutado como **usuario normal** `rc-aa-ec`, solo localhost:9110.
- `netlab360-s05-noc.service` ejecutado como **usuario normal** `rc-aa-ec`, solo localhost:9130.
- Un único **ejecutable de lectura privilegiada, root:root 0755**, `/usr/local/libexec/netlab360-observer`, que **solo acepta el argumento fijo `snapshot`**. Lee de tres contenedores Docker S02 definidos de antemano (`nl360-s02-r-hq`, `-s1`, `-s2`) usando inspect y nsenter para `ip -j link show` y `ip -j -4 route get` de destinos constantes. Verifica hostname, propietario WAN, IDs de contenedor, etiqueta de Compose y network_mode=none; nunca ejecuta comandos enviados por clientes HTTP.
- Regla sudoers restringida: **`rc-aa-ec ALL=(root) NOPASSWD: /usr/local/libexec/netlab360-observer snapshot`**. No se autoriza Docker CLI, nsenter genérico, shells, escritura, comandos variables, pertenencia al grupo docker ni sudo sin contraseña en general.
- Los servicios no ejecutan Python web como root. `ProtectSystem=strict`, `ProtectHome=read-only` y `PrivateTmp=yes` agregan aislamiento; no incluir `NoNewPrivileges=yes` porque impediría el pequeño cambio de privilegios vía sudo. Verificar efectividad con `systemctl` y respuestas API.
- Los registros se consultan sin interactividad: `sudo journalctl -u netlab360-s04-exporter.service -n 40 --no-pager` y `sudo journalctl -u netlab360-s05-noc.service -n 40 --no-pager`.
- Una sola PowerShell SSH para operaciones. Más adelante, después de activar ambos servicios, la conexión Windows puede incluir `-L 9130:127.0.0.1:9130`, conservando simultáneamente consola SSH y acceso Chrome a NOC.

## Fuentes versionadas

- `scripts/operacion/s05-observador-privilegiado.py`: implementar/instalar en ruta root-owned; **no ejecutarlo desde ruta de usuario como root**.
- `servicios/systemd/netlab360-s04-exporter.service`, `servicios/systemd/netlab360-s05-noc.service`: copiar a `/etc/systemd/system` como root:root 0644.
- `servicios/observabilidad/s04_exporter_multisede.py` y `servicios/topologia-s05/app.py`: cuando `NETLAB360_PRIV_OBSERVER=/usr/local/libexec/netlab360-observer`, consultan el helper con `sudo -n`; sin esa variable preservan la ruta de consulta histórica para compatibilidad con pruebas y ejecución interactiva.
- `tests/test_s05_servicios_persistentes.py`: seis pruebas offline de alcance, rutas FIB válidas, interfaz de confianza y units; regresión S04 y S05 continúa.

## Instalación por etapas (pendiente de ejecutar)

1. **Preflight** (sin cambios): Git limpio y sincronizado; confirmar hostname, ID de usuario, binarios `docker`, `nsenter`, `ip`, `visudo`, `systemctl`, `python3`; confirmar 9110/9130 sin LISTEN, systemd units y helper/sudoers destinos sin colisiones, WAN state y tres contenedores S02 activos. Ejecutar 6 nuevas pruebas y toda batería S05/S04.
2. **Archivos de privilegio**: copiar helper mediante `sudo install -D -o root -g root -m 0755` a `/usr/local/libexec/netlab360-observer`; crear sudoers **solo si ausente** con `0440` y confirmar sintaxis `sudo visudo -cf`. Probar `sudo -n /usr/local/libexec/netlab360-observer snapshot` y validar JSON de 3 contenedores/2 rutas antes de iniciar HTTP.
3. **Servicios**: instalar units versionadas como root:root 0644, `sudo systemctl daemon-reload`, activar exporter primero y NOC segundo; validar `active`, 9110/9130 en 127.0.0.1, S04 `source_ok=true`, NOC `routing.available=true`, FIB `S1=s1p`, `S2=s2p` y sin warnings, `ens33` intacta.
4. **Persistencia**: después de verificación, salir del único SSH y reconectar por otro SSH/túnel; consultar `systemctl is-active` y APIs para demostrar que sobreviven a la desconexión. **No se requiere tmux**.
5. **Rollback acotado** si instalación falla: detener y deshabilitar únicamente dos units NETLAB360; no modificar Docker FRR, interfaces, OSPF ni snapshot. Quitar archivos de servicio/helper/sudoers solamente si sus rutas y firmas corresponden a los que acabamos de instalar, tras revisar el fallo; no ejecutar limpieza masiva. Logs de instalación quedan en `~/netlab360-bootstrap/s05/evidencias/operacion`.

## Límites de seguridad y comportamiento

El helper usa privilegio root, pero sus acciones son lecturas fijas; una actualización no confiable de scripts/HTML del repositorio puede afectar el código del servidor web **aunque no altere el helper instalado**. Antes de cada `git pull`, revisar los cambios. No abrir 9110/9130 públicamente: ambos se enlazan exclusivamente a `127.0.0.1`. No cambiar la política sudo sin documentar.

Estas units **no sustituyen infraestructura física redundante ni un segundo host**; resuelven persistencia del NOC y caducidad de sudo interactivo, y permiten reanudar HA después de validar.

**Capturas:** recuperación y hardening de servicios se documentan en TXT y `journalctl`; no rehacer S05_29–33 ni crear capturas de HA inexistente. **Snapshot manual `NETLAB360_S05_PreLAN_20261110` permanece intacto.**
