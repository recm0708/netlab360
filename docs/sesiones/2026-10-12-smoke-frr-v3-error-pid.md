# NETLAB360 — Ensayo FRRouting v3: montaje validado, fallo de PID watchfrr

**Ejecución real:** 2026-10-12 23:17:30 (-05:00, Panamá).  
**Fase:** S01; bloque B2-L3; issue [#42](https://github.com/recm0708/netlab360/issues/42).  
**Resultado:** **No superado** (`RESULTADO_SMOKE_FRR_V3=4`). Rollback correcto.

## Evidencia recibida

- `git pull --ff-only origin main`: avance de `86c28db` a `7cc979a`, `bash -n` sin errores, `git status --short --branch` limpio antes y después del ensayo.
- `bash scripts/laboratorio/b2-frr-smoke-v3-verificacion-acceso.sh --snapshot-confirmado` ejecutado una sola vez; IPAM B1 OK (3 sedes, 9 VLAN, 2 WAN, 15 subredes incluida VMnet8).
- Configuración temporal: `/etc/frr/daemons` UID100/GID101 modo 640, `frr.conf` UID100/GID102 modo 660, directorio temporal UID100/GID101 modo 755. `ospfd=yes`, `vtysh_enable=yes`, `bgpd=no`.
- Precheck de contenedor efímero `--network none` con `CAP_DAC_READ_SEARCH`: **`FRR_MOUNT_READABLE: SI`**, ambos archivos físicamente presentes y legibles dentro del montaje. Por ello el fallo “daemons does not exist” del intento anterior queda corregido en esta etapa.
- Arranque real de `nl360-frr-smoke-v3`: contenedor `exited`, **`ExitCode=1`**. Registro: **`WATCHFRR: Can't create pid lock file /var/run/frr/watchfrr.pid (Permission denied), exiting`** con timestamp Docker `2026-10-13T04:17:31.427040581Z` (UTC = 12/10 23:17:31 Panamá).
- Como `watchfrr` no consiguió crear su PID, `vtysh` nunca quedó disponible; no es posible afirmar que zebra u ospfd se hayan iniciado ni que haya rutas/vecinos OSPF.
- Cleanup verificó 0 contenedores y namespaces, `ens33=192.168.47.40/24`, default por `192.168.47.2`, servicios docker/ssh/open-vm-tools activos, Git limpio.
- Log original local `~/netlab360-bootstrap/evidencias/12-b2-frr-smoke-v3-20261012-231730.log`.
- El usuario ejecutó una presentación delimitada `INICIO CAPTURA B2_08` a `FIN CAPTURA B2_08`, que incluye `FRR_MOUNT_READABLE: SI` y resultado 4. **No ha confirmado todavía haber tomado un archivo PNG B2_08**. Si lo tomó, identificar `B2_08_Diagnostico_FRR_V3.png`.

## Análisis y alcance

El error está en **escritura del directorio PID** para `watchfrr`, no en lectura de configuración FRR. En el script v3, el contenedor ejecuta con `--cap-drop ALL` (se añaden varias capacidades específicas, pero no `DAC_OVERRIDE`), por lo que root no puede suprimir automáticamente la protección DAC de un directorio `frr:frr` donde carece de permisos de escritura ordinarios. Este mecanismo es una **explicación probable**, no una causa raíz certificada para todos los subprocesos.

No conceder `--privileged` ni modificar `/run/frr` en Ubuntu para resolverlo.

## Corrección propuesta para prueba v4, aún no ejecutada

- Nuevo archivo `scripts/laboratorio/b2-frr-smoke-v4-pid-aislado.sh`: monta **tmpfs exclusivo del contenedor** en `/run/frr` con `uid=0,gid=101,mode=0770`, de forma que el lanzador UID0 y el grupo FRR tengan escritura. `/var/run/frr` apunta al directorio de ejecución del contenedor. El cambio no toca `/run` del anfitrión.
- Antes de iniciar FRR, hace un segundo chequeo efímero `FRR_PID_DIR_WRITABLE: SI` que crea y elimina un archivo de prueba dentro del tmpfs; también conserva `FRR_MOUNT_READABLE: SI` para configuración.
- Mantiene `--network none` y no conecta interfaces a `ens33` ni crea WAN. El ensayo v4 **no solicita `CAP_SYS_ADMIN`**, capacidad muy amplia que todavía no se ha demostrado imprescindible para este arranque mínimo.
- Continúa almacenando estado del contenedor y `docker logs` antes del rollback. Si falla, **no repetir el mismo script sin analizar el nuevo registro**.
- Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` ya confirmado por usuario. No exigir uno nuevo.

## Evidencias siguientes

Usar consulta corta del log original para `B2_08_Diagnostico_FRR_V3.png` si el usuario aún no capturó la vista; debe mostrar timestamp, `FRR_MOUNT_READABLE: SI`, error de PID y `RESULTADO_SMOKE_FRR_V3=4`. Para el próximo ensayo, `B2_09_Arranque_FRR_V4_Verificado.png` **únicamente si** lectura y escritura PID OK, vtysh OK y resultado 0; en caso de fallo `B2_09_Diagnostico_FRR_V4.png`. Cada PNG con delimitadores INICIO/FIN y archivo log identificado. Logs permanecen locales, no declarar imágenes subidas a Git.
