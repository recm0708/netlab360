# NETLAB360 — Registro de inicialización de GitHub

## ACTUALIZACIÓN MÁS RECIENTE — 13/10/2026 17:45 PANAMÁ | B3 LIVE WAN COMPLETADO, CIERRE DE PUERTOS PENDIENTE

**Falla real y recuperación observadas, NO repetir la topología B2:** prueba 17:38–17:45 reportada por usuario: `status` OSPF 2 vecinos Full, WAN-P UP; `fail` código 0, ruta WAN-B y eventos del exporter `WAN_PRIMARY_DOWN` + `WAN_ROUTE_CHANGED` a **17:39:33.189**. `restore` código 0, `WAN_PRIMARY_RESTORED` a **17:42:05.813** (aún FIB WAN-B) y FIB WAN-P `WAN_ROUTE_CHANGED` a **17:42:15.841**. Contadores down=1, restored=1, route_changed=2; `down` B2 con limpieza código0, `TOPOLOGY_STOPPED` 17:44:56; exporter reflejó `topology=offline`. Cinco eventos JSONL guardados localmente `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl`; **no versionados físicamente**. [Bitácora completa](sesiones/2026-10-13-b3-live-ciclo-incidente-wan-verificado.md).

**Resultado crítico de postcheck:** captura B3_09 a 17:45:10 imprimió `PUERTO_9108_LIBRE: NO`, ya que exporter aún estaba activo; Docker/netns vacíos, host ens33 `192.168.47.40/24`, gateway `192.168.47.2` y servicios activos. PowerShell 3 seguía con túnel `ssh -N -L 9108:127.0.0.1:9108 netlab360` y errores repetidos `Connection refused` hacia destino; **primero terminar con Ctrl+C en PowerShell 3 y Terminal SSH 1 SI AÚN ESTÁN ACTIVAS, sin matar procesos al azar**, luego comprobar con `ss` puerto 9108 libre. Captura adicional **B3_09_Postcheck_Telemetria_Viva_Final.png** solo consulta read-only. B3_05–B3_09 se asumen tomadas según usuario, **sus PNG aún no están recibidos/inspeccionados**, a diferencia de los 24 PNG auditados de B1/B2/B3 anterior.

**Git local sincronizado en commit `2c468d1` pero `git status` NO limpio** por `?? servicios/observabilidad/__pycache__/` y `?? tests/__pycache__/` creados por Python. NUEVA [`.gitignore`](../.gitignore) en GitHub para excluirlos; `git pull --ff-only origin main` debe dejarlos ignorados, sin `reset --hard`. **S01 actualizado a 48% estimado** (B3 5/15 por eventos live, Prometheus NO realizado; antes 45%).

**PRÓXIMA ETAPA VERSIONADA PERO NO EJECUTADA:** [plan Prometheus real](operaciones/plan-b3-prometheus-local.md), archivos `servicios/observabilidad/prometheus/prometheus.yml`, `rules/wan-alerts.yml`, `scripts/observabilidad/preparar-prometheus-local.sh` y `ejecutar-prometheus-local.sh`. Estrategia segura: extraer binarios de imagen versionada `quay.io/prometheus/prometheus:v3.7.0` desde contenedor temporal `--network none`, **no se ha comprobado todavía la existencia de esa etiqueta en Ubuntu**, ejecutar Prometheus como proceso de usuario en `127.0.0.1:9090` y exporter habitual en `127.0.0.1:9108`; sin alterar host NIC/gateway, no usar Docker host network ni publicar puertos de VMware. El objetivo es demostrar **scrape real/TSDB y reglas cargadas**; luego un nuevo ensayo de alerta real con WAN-P DOWN/UP si procede. No atribuir Prometheus instalado ni alerta firing antes de pruebas.

**Issues #1/#12/#15/#20/#21/#35/#43** actualizadas; S01 sigue abierta. Evitar nuevos fallos mediante preflight, separación clara de terminales y verificación de puertos.

---


## REANUDACIÓN MÁS RECIENTE — 13/10/2026 17:31 PANAMÁ | EXPORTER B3 LIVE OK; TERMINAL 1 EN ESPERA NORMAL

**Más nuevo que diagnósticos antiguos de preflight:** usuario envió resultados reales 17:29–17:31: dos FRR `nl360-b2-r-hq` y `nl360-b2-r-s1` activos, marcador `netlab360-b2-dualwan`, red ens33 `192.168.47.40/24` y gateway `192.168.47.2` intactos. Git pull a `c4f3d47` limpio antes del commit de esta bitácora; `ast.parse` y `bash -n` OK; **5/5 tests de regresión OK**; auditoría de dependencias **0 programas requeridos ausentes** (Docker 29.9, Compose 5.6, FRR 10.7.1, Python y PyYAML, OpenTofu, Ansible, gh, Node/NPM verificados). Fallo de parseo Docker minúsculas YA REPARADO Y VALIDADO realmente.

**Terminal SSH 1**: `live_exporter.py --check` devolvió `B3_LIVE_PREFLIGHT=OK`, `B3_TOPOLOGIA=ACTIVE`, código 0. Luego `python3 servicios/observabilidad/live_exporter.py --serve` se inició correctamente y **SIGUE corriendo en primer plano como servidor** en `127.0.0.1:9108`; esto es normal, **NO Ctrl+C hasta finalizar las pruebas**, no iniciar otro servidor. A ~17:31:26 respondió HTTP `/healthz` 200, `/api/v1/live` 200, `/metrics` 200; `fresh=true`, `live_monitoring=true`, HQ=1, S1=1, `wan_primary_admin_up=1`, `selected_link=wan-p`, `source_up=1`, eventos down/restored/route_changed=0 **ANTES** de generar falla. **No hay todavía evento WAN real en las últimas salidas recibidas**.

**PRÓXIMA ACCIÓN INMEDIATA SIN REDESPLEGAR B2:** Terminal SSH 2: `sudo -v`, `bash scripts/laboratorio/b2-dualwan-ospf.sh status`, `curl` a live con WAN-P UP, captura **B3_05**, un único `bash ... fail`, aguardar ~4s, consultar `/api/v1/live` y `/api/v1/events` y capturar **B3_06** (down y wan-b). Opcional túnel SSH desde Windows `ssh -N -L 9108:127.0.0.1:9108 netlab360` para screenshot HTML **B3_08**. `bash ... restore`, aguardar 4s, comprobar WAN-P UP/wan-p y eventos **B3_07**. `bash ... down` debe retirar solo recursos B2 válidos; exporter verá topología OFFLINE; detener túnel y Terminal1 con Ctrl+C, puerto 9108 libre, Docker/netns vacíos y ens33/GW intactos, captura **B3_09**. Si fail/restore fallan, diagnosticar y restaurar/retirar sin repetir up ni crear recursos. **No apagar con routers activos**.

**Fuente documentada:** [bitácora de preflight y baseline live](sesiones/2026-10-13-b3-live-precheck-y-baseline-verificada.md). Issues #1/#12/#15/#20/#21 actualizadas con el hito real; **S01 45% provisional**, sin incrementar hasta comprobar fail/restore y limpieza. NO Prometheus scraper ni Alertmanager instalados/validados. El usuario quiere **varios pasos en un mensaje, sin «seguimos» intermedio**, y considera capturas tomadas salvo aviso; no afirmar revisión visual o subida de futuras PNG hasta recibirlas. **GitHub remoto avanza con esta bitácora y checkpoints, pero no hacer pull mientras haya trabajos a medio ejecutar si se desea reducir interferencia; sincronizar al finalizar.**

---


## ACTUALIZACIÓN PRIORITARIA — 2026-10-13 ~16:40 PANAMÁ | B3 LIVE PRECHECK FALLÓ POR BUG, NO FALTAN PROGRAMAS

**Último usuario aportó logs completos de Terminales 1–3; este bloque prevalece sobre anteriores promesas de exporter live.** `git pull` llevó VM a `9defd03` antes de nuevas correcciones. `ast.parse` de `servicios/observabilidad/live_exporter.py` era OK, pero `python3 ... --check` devolvió **`B3_LIVE_PREFLIGHT=ERROR`, `B3_TOPOLOGIA=DEGRADED`, rc=4** al interpretar Docker `error: no such object: nl360-b2-r-hq` en minúsculas como fallo real, cuando era el estado esperado de routers apagados. El código comparaba `"No such object"` con mayúscula. Por el error, `--serve` no abrió puerto `9108`, y `curl: (7) Failed to connect` / túnel Windows `channel ... Connection refused` son consecuencias, **NO falta de programas ni paquetes**.

A las **16:40:11** el usuario ejecutó realmente **un precheck B2 exitoso y un `up --snapshot-confirmado` EXITOSO**: `OSPF_DUAL_FULL: SI`, **dos adyacencias Full por router**, ruta a LAN S1 vía `wan-p`, `RESULTADO_UP_B3=0`. A las **16:40:39** ejecutó otro precheck/`up`, que devolvió `ERROR: recursos previos B2` / RC=3 porque YA había routers desplegados; esta negativa **ES CORRECTA**. **No consta `down` ni `fail/restore` posterior**: NO ejecutar `up` de nuevo ni destruir redes a ciegas; primero verificar `sudo docker ps -a --filter name=nl360-b2-`, marcador `~/netlab360-bootstrap/estado-b2-dualwan/.nl360-owner`, `bash scripts/laboratorio/b2-dualwan-ospf.sh status` solo si marker válido, ens33 y rutas. Evitar túnel Windows hasta tener `ss` mostrando LISTEN en 9108. `sudo` rechazó un primer intento de contraseña en Terminal 2; no representa software faltante.

**Fix YA EN GITHUB, AÚN NO PROBADO POR USUARIO:** [`servicios/observabilidad/live_exporter.py`](../servicios/observabilidad/live_exporter.py) compara salida `.lower()` y distingue contenedor ausente (OFFLINE) de error real de permiso/daemon (DEGRADED); [pruebas unitarias](../tests/test_b3_live_exporter.py) con 5 casos; [auditoría preventiva solo lectura](../scripts/validacion/auditar-dependencias-netlab360.sh); [matriz de herramientas](operaciones/matriz-dependencias-s01.md); [bitácora de fallos y guardas](sesiones/2026-10-13-b3-exporter-preflight-docker-case.md). Primer paso: pull seguro + `bash -n`, `python3 -m unittest discover -s tests -p test_b3_live_exporter.py -v`, `sudo -v`, `bash scripts/validacion/auditar-dependencias-netlab360.sh`, `python3 servicios/observabilidad/live_exporter.py --check`. **No subir puntos del S01 45% solo por fix.**

**Captura B3_05 de intento fallido:** terminal mostró `curl` al puerto sin servidor. Si el usuario la capturó, registrar como `B3_05_Diagnostico_Exporter_No_Escucha.png` y no como éxito. **NO pedir repetir despliegue para la captura**; completar ensayos B3 live con el nuevo código y capturas de éxito después. Git del usuario estaba limpio `9defd03` a las 16:40; tras commits nuevos remoto está por delante, requiere pull.

---


## CHECKPOINT ACTUAL — 13/10/2026 16:26+, EVIDENCIAS COMPLETADAS Y EXPORTER B3 LIVE PREPARADO

