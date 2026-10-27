# NETLAB360 S02 — Tres routers FRRouting en Docker Compose

**Estado validado en S02 y reutilizado durante S03/S04.** El escenario experimental fue desmontado de forma controlada al finalizar S04 y la VM recibió orden de apagado.

`topologias/s02-frr/docker-compose.yml` define tres contenedores con FRRouting 10.7.1: `nl360-s02-r-hq`, `nl360-s02-r-s1` y `nl360-s02-r-s2`, con `network_mode:none`. Las configuraciones generadas desde `inventario/ipam/topologia-s02.yaml` se prepararon en `~/netlab360-bootstrap/s02/rendered/` y se utilizaron desde directorios externos de ejecución.

Los scripts de despliegue configuran cuatro enlaces WAN `s1p/s1b/s2p/s2b`, costos OSPF 10/100 y tres redes locales VLAN por sede, sin adjuntar la interfaz `ens33`. Se verificaron FULL HQ/S1/S2 **4/2/2**, rutas preferidas **6/6**, pings de loopback **6/6**, nueve puertas de enlace y seis comprobaciones LAN. Se ejecutó fallo/restauración de S1 y S2 y pruebas HTTP/ACL selectivas; en S04 se integró el colector/NOC de observabilidad.

**Operación segura:** usar scripts `scripts/laboratorio/s02-routers-start.sh`, `s02-wan-links.py`, `s02-lan-vlan.py` y validadores oficiales exclusivamente bajo sus prechecks y controles de propiedad; desmontar en orden inverso LAN→WAN→FRR. No recrear los contenedores para obtener capturas ya verificadas.

[Continuidad y estado de la VM](../../docs/REANUDAR-AQUI.md) · [Aceptación S02](../../docs/control/05-s02-aceptacion-y-documentacion-2026-10-24.md).
