# NETLAB360 — S02: apagado controlado y reanudación (23/10/2026)

**Origen de datos:** registro de terminal aportado por el operador (233 líneas); no confundir salidas verificadas con acciones inferidas. **Estado posterior a SSH:** acceso remoto restablecido; aún sin nueva inspección de host/contendores/archivos tras arranque.

## Preapagado real y éxito

- Se respaldaron los **dos estados activos** antes de desmontar S02 en `~/netlab360-bootstrap/s02/preapagado-20261023_212528/` (copias de `wan-links-state.json` y `lan-vlan-state.json`).
- Antes de desmontar: `validar-ospf-s02.py` verificó **FULL HQ=4 / S1=2 / S2=2**, FIB primarias **6/6** y seis ICMP entre loopbacks; `validar-lan-s02.py` verificó **9/9 gateways** y **6/6 ICMP VLAN/sedes**.
- Retiro controlado LAN S02: `s02-lan-vlan.py down` eliminó **tres trunks** y **12 network namespaces** de su propiedad, terminó `S02_LAN_DOWN=OK`.
- Retiro controlado WAN S02: `s02-wan-links.py down` retiró cuatro WAN, tres loopbacks, revirtió la propiedad de las interfaces correspondientes y obtuvo `S02_HOST_POSTCHECK=OK`, `S02_WAN_DOWN=OK`. Valores de forwarding reportados restaurados a 1 en cada contenedor (su valor registrado previo; no afirmar reset a cero).
- `docker compose -f topologias/s02-frr/docker-compose.yml down` detuvo y retiró **exclusivamente los tres routers** `nl360-s02-r-hq/s1/s2`. Revisión mostró **cero contenedores S02** restantes.
- Estados **operativos** `~/netlab360-bootstrap/s02/wan-links-state.json` y `lan-vlan-state.json` quedaron AUSENTES después de down; las copias de seguridad se preservaron. `ens33=192.168.47.40/24`, gateway `192.168.47.2` y Git limpio.
- El comando `sync` terminó y dejó `NETLAB360_APAGADO_PREPARADO=OK` y `RESULTADO_PREAPAGADO=0`. Log: `~/netlab360-bootstrap/evidencias/S02_Preapagado_Controlado.log`.
- El operador ejecutó `sudo systemctl poweroff`; la sesión SSH se desconectó. Posteriormente Windows PowerShell realizó `ssh netlab360` correctamente, mostrando **Ubuntu 26.04.1 LTS, kernel 7.0.0-38** y shell `rc-aa-ec@netlab360-lab`. **SSH reanudado confirmado**, pero esto no demuestra por sí solo que la red Docker o archivos locales se hayan revisado después del arranque.

## Conclusión y siguiente fase

**Apagado seguro validado.** No se borraron scripts, runtime externos ni pruebas históricas en las operaciones mostradas; verificar su existencia después del arranque antes de afirmarlo globalmente. El estado deseado de la topología S02 es **detenido intencionalmente**, no desplegado/activo tras el reinicio. No ejecutar `validar-ospf-s02.py` ni `validar-lan-s02.py` esperando éxito hasta reconstrucción controlada, y no reutilizar states antiguos como si fueran propiedad de los contenedores nuevos.

**Prioridad próxima:** verificación POST-BOOT read-only (red, Git, contenedores S02 ausentes, estados operativos ausentes, logs, configuraciones y evidencias); auditar PNG S02_01–09 y documentar S01+S02 en informe institucional bajo norma APA7. Integración funcional S02 **ya comprobada antes del apagado** y no requiere repetición para documentación. La ejecución avanzada S03 queda pausada hasta cierre del núcleo y actualización del informe.

[Issue S02](https://github.com/recm0708/netlab360/issues/2) · [Registro WAN/LAN](2026-10-23-s02-integracion-wan-lan.md) · [Seguimiento de avance](../control/04-avance-s01-s03-2026-10-23.md).
