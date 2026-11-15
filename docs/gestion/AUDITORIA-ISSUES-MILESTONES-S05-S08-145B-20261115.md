# NETLAB360 — Auditoría de issues y milestones S05–S08

**Corte:** 15/11/2026, tras ejecución correcta de lotes 145A y 145B en la VM. Reconciliación de **24 issues** asignadas a cuatro milestones, incluyendo tres cerradas. Sin desarrollo de S06, S07 ni S08.

## Fuentes de verdad — ejecución S05

- **145A=OK:** instalador reemplazó de forma atómica el helper root con respaldo verificado; snapshot FRR/FIB S1 por s1p y S2 por s2p, tres LACP HQ/S1/S2 2/2 en switch/cliente, Faucet conectado y 25 flujos. Gestión ens33 192.168.47.40/24 y GW 192.168.47.2, Git limpio.
- **145B=OK:** reinicio SOLO del NOC 9130; primer curl RC7 transitorio durante arranque, health posterior sano. Dos muestras API: 18 nodos/21 enlaces, HA BACKEND_HQ/PRINCIPAL, LACP 3×2/2, SDN OpenFlow conectado con 25 reglas, FIB primarias, warnings=[], 6 servicios active, hora America/Panama 10:07:17 y 10:07:21.
- **145C NO EJECUTADO:** captura PNG S05_63 y revisión visual final todavía pendientes; los PNG 60/61/62 reportados tomados no han sido auditados por bytes/hash. No cerrar issue #64 ni S05 hasta comprobarlos.
- Las indicaciones anteriores que decían que 145A/145B no se ejecutaron ya son históricas y obsoletas.

## Estado real de milestones

| Hito | Estado GitHub | Abiertas | Cerradas | Justificación |
|---|---|---:|---:|---|
| S05, número 5 | abierto | 6 | 1 | Captura NOC, HA independiente, P1/P1B, integridad PNG y aceptación pendientes |
| S06, número 6 | abierto | 3 | 0 | Solo insumos históricos y baseline de reglas; NO ML entrenado |
| S07, número 7 | abierto | 1 | 0 | NO ciclo AIOps supervisado |
| S08, número 8 | abierto | 11 | 2 | Entregables futuros; preparación de S01–S04 documentada |

Los milestones permanecen abiertos deliberadamente. El conector GitHub disponible permite auditar asignaciones y contadores de issues, pero no modificar la descripción del milestone; no se ha fingido una edición no realizada. Ninguna issue fue reasignada de fase ni cerrada indebidamente.

## Auditoría completa issue por issue

### S05: 7 issues

