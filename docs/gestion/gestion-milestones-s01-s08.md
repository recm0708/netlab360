# Gestión y aceptación de milestones S01–S08

## Estado vigente

Las fases S01–S06 están cerradas. S07 tiene sus ocho issues técnicas cerradas y el catálogo validado; su issue maestra permanece abierta por la actualización del informe. S08 conserva sus criterios de implementación y aceptación.

| Milestone | Estado | Criterio central |
|---|---|---|
| S01 | Cerrada | VM, IPAM, SSH y línea base |
| S02 | Cerrada | Tres sedes, FRRouting, OSPF, cuatro WAN y nueve VLAN |
| S03 | Cerrada | SoT candidata, Ansible, OpenTofu local y CI/CD |
| S04 | Cerrada | Observabilidad, incidentes, persistencia y SLI/SLO experimentales |
| S05 | Cerrada | HTTP HA, LACP multisede, SDN y NOC integrado |
| S06 | Cerrada | Diagnóstico experimental V2, modelos congelados, FAULT HTTP independiente y recuperación |
| S07 | Abierta (cierre académico) | AIOps supervisado, aprobación, reversión segura y API validadas |
| S08 | Abierta | Consola interactiva, regresión y entrega académica |

## Reconciliación de GitHub

S07 comprende la issue maestra #7 y las ocho issues técnicas #190–#197. S08 incorpora el copiloto RAG #198 además de sus issues vigentes. #17 (OpenTofu externo) y #24 (cuarta sede/WireGuard) permanecen condicionadas; su destino se decidirá al reevaluar S07 y S08. S09 no dispone de milestone aprobada.

Asignamos un pull request a un milestone únicamente cuando existe un hito de aceptación inequívoco. Los PR transversales conservan sus etiquetas temáticas y de fase pertinentes; cuando no existe un hito principal, permanecen sin milestone. Revisamos las asignaciones históricas según el alcance y la evidencia de aceptación de cada cambio. Esta clasificación no acredita funcionalidades adicionales ni altera por sí sola la aceptación académica.

El cierre de una milestone exige comprobar el estado y los criterios de aceptación de sus issues. El porcentaje de GitHub no representa por sí solo el avance técnico ni una calificación académica.

El [reconciliador de milestones](../../scripts/operacion/reconciliar_milestones_netlab360.py) admite una auditoría no mutadora mediante `--check`. La ejecución de `--apply` requiere una necesidad previamente identificada y autorización específica. No repetir operaciones de recálculo sobre una milestone ya reconciliada.

## Límites y seguimiento

S06 no acredita pronóstico de fallas futuras, MAE prospectivo, deriva de concepto inferencial, generalización entre ICMP y HTTP ni remediación autónoma.

Las ampliaciones tecnológicas se evaluarán conforme a su necesidad, viabilidad y pruebas propias, sin modificar retroactivamente los resultados de las fases cerradas.

[Plan maestro](../diseno/s06-s08-plan-maestro-y-criterios.md) · [Cobertura académica](cobertura-academica-netlab360.md).
