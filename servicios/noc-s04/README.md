# NETLAB360 S04 — NOC multisede centralizado

**Estado verificado 27/10/2026: funcionamiento real sobre HQ, S1 y S2, incidentes y persistencia histórica validados.**

## Arquitectura
- `servicios/noc-s04/app.py` sirve panel web y API de solo lectura en `127.0.0.1:9120`, con vistas CENTRAL/HQ/S1/S2.
- Consulta el [colector S04](../observabilidad/README-S04.md) (`127.0.0.1:9110`) y Prometheus local (`127.0.0.1:9091`); la UI presenta estados operativos, frescura de fuente y alertas.
- Estado `UNKNOWN` cuando no existe fuente fiable; `offline` cuando la topología está intencionalmente desmontada; `active` cuando se detectan los tres routers autorizados. Ninguno de estos estados certifica disponibilidad contractual HTTP o pérdida de paquetes continua.
- Diario SQLite externo al repositorio en `~/netlab360-bootstrap/s04/historial/incidentes.sqlite3`; API de historial por sede y exportación CSV.
- Sin cambios automáticos a FRR, sin envío de correo/mensajería externa ni diagnóstico ML.

## Pruebas auténticas realizadas

G3: WAN principal HQ/s1p interrumpida por procedimiento protegido durante 60s, alarma `pending→firing`, ruta secundaria s1b y recuperación comprobada; S2 estable. G4: importación idempotente desde log G3 verificado SHA-256, tres eventos `pending/firing/resolved` persistentes tras reiniciar NOC (PID `248883→263894`). La pérdida controlada del colector se representó como `UNKNOWN`, sin falsas alertas WAN/VLAN; posterior retorno a `active`.

[Pruebas de historial](../../docs/operaciones/s04-g4-historial-persistente-noc.md) · [Matriz de aceptación](../../docs/operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md) · [Evidencias S04](../../evidencias/capturas/fase4/README.md).

La VM se apagó ordenadamente tras desmontaje y respaldos; **no iniciar servicios sin los prechecks de S05 y la red administrativa protegida**.
