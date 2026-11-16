# NETLAB360 — G4: persistencia real de la TSDB tras reiniciar Prometheus S04

**Corte operativo:** 27/10/2026, hora de Panamá. **Origen:** terminales 1, 2, 3 y 4 aportadas por el operador en el registro `Texto pegado(20261027-065622).txt`. No es una reconstrucción ni una prueba offline.

## Resultado de G4 antes del reinicio

1. Sincronización `main` fast-forward `b1abeb4→2b6689f`, árbol limpio, herramienta G4 y 7 pruebas unitarias aprobadas.
2. `python3 scripts/observabilidad/s04-verificar-persistencia-tsdb.py --before`: `prometheus_start_utc=2026-10-27T05:11:42.574438879Z`, WAN HQ/s1p **68** muestras del episodio G3, `ALERTS` firing **28** muestras, `S04_G4_BASELINE=OK`, `S04_G4_BASELINE_PREPARADA=OK`.
3. Baseline escrita fuera de Git en `~/netlab360-bootstrap/s04/evidencias/S04_G4_TSDB_Antes_Reinicio.json`, SHA-256 **`fb9ac6d761a7e8b5cf39df9d955b9171689c1d94746cd0238c2050209dcec095`**.

## Reinicio controlado y evidencia de persistencia

- Terminal 3 relanzó `bash scripts/observabilidad/s04-iniciar-prometheus-local.sh` después de comprobar `S04_G4_PUERTO_9091_LIBRE=OK`. Se verificaron reglas Prometheus (4/4, promtool SUCCESS), target 9110 y `S04_INSTANCIA_B3_INTACTA=SI`.
- Inicio Prometheus 3.7.0 UTC **2026-10-27T06:54:31.491762152Z**; bitácora muestra **Found healthy block**, replay de WAL segmentos 0–3, `WAL replay completed`, `TSDB started` y `Server is ready to receive web requests`. Escucha solo `127.0.0.1:9091`, retención configurada 1 día.
- Terminal 1 ejecutó `python3 scripts/observabilidad/s04-verificar-persistencia-tsdb.py --after`: `S04_G4_WAN_MUESTRAS_DESPUES=68`, `S04_G4_ALERTA_FIRING_MUESTRAS_DESPUES=28`. La herramienta validó **diferencia de startTime** y **equivalencia de todos los pares (timestamp,valor)** de ambas series. **`S04_G4_PERSISTENCIA_TSDB=OK`**.
- Registro posterior `~/netlab360-bootstrap/s04/evidencias/S04_G4_TSDB_Despues_Reinicio.json`, SHA-256 **`1e1be26c09e299f0488a5e773ff28a5989556860535b1f9f937322bbdfc200bf`**.
- NOC después: `S04_G4_TOPOLOGIA=active`, `EXPORTER=FRESCO`, `PROMETHEUS=up`, `NOC=DISPONIBLE`, cero alertas activas. `S04_G4_NOC_POSTREINICIO=OK`, `S04_G4_POSTREINICIO=OK`. Exporter en Terminal 2 y NOC en Terminal 4 conservaron sus procesos en puerto 9110 y 9120.
- **Alcance probado:** reinicio **del proceso Prometheus**, no reboot de VM ni preservación por más de un día de retención. Esta prueba no representa exportación permanente de incidentes, ni verifica que un correo/notificación externa haya sido enviado.

## Puertas y evidencias

- **G0–G3** cerradas técnicamente. G3 se complementó con postcheck OSPF Full 4/2/2, FIB 6/6, ICMP LAN 6/6 y gestión intacta.
- **G4 parcial:** historia TSDB en operación y **persistencia tras reinicio comprobadas**. Pendientes: pérdida de fuente exporter/scrape y estado semántico `UNKNOWN` sin falsa caída WAN, además de historial **durable** consultable por sede en NOC con límites de retención documentados.
- **G5 pendiente:** SLI/SLO con denominador/ventana reales y alcance de notificaciones (no asumir Alertmanager).
- **G6 pendiente:** evidencias finales, regresión de servicios y WAN/LAN, escrito fase4 en informe único y aceptación interna.
- El operador aún no ha confirmado si tomó la captura reservada `S04_12_Historico_Prometheus_G3_Persistente_Tras_Reinicio`; no marcarla como guardada/publicada. El inventario real ya publicado en GitHub es **122 PNG**, incluidas 15 S04 de lotes01 y 02, revisados por la nueva CI de integridad PR #68.

## Continuidad segura

Conservar Term1 para operación/túnel; Term2 exporter, Term3 Prometheus y Term4 NOC. No desmontar FRR/WAN/LAN. Para evaluar `UNKNOWN`, detener temporalmente **solo exporter** de forma reversible, observar Prometheus y NOC en consola, y restaurarlo antes de registrar cierre; conservar timestamps, no producir falso estado WAN DOWN. La posterior capa de histórico web será un módulo de S04 y la visualización de grafo animado ampliada pertenece a S05 issue #64.

**Issue de control:** [#4](https://github.com/recm0708/netlab360/issues/4); histórico/SLI [#21](https://github.com/recm0708/netlab360/issues/21); fuentes [#20](https://github.com/recm0708/netlab360/issues/20).
