# NETLAB360 · Auditoría de issues cerradas y abiertas

**Corte:** 14/11/2026. Datos leídos directamente de GitHub antes de modificar checklists de S05.

- Issues reales auditadas: **50** (excluye pull requests).
- Issues cerradas: **31**; abiertas: **19**.
- Issues cerradas con algún checkbox `- [ ]` sin marcar: **0**.
- Esta verificación cuenta casillas vacías; **no demuestra por sí sola la ejecución técnica**. Se respeta el estado actual de las issues cerradas y no se reabren sin un incumplimiento acreditado.
- S05: 5 issues abiertas (#5, #23, #31, #32, #64), una cerrada #24 (WireGuard/4.ª sede expresamente descartada).

## Issues cerradas auditadas

| Número | Estado | Checks terminados | Checks pendientes | Título |
|---:|---|---:|---:|---|
| [#1](https://github.com/recm0708/netlab360/issues/1) | Cerrada | 10 | 0 | [S01] Línea base y SSH seguros — CERRADA |
| [#2](https://github.com/recm0708/netlab360/issues/2) | Cerrada | 10 | 0 | [S02] Infraestructura multisede verificada y documentada — CERRADA |
| [#3](https://github.com/recm0708/netlab360/issues/3) | Cerrada | 10 | 0 | [S03] SoT candidate, Ansible FRR, OpenTofu metadata y CI — CERRADA |
| [#4](https://github.com/recm0708/netlab360/issues/4) | Cerrada | 12 | 0 | [S04] Implementación NOC/Prometheus y validaciones G0–G6 — CERRADA |
| [#9](https://github.com/recm0708/netlab360/issues/9) | Cerrada | 4 | 0 | [001] Seguimiento académico consolidado en #36 y #46–48 |
| [#10](https://github.com/recm0708/netlab360/issues/10) | Cerrada | 5 | 0 | [002] Entorno VMware/Ubuntu y recursos de VM comprobados |
| [#11](https://github.com/recm0708/netlab360/issues/11) | Cerrada | 5 | 0 | [003] IPAM y diseño multisede implementados y contrastados |
| [#12](https://github.com/recm0708/netlab360/issues/12) | Cerrada | 5 | 0 | [004] PoC observable de fallo WAN y alertas verificada |
| [#13](https://github.com/recm0708/netlab360/issues/13) | Cerrada | 7 | 0 | [005] Tres routers FRR y cuatro WAN multisede verificados |
| [#14](https://github.com/recm0708/netlab360/issues/14) | Cerrada | 6 | 0 | [006] Conmutación y restauración WAN de S1/S2 verificadas |
| [#15](https://github.com/recm0708/netlab360/issues/15) | Cerrada | 7 | 0 | [007] NOC S04 multisede y bitácora SQLite — VALIDADO |
| [#16](https://github.com/recm0708/netlab360/issues/16) | Cerrada | 7 | 0 | [008] Contrato SoT candidate S03 y propiedad de cambios — CERRADO |
| [#18](https://github.com/recm0708/netlab360/issues/18) | Cerrada | 8 | 0 | [010] Ansible FRR: compliance, drift y reconciliación real comprobados |
| [#19](https://github.com/recm0708/netlab360/issues/19) | Cerrada | 7 | 0 | [011] CI GitOps y pull requests verificados; ciclo técnico completado |
| [#20](https://github.com/recm0708/netlab360/issues/20) | Cerrada | 7 | 0 | [012] Colector y Prometheus S04: alertas, TSDB y UNKNOWN — VALIDADO |
| [#21](https://github.com/recm0708/netlab360/issues/21) | Cerrada | 8 | 0 | [013] S04 SLI y referencia experimental 99% — MEDIDOS Y DOCUMENTADOS |
| [#22](https://github.com/recm0708/netlab360/issues/22) | Cerrada | 8 | 0 | [014] Incidentes controlados S04, seguridad y rollback — VALIDADO |
| [#24](https://github.com/recm0708/netlab360/issues/24) | Cerrada | 4 | 0 | [016] WireGuard/sucursales adicionales — ampliación S05 condicionada |
| [#28](https://github.com/recm0708/netlab360/issues/28) | Cerrada | 3 | 0 | [POSENTREGA] Manual independiente no requerido — NO PLANIFICADO |
| [#30](https://github.com/recm0708/netlab360/issues/30) | Cerrada | 8 | 0 | [022] VLAN/trunk/HTTP/ACL intersedes validados en topología integrada |
| [#33](https://github.com/recm0708/netlab360/issues/33) | Cerrada | 6 | 0 | [025] CI segura y separación de pruebas locales de red |
| [#35](https://github.com/recm0708/netlab360/issues/35) | Cerrada | 8 | 0 | [027] Reorganización documental según guías docentes 1457 — completada |
| [#37](https://github.com/recm0708/netlab360/issues/37) | Cerrada | 4 | 0 | [029] Ensayo OVA opcional consolidado en #29 (fase 8) |
| [#38](https://github.com/recm0708/netlab360/issues/38) | Cerrada | 10 | 0 | [030] S01 SSH endurecido, clave ED25519 y rollback — CERRADO |
| [#39](https://github.com/recm0708/netlab360/issues/39) | Cerrada | 9 | 0 | [031] Reservar dirección IPv4 fija de NETLAB360 en VMnet8 sin colisiones |
| [#40](https://github.com/recm0708/netlab360/issues/40) | Cerrada | 11 | 0 | [032] Autenticar GitHub CLI desde Ubuntu mediante SSH y clonar repositorio |
| [#41](https://github.com/recm0708/netlab360/issues/41) | Cerrada | 17 | 0 | [033] Herramientas base y checkpoint VMware completados |
| [#42](https://github.com/recm0708/netlab360/issues/42) | Cerrada | 6 | 0 | [034] Implementar FRRouting OSPF dual-WAN con failover y recuperación |
| [#46](https://github.com/recm0708/netlab360/issues/46) | Cerrada | 4 | 0 | [ACA] Título comunicado y revisión sin observaciones registradas — CERRADO |
| [#47](https://github.com/recm0708/netlab360/issues/47) | Cerrada | 5 | 0 | [ACA 30-10] Revisión realizada; profesora conforme, continuar siguiente entregable |
| [#51](https://github.com/recm0708/netlab360/issues/51) | Cerrada | 6 | 0 | [Evidencias] Catálogo oficial S01–S03 versionado y auditado |

## Issues abiertas al corte

| Número | Milestone | Checks terminados | Checks pendientes | Título |
|---:|---|---:|---:|---|
| [#5](https://github.com/recm0708/netlab360/issues/5) | S05 | 75 | 49 | [S05] Redundancia avanzada, LACP multistream y SDN OVS/Faucet |
| [#6](https://github.com/recm0708/netlab360/issues/6) | S06 | 1 | 4 | [S06] Datos etiquetados y evaluación de diagnóstico IA |
| [#7](https://github.com/recm0708/netlab360/issues/7) | S07 | 0 | 6 | [S07] Integración AIOps y recuperación supervisada extremo a extremo |
| [#8](https://github.com/recm0708/netlab360/issues/8) | S08 | 0 | 8 | [S08] Integración final, informe único, TAR técnico y defensa |
| [#17](https://github.com/recm0708/netlab360/issues/17) | S08 | 4 | 4 | [S05+] OpenTofu: data sources y ownership externo — REPROGRAMADO |
| [#23](https://github.com/recm0708/netlab360/issues/23) | S05 | 1 | 5 | [015] SDN OVS/Faucet acotado — fase 5 pendiente |
| [#25](https://github.com/recm0708/netlab360/issues/25) | S06 | 1 | 4 | [017] Dataset etiquetado para incidentes — fase 6 pendiente |
| [#26](https://github.com/recm0708/netlab360/issues/26) | S06 | 1 | 5 | [018] Evaluación ML contra reglas — fase 6 pendiente |
| [#27](https://github.com/recm0708/netlab360/issues/27) | S08 | 7 | 4 | [019] Informe único 4.6 validado hasta S04; continuidad S05–S08 |
| [#29](https://github.com/recm0708/netlab360/issues/29) | S08 | 1 | 4 | [021] Exportación OVA/OVF condicionada a requisito confirmado — S08 |
| [#31](https://github.com/recm0708/netlab360/issues/31) | S05 | 14 | 6 | [023] LACP 802.3ad: multistream piloto medido; capacidad e integración pendientes |
| [#32](https://github.com/recm0708/netlab360/issues/32) | S05 | 48 | 43 | [024] Redundancia de equipos/servidor multisede — fase 5 pendiente |
| [#34](https://github.com/recm0708/netlab360/issues/34) | S08 | 6 | 3 | [026] Compatibilidad base validada; extensiones S05–S08 pendientes |
| [#36](https://github.com/recm0708/netlab360/issues/36) | S08 | 9 | 6 | [028] Hitos académicos: 30/10 conforme; revisión 13/11 y final pendientes |
| [#43](https://github.com/recm0708/netlab360/issues/43) | S08 | 4 | 4 | [035] Catálogo de evidencias S01–S04 validado; preparación TAR S08 pendiente |
| [#44](https://github.com/recm0708/netlab360/issues/44) | S08 | 0 | 7 | [036] PowerPoint y demostración final en vivo — fase 8 pendiente |
| [#45](https://github.com/recm0708/netlab360/issues/45) | S08 | 3 | 5 | [037] TAR técnico externo — preparación y validación final S08 |
| [#48](https://github.com/recm0708/netlab360/issues/48) | S08 | 4 | 3 | [ACA 13-11] Revisión próxima de fundamento y diseño — preparado en PDF 4.6 |
| [#64](https://github.com/recm0708/netlab360/issues/64) | S05 | 116 | 54 | [S05] Topología interactiva NOC: WAN primaria/respaldo, nodos, VLAN y tráfico verificado |

**Nota S05:** los checkboxes sin marcar de #5/#32/#64 incluyen instrucciones operativas históricas ya superadas. Se preserva su texto íntegro en `docs/gestion/historico-issues/` y se sustituye la lista de acciones vigentes por checklists concisos en la issue actual.