**PREVALECE SOBRE LAS NOTAS ANTERIORES QUE DECIAN QUE LOS PNG NO ESTABAN SUBIDOS.**
- Usuario verificó y publicó correctamente en GitHub **19 PNG B1/B2** más manifiesto (`evidencias/capturas/B1_B2_lote01`), commit **[`d62d33b`](https://github.com/recm0708/netlab360/commit/d62d33b3dd5876a795ca2dadc47b2a1474c86104)**, y **5 PNG B3** más manifiesto (`evidencias/capturas/B3_lote02`), commit **[`a21b8f8`](https://github.com/recm0708/netlab360/commit/a21b8f8d1b76c2f7cebfd657213bc4c7c7b21bc2)**. 24 archivos PNG realmente auditados y físicamente en `main`. SHA256 internos correctos, comprobación GitHub de commits confirmó **19 y 5 PNG**. Git del usuario a 16:26:20 `a21b8f8`, `## main...origin/main` limpio, `GIT_SINCRONIZADO: SI`. El problema original de identidad del autor fue corregido **en scope local del repo**, rebase/push sin problemas. Lote 01 y lote 02 cerrados en cuanto a importación; issue #43 ABIERTA para nuevas fases y la imagen B3_04_FINAL.
- Postcheck real `B3_04_FINAL` a las 16:25:50: `PUERTO_8765_LIBRE: SI`, contenedores/netns vacíos, `ens33 UP 192.168.47.40/24`, default `192.168.47.2`, servicios docker/ssh/open-vm-tools activos. Captura B3_04_FINAL considerada tomada por instrucción del usuario, pero **no recibida todavía como PNG**, no está subida.
- **S01 45% estimado y 55% pendiente** (matriz `docs/control/01-avance-s01.md`); API y dashboard **HISTÓRICOS** funcionales y auditados, pero SIN Prometheus, exporter live o alerta WAN en NOC. Issues #1/#12/#15/#20/#21 ABIERTAS.
- **NUEVO ARTEFACTO SOLO VERSIONADO, NO EJECUTADO:** [`servicios/observabilidad/live_exporter.py`](../servicios/observabilidad/live_exporter.py) y [protocolo](../servicios/observabilidad/README.md). Exporter Python de solo lectura `127.0.0.1:9108` consulta Docker/FRR mediante `sudo -n docker inspect`, `nsenter ip`, FIB WAN-P/WAN-B; API `/api/v1/live`, `/api/v1/events`, `/metrics`, `/healthz`, dashboard dinámico `/`; eventos por cambios reales `WAN_PRIMARY_DOWN`, `WAN_PRIMARY_RESTORED`, `WAN_ROUTE_CHANGED` guardados localmente en `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl`. **TODAVÍA NO VALIDADO EN UBUNTU, ni Prometheus real**. Se debe hacer `git pull --ff-only`, `ast.parse` y `sudo -v` misma terminal, `python3 ... --check`, y ejecutar foreground. Solo después, en otra terminal, `bash scripts/laboratorio/b2-dualwan-ospf.sh up --snapshot-confirmado` y secuencia `status/fail/restore/down` **si hay aprobación precheck/Full**, consultando live API y /events tras cada paso. Desplegar WAN únicamente en `--network none` y never alterar VMnet8/ens33. Capturas planificadas B3_05–B3_09. No repetir ensayos anteriores salvo que esta prueba viva los requiera.
- **Advertencia de precisión:** cualquier muestra de WAN es temporal/discreta; no demostrar disponibilidad total ni segundos exactos de convergencia. `/metrics` de exporter no acredita por sí solo scrape de Prometheus, Alertmanager ni alarmas de producción. Si no hay routers, `B3_TOPOLOGIA=OFFLINE` es correcto. El exporter requiere `sudo -n -v` exitoso tras `sudo -v`; sin ello se detiene. No dar por probada implementación hasta recibir salidas reales. No aumentar el 45% solo por crear archivos.
- **IMPORTANTE SOBRE SINCRONIZACIÓN:** usuario en Ubuntu acabó en `a21b8f8` **antes** de nuevos commits de GitHub de esta respuesta: para bajar live_exporter y docs nuevos, usar `git pull --ff-only origin main`; no asumir que el checkout actual contiene script.

---


## CHECKPOINT VIGENTE — 13/10/2026 POST 16:09 | API HISTÓRICA VALIDADA; GIT IDENTIDAD PENDIENTE

**PRIORIDAD DE LECTURA:** [`docs/REANUDAR-AQUI.md`](REANUDAR-AQUI.md). Lote 01 B1/B2 (19 PNG) y lote 02 B3 (5 PNG) **realmente recibidos y visualmente auditados**, registros oficiales SHA-256 `docs/evidencias/01-auditoria-visual-b1-b2-2026-10-13.md` y `docs/evidencias/02-auditoria-visual-b3-2026-10-13.md`. B3 panel NOC **histórico** mostrado en navegador; API /metrics/healthz/baseline OK. Postcheck a 15:52 `PUERTO_8765_LIBRE: NO` fue anterior al postcheck a **16:09:58 `PUERTO_8765_LIBRE: SI`**; contenedores/netns vacíos y ens33/VMnet8 intactos. Cerrar túnel PowerShell con Ctrl+C si sigue abierto.

**Bloqueador actual:** PNG B1/B2 transferidos y `git add` aplicado pero `git commit` FALLÓ por identidad Git no configurada; `git push` sin commit no publicó nada. Stage contiene 19 PNG + CSV. Configurar usuario+correo noreply **solo en este repo**, `git commit`, sincronizar cambios remotos sin forzar historial y hacer push. ZIP B3 de 5 PNG pendiente de transferencia y segundo commit. **No afirmar que los binarios están ya en GitHub.** S01 **45% estimado** (B3 histórico 2/15, sin telemetry live). #1/#12/#15/#20/#35/#43 abiertas.

---


## ACTUALIZACIÓN PRIORITARIA — 13/10/2026 (DESPUÉS DE 15:52) | LOTE 01 DE 19 PNG AUDITADO; API B3 PROBADA, POSTCHECK PENDIENTE

**ESTA SECCIÓN PREVALECE SOBRE LAS MENCIONES HISTÓRICAS "CAPTURAS SUPUESTAS" EN DOCUMENTOS ANTERIORES.**
- **Lote 01 de 19 capturas B1/B2:** archivos **realmente recibidos e inspeccionados visualmente**. Hay registro oficial con nombres canónicos, clasificación de éxito/diagnóstico, observaciones y 19 SHA256 en [`docs/evidencias/01-auditoria-visual-b1-b2-2026-10-13.md`](evidencias/01-auditoria-visual-b1-b2-2026-10-13.md). La issue #43 está actualizada; sigue ABIERTA para otros lotes e importación de bytes PNG al repositorio. Los **PNG aún NO están físicamente subidos al repo**, pero se preparó un ZIP con los 19 sin alterar sus píxeles, los nombres normalizados, manifiesto CSV y registro. SHA256 ZIP `a81a6ceaf8daace88f740d288327231ea6818bac80241d0017d5ca32438bef66`. En el ZIP `B2_06_Arranque_FRR_V2_Exitoso.png` → `B2_06_Diagnostico_FRR_V2_Permisos.png` (resultado original smoke v2=2) y `B2_16_Diagnostico_Convergencia.png` → `B2_16_Medicion_Continua_Convergencia.png` (76/76 muestras y cleanup OK). B2_L2_01, B2_15, B2_16 tienen notas de encuadre; NO repetir ensayo solo por ese detalle.
- **B3 API realmente probada** por usuario (salida de 3 terminales a 15:48–15:52): `B3_SINTAXIS: OK`, `--check` código0 y 76 muestras, `python3 servicios/noc-historico/app.py --serve` escuchó en `127.0.0.1:8765`. `GET /healthz`, `GET /api/v1/baseline`, `GET /metrics`, `GET /` todos **200**, URL inexistente **404**, POST **405**. `/healthz` dice `historical`, `live_monitoring:false`; no confundir con exporter actual, Prometheus desplegado, dashboard de incidente real ni alarma. [Bitácora](sesiones/2026-10-13-b3-api-noc-historico-probada.md). Túnel `ssh -N -L 8765:127.0.0.1:8765 netlab360` iniciado, **imagen de navegador B3_03 todavía NO enviada para validación visual**.
- **PENDIENTE OPERATIVO INMEDIATO:** La salida de B3_04 a las 15:52:24 mostraba **`PUERTO_8765_LIBRE: NO`**, sin salida de Ctrl+C ni `B3_SERVIDOR_DETENIDO=SI`. Detener túnel PowerShell (Ctrl+C), detener Python en Terminal SSH 1 (Ctrl+C), verificar con `ss -H -ltn '( sport = :8765 )'` que puerto no quede ocupado. NO cerrar el postcheck B3 antes de salida de `PUERTO_8765_LIBRE: SI`; no matar procesos ajenos.
- **S01 ~43% provisional**, pendiente de reevaluación tras cierre, evidencia visual de UI y siguientes controles B3; issues #1, #12, #15, #20, #21, #35, #42, #43 ABIERTAS. Git local verificado en `07c2731` **antes de nuevos commits remotos de auditoría**. Hace falta `git pull --ff-only origin main` cuando no haya cambios locales; no repetir smoke FRR/OSPF/ICMP de B2.
- **Próxima incorporación de PNG:** transferir ZIP desde el chat a Windows y Ubuntu, verificar SHA256, extraer en carpeta de evidencias dentro de repositorio, `git add/commit/push` solo tras inspección. No afirmar subida GitHub sin verificar commit real. El usuario enviará las capturas restantes para auditar una segunda tanda; no volver a cuestionar la existencia de las 19 del lote 01.

---


## REANUDACIÓN ACTUAL 13/10/2026 15:29 — B3 DATOS RETROSPECTIVOS OK; API NOC PREPARADA, NO EJECUTADA

**LEER PRIORITARIAMENTE `docs/REANUDAR-AQUI.md`**: el usuario volvió a encender VM, SSH/red/servicios/almacenamiento/mantenimiento APT/Git todo validado; raíz 9%, Docker/netns vacíos, `ens33 192.168.47.40/24` GW `.2` intactos. CSV original 76/76 ICMP `CSV_INTEGRIDAD: OK`; JSON `b3-resumen-convergencia.json` y `b3-metricas-retrospectivas.prom` generados realmente con `B3_ANALISIS_RETROSPECTIVO=OK`. B3_01 tomada por convención del usuario (PNG sin auditar).

**NUEVO EN GITHUB, AÚN NO PROBADO EN UBUNTU:** `servicios/noc-historico/app.py` (API/HTML local solo lectura `127.0.0.1:8765`) y manual `servicios/noc-historico/README.md`, bitácora `docs/sesiones/2026-10-13-b3-linea-base-retrospectiva-validada.md`. Necesita pull/validación/arranque/curl/túnel SSH/stop y postcheck. `/metrics` es histórico y Prometheus no está instalado ni scrapeando; no atribuir incidentes activos, alarmas ni visualización dinámica. S01 43% técnico, 57% pendiente; issues #1/#12/#15/#20/#21/#35/#43 abiertas. Último Git **local** comprobado `c53f0a6` antes de commits remotos B3 de hoy.

---


## ÚLTIMO CHECKPOINT — 13/10/2026 11:52 PANAMÁ | CONVERGENCIA B2 COMPLETADA; CIERRE INMEDIATO

**PUNTO ÚNICO DE CONTINUIDAD:** [`docs/REANUDAR-AQUI.md`](REANUDAR-AQUI.md). El usuario ejecutó con éxito `scripts/laboratorio/b2-dualwan-medicion-continua.py --snapshot-confirmado` a 11:51:41–11:52:40, `RESULTADO_EJECUCION_CONVERGENCIA=0`, 76/76 sondas ICMP exitosas (0 pérdidas observadas), OSPF dual WAN-P→WAN-B→WAN-P. Primer sondeo FIB vio respaldo **0.186s** tras inicio de acción, principal restaurada **10.147s** tras inicio (aproximaciones de sondeo ~0.37s, NO convergencia OSPF exacta). `LIMPIEZA_FINAL=OK`, `CONTENEDORES_B2_RESIDUALES=0`, Docker/netns vacíos y `ens33 192.168.47.40/24`/GW `192.168.47.2` preservados. Logs/CSV locales `17-b2-convergencia-20261013-115141.{log,csv}`, captura B2_16 asumida tomada, auditoría PNG pendiente #43. [Bitácora](sesiones/2026-10-13-b2-convergencia-icmp-continuo-verificada.md).

**S01 ahora 43% técnico estimado, 57% pendiente** ([matriz](control/01-avance-s01.md)), #1/#12/#42/#43/#35 ABIERTAS. Éxito parcial de red **no equivale** a entrega del MVP completo. **Usuario solicitó cerrar SIN ESPERAR A LAS 12:00:** no iniciar pruebas; hacer `git pull --ff-only origin main`, revisar Git limpio/HEAD=origin/main, Docker/netns vacíos, red/servicios, `sync; sudo systemctl poweroff`, esperar VMware Powered Off y luego apagar Windows. **No consta apagado completado todavía.** Los registros locales/PNG no están subidos automáticamente; sus resultados se documentaron en GitHub. No repetir pruebas de hoy.

---


## PUNTO ÚNICO DE REANUDACIÓN — 2026-10-13 11:24 PANAMÁ | S01 42% | B2-L3 ICMP 30/30

**AL RETOMAR, LEER PRIMERO:** [`docs/REANUDAR-AQUI.md`](REANUDAR-AQUI.md), que contiene checklist de resultados probados, rutas exactas de logs, criterios pendientes, links a issues, comandos de sincronización y cierre de las 12:00–12:15. Este checkpoint **supera los encabezados antiguos** de este archivo que indicaban “ping pendiente” o “dual-WAN no ejecutado”.

- **Última PRUEBA REAL:** 13/10/2026 11:22–11:24, `bash scripts/laboratorio/b2-dualwan-ping-lan.sh` con 3 fases `normal/respaldo/restaurada`, dos direcciones de ICMP entre IP LAN dummy 10.70.10.1 ↔ 10.71.10.1: **5/5 + 5/5 por fase, total 30/30 y 0% pérdida durante los sondeos**. Rutas FIB correctas WAN-P→WAN-B→WAN-P, OSPF 2 vecinos Full/Router, `RESULTADO_UP=0`, `RESULTADO_FAIL=0`, `RESULTADO_RESTORE=0`, `RESULTADO_DOWN=0`.
- **Cleanup REAL 11:23:52:** Docker y namespaces sin elementos; `ens33=192.168.47.40/24`, gateway `192.168.47.2`, servicios docker/ssh/open-vm-tools activos. Git limpio hasta checkout local `0f334dc` **antes de nuevos commits remotos**. Logs originales están en `~/netlab360-bootstrap/evidencias`, no subidos a GitHub. Captura B2_15 asumida tomada, revisión visual posterior #43.
- **Nueva bitácora:** [B2-L3 ICMP en 3 estados](sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md). **Matriz:** [S01 avance técnico 42%](control/01-avance-s01.md), 58% pendiente. Fase S01 #1, #42, #12 y #43 todavía ABIERTAS. 43 issues totales, 3 cerradas (#39/#40/#41). La medición de pérdida durante el instante de failover, clientes/servicios reales, telemetría, IaC, LACP/ACL y entregables siguen pendientes.
- **No confundir 30/30 con 0 pérdidas DURANTE cambio WAN:** pings ejecutados después de estabilizar cada ruta. No iniciar más pruebas a partir de las 12:00 Panamá; usuario pidió repo sincronizado y Ubuntu/Windows apagados a más tardar 12:15. El estado de apagado no está confirmado.

---


## HITO CONCLUÍDO — 13/10/2026 11:11 PANAMÁ | DOS ROUTERS OSPF, FAILOVER Y RETORNO OK

**Este estado sustituye planes previos que indicaban dual-WAN no desplegada.** La VM `netlab360-lab` está encendida y administrable por SSH `ssh netlab360`; gestión fija `ens33=192.168.47.40/24`, gateway `192.168.47.2`. **El despliegue dual-WAN se ejecutó Y SE LIMPIÓ**, por lo que **ahora no hay contenedores ni namespaces B2 activos**.

**Prueba REAL aportada por usuario en log completo 415 líneas:** `bash scripts/laboratorio/b2-dualwan-ospf.sh up --snapshot-confirmado` a las 11:03:57, `RESULTADO_DESPLIEGUE=0`, dos routers FRRouting con veth WAN-P/WAN-B, **2 vecinos OSPF Full por router**, `RESULTADO_STATUS=0`; HQ aprendió `10.71.10.0/24` vía `wan-p` `[110/20]`. A 11:09:30 el comando `fail` bajó `wan-p` y comprobó ruta `via 10.78.0.6 dev wan-b`, `[110/110]`, `CONMUTACION_WAN_B: OK (sondeo 1)`, `RESULTADO_FAILOVER=0`. A 11:10:11 `restore` devolvió `wan-p` `via 10.78.0.2`, `RESTAURACION_WAN_P: OK (sondeo 11)`, `RESULTADO_RESTAURACION=0`; sondas no son mediciones precisas de segundos. `down` a 11:11:08 dio `RESULTADO_DOWN=0`, `RESULTADO_B2_LIMPIEZA=0`, Docker/netns vacíos, `ens33` y GW intactos, servicios activos, Git limpio en local **antes de siguientes commits del asistente**.

**Documentos:** bitácora técnica completa `docs/sesiones/2026-10-13-b2-dualwan-ospf-failover-resultado.md`; control de porcentaje actualizado `docs/control/01-avance-s01.md` con **S01 40% estimado** (anterior 30%). #42 y #12 actualizadas, ambas **ABIERTAS**; #1 sigue abierta. Capturas `B2_12_Vecinos_y_Rutas_OSPF_DualWAN.png`, `B2_13_Failover_WAN_Principal_a_Respaldo.png`, `B2_14_Restauracion_WAN_Principal.png` se presumen tomadas por instrucción del usuario; no auditadas visualmente, issue #43.

**Próxima prueba nueva, NO EJECUTADA:** `scripts/laboratorio/b2-dualwan-ping-lan.sh` ya versionado en GitHub para comprobar **ping bidireccional real entre LAN dummy** (`10.70.10.1` ↔ `10.71.10.1`) en estados `normal`, `respaldo`, `restaurada`, con comprobación de `ip route get` esperado y log `16-b2-lan-ping-*.log`. Requiere `up` previo, luego `fail`, luego `restore` y finalmente `down`. No hacer `ping -I lan0` (forzaría una interfaz dummy); usar `-I dirección_local` ya implementado en el script. **Ningún ping LAN ha sido ejecutado en esta sesión todavía**. Si falla: guardar logs y ejecutar rollback `down`, no repetir automáticamente. No confundir rutas FIB con entrega real de paquetes.

**Horario fijo del usuario:** cesar nuevas pruebas a las **12:00** Panamá; sincronizar issues/docs/GitHub y verificar todos los recursos antes 12:10; `sync; sudo systemctl poweroff` y VMware Powered Off, luego Windows apagado antes 12:15. Si falta margen, NO iniciar ensayo. No modificar VMnet8/ens33 ni IP/rutas anfitrión; snapshot VMware base ya confirmado.

---


## SUBHITO 13/10/2026 10:57 PANAMÁ — PRECHECK DUALWAN OK; DESPLIEGUE AÚN NO EJECUTADO

**Estado más reciente, prevalece sobre entrada 10:47:** `bash -n scripts/laboratorio/b2-dualwan-ospf.sh` => `RESULTADO_SINTAXIS=0`; `bash scripts/laboratorio/b2-dualwan-ospf.sh precheck` => `RESULTADO_B2_DUALWAN_PRECHECK=0` y `RESULTADO_PRECHECK_DUALWAN=0`; validador IPAM B1 OK y imagen FRR 10.7.1 amd64 en caché. `sudo docker ps -a` sin contenedores, `sudo ip netns list` sin namespaces; `ens33=192.168.47.40/24` con default `192.168.47.2`; Git limpio hasta commit `ba809da` **antes del commit remoto posterior**. Log local `~/netlab360-bootstrap/evidencias/15-b2-dualwan-precheck-20261013-105732.log`; captura `B2_11_Precheck_Despliegue_DualWAN.png` asumida tomada, pendiente de revisión visual #43.

**Actualización remota posterior al precheck:** `scripts/laboratorio/b2-dualwan-ospf.sh` reforzado para verificar la **ruta real** `dev wan-b` después de failover y `dev wan-p` después de restauración, sondeos acotados. Usuario debe hacer `git pull --ff-only` y `bash -n` ANTES de `up`; no declarar implementada una prueba no realizada. El comando `up` incluye su propio precheck y, si falla durante inicialización, registra diagnóstico y limpia recursos marcados propios. Mantener fail/restore condicionados a `up` correcto, 2 vecinos Full y rutas OSPF. Una vez acabada la prueba invocar `down`, verificar cero contenedores/netns y ens33 intacta.

**Ventana de cierre:** iniciar preservación de logs/commits/issues y sincronización a las 12:00, `sync; sudo systemctl poweroff` aproximadamente 12:10, Windows apagado antes 12:15. No iniciar pruebas nuevas desde 12:00. El usuario pidió **más pasos agrupados por respuesta**, idealmente 7–9 pasos, sin saturar ni perder puntos de corte seguros. Todas las capturas indicadas se asumen tomadas salvo negativa expresa del usuario, pero no revisadas/subidas.

---


## REANUDACIÓN VERIFICADA — 2026-10-13 10:47 PANAMÁ | B2 ORQUESTADOR PREPARADO, NO EJECUTADO

**PREVALECE SOBRE NOTAS DE LAS 10:42:** Usuario arrancó VM `NETLAB360-Ubuntu-Desktop`, desde PowerShell `ssh netlab360` con llave/contraseña de la clave, Ubuntu 26.04.1 LTS, kernel `7.0.0-38-generic`, hostname `netlab360-lab`, uptime 3min, red `ens33 192.168.47.40/24` y default `192.168.47.2`, servicios docker/ssh/open-vm-tools activos, **sin contenedores y sin netns**.

Mantenimiento preventivo del invitado a las 10:47: `sudo apt update` OK, `apt list --upgradable` sin entradas, `apt-get -s upgrade` 0 actualizaciones, `dpkg --audit` vacío y **no se requiere reinicio**. Aviso 4 ESM Apps opcionales no interfiere con APT ordinario. `git pull --ff-only origin main` adelantó `c519a02..e9460ee`; `git status --short --branch` mostró `## main...origin/main`, sin cambios. Esto fue **antes de nuevos commits de GitHub**: repetir pull al retomar.

**Nuevo artefacto GitHub, todavía NO probado en Ubuntu:** `scripts/laboratorio/b2-dualwan-ospf.sh`. Acciones `precheck`, `up --snapshot-confirmado`, `status`, `fail`, `restore`, `down`. Recupera permisos/capacidades del smoke FRR v5, contenedores `nl360-b2-r-hq`/`nl360-b2-r-s1`, `--network none`, pares veth exclusivos, loopbacks `10.79.0.1/.2`, WAN-P `10.78.0.1/.2/30` costo10, WAN-B `10.78.0.5/.6/30` costo100, dummy LAN HQ/S1 y OSPF área0. Incluye guardia de propietario para `down`, rollback del `up` fallido y comprobación ens33/gateway. Su sintaxis y ejecución **aún deben comprobarse por el usuario**, no declarar adyacencias ni rutas comprobadas.

**Comandos INMEDIATOS para el usuario (solo precheck):**
```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
bash -n scripts/laboratorio/b2-dualwan-ospf.sh
grep -nE 'precheck\)|up\)|status\)|fail\)|restore\)|down\)|snapshot-confirmado|RESULTADO_B2_DUALWAN_PRECHECK' scripts/laboratorio/b2-dualwan-ospf.sh
bash scripts/laboratorio/b2-dualwan-ospf.sh precheck
echo "RESULTADO_PRECHECK_DUALWAN=$?"
git status --short --branch
```
El `precheck` es de lectura y **no crea routers ni WAN**. Revisar su salida antes de autorizar `up`. Log generado `~/netlab360-bootstrap/evidencias/15-b2-dualwan-precheck-*.log`.

**Ventana de cierre:** cesar pruebas nuevas 12:00 Panamá, dejar GitHub sincronizado local/remoto y evidencias guardadas ~12:10, apagar `sync; sudo systemctl poweroff`, comprobar VMware Powered Off y apagar Windows antes de las 12:15. Se programó recordatorio 12:00. S01 ~30% ponderado, #1 ABIERTA, #42 ABIERTA, #12 y #43 ABIERTAS; #39/#40/#41 CERRADAS. Última validación funcional: FRR v5 local exitoso, no repetir por rutina.

**Guía de capturas:** todas las capturas indicadas se presumen tomadas salvo aviso del usuario; dar comandos y límites INICIO/FIN y nombre PNG por prueba. PNG aún no auditados visualmente ni subidos. Bitácora `docs/sesiones/2026-10-13-reanudacion-precheck-y-dualwan.md`.

---


## SESIÓN EN CURSO — 2026-10-13 10:42 PANAMÁ | CIERRE OBLIGATORIO ANTES DE 12:15

**Última instrucción del usuario:** continuar NETLAB360 ahora, pero salir a las **12:15 p. m.**; todo debe quedar sincronizado en GitHub y Ubuntu/Windows apagados. Se creó un aviso puntual para **12:00**, momento en que **DEJAMOS DE INICIAR PRUEBAS**. Esta nota **NO significa que el equipo haya sido encendido o que los comandos hayan sido ejecutados**, porque aún faltan sus salidas del arranque de hoy.

### Estado técnico y próximos pasos inmediatos
- Último éxito comprobado (12/10, 23:57): **smoke FRR v5** con zebra/ospfd reales, OSPF router-id 10.79.0.254, `RESULTADO_SMOKE_FRR_V5=0`, limpieza completa. Evitar repetir smoke v1–v5.
- S01 **30% estimado**, issues #39/#40/#41 cerradas, #1 S01 abierta, #42 FRR dual-WAN abierta, #12 incidente/alarma abierta, #43 auditoría de capturas abierta. Snapshot `NETLAB360-BASE-HERRAMIENTAS` confirmado por operador; no crear otro por rutina.
- Primera tarea usuario: encender exclusivamente `NETLAB360-Ubuntu-Desktop`, conectar `ssh netlab360`, confirmar `ens33=192.168.47.40/24`, gateway `.2`, servicios `docker/ssh/open-vm-tools` activos, sin Docker/netns residuales, recursos/kernel.
- Mantenimiento tras reanudar: `sudo apt update`, `apt list --upgradable`, `sudo apt-get -s upgrade`, `sudo dpkg --audit`, verificar `/run/reboot-required`; revisar resultados antes de hacer upgrade/reiniciar.
- Sincronizar al inicio con `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main && git status --short --branch`. **Nuevo documento ya versionado, no ejecutado:** `docs/arquitectura/04-b2-dualwan-plan-ejecucion-segura.md`, que define 2 contenedores R-HQ/S1 `--network none`, pares veth WAN-P/WAN-B, OSPF área0, costos10/100, validación y rollback sin tocar `ens33`.
- Si el precheck/actualización se completa sin incidentes y queda tiempo, preparar orquestador aislado `up/status/down` y prueba WAN; no declarar resultados hasta ejecutar y recibir logs.

### Rutina cierre 12:00–12:15 (prioritaria, aunque prueba incompleta)
1. **12:00:** terminar nuevas pruebas. Si alguna falla, salvar logs; no intentar corregir y reejecutar contra reloj. Actualizar issues #42/#1, reporte y esta continuidad con resultados confirmados.
2. **Hasta 12:10:** actualizar commits GitHub (asistente vía conector si procede), luego usuario `git pull --ff-only origin main`, verificar `git status -sb`, `git rev-parse HEAD`, `git rev-parse origin/main`; confirmar sin cambios locales y misma revisión. Preservar logs locales; los PNG se presumen tomados y se auditarán después, NO se han subido automáticamente.
3. Comprobar `sudo docker ps -a`, `sudo ip netns list`, `ip -4 -br addr show ens33`, `ip -4 route show default`, `systemctl is-active docker ssh open-vm-tools`. Si hubo recursos aislados de B2, ejecutar su **rollback específico** antes de apagar; no forzar eliminación de recursos ajenos.
4. **12:10–12:15:** `sync; sudo systemctl poweroff`, comprobar estado **Powered Off** de VMware Workstation y solo después apagar Windows desde Inicio. Cierre SSH normal durante poweroff. **No prometer apagado remoto hecho por el asistente.**
5. Si trabajo no concluido a las 12:00, continuar otro día desde el hito exacto documentado y no aumentar 30% sin nueva evidencia aceptada.

---


## PAUSA OPERATIVA SOLICITADA — 2026-10-13 01:17 Panamá (APAGADO PENDIENTE DE CONFIRMACIÓN)

El usuario indicó que **apagará la VM NETLAB360-Ubuntu-Desktop para descansar** y retomará más tarde el 13/10/2026. Esta entrada es un **plan de pausa**, NO una confirmación de que ya se ejecutó el apagado. Los comandos recomendados para la VM Ubuntu son:

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git status --short --branch
sudo docker ps -a
sudo ip netns list
ip -4 -br address show ens33
ip -4 route show default
systemctl is-active docker ssh open-vm-tools
sync
sudo systemctl poweroff
```

Si `git pull --ff-only` falla, o hay cambios Git no identificados, **revisar antes de apagar y no forzar operaciones Git**. Docker no debería tener contenedores del ensayo después del cleanup v5; verificar y no eliminar recursos ajenos. En VMware esperar hasta **Powered Off**; no usar Power Off forzado con Ubuntu encendido. El corte de SSH durante `poweroff` es esperado.

Al reanudar, encender exclusivamente `NETLAB360-Ubuntu-Desktop` y conectar desde Windows por `ssh netlab360`. Realizar verificación de inicio, mantenimiento preventivo proporcionado al usuario sin alterar configuraciones, `git pull --ff-only`, salud servicios/docker/red/almacenamiento. Leer la sección **ESTADO VIGENTE Y REANUDACIÓN — S01 30%** más abajo: FRRouting v5 YA PASÓ (zebra/ospfd y OSPF local), no repetir smoke v1–v5 por inercia. Próximo desarrollo funcional: topología HQ/S1 con dos WAN aisladas, OSPF Full, failover/restauración y evidencias.

Estado de seguimiento antes de apagar: S01 **~30% estimado**, [#1](https://github.com/recm0708/netlab360/issues/1) ABIERTA; issues #39/#40/#41 cerradas, #42 dual WAN ABIERTA, #12 incidente/observabilidad ABIERTA, #43 auditoría posterior de capturas ABIERTA. Capturas solicitadas se presumen tomadas salvo aviso del usuario; pendientes de revisión visual, no subir tokens, claves ni OVA sin sanitizar.

---


## ESTADO VIGENTE Y REANUDACIÓN — S01 30% ESTIMADO, FRR V5 SUPERADO (2026-10-12 23:57 PANAMÁ)

**LEER ANTES DE CUALQUIER APARTADO HISTÓRICO DE ESTA PÁGINA.** Proyecto privado GitHub `recm0708/netlab360`, rama main; Ubuntu Desktop 26.04.1 LTS en VMware Workstation Pro, VM `netlab360-lab`, usuario `rc-aa-ec`, SSH desde Windows `ssh netlab360`, `ens33=192.168.47.40/24`, gateway `192.168.47.2`. Snapshot `NETLAB360-BASE-HERRAMIENTAS` **confirmado por el usuario**, no volver a pedirlo. No modificar VMnet8, ens33, rutas host ni NetworkManager en laboratorios.

### Hito nuevo observado y probado

**SMOKE FRROUTING v5 SATISFACTORIO, ejecución 2026-10-12 23:57:25 (-05:00).** Script `scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh --snapshot-confirmado`. Verificados:
- `FRR_MOUNT_READABLE: SI`, `FRR_CRASHLOG_WRITABLE: SI`, `FRR_PID_DIR_WRITABLE: SI`; configuraciones `daemons`/ `frr.conf`/ `vtysh.conf` con UID/GID correctos.
- `FRR_DAEMONS_ACTIVOS: SI (zebra, ospfd; intento 1)` y procesos mgmtd/zebra/ospfd/staticd/watchfrr realmente visibles; `vtysh -b` carga configuración.
- `OSPF_CONTROL_PLANE: OK`, `OSPF Routing Process, Router ID: 10.79.0.254`. **No hay áreas adjuntas, interfaces WAN ni vecinos; este smoke no equivale a OSPF entre routers.**
- `PRUEBA_SMOKE_FRR_V5: OK`, `RESULTADO_SMOKE_FRR_V5=0`, `RESULTADO_EJECUCION_FRR_V5=0`; limpieza: 0 contenedores, 0 namespaces; ens33 .40 y gateway .2, docker/ssh/open-vm-tools activos, Git local limpio hasta `afbd7f5` **antes de los últimos commits remotos**.
- Bitácora publicada `docs/sesiones/2026-10-12-smoke-frr-v5-exitoso.md`, log ORIGINAL LOCAL `~/netlab360-bootstrap/evidencias/14-b2-frr-smoke-v5-20261012-235725.log`. Evidencia `B2_10_Arranque_FRR_V5_Verificado.png` **considerada tomada por convención del usuario**, aún no auditada visualmente ni subido PNG a GitHub. Capturas anteriores también se asumen tomadas, salvo aviso del usuario.
- Pruebas históricas smoke v1/v2/v3/v4 fallaron por disponibilidad, permisos de configuración, lectura DAC, creación PID y `CAP_SYS_ADMIN` faltante, respectivamente. **NO REEJECUTAR** versiones anteriores: v5 ya demostró arranque. Retener registros como trazabilidad.

### Control formal de fases e issues

**S01 sigue ABIERTA** en [#1](https://github.com/recm0708/netlab360/issues/1); estimación ponderada **30% completado / 70% pendiente**, no cifra oficial de docente. Metodología y pesos en `docs/control/01-avance-s01.md`, y checklist de fase en `backlog/semanas/01-semana-1.md`. Semanas planeadas 5–11/10, retraso registrado; no mover automáticamente S02–S08.

**Al corte actual, 43 issues: 3 cerradas y 40 abiertas.**
- **CERRADAS:** [#39](https://github.com/recm0708/netlab360/issues/39) IPv4 fija; [#40](https://github.com/recm0708/netlab360/issues/40) GitHub CLI y repositorio; [#41](https://github.com/recm0708/netlab360/issues/41) herramientas base/snapshot VMware.
- **SUBPRUEBAS COMPLETADAS en issues ABIERTAS:** B1 IPAM YAML draft sin colisiones #11/#16; B2-L2 VLAN110/120 conectividad-aislamiento-restauración #30/#12; smoke B2 FRR local #42 (v5 code0). **No cerrar estas issues hasta cumplir sus criterios integrales.**
- **ABIERTAS IMPORTANTES:** #42 configurar routers HQ/S1 y dual WAN OSPF con vecinos/rutas/failover; #12 incidente con telemetría, alarma y dashboard; #38 hardening SSH/documentos; #10 y #34 verificaciones de recursos/compatibilidad definitivas; #35 informe/bitácora/manual; #36 rúbrica; #43 **auditoría visual futura de capturas**. #1 S01 solo se cerrará tras criterios completos o recorte de alcance aprobado.
- La captura debe incluir comando de consulta, fecha/hostname, log original y marcadores literales **INICIO CAPTURA / FIN CAPTURA** con nombre PNG exacto. **Todas las capturas solicitadas se consideran tomadas salvo aviso en contrario**, pero revisión gráfica y subida a GitHub siguen pendientes (#43). No usar `clear` para construirlas.

### Siguiente avance funcional: B2-L3 dos routers con WAN dual

1. `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`; verificar IP/servicios/Docker y preservar VMnet8.
2. Usar el éxito de smoke FRR v5 como patrón de permisos/capacidades para desplegar **dos contenedores aislados** `R-HQ`, `R-S1`. Versionar scripts `up/status/down` con rollback y limpieza segura por nombre prefijado `nl360-`, sin alterar interfaces del host ajenas al laboratorio.
3. Usar WAN-P `10.78.0.0/30` (HQ .1, S1 .2; costo OSPF 10) y WAN-B `10.78.0.4/30` (HQ .5, S1 .6; costo100). Loopbacks `10.79.0.1/32` y `10.79.0.2/32` y prefijos LAN en IPAM; OSPF área0.
4. Validar interfaces/veth, vecinos **Full**, rutas de prefijos remotos, selección primaria; cortar WAN-P, medir migración a WAN-B, restaurar; preservar logs y capturas desde/hasta. En cada subhito significativo actualizar #42 y continuidad; luego integrar alarmas/dash #12.
5. No llamar fase terminada ni avanzar por defecto a S02–S08. No prometer disponibilidad de datos ni rutas inexistentes.

**Documentos clave:** `README.md`, `docs/control/01-avance-s01.md`, `backlog/semanas/01-semana-1.md`, `docs/05-plan-operativo-y-pausas.md`. Los registros antiguos de esta misma página son cronológicos y pueden contener apartados “pendiente” ya superados: **esta ancla tiene prioridad**.

**Seguridad:** credencial GitHub CLI permanece en el guest; nunca publicar tokens, claves privadas, `~/.config/gh/hosts.yml` ni OVA no sanitizada. Antes de exportar, revocar/retirar secretos y validar reimportación+SHA256.

---


## PUNTO DE REANUDACIÓN MÁS RECIENTE — 2026-10-12 23:32, smoke v4 reveló CAP_SYS_ADMIN; v5 PREPARADA

**Priorizar este bloque al retomar.** Proyecto NETLAB360 privado `recm0708/netlab360`, rama `main`. Usuario trabaja en Ubuntu Desktop 26.04.1 LTS de VMware Workstation Pro; hostname `netlab360-lab`, cuenta `rc-aa-ec`, SSH desde Windows `ssh netlab360`, gestión `ens33=192.168.47.40/24`, GW `192.168.47.2`. **NO tocar VMnet8, ens33, NetworkManager ni rutas del anfitrión.** Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` confirmado expresamente por usuario; #41 cerrada.

### Últimos resultados REALES
- B0 Ubuntu/herramientas/GitHub/Docker verificados; B1 IPAM propuesto HQ/S1 y S2 reservada, 9 VLAN/2 WAN, sin conflictos activos. B2-L2 Linux bridge y VLAN 110: pings 3/3, aislamiento VLAN 120, retorno 3/3, limpieza. Imagen FRRouting oficial `quay.io/frrouting/frr:10.7.1` amd64 descargada.
- Smoke v1 falló por tiempo de espera; primer v2 por grep sin sudo y segundo v2 por imposibilidad de leer `daemons`. V3 `FRR_MOUNT_READABLE: SI` pero `watchfrr.pid` no escribible. **Última prueba v4 (2026-10-12 23:32:22 Panamá):** script `b2-frr-smoke-v4-pid-aislado.sh` ejecutado, resultado `FRR_MOUNT_READABLE: SI`, `FRR_PID_DIR_WRITABLE: SI`, `VTYSH_DISPONIBLE: SI (intento 1)`. **No es éxito:** `show ip ospf` indicó `ospfd is not running`; logs mostraron `privs_init: initial cap_set_proc failed: Operation not permitted` para mgmtd/zebra/ospfd, `Wanted caps: cap_net_admin,cap_net_raw,cap_sys_admin=p`, `Have caps:` sin `cap_sys_admin`. También errores al crear `/var/tmp/frr`, falta `/etc/frr/vtysh.conf` y socket staticd denegado. `RESULTADO_SMOKE_FRR_V4=1`. FRR NO probado operativo; no hay WAN, vecinos ni failover.
- Cleanup v4: cero contenedores y netns, `ens33 .40/24`, default vía `.2`, `docker/ssh/open-vm-tools` activos, Git local `## main...origin/main` limpio hasta `e458944` antes de commits remotos. Log `~/netlab360-bootstrap/evidencias/13-b2-frr-smoke-v4-20261012-233222.log`, bitácora GitHub `docs/sesiones/2026-10-12-smoke-frr-v4-capacidades.md`.
- **Capturas**: el usuario estableció explícitamente que **todas las capturas solicitadas están tomadas salvo que diga lo contrario**; conserva capturas por fecha/identificador y más adelante enviará conjunto PNG para revisión de contenido, numeración, calidad y correcciones. No insistir en preguntar si fueron tomadas. Las capturas NO constan incorporadas al repositorio; no confundir declaración de toma con verificación visual/subida. B2_09 se llama `B2_09_Diagnostico_FRR_V4.png`; no nombre de éxito.
- **Estado de GitHub**: issue #42 abierta para arranque FRR y topología R-HQ/R-S1, #12 abierta para fallo WAN y observabilidad, #1 S01 abierta, #41 cerrada. Esta ancla se actualiza después de subhitos. Cada captura: comando de vista limpia sin `clear`, INICIO y FIN literales, nombre PNG, qué resultado debe verse; si la salida no cabe, dividirla en dos capturas.

### Siguiente artefacto ya versionado, **NO ejecutado**
`scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh` (**NO repetir v1-v4**). Implementa:
1. Configuración `daemons` zebra=yes/ospfd=yes y archivos `daemons`, `frr.conf`, `vtysh.conf` con propiedad/permisos FRR correctos.
2. Verifica lectura en contenedor aislado (`FRR_MOUNT_READABLE: SI`), escritura PID en tmpfs `/run/frr` (`FRR_PID_DIR_WRITABLE: SI`) y escritura `/var/tmp/frr` por usuario frr (`FRR_CRASHLOG_WRITABLE: SI`).
3. Smoke efímero en Docker `--network none`, sin host networking ni `--privileged`, agrega específicamente `CAP_SYS_ADMIN` por requisito demostrado de daemons, `DAC_OVERRIDE` por acceso DAC a sockets (capacidad SYS_ADMIN es amplia, solo en VM aislada).
4. Ya NO considera `vtysh show version` suficiente: verifica procesos reales `zebra` y `ospfd` por `/proc/*/comm`, aplica `vtysh -b`, valida `show ip ospf`, captura inspect/procesos/logs antes de limpiar; no crea WAN ni L2.

**Comandos para reanudar:**
```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
bash -n scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh
grep -nE 'CRASH_TMPFS|SYS_ADMIN|DAC_OVERRIDE|FRR_DAEMONS_ACTIVOS|RESULTADO_SMOKE_FRR_V5' scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh
bash scripts/laboratorio/b2-frr-smoke-v5-demonios-verificados.sh --snapshot-confirmado
echo "RESULTADO_EJECUCION_FRR_V5=$?"
sudo docker ps -a
sudo ip netns list
ip -4 -br addr show ens33
ip -4 route show default
```
Se ejecuta **UNA sola vez**, después de confirmar `bash -n`. Si da error, no repetir hasta evaluar log `~/netlab360-bootstrap/evidencias/14-b2-frr-smoke-v5-*.log`. Si funciona, no equivale aún a validar vecinos OSPF: solo plano de control local sin WAN.

**Captura siguiente:** `B2_10_Arranque_FRR_V5_Verificado.png` si y solo si `FRR_MOUNT_READABLE: SI`, `FRR_PID_DIR_WRITABLE: SI`, `FRR_CRASHLOG_WRITABLE: SI`, `FRR_DAEMONS_ACTIVOS: SI`, `OSPF_CONTROL_PLANE: OK`, `RESULTADO_SMOKE_FRR_V5=0`. Si falla: `B2_10_Diagnostico_FRR_V5.png`. Mostrar marcadores exactos INICIO/FIN CAPTURA B2_10, fecha/hostname y ruta log; no presentar valores esperados como comprobados.

**Continuidad:** actualizar issues #42/#12, bitácora y esta ancla tras prueba. Preferencia de usuario: varios pasos/comandos juntos, no pausas por microcomando, snapshots ya confirmados, no guardar OAuth/token/contraseñas ni publicar OVA privada. **NO instalar nuevos componentes ni crear WAN antes de smoke local OK.**

---


## ANCLA DE REANUDACIÓN — 12/10/2026 23:18 Panamá, V3 FALLÓ EN PID, V4 PREPARADA NO EJECUTADA

**ESTADO MÁS RECIENTE; LEER PRIMERO.** Proyecto NETLAB360, repo privado `recm0708/netlab360`, Fase S01 abierta, issue #42 para FRR/OSPF, issue #12 para incidente/alarma/dashboard. Snapshot privado VMware `NETLAB360-BASE-HERRAMIENTAS` **CONFIRMADO por usuario**, #41 cerrada. No solicitar repetir snapshot.

**Última prueba REAL (v3, 12/10/2026 23:17:30):** `bash scripts/laboratorio/b2-frr-smoke-v3-verificacion-acceso.sh --snapshot-confirmado`, IPAM válido, `FRR_MOUNT_READABLE: SI` con `daemons` 0640 frr:frr y `frr.conf` 0660 frr:frrvty. Pero Docker `exited ExitCode=1`, error textual `WATCHFRR: Can't create pid lock file /var/run/frr/watchfrr.pid (Permission denied), exiting`, `RESULTADO_SMOKE_FRR_V3=4`. **NO hay zebra/ospfd/vtysh funcionando ni vecinos OSPF**. Rollback correcto: Docker sin contenedores, cero namespaces; `ens33=192.168.47.40/24`, gateway `192.168.47.2`, docker/ssh/open-vm-tools activos, Git local limpio hasta `7cc979a` antes de nuevos commits.
 
**Pruebas anteriores:** B0 herramientas instaladas/validadas, B1 IPAM HQ+S1, S2 reservado, VLAN/IPAM sin choques; B2-L2 VLAN 110 conectividad 3/3, aislamiento VLAN 120, restauración 3/3. FRR `quay.io/frrouting/frr:10.7.1` amd64 imagen descargada. Smoke v1 timeout, primer v2 falló lectura grep sin sudo, segundo v2 falló lectura `daemons` dentro del contenedor; v3 corrigió lectura pero reveló fallo de escritura de PID. No repetir v1/v2/v3. No tocar ens33/VMnet8/NetworkManager.

**Log v3:** `~/netlab360-bootstrap/evidencias/12-b2-frr-smoke-v3-20261012-231730.log`. Usuario mostró en terminal marcadores `INICIO CAPTURA B2_08` y `FIN CAPTURA B2_08` con código 4 y montaje sí legible; **NO confirmó que guardara captura PNG B2_08**. Si se tomó debe nombrarse `B2_08_Diagnostico_FRR_V3.png`. Bitácora GitHub `docs/sesiones/2026-10-12-smoke-frr-v3-error-pid.md`. Repositorio GitHub contiene RESÚMENES, no los logs locales ni las capturas PNG.

**Nueva variante v4 (EN GITHUB, todavía no ejecutada):** `scripts/laboratorio/b2-frr-smoke-v4-pid-aislado.sh`. Monta tmpfs exclusivo **del contenedor** en `/run/frr`, UID0/GID101 modo0770 para permitir que lanzador root y grupo frr creen archivos PID; verifica primero `FRR_MOUNT_READABLE: SI`, luego escritura real `FRR_PID_DIR_WRITABLE: SI`. Solo entonces crea contenedor temporal `--network none` y habilita `zebra=yes`, `ospfd=yes`. Retira capacidad `SYS_ADMIN` del smoke; conserva capacidades explícitas restantes, guarda docker inspect/logs antes de limpiar; no configura WAN ni altera `/run/frr` del host. Esta es **propuesta de corrección**, no éxito demostrado.

**PASOS AL RETOMAR EN UBUNTU:**
```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
bash -n scripts/laboratorio/b2-frr-smoke-v4-pid-aislado.sh
grep -nE 'PID_TMPFS|FRR_PID_DIR_WRITABLE|FRR_MOUNT_READABLE|RESULTADO_SMOKE_FRR_V4' scripts/laboratorio/b2-frr-smoke-v4-pid-aislado.sh
bash scripts/laboratorio/b2-frr-smoke-v4-pid-aislado.sh --snapshot-confirmado
echo "RESULTADO_EJECUCION_FRR_V4=$?"
sudo docker ps -a
sudo ip netns list
ip -4 -br addr show ens33
ip -4 route show default
```
**Si falla:** no repetir. Revisar `~/netlab360-bootstrap/evidencias/13-b2-frr-smoke-v4-*.log`, estado y error original; actualizar #42 y esta ancla antes de otro ensayo.

**Captura siguiente:** `B2_09_Arranque_FRR_V4_Verificado.png` solo con `FRR_MOUNT_READABLE: SI`, `FRR_PID_DIR_WRITABLE: SI`, `VTYSH_DISPONIBLE: SI`, `RESULTADO_SMOKE_FRR_V4=0`; si error, `B2_09_Diagnostico_FRR_V4.png`. Mostrar comando de consulta, fecha/hora, hostname, ruta al log original, marcadores exactos INICIO/FIN. No usar `clear`. Usuario desea instrucciones **desde tal línea hasta tal línea**. En respuestas dar varios pasos/comandos agrupados y documentación frecuente.
 
**Siguiente hito:** solo si smoke v4 correcto, implementar dos routers R-HQ y R-S1 con FRR en espacios aislados, WAN-P `10.78.0.0/30` costo10, WAN-B `10.78.0.4/30` costo100, loopbacks `10.79.0.1/32` y `10.79.0.2/32`, OSPF área0, pruebas de fallo/restauración; telemetría/dashboard aparte. No declarar S01 terminada. No almacenar credenciales GitHub/OVA en repo.

---


## ÚLTIMA SITUACIÓN — 2026-10-12 23:09 (Panamá) — smoke FRR v2 ExitCode=1; v3 PREPARADA, NO EJECUTADA

**Esta sección tiene prioridad al retomar una conversación.** Proyecto NETLAB360, repositorio privado recm0708/netlab360; fase S01 ABIERTA. Usuario requiere conservar en GitHub la trazabilidad y recibir **múltiples pasos por respuesta**, delimitando cada captura INICIO/FIN con nombre PNG y qué debe verse. Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` **CONFIRMADO por usuario**, issue #41 cerrada. No volver a preguntar ni crear de nuevo.

- Infraestructura validada: Ubuntu Desktop 26.04.1 LTS en VMware Workstation Pro, VM `netlab360-lab`, usuario `rc-aa-ec`, SSH desde Windows PowerShell `ssh netlab360`, `ens33 192.168.47.40/24` gateway `192.168.47.2`. Docker 29.9.0, Compose 5.6.0, Ansible 2.20.1, OpenTofu 1.13.1, Node 24, GitHub CLI autenticado. Nunca tocar ens33/NetworkManager/VMnet8 durante ensayos.
- B1 IPAM válido: HQ y S1 propuestas, S2 reservada, 9 VLAN y WAN dual; B2-L2 Linux bridge: VLAN 110 conectividad 3/3, VLAN 120 aislamiento, restauración 3/3; rollback OK. Evidencias PNG de B1/B2-L2 previamente informadas por usuario, no aseguradas como subidas a Git.
- Imagen `quay.io/frrouting/frr:10.7.1` amd64 descargada; binarios zebra/ospfd/vtysh presentes, entrypoint tini/docker-start. OSPF aún no operativo.
- Smoke v1 histórico falló tiempo de espera `RESULTADO_SMOKE_FRR=4`. Primer v2 falló antes de Docker con `grep: Permiso denegado`, código 2; corregido con `sudo grep`. **Segundo v2 ejecutado 12/10 23:08:48:** archivos temporales `daemons` 640, UID100/GID101, `frr.conf` 660, UID100/GID102. Docker inició contenedor `nl360-frr-smoke-v2`, que salió inmediato `ExitCode=1`; log: `cannot run : /etc/frr/daemons does not exist`; `RESULTADO_SMOKE_FRR_V2=4`. Postcheck 0 contenedores y namespaces, IP y ruta ens33 intactas, servicios activos y Git `main...origin/main` limpio antes de commits remotos.
- **Causa probable basada en fuente 10.7.1**: `/usr/lib/frr/frrcommon.sh` comprueba `[ -r "$C_PATH/daemons" ]`; informa inexistencia si no legible. El proceso de entrada corre como root pero el contenedor fue lanzado con `--cap-drop ALL` sin capacidades DAC para leer fichero 640 propiedad frr. **No atribuir fallo definitivamente al montaje físico sin comprobar lectura.** Fuente: https://fossies.org/linux/frr/tools/frrcommon.sh.in y https://docs.frrouting.org/en/latest/setup.html.
- Evidencia log local `~/netlab360-bootstrap/evidencias/11-b2-frr-smoke-v2-20261012-230848.log`, vista `INICIO CAPTURA B2_07` a `FIN CAPTURA B2_07` producida en consola; **usuario no confirmó PNG B2_07**. Bitácora GitHub `docs/sesiones/2026-10-12-smoke-frr-v2-salida-exit1.md`.
- **Nueva script v3 EN GITHUB, AÚN NO EJECUTADA:** `scripts/laboratorio/b2-frr-smoke-v3-verificacion-acceso.sh` agrega primero contenedor de lectura `--network none` con bind mount readonly y `CAP_DAC_READ_SEARCH`, exige `FRR_MOUNT_READABLE: SI`, mantiene permisos 640/660; arranque FRR aislado con `CAP_DAC_READ_SEARCH` adicional; observa `vtysh`, OSPF, docker inspect/logs antes de cleanup. `CAP_SYS_ADMIN` presente (amplio, restringir a VM propia y revisar posteriormente).
- **INSTRUCCIONES PARA CONTINUAR:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/laboratorio/b2-frr-smoke-v3-verificacion-acceso.sh
  grep -nE 'FRR_MOUNT_READABLE|DAC_READ_SEARCH|RESULTADO_SMOKE_FRR_V3' scripts/laboratorio/b2-frr-smoke-v3-verificacion-acceso.sh
  bash scripts/laboratorio/b2-frr-smoke-v3-verificacion-acceso.sh --snapshot-confirmado
  echo "RESULTADO_EJECUCION_V3=$?"
  sudo docker ps -a
  sudo ip netns list
  ip -4 -br addr show ens33
  ```
- **Captura a indicar explícitamente:** `B2_08_Arranque_FRR_V3_Verificado.png` solo si lectura+vtysh+OSPFD+resultado 0; de lo contrario `B2_08_Diagnostico_FRR_V3.png`. Vista de log `12-b2-frr-smoke-v3-*.log` delimitada INICIO/FIN, fecha/hostname, test de montaje y resultado. Si falla, no repetir sin analizar log.
- Issues #42 (FRR OSPF WAN dual) y #12 (incidente WAN/dashboard) ABIERTAS, #1 S01 ABIERTA, #41 CERRADA. No crear topologías ni redes nuevas aún. Documentar tras siguiente hito real.
- Política de pausas: después de hitos sustanciales, no cada comando. Nunca subir tokens OAuth ni distribuir snapshot/OVA privado sin sanitizar.

---


## ESTADO INMEDIATO — 2026-10-12, 22:35 Panamá | SMOKE FRR V2 FALLÓ ANTES DE DOCKER; CORREGIDO EN GITHUB

**Leer primero al retomar.** Usuario quiere actualización periódica de GitHub/issues y comandos agrupados con instrucciones **exactas desde/hasta** para cada captura.

- **Último resultado observado:** `b2-frr-smoke-v2-con-logs.sh --snapshot-confirmado` a las 20:48:17 preparó archivos `/tmp/nl360-smoke-v2.*/daemons` con UID/GID 100:101 y modo `640`, `frr.conf` UID/GID 100:102 modo `660`, directorio modo 755. El script ejecutó luego `grep` como usuario Linux `rc-aa-ec`; **`Permiso denegado`** al intentar leer `daemons`. Resultado `RESULTADO_SMOKE_FRR_V2=2`, ejecución =2. **No llegó a `docker run -d`: NO es una prueba fallida del arranque de FRR en v2.** Estado posprueba: 0 contenedores, 0 namespaces, `ens33 192.168.47.40/24`, default `192.168.47.2`, Docker/SSH/open-vm-tools activos, Git limpio.
- **Evidencia local:** `~/netlab360-bootstrap/evidencias/11-b2-frr-smoke-v2-20261012-204817.log`. Consulta del mismo log a las 22:35:00, no nuevo ensayo. Usuario **tomó** captura `B2_06_Diagnostico_FRR_V2.png` desde `INICIO CAPTURA B2_06` a `FIN CAPTURA B2_06`. El PNG no consta subido al repositorio. Bitácora `docs/sesiones/2026-10-12-smoke-frr-v2-error-permisos.md`.
- **Corrección YA COMPROMETIDA EN GITHUB:** dentro de `scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh`, leer `daemons` con `sudo grep` después de `chown/chmod`, sin cambiar los permisos seguros. El script corregido **NO SE HA EJECUTADO TODAVÍA**. No repetir versión anterior. Issue [#42](https://github.com/recm0708/netlab360/issues/42) actualizada, abierta; #12 incidente observable abierta; snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` confirmado anteriormente por el usuario; #41 cerrado.
- **Próximos comandos para la VM:** 
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh
  grep -n 'sudo grep' scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh
  bash scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh --snapshot-confirmado
  echo "RESULTADO_FRR_V2_CORREGIDO=$?"
  sudo docker ps -a
  sudo ip netns list
  ip -4 -br addr show ens33
  ip -4 route show default
  ```
  Ejecutar solo una vez; si Docker/vtysh falla, registrar logs retenidos, no repetir ciegamente.
- **Captura siguiente:** generar vista SIN `clear` delimitada `========== INICIO CAPTURA B2_07 ==========` hasta `========== FIN CAPTURA B2_07 ==========`, con fecha, hostname, log 11-b2 más reciente, líneas del éxito/error y del postcheck. Nombrar `B2_07_Arranque_FRR_Verificado.png` **solo si el log confirma arranque y resultado 0**; en caso contrario `B2_07_Diagnostico_Arranque_FRR.png`. Fecha de consulta diferente a fecha original del ensayo, conservar ambas.
- **Estado de fondo:** Ubuntu Desktop 26.04.1 LTS en VMware, VM `netlab360-lab`, gestión fija .40, GitHub CLI autenticado como recm0708; Docker 29.9.0/Compose5.6, OpenTofu1.13.1, Ansible Core2.20, Node24; B1 IPAM/switch L2 probado, VLAN 110 3/3 ping, VLAN 120 aislada, restauración 3/3. FRR `quay.io/frrouting/frr:10.7.1` amd64 descargado, digest `sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`. OSPF routers, doble WAN, failover, dashboard y alarmas todavía pendientes. No cambiar `ens33`, NetworkManager ni rutas del host; no guardar tokens/OVA en GitHub.

---


## ÚLTIMO CHECKPOINT — 12/10/2026 19:59: B2_05 LISTA Y SMOKE FRR V2 REVISADO

**Leer este bloque primero al retomar**: S01 sigue abierta; #42 es la issue activa para iniciar zebra/ospfd. El snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` fue confirmado por usuario y #41 quedó cerrada. La red de administración fija `ens33 192.168.47.40/24`, gateway `.2`, no debe tocarse.

- Resultado previo: `diagnosticar-smoke-frr-b2.sh` terminó `RESULTADO_DIAGNOSTICO_ESTATICO=0` el 12/10 19:21:41. El registro local `~/netlab360-bootstrap/evidencias/10-b2-frr-diagnostico-estatico-20261012-192141.log` confirma propietarios `frr:frr` y nota de permisos FRR; contenedores y namespaces 0. **El smoke v1 falló con código 4; no repetirlo.**
- **Evidencia:** el usuario confirmó la captura `B2_05_Diagnostico_Estatico_FRR.png`, con delimitadores `INICIO CAPTURA B2_05` y `FIN CAPTURA B2_05`, fecha de consulta 19:59:38. **El PNG no está aún en GitHub ni ha sido recibido en esta intervención**, solamente su salida textual. Se evitó repetir la prueba; fecha original del diagnóstico 19:21:41.
- **Script v2 revisado y actualizado** en `scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh`: copia `daemons` desde imagen oficial FRR 10.7.1 amd64, activa `ospfd=yes`, crea `frr.conf` con propiedades UID/GID FRR, usa un contenedor temporal `--network none` con capacidades enumeradas necesarias (incluida `SETPCAP`), guarda `docker inspect`, procesos y logs *antes* de limpieza, compara IP/rutas de gestión. `SYS_ADMIN` sigue presente y es capacidad muy poderosa; mantener solo VM lab aislada, no usar `--privileged` ni `--network host`. **No se ha ejecutado v2.**
- **Próximos comandos:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh
  bash scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh --snapshot-confirmado
  echo "RESULTADO_FRR_V2=$?"
  sudo docker ps -a
  sudo ip netns list
  ip -4 -br address show ens33
  ip -4 route show default
  ```
- **Próxima evidencia si éxito:** imagen `B2_06_Arranque_FRR_V2_Exitoso.png` de una vista del log con marcadores INICIO/FIN y fecha original, `VTYSH_DISPONIBLE: SI`, resultado `show ip ospf`, `PRUEBA_SMOKE_FRR_V2: OK`, `RESULTADO_SMOKE_FRR_V2=0`. Si falla, capturar como `B2_06_Diagnostico_FRR_V2.png` solo con código de fallo, estado y logs; no presentar éxito imaginado.
- Actualizar #42 y esta ancla tras el ensayo v2. **Sin OSPF, WAN ni dashboard activos todavía**. No descargar otros componentes ni reiniciar VM por este diagnóstico.
- Normativa capturas: siempre comandos de vista delimitados INICIO/FIN, nombre PNG, desde-hasta exactos y condición de validez. Véase `docs/sesiones/2026-10-12-diagnostico-estatico-frr-y-protocolo-capturas.md`. No ejecutar `clear`; no subir tokens GH.

---


## REANUDACIÓN PRIORITARIA — 2026-10-12, 19:08 Panamá: FRR SMOKE V1 FALLÓ, LIMPIEZA CORRECTA

**ESTADO VIGENTE. Leer antes de registros antiguos.** NETLAB360 S01 abierta: Ubuntu/Docker/Git/SSH sanos, IPAM B1 OK, B2-L2 VLAN aislada funcionando y restaurada, FRRouting 10.7.1 descargado, **pero el primer intento de arrancar zebra y ospfd falló**. **NO ejecutar otra vez el mismo script hasta diagnosticar.** Sin adyacencias OSPF ni WAN creada.

- **Entorno:** VMware Workstation Pro, Ubuntu Desktop 26.04.1 LTS, `netlab360-lab`, usuario `rc-aa-ec`, 8 vCPU/16 GB RAM, disco 160GB, interfaz protegida `ens33 192.168.47.40/24` gateway `192.168.47.2`. Windows PowerShell `ssh netlab360` con llave Ed25519. Herramientas Docker 29.9.0/Compose 5.6.0, OpenTofu 1.13.1, Ansible Core 2.20.1, Node 24.21.0, GitHub CLI 2.102.0.
- **Snapshot:** `NETLAB360-BASE-HERRAMIENTAS` **CONFIRMADO EXPLÍCITAMENTE POR USUARIO** desde la primera indicación; issue [#41](https://github.com/recm0708/netlab360/issues/41) **cerrada**. No volver a preguntar por su existencia. No publicar snapshot/OVA con tokens.
- **Resultados previos válidos:** IPAM propuesto 3 sedes (S2 reservada), 9 VLAN, 2 WAN; no colisiones entre las 14 redes virtuales y 3 rutas/subredes activas; módulos Linux L2 presentes. B2-L2 bridge/VLAN 110: 3/3 ping, VLAN 120 aislamiento, restauración 3/3; cleanup, exit 0. Capturas B1_01, B1_02, B2_L2_01 entregadas.
- **Imagen FRR:** `quay.io/frrouting/frr:10.7.1` amd64 digest `sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`. Entrypoint tini -> docker-start -> watchfrr; daemons de fábrica `ospfd=no`. Precheck del entrypoint 18:47 exit 0. Capturas B2_03 (2 partes) correctas.
- **Prueba smoke fallida 19:07:27:** `bash scripts/laboratorio/b2-frr-smoke-aislado.sh --snapshot-confirmado` creó directorio temporal con `zebra=yes`, `ospfd=yes` y `frr.conf` mínimo, inició contenedor aislado Docker `--network none`, `--cap-drop ALL` y solo NET_ADMIN/NET_RAW. `vtysh -c 'show ip ospf'` no respondió en 10 intentos: `RESULTADO_SMOKE_FRR=4` (`RESULTADO_LANZAMIENTO_FRR=4`). **No se conocen aún causa precisa ni logs internos**: container `--rm` pudo salir antes y Docker no retuvo diagnóstico. Captura `B2_04_Arranque_Zebra_OSPFD.png` muestra FALLO; nombrar `B2_04_Diagnostico_Arranque_FRR.png`, no prueba de éxito.
- **Postcheck demostrado:** `sudo docker ps -a` vacío, `sudo ip netns list` vacío, `ens33=.40/24`, gateway `.2`, docker/ssh/open-vm-tools activos, Git `## main...origin/main` limpio al final (antes de nuevos commits remotos).
- **Evidencia:** `~/netlab360-bootstrap/evidencias/09-b2-frr-smoke-20261012-190727.log`; bitácora `docs/sesiones/2026-10-12-smoke-frr-primer-intento.md`; issue [#42](https://github.com/recm0708/netlab360/issues/42) con diagnóstico, [#12](https://github.com/recm0708/netlab360/issues/12) incidente observable pendiente, #1 S01 abierta.
- **Hipótesis no verificadas:** el script guardó `daemons` y `frr.conf` como propiedad del usuario normal del host en vez de UID100/GID101 frr, modo 0644; además `--cap-drop ALL` + NET_ADMIN/NET_RAW podría ser insuficiente. La documentación oficial FRR especifica permisos apropiados. NO declarar causa raíz sin pruebas.
- **Siguiente script versionado (SOLO LECTURA, sin iniciar FRR):** `scripts/diagnostico/diagnosticar-smoke-frr-b2.sh`. Inspecciona `frrcommon.sh`, `docker-start`, `/etc/frr/daemons`, propiedades y capacidades del proceso de inspección, en contenedor temporal sin red. Logs bajo `~/netlab360-bootstrap/evidencias/10-b2-frr-diagnostico-estatico-*.log`.
- **PRÓXIMAS ÓRDENES:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/diagnostico/diagnosticar-smoke-frr-b2.sh
  bash scripts/diagnostico/diagnosticar-smoke-frr-b2.sh
  echo "RESULTADO_DIAGNOSTICO_ESTATICO=$?"
  sudo docker ps -a
  sudo ip netns list
  ip -4 -br address show ens33
  git status --short --branch
  ```
- Tras salida, **editar prueba v2** con ficheros de propiedad y permisos FRR correctos, capacidades justificadas y persistencia de logs/estado de contenedor (no borrar antes de diagnosticar). Revisar script y volver a probar una sola vez. Mantener SSH y VMnet8 intactos, luego avanzar a OSPF dual WAN y observabilidad.
- **Regla usuario:** registrar hitos/errors en repo e issues, dar varios pasos por mensaje, no hacer pausas cada microtarea, sí checkpoint tras avance sustancial. Capturas deben mostrar fecha/hostname/comando/salida real. No subir tokens/códigos/credenciales.

---


## ANCLA ACTUAL — 12/10/2026 18:49 Panamá: FRR precheck OK y snapshot CONFIRMADO

**Leer esta sección primero en cualquier conversación nueva.** Usuario confirmó personalmente que creó al principio el snapshot `NETLAB360-BASE-HERRAMIENTAS`; issue #41 de preparación cerrada. **No pedir otra vez snapshot.** Los apagados `sudo systemctl poweroff` y los arranques por SSH también están comprobados. No hay routers FRR ni enlaces WAN ejecutados.

### Estado técnico verificado

- VMware Workstation Pro 26H1u1, VM Ubuntu Desktop 26.04.1 LTS, `netlab360-lab`, `rc-aa-ec`, 8 vCPU, 16 GB RAM, 160 GB disco. `ens33 192.168.47.40/24`, default `192.168.47.2`. `ssh netlab360` desde PowerShell con llave Ed25519. Docker 29.9.0, Compose 5.6.0, OpenTofu 1.13.1, Ansible Core 2.20.1, Node 24.21.0, Python 3.14.4 y GitHub CLI 2.102.0.
- B0 plataforma y mantenimiento validados; B1 IPAM 3 sedes/9 VLAN/2 WAN y preflight compatibilidad L2 OK. B2-L2 probó conectividad VLAN 110 (3/3), aislamiento VLAN 120, retorno VLAN 110 (3/3), limpieza automática, IP/rutas host intactas.
- Imagen `quay.io/frrouting/frr:10.7.1` amd64 descargada con digest `sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`.
- Precheck de FRR 18:47:25 **`RESULTADO_PRECHECK_ARRANQUE=0`**; metadatos `Entrypoint=["/sbin/tini","--"]` / `Cmd=["/usr/lib/frr/docker-start"]`, que ejecuta `watchfrr $(daemon_list)`. Daemons de fábrica `ospfd=no`, `bgpd=no`, `vtysh_enable=yes`; usuario `frr` UID 100, grupos frr/frrvty. Sin demonios iniciados en prueba de lectura. `/run/frr` existe.
- Git al terminar este diagnóstico: `## main...origin/main` limpio, hasta `1627726`, **antes de nuevos commits GitHub**. Un error `git status --short --branchcd` fue pegado accidentalmente y después se ejecutó un status correcto, sin cambios.
- Último log local original: `~/netlab360-bootstrap/evidencias/08-b2-frr-entrypoint-20261012-184725.log` (2.4KB). Bitácora versionada `docs/sesiones/2026-10-12-precheck-arranque-frr-b2.md`.
- Capturas aportadas de B1 y de inspección FRR ya revisadas en conversación; no constan como archivos rastreados por Git. No repetir capturas validadas. El siguiente paso debe indicar cuándo tomar evidencias de procesos FRR/vecinos/rutas y mantener fecha, hostname, comandos y resultado.

### Seguimiento GitHub y próximos pasos

- **#41 CERRADA:** paquete base, red fija, GitHub CLI, snapshot y recuperación comprobados.
- **#11 ABIERTA:** diseño IPAM, VLAN y arquitectura; completadas pruebas preliminares, todavía faltan componentes finales.
- **#12 ABIERTA:** incidente con cambio de ruta, sellos temporales, alarma y dashboard.
- **#42 ABIERTA (nueva):** subtarea FRR en dos routers, WAN dual OSPF y recuperación, con evidencia funcional.
- **#1 ABIERTA:** S01 transversal. No llamar fase terminada hasta criterios y entregables validados.
- Nueva prueba **PREPARADA, NO EJECUTADA:** `scripts/laboratorio/b2-frr-smoke-aislado.sh` para habilitar `zebra` y `ospfd` dentro de UN contenedor Docker temporal `--network none` con capacidades limitadas, inspeccionar `vtysh` y limpiarlo automáticamente. Esta prueba no crea todavía WAN, LAN ni adyacencias.
- **Comandos para retomar:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/laboratorio/b2-frr-smoke-aislado.sh
  sed -n '1,230p' scripts/laboratorio/b2-frr-smoke-aislado.sh
  bash scripts/laboratorio/b2-frr-smoke-aislado.sh --snapshot-confirmado
  echo "RESULTADO_LANZAMIENTO_FRR=$?"
  sudo docker ps -a
  sudo ip netns list
  ip -4 -br addr show ens33
  git status --short --branch
  ```
- Si prueba falla, NO repetir automáticamente ni desplegar R-HQ/R-S1: revisar `09-b2-frr-smoke-*.log` y códigos/log de Docker; ajustar script versionado, documentar el cambio y revalidar.
- Después de prueba satisfactoria, preparar `up/status/down` y configuración para dos routers con WAN primaria 10.78.0.0/30 (costo 10) y respaldo 10.78.0.4/30 (costo 100), OSPF área 0, loopbacks 10.79.0.1/32 y .2/32; medir fallo/restauración, conservar `ens33`.
- Guardar bitácoras/commits/issues tras subhitos significativos y antes de pausas. Al retomar no repetir instalación base. **Nunca almacenar tokens OAuth, contraseñas, OVA privada o material sensible en repositorio**.

---


## CONTINUAR DESDE AQUÍ — 2026-10-12 18:36 Panamá: imagen FRR inspeccionada

**Estado vigente:** S01 abierta. B0 y B1 validados, primer ensayo B2-L2 de Linux Bridge/VLAN 110/120 superado con restauración y limpieza. Imagen `quay.io/frrouting/frr:10.7.1` descargada e inspeccionada; **R-HQ/R-S1, OSPF y WAN dual todavía NO ejecutados**.

- `scripts/diagnostico/inspeccionar-imagen-frr-b2.sh` tuvo `RESULTADO_INSPECCION_FRR=0` el 2026-10-12 18:36:14. Usuario `frr` UID100/GID101 y grupo `frrvty` GID102; `id frrvty` imprime mensaje informativo porque no es cuenta. Imagen incluye `/etc/frr/daemons` (ospfd=no, vtysh_enable=yes), binarios vtysh/zebra/ospfd; **no** trae `/etc/frr/frr.conf` de fábrica. Un contenedor temporal de inspección quedó eliminado y Docker continuó sin contenedores.
- Gestión sin cambios: `ens33 192.168.47.40/24`, ruta predeterminada por `.2`, servicios docker/ssh/open-vm-tools activos y Git limpio antes de los últimos commits documentales. Log `~/netlab360-bootstrap/evidencias/07-b2-inspeccion-imagen-frr-20261012-183614.log`.
- **Imágenes adjuntas revisadas:** `B1_01_Validacion_IPAM_y_Redes.png` y `B1_02_Compatibilidad_Capa2.png` aprobadas. `B2_01_Imagen_FRR_Descargada.png` refleja INSPECCIÓN de archivos internos FRR y debe renombrarse `B2_02_Inspeccion_Imagen_FRR.png`. No están subidas aún al repositorio Git; su existencia se verificó como adjuntos en la conversación. Bitácora de revisión `docs/sesiones/2026-10-12-inspeccion-interna-frr-y-capturas.md`.
- **Nueva preparación en GitHub:** `scripts/diagnostico/precheck-arranque-frr-b2.sh` (solo lectura, contenedor temporal sin red; inspecciona Entrypoint, daemons y directorios), `topologias/b2-frr/configs/R-HQ.frr.conf` y `R-S1.frr.conf` (configuraciones CANDIDATAS, NO aplicadas), `topologias/b2-frr/README.md` y documentación de B2-L3. Ver issue #12, todavía ABIERTA.
- **Próxima secuencia:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/diagnostico/precheck-arranque-frr-b2.sh
  bash scripts/diagnostico/precheck-arranque-frr-b2.sh
  echo "RESULTADO_PRECHECK_ARRANQUE=$?"
  ls -lh ~/netlab360-bootstrap/evidencias/08-b2-frr-entrypoint-*.log
  sed -n '1,90p' topologias/b2-frr/configs/R-HQ.frr.conf
  sed -n '1,90p' topologias/b2-frr/configs/R-S1.frr.conf
  sudo docker ps -a
  git status --short --branch
  ```
- **Antes de desplegar OSPF:** confirmar desde VMware Snapshot Manager que la instantánea `NETLAB360-BASE-HERRAMIENTAS` existe. El parámetro anterior `--snapshot-confirmado` NO constituye verificación independiente. Diseñar y probar `up/status/down` con limpieza solo de recursos propios y red aislada de VMnet8.
- **Capturas futuras:** incluir fecha/hostname, comando efectivo, salida de éxito/error y comprobación posterior; usar log para salidas largas. Captura de primera prueba L2-B2 no confirmada, pero existe el log local `05-b2-l2-20261012-181601.log`.
- **Continuidad:** registrar resultados y evidencias en #12 y aquí cada avance sustancial, sin esperar límite de contexto; usuario prefiere varios comandos por turno y pausas después de hitos significativos. No publicar tokens ni contenido de `~/.config/gh/hosts.yml`.

---


## ÚLTIMO ESTADO — 2026-10-12 18:22 Panamá: FRR 10.7.1 DESCARGADO, OSPF AÚN PENDIENTE

**Priorizar este punto sobre los registros históricos siguientes.** El laboratorio B2-L2 pasó todas las pruebas de conectividad VLAN/aislamiento/restauración, sin residuos. El siguiente paso es **inspección interna de la imagen FRRouting**, antes de crear routers.

- `precheck-frr-b2.sh`: `RESULTADO_PREFLIGHT_FRR=0`, IPAM B1 OK, host `ens33=192.168.47.40/24`, gateway `.2`, Docker Engine 29.9.0, servicios activos, 0 contenedores, Git limpio tras `git pull` hasta commit `c53ed0f` (antes de nuevos commits remotos).
- Imagen **descargada** `quay.io/frrouting/frr:10.7.1`, arquitectura `amd64`, digest `sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`. Manifiesto de plataforma `linux/amd64` también disponible. **No hay contenedores FRR ejecutándose, no hay vecinos OSPF ni failover WAN demostrado.**
- Evidencia del preflight: `~/netlab360-bootstrap/evidencias/06-b2-frr-precheck-20261012-182150.log` (2.1KiB). Bitácora GitHub `docs/sesiones/2026-10-12-precheck-frr-imagen-b2.md`.
- Próximo script **versionado pero sin ejecutar**: `scripts/diagnostico/inspeccionar-imagen-frr-b2.sh`. Ejecuta un contenedor temporal sin red, con `--cap-drop ALL`, `--read-only` y `--rm` para verificar el usuario frr, archivos /etc/frr y ejecutables vtysh/zebra/ospfd; no instala ni crea redes.
- **Comandos para continuar:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/diagnostico/inspeccionar-imagen-frr-b2.sh
  bash scripts/diagnostico/inspeccionar-imagen-frr-b2.sh
  echo "RESULTADO_INSPECCION_FRR=$?"
  sudo docker ps -a
  ip -4 -br addr show ens33
  git status --short --branch
  ```
- **Snapshot pendiente de confirmación independiente:** se comprobó apagado y reencendido de Ubuntu antes de B2-L2; se usó flag `--snapshot-confirmado`, pero la existencia/nombre `NETLAB360-BASE-HERRAMIENTAS` no fue observada directamente en VMware Snapshot Manager en esta conversación. Confirmar antes de levantar la topología OSPF.
- Después de ver la salida: redactar `daemons` y `frr.conf` coherentes con usuarios/permisos reales de la imagen, montar 2 routers aislados con WAN-P `10.78.0.0/30` cost 10 y WAN-B `10.78.0.4/30` cost 100, anunciar prefijos de LAN, probar fallo/restauración y rollback sin ens33. Actualizar issue #12 y esta ancla con evidencia real.
- Dos capturas B1 confirmadas; **ninguna captura B2 confirmada**. Las imágenes y logs completos siguen locales, no se declaró su subida.
- Política de trabajo: entregar varios pasos/comandos por turno, actualizar GitHub cada bloque relevante y antes de pausas; no cerrar S01, #12 ni inventar adyacencias/alarma/dashboard.

---

## ESTADO VIGENTE — 2026-10-12, 18:16 Panamá: B2-L2 DEMOSTRADO

**Priorizar este bloque cuando se retome el proyecto o se abra otra conversación.** El hito B1 concluyó satisfactoriamente, la **primera prueba VLAN B2-L2 está ejecutada y validada**, y está preparado el **preflight B2-L3/OSPF**. **La fase S01 sigue abierta** porque aún faltan WAN/OSPF, telemetría, API/dashboard, analítica y entregables.

### Último trabajo confirmado

- **VM:** Ubuntu 26.04.1 LTS en VMware Workstation 26H1u1, hostname `netlab360-lab`, usuario `rc-aa-ec`, 8 vCPU/16 GB RAM/160 GB disco, SSH desde PowerShell `ssh netlab360` con llave Ed25519. Gestión `ens33=192.168.47.40/24`, gateway `.2`, VMnet8 aislada de laboratorio.
- **B0/B1:** APT actualizado, Docker/SSH/VMware Tools activos; IPAM B1 validado (3 sedes, 9 VLAN y 2 WAN propuestas, S2 reservada), sin colisiones con rutas/redes activas del host; kernel soporta módulos 8021q/bonding/openvswitch/veth/bridge.
- **Ejecución B2-L2 2026-10-12 18:16:01:** `bash scripts/laboratorio/b2-l2-aislado.sh --snapshot-confirmado`. Prueba positiva VLAN 110 (3/3, 0.068ms RTT medio); cambio del puerto sw-b a VLAN 120 impide respuesta ICMP; restauración a VLAN 110 (3/3, 0.044ms RTT medio). `PRUEBA B2-L2: OK`, `CODIGO_FINAL: 0`, `RESULTADO_B2=0`. Namespaces eliminados, rutas/IP de ens33 intactas y ningún contenedor Docker. Local Git `## main...origin/main` limpio inmediatamente después de la prueba, **antes de nuevos commits remotos**.
- **Reinicio intermedio:** se ejecutó `sync; sudo systemctl poweroff`, SSH se desconectó normalmente. Un SSH inmediato agotó el tiempo durante VM apagada; siguiente SSH exitoso tras encenderla. **La existencia de snapshot `NETLAB360-BASE-HERRAMIENTAS` no se observó directamente en VMware**. El argumento `--snapshot-confirmado` declara confirmación del operador, no un chequeo programático; pedir al usuario confirmación de Snapshot Manager antes de enrutamiento.
- **Evidencias B1:** el usuario dijo haber tomado dos capturas PNG (no subidas a GitHub). No ha indicado todavía captura B2. Log B2 local `~/netlab360-bootstrap/evidencias/05-b2-l2-20261012-181601.log` (~1.6KiB); bitácora GitHub `docs/sesiones/2026-10-12-prueba-vlan-l2-b2.md` (no contiene secretos).
- **GitHub:** issue #12 actualizada, permanece abierta; #11 y #41 también abiertas. Diseño preliminar para siguiente paso: `docs/arquitectura/03-frr-ospf-dual-wan-b2-plan.md`, diagnóstico `scripts/diagnostico/precheck-frr-b2.sh`. Imagen candidata oficial `quay.io/frrouting/frr:10.7.1` **NO descargada ni verificada**.
- **Próximas instrucciones para Ubuntu, SOLO LECTURA:**
  ```bash
  cd ~/proyectos/netlab360
  GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
  bash -n scripts/diagnostico/precheck-frr-b2.sh
  bash scripts/diagnostico/precheck-frr-b2.sh
  echo "RESULTADO_PREFLIGHT_FRR=$?"
  ls -lh ~/netlab360-bootstrap/evidencias/06-b2-frr-precheck-*.log
  ```
  El diagnóstico lee host/Docker/IPAM y consulta el manifiesto de imagen oficial. **No descarga, instala ni ejecuta FRR ni toca interfaces**.
- **Después del preflight:** revisar compatibilidad del tag/arquitectura, confirmar snapshot, decidir descarga versionada de imagen FRR y generar ensayo WAN dual OSPF aislado con corte/restauración y rollback. No afirmar rutas ni adyacencias antes de pruebas. Diferenciar doble WAN OSPF, LACP, redundancia de equipo y trunks 802.1Q.
- **Regla de trazabilidad:** actualizar este encabezado, issues y bitácoras al completar un hito sustancial o antes de la próxima pausa; usuario prefiere varios comandos agrupados. No almacenar token OAuth (ubicado en `~/.config/gh/hosts.yml`) en repositorio/OVA; permisos 600 y directorio GH 700.

---

## HITO DE REANUDACIÓN — B1 validado; primer ensayo L2 B2 PREPARADO, no ejecutado

**Fecha:** 2026-10-12, después de 18:03 Panamá. **Estado actual:** B1 IPAM y capacidades del kernel verificados; no hay infraestructura empresarial desplegada, no hay VLAN real, OSPF, LACP, FRR ni OVS instalados.

- El usuario aportó `RESULTADO_L2=0` del script `precheck-l2-b1.sh`: módulos `8021q`, `bonding`, `openvswitch`, `veth` y `bridge` disponibles (solo bridge cargado). `ip_forward=1`, `ens33 192.168.47.40/24`, gateway `.2`, `docker0 172.17.0.0/16`, cero namespaces y contenedores. Servicios activos, 8 vCPU y aproximadamente 13 GiB disponibles. `VALIDACIÓN B1: OK` reiterada y Git limpio al final de la comprobación anterior a nuevos commits.
- El usuario **ya tomó dos capturas**: `B1_01_Validacion_IPAM_y_Redes.png` y `B1_02_Compatibilidad_Capa2.png`. **No están incorporadas al repositorio**, no pedir repetirlas. Logs locales `03-b1-preflight-20261012-173813.log` y `04-b1-compatibilidad-l2-20261012-180335.log`, en `~/netlab360-bootstrap/evidencias/`.
- Bitácoras GitHub: `docs/sesiones/2026-10-12-validacion-ipam-b1.md` y `docs/sesiones/2026-10-12-compatibilidad-l2-b1.md`; issue #11 comentada/actualizada.
- Nueva decisión propuesta `docs/decisiones/ADR-003-redes-virtuales-aisladas.md`: utilizar inicialmente Linux network namespaces, veth y Linux bridge para ensayo L2; FRRouting/OSPF después, con OVS/Faucet y LACP tratados separadamente. **Propuesta, no validación operativa**.
- Nuevo script preparatorio `scripts/laboratorio/b2-l2-aislado.sh`: test aislado con dos endpoints VLAN 110, separación de puerto VLAN 120 y restauración, con limpieza al terminar; **NO se ha ejecutado**. Requiere argumento `--snapshot-confirmado` y comprobaciones previas; no se modifica ens33. Versionado para revisión, no sustituye inspección y `bash -n`.
- **BLOQUEO ANTES DE EJECUTAR PRUEBA:** confirmar la instantánea VMware `NETLAB360-BASE-HERRAMIENTAS`. Ninguna salida de usuario ha confirmado todavía su creación. Si existe, verificar desde VMware; si no, apagar VM ordenadamente, crear snapshot con VM apagada, encender de nuevo y verificar `ssh netlab360`.
- **PRÓXIMA SECUENCIA:** `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`; `bash -n scripts/laboratorio/b2-l2-aislado.sh`; verificar snapshot; si está confirmado, ejecutar `bash scripts/laboratorio/b2-l2-aislado.sh --snapshot-confirmado` y revisar su salida y `sudo ip netns list`, ruta/IP, Docker y log `05-b2-l2-*.log`. Si falla, detenerse y revisar salida, sin repetir ni agregar otras redes.
- Al obtener pruebas funcionales, actualizar issue #12, bitácora, evidencias y esta ancla; no cerrar S01 ni declarar failover OSPF hasta demostración.

---

## ANCLA DE REANUDACIÓN — Estado vigente 2026-10-12, 18:03 Panamá

**Lee esta sección antes que los registros históricos situados más abajo.** NETLAB360 sigue en S01, B1: IPAM y **compatibilidad L2/L3 del kernel ya verificados**. La matriz de conexiones es propuesta, todavía no implementada. **No hay red empresarial desplegada ni Fase 1 cerrada**.

1. **VM:** Ubuntu Desktop 26.04.1 LTS, host `netlab360-lab`, usuario `rc-aa-ec`, VMware Workstation Pro 26H1u1, 8 vCPU, 16 GB RAM, disco virtual 160 GB. Gestión exclusiva por `ens33=192.168.47.40/24` y NAT `192.168.47.2`; Windows PowerShell `ssh netlab360` con llave ED25519.
2. **Post-reinicio validado:** `docker`, `ssh`, `open-vm-tools` activos, 0 unidades fallidas; GitHub CLI autenticado como `recm0708`, `git pull` exitoso y rama limpia en revisión de las 16:58; APT actualizado, `dpkg --audit` sin salida.
3. **Toolchain:** Docker Engine 29.9.0, Compose 5.6.0, Buildx 0.38.0, containerd 2.4.1, OpenTofu 1.13.1, Ansible Core 2.20.1, Python 3.14.4, Node.js 24.21.0, npm 11.19.0, gh 2.102.0; Docker hello-world OK; 136 GB disponibles según inventario anterior.
4. **Checkpoint:** base B0 sana técnicamente. **Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` aún no confirmado**, pendiente issue #41. No reiniciar instalador.
5. **B1 IPAM YA VERIFICADO (2026-10-12, 17:38):** Git pull exitoso; validador IPAM **OK** (3 sedes, 9 VLAN, 2 WAN y 15 redes incluida VMnet8), preflight de host/Docker **RESULTADO_B1=0** (14 redes virtuales sin choque con 3 rutas/redes activas), PyYAML 6.0.3, 8 vCPU/13Gi disponibles/136GB libres, servicios activos, sin contenedores. Evidencia local: `~/netlab360-bootstrap/evidencias/03-b1-preflight-20261012-173813.log`. Bitácora: [validación B1](sesiones/2026-10-12-validacion-ipam-b1.md). Diseño **aún no desplegado**. Ver issue #11.
6. **PRECHECK L2/L3 YA VERIFICADO 18:03:35**: `bash -n` correcto, `bash scripts/diagnostico/precheck-l2-b1.sh` **RESULTADO_L2=0**, evidencia `~/netlab360-bootstrap/evidencias/04-b1-compatibilidad-l2-20261012-180335.log`. Módulos disponibles `8021q`, `bonding`, `openvswitch`, `veth`, `bridge` (solo `bridge` cargado). `ip/tc/bridge/docker` presentes; `ovs-vsctl`, `vtysh`, `containerlab` no instalados. Rutas y ens33 sin cambios, Docker sin contenedores, IPAM validado OK. Bitácora [L2](sesiones/2026-10-12-compatibilidad-l2-b1.md). **SIGUIENTE:** elegir aislamiento de switches/FRR, verificar snapshot VMware y luego planificar pruebas B2; no instalar o crear recursos aún.
7. **Trazabilidad:** issue #11 actualizada con IPAM y L2 exitosos. El usuario **ya capturó dos evidencias** `B1_01_Validacion_IPAM_y_Redes.png` y `B1_02_Compatibilidad_Capa2.png` (archivos de imagen no localizados/subidos al repo todavía). Logs originales solo locales. Bitácoras: [IPAM](sesiones/2026-10-12-validacion-ipam-b1.md) y [L2](sesiones/2026-10-12-compatibilidad-l2-b1.md). Política de pausas en `docs/05-plan-operativo-y-pausas.md`.
8. **Seguridad y bloqueo B2:** GH CLI guarda credenciales en `~/.config/gh/hosts.yml` con permisos 600; no compartir token ni empaquetarlo en OVA. No usar `ens33` como switch emulado. **Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` sin confirmación; no crear bridges, redes virtuales ni topología B2 hasta tenerlo**. El paquete v0.2 de planificación NO se ha importado.

---


Fecha inicial: 2026-10-09 (Panamá, UTC−05:00).

## Repositorio
- Canonical: https://github.com/recm0708/netlab360
- Visibilidad: PRIVATE.
- Rama principal: `main`.
- Repositorio inicializado con README y workflow `.github/workflows/bootstrap-github.yml`.

## Trabajo registrado
- Ocho issues de fase: #1–#8, con checklist transversal y criterios de cierre.
- Veintinueve issues técnicas: #9–#37, correspondientes a los identificadores [001]–[029] de la plantilla.
- Todas las issues abiertas, asignadas a `recm0708`.
- Workflow de gestión para etiquetas `semana:01` a `semana:08`, tipos/prioridades y milestones `S01` a `S08`; verificar resultado del workflow antes de dar por habilitada la clasificación.

## Pendientes inmediatos
- [ ] Importar íntegramente la plantilla local `NETLAB360_Planificacion_v0.2.zip` a la raíz de este repositorio (sin anidar carpeta contenedora).
- [ ] Verificar etiquetas y milestones generados por GitHub Actions.
- [ ] Comparar cuerpos de las issues con los archivos de `backlog/`; sincronizar únicamente si no afecta checkboxes ya trabajados.
- [ ] Verificar que el pipeline CI inicial sea exitoso y no involucre operaciones de red privilegiadas.
- [ ] Confirmar versiones compatibles para Ubuntu Desktop y VMware (no instalar por ser «la última» sin verificación). Se revisaron referencias oficiales para 26H1u1; falta inspección local del equipo.
- [ ] Preparar laboratorio mínimo de F1 con segmentación, ruta de respaldo y evento realmente observable.
- [ ] Abrir tres entregables editables y comenzar evidencias desde F1.
- [ ] Registrar requisitos nuevos de la docente como cambios controlados.

## Reglas de continuidad
1. Antes de continuar, leer este registro, `README.md`, `docs/05-plan-operativo-y-pausas.md` y las issues abiertas del hito correspondiente.
2. El estado observado y los resultados de los comandos prevalecen sobre supuestos de configuración.
3. No cerrar issues por completar solamente comandos; deben existir evidencia, comprobación operacional, documentación y recuperación.
4. Los archivos de máquina virtual, credenciales y state sensible no se almacenan en Git.
5. Un issue o un comentario puede contener una decisión, pero una decisión arquitectónica duradera debe registrarse también en `docs/decisiones/`.

## Condición de entrega
Cada fase es un candidato demostrable independiente; el cumplimiento definitivo queda condicionado a los requisitos/rúbrica que publique la docente. No se declarará un SLO, failover, IA, streaming ni LAG «validado» sin prueba reproducible.

## Estado de preparación del entorno (2026-10-09)
- El usuario aprobó **crear VM nueva VMware Workstation sin ISO**; queda documentado en `docs/decisiones/ADR-001-vmware-vm-sin-iso.md`.
- Se iniciaron las tareas #10, #34, #1 y #29 mediante comentarios de seguimiento. Ningún criterio de creación o instalación de VM se declara completado.
- VMware Workstation Pro **26H1u1 (26.0.1 build 25688693)** ya está verificado, con i9-12900H (14 núcleos, 20 hilos), 63.70 GB RAM y espacio libre suficiente en C:.
- Tras ajuste del usuario, VMware muestra **8 vCPU**, 16 GB RAM, disco SCSI 160 GB y NIC NAT.
- **Ubuntu Desktop 26.04.1 LTS instalado**; usuario `rc-aa-ec`, hostname `netlab360-lab`, `nproc=8`, RAM 15 GiB, `/dev/sda2` 157 GB, kernel `7.0.0-38-generic`, SSH y VMware Tools activos.
- Se abrió la issue **#38** para Ubuntu Desktop + SSH. Guía versionada: `docs/infraestructura/02-ubuntu-desktop-instalacion-ssh.md`.
- **VMnet8/IP administrativa definitiva propuesta y aplicada:** `192.168.47.40/24`, fuera del pool DHCP `192.168.47.128–254` y reservas declaradas. Gateway `192.168.47.2`; DNS `.2` y `1.1.1.1`; perfil `netlab360-gestion`. Gateway e Internet 4/4 pings, DNS funcional. ADR-002 actualizado.
- **SSH Windows comprobado con clave:** credencial Ed25519 de cliente generada en `C:\\Users\\ruben\\.ssh\\netlab360_ed25519`, clave pública autorizada, login sin contraseña de Ubuntu validado, alias `ssh netlab360` probado. La llave requiere passphrase local. Entrada antigua `.130` no se eliminó.
- **Reinicio completo comprobado:** IP manual `192.168.47.40/24`, perfil `netlab360-gestion`, gateway `192.168.47.2`, servicio SSH y VMware Tools activos; DNS `github.com` operativo.
- **GitHub CLI:** `gh` versión 2.46.0 instalada desde Ubuntu; intento `gh auth login -h github.com -p https -w` falló al intentar abrir navegador Snap en sesión SSH sin variable `DISPLAY`. La autorización de GitHub no ha concluido.
- Se ha recomendado **rotar la contraseña compartida en chat** y no documentarla ni reutilizarla en otros servicios. No almacenar secretos.
- Issue #38 y guía `docs/infraestructura/02-ubuntu-desktop-instalacion-ssh.md` actualizadas.

## Pausa operativa solicitada — 2026-10-09
- **Objetivo actual:** instalar dependencias base y detenerse sin desplegar redes ni servicios del proyecto. Solo se realizará preparación de plataforma.
- **GitHub CLI autenticado:** `gh auth status` confirmó la cuenta `recm0708` en github.com, repo privado `recm0708/netlab360` visible, `gh auth setup-git` aplicado.
- **Git clonado:** `~/proyectos/netlab360`; `git status --short --branch` mostró `## main...origin/main`, sin cambios locales antes de esta actualización remota.
- **Issue #40:** autenticación y clonación completadas, cerrada. **Issue #41:** instalación de herramientas y pausa operativa, abierta.
- **Instalador pendiente de ejecución en VM:** `scripts/bootstrap/preparar-entorno-ubuntu.sh` (APT base, GitHub CLI oficial, Docker/Compose/Buildx, Ansible, OpenTofu, Node.js 24 LTS, herramientas de red). No declarar instalado ningún componente hasta recibir salidas.
- **Guía de ejecución/pausa:** `docs/infraestructura/04-preparacion-herramientas-pausa.md`.
- **Herramientas diferidas al inicio de implementación:** FRRouting/OVS/Faucet, Containerlab, Prometheus y servicios web/IA; se versionarán y probarán dentro de entornos aislados.
- **Template v0.2 pendiente:** se conserva y se importará solo con revisión para no sobrescribir documentos posteriores, sin duplicar issues.
- **Seguridad:** token GitHub y llave cliente SSH permanecen en el invitado/Windows; **sanitizar antes de exportar VM a docente**. Rotar la contraseña que fue compartida en conversación.

## Pausa operativa: resultado final registrado (2026-10-09, 15:06–15:10 EST)

**La preparación no terminó. NO declarar Docker, OpenTofu, Ansible ni Node.js instalados por este script.**

- `git pull --ff-only origin main` completó fast-forward a commit `7644cf5`, se revisó script y `bash -n` no mostró errores.
- Al ejecutar `scripts/bootstrap/preparar-entorno-ubuntu.sh`, creó el archivo `~/netlab360-bootstrap/evidencias/02-preparacion-herramientas-20261009-150619.log` y **abortó en `sudo -v`** tras tres intentos de autenticación incorrecta. Por `set -e`, ningún paquete del script llegó a instalarse.
- Verificación posterior: `sudo docker` → `command not found`; servicio docker inactivo. `ssh` y `open-vm-tools` activos, IPv4 `192.168.47.40/24`, raíz 157G/137G disponibles, sin reinicio requerido. Git limpio (`## main...origin/main`).
- Se ejecutaron `sync` y `sudo systemctl poweroff`. El enlace SSH se cerró con `Connection reset`; es compatible con apagado, pero la confirmación visual de VMware sigue pendiente.
- Issue #41 **permanece abierta**. No se activaron simulaciones, redes, containers ni aplicaciones del proyecto.
- La contraseña de sudo en Ubuntu corresponde al usuario **rc-aa-ec**, no a la frase de contraseña de la llave SSH privada de Windows. No enviar ni almacenar ningún secreto. Verificar distribución teclado y Caps Lock desde consola VMware si falla.

## Próxima acción cuando el usuario solicite reanudar

1. Confirmar desde VMware que la VM está apagada; si es así, no es necesario hacer nada hasta el siguiente día de trabajo.
2. Al regresar, encender VM en VMware y desde PowerShell abrir `ssh netlab360`.
3. En Ubuntu, ejecutar **primero** `sudo -k && sudo -v` introduciendo la contraseña actual del usuario Ubuntu (no la passphrase SSH) y verificar que retorna sin error. Si falla, detenerse y revisar desde consola VMware. No insistir con el instalador.
4. Desde Ubuntu, `cd ~/proyectos/netlab360 && git pull --ff-only origin main`. El remoto habrá avanzado debido a esta actualización documental.
5. Ejecutar `bash -n scripts/bootstrap/preparar-entorno-ubuntu.sh`; luego `bash scripts/bootstrap/preparar-entorno-ubuntu.sh`. Corregir errores de compatibilidad repositorio/paquete en el paso específico; no instalar servicios de topología.
6. Validar versiones, `sudo docker run --rm hello-world`, Docker/SSH/open-vm-tools activos, IP, Git limpio y evidencias. Actualizar #41.
7. Solo después de comprobar que la preparación terminó, crear instantánea de recuperación y apagar ordenadamente.


## Reanudación 2026-10-12 — sudo restaurado, Git HTTPS solicita credenciales

- `whoami` identifica `rc-aa-ec`; `sudo -k` y `sudo -v` funcionaron. Problema de autenticación local Ubuntu **resuelto**.
- Antes de iniciar el instalador, `git pull --ff-only origin main` detuvo el flujo solicitando usuario y contraseña de GitHub. **No hay constancia de pull completado ni de instalación de dependencias en esta sesión**.
- No introducir contraseña de GitHub por HTTPS. Verificar `gh auth status -h github.com` y `gh api user --jq .login`; luego `gh auth setup-git --hostname github.com` para configurar el helper oficial. Reintentar con `GIT_TERMINAL_PROMPT=0 git ls-remote --heads origin main`, después `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`. Si falla, inspeccionar el helper sin exponer tokens.
- Si `gh auth status` indica que OAuth ha caducado, autorizar desde navegador Windows mediante `GH_BROWSER=/bin/true gh auth login -h github.com -p https -w` con código temporal (no compartir código).
- Tras Git: hacer mantenimiento preventivo `sudo apt update`, consultar actualizaciones con `apt list --upgradable`, ejecutar `sudo apt upgrade -y`; reiniciar si `/var/run/reboot-required` aparece y verificar SSH/IP/servicios. No forzar phased updates.
- Ejecutar instalador `scripts/bootstrap/preparar-entorno-ubuntu.sh` solo tras volver a verificar `sudo`, Git y versión del script.
- Issue #41 continúa abierta hasta versiones y pruebas confirmadas. No declarar Docker/OpenTofu/Ansible/Node instalados.

## Estado vigente — 2026-10-12, instalación base completada

El segundo intento de preparación **sí completó** todas las etapas del script. Tras cancelar el prompt de Git, Bash ejecutó las siguientes órdenes ya suministradas. Actualizó 19 paquetes, instaló herramientas base y verificó Docker `hello-world`, OpenTofu, Ansible, GitHub CLI y Node.js. Ver registro `docs/sesiones/2026-10-12-preparacion-base-validada.md`.

- Docker Engine 29.9.0; Compose 5.6.0; Buildx 0.38.0; containerd 2.4.1.
- OpenTofu 1.13.1, Ansible Core 2.20.1, Python 3.14.4.
- Node 24.21.0, npm 11.19.0, gh 2.102.0.
- Servicios `docker`, `ssh`, `open-vm-tools` activos; IP fija .40; 136 GB libres; sin reboot requerido.
- GH CLI informó que la sesión local no está autenticada y la llamada `gh api user` devolvió HTTP 401. El `git pull` inicial **no se completó**.
- No ejecutar de nuevo script bootstrap. Reautorizar GH CLI desde navegador Windows, ejecutar `gh auth setup-git --hostname github.com`, verificar con `GIT_TERMINAL_PROMPT=0 git ls-remote --heads origin main`, luego `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`.
- Tras confirmar Git, registrar snapshot y apagar; las fases de red aún no se iniciaron.

## Bloques y checkpoints incorporados — 2026-10-12

- Se acordó avanzar por **bloques funcionales sustanciales** (B0 base, B1 IPAM, B2 red y failover, B3 telemetría y dashboard, B4 diagnóstico, B5 documentación), no por pausas a cada subpaso.
- Conservar evidencia, prueba y commits antes de pausas largas. Ofrecer pausa tras completar uno o varios bloques útiles o aproximadamente 2–4h de trabajo concentrado; **no ejecutar apagados sin decisión del usuario**.
- La fase S01 planificada para 5–11 de octubre está abierta el 12; no reprogramar fechas ni declarar cumplida sin pruebas. La meta inicial ahora es consolidar B0 y empezar B1 en esta sesión.
- **Plan maestro operativo:** `docs/05-plan-operativo-y-pausas.md` (creado). README enlaza la guía.
- **Confirmado en esta conversación:** GH CLI autenticado como `recm0708`; `gh auth setup-git --hostname github.com`, `git ls-remote --exit-code origin refs/heads/main` y `git pull --ff-only origin main` exitosos. Rama local `main...origin/main` limpia al concluir, antes de nuestros commits posteriores de planificación.
- **Siguiente comando en Ubuntu:** `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main` para incorporar estos nuevos documentos; después salud de red, dpkg, APT, Docker, disco, SSH y token protegido. NO volver a ejecutar script instalador ya terminado.
- **Pendiente:** instantánea base `NETLAB360-BASE-HERRAMIENTAS`, inicio arquitectura IPAM #11; OAuth de GH en `~/.config/gh/hosts.yml` sin cifrar: asegurar permisos y sanitizar antes de exportar VM.

## Precheck final B0 y reinicio de Windows solicitado — 2026-10-12, 11:20 Panamá

- Git: `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main` exitoso; `git status --short --branch` mostró `## main...origin/main`, sin cambios locales en ese momento. Se hicieron commits remotos posteriores a la revisión: al retomar debe ejecutarse otro pull.
- Credenciales GH CLI: carpeta `~/.config/gh` permisos `700`, archivo `hosts.yml` permisos `600`; siguen sin cifrar; no difundir ni incluir en una OVA.
- APT: `sudo apt update` informó todos los paquetes al día; `sudo apt upgrade -y` registró **0 actualizados, 0 instalados, 0 eliminados, 0 pendientes**. `sudo dpkg --audit` vacío, `systemctl --failed` **0 unidades**. Aviso Ubuntu Pro ESM Apps informativo sin impedir el mantenimiento.
- Los servicios `docker`, `ssh`, `open-vm-tools` mostraron `active`; sin contenedores Docker. Docker Compose **v5.6.0**.
- `ens33` `192.168.47.40/24`, puerta de enlace `192.168.47.2`; raíz 157G con **136G libres**; **NO SE REQUIERE REINICIO** del invitado por actualizaciones.
- El usuario **decidió reiniciar Windows anfitrión**, no terminar todavía S01. Se aconseja apagar **antes** la VM desde SSH con `git status --short --branch; sync; sudo systemctl poweroff`, verificar visualmente que aparece apagada en VMware, tomar snapshot `NETLAB360-BASE-HERRAMIENTAS` con VM apagada y después reiniciar Windows. **Ejecución/confirmación del apagado y snapshot aún no recibidas**.
- No hay más dependencias base por instalar ahora. FRR/OVS/Faucet/Containerlab/Prometheus/backend frontend/IA quedarán para fases del diseño.
- Tras reiniciar Windows: abrir VMware, arrancar `NETLAB360-Ubuntu-Desktop` solamente si se continúa; en PowerShell `ssh netlab360`; en Ubuntu comprobar red, servicios, `gh auth status -h github.com`, `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`, `sudo apt update` y `sudo dpkg --audit`. No repetir instalador.
- Issue #41 permanece abierta únicamente por snapshot/apagado y confirmación de restauración cuando corresponda. Próximo bloque sustantivo de S01: B1 diseño e IPAM, issue #11, antes de desplegar topologías.
