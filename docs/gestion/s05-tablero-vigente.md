# NETLAB360 · Tablero vigente de la fase S05

> **Corte más reciente 14/11/2026 — LACP HQ/S1/S2 COMPLETADO:** L119A=26/26 tests y tres bonds 2/2; L119B S1 y L120 S2 **2→1→2 reales**, 4 pings/HTTP HQ/HA/FIB verificados durante el miembro único, rescates systemd cancelados; L121 **`LOTE121_LACP_MULTISEDE=OK`** con OSPF s1p/s2p, seis servicios active, red de gestión `192.168.47.40/24` GW `.2`, Git limpio; SHA-256 de 4 TXT verificado 4/4. Hubo timeout ICMP aislado recuperado al segundo intento en S1 y HQ→S2; no afirmar 0 pérdida durante transición. **No repetir las pruebas LACP ni reconstruir bonds.** Issue #31 requiere solo estadística y verificación/importación de PNG originales. S05 aún abierto por OVS/Faucet (#23), HA instancia/equipo (#32), NOC con LACP/SDN real (#64) y evidencias (#105). S06 (ML) y S07 (AIOps) todavía no ejecutados. [Plan de aceleración y lote 122 read-only](https://github.com/recm0708/netlab360/blob/main/docs/gestion/plan-aceleracion-y-cierre-practico-20261114.md). **No reiniciar VM ni Windows con VM activa** hasta terminar práctica, respaldar evidencias y demostrar recuperación de namespaces (#106). El informe único v4.6 de 113 páginas llega hasta S04; actualizarlo, no reiniciarlo desde cero.

> **Actualización de código protegida 14/11/2026:** [PR #117](https://github.com/recm0708/netlab360/pull/117) CI OK (failover 2→1→2 S1/S2, rescates systemd diferentes), [PR #118](https://github.com/recm0708/netlab360/pull/118) CI OK (respuesta NOC/FIB incompleta no provoca KeyError ni falsa aceptación), [PR #120](https://github.com/recm0708/netlab360/pull/120) CI OK (marcadores de captura 53/54 S1 y 55/56 S2 correctamente identificados). **Versión mínima antes de ejecutar lotes 119–121: ed8985dc7db4e9200f9a986c351957dd59921e52.** Scripts de fallo de sucursales preparados pero **aún no ejecutados en la VM**. Los PNG 48/49/51/52 se declararon tomados, no constan sus bytes en GitHub. [Runbook S1/S2 protegido](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-119-121-failover-lacp-s1-s2-20261114.md). No reiniciar ni volver a realizar UP HQ/S1/S2.

> **Corte operativo 14/11/2026 — 3 LACP multisede desplegados.** L117R-A comprobó inexistencia de estado/ns/puertos S2, 17 pruebas OK, precheck S2 y HQ/S1 sanos. L117R-B completó S2 VLAN320 cliente 10.72.20.40/24, 2/2 miembros en cliente y switch, ICMP 4/4, HA/FIB y gestión intactas. L118-R: primer intento de lectura NOC falló por `KeyError: 'S1'` en snapshot de FIB incompleto después de un timeout ICMP S1 recuperado en segundo intento; **el segundo 118-R completó**: HQ/S1/S2 2/2, 4/4 pings cada sede, rutas OSPF HQ→S1 por s1p y HQ→S2 por s2p, seis servicios activos, ens33=192.168.47.40/24 GW .2, Git limpio. Capturas 48/49/51/52 declaradas tomadas por usuario; aún sin importación binaria SHA-256 a repo. **NO repetir los UP HQ/S1/S2.**
>
> **Cambios CI OK:** [PR #117](https://github.com/recm0708/netlab360/pull/117), scripts de falla/retorno S1/S2 con rescue systemd independiente y evidencia 53–56; [PR #118](https://github.com/recm0708/netlab360/pull/118), lecturas NOC/FIB parciales con hasta 3 intentos y rechazo si no hay FIB principal completa. Continuación: [lotes 119–121](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-119-121-failover-lacp-s1-s2-20261114.md): tests, precheck ambas sedes, S1 2→1→2, S2 2→1→2, postcheck HQ/S1/S2 y manifiesto SHA256. Solo ejecutar 119-B tras 119-A OK y S2 tras S1 OK; si cae SSH durante run no repetir hasta auditar estado de bond.

> **Corte 14/11/2026 — LACP S1 implementado; S2 pendiente por timeout:** 115 ejecutó 7 tests OK; 116 `S05_LACP_S1_DESPLIEGUE=OK` con switch y cliente S1 2/2, VLAN220, `10.71.20.40/24`, 4/4 pings, HQ/HA/FIB/gestión intactos. 117 paso 596 precheck S2 OK (inventario de 37 IP tras incorporar S1); paso 597 abortó **antes de crear recursos S2** por `TimeoutExpired` de lectura `bridge vlan show` del switch S2 (15s). No se ejecutaron 598–600; **no presumir S2 operativa ni repetir UP sin auditar estado**. PR #115 integrada/CI OK con consulta read-only y 2 intentos de hasta 30s, falla cerrado si persiste. Ejecutar [lotes 117R-A/B y 118-R](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-117r-118r-recuperacion-s2-20261114.md): **verificar ausencia de state-s2.json, namespace y puertos antes del despliegue**. Capturas del chat: 18 PNG 32–47 y 50 revisados; 39A y 44 complementables; 48/49 no aportadas, 51/52 pendientes de S2. No reiniciar VM, no repetir HQ/S1.

> **Corte operativo 14/11/2026 — HQ LACP REAL 2→1→2 completado:** 114A-S (2 rondas a 4 destinos: **16/16 paquetes**, 0 % pérdida en esas rondas), 114B (switch/cliente 2→1→2, ping 4/4 durante enlace único, HTTP `200_BACKEND_HQ`, HA/FIB/S02/gestión conservados; watchdog systemd armado y cancelado tras restauración), 114C (salidas S05_48/49 delimitadas, PNG originales **sin confirmación de guardado**), 114D (precheck S1/S2 VLAN220/320 y nuevas IP .40, 36 direcciones auditadas, tres FRR RUNNING, HQ 2/2). **No repetir 114B ni ejecutar UP HQ.**
>
> **Código nuevo en GitHub:** [PR #113](https://github.com/recm0708/netlab360/pull/113) CI OK e integrada; dos scripts de integración S1/S2 con propiedad separada y rollback, sin haberlos ejecutado aún. [Guía lotes 115–118](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-115-118-lacp-s1-s2-20261114.md): tests/precheck, despliegue exclusivo S1, despliegue S2 tras comprobar S1 y aceptación de tres bonds. Si falla alguna sede, **no repetir UP sin diagnosticar estado**. La prueba 2→1→2 de S1/S2 permanece pendiente.

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
