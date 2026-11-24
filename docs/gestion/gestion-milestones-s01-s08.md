# Gestión y aceptación de hitos de las fases 01–08

## Estado vigente

Las fases 01 a 07 están cerradas. La fase 08 permanece abierta para su implementación y aceptación integral.

Utilizamos la denominación «Fase 01», «Fase 02» y sucesivas en la documentación técnica. Los títulos de los hitos de GitHub utilizan «Fase 1», «Fase 2» y sucesivos, como convención administrativa. Conservamos los códigos S01, S02 y sucesivos exclusivamente como identificadores técnicos cuando forman parte de rutas, archivos, esquemas, ensayos, prefijos de issues y pull requests o evidencias originales.

| Hito | Estado | Criterio central |
|---|---|---|
| Fase 01 | Cerrada | VM, IPAM, SSH y línea base |
| Fase 02 | Cerrada | Tres sedes, FRRouting, OSPF, cuatro WAN y nueve VLAN |
| Fase 03 | Cerrada | SoT candidata, Ansible, OpenTofu local y CI/CD |
| Fase 04 | Cerrada | Observabilidad, incidentes, persistencia y SLI/SLO experimentales |
| Fase 05 | Cerrada | HTTP HA, LACP multisede, SDN y NOC integrado |
| Fase 06 | Cerrada | Diagnóstico experimental V2, modelos congelados, FAULT HTTP independiente y recuperación |
| Fase 07 | Cerrada | AIOps supervisado, aprobación, reversión segura y API validadas |
| Fase 08 | Abierta | Consola interactiva, regresión y entrega académica |

## Reconciliación de GitHub

La fase 07 comprende la issue maestra #7 y las ocho issues técnicas #190–#197. La fase 08 incorpora el copiloto RAG #198 además de sus issues vigentes. #17 (OpenTofu externo) y #24 (cuarta sede/WireGuard) permanecen condicionadas; su destino se decidirá al reevaluar las fases 07 y 08. La fase 09 no dispone de milestone aprobada.

Asignamos un pull request a un milestone únicamente cuando existe un hito de aceptación inequívoco. Los PR transversales conservan sus etiquetas temáticas y de fase pertinentes; cuando no existe un hito principal, permanecen sin milestone. Revisamos las asignaciones históricas según el alcance y la evidencia de aceptación de cada cambio. Esta clasificación no acredita funcionalidades adicionales ni altera por sí sola la aceptación académica.

El cierre de una milestone exige comprobar el estado y los criterios de aceptación de sus issues. El porcentaje de GitHub no representa por sí solo el avance técnico ni una calificación académica.

El [reconciliador de milestones](../../scripts/operacion/reconciliar_milestones_netlab360.py) admite una auditoría no mutadora mediante `--check`. La ejecución de `--apply` requiere una necesidad previamente identificada y autorización específica. No repetir operaciones de recálculo sobre una milestone ya reconciliada.

## Límites y seguimiento

La fase 06 no acredita pronóstico de fallas futuras, MAE prospectivo, deriva de concepto inferencial, generalización entre ICMP y HTTP ni remediación autónoma.

Las ampliaciones tecnológicas se evaluarán conforme a su necesidad, viabilidad y pruebas propias, sin modificar retroactivamente los resultados de las fases cerradas.

[Plan maestro](../diseno/s06-s08-plan-maestro-y-criterios.md) · [Cobertura académica](cobertura-academica-netlab360.md).
