# NETLAB360 — Inspección interna de imagen FRRouting y revisión de capturas

**Fecha de ejecución:** 2026-10-12 18:36:14 (Panamá).  
**Estado:** prueba de inspección completada, sin routers desplegados ni vecindades OSPF.  
**Referencia:** issue #12 y `docs/arquitectura/03-frr-ospf-dual-wan-b2-plan.md`.

## Comandos y resultados comprobados

- `git pull --ff-only origin main`: fast-forward `c53ed0f..287280d`; `bash -n scripts/diagnostico/inspeccionar-imagen-frr-b2.sh` no produjo errores; Git limpio al terminar.
- Imagen existente `quay.io/frrouting/frr:10.7.1`, `amd64`, ID/digest observado `sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`.
- `bash scripts/diagnostico/inspeccionar-imagen-frr-b2.sh`: `RESULTADO_INSPECCION_FRR=0`. Contenedor efímero sin red, capacidades eliminadas, raíz solo lectura y `--rm`.
- Usuarios: `root` (UID 0), `frr` (UID 100, GID 101), grupo `frrvty` (GID 102). Mensaje `id: unknown user frrvty`: `frrvty` es grupo, no usuario (informativo).
- `/etc/frr` existe, propiedad `frr:frr`; `/etc/frr/daemons` existe, propiedad `frr:frr` y permiso `0644`. No existen `/etc/frr/frr.conf` ni `vtysh.conf` en la imagen inicial.
- `ospfd=no`, `bgpd=no`, `vtysh_enable=yes`; opciones de `zebra` y `ospfd` referidas a 127.0.0.1. La inspección NO establece si el servicio `zebra` está habilitado o si el proceso FRR arranca correctamente.
- Binarios disponibles: `/usr/bin/vtysh`, `/usr/lib/frr/zebra`, `/usr/lib/frr/ospfd`; herramientas `ip` y `ping`.
- Postcheck: Docker sin contenedores, redes base `bridge/host/none`, cero namespaces adicionales, `ens33=192.168.47.40/24`, gateway `192.168.47.2` intactos; servicios `docker`, `ssh`, `open-vm-tools` activos.
- Log local: `~/netlab360-bootstrap/evidencias/07-b2-inspeccion-imagen-frr-20261012-183614.log`, tamaño aprox. 1,9 KiB.

## Capturas revisadas mediante adjuntos del usuario

| Archivo recibido | Revisión | Recomendación |
|---|---|---|
| `B1_01_Validacion_IPAM_y_Redes.png` | Válido: fecha, host, resultados IPAM/colisiones y Git limpio visibles | Conservar |
| `B1_02_Compatibilidad_Capa2.png` | Válido: módulos 8021q, bonding, openvswitch, veth, bridge; IP, Docker, cierre de prueba | Conservar |
| `B2_01_Imagen_FRR_Descargada.png` | Válido como **inspección interna**, no muestra el comando original de descarga `docker pull` | Renombrar `B2_02_Inspeccion_Imagen_FRR.png`; usar imagen separada para descarga si hace falta |

**Estado de archivos:** los PNG se revisaron en esta conversación, pero **no se afirma que estén añadidos a GitHub**. La evidencia en el repo es textual; los PNG no se transfirieron desde los archivos adjuntos de la conversación al clon Ubuntu.

## Reglas para las siguientes capturas

Incluir en la vista terminal: (1) fecha/hora y hostname; (2) comando efectivo ejecutado —preferiblemente en la misma terminal, no solo `tail` de log—; (3) salida decisiva y código de retorno; (4) estado posterior y ausencia de residuos cuando corresponda. En resultados largos usar 2 imágenes o `tail` + log íntegro; no distorsionar ni editar los resultados. No mostrar tokens, contraseñas o códigos OAuth.

El B2-L2 completado el mismo día tiene su propio log `05-b2-l2-20261012-181601.log`; captura B2-L2 todavía no informada explícitamente, aunque las 2 de B1 sí están confirmadas.

## Próximo subpaso

Inspeccionar el punto de entrada (`Entrypoint`/`Cmd`), la habilitación actual de `zebra` y `ospfd`, y requerimientos de montaje mediante sondeo `--network none`, sin ejecutar demonios. Después versionar configuraciones `daemons` y `frr.conf` para R-HQ/R-S1, plan de lanzamiento `up/status/down` y recuperación. Antes de crear routers/líneas WAN, verificar visualmente el snapshot VMware `NETLAB360-BASE-HERRAMIENTAS`; aún no confirmado de forma explícita.
