# NETLAB360 — G4: comprobar persistencia TSDB por reinicio acotado

**Estado:** herramienta y procedimiento listos; **ningún reinicio ejecutado todavía**. El incidente S04 G3 ocurrió a 2026-10-27T06:05Z y fue observado por exporter/Prometheus/NOC. La consulta mientras Prometheus operaba recuperó 68 muestras WAN (UP/DOWN) y 28 muestras de alerta FIRING.

## Alcance y condiciones

- Mantener infraestructura FRR 3/3, 4 WAN, 9 VLAN y la administración `ens33=192.168.47.40/24` intactas. Mantener Terminal 2 (exporter 9110), Terminal 4 (NOC 9120) y Terminal 1 (SSH/operación) activos.
- Reiniciar **solo Prometheus S04 en Terminal 3**, con Ctrl+C del proceso lanzado originalmente por `bash scripts/observabilidad/s04-iniciar-prometheus-local.sh`, después de confirmar fin normal y puerto 9091 liberado. Relanzar exactamente ese script; misma ruta persistente `~/netlab360-bootstrap/prometheus/s04/data`. No borrar TSDB ni alterar la instancia B3.
- Validar `/api/v1/status/runtimeinfo` antes y después: `startTime` debe cambiar; no basta observar `up`.
- Guardar copia antes/después, fuera de Git y sin sobrescribir existentes: `~/netlab360-bootstrap/s04/evidencias/S04_G4_TSDB_Antes_Reinicio.json` y `S04_G4_TSDB_Despues_Reinicio.json`.
- La herramienta `scripts/observabilidad/s04-verificar-persistencia-tsdb.py` ejecuta consultas históricas `query_range` de HQ/s1p y alerta `firing` en ventana fija UTC 06:04:45–06:07:00 del 27/10 con paso 2s. Exige que la serie original conserve secuencia exacta tras reinicio, contenga UP y DOWN, y que `ALERTS` contenga valores 1. No escribe en ningún dispositivo de red ni modifica el servidor.
- El script rechaza baseline inexistente, una segunda ejecución que sobrescriba evidencia, timestamp de arranque sin cambios, pérdida de muestras, otros hosts y ejecuciones como root. **No mide reinicio de VM**, solo del proceso Prometheus.

## Orden operativo

1. En Terminal 1 sincronizar rama limpia a `main`; tests G4 `python3 -m unittest discover -s tests -p 'test_s04_tsdb_persistencia.py' -v`; precheck exporter/NOC/Prometheus y FRR; ejecutar `python3 scripts/observabilidad/s04-verificar-persistencia-tsdb.py --before`. Debe registrar muestras reales antes y `S04_G4_BASELINE=OK`.
2. En Terminal 3 pulsar Ctrl+C exclusivamente en la consola que ejecuta Prometheus S04; verificar que `ss -ltn` no muestra 9091; relanzar `bash scripts/observabilidad/s04-iniciar-prometheus-local.sh` y observar `Server is ready to receive web requests`.
3. En Terminal 1 ejecutar `--after`. Debe mostrar `S04_G4_PERSISTENCIA_TSDB=OK`, `startTime` distinto y mismas muestras, seguidas de precheck normal S04 G3 y verificación NOC `scrape=up`, cero alertas activas. Conservación y exposición del histórico son conceptos distintos: 1 día de retención actual, **no** archivo permanente de incidentes.

## Límites y próximos bloques

Esta prueba no corresponde al ensayo de disponibilidad de la fuente `UNKNOWN`, que debe hacerse separadamente y sin confundir scrape down con caída WAN. Tampoco crea todavía historial navegable en NOC. La capacidad de histórico durable y exportación permanece en #21 (G4/G5); diseño del grafo animado en S05 #64. Capturar evidencia G4 de reinicio **solo tras salida real** y registrar hash de los archivos JSON. No atribuir fallos reales ni screenshots que no se hayan observado.
