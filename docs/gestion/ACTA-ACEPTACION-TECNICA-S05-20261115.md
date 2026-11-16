# Acta de aceptación técnica — fase 5

**Proyecto:** NETLAB360  
**Validación operativa:** 15 de noviembre de 2026  
**Integridad y publicación de evidencias:** 16 de noviembre de 2026

## Objeto

Comprobamos la integración de una red multisede virtual en HQ, S1 y S2, incorporando alta disponibilidad lógica HTTP, agregación LACP 802.3ad, segmentación OVS/Faucet y un centro de operaciones de red que observa fuentes reales.

## Resultados verificados

| Dominio | Comprobación |
|---|---|
| WAN/OSPF y VLAN | Cuatro WAN, nueve VLAN; conmutación y retorno de rutas observados |
| LACP | Dos miembros por sede, prueba de falla y recuperación 2→1→2 |
| OVS/Faucet | VLAN410 A/B comunicada, VLAN420 C aislada y puerto restaurado |
| HTTP HA | Backend HQ→S1→HQ observado en 17 muestras, timer de rescate cancelado |
| NOC | API saludable, 18 nodos/21 enlaces, FIB, LACP, HA y controlador SDN |
| Estado de VM | 21 namespaces, cuatro contenedores y seis servicios activos |
| Gestión | `ens33 192.168.47.40/24`, gateway `192.168.47.2`, intactos |
| Integridad P1/P1B | 4/4 archivos históricos P1 y 5/5 P1B con SHA comprobado |
| Evidencias S05 | 71 PNG, inventario, tres manifiestos y dos registros HA, 77 archivos en total |

## Trazabilidad documental

El lote 158 acreditó los resultados operativos sin provocar nuevas fallas. El conjunto de 77 archivos se publicó sin modificar los originales mediante el [PR #152](https://github.com/recm0708/netlab360/pull/152), fusionado en `main`. Los 71 PNG y sus registros se conservan en [evidencias S05](../../evidencias/capturas/fase5/README.md) y [registros HA](../../evidencias/registros/s05/).

## Alcance de aceptación

**La implementación y la aceptación técnica de S05 quedan comprobadas.** El informe académico único, las ampliaciones S06–S07 y el paquete final S08 son actividades independientes que siguen pendientes de sus propios criterios.

Las conmutaciones son lógicas dentro de una única VM; no demuestran redundancia física, disponibilidad contractual ni recuperación tras reiniciar Ubuntu. Los namespaces efímeros deben conservarse mediante suspensión controlada hasta validar una reconstrucción segura.
