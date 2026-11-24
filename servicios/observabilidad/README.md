# Observabilidad de red — Fases 01 y 04

## Descripción

Desarrollamos un exportador inicial para el laboratorio de la fase 01 y posteriormente un colector multisede que publica métricas y permite observar el estado de WAN, VLAN y routers FRRouting.

## Componentes

| Servicio | Función |
|---|---|
| [Exportador de la fase 01](live_exporter.py) | Consultas iniciales de rutas y eventos |
| [Exportador de la fase 04](s04_exporter_multisede.py) | Estado y métricas de HQ, S1 y S2 |
| [Prometheus](prometheus/s04-prometheus.yml) | Almacenamiento y consulta de series temporales |
| [Reglas de alerta](prometheus/rules/s04-alerts.yml) | Detección del escenario WAN observado |
| [NOC de la fase 04](../noc-s04/README.md) | Visualización e historial de incidentes |

## Resultados

El colector de la fase 04 registró 25 series de métricas asociadas a tres sedes, ocho extremos WAN y nueve interfaces VLAN. Comprobamos la conservación de los registros temporales tras reiniciar Prometheus y la presentación de `UNKNOWN` cuando la fuente no estaba disponible.

La recolección alcanzó **100 % en 15 minutos** y **97,586 % en 60 minutos**. La segunda ventana quedó por debajo de la referencia experimental del 99 %.

## Limitaciones

Los componentes son de observación: no modifican la configuración de routers ni ejecutan recuperación autónoma. Los resultados del laboratorio no constituyen un acuerdo de disponibilidad de servicios de producción.

## Documentación relacionada

[Validación de las fases 01–04](../../docs/validacion/s01-s04-resultados.md) · [Capturas de la fase 04](../../evidencias/capturas/fase4/README.md).
