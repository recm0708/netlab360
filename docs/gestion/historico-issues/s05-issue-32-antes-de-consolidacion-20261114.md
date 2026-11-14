# Archivo histórico de issue #32

**Fecha de corte:** 2026-11-14 (Panamá). **Origen:** https://github.com/recm0708/netlab360/issues/32

**Título original:** [024] Redundancia de equipos/servidor multisede — fase 5 pendiente

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

## Recuperación SSH/NOC 84R-G: situación observada y procedimiento (11/11/2026)

- [x] **Lote 84R-G FALLÓ por fuente S04 caída**, no por failover ni por HA: `tmux list-sessions` mostró `nl360-noc` **attached**, `ss` mostró solo 127.0.0.1:9130 PID `564662`, y `urllib` falló al abrir `127.0.0.1:9110` con `ConnectionRefusedError`. El NOC fue reiniciado en el terminal 3 y puede seguir operando en la sesión `nl360-noc`. El túnel de PowerShell en terminal 2 recibió repetidos `channel 2: open failed: connect failed: Connection refused`; su estado no equivale a un fallo de SSH general.
- [ ] **Secuencia de recuperación en vez de crear más terminales:** desprender la sesión NOC desde T3 con Ctrl+B, D **sin Ctrl+C**; detener solamente el túnel SSH antiguo T2 con Ctrl+C; establecer una sola sesión PowerShell `ssh -tt -L 127.0.0.1:9130:127.0.0.1:9130` con ServerAliveInterval/Count; auditar tmux/listeners y reiniciar **solo exporter** 9110 dentro de `tmux new-session -s nl360-exporter` tras comprobar puerto libre y `sudo -v` dentro de tmux; desprender Ctrl+B,D; verificar API S04 y NOC.
- [ ] El visor usa `sudo -n docker inspect/nsenter` y su autorización puede expirar por TTY: tratar FIB no disponible como aviso de observabilidad, NO como defecto de OSPF/FRR. No añadir a grupo Docker ni `NOPASSWD` genérico. Evaluar lector FIB de privilegios mínimos después de normalizar servicios.
- [ ] **Lotes HA 84,85,86 siguen sin ejecutar**, no existen PNG S05_34–36. No tocar `ens33`, routers S02, snapshot manual VMware. Anteriores lotes 81–83 y capturas 32/33 permanecen aprobados.

## Incidente recuperable de supervisión — diagnóstico 84R-D (11/11/2026)

- [x] **Auditoría de solo lectura ejecutada:** NOC 9130 PID `449431` ligado a terminal antigua `pts/2`, exporter 9110 PID `546643` en `pts/4`. Ambos escuchan en 127.0.0.1. FRR `nl360-s02-r-hq`, `-r-s1`, `-r-s2` **Up 12 hours**; S04 `source_ok=True`, `topology=active`, `errors=[]`.
- [x] **Causa precisa de pantalla sin FIB:** NOC en PID antiguo devuelve `routing.available=False`, `routes={}`, aviso `FIB: Docker no consultable sin privilegios interactivos`. Su fuente S04 sí funciona. El código del NOC invoca `sudo -n docker inspect` y `sudo -n nsenter`; la autorización `sudo -v` del proceso antiguo ya no está disponible.
- [x] **Confusión de nombre tmux identificada:** sesión `nl360-noc` creada 07:15, **attached**, panel ejecuta `python3 s04_exporter_multisede.py`, no NOC. Necesita renombrarse a `nl360-exporter` SIN detener el proceso.
- [x] **Infraestructura preservada:** `ens33 UP 192.168.47.40/24`, gateway `192.168.47.2`, Git limpio. No inferir que FRR o los 12 namespaces cayeron; no volver a desplegar S02.
- [ ] **Recuperación pendiente:** desprender sesión tmux exporter sin Ctrl+C; renombrar a `nl360-exporter`; finalizar únicamente viejo proceso NOC PID 449431 tras verificar CMD; levantar NOC dentro de tmux `nl360-noc` con autorización sudo renovada dentro de la sesión. Comprobar ambas APIs/FIB. Después fusionar túnel y SSH de control en UNA PowerShell, sin duplicar listener.
- [ ] **Limitación de largo plazo:** sudo timestamp de cada TTY puede expirar. No conceder membresía en grupo Docker ni `NOPASSWD` genérico para Docker/nsenter; diseñar un observador privilegiado mínimo y acotado con lectura estructurada si se requiere FIB indefinidamente, manteniendo APIs no privilegiadas solo en localhost.
- [ ] **Lotes 84–86 del despliegue HA NO ejecutados.** El código GitHub puede estar listo, pero no se ha creado red HA. Mantener snapshot VMware manual sin tocar.

