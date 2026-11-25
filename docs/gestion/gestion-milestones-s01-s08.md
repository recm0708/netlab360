# Gestión y aceptación de hitos

## Estado vigente

Las fases 01–07 están cerradas. Las fases 08–10 están abiertas y disponen de alcance, issues y criterios de aceptación propios.

La documentación técnica utiliza títulos y referencias por componente. Los títulos de los hitos de GitHub utilizan «Fase 1», «Fase 2» y sucesivos, como convención administrativa. Conservamos los códigos S01, S02 y sucesivos exclusivamente como identificadores técnicos cuando forman parte de rutas, archivos, esquemas, ensayos, prefijos de issues y pull requests o evidencias originales.

| Hito | Estado | Criterio central |
|---|---|---|
| Fase 01 | Cerrada | VM, IPAM, SSH y línea base |
| Fase 02 | Cerrada | Tres sedes, FRRouting, OSPF, cuatro WAN y nueve VLAN |
| Fase 03 | Cerrada | SoT candidata, Ansible, OpenTofu local y CI/CD |
| Fase 04 | Cerrada | Observabilidad, incidentes, persistencia y SLI/SLO experimentales |
| Fase 05 | Cerrada | HTTP HA, LACP multisede, SDN y NOC integrado |
| Fase 06 | Cerrada | Diagnóstico experimental V2, modelos congelados, FAULT HTTP independiente y recuperación |
| Fase 07 | Cerrada | AIOps supervisado, aprobación, reversión segura y API validadas |
| Fase 08 | Abierta | Plataforma interactiva, RAG, observabilidad avanzada y recuperación |
| Fase 09 | Abierta | Ampliación tecnológica y automatización avanzada |
| Fase 10 | Abierta | Validación científica, aceptación integral y entrega |

## Reconciliación de GitHub

La fase 07 comprende la issue maestra #7 y las ocho issues
técnicas #190–#197. El PR #202 permanece asignado y fusionado.

Las issues maestras de las fases restantes son #8, #212 y #218.
OpenTofu avanzado (#17) y WireGuard (#24) corresponden a la
fase 09. Los entregables académicos finales se consolidan en
la fase 10; la documentación y las evidencias se actualizan
al cerrar cada fase.

Asignamos un pull request a un milestone únicamente cuando existe un hito de aceptación inequívoco. Los PR transversales conservan sus etiquetas temáticas y de fase pertinentes; cuando no existe un hito principal, permanecen sin milestone. Revisamos las asignaciones históricas según el alcance y la evidencia de aceptación de cada cambio. Esta clasificación no acredita funcionalidades adicionales ni altera por sí sola la aceptación académica.

El cierre de una milestone exige comprobar el estado y los criterios de aceptación de sus issues. El porcentaje de GitHub no representa por sí solo el avance técnico ni una calificación académica.

El [reconciliador de milestones](../../scripts/operacion/reconciliar_milestones_netlab360.py) admite una auditoría no mutadora mediante `--check`. La ejecución de `--apply` requiere una necesidad previamente identificada y autorización específica. No repetir operaciones de recálculo sobre una milestone ya reconciliada.

## Límites y seguimiento

La fase 06 no acredita pronóstico de fallas futuras, MAE prospectivo, deriva de concepto inferencial, generalización entre ICMP y HTTP ni remediación autónoma.

Las ampliaciones tecnológicas se evaluarán conforme a su necesidad, viabilidad y pruebas propias, sin modificar retroactivamente los resultados de las fases cerradas.

[Plan maestro](../diseno/s06-s08-plan-maestro-y-criterios.md) · [Cobertura académica](cobertura-academica-netlab360.md).

## Corte de aceptación de la consola

El backend (#204) y el explorador técnico (#243) están cerrados. La interfaz operacional (#205) conserva dos criterios de equivalencia integral pendientes; los PR funcionales hasta #253 se fusionaron. La regresión específica comprende 204 casos aprobados y la validación de Swagger en ambos temas. Las pruebas de red (#206) y sondas/SLI/SLO (#207) son el siguiente alcance. La administración avanzada (#242), recuperación (#106) y aceptación integral (#211) siguen abiertas.
