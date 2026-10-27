# NETLAB360 — Plan operativo y apagado seguro entre S04 y S05

**Actualizado:** 27/10/2026. Referencia académica: un único informe Word/PDF de mínimo 40 páginas (capítulos 1–8 + referencias), PowerPoint y demostración final en vivo, **TAR técnico externo** y **sin apartado de anexos**. Versión recibida `1457-Proyecto Semestral_borrador4.0.pdf` (94 pp.) todavía sin S04 integrada. El estado remoto de Git y la VM no equivale a una entrega académica.

## Estado confirmado previo a la parada

- S04 G0–G4: validadas. G5: SLI 15m `450/450=100%`; 60m `1698/1740=97.586%`, presupuesto al objetivo **99% candidato** `−25`; SLO no ratificado. G6: postcheck y 22 PNG auditadas, manuscrito pendiente.
- GitHub `main`: 129 PNG verificadas, fases S01=90/S02=9/S03=8/S04=22 (lotes S04 7+8+7), CI SHA-256 SUCCESS. SSH management `ens33=192.168.47.40/24`/GW `192.168.47.2`.
- Servicios locales **interactivos**: Terminal 2 exporter `127.0.0.1:9110`; Terminal 3 Prometheus `127.0.0.1:9091`, TSDB `~/netlab360-bootstrap/prometheus/s04/data`; Terminal 4 NOC `127.0.0.1:9120`, SQLite `~/netlab360-bootstrap/s04/historial/incidentes.sqlite3`. Terminal 1 SSH y validaciones.
- Topología S02 **desplegada** al último postcheck: contenedores `nl360-s02-r-hq/s1/s2`, cuatro WAN y LAN 12 namespaces, 9 VLAN/hosts. Mantener intacta hasta ejecutar los pasos de retirada en orden.
- Base de incidente G3 y registros G5/G6 preservados fuera de Git. No borrar, resetear ni subir `terraform.tfstate` ni secretos.

## Orden obligatorio de parada; seguir solo tras confirmar el estado en Ubuntu

1. **Preparación Terminal 1 (sin cambiar red):** `git status --short --branch` sin cambios, validadores G6 de OSPF/LAN/NOC ya comprobados, `ip -4 -br address show ens33`, ruta predeterminada, puerto 9091/9110/9120 en localhost. Registrar el commit final y hora. Crear carpeta preapagado fuera de Git con permisos privados y copiar **antes de down** los estados `s02/wan-links-state.json` y `s02/lan-vlan-state.json` para auditoría histórica. No reinyectar esas copias en nuevos contenedores.
2. **Cerrar fuentes dependientes:** en Terminal 4 `Ctrl+C` NOC y comprobar `S04_NOC_DETENIDO=SI` (cierra correctamente monitor SQLite); en Terminal 3 `Ctrl+C` Prometheus y esperar final de proceso/flush TSDB; en Terminal 2 `Ctrl+C` exporter. Desmontar túnel Windows solo después de dejar de usar la web. Verificar con `ss` que no escuchan 9120/9091/9110. No utilizar `kill -9` ni borrar WAL/SQLite.
3. **Respaldo opcional con servicios detenidos:** copiar o empaquetar TSDB en frío si existe espacio suficiente; registrar SHA-256 del respaldo y comprobar la integridad de SQLite con `PRAGMA integrity_check` usando Python, sin modificar la base real. Preservar los JSON y log de G3.
4. **Retirar solo topología propia** por scripts con comprobaciones de propiedad y `sudo -v`: `python3 scripts/laboratorio/s02-lan-vlan.py down` → verificar `S02_LAN_DOWN=OK`; `python3 scripts/laboratorio/s02-wan-links.py down` → `S02_WAN_DOWN=OK` + `S02_HOST_POSTCHECK=OK`; `sudo env HOME="$HOME" docker compose -f topologias/s02-frr/docker-compose.yml down` → verificar ausencia de los tres contenedores. **No invertir orden** ni usar `docker system prune`, `ip netns delete` masivo ni cambios de `ens33`.
5. **Postcheck Terminal 1:** estados S02 operativos ausentes pero respaldos conservados; cero contenedores *NETLAB360 S02* y cero namespaces de S02, puertos S04 libres, datos TSDB e historial SQLite presentes, Git limpio, IP/GW administrativos intactos. Guardar log de cierre y `sync`. Los validadores OSPF/LAN **no deben exigirse activos** una vez desmontada la topología; su éxito ya consta en el preapagado.
6. **Apagar únicamente la VM NETLAB360 desde Ubuntu** con `sudo systemctl poweroff`, **después** de revisar la salida de postcheck. La desconexión SSH es esperable. Confirmar `Powered Off` en VMware Workstation. No apagar otras VM ni la PC Windows. Instantánea VMware apagada opcional antes de S05; no interpretar snapshot como respaldo externo.

**No ejecutar automáticamente** las etapas 2–6 en una sola transacción desde SSH: el apagado se autoriza en la terminal solo después de revisar cada punto de control. Si algún `down` falla, no continuar con los pasos destructivos restantes; conservar state y diagnosticar. No crear nuevos incidentes G3.

## Reanudación planificada para S05

Arrancar VM Ubuntu, inspeccionar `ens33`, GW, SSH, `git status`/pull, Docker y ausencia de residuos de S02; confirmar respaldos TSDB/SQLite y estado de issues. Restaurar la topología S02 exclusivamente mediante `scripts/laboratorio/s02-routers-start.sh`, `s02-wan-links.py up --snapshot-confirmado` y `s02-lan-vlan.py up --snapshot-confirmado`, cada uno con su precheck y validadores, antes de activar nuevamente exporter/Prometheus/NOC. S05 se centra en [issue #5](https://github.com/recm0708/netlab360/issues/5) y [topología dinámica #64](https://github.com/recm0708/netlab360/issues/64); no declararlas ya desarrolladas.

## Convenciones y trazabilidad

- La denominación de `docs/sesiones` identifica históricos: sus encabezados antiguos no sustituyen al presente estado vigente. Mantener la cronología útil, no borrar cientos de registros porque no sean entregables al docente.
- `docs/academico/03-anexos-y-demostracion.md` tiene nombre heredado, **pero su contenido vigente dispone TAR externo y sin anexos**; no eliminar ni renombrar antes de auditar enlaces entrantes.
- Antes de eliminar un `.md`: comprobar referencias desde README, guiones, issues, enlaces relativos y SHA de evidencias; retener bitácoras y ADR incluso si no van en el TAR final. **A la fecha, ningún .md borrado**, pendiente determinar duplicación real y ausencia de trazabilidad.
- Fuente docente actual: [criterios académicos](academico/00-criterios-docentes-y-hitos.md). Revisión 30/10 introducción/objetivos/problema **aún por realizar**, no confundir con aceptación de S04.
