# NETLAB360 — Punto único de reanudación

**Actualizado:** 27 de octubre de 2026. La siguiente actividad inmediata es **editar el capítulo 7 del informe académico**, no ejecutar laboratorios.

## Estado técnico acumulado

| Fase | Condición comprobada |
|---|---|
| S01 | Baseline experimental validada; cierre fundacional/SSH aún en seguimiento |
| S02 | Tres sedes/4 WAN/9 VLAN, OSPF 4/2/2 y HTTP/ACL, cerrada por alcance |
| S03 | SoT, Ansible FRR vivo con drift corregido, 17 metadatos OpenTofu y CI comprobados; aceptación de alcance pendiente |
| S04 | G0–G4 validados, G5 SLI medido y G6 técnico finalizado; aceptación académica/SLO aún abierta |
| S05–S08 | No ejecutadas en el alcance nuevo |

**Inventario oficial de evidencias:** S01 83, S02 9, S03 8 y S04 22: **122 PNG** con huellas y controles automatizados. [Directorio](../evidencias/capturas/README.md).

## Informe único

PDF recibido **`1457-Proyecto Semestral_borrador4.4.pdf`**, **110 páginas**. Implementación cap. 5 llega a **5.6.5**; pruebas cap. 6 llegan a **6.9.6**, Figuras 16–20, Tabla 13. Las cifras de resultados S04 coinciden con el laboratorio: G3 WAN, G4 TSDB/SQLite y G5 SLI. Pendientes: actualizar la apertura del capítulo 7 que sigue limitada a tres fases, insertar 7.10, modificar conclusiones y recomendaciones del capítulo 8, reconciliar Tabla 12 a 122 imágenes y actualizar índice/citas. Los textos se entregan por el chat para copiar/pegar en Word, sin generar un PDF nuevo.

## Seguridad y pausa operativa

VM Ubuntu `netlab360-lab`, gestión `ens33=192.168.47.40/24`, GW `192.168.47.2`, VMware VMnet8 NAT. Se comprobaron respaldos originales y TSDB SHA256, el desmontaje de LAN/WAN/FRR y servicios de observabilidad y la sincronización Git. Se ejecutó `sudo systemctl poweroff`; Ubuntu cerró la conexión SSH. **Solo falta confirmar visualmente el estado `Powered Off` en VMware Workstation**, sin reencender la máquina para redactar.

El próximo arranque, cuando se inicie S05, requiere revisión de recursos, snapshot/backup, SSH, estado limpio y dependencias antes de ejecutar cualquier componente.

## Problemas y decisiones abiertos

- Formalizar SLO académico **99 % candidato** y notificaciones visuales locales. Los datos de 60m muestran **1698/1740 = 97,586 %**, no cumplimiento del candidato; no hubo avisos externos acreditados.
- Aceptación académica S04 y resultados de revisión Teams 30/10, aún futura al corte.
- Criterios SoT `candidate` y propiedad OpenTofu S03, endurecimiento SSH S01 (sin aplicar cambios a ciegas).
- S05: plan de alta disponibilidad, OVS/Faucet y topología interactiva con semántica de rutas/fuentes; no animar tráfico sin métricas de paquetes reales.

## Documentación activa

[Estado general](00-estado-y-continuidad.md) · [Plan operativo](05-plan-operativo-y-pausas.md) · [Hitos y métricas](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [Cierre de S04](operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md) · [Guion académico](academico/s04-guion-de-actualizacion-del-informe.md) · [Issues](https://github.com/recm0708/netlab360/issues).
