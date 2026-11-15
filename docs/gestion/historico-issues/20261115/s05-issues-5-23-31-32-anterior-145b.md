# Archivo histórico de issues S05, antes de la auditoría 145B · 15/11/2026

Respaldo íntegro de las descripciones previas, incluidas entradas cronológicas obsoletas. Las checklists vigentes están EN LAS ISSUES ACTUALES; no ejecutar comandos de este archivo histórico.



---

# ISSUE #5 · [S05] WAN/HTTP HA, LACP y SDN validados; NOC, HA de instancia y evidencias pendientes · estado open

## Continuidad 15/11/2026 — scripts 145A/145B probados en CI y fusionados

- [x] Lotes **144A/B/C** completados en VM: monitor HTTP S2 de 1.69s con ambos backends running y frontal BACKEND_HQ/PRINCIPAL, 2 muestras NOC sin advertencias y rutas FIB S1=s1p/S2=s2p; 3 GET HTTP desde S2 200 OK; helper legacy root:root 0755/FIB sin cambios.
- [x] **PR #141** fusionado (docs, commit cc6f2a67): [corte maestro operativo](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), procedimiento de backup/rollback y validación NOC LACP/SDN.
- [x] **PR #142** fusionado tras **dos workflows CI SUCCESS** (commit 50f18f30): scripts ejecutables [145A](https://github.com/recm0708/netlab360/blob/main/scripts/operacion/s05-lote-145a-instalar-observador.sh) y [145B](https://github.com/recm0708/netlab360/blob/main/scripts/operacion/s05-lote-145b-activar-noc.sh), test offline bash -n y prohibición de mutaciones de red. Incidencia previa en aserción de test estático corregida y la revisión final de CI aprobada. **NO se han ejecutado todavía en la VM.**
- [ ] **SIGUIENTE ACCIÓN REAL**: en VM `cd ~/proyectos/netlab360 && git pull --ff-only origin main`; con Git limpio y SHA del helper legacy correcto, ejecutar `bash scripts/operacion/s05-lote-145a-instalar-observador.sh` y confirmar marcador `LOTE145A_HELPER_ROOT_NOC=OK` y snapshot FRR/FIB/LACP/SDN. **Después solamente** ejecutar `bash scripts/operacion/s05-lote-145b-activar-noc.sh`, confirmar dos muestras API y marcador `LOTE145B_NOC_LACP_SDN=OK`. Los scripts tienen respaldo root y retorno ante error y registran logs TXT 14 y 15 en noc-integracion.
- [ ] Tras 145B OK, revisar dashboard en Chrome con SSH túnel 9130, cuatro tarjetas reales LACP HQ/S1/S2 + Faucet, hora Panamá, capturar S05_63. Si hay error, NO repetir sin diagnosticar hash/backup y leer log.
- [ ] S05 restante: #32 HA independiente instancia/equipo y su alcance mono-VM, #31 P1/P1B estadística, #105 auditoría PNG originales; pasar a S06/S07 cuanto antes. Informe S01–S04 existente puede ampliarse **ya**, sin esperar S07 ni reescribirse de cero.


---

## CORTE ACTUAL 15/11/2026 — 144A/B/C COMPLETADOS, desplegar NOC en 145A/B

