# Centro de operaciones multisede

## Descripción

Implementamos un NOC web local para observar las sedes HQ, S1 y S2, consultar su estado y conservar el historial de incidentes de laboratorio.

## Componentes

- [Aplicación NOC](app.py), disponible en `127.0.0.1:9120`.
- [Historial de incidentes](historial_s04.py) mediante SQLite.
- [Exportador y métricas](../observabilidad/README.md) en el entorno multisede.

## Resultados

Durante el ensayo WAN observamos la transición **pending → firing → resolved**, con selección del enlace alternativo y posterior recuperación. Comprobamos la conservación de tres eventos en SQLite después de reiniciar el servicio NOC.

## Limitaciones

El sistema distingue entre fuente disponible, entorno desmontado y estado `UNKNOWN`. No interpreta automáticamente una muestra ausente como falla WAN. La implementación registra alertas locales, pero no envía notificaciones externas ni corrige rutas sin intervención autorizada.

## Documentación relacionada

[Resultados de entorno, red y observabilidad](../../docs/validacion/s01-s04-resultados.md) · [Capturas de observabilidad](../../evidencias/capturas/fase4/README.md).
