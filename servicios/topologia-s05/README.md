# NOC de topología multisede — Fase 05

## Descripción

Implementamos una interfaz web y API para consultar la topología integrada de HQ, S1 y S2, con indicadores WAN, FRRouting, LACP, disponibilidad HTTP y controlador SDN.

## Componentes

- [Aplicación de topología](app.py) e [interfaz web](index.html) en `127.0.0.1:9130`.
- Representación de **18 nodos y 21 enlaces**, con detalles por sede.
- Rutas FIB principales y alternativas de S1 y S2.
- Estado de los agregadores LACP y conexión OpenFlow/Faucet.
- Selección del backend HTTP y visualización de la hora de Panamá.

## Resultados

Comprobamos rutas principales S1=`s1p` y S2=`s2p`, agregación de dos enlaces por sede y controlador Faucet conectado. El NOC registró la conmutación HTTP **HQ → S1 → HQ** a lo largo de 17 muestras. Los seis servicios supervisados permanecieron activos tras la recuperación.

## Limitaciones

La consola consulta fuentes reales, pero no administra directamente rutas ni switches. La existencia de reglas OpenFlow no equivale a una prueba de tráfico exitoso; los resultados de HA corresponden a servicios lógicos dentro de una VM.

## Documentación relacionada

[Validación S05](../../docs/validacion/s05-integracion-y-aceptacion.md) · [Diseño HTTP](../../docs/diseno/s05-ha-servicios-multisede.md) · [Capturas S05](../../evidencias/capturas/fase5/README.md).
