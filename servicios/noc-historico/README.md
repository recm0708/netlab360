# NETLAB360 S01 — NOC histórico del laboratorio inicial

**Estado: prototipo de la fase 1 ejecutado y validado**, anterior al NOC multisede S04.

El módulo `servicios/noc-historico/app.py` representa registros derivados de un ensayo auténtico de **76 sondeos ICMP**, con consultas del historial y presentación de rutas observadas. Su interfaz usa solo loopback `127.0.0.1:8765`. La salud de este servicio de lectura **no acredita el estado actual de los routers**.

Este prototipo no modifica interfaces, Docker, FRR, rutas ni administración de VMware. Su información es histórica y no debe mezclarse con muestras en vivo para inferir disponibilidad actual.

La implementación multisede de la cuarta fase se encuentra en [NOC S04](../noc-s04/README.md), con integración Prometheus, alertas y persistencia SQLite comprobadas. No ejecutar servicios de S01 únicamente para editar el informe académico.
