# B2-L3 — Plan de dos WAN y FRRouting/OSPF (antes de implementar)

**Estado:** diseño de la siguiente actividad; NO ejecutada, routers FRRouting NO desplegados.  
**Fecha:** 2026-10-12; fase S01, issue #12.

## Progreso que habilita la siguiente fase

La subprueba B2-L2 ya demostró comunicación de dos endpoints VLAN 110, aislamiento de VLAN 110 vs 120 y recuperación, con rollback y sin alterar gestión `ens33 192.168.47.40/24`. Log local `05-b2-l2-20261012-181601.log`; bitácora `docs/sesiones/2026-10-12-prueba-vlan-l2-b2.md`. Ninguno de esos ensayos probó OSPF.

## Selección técnica provisional

Usar **dos routers FRRouting en contenedores aislados con `--network none`**, y unirlos mediante interfaces `veth` independientes administradas por scripts del laboratorio. No ejecutar demonios FRR directamente en el namespace del anfitrión, no conectar Docker default bridge ni `ens33` a interfaces del laboratorio.

**Imagen confirmada (2026-10-12):** `quay.io/frrouting/frr:10.7.1` descargada y verificada para `amd64`. Digest `RepoDigests` observado: `sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`. El tag es válido para esta VM; fijar el digest en el futuro laboratorio reproducible. FRRouting documenta distribución de imágenes mediante Quay desde FRR 8.4.2; la disponibilidad de la etiqueta seleccionada ya fue comprobada con Docker. Referencia de etiquetas: https://quay.io/repository/frrouting/frr?tab=tags . FRR 10.7.1 figura entre las versiones publicadas en agosto de 2026. La prueba debe guardar digest de la imagen real descargada y verificar comandos de FRR antes de configurar OSPF.

Referencias oficiales:
- https://frrouting.org/release/
- https://docs.frrouting.org/en/latest/setup.html
- https://docs.frrouting.org/en/latest/ospfd.html

## Matriz WAN de primer ensayo

| Enlace | R-HQ | R-S1 | Red | OSPF cost por extremo | Uso esperado |
|---|---|---|---|---|---|
| WAN-P | wan-p `10.78.0.1/30` | wan-p `10.78.0.2/30` | `10.78.0.0/30` | 10 / 10 | Preferida |
| WAN-B | wan-b `10.78.0.5/30` | wan-b `10.78.0.6/30` | `10.78.0.4/30` | 100 / 100 | Respaldo |
| Loopback HQ | `10.79.0.1/32` | — | /32 | No aplica | Router ID |
| Loopback S1 | — | `10.79.0.2/32` | /32 | No aplica | Router ID |

Anunciar interfaces WAN en OSPF área 0; utilizar `passive-interface` para loopbacks. La LAN inicialmente puede simularse con interfaces aisladas `10.70.10.1/24` y `10.71.10.1/24` según IPAM. Se requieren destinos realmente instalados en los routers para observar rutas preferidas y prueba de continuidad, no solo salida de vecinos.

**Comprobaciones planeadas:**
1. Adyacencias en cada WAN, `show ip ospf neighbor`.
2. Selección de ruta a la LAN de la otra sede, `show ip route` / `ip route`.
3. Continuidad de ping entre extremos al desactivar **únicamente wan-p virtual**; registrar sello temporal, paquetes perdidos y tiempo de convergencia.
4. Reconvergencia después de reactivar wan-p; evitar interpretar cualquier cambio de RTT como prueba de failover.
5. Limpieza de routers/conexiones del proyecto, rutas globales y ens33 intactas; monitorear ausencia de contenedores y de redes residuales.

## Controles de seguridad y recuperación

- **Verificar visualmente instantánea VMware `NETLAB360-BASE-HERRAMIENTAS`**. El argumento de un script `--snapshot-confirmado` no verifica por sí mismo que exista.
- No usar `docker run --privileged` por defecto. Conceder permisos mínimos necesarios en contenedores aislados, incluyendo NET_ADMIN solo cuando haga falta; no compartir el network namespace del host.
- Registrar identificadores propios `nl360-` y limpiar únicamente recursos creados por el proyecto.
- No usar `iptables --flush`, `ip route flush`, reinicio de NetworkManager ni manipulación de `ens33`.
- Hacer `sudo docker manifest inspect` / `docker pull` únicamente después de confirmar etiqueta, DNS e integridad del daemon. Bajar imagen no constituye desplegar la topología.
- Documentar versiones reales, digest, fallo controlado, evidencia y limitaciones en GitHub antes de pausa.

## Próxima acción del usuario

El diagnóstico `scripts/diagnostico/precheck-frr-b2.sh` terminó exitosamente; la imagen oficial ya fue descargada. **Próximo paso:** inspeccionar el contenido con `scripts/diagnostico/inspeccionar-imagen-frr-b2.sh`, en contenedor efímero `--network none`, sin privilegios y sin iniciar FRR. Comprobar usuarios, daemons y herramientas antes de crear configuraciones. Ver `docs/sesiones/2026-10-12-precheck-frr-imagen-b2.md`. Guardar logs en `~/netlab360-bootstrap/evidencias/`, sin tokens.
