# NETLAB360 · Tablero vigente de la fase S05

> **Corte 14/11/2026 — lote 114A-R aprobado y 114A-S aún sin ejecutar.** Tras sincronizar `da6e7b5`, las suites `test_s05_lacp_hq_integracion` (10/10), `test_s05_lacp_hq_falla_retorno` (7/7) y `test_s05_lacp_integracion_precheck` (8/8) suman **25/25 aprobadas**. Estado HQ 2/2, ping 4/4 en intento 1, HTTP BACKEND_HQ y FIB/puertos conservados; S1/S2 precheck selectivo OK, IP candidatas aún sin asignar, gestión y Git correctos. Marcador exacto en log `29_Precheck_Failover_HQ_y_S1S2_Corregido.txt`: `========== LOTE114A_R_PRECHECK=OK ==========`. Dos intentos posteriores de 114A-S se detuvieron **antes del paso 573** porque `grep -Fxq` buscaba solo `LOTE114A_R_PRECHECK=OK` sin los signos `==========`. No se bajó ningún enlace, 114B sin ejecutar. **Reanudar directamente con 114A-S corregido**, sin repetir 114A-R; seguir 114B únicamente con dos marcadores correctos. [Runbook actualizado](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-siguientes-lacp-hq-20261114.md).

**Corte de evidencia:** 14 de noviembre de 2026, 15:18, hora de Panamá. **Alcance:** solo resultados observados en VM y salidas aportadas por el operador; los cambios de código y pruebas CI se identifican por separado. **La fase S05 no está cerrada.**

## Incidencia 114A y próximo gate (14/11)

