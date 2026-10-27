# NETLAB360 S01 — Exportador FRRouting de la primera etapa

**Estado: prototipo inicial comprobado sobre escenarios HQ/S1**, con observación de estados WAN, rutas seleccionadas y eventos durante caída/restauración. Se utilizó en S01 antes del colector multisede S04.

`servicios/observabilidad/live_exporter.py` ofrece consultas locales de solo lectura en `127.0.0.1:9108`: estado de la fuente, rutas y eventos; no crea fallas ni modifica routers o interfaces. Sus métricas se integraron con Prometheus y reglas locales de alarma durante las pruebas iniciales. Se diferenció la disponibilidad del servicio del estado de la WAN y de la ruta instalada.

Las mediciones discretas no garantizan continuidad sin pérdidas entre sondeos ni un tiempo universal de convergencia. Los procesos B3 y sus datos históricos se mantienen separados de las fuentes S04.

Para la implementación validada sobre **tres sedes, cuatro WAN y nueve VLAN**, consultar [Colector S04](README-S04.md) y [NOC](../noc-s04/README.md). La máquina está en pausa tras apagado ordenado de S04.
