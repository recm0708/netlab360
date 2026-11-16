# Arquitectura y validación de alta disponibilidad HTTP — S05

Implementamos una solución de **alta disponibilidad lógica de servicio HTTP** basada en dos backends ubicados en las sedes HQ y S1. Un frontal en HQ selecciona la instancia principal y conmuta a la secundaria cuando la primera deja de estar disponible. La observación desde S2 permite comprobar la selección del servicio sin confundirla con el estado de la WAN.

## Componentes implementados

| Función | Sede y VLAN | Namespace | IPv4 |
|---|---|---|---|
| Backend principal HTTP | HQ, VLAN120 | `nl360-s05-ha-hq` | `10.70.20.21/24` |
| Backend secundario HTTP | S1, VLAN220 | `nl360-s05-ha-s1` | `10.71.20.21/24` |
| Frontal de acceso | HQ, VLAN120 | `nl360-s05-ha-fe` | `10.70.20.23/24` |
| Cliente de observación | S2, VLAN320 | `nl360-s02-h-s2-320` | `10.72.20.20/24` |

Los backends comparten la infraestructura multisede previamente creada; no modificamos la red administrativa `ens33`. Su selección y los estados de servicio se observan en el NOC de S05 por medio de fuentes de telemetría reales.

## Verificación del servicio

Comprobamos respuestas HTTP correctas de ambos backends y del frontal. Posteriormente efectuamos **una única interrupción controlada del backend HQ**, después de programar un rescate autónomo mediante `systemd` para restablecer exclusivamente esa unidad. El NOC registró **17 observaciones** con la secuencia `BACKEND_HQ → BACKEND_S1 → BACKEND_HQ`. El temporizador se canceló tras comprobar la restauración; el frontal, el monitor S2 y los servicios de observabilidad quedaron activos.

La regresión posterior acreditó FIB S1=`s1p`, S2=`s2p`, seis servicios activos y gestión `192.168.47.40/24` intacta. La evidencia original se conserva en JSONL, TXT y PNG64 con manifiestos SHA-256.

## Límites y recuperabilidad

Esta prueba verifica tolerancia al fallo lógico de **una instancia backend** dentro de una única VM, no HA del frontal, del propio host Ubuntu, del hipervisor, del almacenamiento ni del equipo físico. Tampoco equivale a failover de miembro LACP ni a conmutación de enlace WAN; estos mecanismos se validaron en escenarios separados.

El rescate de `systemd` depende de que Ubuntu continúe ejecutándose. Un apagado normal de la VM destruiría los namespaces efímeros si no se ha completado su reconstrucción reproducible. Para pausas temporales preservamos el estado mediante suspensión VMware.

[Acta técnica de S05](../gestion/ACTA-ACEPTACION-TECNICA-S05-20261115.md) · [Evidencias](../../evidencias/capturas/README.md).
