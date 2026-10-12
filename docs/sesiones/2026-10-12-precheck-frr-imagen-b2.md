# B2 — Validación de FRRouting 10.7.1 y descarga de imagen

**Fecha/hora:** 12 de octubre de 2026, 18:21:50 (Panamá, UTC−05:00).  
**VM:** `netlab360-lab`, Ubuntu Desktop 26.04.1 LTS.  
**Actividad:** diagnóstico previo a FRR/OSPF, sin routers implementados.

## Evidencia recibida

1. `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main` pasó de `6f145e9` a `c53ed0f`. `bash -n scripts/diagnostico/precheck-frr-b2.sh` sin error; rama `main...origin/main` limpia.
2. `bash scripts/diagnostico/precheck-frr-b2.sh` terminó con `RESULTADO_PREFLIGHT_FRR=0` y confirmó `MANIFIESTO_FRR: DISPONIBLE` para `quay.io/frrouting/frr:10.7.1`.
3. La variante `linux/amd64` está publicada con digest de plataforma `sha256:9aeb1c4947207a3d405674c4de06451d8b7e0d00e6f7d1f8e61e7354273efc63`. También aparecen arm64/ppc64le/s390x/arm/riscv64.
4. `sudo docker pull quay.io/frrouting/frr:10.7.1` descargó la imagen satisfactoriamente. El digest del manifiesto de imagen/referencia `RepoDigests` reportado fue **`quay.io/frrouting/frr@sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`**. Arquitectura inspeccionada: `amd64`.
5. Registro original local `~/netlab360-bootstrap/evidencias/06-b2-frr-precheck-20261012-182150.log` (aprox. 2,1 KiB).
6. **Postcheck sin incidentes:** `ens33 192.168.47.40/24`, gateway `.2`, solo redes Docker `bridge/host/none`, 0 contenedores; Docker 29.9.0 con `overlayfs` y cgroup v2, `docker/ssh/open-vm-tools` activos; IPAM B1 validado; Git limpio.

## Interpretación

- El tag y la arquitectura de la imagen están comprobados; **no es una prueba de ejecución de los demonios FRR**.
- El digest de la lista multiarquitectura descargada y el digest específico de plataforma no tienen por qué coincidir; se guardan por separado para trazabilidad.
- OSPF vecinos, dos WAN, selección de ruta, conmutación y recuperación **pendientes**.
- El nombre y existencia de snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` continúan sin confirmación textual/visual; el argumento `--snapshot-confirmado` usado antes en un ensayo no inspecciona Snapshot Manager.

## Siguiente paso sin intervención en red

Se versionó `scripts/diagnostico/inspeccionar-imagen-frr-b2.sh`, que utiliza un contenedor temporal de inspección, sin red, solo lectura, sin capacidades elevadas y con `--rm`, para verificar usuarios internos, permisos, ficheros `/etc/frr` y comandos `zebra/ospfd/vtysh` de la imagen. Esta prueba **aún no se ejecutó** y no activa FRR/OSPF.

La arquitectura WAN dual de R-HQ y R-S1 está documentada en `docs/arquitectura/03-frr-ospf-dual-wan-b2-plan.md`.

**Continuidad:** `docs/00-estado-y-continuidad.md`, issues #12 y #1.
