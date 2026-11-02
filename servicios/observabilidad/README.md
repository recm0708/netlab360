# Observabilidad y exportadores — S01 y S04

En este directorio conservamos dos implementaciones diferenciadas: el primer prototipo FRR de S01 y el colector de estado multisede desarrollado en S04. **No mezclamos muestras históricas con estados actuales.**

## S01 — Exportador inicial

[`live_exporter.py`](live_exporter.py) consulta en solo lectura eventos y estado de rutas en escenarios HQ/S1, mediante `127.0.0.1:9108`. Durante S01 validamos alertas y recuperación WAN, sin inferir continuidad de paquetes entre sondeos.

## S04 — Colector multisede y Prometheus

[`s04_exporter_multisede.py`](s04_exporter_multisede.py) consulta en solo lectura la SoT candidata, Docker y los routers FRRouting autorizados. Publica `/api/v1/state`, `/metrics` y salud local desde `127.0.0.1:9110`. Registramos 25 series de métricas relacionadas con tres sedes, ocho extremos WAN y nueve interfaces VLAN.

Prometheus 3.7.0 se ejecutó en `127.0.0.1:9091`, con [configuración S04](prometheus/s04-prometheus.yml) y [reglas de alerta](prometheus/rules/s04-alerts.yml). Verificamos persistencia **68/68** muestras de WAN y **28/28** de alerta después de reiniciar Prometheus; el NOC mostró `UNKNOWN` durante la interrupción del colector sin inventar fallas WAN.

**SLI medido:** 450/450 scrapes (100 %) en 15 minutos y 1698/1740 (97,586 %) en 60 minutos. El 99 % se adoptó como **referencia experimental interna de evaluación**, incumplida en la ventana de 60 minutos; no equivale a un SLA ni a aprobación individual docente del indicador. Ninguna de estas medidas representa por sí sola un SLA de aplicaciones.

No ejecutamos `s04_exporter_multisede.py` para cambiar interfaces o routers; el componente es de observación. Su visualización e historial corresponden al [NOC S04](../noc-s04/README.md). Conservamos los datos TSDB y SQLite fuera de Git.

[Pruebas G5](../../docs/operaciones/s04-g5-decision-medida-notificaciones-locales.md) · [Evidencias S04](../../evidencias/capturas/fase4/README.md).
