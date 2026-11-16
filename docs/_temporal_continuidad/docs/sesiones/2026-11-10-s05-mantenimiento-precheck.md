# NETLAB360 — Mantenimiento preventivo S05/P0 (10/11/2026)

**VM:** `netlab360-lab`, Ubuntu Desktop 26.04.1 LTS, `ens33=192.168.47.40/24`, gateway `192.168.47.2`.
**Fuente:** salidas operativas aportadas por el operador durante la sesión del 10/11/2026. Los registros originales permanecen en la VM y **no se han subido todavía** a este repositorio. No son capturas académicas adicionales.

## Resultado validado

1. Precheck inicial `scripts/validacion/s05-precheck-solo-lectura.sh`: `S05_FALLOS=0`, `S05_AVISOS=1` (Docker no consultable sin privilegios); `ens33`, gateway, Git y `PRAGMA quick_check` de la SQLite S04, correctos. Servicios/puertos S04 no escuchaban al estar desmontada la topología; no implica daño en el histórico.
2. Antes de instalar paquetes: `dpkg --audit` vacío, 0 servicios fallidos y 0 paquetes retenidos manualmente. Simulación APT estándar: **95 actualizados, 0 nuevos, 0 eliminados**. Aplicación real `apt-get upgrade` finalizó sin error; se mantuvieron los cinco paquetes sujetos a *phasing*.
3. Kernel: `linux-image-7.0.0-43-generic` y 8 paquetes nuevos asociados, sin eliminaciones; `dracut` generó initramfs y GRUB encontró ambos kernels `7.0.0-38` y `7.0.0-43`. Reinicio voluntario: **7.0.0-43-generic activo**, acceso SSH recuperado y cuatro pings correctos desde Windows.
4. Actualizaciones de software verificadas: Docker Engine **29.9.3**, Docker Compose **5.7.0**, OpenTofu **1.13.9**, Node.js **24.22.2**, GitHub CLI **2.103.3**; Ansible Core **2.20.1** e iperf3 **3.20** disponibles.
5. Aplicaciones Snap actualizadas individualmente: `core24=20261022`, `snapd=2.78`, `firefox=159.0.1-1`. `snap refresh --list`: **todos los snaps actualizados**; Flatpak no instalado.
6. Validación final: `dpkg --audit` sin hallazgos, **0 servicios systemd fallidos**, `ssh.service`, `docker.service`, `containerd.service` y `open-vm-tools.service` activos; `ens33` y ruta por defecto intactos, Git `main...origin/main` limpio. `REINICIO_PENDIENTE=NO`. Docker sin contenedores activos y con su volumen anterior conservado.
7. Precheck S05 repetido tras mantenimiento: `S05_FALLOS=0`, `S05_AVISOS=1`; `S05_SQLITE_INTEGRIDAD=ok`; `S05_PRECHECK_RESULTADO=OK_CON_VALIDACION_PENDIENTE`. Esto avala avanzar a la **auditoría específica P1**, no da por desplegada una topología LACP multisede ni por completadas las issues S05.

## Políticas de conservación

- **No** se ejecutaron `autoremove`, `docker system prune`, cambios de permisos del socket Docker, cambios en VMnet8 o `ens33`, ni actualizaciones indiscriminadas de imágenes de contenedor.
- Se constató el respaldo `~/netlab360-bootstrap/s05/mantenimiento-20261110/06_configuracion_pre_upgrade.tar.gz` con integridad TAR OK; contiene potencialmente configuraciones sensibles y **no debe publicarse**.
- Se retuvo el kernel `7.0.0-38-generic` como alternativa de recuperación.
- Los cinco paquetes APT en fase escalonada siguen pendientes deliberadamente: `distro-info`, `python3-distro-info`, `python3-software-properties`, `snapd` (paquete Debian) y `software-properties-common`. El **snap** `snapd` sí fue actualizado a 2.78: son canales de paquetes distintos.

## Registros originales en la VM

```text
~/netlab360-bootstrap/s05/mantenimiento-20261110/
01_inventario_pre_actualizacion.txt
02_actualizacion_indices_apt.txt
03_paquetes_actualizables.txt
04_simulacion_upgrade.txt
05_simulacion_full_upgrade.txt
06_configuracion_pre_upgrade.tar.gz                  [privado; no publicar]
07_baseline_pre_upgrade.txt
08_simulacion_final_upgrade.txt
09_ejecucion_upgrade.txt
10_validacion_post_upgrade.txt
12_simulacion_kernel.txt
13_instalacion_kernel.txt
14_validacion_pre_reinicio.txt
15_pre_reinicio_final.txt
16_validacion_post_reinicio.txt
17_revision_snap.txt
18_actualizacion_core24.txt
19_actualizacion_snapd.txt
20_actualizacion_firefox.txt
21_validacion_final_mantenimiento.txt
22_precheck_s05_post_mantenimiento.txt
```

**Siguiente paso:** S05/P1, prueba aislada LACP 802.3ad con `iperf3` multistream, hashing por flujo y evento de interrupción/restitución del miembro; el resultado exige datos reales y limpieza verificable de namespaces. Issues [#31](https://github.com/recm0708/netlab360/issues/31) y [#5](https://github.com/recm0708/netlab360/issues/5) permanecen **abiertas** hasta satisfacer aceptación.
