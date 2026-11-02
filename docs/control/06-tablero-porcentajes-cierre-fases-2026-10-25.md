# NETLAB360 — Estado de fases y criterios de aceptación

**Corte operativo actualizado: 01/11/2026.** Distinguimos entre cierre técnico interno de cada fase, avance de issues/milestones y aprobación de la docente. No utilizamos porcentajes históricos como calificaciones ni como evidencia de finalización.

| Fase | Estado interno | Alcance acreditado | Seguimiento |
|---|---|---|---|
| S01 | **Cerrada** | Base VMware/Ubuntu, redes virtuales, OSPF dual WAN, VLAN/ACL, LACP y seguridad SSH ED25519 | [#1](https://github.com/recm0708/netlab360/issues/1), [#38](https://github.com/recm0708/netlab360/issues/38) |
| S02 | **Cerrada** | HQ/S1/S2, cuatro WAN, nueve VLAN, OSPF 4/2/2, failover y HTTP/ACL | [#2](https://github.com/recm0708/netlab360/issues/2) |
| S03 | **Cerrada por alcance implementado** | SoT candidate, Ansible FRR 8/8, drift reconciliado, OpenTofu 17 metadatos y GitOps | [#3](https://github.com/recm0708/netlab360/issues/3), [#16](https://github.com/recm0708/netlab360/issues/16) |
| S04 | **Implementación cerrada; aceptación académica pendiente** | Observabilidad, NOC, alertas de WAN, persistencia y mediciones SLI reales | [#4](https://github.com/recm0708/netlab360/issues/4), [#21](https://github.com/recm0708/netlab360/issues/21) |
| S05–S08 | Pendientes | Nuevas funciones de red, integración, demostración y entregables | Planificación posterior |

**Delimitación S03:** no implementamos `data sources` ni propiedad de recursos externos OpenTofu. Reprogramamos ese objetivo a [#17](https://github.com/recm0708/netlab360/issues/17) para una fase posterior y no lo contamos como prueba satisfactoria de S03.

**Medición S04:** en 15 minutos obtuvimos 450/450 scrapes (100 %) y en 60 minutos 1698/1740 (97,586 %), con 42 fallos. El objetivo académico 99 % se mantiene candidato **sin ratificación** y no se cumplió en la segunda ventana. Solo acreditamos avisos visuales locales.

**Evidencia publicada:** 122 PNG con manifiestos e integridad verificada: 83 de S01, 9 de S02, 8 de S03 y 22 de S04. Las capturas administrativas nuevas de SSH y firmware, así como preapagado y postcheck de S04, no se agregan al catálogo por ser redundantes frente a resultados ya preservados.

**Documento escrito:** borrador 4.6, 113 páginas, figuras 1–20 y tablas 1–13, con las cuatro primeras fases tratadas. La revisión académica prevista para el 30/10 no tiene dictamen confirmado en el repositorio. No inferimos aprobación docente por completar la parte técnica.

[Continuidad](../REANUDAR-AQUI.md) · [Puertas S01–S03](07-puertas-cierre-fases1-a-3-2026-10-25.md) · [Evidencias](../../evidencias/capturas/README.md).
