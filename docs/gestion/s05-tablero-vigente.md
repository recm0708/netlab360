# Fase S05 — Tablero técnico de aceptación

**Corte:** 15 de noviembre de 2026. Presentamos resultados verificados del laboratorio, no porcentajes estimados.

| Componente | Evidencia o resultado | Estado |
|---|---|---|
| Red multisede | HQ/S1/S2, cuatro WAN, nueve VLAN; rutas preferidas y respaldo OSPF | Comprobado |
| Alta disponibilidad HTTP | Backends HQ/S1; una conmutación real HQ→S1→HQ con 17 muestras y retorno estable | Comprobado |
| LACP | Tres sedes con dos miembros agregados; caída y restauración 2→1→2 | Comprobado |
| SDN | OVS/Faucet aislado, VLAN410 A–B permitida, VLAN420 C aislada; puerto restaurado | Comprobado |
| NOC | Topología de 18 nodos y 21 enlaces; fuentes reales para FIB, HA, LACP y Faucet | Comprobado |
| Integridad de P1/P1B | Original 10/11 recuperado 4/4; P1B 5/5; corrida 11/11 identificada por separado | Comprobado |
| Integridad de evidencias S05 | 71 PNG originales y 2 registros HA, manifiestos SHA-256 correctos | Validado en rama local |
| Aceptación operativa | Lote 158, 21 namespaces, 4 contenedores, 6 servicios y gestión intacta | Comprobada |
| Publicación y aceptación documental | Commit/push/PR/merge de los 77 archivos y referencia en informe | Pendiente |
| Recuperación tras reinicio del invitado | Reconstrucción de namespaces y servicios S02/S05 | No demostrada |

## Criterios de cierre

Para dar por concluida la aceptación documental de S05 comprobaremos que los 71 PNG y sus manifiestos, el JSONL de 17 observaciones y el registro del ensayo HA figuren en `main`; verificaremos sus SHA-256 en GitHub, incorporaremos referencias al control del informe y resolveremos los checklists vigentes de las issues [#5](https://github.com/recm0708/netlab360/issues/5), [#23](https://github.com/recm0708/netlab360/issues/23), [#31](https://github.com/recm0708/netlab360/issues/31), [#32](https://github.com/recm0708/netlab360/issues/32), [#64](https://github.com/recm0708/netlab360/issues/64) y [#105](https://github.com/recm0708/netlab360/issues/105). La milestone S05 continuará abierta mientras falte algún criterio verificable.

## Limitaciones

Los enlaces, instancias HTTP y conmutaciones pertenecen a una plataforma virtualizada sobre una sola VM. No atribuimos redundancia de equipo físico, capacidad de enlaces reales ni disponibilidad continua a las medidas obtenidas. El fallo de un miembro LACP no representa la caída de una VM; son escenarios distintos evaluados por separado.

[Índice de evidencia](../../evidencias/capturas/README.md) · [Estado consolidado](../00-estado-y-continuidad.md) · [Control del documento académico](../entregables/01-proyecto-investigacion-maestro.md).
