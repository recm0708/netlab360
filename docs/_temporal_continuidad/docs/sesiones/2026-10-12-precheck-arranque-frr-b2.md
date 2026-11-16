# B2 - Precheck de arranque FRRouting, 12 de octubre 2026

**Sesión registrada:** 18:47-18:49, hora de Panamá. **Estado:** validación sin despliegue, prueba exitosa.

## Resultados

- Repositorio Git actualizado hasta 1627726 y rama main limpia. La comprobación bash -n no informó errores.
- El diagnóstico `scripts/diagnostico/precheck-arranque-frr-b2.sh` terminó con `RESULTADO_PRECHECK_ARRANQUE=0`.
- FRRouting 10.7.1 amd64: entrypoint `/sbin/tini --`, comando `/usr/lib/frr/docker-start`. Este último utiliza `frrcommon.sh` y `watchfrr $(daemon_list)`.
- Configuración de demonios inspeccionada: `ospfd=no`, `bgpd=no`, `vtysh_enable=yes`. Todavía no se demostró el arranque de zebra y ospfd.
- Usuario frr UID 100; grupo frr GID 101 y frrvty GID 102. Existen /etc/frr y /run/frr. No se encontró /var/log/frr, sin que esto detuviera la inspección.
- Después: sin contenedores residuales; solo redes Docker predeterminadas; `ens33=192.168.47.40/24` y gateway `192.168.47.2`; tres servicios activos.
- Evidencia local `~/netlab360-bootstrap/evidencias/08-b2-frr-entrypoint-20261012-184725.log`.
- Se consultó también el registro previo B2-L2 de 18:16, con comunicación 3/3 en VLAN 110, aislamiento respecto de VLAN 120 y recuperación; código 0. Fue una consulta de evidencia, no una repetición del ensayo.
- Una orden Git quedó concatenada durante el pegado como `branchcd`, generó un mensaje de uso; el estado Git correcto se confirmó después.
- El usuario **confirmó expresamente** que el snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` existe desde la primera indicación. Confirmación del operador, sin inspección remota del Snapshot Manager.

## Pendientes

La imagen FRR está descargada, pero las configuraciones de R-HQ y R-S1 siguen siendo propuestas sin aplicar. Falta habilitar zebra/ospfd en contenedores aislados, validar permisos y montaje, crear dos WAN, formar adyacencias OSPF, probar cambio y restauración de ruta, telemetría y dashboard. No atribuir estas funciones al precheck.

Referencia: issue #12 y `docs/00-estado-y-continuidad.md`. Nunca subir credenciales al repositorio.