**Corte operativo posterior (14/11/2026):** lote 114A falló **en el paso 553**, `status` por `TimeoutExpired` de ping `-c 2 -W 2` con timeout externo 10s; dos ejecuciones: primero destino S2 `10.72.20.20` y luego frontal HQ `10.70.20.23`. **14/14 tests offline OK**, switch/cliente HQ 2/2 puertos, sin evidencia de fallo LACP. Lote 114B no pasó su gate (no había `LOTE114A_PRECHECK=OK`), **NO ocurrió failover real**. Ya existe [PR #109](https://github.com/recm0708/netlab360/pull/109), CI OK y merge en `1e2d12a9184c83caf71306bede14d76e88787fff`: reintentos ICMP auditados hasta 3 veces, timeout 15s, fallo cerrado si persiste y aplicado a status/ensayo. Rehacer **solo** 114A como validación de lectura sobre el código nuevo; 114B está prohibido hasta marcador final `OK`. No ejecutar UP HQ ni reiniciar.

## Resumen verificable

| Subsistema | Completado y evidenciado | Pendiente |
| --- | --- | --- |
| Plataforma de base S02 | 3 switches Linux VLAN-aware, 3 routers FRR/OSPF, 9 VLAN, 9 hosts, 4 WAN | No reconstruir, reiniciar ni borrar para S05 |
| Redundancia WAN S05 | Conmutación de rutas S1 `s1p→s1b→s1p` y S2 `s2p→s2b→s2p`; observador FIB NOC | Conservar validación global post-SDN |
| HTTP HA real | BACKEND_HQ `10.70.20.21:8088`, BACKEND_S1 `10.71.20.21:8088`, FRONTAL_HQ `10.70.20.23:8080`; conmutación HQ→S1→HQ probada; monitor S2, 6 servicios `active`, NOC HTTP real y reloj Panamá | Completar prueba de falla de instancia/equipo con aceptación claramente delimitada; verificar evidencia binaria |
| LACP piloto P1/P1B | IEEE 802.3ad 2→1→2, ensayos 1 y 8 flujos, resultados y manifiestos locales; mediciones virtuales condicionadas por CPU | Caracterización reproducible con variación de CPU y conclusiones no extrapolables a Ethernet físico |
| LACP **HQ integrado** | `nl360-s02-sw-hq/s5bond0` + `nl360-s05-lacp-hq/bond0`; 2/2 miembros activos, `layer3+4`, VLAN120 PVID untagged, IP **`10.70.20.40/24` ocupada**, ping gateway, frontal HQ, S1 y S2, gestión/OSPF/HTTP conservados; lotes 109–110 OK | Falla 2→1→2 de HQ todavía no ejecutada; S1/S2 todavía sin bonds; validar tiempos/SSH y evidencias 46–49 |
| Diagnóstico LACP posdespliegue | Lote 111D-R OK: desde cliente LACP HQ ping 4/4; hosts base 3/3; rutas FRR HQ→S1 `s1p`, HQ→S2 `s2p`, retorno S1→HQ `s1p`; gestión y Git intactos. Lote 111D-S: `ssh.service` y socket activos; 15 GiB RAM, ~13 GiB disponibles, disco 12% ocupado, journal últimas 2h sin eventos kernel filtrados; sesión publickey válida | El precheck anterior sufrió timeout al ping a S1; **no atribuir causalidad al LACP**. SSH ha sufrido reinicios de conexión intermitentes sin causa acreditada. Repetir precheck con datos actuales y detallar resultado |
| OVS/Faucet | Línea base de VLAN/FRR/bridge Linux anterior | **No implementado S05**: dominio SDN aislado, políticas, pruebas de conectividad/falla/retorno y comparación |
| NOC | Topología interactiva, FIB primaria/respaldo, selección de HTTP HQ, fallback y restauración verificados | Representar LACP/OVS solo con telemetría real, completar revisión visual, capturas y postcheck |
| Entrega | Captura S05_45 confirmada tomada; log delimitado 46–47 técnicamente correcto; capturas previas y manifiestos locales | **Aún no acreditada importación binaria completa** de capturas S05 al repositorio; verificar originales y SHA-256 antes de cerrarla |

## Próximo trabajo agrupado en 7 bloques (no en micro-pasos)

1. **LACP HQ 2→1→2:** ejecutar suite y precheck actualizados; iniciar prueba `s05-lacp-hq-falla-retorno.py run --confirm-failover` SOLO si el precheck alcanza `OK`. El script implementa rescate systemd transitorio de 120 segundos y restauración en `finally`. Verificar ambos agregadores con dos miembros al final y HTTP/FIB/gestión; capturas S05_48–49 tras éxito.
2. **LACP S1/S2:** ejecutar en código nuevo el validador selectivo `scripts/validacion/s05-lacp-integracion-precheck.py precheck --sites S1 S2` (PR #107 CI OK) para evitar marcar como conflicto a `10.70.20.40` ya usada por HQ. Después versionar por PR implementaciones idempotentes, namespaces exclusivos y propiedad verificable; primero precheck, luego despliegues por sede y pruebas 2→1→2, ICMP/HTTP intersede, rollback de recursos S05; no tocar WAN OSPF ni trunks.
3. **HA equipos/servicios:** ensayar explícitamente indisponibilidad de instancia/servidor independiente de enlace, distinguir de HA física; preservar HTTP HQ/S1 validado.
4. **SDN OVS/Faucet:** integración acotada sin puentes sobre enlaces de producción; reglas VLAN/ACL, controlador, failover y limpieza selectiva comprobados.
5. **NOC final:** enlazar LACP/SDN/HA a observaciones frescas; `SIN DATOS` ante ausencia, revisar gráfica y formato horario de Panamá con el operador.
6. **Integración y evidencias:** suite completa, manifiestos SHA256, originales PNG/JSON/TXT, prueba de integridad y paquete reproducible; auditar checklist de cada issue antes de cerrar.
7. **Cierre de milestone S05 e informe único:** cerrar issues solamente cuando checklist y evidencias sean consistentes; actualizar el **mismo** Word/PDF maestro hasta S05, secciones Implementación, Pruebas, Análisis y Conclusiones, APA7 sin anexos dentro del informe. S06/S07/S08 posteriores siguen abiertos.

## Issues vigentes y criterio de cierre

- [#5](https://github.com/recm0708/netlab360/issues/5): issue madre de S05, se cierra **después** de aceptar dependencias y evidencia.
- [#31](https://github.com/recm0708/netlab360/issues/31): 802.3ad multisede y caracterización de flujo/CPU.
- [#32](https://github.com/recm0708/netlab360/issues/32): redundancia de servicio/instancia/equipo sin prometer HA física.
- [#23](https://github.com/recm0708/netlab360/issues/23): OVS/Faucet aislado.
- [#64](https://github.com/recm0708/netlab360/issues/64): NOC integrado y evidencias visuales.
- [#105](https://github.com/recm0708/netlab360/issues/105): nueva issue S05 de **importación de evidencias auténticas, SHA-256 y aceptación final**; abierta.
- [#24](https://github.com/recm0708/netlab360/issues/24): **cerrada (not planned)**; cuarta sede/WireGuard no requerida, no implementada.
- [#106](https://github.com/recm0708/netlab360/issues/106): nueva issue S08 para **reconstrucción reproducible de namespaces al reiniciar**; no se debe confundir con S05 completada.

## Punto de relevo para otra conversación

**Lotes próximos versionados:** [guía operativa](../operacion/s05-lotes-siguientes-lacp-hq-20261114.md). **HEAD mínimo del validador selectivo:** `89429b9763234911e2313687c033692cf025b424` (PR #107). Esta guía sustituye comandos anteriores que repetían el precheck de los tres candidatos después de desplegar HQ.

**Última auditoría de issues:** 50 issues al corte **antes de crear** #105 y #106 (por tanto ahora al menos 52). S05: seis abiertas (#5, #23, #31, #32, #64, #105), una cerrada (#24). S01–S04 milestones cerradas; S05–S08 abiertas.

## Seguridad operativa

- VM `netlab360-lab`, Ubuntu Desktop 26.04.1, `ens33=192.168.47.40/24`, default vía `192.168.47.2`. Desde Windows una sola sesión SSH con túnel local `9130`.
- **No reiniciar Ubuntu ni destruir namespaces**: actualmente hay topología S02/HA/LACP en netns efímeros; los servicios `systemd` HTTP no están habilitados al arranque hasta diseñar orquestación.
- No tocar Docker FRR, OSPF, VLAN/trunks `tr-sw`, `br0`, HA, IPAM asignado, VMware VMnet8; no usar `clear`.
- LACP HQ **ya está desplegado**; no repetir `up`, no ejecutar `down` sin identificar propiedad; mantener estado `~/netlab360-bootstrap/s05/lacp-multisede/state-hq.json`.
- No repetir P1/P1B, failover WAN ni ciclo HTTP HQ→S1→HQ salvo regresión motivada; reutilizar logs anteriores y auditar integridad.
- Informes y capturas: los PNG reales requieren entrega desde Windows/VM y manifiesto SHA-256; una salida de terminal no demuestra que PNG esté importado.

## Fuentes primarias del corte

- Logs locales (fuera del repositorio): `~/netlab360-bootstrap/s05/evidencias/lacp-integracion/14_Precheck_Despliegue_LACP_HQ.txt`, `15_Despliegue_Controlado_LACP_HQ.txt`, `17_Precheck_Failover_LACP_HQ.txt` (falló antes del marcador OK), `20_Diagnostico_LACP_Rutas_y_Comparacion.txt`, `21_Diagnostico_Estabilidad_SSH.txt`.
- Código/versionado: `scripts/laboratorio/s05-lacp-hq-integracion.py`, `scripts/laboratorio/s05-lacp-hq-falla-retorno.py`, `scripts/validacion/s05-lacp-integracion-precheck.py`, `docs/disenos/s05-lacp-integracion-multisede-candidata.md`.
- Historial completo de issues previo a la normalización: `docs/gestion/historico-issues/s05-issue-*-antes-de-consolidacion-20261114.md`; también en GitHub Events y versiones previas.
