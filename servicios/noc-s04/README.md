# NOC centralizado multisede — S04

Implementamos un panel web y API local de consulta para **HQ, S1 y S2**, junto con un historial persistente de incidentes.

## Componentes y fuentes

- [`app.py`](app.py): vistas centralizadas y por sucursal en `127.0.0.1:9120`.
- [`historial_s04.py`](historial_s04.py): almacenamiento y consulta del historial SQLite, con exportación CSV.
- [Exportador y Prometheus S04](../observabilidad/README.md): métricas en `127.0.0.1:9110` y `127.0.0.1:9091`, respectivamente.

Distinguimos `active` (topología operativa), `offline` (escenario desmontado) y `UNKNOWN` (fuente de observación no fiable). La ausencia de un exportador no se traduce automáticamente en una caída WAN ficticia.

## Resultados

Durante el incidente controlado HQ/s1p observamos la transición `pending → firing → resolved`, con conmutación al respaldo y recuperación. Conservamos **3/3 eventos** en SQLite tras reiniciar el NOC. El sistema solo ofrece avisos visuales y registros locales; no envía correos, SMS, Telegram ni webhooks, y tampoco ejecuta acciones autónomas sobre FRR.

Los datos operativos de SQLite permanecen en `~/netlab360-bootstrap/s04/historial/incidentes.sqlite3`, fuera de Git.

[Validaciones G4](../../docs/validacion/s01-s04-resultados.md) · [Evidencias S04](../../evidencias/capturas/fase4/README.md).
