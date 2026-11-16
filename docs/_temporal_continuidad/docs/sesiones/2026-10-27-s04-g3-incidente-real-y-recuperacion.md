# NETLAB360 — S04 G3: incidente real, respaldo y recuperación documentados

**Fecha:** 27 de octubre de 2026, Panamá (UTC−05). **Origen:** transcripción original del comando de prueba aportada por el operador y ocho capturas PNG adjuntas en esta sesión; no simulación. **Estado:** G3 aceptada técnicamente; las PNG del lote 02 están auditadas localmente, **pendiente su publicación remota**.

## Condición inicial y comando ejecutado

- Los tres servicios S04 permanecieron operativos en `127.0.0.1:9110` exporter, `127.0.0.1:9091` Prometheus y `127.0.0.1:9120` NOC por túnel SSH interactivo.
- `S04_G3_PRECHECK=OK`: 3 routers, 4 WAN, 9 VLAN; fuente `active_fresh`, Prometheus `up`, NOC `available`, WAN 8/8 y VLAN 9/9 con `admin_up=1`. Rutas basales `S1=s1p`, `S2=s2p`; alerta `inactive`; gestión protegida.
- El operador ejecutó `python3 -u scripts/observabilidad/s04-incidente-wan.py --execute --snapshot-confirmado --hold-seconds 60 2>&1 | tee "$LOG"`. Archivo de log indicado en salida: `/home/rc-aa-ec/netlab360-bootstrap/s04/evidencias/S04_G3_Incidente_WAN_S1_20261027.log`. **Existe como ruta comunicada; no se copiaron ni verificaron sus bytes en este registro**.

## Cronología auténtica (UTC)

| Momento UTC | Estado observado | Evidencia |
|---|---|---|
| 2026-10-27 06:05:04 | Inicio incidente, HQ/s1p administrativamente DOWN | `S04_G3_HORA_INICIO_UTC`, `S04_G3_HQ_s1p=DOWN` |
| 2026-10-27 06:05:07 | Prometheus `inactive→pending` | `S04_G3_ALERTA_TRANSICION` |
| 2026-10-27 06:05:13 | Prometheus `pending→firing`; NOC la observó | `S04_G3_NOC_ALERTA_FIRING=SI`, S04_10 |
| Durante el corte | HQ→S1 vía 10.78.0.6 por **s1b**; S1→HQ vía 10.78.0.5 por **s1b**; S2 continúa **s2p**; ICMP exitoso | `S04_G3_CONECTIVIDAD_DURANTE_INCIDENTE=OK` |
| 2026-10-27 06:06:07 | HQ/s1p restaurada `UP` por guarda `finally` | `S04_G3_HQ_s1p=UP_RESTAURADA` |
| Tras reconvergencia OSPF | HQ→S1 retorna vía 10.78.0.2 por **s1p**, S1→HQ vía 10.78.0.1 por **s1p**, ens33 intacta | `S04_G3_HOST_GESTION_INTACTO=SI` |
| 2026-10-27 06:06:18 | Telemetría vuelve a `admin_up=1` y alerta desaparece de `/api/v1/alerts` | `S04_G3_ALERTA_RESUELTA=SI_AUSENTE_EN_ACTIVAS` |

El ensayo finaliza con `S04_G3_RESULTADO=OK` y `S04_G3_EJECUCION_COMPLETA=OK`. La marca de alerta resuelta acredita desaparición de la lista de alertas activas con fuente válida; **no** acredita notificación externa entregada ni registro persistente consultable desde el NOC.

## Auditoría del lote de fotografías 02

El operador adjuntó directamente las siguientes ocho capturas reales, que se revisaron visualmente y verificaron por cabecera PNG, dimensiones y SHA-256, sin editarlas:

- `S04_07_Exporter_Estado_Activo_Tres_Sedes_WAN_VLAN.png`.
- `S04_08_Prometheus_Metricas_Activas_Scrape.png`.
- `S04_09_NOC_Tres_Sedes_Enlaces_Activos-1.png` hasta `-4.png` (cuatro vistas complementarias).
- `S04_10_Incidente_WAN_Principal_Alerta_Firing.png`: dashboard CENTRAL, HQ/s1p DOWN y la alerta NETLAB360S04WANAdminDown `firing`.
- `S04_11_Recuperacion_WAN_Alerta_Resuelta.png`: dashboard CENTRAL, HQ/s1p UP y cero alertas activas tras finalizar prueba.

Se preparó `MANIFIESTO_SHA256_S04_LOTE02_2026-10-27.csv` y ZIP con rutas `evidencias/capturas/fase4/` y `evidencias/manifiestos/`, **fuera del repositorio** hasta importar y publicar en PR posterior. Ocho capturas físicas corresponden a cinco evidencias nominales 07–11. Total remoto permanece **114 PNG**: fase 1=90, fase 2=9, fase 3=8 y fase 4=7; objetivo tras importar este lote y verificar Git: **122 PNG** (fase 4=15). No sumar aún.

## Observaciones de diseño y continuidad

- El NOC actual solo presenta estados **administrativos por interfaz**; durante la falla HQ/s1p mostró DOWN, mientras S1/s1p podía seguir mostrando UP en su extremo. La topología animada posterior debe representar el **enlace extremo a extremo** mediante ambas observaciones + estado lógico y no confundir interfaz UP con transporte extremo a extremo operativo.
- G0/G1/G3 cumplen las comprobaciones programadas; G2 ya estaba validada funcionalmente y sus ocho PNG de este lote registran G2 y G3. No declarar S04 cerrada: G4 UNKNOWN/TSDB/historial persistente, G5 SLI/SLO/notificaciones según decisión, G6 regresión/publicación/escrito y aceptación.
- La fase 4 incorporará historial mínimo de incidentes con datos reales (issue [#21](https://github.com/recm0708/netlab360/issues/21)). La visualización interactiva/animada ampliada se reserva como incremento S05 (issue [#64](https://github.com/recm0708/netlab360/issues/64)), reutilizable por S06/S07.
- **Siguiente operación segura:** mantener servicios/routers/WAN/LAN levantados, verificar `validar-ospf-s02.py`, `validar-lan-s02.py`, `s04-incidente-wan.py --check`, red de gestión e integridad de Git; importar el segundo lote de capturas mediante rama de evidencias y PR, sin ejecutar otra falla.

## Advertencias

Las horas corresponden a las salidas reales, no a una promesa de tiempo de convergencia garantizado. El NOC no confirma daño físico ni HTTP por mostrar `admin_up`; esos indicadores tienen alcance limitado. Tampoco se ha probado disponibilidad de la fuente tras reinicio o historial web persistente, que integran G4.
