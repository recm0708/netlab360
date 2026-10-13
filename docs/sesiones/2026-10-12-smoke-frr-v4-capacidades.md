# NETLAB360 — Smoke FRR v4: permisos PID resueltos; demonios fallaron por capacidades

**Ejecución real:** 2026-10-12 23:32:21–23:32:36 (Panamá, UTC−05:00).  
**Fase:** S01, B2-L3, issue #42. **Resultado: NO superado, rollback correcto.**

## Resultados constatados en consola

- `git pull --ff-only origin main` avanzó de `7cc979a` a `e458944`; `bash -n` sin error y Git limpio.
- Ejecución `bash scripts/laboratorio/b2-frr-smoke-v4-pid-aislado.sh --snapshot-confirmado`, IPAM B1 OK.
- Configuración FRR: `daemons` modo 640 `100:101`, `frr.conf` modo 660 `100:102`, `zebra=yes`, `ospfd=yes`; montaje dentro del contenedor **`FRR_MOUNT_READABLE: SI`**.
- tmpfs exclusivo en `/run/frr` / `/var/run/frr` con propietario root y grupo frr; comprobación real de creación de archivo: **`FRR_PID_DIR_WRITABLE: SI`**. El error previo al crear `watchfrr.pid` ya no se reprodujo.
- Docker creó el contenedor. `VTYSH_DISPONIBLE: SI (intento 1)`; esto **no prueba que zebra u ospfd estén activos**.
- `vtysh -b` informó `Can't open configuration file /etc/frr/vtysh.conf` y `Configuration file[/etc/frr/frr.conf] processing failure: 11`. La siguiente consulta devolvió literalmente **`ospfd is not running`**.
- Proceso `watchfrr` corriendo y `staticd` visible. `mgmtd`, `zebra` y `ospfd` **fallaron**. Diagnóstico de los logs:
  ```text
  privs_init: initial cap_set_proc failed: Operation not permitted
  Wanted caps: cap_net_bind_service,cap_net_admin,cap_net_raw,cap_sys_admin=p
  Have caps: cap_chown,cap_dac_read_search,cap_setgid,cap_setuid,cap_setpcap,cap_net_bind_service,cap_net_admin,cap_net_raw=p
  Failed to start mgmtd!
  Failed to start zebra!
  Failed to start ospfd!
  ```
  Por tanto, **la falta de `CAP_SYS_ADMIN` en la v4 es causa demostrada del fallo de inicialización de capacidades en esos demonios**.
- Mensajes adicionales `failed to mkdir "/var/tmp/frr/<daemon>.<pid>": Permission denied` (registros de fallos) y `staticd: access to socket ... denied: Permission denied`. Deben revisarse directorio temporal y acceso DAC a sockets.
- `RESULTADO_SMOKE_FRR_V4=1` y `RESULTADO_EJECUCION_FRR_V4=1`. Es posible que `vtysh -c 'show ip ospf'` devolviera estado Unix cero aunque su texto indicara demonio no operativo; la nueva prueba debe verificar procesos reales y contenido.
- Posvalidación: 0 contenedores, 0 namespaces, `ens33=192.168.47.40/24`, default `192.168.47.2`, docker/ssh/open-vm-tools activos, Git limpio.
- Evidencia original local `~/netlab360-bootstrap/evidencias/13-b2-frr-smoke-v4-20261012-233222.log`. El usuario indicó que **toma todas las capturas solicitadas por defecto**; se considera tomada `B2_09_Diagnostico_FRR_V4.png`, pendiente de revisión gráfica posterior, no subida a GitHub.
- La salida de consola del usuario contiene delimitadores `INICIO CAPTURA B2_09` / `FIN CAPTURA B2_09`.

## Revisión técnica y preparación

Referencias públicas:
- https://github.com/FRRouting/frr/issues/8681 — requisito `CAP_SYS_ADMIN` de zebra/ospfd reportado oficialmente.
- https://docs.frrouting.org/en/latest/vtysh.html — `vtysh.conf` separado e integración de `frr.conf`.
- https://docs.frrouting.org/en/latest/setup.html — directorio `/var/tmp/frr` para crashlogs.

**Nuevo script v5 versionado, NO EJECUTADO:** `scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh`. Cambios: (1) mantener tmpfs PID y lectura de configuración; (2) `CAP_SYS_ADMIN` explícita solo para contenedor temporal `--network none`, `CAP_DAC_OVERRIDE` para acceso a sockets, sin `--privileged`; (3) tmpfs de `/var/tmp/frr` propiedad frr y prueba de escritura como UID100/GID101; (4) crear `vtysh.conf` con propiedad `frr:frrvty`; (5) validar procesos zebra y ospfd reales leyendo `/proc/*/comm`, comprobar salida OSPF y su identificador, no aceptar únicamente `show version`; (6) conservar Docker inspect/procesos/logs antes de eliminar el contenedor.

**Precondición:** el snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` sigue confirmado por usuario. No tocar VMnet8, ens33, rutas host, NetworkManager.

**Próximo paso:** hacer pull del repositorio, `bash -n` del v5, comprobar que contiene `SYS_ADMIN`, `CRASH_TMPFS`, `FRR_DAEMONS_ACTIVOS`, ejecutar una vez y conservar salida `14-b2-frr-smoke-v5-*.log`. Registrar evidencia `B2_10_Arranque_FRR_V5_Verificado.png` solo si resultado = 0 y procesos comprobados; en caso contrario `B2_10_Diagnostico_FRR_V5.png`.

**No cerrar #42 ni #12 ni S01 hasta contar con vecinos OSPF WAN dual, cambio/restauración y alarma/dashboard cuando corresponda.**
