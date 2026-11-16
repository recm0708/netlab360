# Estado técnico consolidado de NETLAB360

**Fecha de corte:** 15 de noviembre de 2026. Este documento describe la situación observada al terminar la validación de S05; no sustituye los registros de ensayos.

## Resultados obtenidos

Las fases S01–S04 cuentan con evidencia técnica de FRRouting/OSPF, infraestructura de tres sedes, automatización Ansible, recursos OpenTofu locales de metadatos y observabilidad con historial de incidentes. Durante S04 medimos un SLI de recolección del 100 % (15 minutos) y del 97,586 % (60 minutos); la segunda ventana no alcanzó la referencia experimental del 99 %.

En S05 validamos cuatro WAN, nueve VLAN, rutas preferidas y de respaldo, enlaces LACP 802.3ad con dos miembros por sede, aislamiento SDN con Open vSwitch/Faucet y el NOC de topología. La conmutación lógica de HTTP entre los backends HQ y S1 se confirmó mediante 17 muestras y posterior retorno a HQ, sin modificar la red administrativa.

El último lote de aceptación técnica de solo lectura (`158`) confirmó 21 namespaces, cuatro contenedores, seis servicios activos, NOC saludable y gestor de red `192.168.47.40/24`. Los originales P1 y P1B se comprobaron mediante SHA-256 (4/4 y 5/5), así como 71 PNG y dos registros de HA.

## Situación documental y GitHub

El inventario de 71 capturas y sus manifiestos se preparó en la rama local `evidencias/s05-70png-verificados-20261115`. La auditoría de archivos y revisión visual terminó sin detectar información sensible evidente. **Aún resta confirmar el commit, push y merge en `main`**. No se considera cerrada la aceptación documental hasta comprobar los blobs publicados y actualizar las issues afectadas.

El borrador académico maestro revisado al 1/11/2026 integraba S01–S04. La incorporación de S05 al mismo informe, la preparación de S06/S07 y la entrega final S08 se mantienen diferenciadas.

## Conservación del entorno

El laboratorio actual depende de 21 namespaces efímeros. La suspensión de VMware preserva el estado en memoria para reanudar posteriormente; **no acredita reconstrucción tras apagar el invitado**. El apagado normal de Ubuntu requiere antes una estrategia de reconstrucción probada y copias verificadas.

[Reanudar trabajo](REANUDAR-AQUI.md) · [Tablero S05](gestion/s05-tablero-vigente.md) · [Criterios de entrega](entregables/00-politica-editorial-y-entrega-acumulativa.md).