## Corte de recuperación 11/11/2026 — todas las SSH cortadas, Lote 84 NO iniciado

**Confirmación explícita del operador:** las seis terminales SSH/PowerShell de la VM `netlab360-lab` se desconectaron con `client_loop: send disconnect: Connection reset` por inactividad/posible suspensión de VMware. El visor NOC en 9130 y exporter S04 en 9110 se lanzaban en primer plano dentro de terminales SSH, de modo que **sus procesos pueden haberse detenido**. **No hay prueba aún del estado actual** de esos puertos ni de las tres FRR; no atribuir el corte a daño de la infraestructura. **No se ejecutaron lotes 84, 85 ni 86**, no existe despliegue HA nuevo confirmado, no reclamar capturas S05_34–36.

**Próxima secuencia segura:** recuperar VM/SSH, auditar `uptime -s`, `ens33`, default gateway, contenedores FRR, 12 namespaces S02, puertos 9110/9130, `tmux` y estado HA antes de iniciar procesos; recuperar NOC/exporter preferiblemente en sesiones `tmux` persistentes para no depender de seis SSH, comprobando sudo cache por TTY para lecturas Docker; configurar un único túnel local PowerShell 9130; validar API S04/FIB/GUI; **solo entonces** repetir lote 84 (plan/precheck). No duplicar listeners ni ejecutar `up` si `~/netlab360-bootstrap/s05/ha/state.json` ya existe. No modificar VMware snapshot manual `NETLAB360_S05_PreLAN_20261110`.

Los lotes 81–83 y capturas S05_32/S05_33 ya estaban validados; siguen siendo los últimos avances operativos acreditados. El corte SSH no prueba fallos de OSPF ni deshace evidencias históricas.

## HA lógico S05 — implementación de red preconfigurada, pendiente del primer despliegue (11/11/2026)

