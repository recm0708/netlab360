# Archivo histórico de issue #5

**Fecha de corte:** 2026-11-14 (Panamá). **Origen:** https://github.com/recm0708/netlab360/issues/5

**Título original:** [S05] Redundancia avanzada, LACP multistream y SDN OVS/Faucet

**Estado al archivar:** open

**Propósito:** preservar el texto íntegro previo a la normalización del tablero S05. Este archivo es histórico; NO usar las tareas antiguas como lista vigente. Consultar el issue original o `docs/gestion/s05-tablero-vigente.md` para el estado actual.

---

## Corte operativo 11/11/2026 · Lotes 91–94 completados; retoque NOC y captura 39 pendientes

**Validación real aportada por el operador:**
- [x] **91**: `main` a `58aebe4`, **76/76 pruebas S05 OK**, contrato monitor `SOLO_LECTURA`, cinco servicios activos, destino unit monitor libre; `LOTE91_NOC_HA=OK`.
- [x] **92**: unit `netlab360-s05-ha-monitor-s2.service` instalada y **active** sin `enable` (namespace S2 requiere arranque de red). JSON desde VLAN320 fresco (edad <=6s), backend HQ/S1/frontal RUNNING, principal HQ; `LOTE92_NOC_HA=OK`.
- [x] **93**: reinicio controlado de **solo NOC**, grafo API con tres servidores HA RUNNING, frontal HQ seleccionado, S1 standby y FIB WAN S1:s1p/S2:s2p intacta; `LOTE93_NOC_HA=OK`.
- [x] **94**: prueba NOC API HQ→S1→HQ con **22 muestras JSONL**, `S05_HA_NOC_CICLO=HQ_S1_HQ_OK`, `S05_HA_NOC_SERVICIOS_RESTAURADOS=OK`, **seis** servicios active, integridad de 6 archivos OK; `LOTE94_NOC_HA=OK`. Salida delimitada de `S05_40`; no es necesario repetir failover para retoques visuales.
- [x] **Revisión visual aportada por el operador**: panel HA correcto pero mostraba fecha ISO UTC `2026-11-11T14:15:50+00:00` mientras reloj superior en formato Panamá; la conexión HTTP principal HQ-frontal era poco visible en vista adicional, rótulo inglés `SERVER`. **Captura `S05_39` aún NO tomada**, se pospone hasta validar nueva vista. NO confundir capturas aportadas de inspección con captura oficial 39.
- [x] **Correcciones hechas directamente en código GitHub, pendientes de `git pull` y refresco del navegador en VM:** formateador compartido `formatPanamaStamp` para fecha local Panamá de HA y reloj principal; nodos `SERVIDOR` más anchos; línea HTTP principal por carril lateral izquierdo, respaldo diagonal discontinua, etiquetas distintivas, mayor margen inferior. 4 nuevos tests `tests/test_s05_ha_ui.py` con verificación de hora real JS y geometría. [CI del commit `a51d492d` OK](https://github.com/recm0708/netlab360/actions/runs/43038684048) (más CI B1–B4 exitosa).
- [ ] **Siguiente operativo:** lotes 95–96 (una PowerShell/SSH, Git sync, tests, restart únicamente NOC, verificar API y Chrome con Ctrl+Shift+R); luego tomar `S05_39_NOC_Servicios_HA_Hora_Panama` con barra HA y diagrama, revisar si carril principal y texto quedan legibles. No apagar/recrear namespaces, no reiniciar exporter ni HTTP, no habilitar units HA al boot.
- [ ] **Después de captura** iniciar precheck LACP multisede de solo lectura (#31), diseñar integración sin bucles en switches S02 ni toques `ens33`; SDN OVS/Faucet (#23) sigue pendiente. Word académico se retomará tras práctica.

## 11/11/2026 · S05 HTTP HA real completada (87–90); integración NOC preparada

**Ejecutado y confirmado por el operador:**
- [x] **Lote 87:** `main` sincronizado a `855809a`, **62/62 pruebas S05 OK**; precheck HTTP 3 IP/puerto libres y FIB principales correcta; `LOTE87_HTTP=OK`.
- [x] **Lote 88:** 3 units systemd HTTP instaladas **y active**, solo en netns S05: `10.70.20.21:8088`, `10.71.20.21:8088`, `10.70.20.23:8080`; `LOTE88_HTTP=OK`. No habilitadas al boot por dependencia de red efímera.
- [x] **Lote 89:** cliente S2 recibió HTTP 200 de ambos backends y frontal, **elección HQ principal**; `LOTE89_HTTP=OK`, captura `S05_37_Servidores_HTTP_y_Frontal_Principal` confirmada.
- [x] **Lote 90:** prueba controlada HQ→S1→HQ, deteniendo exclusivamente backend HQ, **15 muestras HTTP de respaldo correctas**, `S05_HTTP_FALLBACK_VERIFICADO=OK`, `S05_HTTP_RETORNO=OK`, `S05_HTTP_PRUEBA_CICLO_COMPLETO=OK`, FIB S1 `s1p` y S2 `s2p` sin cambios; tres units restituidas; `LOTE90_HTTP_HA=OK`, SHA256 **6/6 archivos**, captura `S05_38_Conmutacion_HTTP_Principal_Respaldo_Retorno` confirmada. Ningún PNG original importado en binario a GitHub.
- [x] **Nuevos componentes NOC versionados y CI aprobada (NO desplegados aún):** `servicios/ha-s05/monitor_http_s2.py`, unit `netlab360-s05-ha-monitor-s2.service` (cliente S2 VLAN320, HTTP real, sin sudo), `inventario/topologia-extensiones-s05.json` con 3 servidores realizados/5 vínculos, NOC con panel selección HTTP y caducidad 6s **SIN DATOS** si fuente obsoleta; `scripts/validacion/s05-ha-noc-ciclo.py` para validar HQ→S1→HQ por NOC con JSONL/rollback. [CI S05 OK](https://github.com/recm0708/netlab360/actions/runs/43034894085), [registro técnico de resultados](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-ha-http-failover-validado.md).
- [ ] **SIGUIENTE en una sola PowerShell/SSH:** Git pull; 62+ nuevas pruebas y sintaxis; verificar 3 units HTTP y S04/NOC activas; `systemctl start` **sin enable** del monitor nuevo; esperar snapshot fresco y comprobar API del NOC tras `systemctl restart netlab360-s05-noc`; capturar nodos HA y selección HQ. Luego prueba NOC controlada y captura/logs. **Nunca ejecutar `s05-ha-red-servicios.py up` otra vez**.
- [ ] Después: integrar LACP en multisede, OVS/Faucet aislado, observabilidad/diagrama actualizado, cierre final pruebas/inventario y evidencias binarias, **luego** Word/PDF maestro por petición del usuario. Milestone S05 abierta; snapshot VMware `NETLAB360_S05_PreLAN_20261110` sin tocar.

## Actualización real S05 — 11/11/2026 · Red HA validada 84–86; HTTP en preparación

- [x] **Lote 84 red HA:** `main` sincronizado en `ff252b9`, **51/51 tests S05**, `S05_HA_RED_PRECHECK=OK_SIN_CAMBIOS`, captura S05_34 delimitada.
- [x] **Lote 85:** red HA implementada y verificada: BACKEND_HQ `nl360-s05-ha-hq` `10.70.20.21/24` VLAN120, BACKEND_S1 `nl360-s05-ha-s1` `10.71.20.21/24` VLAN220, FRONTAL_HQ `nl360-s05-ha-fe` `10.70.20.23/24` VLAN120; tres puertos `veth` S05, `S05_HA_RED_UP=OK`, `S05_HA_RED_STATUS=OK`, S2 llega a los tres, `S05_S02_CONSERVADO=SI`. Captura S05_35 delimitada.
- [x] **Lote 86 ahora sí completado:** el bloque previo se había quedado en Bash `>` por faltar `)`; operador completó el cierre y ejecutó el postcheck real, `S05_HA_PING_10.70.20.21=OK`, `10.71.20.21=OK`, `10.70.20.23=OK`, `S05_HA_OWNER=OK`, `S05_HA_ESTADO=active`, `S05_HA_NAMESPACES=3`, `S05_HA_FIB_S1=s1p`, `S05_HA_FIB_S2=s2p`, NOC/Exporter active, `ens33=192.168.47.40/24` GW `.2`, Git limpio, `LOTE86_POSTCHECK=OK`, manifiesto **6/6 archivos SHA256 OK**, `LOTE86_HA=OK`. El operador **confirmó captura S05_36 tomada**. No repetir `up`, ni borrar/recrear namespaces.
- [x] **Código HTTP HA nuevo en GitHub, NO instalado en VM:** `servicios/ha-s05/http_ha.py` (backend HQ preferido, backend S1 respaldo, frontal HQ con healthcheck y selección de identidad); tres units systemd con `NetworkNamespacePath=/run/netns/nl360-s05-ha-*` y usuario no privilegiado; precheck read-only `scripts/validacion/s05-ha-http-precheck.py`; ensayo de conmutación controlada con restauración en `finally` `scripts/laboratorio/s05-ha-http-failover.py`; tests `tests/test_s05_ha_http.py`. Puertos **solo en netns**: backends TCP 8088, frontal TCP 8080. **Sin exposición en ens33**. systemd units **NO deben habilitarse al boot** hasta definir recreación de namespaces S02/S05 tras reinicio.
- [ ] **Próximo paso operativo:** Git pull, regresión Python S05 y `--check` del HTTP; precheck de tres direcciones/puertos y fuentes FIB, verificar units no instaladas. Luego instalar unidades y `systemctl start` (NO `enable`) de backend HQ, backend S1 y frontal; probar desde S2 retorno `active_backend=BACKEND_HQ` por `http://10.70.20.23:8080/api/v1/service` antes de simular fallas. Después failover controlado y recuperación.
- [ ] **Aún pendiente:** demostrar fallback HTTP real, actualizar NOC solo con nodos verificados, LACP multisede #31, OVS/Faucet #23, pruebas integradas y entrega de evidencias. Mantener milestone S05 abierta. Snapshot VMware manual `NETLAB360_S05_PreLAN_20261110` intacto.

## S05 · Lotes 84–85 ejecutados; lote 86 pendiente por error de sintaxis (11/11/2026)

- [x] **Lote 84 red HA:** Git sincronizado en commit `ff252b9`, **51 pruebas S05 OK**, plan de 3 nodos HA, `S05_HA_RED_PRECHECK=OK_SIN_CAMBIOS`, NOC/FIB S1 `s1p` y S2 `s2p`; `LOTE84_HA=OK`. Evidencia delimitada `INICIO_CAPTURA_S05_34` → `FIN_CAPTURA_S05_34` mostrada en log.
- [x] **Lote 85 red HA:** creados **3 namespaces/puertos exclusivos** `nl360-s05-ha-hq` `10.70.20.21/24` (HQ VLAN120), `nl360-s05-ha-s1` `10.71.20.21/24` (S1 VLAN220), `nl360-s05-ha-fe` `10.70.20.23/24` (HQ VLAN120). `S05_HA_RED_UP=OK`, `S05_HA_RED_STATUS=OK`, S2 alcanza los tres destinos, `S05_GESTION_INTACTA=SI`, `S05_S02_CONSERVADO=SI`, `LOTE85_HA=OK`. Evidencia S05_35 delimitada INICIO→FIN. `S05_HA_SERVIDORES_HTTP=NO_INICIADOS`: **aún NO hay alta disponibilidad HTTP**.
- [ ] **Lote 86 NO EJECUTADO.** El bloque de comandos anterior tenía **un paréntesis final `)` faltante**: Bash mostró prompt secundario `>` y quedó esperando cierre, no estaba bloqueado ni ejecutó postcheck. Se pulsó `Ctrl+C` una vez, luego se pegó de nuevo y quedó en `>`. Resolver completando `)` en prompt actual o cancelando y ejecutando versión corregida. **No volver a ejecutar `up` ni borrar/recrear la red HA.**
- [ ] **Captura S05_36 pendiente** hasta obtener `INICIO_CAPTURA_S05_36` → `FIN_CAPTURA_S05_36` de postcheck real y `LOTE86_HA=OK`. No afirmar que la captura existe.
- [ ] Tras L86, desplegar backends HTTP y frontal con healthcheck/failover y registrar NOC dinámicamente, sin modificar `ens33` ni snapshot manual VMware.

## Corte verificado 11/11/2026 — Supervisión persistente cerrada; iniciar HA

- [x] **Lote 84R-L completado tras cerrar y reabrir SSH normal con túnel 9130 integrado:** `systemctl is-active netlab360-s04-exporter` y `netlab360-s05-noc` => **active/active**; `is-enabled` => **enabled/enabled**.
- [x] **API y FIB supervivientes a desconexión:** `S05_SERVICIOS_PERSISTENTES=OK`; FIB S1 `s1p` / `10.78.0.2` y S2 `s2p` / `10.78.0.10`; `ens33=192.168.47.40/24`, default `192.168.47.2`; `LOTE84R_L=OK`.
- [x] **Sincronización Git en VM:** `8fde8ea → 404e730`, solo documentación académica; `## main...origin/main`, árbol limpio. La recuperación de SSH y de sudo interactivo queda **CERRADA**; no volver a abrir servidores manualmente, iniciar tmux, ni recrear FRR.
- [x] **Corrección preventiva de VLAN HA en GitHub**: eliminación opcional de VID 1 al insertar nuevos puertos de acceso (equivalente a S02), más prueba de regresión; revisión CI en curso. No se ha ejecutado `up` HA todavía.
- [ ] **Lotes siguientes (HA de servicios)**: sincronizar `main`, validación automática sin conteo fijo, `plan/precheck` de red HA, desplegar únicamente tres netns/puertos nuevos si ambos prechecks OK, realizar `status`, inventario IP/gateway/VLAN/ICMP, evidencia S05_34–36. Después HTTP backends+frontal, failover HTTP, integración NOC. **No confundir 84R-L (cerrado) con HA original 84–86 (pendientes).**
- [ ] **Cierre S05 pendiente** por HA HTTP real (#32), LACP multisede (#31), OVS/Faucet (#23), grafo NOC actualizado (#64), importación de capturas binarios, pruebas globales. Por petición del operador **priorizar práctica; escritura académica de S05 se retomará al cerrar las implementaciones**; guion ya preparado en `docs/academico/s05-guion-de-actualizacion-del-informe.md`.
- [ ] Snapshot manual VMware `NETLAB360_S05_PreLAN_20261110` intacto y fuera de comandos; no borrar/recrear VMs. Una PowerShell/SSH con `-L 9130` basta.

## CORTE VALIDADO 11/11/2026 — servicios systemd S04/NOC ACTIVOS y 50 pruebas S05

- [x] **Regresión S05 ampliada:** el operador hizo `git pull --ff-only` de `2a3f899` a `8fde8ea`; **50 pruebas S05 pasaron**, incluyendo seis pruebas del observador seguro. El lote `84R-H` dejó de avanzar en `grep -Fq 'Ran 46 tests'`; no es un fallo de las pruebas sino un conteo desactualizado. Sus verificaciones posteriores de binarios, archivos destino y puertos no se ejecutaron en esa pasada; resultados equivalentes posteriores confirman instalación y APIs.
- [x] **Lote 84R-I ejecutado en VM**: helper root-owned instalado en `/usr/local/libexec/netlab360-observer`, `sudoers` limitado a comando exacto, `sudo visudo -cf` da `parsed OK`; `sudo -n ... snapshot` verifica 3 routers y FIB S1 `s1p/10.78.0.2`, S2 `s2p/10.78.0.10`; `S05_OBSERVADOR_PRIVILEGIADO=OK`, `LOTE84R_I=OK`.
- [x] **Lote 84R-J ejecutado en VM**: dos units `netlab360-s04-exporter.service` y `netlab360-s05-noc.service` instaladas, habilitadas y **ambas active**. API S04 `source_ok=True`, `topology=active`; NOC `telemetry.available=True`, `routing.available=True`, FIB S1/S2 principal; `S05_SERVICIOS_SYSTEMD=OK`, `LOTE84R_J=OK`.
- [ ] **Prueba adicional pendiente para declarar independencia de SSH:** salir de SSH de forma normal, reconectar **una sola** PowerShell con `-L 9130` integrado, validar `systemctl is-active`, puerto 9110/9130, S04/NOC/FIB y journalctl, sin ejecutar manualmente Python ni `tmux`.
- [ ] **Lotes HA originales 84–86 siguen pendientes**, con state HA ausente en último inventario. Primero persistencia NOC; luego `plan/precheck`, `up` y `status` de red HA. No modificar snapshots ni FRR.
- [x] **Comenzado el guion académico S05 para el Word único**, con resultados ya defendibles en capítulos 5–7: [Guion editorial S05](https://github.com/recm0708/netlab360/blob/main/docs/academico/s05-guion-de-actualizacion-del-informe.md). **No afirmar que se editó el Word original** ni que HA/SDN están operativos.

Las secciones posteriores más antiguas son **historial** y sus casillas de instalación aún pendientes quedaron superadas por las pruebas 84R-I/J aquí citadas. Milestone S05 sigue ABIERTA.

## 11/11/2026 · Reinicio limpio VALIDADO y hardening NOC preparado en GitHub

- [x] **Resultado real de VM confirmado por usuario:** `REINICIO_LIMPIO_PREPARADO=OK`. Exporter 9110 ya estaba detenido; NOC antiguo PID **564662** identidad `servicios/topologia-s05/app.py --serve --port 9130` verificada y detenido por SIGTERM. Ambos puertos **libres** después; contenedores FRR HQ/S1/S2 **Up 12 hours**, `ens33 192.168.47.40/24`, default `192.168.47.2`, Git limpio; `HA_STATE=AUSENTE`. **No se alteró Docker, OSPF, interfaces ni snapshot manual**.
- [x] **Solución persistente y de privilegios mínimos creada y versionada, pero NO instalada en VM:** [procedimiento systemd](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-servicios-systemd-sin-tmux.md), `scripts/operacion/s05-observador-privilegiado.py`, dos units `servicios/systemd/netlab360-s04-exporter.service` y `netlab360-s05-noc.service`. Ejecutan Python web como usuario normal, 127.0.0.1:9110/9130, y consultan un helper root-owned que solo admite `snapshot` de 3 contenedores y rutas fijas. El cambio de permiso se limitará a un único comando exacto sudoers, **sin Docker group, NOPASSWD ALL ni servidor HTTP root**.
- [x] **Integración de código y CI**: S04 exporter y NOC FIB adaptados para leer snapshot estructurado con `NETLAB360_PRIV_OBSERVER`; seis tests offline y workflow S05 ampliado. CI [run 43024220132](https://github.com/recm0708/netlab360/actions/runs/43024220132) éxito; **CI no sustituye instalación/prueba real del entorno**.
- [ ] **Próxima acción, una sola PowerShell y SSH normal:** Git pull (si limpio), auditar preflight de rutas/units/puertos/binarios existentes, ejecutar pruebas. No entrar a tmux; no generar túneles duplicados; no iniciar 9110/9130 manualmente.
- [ ] Instalar helper root:root 0755, sudoers de comando exacto 0440 (con `visudo -cf`), probar snapshot. Luego instalar dos units root:root 0644, habilitarlas secuencialmente y verificar API S04/FIB y continuidad tras desconectar SSH. Conservar logs en TXT y journalctl.
- [ ] **Lotes HA 84/85/86 NO ejecutados**. No crear `veth`/namespaces hasta que supervisor y FIB sean confiables. Estado HA ausente, última prueba real HA = lotes 81–83.

## Corte operacional: reinicio ordenado de SSH solicitado por operador (11/11/2026)

- [x] El operador confirmó que abrir sesiones interactivas con `tmux new-session` ocultó el historial visible de la terminal y generó confusión; se reconoce que el procedimiento anterior no fue apropiado para su flujo de trabajo. **No volver a indicar creación/entrada de sesiones tmux interactivas**.
- [x] Último diagnóstico factual: visor NOC `9130` escuchando (PID **564662**); exporter S04 `9110` **sin listener** en la última prueba `84R-G`, produjo `ConnectionRefusedError`; SSH `-N -L` informó `channel 2 ... Connection refused`. T1/T3/T4 y túneles duplicados provocaron confusión operativa. No hay evidencia de caída FRR o de `ens33`.
- [ ] **Acción siguiente estricta:** cerrar **todas las conexiones SSH y túneles de Windows** sin apagar VM ni detener sshd; abrir **una PowerShell 7 nueva** y **un SSH normal** para auditar y apagar *solo* los procesos de observabilidad `app.py --serve --port 9130` y `s04_exporter_multisede.py --serve --port 9110` que sigan vivos, con identificación de PID y propietario. **No detener Docker, FRR, OSPF, netns S02, S04 datos ni snapshots**. No usar tmux interactivo ni `clear`.
- [ ] Tras confirmar puertos 9110/9130 libres y red `ens33` correcta, diseñar servicios estables desacoplados de SSH con permisos mínimos de lectura, sin depender de credenciales `sudo -n` de TTY; **no prometer FIB disponible en procesos desatendidos mientras no exista colector autorizado**. Evitar nohup/tmux sin explicar su efecto o comprobar los privilegios.
- [ ] **Lotes 84–86 HA NO ejecutados.** Mantener estado de milestone S05 e issue #32 pendientes; último avance real de HA son lotes 81–83, 40/40 pruebas y PNG 32/33. Cualquier instrucción de despliegue HA debe esperar auditoría y recuperación estable del NOC.

## Corte S05 red HA preparada, todavía NO desplegada — 11/11/2026

- [x] Capturas PNG S05_32 (JSONL 119 muestras) y S05_33 (precheck HA) recibidas y verificadas: marcadores INICIO/FIN legibles. **No están incorporadas en binario a GitHub**.
- [x] Lote 81: **40/40 pruebas S05**; lote 82: ownership S02, VLAN 120/220/320, IP HA sin asignación observada y fuentes S04/FIB OK; lote 83: S2→HQ/S1 servicios **2/2** paquetes por destino, VLAN tagging verificado, ens33/Git limpios.
- [x] **Código de red HA listo, sin desplegar:** `scripts/laboratorio/s05-ha-red-servicios.py` con `plan/precheck/up/status/down`, control de ownership `NETLAB360_S05_HA_RED_V1`, tres netns/puertos nuevos aislados, verificación ICMP y rollback limitado. [CI S05 exitosa](https://github.com/recm0708/netlab360/actions/runs/42974399828); cobertura `tests/test_s05_ha_red.py`.
- [ ] Ejecutar lote 84 plan/precheck, lote 85 creación de red HA únicamente si precheck OK, lote 86 status/postcheck. **Aún no hay backends HTTP, frontal, failover HTTP ni nuevos nodos confirmados en NOC.**
- [ ] Posteriores: HTTP HA real, observación/control/rollback, integración NOC de nodos observados, #31 LACP, #23 OVS/Faucet, entrega PNG binaria. Milestone S05 permanece abierta. Snapshot manual VMware no tocar.

## Avance validado 11/11/2026 — Lotes 81–83 y PNG 32/33

- [x] **Lote 81:** `git pull --ff-only` a commit `2a3f899`; sintaxis de `s05-ha-precheck.py` OK; **40/40 tests S05** correctos (incluye 4 pruebas HA); Git limpio.
- [x] **Lote 82:** `S05_HA_PRECHECK=OK_DISENO_PENDIENTE` sin cambios de infraestructura; ownership `NETLAB360_S05`, 12 namespaces S02, routers HQ/S1/S2, VLAN HQ120/S1220/S2320, hosts `.20` verificados; candidatas `10.70.20.21`, `10.71.20.21`, `10.70.20.23` sin asignación observada; S04/NOC y FIB principales sanas. **La inspección no supone reserva exclusiva ni autoriza aún crear equipos HA.**
- [x] **Lote 83:** cliente `nl360-s02-h-s2-320` alcanzó por ICMP a `10.70.20.20` (HQ) y `10.71.20.20` (S1), ambos **2/2 paquetes**, VLAN filtering inspeccionado en switches existentes HQ/S1 y sus puertos `a120/a220` en acceso; `ens33` y Git intactos.
- [x] **Evidencia PNG `S05_32_Validacion_JSONL_Ciclo_Conmutacion_S1.png` y `S05_33_Precheck_Alta_Disponibilidad.png`** aportadas y revisadas: se ven los encabezados INICIO/FIN y los verificadores. Son capturas recibidas en el chat; **NO son archivos binarios importados al repositorio**.
- [ ] **Próximo paso:** preparar despliegue HA aislado mediante puertos `veth` exclusivos por VLAN, healthcheck HTTP y rollback S05, con CI y precheck; los servidores HA **aún no están operativos**.
- [ ] **No tocar:** `ens33` (`192.168.47.40/24`, GW `.2`), FRR/docker, puertos `tr-sw/trunk0/br0`, exporter 9110, NOC 9130, snapshot manual `NETLAB360_S05_PreLAN_20261110`.

**CI verificada:** workflow [NETLAB360 S05 · run 42973137959](https://github.com/recm0708/netlab360/actions/runs/42973137959) concluyó `success` al incorporar `s05-ha-precheck.py` y cuatro pruebas unitarias. La CI **no** sustituye ejecutar `--check` dentro de la VM; aún no hay nodos HA ni IPs nuevas asignadas.

## Estado confirmado 11/11/2026 · Lotes 79/80 cerrados y HA en diseño

- [x] **Lote 79:** JSONL validado con **119 muestras (55 PRINCIPAL, 64 RESPALDO)**, secuencia FIB `s1p/10.78.0.2→s1b/10.78.0.6→s1p/10.78.0.2`, concordancia entre observador/simulador/postcheck, manifiesto SHA-256 **4/4 archivos OK** y TAR técnico `NETLAB360_S05_NOC_FAILOVER_S1_20261111.tar.gz` generado en VM.
- [x] **Lote 80:** 8 vCPU, ~13 GiB RAM disponible, 132 GiB de disco libre, **tres FRR en Docker (network_mode:none)**, **12 namespaces S02**, **tres VLAN de servicios activas** HQ 120 = `10.70.20.20/24`, S1 220 = `10.71.20.20/24`, S2 320 = `10.72.20.20/24`; sistemas S04/NOC escuchan únicamente en localhost 9110/9130, ens33 .40/24 y gateway .2 sin cambio, Git limpio.
- [x] **Diseño HA inicial sin despliegue:** [arquitectura candidata de dos backends HQ/S1 y frontal HQ](https://github.com/recm0708/netlab360/blob/main/docs/diseno/s05-ha-servicios-multisede.md); script `scripts/validacion/s05-ha-precheck.py --check` versión read-only y cuatro pruebas unitarias nuevas.
- [ ] **Falta confirmación visual de S05_32:** la salida muestra `INICIO_CAPTURA_S05_32` → `FIN_CAPTURA_S05_32` y auditoría OK, pero el operador aún no confirmó guardar la imagen.
- [ ] **Próxima validación previa a cualquier HA:** ejecutar el precheck nuevo en VM, revisar IPAM/VLAN/ownership/IP propuestas `HQ:10.70.20.21,10.70.20.23` y `S1:10.71.20.21`, confirmar sin colisiones y definir rollback. No considerar reservas definitivas hasta auditoría real.
- [ ] **Pendientes de fase 5:** HA operativa probada (#32), integración LACP (#31), SDN OVS/Faucet (#23), evidencias binarios PNG aún no importadas y cierre académico. **Milestone S05 permanece abierta.**
- [x] **NO repetir failover S1**: ciclo ya demostrado por NOC y dos salidas, no hace falta interferir en FRR por captar un inspector en la imagen 31.

Las secciones anteriores quedan como historial de ejecución y diagnóstico, no como pendientes vigentes si contradicen este corte. Snapshot `NETLAB360_S05_PreLAN_20261110` manual, sin cambios.

## S05 — Conmutación observada S1 completada (11/11/2026)

- [x] **Lote 75:** Git `main` sincronizado, cambio visual `ACTIVO/INACTIVO/SIN DATOS` presente, **36/36 tests S05 OK**, `S05_NOC_PRECHECK=OK_SIN_CAMBIOS`.
- [x] **Lote 76 / observador solo lectura:** `S05_NOC_OBSERVADOR_LISTO=S1`, **119 muestras**, `PRINCIPAL→RESPALDO→PRINCIPAL`, FIB `s1p→s1b→s1p`, siguiente salto `10.78.0.2→10.78.0.6→10.78.0.2`, `S05_NOC_CICLO_COMPLETO=OK`.
- [x] **Lote 77 / conmutación limitada:** `S02_S1_WAN_PRINCIPAL=DOWN`, respaldo bidireccional FIB comprobado, `S02_S1_OTRA_SEDE_ESTABLE=SI`, ventana de observación de **25s**, restauración primaria y `S02_S1_PRUEBA_COMPLETA=OK`.
- [x] **Lote 78 / retorno:** FIB HQ S1 `s1p/10.78.0.2`, S2 `s2p/10.78.0.10`, `ens33 192.168.47.40/24`, default `.2`, Git limpio; `LOTE78_POSTCHECK=OK`.
- [x] **Capturas S05_29 y S05_30** recibidas y aceptadas. **S05_31** aceptada como representación visual de cambio principal rojo/respaldo azul; **no muestra inspector** y se complementa con JSONL/log de FIB para acreditar `10.78.0.6`.
- [ ] **Pendiente auditoría de archivos locales:** JSONL `S05_NOC_S1_OBSERVACION_20261111T052859Z.jsonl` más tres TXT 10/11/12, manifiesto SHA-256 portable, TAR técnico y carga de PNG a repositorio; **no afirmar que ya se importaron**.
- [ ] **Continuación S05:** diseñar HA de servidor/equipo (#32) con precheck IPAM y recursos, LACP multisede experimental (#31), SDN OVS/Faucet aislado (#23). S2 ya tiene failover de consola validado; NOC S2 simétrico sería evidencia complementaria, no se ha ejecutado durante este corte.

Bitácora [conmutación observada S1 validada](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-observacion-failover-s1-validada.md). Milestone S05 ABIERTA y snapshot manual VMware `NETLAB360_S05_PreLAN_20261110` sin cambios. Las secciones antiguas más abajo documentan *el estado histórico previo a esta ejecución*.

## Cierre de recuperación NOC y revisión de capturas — 11/11/2026

- [x] **Lotes 72R-D/E/F recuperados y comprobados en VM:** NOC T1 reiniciado (PID `449431`, 9130), exporter T4 mantenido (PID `425166`, 9110), túnel T2 PowerShell operativo. S04 `source_ok=True`, `topology=active`, `errors=[]`; NOC `routing.available=True`, `source_warnings=[]`, FIB S1=`s1p/10.78.0.2`, S2=`s2p/10.78.0.10`, dos muestras correctas, `S05_NOC_PRECHECK=OK_SIN_CAMBIOS`. Gestión `ens33` intacta.
- [x] **Cambio estético versionado:** insignia de sede pasa de `RTR: EN EJECUCIÓN/DETENIDO/SIN DATOS` a `ACTIVO/INACTIVO/SIN DATOS`, con recuadro de 94 px; rojo reservado a desconexión realmente observada, gris a estado desconocido. Pruebas CI S05 y regresión aprobadas.
- [x] **PNG S05_28 validado**; renombrar `S05_28_NOC_Rutas_FIB_Principales(1)` a `S05_28_NOC_Rutas_FIB_Principales`. Capturas generales y seleccionado HQ–S1 aportadas; S05_24–27 auditadas previamente. La versión visual antigua de 28 es técnicamente válida.
- [ ] **Capturas oficiales pendientes:** S05_29 (mapa+inspector HQ–S1 incluyendo FIB next-hop `10.78.0.2`) y S05_30 (leyenda de colores completa en una toma); S05_31 solo durante respaldo S1 realmente elegido y observable en NOC.
- [ ] **Demostración de failover visual pendiente, sin cambios aún:** T5 observador con precheck confiable, T6 failover acotado 25s, validar FIB S1 principal→respaldo→principal y gestión intacta. **No ejecutar T6 si T5 no publica `S05_NOC_OBSERVADOR_LISTO=S1`.**
- [ ] **Control de evidencias:** PNG aún en equipo del operador, no incorporados en binario ni firmados en GitHub; luego importar con SHA256. No hacer informes de capacidad LACP física a partir de throughput virtual.

Continuación documentada: [auditoría S05 de cuatro PNG](https://github.com/recm0708/netlab360/blob/main/docs/evidencias/10-auditoria-s05-png-y-capturas-pendientes-2026-11-11.md) y [REANUDAR-AQUI](https://github.com/recm0708/netlab360/blob/main/docs/REANUDAR-AQUI.md). El milestone S05 permanece abierto.

## Continuidad operativa NOC — 11/11/2026 (terminales y fuentes)

- [x] Se verificó que FRR HQ/S1/S2 siguen activos, gestión `ens33=192.168.47.40/24` intacta y NOC 9130 existente (PID 334882) con **S04 9110 detenido** inicialmente.
- [x] Exporter S04 9110 **recuperado** en T4: `source_ok=True`, topología `active`.
- [x] **Incidencia histórica resuelta:** NOC anterior sin FIB por credenciales de su proceso; T1 reinició visor con sudo propio, nueva FIB y fuente S04 verificadas en lotes 72R-D/E.
- [x] Añadido [runbook de terminales T1–T6](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-mapa-terminales-y-recuperacion-noc.md), con diagnósticos exactos, servicios de larga duración, túnel Windows, observador y simulador en sesiones separadas.
- [ ] No repetir failover real S1 hasta observador confiable y precheck sano; incorporar a la arquitectura futura observador persistente de mínimos privilegios (la caché `sudo -n` no es fiable a largo plazo).
- [ ] S05 continúa pendiente HA, SDN OVS/Faucet, LACP integrado, failover gráfico y cierre documental. Snapshot manual `NETLAB360_S05_PreLAN_20261110` preservada.


## Incidencia del observador en S05 — 11/11/2026 (sin falla WAN inducida)

- [x] Lotes **70 y 71** validados: **36/36 pruebas S05**, JS y Python OK, S04 `source_ok=True`, NOC `routing.available=True` y FIB HQ S1 `s1p` / S2 `s2p` correctas; gestión `ens33=192.168.47.40/24` conservada.
- [ ] Lote **72** detuvo el observador durante el **precheck de fuente** (`S04=False`, `FIB=False`, `topology=unknown`), posiblemente vinculado a cierre/restablecimiento de terminales SSH o caché `sudo -n` del proceso de observabilidad. El diagnóstico definitivo exige consultar estado de procesos, puertos y errores reales del exporter. **El lote 73 nunca se ejecutó; no se bajó ninguna WAN**.
- [x] **Recuperación de fuente 9110/9130 completa**, con S1/S2 FIB principal y túnel Windows válidos. **La prueba de respaldo S1 y captura S05_31 continúan pendientes en nueva casilla.**

Ver [#64](https://github.com/recm0708/netlab360/issues/64) y [REANUDAR-AQUI](https://github.com/recm0708/netlab360/blob/main/docs/REANUDAR-AQUI.md) para el registro y las instrucciones. Milestone S05 continúa abierto.

## Corte operativo — 11/11/2026: NOC V7.2 aprobado, conmutación observable preparada

- [x] Diseño de topología multisede V7.2 aprobado visualmente por el operador, con green-lima de selección, respaldo FIB distinguido, inspector limpio y código de colores. V7.2 en VM alcanzó **28/28 pruebas correctas**; el lote de shell se detuvo por una búsqueda impropia de stdout capturada, sin invalidar las pruebas.
- [x] Redacción de la consola actualizada en GitHub a estilo NOC empresarial: supervisión operativa contextual, estados observados en español e integraciones registradas sin prometer funcionalidades no implementadas.
- [x] Extensión read-only para evidencia del failover NOC `scripts/validacion/s05-observar-conmutacion-noc.py` y ventana de 0–30s agregada al simulador WAN preexistente, restaurado por `finally`; tests nuevos y CI incluidos. **No ejecutado aún en VM**; total esperado **36/36 tests**.
- [ ] Sincronizar Git y superar 36/36 + sintaxis JS/API + precheck en S1; observar S1 principal→respaldo→principal desde API y pantalla con 20s de ventana, sin tocar otras sedes ni `ens33`. Validar recuperación e identificar evidencias oficiales.
- [ ] Después avanzar a redundancia de equipos/servicios [#32](https://github.com/recm0708/netlab360/issues/32), SDN OVS/Faucet [#23](https://github.com/recm0708/netlab360/issues/23) e integración/caracterización LACP [#31](https://github.com/recm0708/netlab360/issues/31). Mantener milestone **S05 ABIERTO**, sin afirmar 100%.

Bitácora para continuar si cambia el chat: [REANUDAR-AQUI](https://github.com/recm0708/netlab360/blob/main/docs/REANUDAR-AQUI.md) y [sesión de NOC/observación](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-noc-v72-y-preparacion-conmutacion.md). Instantánea VMware manual `NETLAB360_S05_PreLAN_20261110`: **no operar sobre ella desde terminal**.

# Fase 5 — Alta disponibilidad y SDN acotada

**Estado operativo al 11/11/2026:** LACP P1/P1B medidos, tres sedes activas con 9 VLAN/hosts y WAN OSPF primaria/respaldo comprobada por failover de S1 y S2. **Pendientes de aceptación S05:** HA de equipos/servicios, SDN OVS/Faucet, NOC FIB/OSPF en vivo, correlación de tráfico, cierre experimental LACP y entrega documental. El fallo de enlace no equivale a HA de equipos.

- [x] LACP IEEE 802.3ad con dos miembros, falla 2→1→2 y HTTP continuo, **solo en escenario experimental inicial**.
- [x] Medir LACP P1/P1B: 1/8 flujos, reparto por miembros, 2→1→2, comparación virtual CPU-limitada y retransmisiones; resultados y límites en [#31](https://github.com/recm0708/netlab360/issues/31).
- [ ] Completar caracterización experimental de capacidad y vínculo al escenario multisede; las tasas P1B no representan capacidad física.
- [ ] Integrar redundancia virtual de routers/switches/servidores, fallas y recuperación de equipos, diferenciando dominios físicos y virtuales [#32](https://github.com/recm0708/netlab360/issues/32).
- [ ] Prueba acotada de OVS/Faucet, segmentación/ACL y protección contra bucles [#23](https://github.com/recm0708/netlab360/issues/23).
- [x] Evaluar WireGuard/4.ª sede: **descartados del alcance obligatorio de S05** por bajo beneficio frente a las tres sedes ya probadas, SDN/HA y límite de recursos; [#24](https://github.com/recm0708/netlab360/issues/24) cerrado como *not planned*, no implementado.
- [ ] **Cierre documental:** capturas oficiales S05_29/30 y conmutación NOC, hashes/manifest y análisis en informe. La evidencia S05_24–28 ya fue revisada, pero no está incorporada en binario a GitHub.

**No bloquea fase 2**, cuyo núcleo multisede ya superó sus verificaciones. Conservar TAR externo separado del Word.

## Preparación operativa P0 — 10/11/2026

- Script de **auditoría sin cambios** versionado: [`scripts/validacion/s05-precheck-solo-lectura.sh`](https://github.com/recm0708/netlab360/blob/main/scripts/validacion/s05-precheck-solo-lectura.sh).
- Ejecutado desde la VM original el **10/11/2026** después de sincronizar Git: **0 fallos**, IP/GW/Git correctos, SQLite S04 `quick_check=ok`, servicios principales activos. Dos capturas P0 confirmadas por el operador.
- Mantenimiento seguro Ubuntu/kernel/Snap completado y validado tras reinicio; [registro técnico](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-mantenimiento-precheck.md). El aviso del precheck es el socket Docker sin acceso de usuario corriente; Docker se validó con `sudo`. **No se considera completa ninguna casilla de implementación avanzada o pruebas LACP/HA/SDN S05.**
- El precheck no alteró red, FRR, Docker, máquinas virtuales ni credenciales. El [piloto P1 LACP multistream acotado](https://github.com/recm0708/netlab360/blob/main/scripts/laboratorio/s05-lacp-multistream-piloto.sh) **sí se ejecutó el 10/11/2026**, con 0 fallos de ejecución, 2→1→2 enlaces y limpieza correcta. El resultado se documentó en [informe técnico S05/P1](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-lacp-multistream-piloto-validado.md). El límite de 120 Mb/s por flujo no permite deducir capacidad máxima y se observaron 553 retransmisiones durante la falla. La aceptación general de S05 y sus casillas de capacidad/integración/HA/SDN sigue pendiente.

## Progreso adicional S05/P1B y NOC — 10/11/2026

- **P1B ejecutado y validado:** [resultados técnicos](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-lacp-p1b-capacidad-validada.md), 4 escenarios sin `-b`, 2→1→2, entre 70,21 y 127,39 Gb/s virtuales bajo afinidad de CPU, sin inferir capacidad física. Cinco capturas tomadas (pendientes de recibir/auditar). Issue #31 conserva replicación experimental e integración.
- **Topología interactiva preparada en código:** [visor S05](https://github.com/recm0708/netlab360/tree/main/servicios/topologia-s05) representa las tres sedes, equipos y enlaces del IPAM, separa `candidate` de observado y actualiza estados sin escribir en infraestructura. **Todavía no probado en la VM ni capturado**; sin telemetría S04 muestra `UNKNOWN`. Issue #64 sigue abierta.

## Requisito nuevo de visualización avanzada — 27/10/2026

- [ ] [Issue #64](https://github.com/recm0708/netlab360/issues/64): grafo web multisede actualizado por telemetría con routers, switches, WAN primaria/respaldo, 9 VLAN/hosts; color primario sano/backup activo/degradado/fallo/UNKNOWN y animación de tráfico solo cuando existan contadores. En S05 primero validar red/HA/SDN propia y después integrar representación visual, sin frenar cierre de S04 ni duplicar alertas.


## Avance acreditado 11/11/2026 — failover completo de las cuatro WAN

- [x] 3 FRR, 3 switches, 9 VLAN/hosts, 4 enlaces (2 principales + 2 respaldos); OSPF FULL 4/2/2, FIB principales `s1p/s2p`; 9/9 gateways y 3/3 comunicaciones intersede.
- [x] **Failover S1:** `s1p → s1b → s1p` confirmado por FIB en ambos extremos, ICMP y control de otra sede; `LOTE57_FAILOVER_S1=OK`.
- [x] **Failover S2:** `s2p → s2b → s2p` confirmado por FIB, ICMP y control de otra sede; `LOTE58_FAILOVER_S2=OK`.
- [x] Postcheck FIB, 2/2 pings HQ→S1 y HQ→S2 sin pérdida **después** de la recuperación, gestión intacta; `LOTE59_POSTCHECK=OK`. El operador reporta las capturas `S05_24/25/26` tomadas, originales pendientes de recepción. [Bitácora técnica](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-failover-wan-s1-s2-verificado.md).
- [ ] Cierre de aceptación avanzada LACP con evidencia original/estadística e integración controlada multisede.
- [ ] Ensayo HA real de equipo/servidor distinto de fallos de interfaz; completar [#32](https://github.com/recm0708/netlab360/issues/32).
- [ ] Implementación y validación de OVS/Faucet bajo aislamiento; completar [#23](https://github.com/recm0708/netlab360/issues/23).
- [x] Extensión NOC V7/V7.2 implementada: lectura **FIB real** de HQ con estados selected/standby/unavailable/unknown y telemetría S04, sin afirmar tráfico medido. **Pendiente la prueba dinámica de respaldo azul y retorno**, registrada en [#64](https://github.com/recm0708/netlab360/issues/64).
- [ ] Incorporar PNG/JSON/log con manifiestos SHA-256 y actualizar informe y demostración S05.

**El milestone S05 no se cierra** por las funciones aún no demostradas. OpenTofu de proveedores externos [#17](https://github.com/recm0708/netlab360/issues/17) es ampliación reprogramada a S08 condicionada a recursos, no resultado de S05.


## Mejora de usabilidad NOC V7.1 — 11/11/2026

- [x] Defecto visual identificado en captura preliminar S05_29: la selección del enlace HQ-S1 principal mostraba inspector FIB correcto, pero el circuito seguía verde sin contraste suficiente frente al resto.
- [x] Se versionó corrección **exclusivamente visual**: halo violeta en selección de ruta, etiqueta, inspector y dispositivos; paleta FIB principal verde, backup elegido azul, standby gris discontinuo, admin DOWN rojo, sin datos gris. Leyenda diferencia selección humana de estado operativo. CI de topología y regresión GitHub en verde.
- [x] V7.1 sincronizada y probada **25/25 en VM**, pero su diseño violeta fue rechazado y sustituido por V7.2. **No usar capturas violetas como evidencia final**; S05_29 espera versión V7.2.
- [ ] Posteriormente realizar prueba gráfica controlada durante conmutación S1/S2 antes de considerar completa la observabilidad dinámica.

## Verificación NOC V7 sobre VM real — 11/11/2026

- [x] Lote 60: 24/24 tests S05, JS OK, S04 exporter confiable activo, FIB HQ observable y red Git intacta (`LOTE60_NOC_V7=OK`).
- [x] Lote 62/captura S05_27: primarias HQ→S1/HQ→S2 `selected`, respaldos `standby`, next hops 10.78.0.2 y 10.78.0.10, sin atribuir tráfico real (`traffic_measured=false`).
- [x] Capturas recibidas y revisadas S05_24–28, incluida S05_28 vista completa del mapa con primarias verdes y respaldos discontinuos. Faltan S05_29 (inspector de ruta) y prueba dinámica en NOC durante failover.
- [ ] Cerrar observabilidad visual de failover y agregar hashes/originales de capturas al repositorio; luego avanzar a HA real de equipos/servicios y OVS/Faucet.

## V7.2 — Validación visual de la fase

- [x] Propuesta visual V7.1 probada en VM (25/25 pruebas correctas) y retroalimentación del operador incorporada: se elimina el halo violeta y el recuadro del inspector.
- [x] Versión V7.2 implementada en GitHub: selección verde lima independiente del estado real, clic reversible en enlaces y equipos, panel limpio, código de colores agrupado y etiquetas en español. Pruebas unitarias y de interacción JS añadidas (28 esperadas).
- [x] V7.2 sincronizada en VM y **28/28 tests aprobados**, con captura preliminar que el operador aceptó visualmente (resaltado verde lima, inspector FIB). **Pendiente en casilla separada** la captura oficial S05_29 y demostrar el failover dinámico en NOC.
- [ ] HA real de equipos/servicios, OVS/Faucet, LACP integrado y consolidación final siguen pendientes. El milestone S05 se mantiene abierto.

