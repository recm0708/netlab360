# Archivo histórico de issue #64

**Fecha de corte:** 2026-11-14 (Panamá). **Origen:** https://github.com/recm0708/netlab360/issues/64

**Título original:** [S05] Topología interactiva NOC: WAN primaria/respaldo, nodos, VLAN y tráfico verificado

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

## Avance validado 11/11/2026 — Lotes 81–83 y PNG 32/33

- [x] **Lote 81:** `git pull --ff-only` a commit `2a3f899`; sintaxis de `s05-ha-precheck.py` OK; **40/40 tests S05** correctos (incluye 4 pruebas HA); Git limpio.
- [x] **Lote 82:** `S05_HA_PRECHECK=OK_DISENO_PENDIENTE` sin cambios de infraestructura; ownership `NETLAB360_S05`, 12 namespaces S02, routers HQ/S1/S2, VLAN HQ120/S1220/S2320, hosts `.20` verificados; candidatas `10.70.20.21`, `10.71.20.21`, `10.70.20.23` sin asignación observada; S04/NOC y FIB principales sanas. **La inspección no supone reserva exclusiva ni autoriza aún crear equipos HA.**
- [x] **Lote 83:** cliente `nl360-s02-h-s2-320` alcanzó por ICMP a `10.70.20.20` (HQ) y `10.71.20.20` (S1), ambos **2/2 paquetes**, VLAN filtering inspeccionado en switches existentes HQ/S1 y sus puertos `a120/a220` en acceso; `ens33` y Git intactos.
- [x] **Evidencia PNG `S05_32_Validacion_JSONL_Ciclo_Conmutacion_S1.png` y `S05_33_Precheck_Alta_Disponibilidad.png`** aportadas y revisadas: se ven los encabezados INICIO/FIN y los verificadores. Son capturas recibidas en el chat; **NO son archivos binarios importados al repositorio**.
- [ ] **Próximo paso:** preparar despliegue HA aislado mediante puertos `veth` exclusivos por VLAN, healthcheck HTTP y rollback S05, con CI y precheck; los servidores HA **aún no están operativos**.
- [ ] **No tocar:** `ens33` (`192.168.47.40/24`, GW `.2`), FRR/docker, puertos `tr-sw/trunk0/br0`, exporter 9110, NOC 9130, snapshot manual `NETLAB360_S05_PreLAN_20261110`.

## Conmutación S1 — evidencia técnica cerrada y etapa de HA 11/11/2026

