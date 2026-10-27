# NETLAB360 S04 — Colector de métricas multisede y Prometheus

**Estado verificado 27/10/2026: integrado con la topología real HQ/S1/S2 y comprobado durante incidentes.**

## Funciones y límites

`servicios/observabilidad/s04_exporter_multisede.py` consulta en solo lectura el SoT `candidate`, Docker y las interfaces permitidas de los tres routers FRRouting. Publica `/api/v1/state`, `/metrics` y estado de salud local en `127.0.0.1:9110`. Se observaron **25 series**, ocho extremos WAN, nueve interfaces VLAN y tres sedes. Una interfaz `admin_up` no prueba transferencia exitosa de paquetes ni conectividad de aplicación.

Prometheus 3.7.0 utilizó `127.0.0.1:9091` con reglas de alerta de indisponibilidad de fuente, WAN y VLAN. La TSDB permitió consultar historia de HQ/s1p y conservar **68/68** muestras WAN y **28/28** muestras de alerta después de reiniciar Prometheus. La retención no es indefinida.

Ante interrupción controlada de la fuente, el NOC informó `UNKNOWN`, Prometheus `scrape=down`, alarma del exporter `firing`, **sin falsas alarmas WAN/VLAN**, seguido de recuperación. En el incidente real HQ/s1p, la alerta WAN alcanzó `pending/firing` y se resolvió con la restauración del enlace.

## SLI

Se registraron 450/450 scrapes correctos (100 %, 15m) y 1698/1740 (97,586 %, 60m), con 42 fallos y presupuesto −25 para un objetivo **99 % únicamente candidato**. La métrica `source_up` depende de muestras presentes, por lo que no sustituye disponibilidad total del exporter ni de aplicaciones.

[Decisión y resultados G5](../../docs/operaciones/s04-g5-decision-medida-notificaciones-locales.md) · [Matriz G6](../../docs/operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md).

No levantar los procesos después del apagado S04 sin iniciar las verificaciones de continuidad S05 y proteger la interfaz administrativa `ens33`.
