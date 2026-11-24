# Diseño de disponibilidad HTTP — Fase 05

## Descripción

Implementamos dos instancias lógicas de servicio HTTP en HQ y S1, con un frontal de acceso en HQ y observación desde S2. El objetivo es evaluar la selección de una instancia alternativa cuando el backend principal deja de responder.

## Arquitectura

| Componente | Ubicación | Dirección IPv4 |
|---|---|---|
| Backend principal | HQ, VLAN 120 | `10.70.20.21/24` |
| Backend alternativo | S1, VLAN 220 | `10.71.20.21/24` |
| Frontal HTTP | HQ, VLAN 120 | `10.70.20.23/24` |
| Cliente de observación | S2, VLAN 320 | `10.72.20.20/24` |

La selección de servicio se representa en el NOC junto con el estado de la red multisede.

## Validación

Durante una única interrupción controlada del backend HQ, el NOC registró **17 observaciones** con la secuencia **HQ → S1 → HQ**. La recuperación del servicio principal se comprobó después de restablecer su unidad de ejecución.

La validación posterior acreditó seis servicios activos, rutas principales S1=`s1p` y S2=`s2p`, y continuidad de la interfaz administrativa `ens33`.

## Protección de la intervención controlada

El ensayo de interrupción del backend HQ utilizó un temporizador independiente de la conexión SSH, gestionado por systemd, para solicitar la recuperación del servicio principal después de 120 segundos si permanecía detenido.

La intervención se limita a la instancia autorizada. Los controles previos y posteriores verifican los servicios, las rutas, la red administrativa y la selección del backend.

Este mecanismo reduce el riesgo de dejar el servicio detenido cuando se interrumpe la sesión del operador. No garantiza recuperación si Ubuntu se apaga o deja de ejecutar systemd.

Procedimiento: [ciclo HA protegido](../../scripts/operacion/s05-lote-ha-instancia-con-watchdog.sh).

## Limitaciones

La conmutación se produce entre instancias de aplicación dentro de una misma VM. No constituye redundancia del frontal, de Ubuntu, de VMware ni del hardware físico. Tampoco debe confundirse con la recuperación de un miembro LACP o con la conmutación de un enlace WAN.

## Documentación relacionada

[Arquitectura multisede](../arquitectura/arquitectura-multisede-implementada.md) · [Validación S05](../validacion/s05-integracion-y-aceptacion.md) · [Capturas S05](../../evidencias/capturas/fase5/README.md).