- [x] **Lote 79 auditoría técnica:** 119 muestras JSONL, **55 PRINCIPAL / 64 RESPALDO**, secuencia `s1p→s1b→s1p`, `S05_CICLO_JSONL=OK`, concordancia 3 logs, SHA-256 de 4 archivos y TAR técnico `NETLAB360_S05_NOC_FAILOVER_S1_20261111.tar.gz` creado localmente.
- [x] **Lote 80 observación actual:** tres FRR en Docker, doce namespaces y VLAN de servicios HQ120/S1220/S2320, NOC 9130 y S04 9110 escuchando, ruta de gestión VMnet8 preservada. Observación no acredita un balanceador HA desplegado.
- [x] **S05_29 y 30 aprobadas; S05_31 aprobada con salvedad** ya registrada: color rojo/azul durante conmutación, siguiente salto exacto se aporta por JSONL y simulador; no volver a bajar WAN para repetir captura.
- [ ] Confirmar que el operador guardó **S05_32** (rango INICIO→FIN en auditoría local); no afirmar que está en GitHub.
- [ ] En la siguiente etapa, NOC debe mostrar activos HA nuevos **solamente una vez verificados**; el inventario `inventario/topologia-extensiones-s05.json` sigue vacío por diseño. No pintar servicio HA «activo» antes de despliegue.
- [ ] Continuar como parte de issue [#32](https://github.com/recm0708/netlab360/issues/32) con [precheck HA nuevo](https://github.com/recm0708/netlab360/blob/main/scripts/validacion/s05-ha-precheck.py), sin afectar fuentes S04/FIB del core.

## NOC S05 — Prueba dinámica aceptada y PNG 29–31 (11/11/2026)

- [x] `main` sincronizado en VM (`0a5500c`) y distintivos compactos `ACTIVO/INACTIVO/SIN DATOS` funcionando; **36/36 pruebas S05** y precheck S1 principal correctos.
- [x] NOC S05 observado con fuente S04/FIB confiable: **119 muestras JSONL**, `S05_NOC_CICLO_COMPLETO=OK`, transición `s1p / 10.78.0.2 → s1b / 10.78.0.6 → s1p / 10.78.0.2`.
- [x] Simulador controlado, ventana 25s, failover bidireccional de S1, S2 estable, retorno OSPF/FIB y postcheck `ens33`/Git intactos; `S02_S1_PRUEBA_COMPLETA=OK` y `S05_FIB_RESTAURADA=OK`.
- [x] **PNG S05_29** (selección principal/inspector FIB) y **S05_30** (código de colores completo) recibidos y aceptados.
- [x] **PNG S05_31** aceptado como vista del failover: primaria HQ–S1 roja, respaldo azul discontinuo en FIB, otra sede verde. **Limitación visible:** PNG no incluye inspector ni next-hop; el `10.78.0.6` está probado por logs/JSONL, no visible en la imagen. No repetir intervención solo por estética.
- [ ] **Control documental de entrega:** verificar JSONL+TXT, SHA-256, manifiesto y TAR; importar PNG auténticos a `evidencias/capturas/fase5` en lote posterior. No hay prueba de tráfico medido por la FIB; mantener esa limitación.
- [ ] **No cerrar aún issue #64**: está asociada al NOC extensible, importación de evidencias y futura observabilidad de nuevas funciones HA/OVS/LACP. Se completó **la demostración NOC de conmutación S1**, no todo S05.

[Bitácora de conmutación observada](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-observacion-failover-s1-validada.md) · [Auditoría de capturas S05](https://github.com/recm0708/netlab360/blob/main/docs/evidencias/10-auditoria-s05-png-y-capturas-pendientes-2026-11-11.md). El resto del cuerpo es historial anterior.

## Recuperación NOC y evidencia actual verificadas — 11/11/2026

- [x] **Falla anterior resuelta:** reinicio controlado de NOC T1 con `sudo -v` (nuevo PID `449431`, 9130) y exporter S04 T4 activo (PID `425166`, 9110). T2 túnel Windows validado. Dos lecturas S04/NOC separadas por 4s: `S04_FUENTE=True`, `topology=active`, `errors=[]`, `NOC_FIB=True`, `source_warnings=[]`, S1 `s1p/10.78.0.2`, S2 `s2p/10.78.0.10`; `LOTE72R_FUENTES_RECUPERADAS=OK`.
- [x] **Precheck estable:** `S05_NOC_FASE=PRINCIPAL`, `S05_NOC_PRECHECK=OK_SIN_CAMBIOS`; el navegador muestra topología ACTIVA y cabecera corporativa. El incidente previo era de supervisión, no de pérdida de la WAN.
- [x] **Indicador visual compacto:** badges `ACTIVO` (verde), `INACTIVO` (rojo solo observado) y `SIN DATOS` (gris); se eliminó el redundante `RTR:`. Código y prueba estática versionados; CI aprobado.
- [x] **S05_28 aceptada:** el PNG presentado confirma rutas principales elegidas verdes y respaldos grises. Retirar solo sufijo `(1)`. Revisión de cuatro capturas documentada en [auditoría de evidencias](https://github.com/recm0708/netlab360/blob/main/docs/evidencias/10-auditoria-s05-png-y-capturas-pendientes-2026-11-11.md).
- [ ] **S05_29 final:** seleccionar principal HQ↔S1, mapa desde encabezado y campo inspector `Origen ruta`, con siguiente salto `10.78.0.2`.
- [ ] **S05_30 final:** tarjeta completa `Código de colores y estados`, desde el título hasta último texto explicativo, en una sola toma.
- [ ] **S05_31 dinámica:** tras iniciar T5 observador y verificar disponibilidad, ejecutar T6 durante máximo 25s de respaldo S1; capturar el estado azul seleccionado con próximo salto `10.78.0.6`. No se ha realizado todavía. Debe confirmar JSONL/retorno FIB y ens33 intacta.
- [ ] **Mejora operativa posterior:** recolección FIB de mínimo privilegio sin dependencia de caché interactiva sudo; no otorgar NOPASSWD amplio.

**No crear instantáneas, no volver a desplegar S02 y no cerrar #64 o milestone S05 hasta completar la evidencia dinámica.**

## Diagnóstico confirmado de supervisión — 11/11/2026, recuperación en curso

- [x] **Lote 72R-A:** proceso NOC existente **PID 334882** escucha en `127.0.0.1:9130`; **9110 sin proceso** antes de recuperación. Tres routers Docker `nl360-s02-r-hq/s1/s2` activos ~4 h; gestión `ens33 192.168.47.40/24` y ruta default `.2` correctas.
- [x] **T4 exporter S04 restaurado** con `sudo -v` en su propia sesión, `source_ok=True` y `topology=active`.
- [x] **Incidencia histórica 72R-C corregida después:** el viejo NOC no tenía FIB, pero fue reiniciado limpiamente en T1; el nuevo NOC 9130 reportó FIB S1/S2, sin source_warnings. No se tocó FRR.
- [ ] **Causa FIB probable por diseño:** `fib_routes()` en `app.py` hace `sudo -n docker inspect` y `sudo -n nsenter -t PID -n ip -j -4 route get`. La autorización de `sudo` en T1 podía estar vencida: el NOC llevaba **1h14m**. Confirmar después de renovar credenciales en **la misma T1**, detener sólo su proceso con Ctrl+C y relanzarlo. Un `sudo -v` desde T3/T5 no garantiza privilegios del NOC en T1.
- [x] **Runbook operatorio GitHub creado:** [mapa de seis terminales y recuperación NOC](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-mapa-terminales-y-recuperacion-noc.md) con T1 visor 9130, T2 túnel Windows 9130, T3 auditoría SSH, T4 exporter 9110, T5 observador temporal, T6 simulador temporal; se prohíbe iniciar procesos duplicados y tocar snapshot manual.
- [x] **Prerrequisitos de observabilidad completados:** T1 NOC reiniciado, T4 S04 operativo, T3 dos muestras sanas y precheck S1 OK, T2 túnel Windows comprobado. **T5 observador / T6 failover aún no realizados**.
- [ ] **Deuda técnica del NOC empresarial:** sustituir la dependencia de credenciales sudo de TTY y caducidad para supervisión desatendida por lectura de mínimos privilegios; no resolver corriendo servidor HTTP como root ni dando NOPASSWD amplio.

**Este incidente no provocó conmutación WAN ni ejecución del lote 73.** La issue y milestone S05 permanecen abiertas, sin borrar evidencias.

## Incidencia de reanudación del observador NOC — 11/11/2026

- [x] `LOTE70_PREPARACION=OK`: Git `main` limpio, **36/36 tests S05 OK**, compilación Python, sintaxis JavaScript y precheck del visor correctos (commit VM `2117f64`).
- [x] `LOTE71_OBSERVADOR_LISTO=OK`: exporter S04 `source_ok=true`, topología `active`, NOC `routing.available=true`, FIB S1 `s1p/10.78.0.2` y S2 `s2p/10.78.0.10`, `ens33=192.168.47.40/24` y gateway `.2`.
- [ ] **Bloqueo lote 72**, aún no resuelto: en sesión SSH distinta, `--watch --site S1` abortó **en el precheck**, indicando `topology=unknown`, `fuente_s04=False`, `fuente_fib=False`, `fase=SIN_FUENTE_VERIFICABLE`. El mensaje `S05_NOC_OBSERVADOR_LISTO=S1` **nunca apareció** y **no hubo** ejecución de failover lote 73 ni postcheck 74. El usuario cerró una terminal por equivocación; túnel SSH había notificado `Connection reset` y `Connection refused` hacia 9130. **No consta mutación alguna de WAN en este intento**.
- [ ] **Diagnóstico seguro antes de reintento:** comprobar procesos/puertos 9110/9130, `/api/v1/state` y `/api/v1/graph` y `source_warnings`; verificar autorización `sudo -n` en las sesiones **donde corren** S04 y NOC (cache sudo potencialmente por TTY y tiempo). Reiniciar solo observadores si es necesario, sin reiniciar Docker/FRR ni recrear WAN/LAN, y repetir `--precheck`.
- [ ] Mantener pendiente la conmutación real S1, observación de backup azul, retorno, capturas S05_29/30/31 y documentación SHA256.

Fuente aportada por el operador: `Texto pegado(20261111-043826).txt`, transcripción de terminales 1–5. No restaurar ni operar sobre snapshot manual `NETLAB360_S05_PreLAN_20261110`.

## Actualización prioritaria — 11/11/2026: diseño V7.2 aceptado y observación dinámica preparada

- [x] **Validación visual V7.2:** el operador remitió imagen del NOC y aprobó el diseño verde lima sin contorno violeta; la principal HQ–S1 conserva FIB seleccionada con siguiente salto `10.78.0.2`. El segundo clic para deseleccionar está cubierto por tests, pero la captura oficial `S05_29` y la leyenda completa `S05_30` aún deben confirmarse como archivos de evidencia.
- [x] **Pruebas V7.2 ejecutadas en VM:** `Ran 28 tests ... OK`. El lote 67 se detuvo después de las pruebas por un `grep` sobre texto interno de Node capturado por el runner; no hay fallo de las 28 pruebas. Falta comprobar `node --check` y `app.py --check` en el siguiente lote.
- [x] **Edición corporativa del NOC en GitHub:** cabecera de centro de operaciones, mensaje contextual `Supervisión operativa` cuando S04 es confiable, rutas FIB verificadas únicamente si el API las acredita, panel `Integraciones de infraestructura` y pie sin menciones a avances futuros.
- [x] **Código de observación NOC de failover preparado, sin ejecución en VM:** `scripts/validacion/s05-observar-conmutacion-noc.py` consulta exclusivamente `127.0.0.1:9130/api/v1/graph`, verifica baseline y registra `PRINCIPAL→RESPALDO→PRINCIPAL` con FIB y UTC en JSONL local. Script de failover S02 con opción `--hold-seconds 0..30` (default 0) y restauración `finally`; no se ha inducido otra falla todavía.
- [x] **Regresión adicional en GitHub:** ocho tests offline del observador y compatibilidad de ventana de restauración. Workflow S05 ampliado; total esperado en la VM al sincronizar: **36/36 tests**.
- [ ] **Siguiente validación sin cambios:** Git limpio, 36/36, `node --check`, `app.py --check`, API S04 y NOC 9130 con FIB principal verificada, `--precheck --site S1`. No cortar WAN si la fuente/identidad no es confiable.
- [ ] **Demostración NOC real S1:** una terminal observa `--watch --site S1 --seconds 90 --interval 0.5`; otra ejecuta `s02-failover-wan.py S1 --hold-seconds 20` con `sudo -v` y supervisión. Validar respaldo azul elegido por FIB, retorno a principal verde, JSONL y gestión `ens33` intacta. Registrar captura con encuadre exacto; después decidir S2.
- [ ] **Cierre documental:** consolidar PNG oficiales S05_29/S05_30 y futuras capturas dinámicas con nombres sin extensión e integridad SHA256. No marcar completada esta issue hasta observar backup elegido/restauración, y no afirmar tráfico medido.

Referencias: [sesión V7.2 y guion de conmutación](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-noc-v72-y-preparacion-conmutacion.md), [punto de reanudación](https://github.com/recm0708/netlab360/blob/main/docs/REANUDAR-AQUI.md). **Preservar instantánea manual `NETLAB360_S05_PreLAN_20261110` y `ens33`.**

# Topología interactiva NETLAB360 — Fase 5 (visualización avanzada)

**Origen:** requisito propuesto por el operador el 27/10/2026 tras validar el incidente G3 de S04. **Estado al 11/11/2026:** visor/API V6 implementados, probados (18/18), aprobados visualmente e integrados a S04; red multisede funcionando y conmutación de ambas WAN verificada por consola. **Sigue faltando correlación en vivo FIB/OSPF en el NOC y uso de contadores antes de afirmar tráfico**. La fase S04 ya muestra tarjetas reales CENTRAL/HQ/S1/S2 y eventos activos; esta ampliación no bloquea los controles G4–G6 de S04.

## Alcance visual esperado

- Diagrama multisede actualizado automáticamente (sin recarga): bloques HQ, S1 y S2, tres routers FRR, cuatro WAN (dos primarias y dos de respaldo), tres switches virtuales, nueve VLAN/segmentos y nueve hosts/nodos. En futuras fases, añadir OVS/Faucet, LACP, redundancia de equipamiento o servidores **solo si existen realmente en el laboratorio**.
- Diferenciar interfaces y **enlace extremo a extremo**: si HQ/s1p está DOWN aunque S1/s1p siga administrativamente UP, el enlace HQ–S1 principal **no** se representa como operativo. Combinar observaciones de ambos extremos y estado de rutas/OSPF cuando estén instrumentados.
- Propuesta de colores semánticos: **verde** primaria operativa y elegida; **azul** respaldo tomando tráfico real; **turquesa/azul discontinuo** respaldo disponible pero en espera; **amarillo/ámbar** degradación, transición o mantenimiento; **rojo** fallo real confirmado; **gris** sin datos o topología desmontada intencionalmente. No llamar daño físico a un estado administrativo de una red virtual.
- Animación de flujo: puntos desplazándose por enlaces solamente si hay **incremento de contadores de tráfico**, flujos o métricas de datos reales. No inferir paquetes del estado `admin_up=1`. Si solo se conoce OSPF/FIB, puede mostrarse animación etiquetada de **ruta seleccionada**, sin afirmar tráfico medido. Ajuste de animaciones para accesibilidad y reducción de movimiento.
- Vistas central/por sede, panel de detalles al seleccionar dispositivo, IP/VID y naturaleza de dato (SoT esperado vs dato observado), tiempos UTC/edad de muestra y estado de fuentes UNKNOWN. Animación y colores con leyenda textual accesible, no depender de color únicamente.

## Fuentes y arquitectura

- Reutilizar SoT `candidate` con contrato explícito y *exporter*/Prometheus/NOC existentes, sin red inventada; mantener el SoT de S03 trazable y diferenciar esperado vs descubierto.
- Incorporar capa de topología lógica y grafo de estados derivado de telemetría; no modificar FRR al pintar.
- Historial y logs persistentes de incidentes como parte de **G4/G5 S04** (issue #21); S05 visualizará ese histórico, S06 aplicará diagnóstico etiquetado y S07 integrará reparación supervisada.
- No exponer API ni procesos a `0.0.0.0` ni tocar `ens33`.

## Criterios de aceptación futura

- [x] **Baseline sano NOC V7 verificado 11/11/2026:** 3 routers, 4 WAN, 9 VLAN, 9 hosts; FIB HQ real confirma primarias verdes `selected` (`s1p`,`s2p`) y respaldos discontinuos `standby` (`s1b`,`s2b`). Captura `S05_28`, API `S05_27` y lote 60 documentados; aún no acredita tráfico medido ni visualización durante un corte.
- [ ] Incidente S1: primario HQ–S1 rojo/ámbar según evidencia, respaldo azul activo, S2 sano.
- [ ] Recuperación: transición reproducible, retorno a enlace principal y cronología correspondiente.
- [ ] Fuente caída/obsoleta: gris/UNKNOWN (sin falsos verdes o falsos fallos).
- [ ] Tráfico animado demostrablemente correlacionado con contadores; modo solo rutas si no hay medidas de tráfico.
- [ ] Tests de modelo de estados y regresiones, capturas S05, manual técnico, integración web y modo accesible.

**Dependencias:** S04 API activa, S03 SoT candidato con limitaciones explícitas, S05 redes avanzadas según hitos propios. No exigir completar IA S06 ni S07 para el primer diagrama.

## Primera implementación S05/NOC — código preparado 10/11/2026

- [x] [Servidor local de grafo, solo lectura](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/app.py) con datos IPAM S02 (`candidate`), 3 sedes, 3 routers, 3 switches y 9 hosts; cuatro WAN bidireccionales; escucha **solo** en `127.0.0.1:9130`.
- [x] [Interfaz interactiva SVG](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/index.html) con nodos seleccionables, enlaces primarios continuos/respaldo discontinuos, inspector, filtro de sede y actualización cada 3 s. Documentación y prueba automática offline incluidas.
- [x] Contrato básico de estados: exporter S04 reciente para RUNNING/ADMIN UP/DOWN/OFFLINE; chequeo lectura `netns` para inventario LAN; `UNKNOWN` cuando fuente no disponible. **ADMIN UP no prueba ruta seleccionada ni flujo**.
- [x] Ejecutar **contrato backend inicial 6/6** y `--check` en Ubuntu; `/healthz` sano, `/api/v1/graph` accesible desde Windows mediante túnel SSH 9130; inventario 3 sedes, 3 routers, 3 switches, 9 hosts/9 VLAN, 4 WAN y `UNKNOWN` sin exporter, confirmado por salida del operador el 10/11/2026.
- [x] Validar frontend **v2/v3** en Ubuntu con 10/10 y 13/13 pruebas, sintaxis JavaScript, API y reloj de VM Panamá; el operador abrió el visor y compartió capturas preliminares desde Windows.
- [x] **Diseño visual V6 aprobado** por el operador después de revisar capturas provisionales Windows: HQ/S1/S2, cuatro enlaces principales/respaldos y etiquetas sin superposiciones relevantes. La aprobación es únicamente de presentación.
- [x] Capturas del mapa completo `S05_10`, inspector WAN respaldo `S05_11` y `UNKNOWN` complementaria `S05_12` revisadas; **18/18 pruebas V6** ejecutadas y registradas. PNG aún no importados al repositorio.
- [ ] Añadir correlación OSPF/FIB y ambos extremos para identificar primaria elegida, respaldo activo y degradación sin confundir `admin_up` con salud E2E.
- [ ] Incorporar nuevos equipos HA/OVS/servidores **solo con despliegue y evidencias**; extender geometría para sedes futuras y nuevas conexiones.
- [ ] Medir contadores por intervalo y activar animaciones accesibles solo cuando existan datos reales.

[Manual de primera versión](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/README.md). El catálogo `inventario/topologia-extensiones-s05.json` permanece vacío porque no se han certificado equipos adicionales.


## Revisión visual del operador (10/11/2026)

- El primer acceso real en Windows confirmó que la API y el túnel funcionan, pero la vista v1 tenía dispositivos encima de subtítulos, líneas LAN sobre etiquetas y necesidad de desplazamiento para ver todas las sedes.
- Se rediseñó [index.html](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/index.html) con geometría segmentada, corredor WAN, nombres dentro de símbolos, sin router dibujado dos veces, y botón **Modo presentación** (tecla Esc para salir).
- Se añadieron [pruebas de geometría](https://github.com/recm0708/netlab360/blob/main/tests/test_s05_layout.py) y chequeo de sintaxis JS en [CI S05](https://github.com/recm0708/netlab360/blob/main/.github/workflows/ci-s05-topologia.yml); pendientes de ejecución real de esta revisión en la VM. **No declarar capturas oficiales tomadas ni cerrar issue.**


## Revisión adicional v3 — reloj de VM Panamá y compactación (10/11/2026)

- [x] Código del backend ampliado con `vm_clock.utc` y `vm_clock.panama`, calculados del mismo instante del reloj de la VM con `zoneinfo(America/Panama)` y UTC preservado para auditoría.
- [x] Frontend ajustado para mostrar fecha/hora legible `es-PA` y chip por sede de **estado del router**, sin deducir salud global. SVG compactado (1440×920) manteniendo corredor WAN y separación geométrica de equipos/cableado.
- [x] Añadidas pruebas sobre la coherencia UTC/Panamá y cableado LAN, y validación estática de sintaxis JavaScript de la versión v3.
- [x] v3 **ejecutada** en Ubuntu: 13/13 tests, sintaxis JS, `--check`, reloj VM UTC y Panamá coincidente, navegador Windows y API accesibles. Un túnel SSH se reconectó tras un reset; se confirmó el servicio posteriormente.
- [ ] Tomar capturas oficiales solo cuando el visor v3 quede aprobado. Las imágenes enviadas hasta ahora siguen siendo provisionales.


## V4 — Corrección de arquitectura WAN del diagrama (10/11/2026)

- Se detectó en las capturas v3 que los caminos WAN curvos parecían partir de los **hosts VLAN**. Se reemplazaron por **circuitos ortogonales en el SVG, que parten de `R-HQ` y finalizan en `R-S1`/`R-S2`**, sin atravesar tarjetas LAN ni encabezados.
- Principal = línea continua por corredor exterior; respaldo = discontinua por el corredor interior entre sucursales. Se corrigieron posibles cruces entre circuitos separando entradas laterales de routers.
- Las etiquetas ya no son únicamente `HQ–S1 P`: identifican `HQ ↔ SUCURSAL S1/S2`, `WAN PRINCIPAL/RESPALDO` y la **subred IPAM**.
- La API intenta enumerar namespaces con `ip netns list` sin privilegios antes del fallback `sudo -n`, sin ninguna operación de modificación. Se añadieron tests para ruta WAN router-router, no intersección de cables y consulta de namespaces.
- **V4 ejecutada con 16/16 tests OK**, API y JS correctos, pero las capturas provisionales mostraron cables y etiquetas WAN amontonados (en particular, la leyenda inferior se superponía con los respaldos). Se rechaza V4 para evidencia final, sin declarar problema de red.


## V5 — Dos grupos WAN y disposición apaisada (10/11/2026)

- [x] Reorganizar geometría lógica: HQ en columna izquierda, S1 arriba a la derecha y S2 abajo a la derecha; módulos WAN S1/S2 en el corredor central, con dos pistas por módulo, cada una rotulada por tipo y subred.
- [x] Mantener cuatro circuitos individuales de `R-HQ` hacia `R-S1`/`R-S2` sin cruces de trayectorias, ni rutas que recorran los hosts VLAN. Línea continua principal, discontinua respaldo, selección accesible e inspector más legible.
- [x] Eliminar anotación redundante de principal/respaldo en el medio del trazado; conservar la leyenda del panel lateral y `UNKNOWN` cuando la fuente S04 no está disponible.
- [x] Revisar una previsualización SVG local del diseño y actualizar las verificaciones geométricas para módulos/píldoras y terminaciones router-router. **No es una captura real del navegador/VM**.
- [ ] Confirmar regresión V5/V6 en Ubuntu (V6: **18 tests**, 9 geometría y 9 grafo), `node --check`, precheck y revisión de la nueva V6 en navegador Windows. Se recibieron **capturas provisionales V5**, pero todavía no una ejecución formal con logs de prueba V5 ni evidencias finales.
- [ ] Integrar telemetría FIB/OSPF, failover de equipos y enlaces de forma verificable; no marcar rutas elegidas o dispositivos activos basándose solo en el inventario candidate.

[Manual actualizado V5](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/README.md). **Issue abierta hasta validación funcional/visual y evidencias de estado real**.


## V6 — Ajuste de simetría solicitado por el operador (10/11/2026)

- En las capturas provisionales V5, el operador considera que la ruta de respaldo a S2 necesita mayor simetría con S1. Se conserva intencionalmente la organización interna de ambas sucursales: **título, router, switch, VLAN**, sin invertir el sentido de S2.
- **Preparado en código:** R-HQ se acerca al eje medio entre R-S1 y R-S2; se redistribuyen los cuatro puertos WAN del símbolo HQ; el módulo S2 sube 30 unidades y el respaldo llega al router con codo final de 25 unidades. Se mantienen principal continua y respaldo discontinuo, subredes/IPAM y click-inspector.
- Se añadió prueba geométrica V6 para proximidad del último codo, simetría vertical del origen, separación de carriles y organización de VLAN. **18 pruebas esperadas; aún sin resultados de la VM**.
- **Pendiente:** `git pull`, pruebas locales, vista normal y modo presentación en Windows. **No** utilizar las capturas preliminares para el informe ni cerrar la issue por cambios puramente gráficos.


## Cierre de diseño gráfico V6 — aprobado visualmente (10/11/2026)

- [x] El operador revisó dos capturas provisionales de la V6 y confirmó que **el diseño ya le parece correcto**. Se congela la geometría para trabajar observabilidad/failover y evitar más iteraciones cosméticas sin necesidad.
- [x] Se mantienen HQ, S1, S2, 3 FRR, 3 switches virtuales, 9 VLAN/hosts y 4 WAN de IPAM candidate, con líneas continuas y discontinuas y hora Panamá.
- [x] **Capturas visuales recibidas y auditadas**: `S05_10_Topologia_General_Tres_Sedes` completa y `S05_11_Topologia_Inspector_Enlace_WAN` con respaldo HQ-S2 seleccionado y extremos correctos; `S05_12` aceptable como evidencia histórica de `UNKNOWN` aunque incluye aviso antiguo sobre namespaces.
- [ ] Integrar bytes PNG originales en el repositorio con SHA-256; opcionalmente reemplazar `S05_12` por captura posterior sin el aviso obsoleto.
- [x] **Regresión V6 documentada:** lote 41, 18/18 pruebas OK; `--check`, JSON `--once`, Git `main` limpio, `S05_V6_ACEPTACION_TECNICA=OK` (commit `4cecabd` registrado).
- [x] **Auditoría de fuente S04 completada:** SoT candidate íntegro, observación `--once` confiable con `source_ok=true`, `topology=offline`, tres routers en 0; Docker y netns vacíos, 9110 sin servidor, visor 9130 saludable.
- [x] **Integración S04 HTTP ↔ visor V6 verificada** en vivo: exporter `127.0.0.1:9110/api/v1/state` devuelve `source_ok=True`, `topology=offline`; API NOC `127.0.0.1:9130/api/v1/graph` devuelve `telemetry.available=True`, `telemetry.topology=offline`; R-HQ/R-S1/R-S2 identificados `offline`; marcador `S05_S04_INTEGRACION_OFFLINE=OK` y captura `S05_13_Topologia_Offline_Observado` recibida.
- [ ] **Resta** validar en escenario desplegado OSPF Full, FIB activa, tráfico, rutas principales/alternas y conmutación/recuperación; este test solamente acredita fuente y estado offline.

La [guía del visor](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/README.md) distingue aprobación **visual** de aceptación **funcional**; mantener abierta la issue hasta evidencias y pruebas reales.


## Recepción de evidencia y fuente S04 (10/11/2026)

La auditoría de los 14 PNG aportados distingue capturas de precheck (2), piloto LACP P1 (4), P1B (5) y NOC V6 (3). Las imágenes S05_10/11 cubren criterios visuales; S05_12 es válida como captura de fuente desconectada, pero tiene un aviso anterior sobre permisos netns. Los 18 tests V6 pasaron y la red de gestión permaneció igual. El exporter S04 `--once` reportó **tres routers ausentes y topología OFFLINE**, sin contenedores Docker ni namespaces, pero `127.0.0.1:9110` no estaba sirviendo; por tanto el NOC marcaba `UNKNOWN`, como corresponde. Integración HTTP, empaquetado de PNG originales y observabilidad de rutas siguen pendientes. [Auditoría visual de 14 PNG y fuente S04](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-auditoria-capturas-y-fuente-s04.md).


## Verificación de integración en vivo S04↔V6 — 10/11/2026 (Panamá)

- [x] Operador inicia `s04_exporter_multisede.py --serve --port 9110 --interval 2` con `sudo -v` temporal. El servicio anuncia `S04_MODO=SOLO_LECTURA` y no despliega ni modifica redes. El NOC continúa en `127.0.0.1:9130`.
- [x] Consulta cruzada guardada localmente en `~/netlab360-bootstrap/s05/evidencias/observabilidad/02_Integracion_Exporter_S04_V6.txt`: `S04_FUENTE=True`, `S04_TOPOLOGIA=offline`, `NOC_FUENTE=True`, `NOC_TOPOLOGIA=offline`, routers R-HQ/S1/S2 `offline` y `S05_S04_INTEGRACION_OFFLINE=OK`.
- [x] Captura `S05_13_Topologia_Offline_Observado` recibida y revisada: encabezado `Topología OFFLINE`, `Fuente S04 actualizada`, hora Panamá. **Válida como evidencia específica de cambio de estado; no es imagen del diagrama completo.** Todavía no se incorporan bytes PNG/sha al repositorio.
- [x] **Transición de observación OFFLINE→ACTIVE verificada**: el operador inició únicamente tres routers FRR aislados (Docker `network_mode:none`); S04 y NOC devolvieron `active`, mientras que `show ip ospf neighbor` seguía sin vecinos, como se esperaba. Demuestra cambio de presencia de procesos, **no** enlaces ni rutas operativas.
- [x] Las cuatro WAN, OSPF 4/2/2 FULL, FIB principal y conmutaciones S1/S2 fueron comprobadas en la VM; la instantánea vigente fue creada manualmente. **Nota histórica:** esta casilla quedó pendiente tras una ejecución antigua.

El estado `OFFLINE` actual describe la **ausencia de los tres routers**, no una falla inducida, y la disponibilidad temporal del exporter depende de que permanezca ejecutándose con capacidad de observación. Mantener abierta issue para telemetría y failover.


## Reactivación S02 para S05 (lotes 45–47; 10/11/2026)

- [x] Arranque verificado de `nl360-s02-r-hq`, `nl360-s02-r-s1`, `nl360-s02-r-s2` con imagen FRR local, `Running=True`, `NetworkMode=none`; no se creó ninguna WAN ni namespace host. Captura recibida `S05_14_Routers_FRR_Aislados_Iniciados`.
- [x] Las cuatro WAN (10.78.0.0/30, .4/30, .8/30 y .12/30) superaron `S02_WAN_PRECHECK=OK`; los vecinos OSPF están vacíos en los tres routers, correctamente antes del despliegue. Captura recibida `S05_15_Precheck_WAN_y_Routers_FRR`.
- [x] NOC y exporter S04 muestran `active` con fuente confiable al observar tres contenedores; gestión `ens33 192.168.47.40/24` y ruta por defecto `192.168.47.2` permanecen intactas; SSH Windows por clave funcional. [Bitácora S05/FRR](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-reactivacion-routers-y-precheck-wan.md).
- [x] **WAN S02 construidas y validadas:** 4 enlaces veth (costo OSPF principales 10, respaldos 100), `wan-links-state.json` válido, R-HQ 4 FULL, R-S1 2 FULL, R-S2 2 FULL; FIB en HQ selecciona `s1p` y `s2p`; `ens33` sin cambios. Capturas S05_17 (3), S05_18 (3), S05_19 recibidas y auditadas.
- [x] **VMware (resolución manual reportada):** el usuario eliminó las instantáneas anteriores y creó `NETLAB360_S05_PreLAN_20261110` de forma manual. No repetir acciones sobre instantáneas desde la terminal.
- [ ] Consolidar bytes originales de capturas S05_14/15 y manifiestos SHA-256; no se han subido a GitHub.


## OSPF FULL y FIB principales, S05 lotes 48–51 — 10/11/2026

- [x] Los cuatro enlaces WAN de S02 están creados y FRR aplicó configuración; hubo vecinos Init transitorios en la lectura inmediata de lote 50, seguida de convergencia FULL 4/2/2 en lote 51. Tablas OSPF y FIB confirman primarias `s1p`→`10.79.0.2` y `s2p`→`10.79.0.3` desde HQ, costos [110/10] frente a respaldo con costo 100. Salidas `LOTE50_WAN_CREADAS=OK` y `LOTE51_OSPF_Y_FIB=OK`.
- [x] Revisadas visualmente siete capturas S05_17 a S05_19 y transcripción original; gestor host `192.168.47.40/24`, GW `.2` no se alteró.
- [ ] **Importación** de los PNG/logs/JSON al repositorio con SHA-256 pendiente.
- [x] **Snapshot VMware — incidencia histórica resuelta por el usuario:** se retiraron las entradas antiguas y se dejó un punto de retorno nuevo `NETLAB360_S05_PreLAN_20261110`, según confirmación del operador. No ejecutar gestión automática de instantáneas.
- [x] **LAN completa y validada:** lotes 54R/55R, 3 switches, 9 VLAN/hosts y 12 namespaces; `S02_LAN_UP=OK`, 9/9 gateways accesibles, 3/3 pings intersede y rutas OSPF remotas en FIB. Capturas S05_21A/21B/22/23 recibidas y auditadas. El NOC `ACTIVE` refleja contenedores/interfaces, no tráfico o ruta seleccionada.
- [x] **Failover WAN S1 y S2 e inspección FIB real:** demostrados en lotes 57–59 y NOC V7. La *visualización durante la conmutación* continúa como casilla pendiente separada.

[Bitácora actualizada](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-reactivacion-routers-y-precheck-wan.md).


## Cierre de LAN S05 — evidencias originales 21A/21B/22/23

- [x] `LOTE54R_LAN_COMPLETADA=OK`: 3 switches, 9 VLAN/hosts, 12 namespaces y estado JSON legítimo.
- [x] `LOTE55R_CONECTIVIDAD=OK`: 9 gateways accesibles, HQ–S1, HQ–S2 y S1–S2 verificados. Rutas OSPF hacia seis redes remotas en HQ por `s1p/s2p`.
- [x] Cuatro PNG originales recibidos y auditados visualmente, con delimitadores completos y SHA-256 de copias del chat documentados en [bitácora de LAN](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-10-s05-lan-vlan-conectividad-validada.md). **No** están todavía importados como binarios en este repositorio.
- [x] Usuario reporta haber eliminado instantáneas antiguas y creado manualmente `NETLAB360_S05_PreLAN_20261110`. **Respetar método manual; no dar comandos para crear snapshots** y no tocar la instantánea durante failover.
- [x] Ejecutados en S05 los dos failovers del script `s02-failover-wan.py`: S1 `s1p→s1b→s1p` y S2 `s2p→s2b→s2p`, FIB bidireccional, ICMP y otra sede; postcheck `LOTE59_POSTCHECK=OK`. Capturas `S05_24/25/26` **reportadas tomadas, PNG aún no recibidos**.


## Validación real de conmutación y retorno — 11/11/2026

- [x] `S05_FAILOVER_PRECHECK=OK`: WAN y LAN state válidos; FULL en HQ 4, S1 2, S2 2; primarias seleccionadas.
- [x] `S02_S1_CONMUTACION=OK`, `S02_S1_RETORNO_PRINCIPAL=OK`, `S02_S1_PRUEBA_COMPLETA=OK`.
- [x] `S02_S2_CONMUTACION=OK`, `S02_S2_RETORNO_PRINCIPAL=OK`, `S02_S2_PRUEBA_COMPLETA=OK`.
- [x] `S05_FIB_PRINCIPALES_RESTAURADAS=OK`, pings posteriores 2/2 por destino HQ→S1 y HQ→S2, `S05_GESTION_FINAL=OK`, `LOTE59_POSTCHECK=OK`. [Bitácora verificable](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-failover-wan-s1-s2-verificado.md).
- [ ] **Aceptación visual de fallo/retorno en NOC aún pendiente:** la API S04 actual acredita Docker/router existente y flags administrativos. No declara por sí misma vecinos OSPF FULL, ruta FIB elegida ni bytes transferidos. Añadir observación FIB en runtime con identidad y validación temporal, manteniendo UNKNOWN si la consulta falla, luego probar con failover y capturas dinámicas.

No cerrar issue hasta validar fuente FIB, cambios de estado y evidencias finales.


## V7.1 — Visibilidad de selección sin falsear estados (11/11/2026)

- [x] Revisión de imagen preliminar S05_29: datos del inspector HQ–S1 correctos (`10.78.0.2`, FIB seleccionada, R-HQ), pero el clic casi no destacaba la línea verde; se pospone la captura definitiva hasta corregir UI.
- [x] Código versionado de **selección violeta independiente del estado FIB**: halo ancho del trayecto y extremos, contorno violeta de etiqueta y de inspector, dispositivo seleccionado igualmente diferenciado, explicación visual y leyenda que separa verde principal elegida, azul respaldo elegido, gris standby, rojo admin DOWN y gris sin datos/offline. No hay cambio en FRR, S04, Docker o red.
- [x] Prueba de regresión estática nueva sobre halo de selección y semántica de colores incorporada a `tests/test_s05_layout.py`; [documentación V7.1](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/README.md).
- [x] **V7.1 validada históricamente en VM** con 25/25 pruebas y captura preliminar del halo violeta. **Diseño rechazado por el operador y reemplazado por V7.2** (verde lima); la captura oficial S05_29 continúa pendiente en casilla propia.
- [ ] V7.1 **no cierra** la prueba gráfica de failover que evidencie respaldo azul elegido y principal restaurada; tampoco implementa alertas de salud sin telemetría ni atribuye tráfico por FIB.

## NOC V7 — observación de FIB, desarrollo versionado 11/11/2026

- [x] Implementar **código de observación FIB solo lectura**: validar el propietario del `wan-links-state.json`, ID exacto Docker del router `nl360-s02-r-hq`, etiqueta `netlab360-s02-wan`, `network_mode:none` y 2 rutas hacia `10.79.0.2`/`10.79.0.3` con gateway esperado. Lecturas autorizadas `sudo -n docker inspect` y `sudo -n nsenter ... ip -j -4 route get`; no mutaciones. `routing.available=false` si no hay muestras confiables.
- [x] Añadir en API `links[].route_selection` (`selected/standby/unavailable/unknown`), origen/gateway y `routing.traffic_measured=false`; colorear el circuito según **FIB real en R-HQ**: primaria seleccionada verde, respaldo elegido azul, standby gris, admin DOWN comprobado rojo. Inspector con selección y próximo salto; no declarar tráfico por elección de ruta.
- [x] Añadir tests offline de selección principal/backup, degradación a UNKNOWN, identidad y lectura exclusiva; regresión estática del UI. [Guía técnica V7](https://github.com/recm0708/netlab360/blob/main/servicios/topologia-s05/README.md).
- [x] **Validación V7 ejecutada en VM original 11/11/2026:** `git pull` commit `8b99bb5`; 24/24 pruebas S05 `OK`; JS `node --check` OK; exporter S04 9110 (`source_ok=true`, `topology=active`); visor 9130 en ejecución; ambas WAN primarias FIB `selected`, respaldos `standby`; `routing.available=true`, `routing.traffic_measured=false`; `LOTE60_NOC_V7=OK`, `S05_V7_API_FIB_BASELINE=OK`. Capturas S05_27 y S05_28 recibidas y revisadas. **Inspector S05_29 y simulación visual de failover aún pendientes.**
- [ ] **Demostración visual de failover** con una única WAN a la vez y restauración `finally`, capturas de FIB backup seleccionado y retorno, sin afirmar flujos animados o milisegundos no medidos.


## Auditoría visual S05_24–28 y puesta en servicio V7 — 11/11/2026

- [x] Operador adjunta y se revisan imágenes `S05_24_Failover_WAN_S1_y_Restauracion`, `S05_25_Failover_WAN_S2_y_Restauracion`, `S05_26_Postcheck_Failover_OSPF_FIB_y_Gestion`: todas incluyen resultados y delimitadores previstos; no repetir pruebas de failover solo por documentación.
- [x] `S05_27_API_FIB_Principales_y_Respaldos` muestra fuente S04 confiable, FIB disponible, `TRÁFICO_MEDIDO=False`, principales `selected` con next hops 10.78.0.2/10.78.0.10 y respaldos `standby`. La API no atribuye tráfico real.
- [x] `S05_28_NOC_Rutas_FIB_Principales` visualiza el mapa completo V7 en modo presentación, HQ/S1/S2, dos principales verdes y dos respaldos discontinuos grises; sin solapamientos determinantes. Captura aceptada para evidencia.
- [ ] **S05_29** falta: en vista normal seleccionar principal `10.78.0.0/30` HQ–S1; incluir en un mismo encuadre el módulo WAN elegido y el inspector con `Selección FIB R-HQ: Ruta FIB elegida`, `Próximo salto FIB: 10.78.0.2` y `Origen ruta: Linux FIB R-HQ`.
- [ ] Falta prueba dinámica gráfica del respaldo `selected` durante corte y posterior restauración `selected` en principal; no se realizará sin baseline y guion controlado.

**Importación pendiente:** estos archivos PNG originales están en la conversación, pero **no se han incorporado al repositorio** como bytes ni manifiestos SHA256. No dar por completada la publicación de evidencias.

## V7.2 — Selección verde reversible e interfaz española

**Motivo:** el operador probó V7.1, obtuvo **25/25 pruebas OK**, y rechazó el halo y el recuadro violetas del inspector por excesivos. La captura provisional del inspector HQ–S1 era técnicamente correcta, pero **S05_29 definitiva no está aceptada**.

- [x] Cambiar interacción sin modificar datos FIB: selección verde lima brillante independiente del trazo operativo (principal verde, respaldo seleccionado azul, standby gris, caída verificada roja y estados no comprobados grises); no hay bordes violetas ni aviso destacado dentro del inspector.
- [x] Implementar clic reversible sobre **el mismo enlace/equipo**: alterna seleccionado/deseleccionado; inspector vuelve a neutro y equipo/circuito recupera su apariencia original. `renderSelection()` preserva selección durante consultas automáticas sin volver a disparar `pick()`.
- [x] Centralizar código de colores y semántica en leyenda y traducir estados del visor: `ACTIVA`, `FUERA DE LÍNEA`, `SIN DATOS`, `DEGRADADA`; se conservan las claves inglesas de API y protocolos.
- [x] Añadir pruebas de regresión de selección/estados y prueba funcional de toggle JS con Node.js sin conexión a red. **28 pruebas S05 previstas (14 grafo, 14 visor)**. Se corrigió el contrato del workflow que exigía erróneamente el literal `UNKNOWN` visible tras la traducción.
- [x] **V7.2 sincronizada y aprobada visualmente en la VM:** 28/28 tests, selección verde lima HQ–S1 y panel FIB `10.78.0.2`, interfaz en español y leyenda. La ejecución del lote se detuvo después de los tests por `grep` incorrecto; **no se presume comprobado `node --check` ni `app.py --check` en ese lote**. Captura definitiva S05_29/30 e inspección de clic reversible explícita todavía pendientes.
- [ ] Sigue pendiente la prueba dinámica de failover **en el propio NOC**; no se repiten sin necesidad las pruebas de OSPF/FIB de terminal `S05_24`–`S05_28`. No cerrar #64 antes de la demostración.

El cambio es exclusivamente de interfaz (HTML/CSS/JS, tests, CI, documentación); **no modifica `ens33`, FRR, S04, Docker, WAN, LAN ni la instantánea manual**.