- [x] **Lotes 81–83 validados:** 40 tests S05 OK, VLAN acceso HQ120/S1220, S2 conecta a hosts de servicios HQ y S1, precheck sin colisión observada de `10.70.20.21`, `10.70.20.23`, `10.71.20.21`; ENS33 intacta.
- [x] **Módulo de red propio con rollback versionado y probado offline:** `scripts/laboratorio/s05-ha-red-servicios.py`, `tests/test_s05_ha_red.py`, [CI verde](https://github.com/recm0708/netlab360/actions/runs/42974399828). Comandos `plan`, `precheck`, `up --confirm-isolated`, `status`, `down --confirm-isolated`. Puertos propios `ha-hq21/ha-hq23` HQ VLAN120, `ha-s121` S1 VLAN220; nombres de namespaces S05 y state ownership. No altera FRR, S02 host ni NOC.
- [ ] **Próxima ejecución en VM:** lotes 84–86 para crear y validar red HA antes de servidores HTTP. `--up` no se ejecutó. Requiere `sudo -v`, Git limpio y prechecks confiables.
- [ ] Servicio HTTP con backend A, backend B y frontal con healthcheck/fallback **todavía por implementar**; distinguir redundancia de backends de verdadera HA de equipo/VM.
- [ ] Posteriormente NOC muestra nodos nuevos solo después de estado real verificado; `inventario/topologia-extensiones-s05.json` permanece sin nodos/links S05.

## Avance validado 11/11/2026 — Lotes 81–83 y PNG 32/33

- [x] **Lote 81:** `git pull --ff-only` a commit `2a3f899`; sintaxis de `s05-ha-precheck.py` OK; **40/40 tests S05** correctos (incluye 4 pruebas HA); Git limpio.
- [x] **Lote 82:** `S05_HA_PRECHECK=OK_DISENO_PENDIENTE` sin cambios de infraestructura; ownership `NETLAB360_S05`, 12 namespaces S02, routers HQ/S1/S2, VLAN HQ120/S1220/S2320, hosts `.20` verificados; candidatas `10.70.20.21`, `10.71.20.21`, `10.70.20.23` sin asignación observada; S04/NOC y FIB principales sanas. **La inspección no supone reserva exclusiva ni autoriza aún crear equipos HA.**
- [x] **Lote 83:** cliente `nl360-s02-h-s2-320` alcanzó por ICMP a `10.70.20.20` (HQ) y `10.71.20.20` (S1), ambos **2/2 paquetes**, VLAN filtering inspeccionado en switches existentes HQ/S1 y sus puertos `a120/a220` en acceso; `ens33` y Git intactos.
- [x] **Evidencia PNG `S05_32_Validacion_JSONL_Ciclo_Conmutacion_S1.png` y `S05_33_Precheck_Alta_Disponibilidad.png`** aportadas y revisadas: se ven los encabezados INICIO/FIN y los verificadores. Son capturas recibidas en el chat; **NO son archivos binarios importados al repositorio**.
- [ ] **Próximo paso:** preparar despliegue HA aislado mediante puertos `veth` exclusivos por VLAN, healthcheck HTTP y rollback S05, con CI y precheck; los servidores HA **aún no están operativos**.
- [ ] **No tocar:** `ens33` (`192.168.47.40/24`, GW `.2`), FRR/docker, puertos `tr-sw/trunk0/br0`, exporter 9110, NOC 9130, snapshot manual `NETLAB360_S05_PreLAN_20261110`.

**CI verificada:** workflow [NETLAB360 S05 · run 42973137959](https://github.com/recm0708/netlab360/actions/runs/42973137959) concluyó `success` al incorporar `s05-ha-precheck.py` y cuatro pruebas unitarias. La CI **no** sustituye ejecutar `--check` dentro de la VM; aún no hay nodos HA ni IPs nuevas asignadas.

## Avance vigente 11/11/2026 · Precheck inicial y diseño HA

- [x] **Lote 80 auditoría base**: 3 FRR activos, 12 netns S02, 3 switches L2, VLAN servicio HQ120/S1220/S2320 y sus gateways, recursos suficientes (8 vCPU, ~13 GiB disponibles, 132 GiB disco), NOC/Exporter localhost, gestión `ens33` intacta; aún no existen namespaces HA de S05.
- [x] **Documento de diseño propuesto**: [HA multisede con HTTP preferido HQ / alterno S1](https://github.com/recm0708/netlab360/blob/main/docs/diseno/s05-ha-servicios-multisede.md). Tres nombres propuestos `nl360-s05-ha-hq`, `nl360-s05-ha-s1`, `nl360-s05-ha-fe`; IP **candidatas**, no asignadas: `10.70.20.21`, `10.71.20.21` y `10.70.20.23`. Frontal HQ es SPOF reconocido; una VM no equivale a HA física.
- [x] **Precheck especializado versionado**: `scripts/validacion/s05-ha-precheck.py --check`, sin `ip add`, sin crear netns, sin cambiar FRR, Docker ni host; verifica owners S02, LAN, puertos/VLAN, tres routers, IPs observadas, `ens33`, S04/NOC FIB. Pruebas unitarias `tests/test_s05_ha_precheck.py` (4 nuevas).
- [ ] **Revisión operativa aún pendiente:** ejecutar prueba en VM y confirmar antes de reservar IP o agregar conexiones `veth` a switches reales.
- [ ] **Construcción y aceptación HA todavía NO ejecutadas**: dos backends de distintas sedes, frontal healthcheck con fallback, cliente intersede, falla de backend A y respuesta B con identidad, restauración, tiempos y manejo de procesos/rollback; actualizar NOC únicamente después de tener datos observados.
- [ ] Validar idempotencia/reinicio y pruebas de regresión del core S02 sin tocar `ens33`, snapshot VMware ni exportador S04.

**Criterio de cierre #32:** demostrar redundancia de servicio, no solo conmutación WAN OSPF. El front-end puede ser SPOF y se documentará limitación hasta diseñar otro mecanismo de acceso.

## Transición a diseño HA — 11/11/2026

- [x] Precondición de red: tres routers FRR, tres conmutadores lógicos, nueve VLAN/equipos y cuatro WAN; **S1 prueba observada por NOC concluida**, S2 primaria conservada. El failover de enlace **no acredita HA de servidores/routers**.
- [ ] **Próximo paso diagnóstico de solo lectura:** inventario de contenedores, namespaces, interfaces, redes IPAM, puertos, servicios/volúmenes y recursos antes de seleccionar un par de servidores redundantes. Prohibido modificar `ens33` (VMnet8 192.168.47.40/24), gateway `.2`, FRR productivo del laboratorio o snapshot manual.
- [ ] Establecer arquitectura de **servicio HTTP de alta disponibilidad aislado** o escenario HA equivalente en una VLAN existente, que conserve servicio ante caída de un nodo con prueba funcional real, y diseñar métricas para incorporación al grafo NOC **solo después de desplegar y verificar**.
- [ ] Documentar criterio de aceptación: 2 nodos, IPs sin colisión, ruta/camino de servicio, conmutación automática y retorno, continuidad/respuesta HTTP, ausencia de degradación administrativa y evidencia reproducible. HA lógica de VM única **no demuestra disponibilidad ante fallo de host físico**.

Bitácora base: [observación S1](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-observacion-failover-s1-validada.md). Issue #32 y milestone S05 siguen abiertos.

# Redundancia avanzada — fase 5

## Antecedentes
- [x] Doble WAN OSPF y conmutación de enlaces lógicos verificados en fases 1/2.
- [x] Bonding/LACP en enlaces virtuales y recuperación de un miembro 2→1→2 probadas en fase1.

## Pendientes exclusivos de S05
- [ ] Diseñar y probar alta disponibilidad de **equipos** (router/switch/servidor) en escenarios definidos, no solamente fallar un enlace WAN.
- [ ] Verificar doble NIC/servidor alterno, caminos redundantes, conservación de estado del servicio y falla/recuperación.
- [ ] Distinguir claramente equipos simulados, enlaces lógicos y redundancia física (no disponible por defecto en VM única).
- [ ] Coordinar pruebas LACP multistream/medición [#31](https://github.com/recm0708/netlab360/issues/31) y SDN/OVS [#23](https://github.com/recm0708/netlab360/issues/23).
- [ ] Registrar pruebas, observabilidad y capturas `S05_*` con valores reales, sin declarar alta disponibilidad por una prueba aislada OSPF.

**No forma parte** del cierre de fase2 ni debe forzar reconstruir su topología aprobada.

## Alcance demostrado al 11/11/2026 (enlace, no equipo)

- [x] En S05 se confirmó fallo temporal y retorno automático de una **WAN primaria**, por separado en S1 y S2: `s1p→s1b→s1p`, `s2p→s2b→s2p`; FIB y pings de loopback, otra sede estable, gestión intacta y postcheck intersede correctos. [Bitácora failover](https://github.com/recm0708/netlab360/blob/main/docs/sesiones/2026-11-11-s05-failover-wan-s1-s2-verificado.md).
- [ ] **Pendiente de esta issue**: implementar un segundo equipo o servicio en HA, provocar falla de **router/switch/servidor** sin confundirla con un corte de enlace, demostrar continuidad/recuperación e inventariar equipos adicionales. La VM única no prueba redundancia física.

