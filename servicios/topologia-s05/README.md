# NOC de topología multisede — S05

Implementamos este componente para consultar y visualizar el estado de las tres sedes **HQ, S1 y S2**, con rutas WAN, interfaces, agregación LACP, disponibilidad HTTP y segmento SDN. La interfaz web y API se ejecutan localmente en `127.0.0.1:9130`.

## Funciones implementadas

- Representación de la topología de **18 nodos y 21 enlaces**; vistas de sede y detalle de enlaces.
- Datos reales de rutas FIB S1/S2, con diferenciación entre enlace preferido, respaldo disponible, respaldo seleccionado y estado no observado.
- Tarjetas del NOC para LACP 802.3ad en HQ/S1/S2, servidor HTTP seleccionado y controlador Faucet/OpenFlow.
- Observaciones de salud y fuente de telemetría; no se transforma una muestra ausente en una caída ficticia.
- Hora de consulta presentada en `America/Panama` y selección reversible de elementos de la topología.

El acceso a operaciones de diagnóstico privilegiadas está limitado a un observador de solo lectura. Este servicio no administra directamente rutas, bridges, bonds o interfaces de gestión.

## Validación técnica

Se comprobaron estados LACP de dos miembros por sede, Faucet conectado con reglas OpenFlow, rutas preferidas S1=`s1p` y S2=`s2p`, y disponibilidad HTTP en HQ. En la fase S05 se observó también la conmutación de backend `HQ → S1 → HQ` en 17 muestras, tras una parada controlada únicamente del servicio backend HQ. La API regresó al estado principal y los seis servicios supervisados quedaron activos.

La cifra de flujos OpenFlow representa reglas observadas, no una medición de throughput ni una garantía de entrega de tráfico. Esta implementación constituye HA lógica entre servicios dentro de una VM, no una solución HA de hardware.

## Referencias

[Acta S05](../../docs/gestion/ACTA-ACEPTACION-TECNICA-S05-20261115.md) · [Diseño HA](../../docs/diseno/s05-ha-servicios-multisede.md) · [Evidencias](../../evidencias/capturas/README.md).
