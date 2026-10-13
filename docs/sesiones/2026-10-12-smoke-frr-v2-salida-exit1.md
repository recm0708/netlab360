# B2 — FRR v2: fallo de lectura del archivo daemons durante el arranque

**Hora real del ensayo:** 2026-10-12 23:08:48 (América/Panamá).  
**Estado:** segundo intento v2 corregido terminó con **`RESULTADO_SMOKE_FRR_V2=4`**; el contenedor salió con código 1. El arranque de FRR no está verificado, no hay adyacencias OSPF.

## Observaciones de la consola

- `git pull --ff-only origin main` completado hasta `86c28db`; sintaxis del script sin errores; comprobación de `sudo grep` en línea 94; árbol Git limpio.
- `bash scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh --snapshot-confirmado` validó IPAM y mostró los permisos preparados: `/tmp/nl360-smoke-v2.am65zfP1` (0755 100:101), `daemons` (0640 100:101) y `frr.conf` (0660 100:102). Lectura con `sudo grep` correcta: `ospfd=yes`, `vtysh_enable=yes`, `bgpd=no`.
- Docker creó contenedor `nl360-frr-smoke-v2`, que terminó enseguida: `Estado=exited ExitCode=1`. Los logs mostraron: **`cannot run : /etc/frr/daemons does not exist`**.
- `vtysh` no llegó a estar disponible. El nombre de error es ambiguo: en FRR 10.7.1, la rutina `frrcommon.sh` verifica **`-r /etc/frr/daemons`**, y emite el mismo texto si el archivo no es legible. Como el contenedor usa `--cap-drop ALL` sin `CAP_DAC_READ_SEARCH` ni `CAP_DAC_OVERRIDE`, mientras el archivo pertenece a UID100/GID101 con modo 0640, el proceso de entrada UID0 no tiene lectura DAC automática. Esta es una explicación técnica probable, a verificar dentro de contenedor; no inferir archivo ausente o fallo de binarios solo del mensaje.
- Rollback confirmado por usuario: `docker ps -a` y `ip netns list` sin entradas; gestión `ens33 192.168.47.40/24` y default `192.168.47.2`, servicios docker/ssh/open-vm-tools activos; `main...origin/main` limpio.
- Log original: `~/netlab360-bootstrap/evidencias/11-b2-frr-smoke-v2-20261012-230848.log`.
- Usuario mostró vista `INICIO CAPTURA B2_07` / `FIN CAPTURA B2_07` con resultado 4; **no confirmó expresamente que tomara PNG**. Si se guarda, usar `B2_07_Diagnostico_Arranque_FRR.png`, no la versión de éxito.

## Comparación con el origen de FRRouting

Fuente pública FRR 10.7.1 `tools/frrcommon.sh.in`, líneas 336–340: comprueba `[ -r "$C_PATH/daemons" ]` y genera mensaje de inexistencia cuando falla. Referencias: https://fossies.org/linux/frr/tools/frrcommon.sh.in y https://docs.frrouting.org/en/latest/setup.html. El mensaje por sí mismo no demuestra que el bind mount haya fallado.

## Corrección y pruebas siguientes

- **Nueva variante versionada, NO EJECUTADA:** `scripts/laboratorio/b2-frr-smoke-v3-verificacion-acceso.sh`. Incorpora comprobación explícita de `test -r` desde un contenedor efímero `--network none` con el mismo montaje; busca `FRR_MOUNT_READABLE: SI`. Añade exclusivamente `CAP_DAC_READ_SEARCH` a las capacidades del contenedor FRR, sin cambiar 0640/0660 ni usar `--privileged`. El resto del entorno permanece intacto.
- La capacidad `SYS_ADMIN` que ya figuraba en v2 sigue en la variante v3; revisar/reducir tras iniciar procesos y antes de implementar la topología de larga duración. El smoke no usa `--network host`.
- Tras `git pull`, ejecutar primero `bash -n` y revisar el archivo; luego realizar **una ejecución** de v3; capturar status/log del arranque antes de limpiar. Si falla, no repetir sin revisar el nuevo log.
- La captura siguiente `B2_08_*.png` debe tener límites `INICIO/FIN CAPTURA B2_08`, fecha, hostname, ruta log y resultado final. Éxito solo si `FRR_MOUNT_READABLE: SI`, `VTYSH_DISPONIBLE: SI` y `RESULTADO_SMOKE_FRR_V3=0`.

**Fase S01 y issues #12/#42 todavía abiertas.** La instantánea de VMware `NETLAB360-BASE-HERRAMIENTAS` permanece confirmada por el operador. No crear WAN/OSPF hasta validar el arranque.