| Issue | Estado | Check de avances y pendiente |
|---|---|---|
| [#5](https://github.com/recm0708/netlab360/issues/5) | abierta | Núcleo WAN/HTTP/LACP/SDN/NOC 145A/B completado; cierre S05 pendiente |
| [#23](https://github.com/recm0708/netlab360/issues/23) | abierta | OVS/Faucet y aislamiento + prueba sdna0 + NOC real completados; faltan PNG/documentación/limpieza selectiva |
| [#24](https://github.com/recm0708/netlab360/issues/24) | **cerrada** | 4/4 checks de NO PLANIFICADO: WireGuard y cuarta sede descartados, no implementados |
| [#31](https://github.com/recm0708/netlab360/issues/31) | abierta | 3 LACP y fallas 2→1→2 comprobados; P1/P1B estadística e integridad aún pendientes |
| [#32](https://github.com/recm0708/netlab360/issues/32) | abierta | HA WAN/HTTP completa; falla de instancia independiente y alcance de equipo pendiente |
| [#64](https://github.com/recm0708/netlab360/issues/64) | abierta | **NOC LACP/SDN ya desplegado y API real aceptada 145B**; falta inspección visual y PNG 63 |
| [#105](https://github.com/recm0708/netlab360/issues/105) | abierta | Logs TXT disponibles; originales PNG SHA-256/acta aceptación pendientes |

### S06: 3 issues, fase NO INICIADA

| Issue | Estado | Lo ya disponible y lo que aún NO existe |
|---|---|---|
| [#6](https://github.com/recm0708/netlab360/issues/6) | abierta | Registros S04/S05 y NOC como insumos; no dataset etiquetado ni ML |
| [#25](https://github.com/recm0708/netlab360/issues/25) | abierta | Eventos históricos candidatos; etiquetado/depuración/particiones pendientes |
| [#26](https://github.com/recm0708/netlab360/issues/26) | abierta | Baseline de reglas existe; comparación con modelo entrenado pendiente |

### S07: 1 issue, fase NO INICIADA

| Issue | Estado | Reconciliación |
|---|---|---|
| [#7](https://github.com/recm0708/netlab360/issues/7) | abierta | S04/S05 constituyen insumos, NO hay ciclo AIOps aprobado ni operaciones de esta fase |

### S08: 13 issues, sin adelantar entregables

| Issue | Estado | Reconciliación |
|---|---|---|
| [#8](https://github.com/recm0708/netlab360/issues/8) | abierta | Informe/TAR/defensa y aceptación total pendientes |
| [#17](https://github.com/recm0708/netlab360/issues/17) | abierta | OpenTofu local realizado; proveedor/data sources externos opcionales reprogramados |
| [#27](https://github.com/recm0708/netlab360/issues/27) | abierta | Informe único v4.6 113 páginas S01–S04; S05 todavía NO incorporado en Word |
| [#28](https://github.com/recm0708/netlab360/issues/28) | **cerrada** | 3/3 checks: manual independiente no requerido, NO PLANIFICADO |
| [#29](https://github.com/recm0708/netlab360/issues/29) | abierta | Exigencia OVA no confirmada; no exportar de más |
| [#34](https://github.com/recm0708/netlab360/issues/34) | abierta | OVS/Faucet S05 y compatibilidad iproute2 real acreditadas; deps S06 y matriz S08 pendientes |
| [#36](https://github.com/recm0708/netlab360/issues/36) | abierta | 30/10 confirmado; dictamen de 13/11 no verificado; entrega pendiente |
| [#37](https://github.com/recm0708/netlab360/issues/37) | **cerrada** | 4/4 checks: OVA duplicada transferida a #29, NO exportada |
| [#43](https://github.com/recm0708/netlab360/issues/43) | abierta | 122 PNG de S01–S04 catalogados; S05 aún no importada |
| [#44](https://github.com/recm0708/netlab360/issues/44) | abierta | PowerPoint/defensa pendientes |
| [#45](https://github.com/recm0708/netlab360/issues/45) | abierta | TAR independiente acordado, aún no generado |
| [#48](https://github.com/recm0708/netlab360/issues/48) | abierta | Revisión del 13/11 y observaciones no confirmadas |
| [#106](https://github.com/recm0708/netlab360/issues/106) | abierta | Suspensión/reanudación VMware YA validada, reinicio guest y reconstrucción NO probados |

## Qué se actualizó y cómo continuar

- Se reescribieron checklists vigentes de #5/#23/#31/#32/#64/#105 para borrar las instrucciones duplicadas que obligaban a repetir lotes. El cuerpo anterior se respaldó en [archivos históricos](historico-issues/20261115/).
- Se depuraron #6/#7 para dejar claro que sus fuentes S05 no son resultados de esas fases. En S08 se actualizaron #27/#34/#36/#106 según evidencia real; otras issues S08 siguen correctamente pendientes y no requieren cambios engañosos.
- Las issues cerradas #24/#28/#37 fueron auditadas y se conservaron cerradas.
- **Próximo paso únicamente S05:** revisión visual NOC y captura S05_63. Luego HA de instancia #32, estadísticas P1/P1B #31, evidencias #105 y aceptación #5. No repetir WAN/LACP/SDN/HTTP failovers ni 145A/B.
