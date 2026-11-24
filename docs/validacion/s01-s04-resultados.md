# Validación técnica de las fases 01–04

## Descripción

Las cuatro primeras fases establecieron la infraestructura de NETLAB360, integraron el enrutamiento multisede, incorporaron automatización declarativa y permitieron estudiar el comportamiento de las redes mediante métricas e incidentes observados.

## Resultados comprobados

| Fase | Componentes validados | Evidencias gráficas |
|---|---|---:|
| S01 | Ubuntu/VMware, FRRouting/OSPF inicial, VLAN, ACL, enlace redundante experimental y acceso remoto | 83 |
| S02 | HQ/S1/S2, cuatro WAN, nueve VLAN, OSPF FULL 4/2/2, rutas de respaldo y HTTP/ACL | 9 |
| S03 | SoT candidata, auditoría Ansible sobre FRR, detección y reconciliación de drift, 17 objetos locales OpenTofu y GitOps | 8 |
| S04 | Exportador WAN/VLAN, Prometheus, NOC multisede, incidente controlado, persistencia y medición de SLI | 22 |

## Validación de red

En la red de tres sedes comprobamos rutas preferidas y alternativas, conexión entre las LAN y conmutación de enlaces WAN con retorno a la ruta principal. Los routers FRRouting mantuvieron adyacencias OSPF FULL y las VLAN permitieron diferenciar tráfico por sede y por función.

## Automatización

La fuente de información S03 fue una configuración **candidata** para ensayos, no un sistema de control de producción. Ansible verificó el estado activo de FRRouting y permitió restaurar ajustes previamente modificados. Los recursos OpenTofu representaron **17 metadatos locales**; no se atribuye a OpenTofu la creación de routers o enlaces externos.

## Observabilidad

S04 registró la interrupción y recuperación de un enlace WAN con transición de alerta `pending → firing → resolved`. Se comprobó la persistencia del historial SQLite y de las series del sistema de métricas después de reiniciar los servicios correspondientes.

La recogida de métricas alcanzó el **100 %** en una ventana de 15 minutos y el **97,586 %** en una ventana de 60 minutos. Esta última medición quedó por debajo de la referencia experimental del **99 %**, lo cual se presenta como resultado medido y no como cumplimiento de ese objetivo.

## Limitaciones

Los ensayos se realizaron en redes y servicios virtualizados sobre una máquina anfitriona. Las pruebas no acreditan redundancia física, SLA de producción ni algoritmos de aprendizaje automático entrenados. Las fases siguientes amplían la plataforma sin modificar retroactivamente el alcance acreditado en S01–S04.

## Documentación relacionada

[Arquitectura multisede](../arquitectura/arquitectura-multisede-implementada.md) · [Catálogo de evidencias gráficas](../../evidencias/capturas/README.md) · [Aceptación S05](s05-integracion-y-aceptacion.md).
