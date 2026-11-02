# NETLAB360 — Cierre interno de las fases S01 a S03

**Corte 01/11/2026:** las tres fases están terminadas según sus pruebas y los límites técnicos declarados. No equivale a aprobación docente final.

| Fase | Estado | Alcance demostrado | Evidencias |
|---|---|---|---:|
| S01 | Cerrada (#1, #38) | Base VMware/Ubuntu, IPAM, FRR/OSPF, VLAN/ACL, LACP, observabilidad inicial; acceso SSH por clave y recuperación VMware | 83 PNG |
| S02 | Cerrada (#2) | Tres sedes, cuatro WAN, nueve VLAN, OSPF Full 4/2/2, conmutación, HTTP/ACL | 9 PNG |
| S03 | Cerrada por alcance real (#3, #16) | SoT candidate validada, Ansible FRR 8/8, drift 100→150→100, OpenTofu de 17 metadatos y GitOps/CI | 8 PNG |

**Contrato S03:** la SoT tiene estado `candidate` para pruebas, no está aprobada para producción. Ansible administra FRR activo y OpenTofu mantiene 17 objetos de metadatos, sin gestionar enlaces ni routers externos. La integración de `data sources` y propiedad de recursos externos **no fue implementada**: está reprogramada como ampliación S05+ en la issue #17, abierta.

El firmware y disco de la VM se comprobaron en S01. El origen de ISO de instalación no puede certificarse con los registros disponibles y queda declarado como límite documental, no como defecto operativo.

**Total oficial al cierre S04:** 122 PNG (83/9/8/22) con controles de integridad. S04 sigue pendiente de ratificar el SLO académico y de registrar el dictamen docente.

[Continuidad](../REANUDAR-AQUI.md) · [Tablero de fases](06-tablero-porcentajes-cierre-fases-2026-10-25.md).
