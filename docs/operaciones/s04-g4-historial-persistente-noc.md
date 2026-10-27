# NETLAB360 S04 G4 — Historial NOC persistente

**Estado:** diseñado, aún no ejecutado en Ubuntu. La implementación integra la base SQLite en el proceso NOC existente, sin requerir una quinta terminal.

## Alcance implementado

- SQLite WAL en ~/netlab360-bootstrap/s04/historial/incidentes.sqlite3, fuera de Git.
- Monitor interno cada 2 segundos: transiciones observadas pending, firing, resolved; evita duplicados al reiniciar el NOC.
- Una fuente UNKNOWN, un scrape fallido o una muestra obsoleta NO dan lugar a una falsa resolución.
- API GET /api/v1/incidents?site=HQ&limit=100 y /api/v1/incidents.csv?site=HQ; filtros ALL/HQ/S1/S2, interfaz web con historial por sede y exportación.
- Las transiciones anteriormente ocurridas no se atribuyen retroactivamente al monitor. Hay un importador G3 explícito y seguro: python3 servicios/noc-s04/app.py --import-g3-log, que verifica el SHA-256 del log auténtico y crea tres eventos G3 de origen verified_G3_terminal_log, con operación idempotente.
- Los eventos reales futuros registrados por la API son de origen prometheus_active_alerts y muestran el tiempo de observación; resolved no indica la hora exacta de recuperación física.

## Secuencia de validación futura

1. Sincronizar main limpia y ejecutar pruebas S04 y prechecks de fuente 9110, Prometheus 9091 y NOC 9120.
2. Importar el log G3 y validar tres entradas. Un segundo import debe devolver cero nuevas.
3. En Terminal 4 detener únicamente el NOC actual con Ctrl+C y reiniciar el mismo NOC en 9120. Mantener Terminal 2 exporter, Terminal 3 Prometheus y toda la red FRR/WAN/LAN operativa.
4. En Terminal 1 validar API JSON/CSV y origen verificado de G3, filtros HQ/S2 y fuente actual active/up. Verificar historial en navegador Windows y capturar evidencia nueva solo si la pantalla funciona.
5. Reprobar persistencia de registros tras reinicio exclusivamente del NOC; las pruebas automáticas de eventos nuevos son offline, no reemplazan una observación real futura.

## Límites

Retención Prometheus S04 actual: un día. SQLite no dispone todavía de política final de retención y respaldo; no confundir con históricos importados en TSDB. No incorpora Alertmanager, mensajería externa, detección AI ni diagrama animado S05. La base operacional permanece fuera de Git y del TAR hasta inspección y selección explícita.