**En VM (logs reales del usuario):**
- [x] **144A:** seis servicios active (NRestarts=0), dos muestras 4 s apartes: `ha_service.status=running` con `BACKEND_HQ/PRINCIPAL` y `available=true`; monitor S2 1.69 s fresco confirma BACKEND_HQ/S1 running y frontal HQ running, `source_warnings=[]`. FIB S1=`s1p` y S2=`s2p`. La muestra aislada offline de 143B no se reprodujo.
- [x] **144B:** desde cliente S2 VLAN320, HTTP 200 e identidad saludable de backend HQ 10.70.20.21:8088, backend S1 10.71.20.21:8088 y frontal HQ 10.70.20.23:8080 (cabeceras BACKEND_HQ/PRINCIPAL). Cuatro servicios HA active sin reinicios, ens33 y Git intactos. **No hay reparación HTTP HA pendiente por esta auditoría**; no repetir failovers.
- [x] **144C:** root helper instalado permanece en versión legacy root:root 0755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; sudoers snapshot RC0 y 3 routers/FIB intactos. NOC 9130 corre como usuario rc-aa-ec y sigue sin campos LACP/SDN: **nuevo código GitHub NO instalado todavía**. Repo limpio `70bd06c`, ens33 `192.168.47.40/24`, default GW `192.168.47.2`.
- [x] [PR #141](https://github.com/recm0708/netlab360/pull/141) fusionado en main `cc6f2a67` para acelerar: [corte maestro 144C](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), [145A instalar helper root con SHA/backup/rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145a-deploy-helper-seguro-20261115.md), [145B reiniciar SOLO NOC y validar 2 muestras API + rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md).
- [ ] **145A y 145B aún NO se ejecutaron**; no afirmar despliegue del observador nuevo. Tras 145B=OK, confirmar en navegador y tomar **S05_63_NOC_LACP_Multisede_y_Faucet_Operativos**; no repetir LACP/SDN WAN/HA antes probados ni reiniciar Ubuntu.
- [ ] Después: #32 alcance HA independiente de instancia/equipo (sin confundir con redundancia de enlace), #31 valoración P1/P1B y #105 originales PNG + SHA y cierre S05. S06 ML (#6/#25/#26) y S07 AIOps (#7) siguen pendientes. El informe largo S01–S04 ya existe y **puede ampliarse en paralelo**.


---

## Corte vigente S05 · 15/11/2026 · 143A/B/C aprobados, HTTP HA en diagnóstico

- [x] **143A COMPLETADO:** Git local main 1fba8c5, 21/21 pruebas del parser, 14/14 topología, 14/14 layout, 6/6 HA/UI = **55/55**. Helper autorizado INSTALADO sigue LEGACY root:root 755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`. ens33 .40/24 gateway .2 y Git limpio.
- [x] **143B COMPLETADO:** 6/6 bonds HQ/S1/S2 switch y cliente, `ip JSON ad_num_ports=None` en los seis y `/proc/net/bonding Number of ports:2` en todos, alias y 802.3ad correctos. OVS propietario S05, Faucet running, OpenFlow connected, 25 reglas. FIB S1=s1p, S2=s2p. API en ejecución aún sin LACP/SDN (NO desplegada).
- [x] **143C COMPLETADO:** cuatro tarjetas HTML fuera del SVG, `node --check` OK, NOC/exporter active, gestión y Git intactos.
- [ ] **Anomalía por investigar, NO declarar HA correcto:** 143B capturó fuente HTTP de S2 válida `available=true`, `ha_service.status=offline`, backend/path `None`, timestamp 2026-11-15T12:39:45+00:00; `source_warnings=[]`. No implica necesariamente caída de los tres servicios. Diagnosticar monitor y endpoints HTTP desde cliente S2 antes de cualquier rollout.
- [x] [PR #140](https://github.com/recm0708/netlab360/pull/140) fusionada en main (commit `70bd06cc`): [corte maestro actual](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-143C-20261115.md) y [lotes 144A/B/C SOLO LECTURA](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-144a-144c-diagnostico-http-ha-pre-noc-20261115.md). Los marcadores `COMPLETADO` de 144 representan diagnósticos, no aceptación HA.
- [ ] **Próximas ejecuciones (NO hechas todavía):** 144A dos muestras de NOC y observación S2, 144B tres GET HTTP desde netns S2 y journal, 144C hash/helper legacy y FIB. No sobrescribir logs históricos 08/09/10, no instalar binario root, no reiniciar NOC ni guest. Tras revisar resultados, definir instalación atómica root:root con backup/rollback y validación UI/FIB/LACP/SDN.


---

## CORTE VIGENTE 15/11/2026 — incidencia 142B y continuación segura

**Estado de ejecución (verificado por el TXT del usuario):** 142A **APROBADO**, 49/49 pruebas (15 nuevas + 14 topología + 14 layout + 6 HA/UI), `LOTE142A_CODIGO_Y_BASELINE=OK`, main de VM sincronizado hasta `eef8946`, Git limpio, `ens33=192.168.47.40/24`, GW `192.168.47.2`. El ejecutable autorizado `/usr/local/libexec/netlab360-observer` **sigue en versión LEGACY** root:root 0755 SHA-256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; el código NUEVO del NOC está en GitHub pero **NO desplegado en la VM**.

**142B ABORTÓ DOS VECES** en paso 826, primer `HQ_SW`: alias correcto `S05_HQ_a14ac59efb1e996a`, modo 802.3ad y flags UP/LOWER_UP; `ip -n ... -j -d link` devolvió `ad_num_ports=None`, lo que produjo `AssertionError` en el verificador, antes de validar los otros cinco bonds y OVS. El TXT histórico `~/netlab360-bootstrap/s05/evidencias/noc-integracion/06_Precheck_Raw_Bonds_OVS_Observador.txt` documenta la segunda ejecución fallida. **No existe marcador 142B=OK** y **142C NO se ejecutó**. Esto **no demuestra falla del bond**: el auditor anterior de `ip -d` mostró 2 miembros y el validador probado usa `/proc/net/bonding`.

**Corrección [PR #139 fusionada en main](https://github.com/recm0708/netlab360/pull/139), CI SUCCESS, commit 1fba8c5f75c2fae57ba7268aebdeaf8616312af5:** observador de lectura solo acepta seis pares namespace/dispositivo fijos, verifica propietario/modo 802.3ad mediante JSON y, si `ad_num_ports` está ausente, consulta `/proc/net/bonding` exigiendo `Number of ports` único (0–2); faltantes/inconsistencias se expresan UNKNOWN, nunca se fabrican dos puertos. Incluye 6 tests nuevos. La corrección GitHub no se ha instalado ni validado aún en la VM.

**Retomar directamente:** [CORTE MAESTRO](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-142B-20261115.md) y [lotes 143A/143B/143C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-143a-143c-reparacion-parser-y-continuidad-20261115.md). Ejecutar 143A tests/legacy hash, 143B seis bonds JSON+/proc y OVS/FIB/HTTP, 143C UI/JS/hashes; conservar todos los TXT históricos. No repetir 142A ni 142B ORIGINAL. **NO instalar helper root, reiniciar NOC, reiniciar guest ni modificar ens33/FRR/OVS/LACP/Faucet hasta gates OK.** S05 y esta issue continúan abiertas; HA instancia #32, evidencia PNG #105 y S06/S07 pendientes.

---

## Estado vigente · 14/11/2026 · **ABIERTA**
S05 tiene WAN, HTTP HA, NOC básico, LACP HQ/S1/S2 con tres pruebas 2→1→2 y SDN Faucet/OVS aislado funcional. **Aún faltan** resiliencia SDN, HA de instancia/equipo, NOC alimentado con LACP/SDN, caracterización/evidencias y aceptación final. **No confundir `main` actualizado o tests CI con aceptación del laboratorio.**

### Acreditado
- [x] Base multisede reutilizada: 3 routers FRR, 3 switches, 9 VLAN, 4 circuitos WAN, OSPF y selección FIB observada.
- [x] Failover WAN principal→respaldo→principal para S1 y S2 con observación NOC; gestión host intacta.
- [x] HTTP HA real con BACKEND_HQ, BACKEND_S1 y FRONTAL_HQ; prueba HQ→S1→HQ y monitor de servicio S2, seis unidades activas.
- [x] Piloto LACP P1/P1B (802.3ad, 1/8 flujos, 2→1→2 aislado) documentado con límites de virtualización/CPU.
- [x] LACP integrado por primera vez al switch HQ S02 en VLAN 120, 2/2 miembros switch y cliente, IP `10.70.20.40`, ping intersede y servicios preservados (lotes 109–110).
- [x] Diagnóstico 111D-R/S aportado: 4 pings desde cliente LACP HQ y 3 desde clientes S02 correctos, tres rutas FRR verificadas; SSH activo, sin causa de resets identificada.
- [x] Copia íntegra del historial de S05 y auditoría de issues almacenadas en GitHub.

### Pendiente para cerrar la fase (dependencias)
- [ ] [#31](https://github.com/recm0708/netlab360/issues/31): 3 bonds y las tres pruebas 2→1→2 acreditadas; pendientes caracterización P1/P1B e importación/verificación de evidencia original.
- [ ] [#32](https://github.com/recm0708/netlab360/issues/32): aceptación de redundancia de instancia/servidor/equipo sin atribuir tolerancia a falla física.
- [ ] [#23](https://github.com/recm0708/netlab360/issues/23): OVS/Faucet funcional y aislado, políticas, fallo/retorno, comparación técnica.
- [ ] [#64](https://github.com/recm0708/netlab360/issues/64): estado NOC de LACP y SDN con observación real, revisión final de UI.
- [ ] [#105](https://github.com/recm0708/netlab360/issues/105): capturas PNG y datos originales, manifiestos SHA-256, regresión integral y aceptación.
- [ ] Reconciliar las cinco issues dependientes contra sus marcadores `OK` y pruebas; cerrar primero dependencias, luego esta issue madre.
- [ ] Cerrar milestone S05 cuando sus issues estén resueltas y actualizar **el mismo** informe académico maestro [#27](https://github.com/recm0708/netlab360/issues/27) con resultados reales de S05 (sin inventar los de S06–S08).

### No hacer / referencias
No repetir `up` HQ/HA, P1/P1B, ni reiniciar Ubuntu. `ens33=192.168.47.40/24`, gateway `.2`, no tocar OSPF, WAN ni troncales. El reinicio reproducible se gestionará por [#106](https://github.com/recm0708/netlab360/issues/106) en S08, no como capacidad ya implementada.

Consultar [tablero S05 vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md), [auditoría de 50 issues](https://github.com/recm0708/netlab360/blob/main/docs/gestion/auditoria-issues-20261114.md) y [histórico íntegro de esta issue](https://github.com/recm0708/netlab360/blob/main/docs/gestion/historico-issues/s05-issue-5-antes-de-consolidacion-20261114.md). Checklist vigente sustituye notas históricas ya archivadas.
## Corte 14/11/2026 — Lote 114A interrumpido; corrección PR #109
- [x] Git sincronizado a `e4521d1`; 6/6 tests de falla-retorno y 8/8 de precheck selectivo OK (**14/14**), sin alteraciones en red.
- [x] Estado HQ: los bonds `s5bond0` y `bond0` reportaron **2 miembros activos**, incluso cuando ping excedió el timeout de 10 s. En dos intentos la excepción afectó destinos diferentes (`10.72.20.20` y `10.70.20.23`); otros destinos habían pasado. Diagnóstico 111D-R previo logró 4/4 desde LACP HQ y 3/3 desde hosts S02.
- [x] Lote 114B pegado una vez pero **no ejecutado**: su compuerta `grep LOTE114A_PRECHECK=OK` terminó sin marcador. Sin falla controlada, sin cambios.
- [x] PR [#109](https://github.com/recm0708/netlab360/pull/109) integrada tras CI: `ping_verified` registra TIMEOUT_PROCESO/ERROR_ICMP, hasta 3 intentos de 2 pings con timeout externo 15 s; **falla cerrado** si todos fallan. Aplica a `status` y a ensayo 2→1→2. No convierte pérdidas en éxito artificial.

## 14/11/2026 · Lote 114A-R aprobado, gate de 114A-S corregido (PR #112)

- [x] Operador sincronizó a `da6e7b5` y completó **25/25 tests** (10 integración HQ, 7 failover HQ offline, 8 precheck S1/S2). Agregadores 2/2; ping 4/4 primer intento tanto en `status` como `precheck`, HTTP `200_BACKEND_HQ`, S1/S2 `.40` no asignadas, 36 IP inventariadas, servicios HA/FIB y VLAN preservados, `ens33=.40/24` GW `.2`, Git limpio; marcador `========== LOTE114A_R_PRECHECK=OK ==========`.
- [x] **114A-S NO ejecutado todavía**: dos intentos se detuvieron sin imprimir paso 573 porque `grep -Fxq` buscaba el marcador sin separadores `==========`. No implicó cambios en bond/FRR/red y 114B sigue sin ejecutar.
- [x] [PR #112](https://github.com/recm0708/netlab360/pull/112) integrada tras CI OK: gates de 114A-S, 114B, 114C ahora usan el texto exacto completo; tres tests automáticos de regresión; continuidad en `docs/REANUDAR-AQUI.md` y tablero S05.

## 14/11/2026 · Lotes 114A-S, 114B, 114C y 114D completados realmente

- [x] **114A-S:** Git a `832b6e1`; dos rondas a gateway HQ `10.70.20.1`, frontal HQ `10.70.20.23`, backend S1 `10.71.20.21` y host S2 `10.72.20.20`: **16/16 paquetes recibidos, 0% pérdida en esas rondas**. Bonds switch/cliente IEEE 802.3ad 2/2; `ens33=.40` GW `.2`, Git limpio. `LOTE114A_S_ESTABILIDAD=OK`.
- [x] **114B:** falla controlada de miembro `s5c1` con watchdog `systemd-run` temporal; switch y cliente pasaron **2/2→1/1→2/2**. Durante 1/1 ping 4/4 destinos y HTTP real `200_BACKEND_HQ`; HA/FIB y puertos S02 conservados. Tras restauración 4/4 ping, VLAN120 PVID untagged, gestión intacta y rescate cancelado. `S05_LACP_HQ_PRUEBA=OK_2_1_2`, `LOTE114B_FALLA_RETORNO=OK`. Esto no demuestra 0 pérdidas durante cada milisegundo de conmutación.
- [x] **114C:** secciones de salida `INICIO_CAPTURA_S05_48/49` a `FIN_CAPTURA` extraídas y revisadas; **no consta confirmación de archivos PNG guardados**, ni importación binaria.
- [x] **114D:** validador selectivo S1/S2 `plan` + `precheck` = OK; candidatas `10.71.20.40` VLAN220 y `10.72.20.40` VLAN320 no asignadas en inventario de 36 direcciones ni responden ICMP desde host VLAN; 3 FRR running, interfaces/VLAN protegidas, NOC/HTTP HA OK; HQ conserva 2/2. `LOTE114D_S1S2_PRECHECK=OK`. La ausencia de respuesta ICMP **no garantiza** globalmente IP libre.

Evidencia local: `~/netlab360-bootstrap/s05/evidencias/lacp-integracion/30_Estabilidad_PreFailover_HQ.txt`, `25_Falla_Retorno_HQ_2_1_2.txt`, `31_Preparacion_LACP_S1_S2.txt`.
## Código para LACP S1/S2 preparado (14/11/2026; NO ejecutado)

- [x] [PR #113](https://github.com/recm0708/netlab360/pull/113) integrada con CI OK: `s05-lacp-s1-integracion.py` VLAN220 IP `10.71.20.40`; `s05-lacp-s2-integracion.py` VLAN320 IP `10.72.20.40`; estados independientes, validación de IPAM por sede, propietario de puertos, VLAN/baseline protegidos, rollback selectivo y confirmación explícita para UP/DOWN. Pruebas automáticas de contrato incluidas.
- [x] [PR #114](https://github.com/recm0708/netlab360/pull/114) integrada: punto de reanudación actualizado y runbook de lotes 115–118 con gates y capturas S05_50/51/52. Aún no se han ejecutado los despliegues en VM.

## Corte 14/11/2026 · Lotes 115–117 y evidencias revisadas

- [x] **Lote 115:** CI y 7 tests locales de contratos S1/S2 OK; precheck S1/S2/HQ, gestión `ens33=192.168.47.40/24`, gateway `.2` y Git intactos.
- [x] **Lote 116:** **LACP S1 desplegado realmente** en VLAN220 y `10.71.20.40/24`, switch `nl360-s02-sw-s1/s5bond0` y cliente `nl360-s05-lacp-s1/bond0` en 802.3ad **2/2 miembros**; pings 4/4 (S1 GW, HQ frontal, S1 backend, S2 host), `S05_LACP_S1_SERVICIOS_HA_FIB=OK`, S02 protegido, HQ 2/2, VLAN220 PVID untagged y gestión intactos. `LOTE116_LACP_S1=OK`. PNG de captura **S05_50 recibido y visualmente validado**, no importado aún al repo.
- [x] **Lote 117 paso 596:** precheck S2 OK; inventario aumentó de 36→**37 IPv4** tras agregar S1. IP `10.72.20.40` propuesta sin asignación observada, VLAN320 sin conflictos y servicios HA/NOC correctos.
- [x] **Lote 117 paso 597 falló antes de crear nuevos recursos S2**: `TimeoutExpired` a 15s en `sudo ip netns exec nl360-s02-sw-s2 bridge vlan show`, durante **precheck** de `up`; no apareció `S05_LACP_S2_DESPLIEGUE=OK`, y 598–600 no corrieron. **No asumir S2 instalada** ni repetir UP sin comprobar state e interfaces.
- [x] [PR #115](https://github.com/recm0708/netlab360/pull/115) integrada tras CI OK, commit `2424d87bbd2806d9060c3fb56117e7d8515d2e03`: consulta `bridge vlan show` ahora solo lectura con **2 intentos hasta 30s**, cuenta timeout y falla cerrado si continúa.

## Corte 14/11/2026 — LACP de las tres sedes ya implementado

- [x] L117R-A/B y L118-R final completado: HQ/S1/S2 con IEEE 802.3ad 2/2, VLAN120/220/320, 4/4 pings por sede, OSPF s1p/s2p, seis servicios HA/NOC activos, gestión intacta; primera L118-R abortó KeyError S1 por lectura NOC incompleta, segunda terminó OK.
- [x] Los scripts de falla controlada de S1/S2 están versionados y pasaron CI (PR #117), con corrección de NOC/FIB incompleta (PR #118). Aún NO se ha ejecutado la prueba real de falla en S1/S2.
- [x] Usuario confirma nuevas capturas guardadas, sin prueba todavía de importación binaria al repo.
- [x] Lotes 119–121: S1/S2 2→1→2 y aceptación de tres sedes terminadas; logs 41/42/43/45 y manifiesto SHA-256 verificados. La evidencia PNG aún no tiene hash/importación confirmada.
- [ ] Enfocar la ruta crítica en OVS/Faucet aislado (#23), redundancia de instancia/equipo (#32), telemetría real NOC (#64), aceptación de evidencias (#105).


**Mantenimiento checklist (14/11/2026):** Se retiraron las instrucciones operativas de lotes 114/115–118 ya superados, preservadas en GitHub y documentos de reanudación. Las casillas abiertas restantes se refieren a trabajo aún no completado; no declarar fase S05 cerrada.

## Corte del lote 122 y preparación SDN (14/11/2026)

- [x] Lote **122** comprobado en segundo intento: el primero perdió SSH y se detuvo sin modificar estado; segundo acabó `LOTE122_AUDITORIA_PRE_SDN=OK`. VM Ubuntu con ~13 GiB RAM, ~132 GiB disco libres, **18 namespaces** S02/HA/LACP, 3 routers FRR Docker, 6 servicios S04/S05 activos, ens33 `192.168.47.40/24` GW `.2`, Git limpio. HQ/S1/S2 bonds 2/2, ping 4/4 y HA/FIB OK.
- [x] OVS y Faucet **no estaban instalados ni cacheados**; el chequeo mostró `ovs-vsctl`, `ovs-ofctl`, `faucet` ausentes y cero imágenes/servicios SDN. Esto es un hallazgo, **no un despliegue exitoso**.
- [x] [PR #123](https://github.com/recm0708/netlab360/pull/123) fusionada tras CI OK: `config/s05/sdn/faucet.yaml` versionado para datapath `br-s05-sdn` DP ID `0x505`, VLAN410 dos clientes A/B y VLAN420 C aislado, sin routers ni puertos de S02; 4 pruebas offline, y [lotes 123–127](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-123-127-preparacion-ovs-faucet-20261114.md) con gates para simulación APT, OVS sin bridges, Faucet Docker con digest y validación `check_faucet_config` aislada.
- [ ] **Próximo trabajo en VM:** ejecutar lotes 123–127 por orden; si instalación APT provoca cambio inesperado, detener. Estos pasos **NO crean dominio OVS ni arrancan Faucet**, por lo que aún no se declara SDN funcional.
- [ ] Después preparar implementación real de puentes veth/OVS, observar OpenFlow, validar aislamiento, permitir A↔B y denegar A↔C, falla/retorno y recuperación de recursos propios, sin interferir WAN/FRR/gestión.

## Corte 14/11/2026 · Lotes 123–127 reales completados y script SDN seguro versionado

- [x] **123:** auditó recursos y confirmó que no había colisión de br-s05-sdn, puertos sdna0/sdnb0/sdnc0, namespaces propios, puerto TCP 16653 ni contenedor Faucet; gestión ens33 .40/24 y FRR conservados.
- [x] **124:** apt update y simulación instalaron conceptualmente 5 paquetes nuevos, **0 actualizados y 0 eliminados**; OVS disponible 3.7.1-2.
- [x] **125:** paquete `openvswitch-switch=3.7.1-2` y common instalados realmente; ovs-vsctl responde `ovs_version=3.7.1`, **0 bridges** y 3 routers FRR en ejecución.
- [x] **126:** descargada imagen Faucet Docker por digest `sha256:34c5d8c1ce207de37abc7e4d9b1b60e020d43524d85e80449c637a7867e5ea32` (amd64); sin contenedor en ejecución.
- [x] **127:** 4/4 tests Python de configuración OK, `check_faucet_config=OK` en contenedor `--network none`, YAML del repo y operativo SHA256 idéntico `5945365af2f7341f02d95e2996e3e42ec585e7c32778a839632b4e1ec7480c5e`. Git limpio, ens33 .40/24, gateway .2. Marcador `LOTE127_SDN_CONFIG_VALIDADA_SIN_DESPLIEGUE=OK`.
- [x] **PR #124** fusionada tras CI OK: script [s05-sdn-ovs-faucet-aislado.py](https://github.com/recm0708/netlab360/blob/main/scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py) con guardas de estado exclusivo/ownership, Faucet publicado solo en 127.0.0.1:16653, OpenFlow13 secure, 3 namespaces sin interfaces S02 y verificaciones A↔B permitida/A↔C bloqueada; pruebas offline + [runbook 128–131](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-128-131-ovs-faucet-real-20261114.md). **El despliegue real aún NO se ejecutó en la VM**.
- [ ] Ejecutar 128 (precheck/suites), 129 (UP única vez solo si 128 OK), 130 (controlador OpenFlow y capturas 58–60), 131 (regresión S02/HA/LACP y hashes). **No repetir UP si falla o se corta SSH**: usar acción inspect sobre state-sdn.json.
- [ ] Tras SDN operativo, ensayar caída/retorno aislada de puerto/controlador con recuperación; integrar NOC y evidencias SHA256, sin cerrar issue prematuramente.

## Incidencia real S05 · Lote 129 parcial (14/11/2026, sin recuperación aún)

- [x] Lote 128 repetido satisfactoriamente: **16/16 tests offline** (4 configuración Faucet y 12 contratos OVS), YAML repo/operativo SHA256 igual, OVS 3.7.1 sin bridges y gestión `192.168.47.40/24` vía `.2` conservada; `LOTE128_SDN_PRECHECK=OK`.
- [x] Lote 129 **NO completado**: `up` pasó precheck, escribió `state-sdn.json`, creó `nl360-s05-faucet`, bridge `br-s05-sdn`, tres namespaces A/B/C y los puertos OF 1/2/3. Apuntó OVS a `tcp:127.0.0.1:16653`, pero falló con `RuntimeError: Faucet/OVS no establecieron canal OpenFlow` tras 15 consultas. El script dejó estado `needs_inspection` (según código; confirmar en la VM) y luego SSH se desconectó.
- [x] El usuario reintentó `up` una vez y este **lo bloqueó correctamente** con `Ya existe estado SDN; NO repetir up`; no se confirmaron cambios de ese segundo intento.
- [ ] **Paso inmediato:** diagnóstico **solo lectura** del archivo de estado, container exit/status/logs, publicación 16653→6653, `Controller is_connected/status.last_error`, puertos OVS, namespaces y estabilidad de gestión/S02/FRR/HA. No ejecutar up/down, docker rm/restart, ovs del-br ni reiniciar hasta identificar causa.
- [ ] Con diagnóstico real, diseñar reparación **selectiva** del despliegue con ownership y prueba de recuperación, sin eliminar el estado ni rehacer recursos; después validar conexión OpenFlow, política A↔B y aislamiento de C y tomar PNG 58–60.

## Diagnóstico definitivo 15/11/2026 — Faucet Errno 13 y recuperación preparada

- [x] **132A**: estado existente `needs_inspection`, propietario `NETLAB360_S05_SDN_V1`, bridge `br-s05-sdn` y los tres netns/puertos OF1/2/3 comprobados. Faucet contenedor `Exited(255)`, TCP `127.0.0.1:16653` no escucha, OVS `is_connected=false` y `last_error=Connection refused`. Gestión `ens33=.40/24` y default GW `.2` conservadas.
- [x] **132B**: Docker logs acreditan `Starting with UID=0 GID=0` y `[Errno 13] Permission denied: '/var/log/faucet/faucet.log'`. El contenedor no consiguió abrir el bind de logs y terminó antes de escuchar OpenFlow. Tres FRR activos, seis servicios HA/NOC `active`, VLAN y puertos propios intactos. El fallo `.:` por comando accidental de shell no corresponde a infraestructura.
- [x] [PR #127](https://github.com/recm0708/netlab360/pull/127) fusionada (CI OK, commit `90cedb3`): script `s05-sdn-recuperar-faucet-logs.py` con precheck de propiedad, digest, mounts, Docker 16653→6653, causante Errno13, namespaces/OFPORT y baseline; recuperación selectiva de permisos en directorio logs a UID0, modo0750 y `docker start` del **mismo contenedor**. Status SDN parcial solo se acepta en modo recuperación y jamás declara `active` sin conexión OpenFlow, flujos, pruebas A↔B, aislamiento C y preservación S02; 8 pruebas nuevas de fallo cerrado.
- [ ] **Ejecutar y validar** [lotes 133A–133D](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-133a-133d-recuperacion-faucet-20261115.md) para precheck, recuperación, capturas reales 58/59/60, regresión global y hash de TXT. **AÚN NO ejecutados** en la VM. No repetir UP, no ejecutar DOWN, no reiniciar Ubuntu/Windows.

## Corte 15/11/2026 · SDN Faucet operativo, falta evidencia 60 y cierre de regresión

- [x] **133A**: 20/20 tests offline OK (8 recuperación + 12 SDN), state previo `needs_inspection`, mounts/propietario/Docker/Errno13 verificados. Primer intento de sincronización sufrió reset SSH sin demostrar regresión.
- [x] **133B**: recuperación selectiva en sitio exitosa; permisos del directorio de logs ajustados y **mismo contenedor Faucet iniciado**, OpenFlow connected al intento 9, 25 reglas, cuatro pings/aislamientos correctos, baseline S02/FRR/gestión intacto; state a `active`, `LOTE133B_RECOVERY=OK`.
- [x] **133C pasos 716–718**: OpenFlow connected y `31` reglas, capturas **S05_58 y S05_59** con resultados válidos, A↔B 2/2 y 2/2 (0% pérdida).
- [ ] **133C paso 719**: A→C devolvió 2 transmitidos/0 recibidos/100% pérdida, pero wrapper externo `timeout -k 2s 10s` marcó **RC124** y abortó el lote (se exigía RC1 del ping). No se ejecutó C→A ni se imprimió FIN_CAPTURA_60 o LOTE133C_OK. No inferir que SDN falló por este RC124.
- [ ] **133D**: NO se ejecutó. El paste en terminal contenía secuencias `[200~` y delimitador `BASH~`, produjo heredoc abierto/errores de sintaxis, cancelado por Ctrl+C. No existe auditoría completa ni manifiesto SHA de 133D.
- [x] [PR #129](https://github.com/recm0708/netlab360/pull/129) propuesta: verificador solo consulta de captura 60 con ping RC1/0 recibidos/100% pérdida, control positivo A→B RC0/2/2, sin timeout externo de 10 s, tests de rechazo RC124 y RC2 y [lotes 134A–134C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-134a-134c-evidencia60-y-regresion-20261115.md) para cerrar evidencia/regresión. **No se han ejecutado lotes 134.**
- [ ] Confirmar captura 60 guardada y PNG SHA256 más adelante. **No repetir 133A/133B ni ejecutar up/down**, mantener Firewall/FRR/LACP/NOC y gestión intactos.

## Corte del 15/11/2026 — suspensión VMware solicitada y fallo de formato ICMP en 134B

- [x] **134A** completado: 10/10 tests offline; `S05_SDN_FAUCET_OPENFLOW=CONNECTED`, 25 reglas, pings A/B y aislamiento C correctos, gestión `ens33=192.168.47.40/24` GW `.2`, repo limpio.
- [x] **134B diagnosticado**, NO completado: estado SDN active, 31 reglas OpenFlow; ping negativo A→C regresó RC1 y `10 packets transmitted, 0 received, +10 errors, 100% packet loss`. El parser solo aceptaba `received, 100%` sin `+10 errors` y 2 enviados; abortó sin FIN_CAPTURA ni marcador OK. Reintento sufrió caída SSH; otro reprodujo lo mismo. **Captura S05_60 pendiente** y 134C no iniciado.
- [x] [PR #131](https://github.com/recm0708/netlab360/pull/131) CI OK y fusionada (commit `d49ff77b`): corregir parsing de salidas iputils con `+N errors` y múltiples transmisiones negativas de ARP, manteniendo RC1+0 recibidos+100% pérdida como gate, rechazando RC124/RC2/timeout, conservando exigencia 2/2 RC0 en A→B. Tests reproducen el caso real.
- [ ] **Pausa operativa antes de más pruebas:** usuario desea reiniciar Windows. Verificar espacio de volumen anfitrión vs RAM guest, baseline en TXT, sincronizar disco y **suspender completamente `netlab360-lab` en VMware Workstation** antes de reiniciar Windows. La suspensión aún **no está confirmada**, ni la reanudación. No reiniciar guest Ubuntu; los netns efímeros requieren estado de RAM conservado. No borrar .vmss/.vmem/.lck, no snapshots permanentes.
- [ ] Tras reanudar, verificar fecha, ens33/route, Faucet/OpenFlow, contenedor/3 namespaces, FRR/LACP/HA/NOC. Entonces repetir **solo** captura 60 con el parser corregido, usando un TXT nuevo que preserve el histórico fallido; completar regresión global y SHA256, y auditar PNG.

## Corte 15/11/2026 — VMware reanudada; LACP status detectó falso drift de tabla completa

- [x] VMware Workstation restauró el estado suspendido de Ubuntu tras reinicio Windows: NTP sincronizado, `ens33=192.168.47.40/24`, default GW `.2`, 21 namespaces y cuatro contenedores (FRR x3 y Faucet) activos.
- [x] SDN state active, OpenFlow connected con 28 reglas, VLAN410 A↔B comunicada y VLAN420 C aislado, baseline S02/FRR/gestión conservado.
- [ ] **LACP de HQ**: bonds 2/2 y cuatro pings OK, pero `status` lanzó `Red de gestión cambió respecto del precheck` al comparar texto literal de TODA la tabla de rutas. La diferencia exacta frente al state-hq.json aún requiere auditoría; S1/S2 y seis servicios no llegaron a validarse en esa ejecución. `NETLAB360_REANUDACION=OK` no apareció.
- [x] [PR #132](https://github.com/recm0708/netlab360/pull/132) CI OK fusionada (`78a03738`): HQ/S1/S2 comprueban ens33 IPv4 y rutas propias/defaults protegidas, no exigen rutas ajenas idénticas; no cambia JSON de state ni configuraciones. Seis pruebas de regresión rechazan drift real.
- [x] [PR #133](https://github.com/recm0708/netlab360/pull/133) fusionada: [lotes 135A/B/C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-135a-135c-reanudacion-y-captura60-20261115.md), sin acciones mutantes.
- [ ] Ejecutar 135A auditoría baseline actual, 135B revalidación completa HQ/S1/S2/SDN/HA/NOC, 135C evidencia 60 con parser ICMP corregido (PR #131). Logs históricos parciales 10/14/19 se preservan; PNG 60 sigue pendiente.

## Corte verificado 15/11/2026 — 135A/B/C completos, S05_60 obtenida; siguientes 136–138

- [x] **135A**: 23/23 tests aprobados (6 gestión+10 HQ+7 sucursales). La diferencia exacta de gestión es `docker0 172.17.0.0/16`: la ruta antigua tenía `linkdown` y la actual no; IPv4 `ens33=192.168.47.40/24` y ruta predeterminada `.2` iguales, las 3 sedes pasaron protección crítica.
- [x] **135B**: LACP HQ/S1/S2 2/2 en ambos extremos, 4 pings por sitio OK, HA/FIB/VLAN conservados; Faucet OpenFlow conectado 28 reglas, segmentación A/B-C correcta; rutas OSPF HQ→S1 por s1p, HQ→S2 por s2p, seis servicios activos, NTP, Git limpio. `LOTE135B_VMWARE_REANUDACION_COMPLETA=OK`.
- [x] **135C**: 13/13 tests de parser, OpenFlow 31 reglas; A→B `RC0 2/2`, A→C y C→A `RC1, 0 recibidos, 100% pérdida` (10 transmisiones por ARP). `S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO`, `LOTE135C_EVIDENCIA60=OK`. El operador **confirma haber guardado S05_60**; la existencia y SHA-256 del PNG original no se han auditado.
- [x] [PR #134](https://github.com/recm0708/netlab360/pull/134) fusionada (CI success, commit `9925ce62`): script S05 de pérdida/restauración **solo de sdna0** con precheck de ownership, timer restore-only systemd de 120s y pruebas ICMP/OpenFlow/servicios sin tocar ens33/FRR/LACP. [PR #135](https://github.com/recm0708/netlab360/pull/135) fusionada: punto de reanudación actualizado.
- [ ] **Próximas ejecuciones, aún NO realizadas en la VM:** [lotes 136, 137A, 137B y 138](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-136-138-aceptacion-y-falla-sdn-20261115.md): hashes TXT estáticos, precheck, falla/retorno protegida puerto A y regresión. Capturas S05_61 y S05_62 pendientes. No repetir 135 ni fault LACP. La resiliencia de puerto SDN no es HA física/instancia.

## Corte real 15/11/2026 — resiliencia de enlace SDN aceptada (lotes 136–138)

- [x] **Lote 136**: Faucet sigue conectado, 25 reglas OpenFlow, A↔B permitido y C aislado, ens33 `.40/24` GW `.2`, Git limpio. Se verificaron **7/7 registros TXT** por SHA-256 (incluidos 135A/B/C y recuperación anterior). `LOTE136_SDN_ESTABLE_Y_CAPTURA60=OK`.
- [x] **137A**: 9/9 tests de seguridad OK; precheck de ownership/puerto SDN A, OpenFlow conectado, 31 reglas, servicios S02/FRR/NOC/HA preservados; `LOTE137A_PRECHECK_FALLA_SDN=OK`.
- [x] **137B**: watchdog `nl360-s05-sdn-port-a-rescate-68997ee0a7.timer` armado; **solo `sdna0` DOWN**. Ping A→B mostró `10 transmitidos, 0 recibidos, 100% pérdida, RC1`, controlador Faucet siguió conectado; preservación de FRR, NOC, HA comprobada. Restauración `sdna0` solicitada; A↔B volvió en **intento 1**, A↔C/C↔A permanecieron aislados, OpenFlow 31 reglas; watchdog cancelado tras validación, `S05_SDN_FALLA_RETORNO=OK_DOWN_UP_ENLACE_A`. Operador confirma capturas **S05_61 y S05_62** tomadas, pendiente auditoría bytes PNG.
- [x] **138**: SDN OK, 3 LACP 2/2, 4/4 pings por sede, rutas OSPF S1 via s1p y S2 via s2p, seis servicios active, ens33/GW/Git inalterados; `LOTE138_REGRESION_FALLA_SDN=OK`. **3/3 TXT** verificados SHA256.
- [ ] **Pendiente dentro de #23:** comparar técnicamente con bridge Linux/FRR, distinguir la falla probada de `sdna0` de una caída de controlador/equipo, integrarlo con NOC real y auditar/importar PNG originales. **No repetir el fallo SDN, ni los LACP.**
- [ ] **Siguiente paso**: precheck de NOC 9130/exporter 9110 y observador privilegiado root:root instalado; diseñar telemetría real de 3 agregadores y OVS/Faucet con caducidad/UNKNOWN, sin mostrar estado estático como disponibilidad.

## Corte comprobado 15/11/2026 — auditoría NOC 139A/B/140/141 y PR #138 preparada

- [x] **139A**: seis servicios S04/S05 activos, 9130 y 9110 LISTEN loopback. Dos muestras 4s separadas: exporter `source_ok=true` y topología active, NOC `routing.available=true` con FIB S1=`s1p` S2=`s2p`, HA HTTP principal HQ `running`, warnings=[], hora `America/Panama` coherente y gestión `.40/24` GW `.2`.
- [x] **139B**: helper `/usr/local/libexec/netlab360-observer` root:root 0755 idéntico al fichero anterior por SHA `8c4480...`; `sudo -n ... snapshot` RC0, FRR x3 y rutas FIB legítimas. systemd NOC corre como rc-aa-ec y consulta helper autorizado por sudoers.
- [x] **140**: LACP HQ/S1/S2 2/2 en switch/cliente, `ad_num_ports 2`, alias de propiedad S05; Faucet/OVS state active, OF1.3 connected, OFPORT1/2/3 LIVE. No se repitieron pruebas de falla, ni se modificó gestión.
- [x] **141**: 14/14 pruebas de topología + 4/4 HA/NOC, 18 nodos/21 enlaces, warnings=[], campos LACP/SDN aun no integrados en API desplegada.
- [x] [PR #138](https://github.com/recm0708/netlab360/pull/138) fusionada (CI success, commit `eef89467`): helper sudoers actual extendido con fuentes read-only acotadas a 3 bonds 802.3ad y OVS/Faucet; app valida propietarios/antigüedad <=15s y devuelve UNKNOWN sin muestra, interfaz con 4 tarjetas sin alterar SVG, formateo horario es-PA. 
- [ ] **NO desplegado todavía en VM:** ejecutar [lotes 142A/142B/142C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-142a-142c-preflight-telemetria-noc-20261115.md) para comparar root helper anterior, correr pruebas, comprobar JSON real iproute2 en 6 bonds y OVS, sintaxis JS y hooks UI. Si JSON no coincide, corregir parser antes de instalar.
- [ ] Tras logs 142 OK: preparar instalación atómica del helper root:root con copia de retorno, validar FIB/LACP/SDN desde mismo sudoers, reiniciar SOLO NOC 9130, medir API y verificar vista real y hora Panamá. No hacer `up/down`, reiniciar guest o alterar FRR/OSPF/LACP/OVS/ens33.



---

# ISSUE #23 · [015] OVS/Faucet S05: dominio aislado y pruebas pendientes · estado open

## Estado vigente · 14/11/2026 · **ABIERTA**

SDN mediante Open vSwitch y Faucet **ya está implementado y validado funcionalmente en una isla S05 aislada** (bridge br-s05-sdn, OF13, VLAN410/420), sin tocar S02. Permanecen pendientes resiliencia dinámica, integración NOC y auditoría final de evidencia.

### Acreditado
- [x] Topología multisede existente de 3 switches VLAN-aware, segmentación y FRR/OSPF establecida, reutilizable como base comparativa.
- [x] Criterio de aislamiento acordado: no conectar OVS en paralelo al trunk S02/VMnet8 y no modificar `ens33`, puertos HA ni rutas WAN.

### Trabajo pendiente
- [x] Diseñar dominio OVS/Faucet **aislado** de gestión/S02, con bridge y puertos exclusivamente S05, comprobación de propietario y reversión selectiva protegida.
- [ ] Versionar configuración Faucet, datapaths OVS, VLAN/ACL y políticas con controles anti-bucle y pruebas offline.
- [x] Desplegar y verificar OpenFlow real con Faucet/OVS, VLAN410 permitida (A↔B RC0 2/2) y VLAN420 aislada (A↔C y C↔A RC1 sin respuestas), sin afirmar ACL adicionales no probadas.
- [x] Provocar pérdida y recuperación del enlace SDN S05 sdna0 (lotes 137A/137B/138) sin interferir con FRR/OSPF/HA existentes. Watchdog restore-only probado y cancelado tras recuperación.
- [ ] Comprobar/documentar limpieza selectiva en un momento seguro; NO ejecutar down sobre el dominio activo ni atribuir el ensayo sdna0 a redundancia de controlador/equipo.
- [ ] Documentar limitaciones/diferencias frente a Linux bridge+FRR, capturas originales y resultados en [#105](https://github.com/recm0708/netlab360/issues/105) e informe único [#27](https://github.com/recm0708/netlab360/issues/27).

Referencias: [tablero S05 vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md) y [histórico íntegro de esta issue](https://github.com/recm0708/netlab360/blob/main/docs/gestion/historico-issues/s05-issue-23-antes-de-consolidacion-20261114.md). No declarar `OVS_RUNNING` ni `FAUCET_CONNECTED` sin pruebas reales.
## Corte del lote 122 y preparación SDN (14/11/2026)

- [x] Lote **122** comprobado en segundo intento: el primero perdió SSH y se detuvo sin modificar estado; segundo acabó `LOTE122_AUDITORIA_PRE_SDN=OK`. VM Ubuntu con ~13 GiB RAM, ~132 GiB disco libres, **18 namespaces** S02/HA/LACP, 3 routers FRR Docker, 6 servicios S04/S05 activos, ens33 `192.168.47.40/24` GW `.2`, Git limpio. HQ/S1/S2 bonds 2/2, ping 4/4 y HA/FIB OK.
- [x] OVS y Faucet **no estaban instalados ni cacheados**; el chequeo mostró `ovs-vsctl`, `ovs-ofctl`, `faucet` ausentes y cero imágenes/servicios SDN. Esto es un hallazgo, **no un despliegue exitoso**.
- [x] [PR #123](https://github.com/recm0708/netlab360/pull/123) fusionada tras CI OK: `config/s05/sdn/faucet.yaml` versionado para datapath `br-s05-sdn` DP ID `0x505`, VLAN410 dos clientes A/B y VLAN420 C aislado, sin routers ni puertos de S02; 4 pruebas offline, y [lotes 123–127](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-123-127-preparacion-ovs-faucet-20261114.md) con gates para simulación APT, OVS sin bridges, Faucet Docker con digest y validación `check_faucet_config` aislada.
- [ ] **Próximo trabajo en VM:** ejecutar lotes 123–127 por orden; si instalación APT provoca cambio inesperado, detener. Estos pasos **NO crean dominio OVS ni arrancan Faucet**, por lo que aún no se declara SDN funcional.
- [ ] Después preparar implementación real de puentes veth/OVS, observar OpenFlow, validar aislamiento, permitir A↔B y denegar A↔C, falla/retorno y recuperación de recursos propios, sin interferir WAN/FRR/gestión.

## Corte 14/11/2026 · Lotes 123–127 reales completados y script SDN seguro versionado

- [x] **123:** auditó recursos y confirmó que no había colisión de br-s05-sdn, puertos sdna0/sdnb0/sdnc0, namespaces propios, puerto TCP 16653 ni contenedor Faucet; gestión ens33 .40/24 y FRR conservados.
- [x] **124:** apt update y simulación instalaron conceptualmente 5 paquetes nuevos, **0 actualizados y 0 eliminados**; OVS disponible 3.7.1-2.
- [x] **125:** paquete `openvswitch-switch=3.7.1-2` y common instalados realmente; ovs-vsctl responde `ovs_version=3.7.1`, **0 bridges** y 3 routers FRR en ejecución.
- [x] **126:** descargada imagen Faucet Docker por digest `sha256:34c5d8c1ce207de37abc7e4d9b1b60e020d43524d85e80449c637a7867e5ea32` (amd64); sin contenedor en ejecución.
- [x] **127:** 4/4 tests Python de configuración OK, `check_faucet_config=OK` en contenedor `--network none`, YAML del repo y operativo SHA256 idéntico `5945365af2f7341f02d95e2996e3e42ec585e7c32778a839632b4e1ec7480c5e`. Git limpio, ens33 .40/24, gateway .2. Marcador `LOTE127_SDN_CONFIG_VALIDADA_SIN_DESPLIEGUE=OK`.
- [x] **PR #124** fusionada tras CI OK: script [s05-sdn-ovs-faucet-aislado.py](https://github.com/recm0708/netlab360/blob/main/scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py) con guardas de estado exclusivo/ownership, Faucet publicado solo en 127.0.0.1:16653, OpenFlow13 secure, 3 namespaces sin interfaces S02 y verificaciones A↔B permitida/A↔C bloqueada; pruebas offline + [runbook 128–131](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-128-131-ovs-faucet-real-20261114.md). **El despliegue real aún NO se ejecutó en la VM**.
- [ ] Ejecutar 128 (precheck/suites), 129 (UP única vez solo si 128 OK), 130 (controlador OpenFlow y capturas 58–60), 131 (regresión S02/HA/LACP y hashes). **No repetir UP si falla o se corta SSH**: usar acción inspect sobre state-sdn.json.
- [ ] Tras SDN operativo, ensayar caída/retorno aislada de puerto/controlador con recuperación; integrar NOC y evidencias SHA256, sin cerrar issue prematuramente.

## Incidencia real S05 · Lote 129 parcial (14/11/2026, sin recuperación aún)

- [x] Lote 128 repetido satisfactoriamente: **16/16 tests offline** (4 configuración Faucet y 12 contratos OVS), YAML repo/operativo SHA256 igual, OVS 3.7.1 sin bridges y gestión `192.168.47.40/24` vía `.2` conservada; `LOTE128_SDN_PRECHECK=OK`.
- [x] Lote 129 **NO completado**: `up` pasó precheck, escribió `state-sdn.json`, creó `nl360-s05-faucet`, bridge `br-s05-sdn`, tres namespaces A/B/C y los puertos OF 1/2/3. Apuntó OVS a `tcp:127.0.0.1:16653`, pero falló con `RuntimeError: Faucet/OVS no establecieron canal OpenFlow` tras 15 consultas. El script dejó estado `needs_inspection` (según código; confirmar en la VM) y luego SSH se desconectó.
- [x] El usuario reintentó `up` una vez y este **lo bloqueó correctamente** con `Ya existe estado SDN; NO repetir up`; no se confirmaron cambios de ese segundo intento.
- [ ] **Paso inmediato:** diagnóstico **solo lectura** del archivo de estado, container exit/status/logs, publicación 16653→6653, `Controller is_connected/status.last_error`, puertos OVS, namespaces y estabilidad de gestión/S02/FRR/HA. No ejecutar up/down, docker rm/restart, ovs del-br ni reiniciar hasta identificar causa.
- [ ] Con diagnóstico real, diseñar reparación **selectiva** del despliegue con ownership y prueba de recuperación, sin eliminar el estado ni rehacer recursos; después validar conexión OpenFlow, política A↔B y aislamiento de C y tomar PNG 58–60.

## Diagnóstico definitivo 15/11/2026 — Faucet Errno 13 y recuperación preparada

- [x] **132A**: estado existente `needs_inspection`, propietario `NETLAB360_S05_SDN_V1`, bridge `br-s05-sdn` y los tres netns/puertos OF1/2/3 comprobados. Faucet contenedor `Exited(255)`, TCP `127.0.0.1:16653` no escucha, OVS `is_connected=false` y `last_error=Connection refused`. Gestión `ens33=.40/24` y default GW `.2` conservadas.
- [x] **132B**: Docker logs acreditan `Starting with UID=0 GID=0` y `[Errno 13] Permission denied: '/var/log/faucet/faucet.log'`. El contenedor no consiguió abrir el bind de logs y terminó antes de escuchar OpenFlow. Tres FRR activos, seis servicios HA/NOC `active`, VLAN y puertos propios intactos. El fallo `.:` por comando accidental de shell no corresponde a infraestructura.
- [x] [PR #127](https://github.com/recm0708/netlab360/pull/127) fusionada (CI OK, commit `90cedb3`): script `s05-sdn-recuperar-faucet-logs.py` con precheck de propiedad, digest, mounts, Docker 16653→6653, causante Errno13, namespaces/OFPORT y baseline; recuperación selectiva de permisos en directorio logs a UID0, modo0750 y `docker start` del **mismo contenedor**. Status SDN parcial solo se acepta en modo recuperación y jamás declara `active` sin conexión OpenFlow, flujos, pruebas A↔B, aislamiento C y preservación S02; 8 pruebas nuevas de fallo cerrado.
- [ ] **Ejecutar y validar** [lotes 133A–133D](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-133a-133d-recuperacion-faucet-20261115.md) para precheck, recuperación, capturas reales 58/59/60, regresión global y hash de TXT. **AÚN NO ejecutados** en la VM. No repetir UP, no ejecutar DOWN, no reiniciar Ubuntu/Windows.

## Corte 15/11/2026 · SDN Faucet operativo, falta evidencia 60 y cierre de regresión

- [x] **133A**: 20/20 tests offline OK (8 recuperación + 12 SDN), state previo `needs_inspection`, mounts/propietario/Docker/Errno13 verificados. Primer intento de sincronización sufrió reset SSH sin demostrar regresión.
- [x] **133B**: recuperación selectiva en sitio exitosa; permisos del directorio de logs ajustados y **mismo contenedor Faucet iniciado**, OpenFlow connected al intento 9, 25 reglas, cuatro pings/aislamientos correctos, baseline S02/FRR/gestión intacto; state a `active`, `LOTE133B_RECOVERY=OK`.
- [x] **133C pasos 716–718**: OpenFlow connected y `31` reglas, capturas **S05_58 y S05_59** con resultados válidos, A↔B 2/2 y 2/2 (0% pérdida).
- [ ] **133C paso 719**: A→C devolvió 2 transmitidos/0 recibidos/100% pérdida, pero wrapper externo `timeout -k 2s 10s` marcó **RC124** y abortó el lote (se exigía RC1 del ping). No se ejecutó C→A ni se imprimió FIN_CAPTURA_60 o LOTE133C_OK. No inferir que SDN falló por este RC124.
- [ ] **133D**: NO se ejecutó. El paste en terminal contenía secuencias `[200~` y delimitador `BASH~`, produjo heredoc abierto/errores de sintaxis, cancelado por Ctrl+C. No existe auditoría completa ni manifiesto SHA de 133D.
- [x] [PR #129](https://github.com/recm0708/netlab360/pull/129) propuesta: verificador solo consulta de captura 60 con ping RC1/0 recibidos/100% pérdida, control positivo A→B RC0/2/2, sin timeout externo de 10 s, tests de rechazo RC124 y RC2 y [lotes 134A–134C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-134a-134c-evidencia60-y-regresion-20261115.md) para cerrar evidencia/regresión. **No se han ejecutado lotes 134.**
- [ ] Confirmar captura 60 guardada y PNG SHA256 más adelante. **No repetir 133A/133B ni ejecutar up/down**, mantener Firewall/FRR/LACP/NOC y gestión intactos.

## Corte del 15/11/2026 — suspensión VMware solicitada y fallo de formato ICMP en 134B

- [x] **134A** completado: 10/10 tests offline; `S05_SDN_FAUCET_OPENFLOW=CONNECTED`, 25 reglas, pings A/B y aislamiento C correctos, gestión `ens33=192.168.47.40/24` GW `.2`, repo limpio.
- [x] **134B diagnosticado**, NO completado: estado SDN active, 31 reglas OpenFlow; ping negativo A→C regresó RC1 y `10 packets transmitted, 0 received, +10 errors, 100% packet loss`. El parser solo aceptaba `received, 100%` sin `+10 errors` y 2 enviados; abortó sin FIN_CAPTURA ni marcador OK. Reintento sufrió caída SSH; otro reprodujo lo mismo. **Captura S05_60 pendiente** y 134C no iniciado.
- [x] [PR #131](https://github.com/recm0708/netlab360/pull/131) CI OK y fusionada (commit `d49ff77b`): corregir parsing de salidas iputils con `+N errors` y múltiples transmisiones negativas de ARP, manteniendo RC1+0 recibidos+100% pérdida como gate, rechazando RC124/RC2/timeout, conservando exigencia 2/2 RC0 en A→B. Tests reproducen el caso real.
- [ ] **Pausa operativa antes de más pruebas:** usuario desea reiniciar Windows. Verificar espacio de volumen anfitrión vs RAM guest, baseline en TXT, sincronizar disco y **suspender completamente `netlab360-lab` en VMware Workstation** antes de reiniciar Windows. La suspensión aún **no está confirmada**, ni la reanudación. No reiniciar guest Ubuntu; los netns efímeros requieren estado de RAM conservado. No borrar .vmss/.vmem/.lck, no snapshots permanentes.
- [ ] Tras reanudar, verificar fecha, ens33/route, Faucet/OpenFlow, contenedor/3 namespaces, FRR/LACP/HA/NOC. Entonces repetir **solo** captura 60 con el parser corregido, usando un TXT nuevo que preserve el histórico fallido; completar regresión global y SHA256, y auditar PNG.

## Corte 15/11/2026 — VMware reanudada; LACP status detectó falso drift de tabla completa

- [x] VMware Workstation restauró el estado suspendido de Ubuntu tras reinicio Windows: NTP sincronizado, `ens33=192.168.47.40/24`, default GW `.2`, 21 namespaces y cuatro contenedores (FRR x3 y Faucet) activos.
- [x] SDN state active, OpenFlow connected con 28 reglas, VLAN410 A↔B comunicada y VLAN420 C aislado, baseline S02/FRR/gestión conservado.
- [ ] **LACP de HQ**: bonds 2/2 y cuatro pings OK, pero `status` lanzó `Red de gestión cambió respecto del precheck` al comparar texto literal de TODA la tabla de rutas. La diferencia exacta frente al state-hq.json aún requiere auditoría; S1/S2 y seis servicios no llegaron a validarse en esa ejecución. `NETLAB360_REANUDACION=OK` no apareció.
- [x] [PR #132](https://github.com/recm0708/netlab360/pull/132) CI OK fusionada (`78a03738`): HQ/S1/S2 comprueban ens33 IPv4 y rutas propias/defaults protegidas, no exigen rutas ajenas idénticas; no cambia JSON de state ni configuraciones. Seis pruebas de regresión rechazan drift real.
- [x] [PR #133](https://github.com/recm0708/netlab360/pull/133) fusionada: [lotes 135A/B/C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-135a-135c-reanudacion-y-captura60-20261115.md), sin acciones mutantes.
- [ ] Ejecutar 135A auditoría baseline actual, 135B revalidación completa HQ/S1/S2/SDN/HA/NOC, 135C evidencia 60 con parser ICMP corregido (PR #131). Logs históricos parciales 10/14/19 se preservan; PNG 60 sigue pendiente.

## Corte verificado 15/11/2026 — 135A/B/C completos, S05_60 obtenida; siguientes 136–138

- [x] **135A**: 23/23 tests aprobados (6 gestión+10 HQ+7 sucursales). La diferencia exacta de gestión es `docker0 172.17.0.0/16`: la ruta antigua tenía `linkdown` y la actual no; IPv4 `ens33=192.168.47.40/24` y ruta predeterminada `.2` iguales, las 3 sedes pasaron protección crítica.
- [x] **135B**: LACP HQ/S1/S2 2/2 en ambos extremos, 4 pings por sitio OK, HA/FIB/VLAN conservados; Faucet OpenFlow conectado 28 reglas, segmentación A/B-C correcta; rutas OSPF HQ→S1 por s1p, HQ→S2 por s2p, seis servicios activos, NTP, Git limpio. `LOTE135B_VMWARE_REANUDACION_COMPLETA=OK`.
- [x] **135C**: 13/13 tests de parser, OpenFlow 31 reglas; A→B `RC0 2/2`, A→C y C→A `RC1, 0 recibidos, 100% pérdida` (10 transmisiones por ARP). `S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO`, `LOTE135C_EVIDENCIA60=OK`. El operador **confirma haber guardado S05_60**; la existencia y SHA-256 del PNG original no se han auditado.
- [x] [PR #134](https://github.com/recm0708/netlab360/pull/134) fusionada (CI success, commit `9925ce62`): script S05 de pérdida/restauración **solo de sdna0** con precheck de ownership, timer restore-only systemd de 120s y pruebas ICMP/OpenFlow/servicios sin tocar ens33/FRR/LACP. [PR #135](https://github.com/recm0708/netlab360/pull/135) fusionada: punto de reanudación actualizado.
- [ ] **Próximas ejecuciones, aún NO realizadas en la VM:** [lotes 136, 137A, 137B y 138](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-136-138-aceptacion-y-falla-sdn-20261115.md): hashes TXT estáticos, precheck, falla/retorno protegida puerto A y regresión. Capturas S05_61 y S05_62 pendientes. No repetir 135 ni fault LACP. La resiliencia de puerto SDN no es HA física/instancia.

## Corte real 15/11/2026 — resiliencia de enlace SDN aceptada (lotes 136–138)

- [x] **Lote 136**: Faucet sigue conectado, 25 reglas OpenFlow, A↔B permitido y C aislado, ens33 `.40/24` GW `.2`, Git limpio. Se verificaron **7/7 registros TXT** por SHA-256 (incluidos 135A/B/C y recuperación anterior). `LOTE136_SDN_ESTABLE_Y_CAPTURA60=OK`.
- [x] **137A**: 9/9 tests de seguridad OK; precheck de ownership/puerto SDN A, OpenFlow conectado, 31 reglas, servicios S02/FRR/NOC/HA preservados; `LOTE137A_PRECHECK_FALLA_SDN=OK`.
- [x] **137B**: watchdog `nl360-s05-sdn-port-a-rescate-68997ee0a7.timer` armado; **solo `sdna0` DOWN**. Ping A→B mostró `10 transmitidos, 0 recibidos, 100% pérdida, RC1`, controlador Faucet siguió conectado; preservación de FRR, NOC, HA comprobada. Restauración `sdna0` solicitada; A↔B volvió en **intento 1**, A↔C/C↔A permanecieron aislados, OpenFlow 31 reglas; watchdog cancelado tras validación, `S05_SDN_FALLA_RETORNO=OK_DOWN_UP_ENLACE_A`. Operador confirma capturas **S05_61 y S05_62** tomadas, pendiente auditoría bytes PNG.
- [x] **138**: SDN OK, 3 LACP 2/2, 4/4 pings por sede, rutas OSPF S1 via s1p y S2 via s2p, seis servicios active, ens33/GW/Git inalterados; `LOTE138_REGRESION_FALLA_SDN=OK`. **3/3 TXT** verificados SHA256.
- [ ] **Pendiente dentro de #23:** comparar técnicamente con bridge Linux/FRR, distinguir la falla probada de `sdna0` de una caída de controlador/equipo, integrarlo con NOC real y auditar/importar PNG originales. **No repetir el fallo SDN, ni los LACP.**
- [ ] **Siguiente paso**: precheck de NOC 9130/exporter 9110 y observador privilegiado root:root instalado; diseñar telemetría real de 3 agregadores y OVS/Faucet con caducidad/UNKNOWN, sin mostrar estado estático como disponibilidad.



---

# ISSUE #31 · [023] LACP multisede 2→1→2 validado; estadística y evidencias finales pendientes · estado open

## Estado vigente · 14/11/2026 · **ABIERTA**
**Piloto de capacidad y primer LACP real de HQ completados.** El objetivo multisede (HQ/S1/S2) y su recuperación aún no está demostrado.

### Completado
- [x] Piloto aislado IEEE 802.3ad con 2 puertos activos y pruebas 2→1→2, HTTP/ICMP preservados en estados estabilizados.
- [x] P1 y P1B registrados con iperf3 multistream 1/8 flujos, retransmisiones, afinidad/CPU y manifestaciones locales. Valores de hasta `127,39 Gb/s` son virtuales condicionados por CPU, no capacidad física.
- [x] Diseño de LACP local en switches VLAN-aware S02, sin fusionar WAN FRR/OSPF; IPAM de tres VLAN auditado (lotes 105–108).
- [x] LACP HQ realmente desplegado en `nl360-s02-sw-hq/s5bond0` (miembros `s5p1/s5p2`) y `nl360-s05-lacp-hq/bond0` (`s5c1/s5c2`), 2/2 miembros 802.3ad `layer3+4`, VLAN 120 PVID untagged, IP `10.70.20.40/24` ocupada.
- [x] Lotes 109–110: 8 tests, precheck, ICMP a gateway/frontal HQ/backend S1/host S2, HTTP HA/FIB/gestión y Git intactos.
- [x] Diagnóstico tras timeout transitorio: lote 111D-R (4/4 ICMP desde cliente, 3/3 desde hosts de comparación, rutas FRR principales), 111D-S (SSH activo, sin fallo kernel filtrado). No atribuir resets SSH a LACP sin datos.
- [x] Prueba HQ 2→1→2 versionada con restauración `finally`, manejador SIGHUP y failsafe transitorio systemd 120s; 6 tests offline CI OK. **NO se ejecutó todavía.**
- [x] S05_45 reportada tomada; salidas de captura S05_46/47 coherentes. PNG 46/47 aún no confirmados.

**Validador actualizado (PR #107, CI OK):** el precheck de S1/S2 debe ejecutarse con `python3 scripts/validacion/s05-lacp-integracion-precheck.py precheck --sites S1 S2`. El modo global original comprueba si HQ .40 está libre y ya no procede después del despliegue. [Runbook de lotes 114A–D](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-siguientes-lacp-hq-20261114.md).

### Pendientes reales
- [x] Ejecutada falla HQ 2→1→2 con verificación HTTP/FIB/gestión, watchdog cancelado y salida para capturas 48/49 (lote 114B aprobado).
- [x] LACP S1 VLAN220 / S2 VLAN320 desplegados realmente y verificados: 2/2 por extremo, 4/4 ICMP por sede, FIB/HTTP/gestión conservados (L116, L117R-B, L118-R).
- [x] Ejecutados y validados los ensayos reales S1/S2 2→1→2 (lotes 119–121), con rescates systemd cancelados, HTTP 200_BACKEND_HQ, OSPF s1p/s2p, 6 servicios activos y postchecks 3 sedes. Se obtuvieron salidas para capturas 53–57; falta auditoría de los PNG originales.
- [ ] Revisión estadística razonable de P1/P1B: variabilidad de carga/CPU, incertidumbre y conclusiones; evitar interpretar throughput virtual como físico.
- [ ] Distinguir claramente falla de miembro LACP de falla de instancia/servidor/equipo, con [#32](https://github.com/recm0708/netlab360/issues/32).
- [ ] Importar y verificar PNG/JSON/log originales con SHA-256 junto a [#105](https://github.com/recm0708/netlab360/issues/105); referencias al informe único.

Recuperación: [tablero S05 vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md). Historial íntegro: [histórico íntegro de esta issue](https://github.com/recm0708/netlab360/blob/main/docs/gestion/historico-issues/s05-issue-31-antes-de-consolidacion-20261114.md). No repetir `up` HQ ni laboratorio P1B ya ejecutado.
## Corte 14/11/2026 — Lote 114A interrumpido; corrección PR #109
- [x] Git sincronizado a `e4521d1`; 6/6 tests de falla-retorno y 8/8 de precheck selectivo OK (**14/14**), sin alteraciones en red.
- [x] Estado HQ: los bonds `s5bond0` y `bond0` reportaron **2 miembros activos**, incluso cuando ping excedió el timeout de 10 s. En dos intentos la excepción afectó destinos diferentes (`10.72.20.20` y `10.70.20.23`); otros destinos habían pasado. Diagnóstico 111D-R previo logró 4/4 desde LACP HQ y 3/3 desde hosts S02.
- [x] Lote 114B pegado una vez pero **no ejecutado**: su compuerta `grep LOTE114A_PRECHECK=OK` terminó sin marcador. Sin falla controlada, sin cambios.
- [x] PR [#109](https://github.com/recm0708/netlab360/pull/109) integrada tras CI: `ping_verified` registra TIMEOUT_PROCESO/ERROR_ICMP, hasta 3 intentos de 2 pings con timeout externo 15 s; **falla cerrado** si todos fallan. Aplica a `status` y a ensayo 2→1→2. No convierte pérdidas en éxito artificial.

## 14/11/2026 · Lote 114A-R aprobado, gate de 114A-S corregido (PR #112)

- [x] Operador sincronizó a `da6e7b5` y completó **25/25 tests** (10 integración HQ, 7 failover HQ offline, 8 precheck S1/S2). Agregadores 2/2; ping 4/4 primer intento tanto en `status` como `precheck`, HTTP `200_BACKEND_HQ`, S1/S2 `.40` no asignadas, 36 IP inventariadas, servicios HA/FIB y VLAN preservados, `ens33=.40/24` GW `.2`, Git limpio; marcador `========== LOTE114A_R_PRECHECK=OK ==========`.
- [x] **114A-S NO ejecutado todavía**: dos intentos se detuvieron sin imprimir paso 573 porque `grep -Fxq` buscaba el marcador sin separadores `==========`. No implicó cambios en bond/FRR/red y 114B sigue sin ejecutar.
- [x] [PR #112](https://github.com/recm0708/netlab360/pull/112) integrada tras CI OK: gates de 114A-S, 114B, 114C ahora usan el texto exacto completo; tres tests automáticos de regresión; continuidad en `docs/REANUDAR-AQUI.md` y tablero S05.

## 14/11/2026 · Lotes 114A-S, 114B, 114C y 114D completados realmente

- [x] **114A-S:** Git a `832b6e1`; dos rondas a gateway HQ `10.70.20.1`, frontal HQ `10.70.20.23`, backend S1 `10.71.20.21` y host S2 `10.72.20.20`: **16/16 paquetes recibidos, 0% pérdida en esas rondas**. Bonds switch/cliente IEEE 802.3ad 2/2; `ens33=.40` GW `.2`, Git limpio. `LOTE114A_S_ESTABILIDAD=OK`.
- [x] **114B:** falla controlada de miembro `s5c1` con watchdog `systemd-run` temporal; switch y cliente pasaron **2/2→1/1→2/2**. Durante 1/1 ping 4/4 destinos y HTTP real `200_BACKEND_HQ`; HA/FIB y puertos S02 conservados. Tras restauración 4/4 ping, VLAN120 PVID untagged, gestión intacta y rescate cancelado. `S05_LACP_HQ_PRUEBA=OK_2_1_2`, `LOTE114B_FALLA_RETORNO=OK`. Esto no demuestra 0 pérdidas durante cada milisegundo de conmutación.
- [x] **114C:** secciones de salida `INICIO_CAPTURA_S05_48/49` a `FIN_CAPTURA` extraídas y revisadas; **no consta confirmación de archivos PNG guardados**, ni importación binaria.
- [x] **114D:** validador selectivo S1/S2 `plan` + `precheck` = OK; candidatas `10.71.20.40` VLAN220 y `10.72.20.40` VLAN320 no asignadas en inventario de 36 direcciones ni responden ICMP desde host VLAN; 3 FRR running, interfaces/VLAN protegidas, NOC/HTTP HA OK; HQ conserva 2/2. `LOTE114D_S1S2_PRECHECK=OK`. La ausencia de respuesta ICMP **no garantiza** globalmente IP libre.

Evidencia local: `~/netlab360-bootstrap/s05/evidencias/lacp-integracion/30_Estabilidad_PreFailover_HQ.txt`, `25_Falla_Retorno_HQ_2_1_2.txt`, `31_Preparacion_LACP_S1_S2.txt`.
## Código para LACP S1/S2 preparado (14/11/2026; NO ejecutado)

- [x] [PR #113](https://github.com/recm0708/netlab360/pull/113) integrada con CI OK: `s05-lacp-s1-integracion.py` VLAN220 IP `10.71.20.40`; `s05-lacp-s2-integracion.py` VLAN320 IP `10.72.20.40`; estados independientes, validación de IPAM por sede, propietario de puertos, VLAN/baseline protegidos, rollback selectivo y confirmación explícita para UP/DOWN. Pruebas automáticas de contrato incluidas.
- [x] [PR #114](https://github.com/recm0708/netlab360/pull/114) integrada: punto de reanudación actualizado y runbook de lotes 115–118 con gates y capturas S05_50/51/52. Aún no se han ejecutado los despliegues en VM.

## Corte 14/11/2026 · Lotes 115–117 y evidencias revisadas

- [x] **Lote 115:** CI y 7 tests locales de contratos S1/S2 OK; precheck S1/S2/HQ, gestión `ens33=192.168.47.40/24`, gateway `.2` y Git intactos.
- [x] **Lote 116:** **LACP S1 desplegado realmente** en VLAN220 y `10.71.20.40/24`, switch `nl360-s02-sw-s1/s5bond0` y cliente `nl360-s05-lacp-s1/bond0` en 802.3ad **2/2 miembros**; pings 4/4 (S1 GW, HQ frontal, S1 backend, S2 host), `S05_LACP_S1_SERVICIOS_HA_FIB=OK`, S02 protegido, HQ 2/2, VLAN220 PVID untagged y gestión intactos. `LOTE116_LACP_S1=OK`. PNG de captura **S05_50 recibido y visualmente validado**, no importado aún al repo.
- [x] **Lote 117 paso 596:** precheck S2 OK; inventario aumentó de 36→**37 IPv4** tras agregar S1. IP `10.72.20.40` propuesta sin asignación observada, VLAN320 sin conflictos y servicios HA/NOC correctos.
- [x] **Lote 117 paso 597 falló antes de crear nuevos recursos S2**: `TimeoutExpired` a 15s en `sudo ip netns exec nl360-s02-sw-s2 bridge vlan show`, durante **precheck** de `up`; no apareció `S05_LACP_S2_DESPLIEGUE=OK`, y 598–600 no corrieron. **No asumir S2 instalada** ni repetir UP sin comprobar state e interfaces.
- [x] [PR #115](https://github.com/recm0708/netlab360/pull/115) integrada tras CI OK, commit `2424d87bbd2806d9060c3fb56117e7d8515d2e03`: consulta `bridge vlan show` ahora solo lectura con **2 intentos hasta 30s**, cuenta timeout y falla cerrado si continúa.

## Corte 14/11/2026 — Integración HQ/S1/S2 completada, fallo sucursales pendiente

- [x] **L117R-A:** 17 tests OK, estado/namespaces/puertos S2 libres y precheck reforzado OK; S1/HQ sin regresión.
- [x] **L117R-B:** despliegue **S2 REAL** en VLAN320, cliente 10.72.20.40/24; ambos bonds 2/2, ICMP 4/4, HA/FIB y gestión intactos. Marcador `LOTE117R_B_S2=OK`.
- [x] **L118-R:** primer intento se detuvo por `KeyError: 'S1'` tras respuesta NOC/FIB incompleta; segundo intento `LOTE118_R_TRES_BONDS=OK` verificó **HQ, S1 y S2 2/2**, ICMP 4/4 por sede, rutas OSPF principales s1p/s2p, seis unidades activas, ens33/gestion y repo sin cambios.
- [x] **Usuario confirma capturas tomadas** de los lotes recientes (48/49/51/52); su verificación PNG/sha256/importación al repositorio sigue pendiente de recepción efectiva.
- [x] [PR #117](https://github.com/recm0708/netlab360/pull/117) CI OK e integrada: scripts independientes de ensayo 2→1→2 de S1 y S2 con rescate systemd, rollback y pruebas offline. [PR #118](https://github.com/recm0708/netlab360/pull/118) CI OK e integrada: reintentos estrictos para lecturas NOC/FIB incompletas.
- [x] Lotes 119–121 ejecutados; manifiesto SHA-256 de los cuatro TXT verificado (4/4). Los PNG originales y su integridad no se han comprobado en GitHub.


**Mantenimiento checklist (14/11/2026):** Se retiraron las instrucciones operativas de lotes 114/115–118 ya superados, preservadas en GitHub y documentos de reanudación. Las casillas abiertas restantes se refieren a trabajo aún no completado; no declarar fase S05 cerrada.

## Resultado final recibido 14/11/2026 — LACP multisede completado técnicamente

- [x] Lote **119A**: 26 pruebas automatizadas OK (S1 8/8, S2 8/8, HQ 7/7 y NOC 3/3); HQ, S1 y S2 2/2, pings/HTTP/HA/FIB correctos, gestión y Git intactos.
- [x] Lote **119B**: S1 2/2→1/1→2/2, 4 destinos accesibles y HTTP `200_BACKEND_HQ` durante 1/1. Un ping a `10.71.20.1` agotó tiempo externo en intento 1 y respondió en intento 2; no afirmar cero pérdida transitoria. Temporizador systemd cancelado y postcheck de 3 sedes OK.
- [x] Lote **120**: S2 2/2→1/1→2/2, 4 destinos y HTTP reales durante 1/1, temporizador systemd cancelado. HQ y S1 conservados; un ping HQ→S2 tuvo timeout transitorio y respondió al segundo intento, sin evidencia de caída permanente.
- [x] Lote **121**: tres sedes con agregadores 2/2, OSPF principal `s1p/s2p`, seis servicios `active`, `ens33=192.168.47.40/24`, gateway `.2`, Git limpio. `LOTE121_LACP_MULTISEDE=OK`. Los **4 TXT** 41/42/43/45 tienen hashes SHA-256 verificados contra el manifiesto 46 (no equivale a validar PNG).
- [ ] Caracterización P1/P1B: redacción estadística y límites del throughput virtual/CPU; revisión de originales PNG y trazabilidad documental de LACP para cerrar #31. Las cuestiones de equipo/instancia van por #32; importación por #105.

**No repetir fallas ni reinstalar bonds**. Avanzar ahora hacia OVS/Faucet (#23), HA de instancia (#32) y NOC (#64).
## Corte 15/11/2026 — VMware reanudada; LACP status detectó falso drift de tabla completa

- [x] VMware Workstation restauró el estado suspendido de Ubuntu tras reinicio Windows: NTP sincronizado, `ens33=192.168.47.40/24`, default GW `.2`, 21 namespaces y cuatro contenedores (FRR x3 y Faucet) activos.
- [x] SDN state active, OpenFlow connected con 28 reglas, VLAN410 A↔B comunicada y VLAN420 C aislado, baseline S02/FRR/gestión conservado.
- [ ] **LACP de HQ**: bonds 2/2 y cuatro pings OK, pero `status` lanzó `Red de gestión cambió respecto del precheck` al comparar texto literal de TODA la tabla de rutas. La diferencia exacta frente al state-hq.json aún requiere auditoría; S1/S2 y seis servicios no llegaron a validarse en esa ejecución. `NETLAB360_REANUDACION=OK` no apareció.
- [x] [PR #132](https://github.com/recm0708/netlab360/pull/132) CI OK fusionada (`78a03738`): HQ/S1/S2 comprueban ens33 IPv4 y rutas propias/defaults protegidas, no exigen rutas ajenas idénticas; no cambia JSON de state ni configuraciones. Seis pruebas de regresión rechazan drift real.
- [x] [PR #133](https://github.com/recm0708/netlab360/pull/133) fusionada: [lotes 135A/B/C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-135a-135c-reanudacion-y-captura60-20261115.md), sin acciones mutantes.
- [ ] Ejecutar 135A auditoría baseline actual, 135B revalidación completa HQ/S1/S2/SDN/HA/NOC, 135C evidencia 60 con parser ICMP corregido (PR #131). Logs históricos parciales 10/14/19 se preservan; PNG 60 sigue pendiente.

## Corte verificado 15/11/2026 — 135A/B/C completos, S05_60 obtenida; siguientes 136–138

- [x] **135A**: 23/23 tests aprobados (6 gestión+10 HQ+7 sucursales). La diferencia exacta de gestión es `docker0 172.17.0.0/16`: la ruta antigua tenía `linkdown` y la actual no; IPv4 `ens33=192.168.47.40/24` y ruta predeterminada `.2` iguales, las 3 sedes pasaron protección crítica.
- [x] **135B**: LACP HQ/S1/S2 2/2 en ambos extremos, 4 pings por sitio OK, HA/FIB/VLAN conservados; Faucet OpenFlow conectado 28 reglas, segmentación A/B-C correcta; rutas OSPF HQ→S1 por s1p, HQ→S2 por s2p, seis servicios activos, NTP, Git limpio. `LOTE135B_VMWARE_REANUDACION_COMPLETA=OK`.
- [x] **135C**: 13/13 tests de parser, OpenFlow 31 reglas; A→B `RC0 2/2`, A→C y C→A `RC1, 0 recibidos, 100% pérdida` (10 transmisiones por ARP). `S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO`, `LOTE135C_EVIDENCIA60=OK`. El operador **confirma haber guardado S05_60**; la existencia y SHA-256 del PNG original no se han auditado.
- [x] [PR #134](https://github.com/recm0708/netlab360/pull/134) fusionada (CI success, commit `9925ce62`): script S05 de pérdida/restauración **solo de sdna0** con precheck de ownership, timer restore-only systemd de 120s y pruebas ICMP/OpenFlow/servicios sin tocar ens33/FRR/LACP. [PR #135](https://github.com/recm0708/netlab360/pull/135) fusionada: punto de reanudación actualizado.
- [ ] **Próximas ejecuciones, aún NO realizadas en la VM:** [lotes 136, 137A, 137B y 138](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-136-138-aceptacion-y-falla-sdn-20261115.md): hashes TXT estáticos, precheck, falla/retorno protegida puerto A y regresión. Capturas S05_61 y S05_62 pendientes. No repetir 135 ni fault LACP. La resiliencia de puerto SDN no es HA física/instancia.



---

# ISSUE #32 · [024] HA WAN y HTTP validada; instancia/equipo y aceptación pendientes · estado open

## Continuidad 15/11/2026 — scripts 145A/145B probados en CI y fusionados

- [x] Lotes **144A/B/C** completados en VM: monitor HTTP S2 de 1.69s con ambos backends running y frontal BACKEND_HQ/PRINCIPAL, 2 muestras NOC sin advertencias y rutas FIB S1=s1p/S2=s2p; 3 GET HTTP desde S2 200 OK; helper legacy root:root 0755/FIB sin cambios.
- [x] **PR #141** fusionado (docs, commit cc6f2a67): [corte maestro operativo](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), procedimiento de backup/rollback y validación NOC LACP/SDN.
- [x] **PR #142** fusionado tras **dos workflows CI SUCCESS** (commit 50f18f30): scripts ejecutables [145A](https://github.com/recm0708/netlab360/blob/main/scripts/operacion/s05-lote-145a-instalar-observador.sh) y [145B](https://github.com/recm0708/netlab360/blob/main/scripts/operacion/s05-lote-145b-activar-noc.sh), test offline bash -n y prohibición de mutaciones de red. Incidencia previa en aserción de test estático corregida y la revisión final de CI aprobada. **NO se han ejecutado todavía en la VM.**
- [ ] **SIGUIENTE ACCIÓN REAL**: en VM `cd ~/proyectos/netlab360 && git pull --ff-only origin main`; con Git limpio y SHA del helper legacy correcto, ejecutar `bash scripts/operacion/s05-lote-145a-instalar-observador.sh` y confirmar marcador `LOTE145A_HELPER_ROOT_NOC=OK` y snapshot FRR/FIB/LACP/SDN. **Después solamente** ejecutar `bash scripts/operacion/s05-lote-145b-activar-noc.sh`, confirmar dos muestras API y marcador `LOTE145B_NOC_LACP_SDN=OK`. Los scripts tienen respaldo root y retorno ante error y registran logs TXT 14 y 15 en noc-integracion.
- [ ] Tras 145B OK, revisar dashboard en Chrome con SSH túnel 9130, cuatro tarjetas reales LACP HQ/S1/S2 + Faucet, hora Panamá, capturar S05_63. Si hay error, NO repetir sin diagnosticar hash/backup y leer log.
- [ ] S05 restante: #32 HA independiente instancia/equipo y su alcance mono-VM, #31 P1/P1B estadística, #105 auditoría PNG originales; pasar a S06/S07 cuanto antes. Informe S01–S04 existente puede ampliarse **ya**, sin esperar S07 ni reescribirse de cero.


---

## CORTE ACTUAL 15/11/2026 — 144A/B/C COMPLETADOS, desplegar NOC en 145A/B

**En VM (logs reales del usuario):**
- [x] **144A:** seis servicios active (NRestarts=0), dos muestras 4 s apartes: `ha_service.status=running` con `BACKEND_HQ/PRINCIPAL` y `available=true`; monitor S2 1.69 s fresco confirma BACKEND_HQ/S1 running y frontal HQ running, `source_warnings=[]`. FIB S1=`s1p` y S2=`s2p`. La muestra aislada offline de 143B no se reprodujo.
- [x] **144B:** desde cliente S2 VLAN320, HTTP 200 e identidad saludable de backend HQ 10.70.20.21:8088, backend S1 10.71.20.21:8088 y frontal HQ 10.70.20.23:8080 (cabeceras BACKEND_HQ/PRINCIPAL). Cuatro servicios HA active sin reinicios, ens33 y Git intactos. **No hay reparación HTTP HA pendiente por esta auditoría**; no repetir failovers.
- [x] **144C:** root helper instalado permanece en versión legacy root:root 0755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; sudoers snapshot RC0 y 3 routers/FIB intactos. NOC 9130 corre como usuario rc-aa-ec y sigue sin campos LACP/SDN: **nuevo código GitHub NO instalado todavía**. Repo limpio `70bd06c`, ens33 `192.168.47.40/24`, default GW `192.168.47.2`.
- [x] [PR #141](https://github.com/recm0708/netlab360/pull/141) fusionado en main `cc6f2a67` para acelerar: [corte maestro 144C](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), [145A instalar helper root con SHA/backup/rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145a-deploy-helper-seguro-20261115.md), [145B reiniciar SOLO NOC y validar 2 muestras API + rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md).
- [ ] **145A y 145B aún NO se ejecutaron**; no afirmar despliegue del observador nuevo. Tras 145B=OK, confirmar en navegador y tomar **S05_63_NOC_LACP_Multisede_y_Faucet_Operativos**; no repetir LACP/SDN WAN/HA antes probados ni reiniciar Ubuntu.
- [ ] Después: #32 alcance HA independiente de instancia/equipo (sin confundir con redundancia de enlace), #31 valoración P1/P1B y #105 originales PNG + SHA y cierre S05. S06 ML (#6/#25/#26) y S07 AIOps (#7) siguen pendientes. El informe largo S01–S04 ya existe y **puede ampliarse en paralelo**.


---

## Corte vigente S05 · 15/11/2026 · 143A/B/C aprobados, HTTP HA en diagnóstico

- [x] **143A COMPLETADO:** Git local main 1fba8c5, 21/21 pruebas del parser, 14/14 topología, 14/14 layout, 6/6 HA/UI = **55/55**. Helper autorizado INSTALADO sigue LEGACY root:root 755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`. ens33 .40/24 gateway .2 y Git limpio.
- [x] **143B COMPLETADO:** 6/6 bonds HQ/S1/S2 switch y cliente, `ip JSON ad_num_ports=None` en los seis y `/proc/net/bonding Number of ports:2` en todos, alias y 802.3ad correctos. OVS propietario S05, Faucet running, OpenFlow connected, 25 reglas. FIB S1=s1p, S2=s2p. API en ejecución aún sin LACP/SDN (NO desplegada).
- [x] **143C COMPLETADO:** cuatro tarjetas HTML fuera del SVG, `node --check` OK, NOC/exporter active, gestión y Git intactos.
- [ ] **Anomalía por investigar, NO declarar HA correcto:** 143B capturó fuente HTTP de S2 válida `available=true`, `ha_service.status=offline`, backend/path `None`, timestamp 2026-11-15T12:39:45+00:00; `source_warnings=[]`. No implica necesariamente caída de los tres servicios. Diagnosticar monitor y endpoints HTTP desde cliente S2 antes de cualquier rollout.
- [x] [PR #140](https://github.com/recm0708/netlab360/pull/140) fusionada en main (commit `70bd06cc`): [corte maestro actual](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-143C-20261115.md) y [lotes 144A/B/C SOLO LECTURA](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-144a-144c-diagnostico-http-ha-pre-noc-20261115.md). Los marcadores `COMPLETADO` de 144 representan diagnósticos, no aceptación HA.
- [ ] **Próximas ejecuciones (NO hechas todavía):** 144A dos muestras de NOC y observación S2, 144B tres GET HTTP desde netns S2 y journal, 144C hash/helper legacy y FIB. No sobrescribir logs históricos 08/09/10, no instalar binario root, no reiniciar NOC ni guest. Tras revisar resultados, definir instalación atómica root:root con backup/rollback y validación UI/FIB/LACP/SDN.


---

## Estado vigente · 14/11/2026 · **ABIERTA**
**Se comprobó redundancia de rutas y del servicio HTTP; la redundancia de un equipo físico completo NO está probada.** No se debe confundir detener un proceso backend con apagar un router/switch/servidor independiente.

### Validado
- [x] Rutas WAN primarias y de respaldo S1/S2, FIB observada con conmutación y restauración sin modificar gestión.
- [x] Tres namespaces HA S05 integrados por VLAN 120/220: backend HQ `10.70.20.21:8088`, backend S1 `10.71.20.21:8088`, frontal HQ `10.70.20.23:8080`.
- [x] Servicios HTTP activos en systemd; conmutación **HQ→S1→HQ** probada al retirar/restaurar el backend principal, con 15 muestras de respaldo y monitoreo desde S2.
- [x] NOC observó el mismo ciclo de HA HQ→S1→HQ con 22 muestras JSONL, selección principal/restauración, seis servicios `active` y FIB de S1/S2 intacta.
- [x] Scripts con rollback/protección de recursos S05, línea base S02 y redes de gestión conservadas.

### Criterios aún pendientes
- [ ] Definir y ejecutar una prueba independiente de **falla de instancia de servidor** o segundo nodo virtual distinguible de una pausa del proceso; comprobar continuidad, restauración y propiedad.
- [ ] Evaluar si el requisito académico exige **segundo equipo router/switch** o si bastan HA WAN/servidores; implementar únicamente lo exigible o documentar el alcance con evidencia, sin reclamar alta disponibilidad física de la VM única.
- [ ] Conservar pings/HTTP/NOC/FIB durante postchecks de LACP S1/S2 y SDN, sin repetir innecesariamente las pruebas previas.
- [ ] Revisar imágenes, logs y SHA-256; alinear demo con [#105](https://github.com/recm0708/netlab360/issues/105) y NOC [#64](https://github.com/recm0708/netlab360/issues/64).

Referencias: [tablero S05 vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md) y [histórico íntegro de esta issue](https://github.com/recm0708/netlab360/blob/main/docs/gestion/historico-issues/s05-issue-32-antes-de-consolidacion-20261114.md). Estados antiguos no ejecutados en el archivo histórico ya fueron superados por lotes 84–94.
## 14/11/2026 · Lotes 114A-S, 114B, 114C y 114D completados realmente

- [x] **114A-S:** Git a `832b6e1`; dos rondas a gateway HQ `10.70.20.1`, frontal HQ `10.70.20.23`, backend S1 `10.71.20.21` y host S2 `10.72.20.20`: **16/16 paquetes recibidos, 0% pérdida en esas rondas**. Bonds switch/cliente IEEE 802.3ad 2/2; `ens33=.40` GW `.2`, Git limpio. `LOTE114A_S_ESTABILIDAD=OK`.
- [x] **114B:** falla controlada de miembro `s5c1` con watchdog `systemd-run` temporal; switch y cliente pasaron **2/2→1/1→2/2**. Durante 1/1 ping 4/4 destinos y HTTP real `200_BACKEND_HQ`; HA/FIB y puertos S02 conservados. Tras restauración 4/4 ping, VLAN120 PVID untagged, gestión intacta y rescate cancelado. `S05_LACP_HQ_PRUEBA=OK_2_1_2`, `LOTE114B_FALLA_RETORNO=OK`. Esto no demuestra 0 pérdidas durante cada milisegundo de conmutación.
- [x] **114C:** secciones de salida `INICIO_CAPTURA_S05_48/49` a `FIN_CAPTURA` extraídas y revisadas; **no consta confirmación de archivos PNG guardados**, ni importación binaria.
- [x] **114D:** validador selectivo S1/S2 `plan` + `precheck` = OK; candidatas `10.71.20.40` VLAN220 y `10.72.20.40` VLAN320 no asignadas en inventario de 36 direcciones ni responden ICMP desde host VLAN; 3 FRR running, interfaces/VLAN protegidas, NOC/HTTP HA OK; HQ conserva 2/2. `LOTE114D_S1S2_PRECHECK=OK`. La ausencia de respuesta ICMP **no garantiza** globalmente IP libre.
- [ ] **Siguiente:** diseñar y ensayar redundancia independiente de instancia/servidor o equipo según alcance académico. El failover de miembro LACP HQ/S1/S2 ya fue aprobado; no repetirlo ni confundirlo con falla física de equipo.

Evidencia local: `~/netlab360-bootstrap/s05/evidencias/lacp-integracion/30_Estabilidad_PreFailover_HQ.txt`, `25_Falla_Retorno_HQ_2_1_2.txt`, `31_Preparacion_LACP_S1_S2.txt`.
