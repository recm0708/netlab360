# NETLAB360 S01 — FRRouting dual-WAN, primer laboratorio

**Estado validado durante la fase 1.** Este directorio conserva configuraciones del ensayo HQ/S1 ejecutado con FRRouting 10.7.1 sobre enlaces virtuales aislados de la gestión del host.

Se emplearon enlaces principal `10.78.0.0/30` (costo OSPF 10) y alternativo `10.78.0.4/30` (costo 100), con router HQ `10.79.0.1/32` y router S1 `10.79.0.2/32`. Las pruebas comprobaron adyacencias OSPF Full, selección de WAN preferida, conmutación hacia respaldo, restauración y solicitudes HTTP satisfactorias en los estados estables correspondientes.

Los ensayos fueron aislados y no constituyen por sí solos la topología integrada de tres sedes, que se implementó y validó posteriormente en [topologías S02](../s02-frr/README.md). La comunicación HTTP medida no implica cero pérdida durante cada transición.

**Seguridad:** no conectar redes de laboratorio a `ens33`, VMnet8 ni cambiar la ruta de gestión; verificar snapshot/prechecks para nuevos despliegues.
