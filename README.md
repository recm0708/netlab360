# NETLAB360 — Planificación semestral

> **Checkpoint 13/10 22:48:** progreso estimado **71/100**, IaC configuró realmente FRRouting mediante candidatos Ansible: OSPF WAN dual Full, failover y restore con rc0, cleanup y gestión intacta; drift reconciliado en copia de archivos, NO en routers vivos. Nueva prueba B4 de inventario de datos reales y CI offline versionadas pero pendientes de ejecución. Fotografías IaC de esta tanda pendientes de recepción; **62 PNG históricos ya publicados**. [Bitácora](docs/sesiones/2026-10-13-iac-b2-frr-live-y-drift-verificado.md) · [B4](docs/sesiones/2026-10-13-b4-auditoria-fuentes-preparada.md).


> **ACTUALIZACIÓN REAL 13/10 22:30:** S01 **68/100 estimado**. OpenTofu `terraform_data` aplicado (5 registros metadata), Ansible dos candidatos FRR `COMPLIANT`, segunda corrida `changed=0`, segundo plan OpenTofu código0, VM intacta. **9 PNG IaC recibidos; 4 necesitan mejor encuadre**, desde logs sin repetir apply. Preparada próxima prueba de drift en copias y gate para usar configs IaC en B2, **NO ejecutadas aún**. [Bitácora](docs/sesiones/2026-10-13-iac-s01-ejecutado.md) · [Auditoría fotográfica](docs/evidencias/07-auditoria-visual-iac-s01-2026-10-13.md). Notas anteriores de 65/100 son históricas.


> **Estado vigente 13/10 22:16:** 62 PNG + 6 CSV **publicados en carpeta plana**, integridad SHA256 auditada, commit **[`328591a`](https://github.com/recm0708/netlab360/commit/328591acaed06431457b903dec6c7a2b91c39b25)**. S01 **65/100 técnico estimado**; IaC SoT OpenTofu/Ansible preparada **sin ejecutar**. [Runbook de siguiente fase](docs/sesiones/2026-10-13-iac-s01-opentofu-ansible-preparado.md). Los estados anteriores a este aviso son históricos.


> **Estado actual posterior al commit 570088c:** 57 PNG **publicados directamente** en [`evidencias/capturas/`](evidencias/capturas/); CSV de lotes 01–04 y mapa en [`evidencias/manifiestos/`](evidencias/manifiestos/). La VM Ubuntu conserva 4 directorios físicos antiguos tras `git mv`; el lote05 (5 PNG + CSV) **todavía NO está publicado**. Scripts corregidos en GitHub, pendiente sincronización y nueva importación. Progreso S01 **65% técnico estimado**, sin cambios. [Checkpoint](docs/REANUDAR-AQUI.md).


> **Estado vigente (13/10/2026 21:39):** S01 65% técnico estimado, LACP y active-backup virtual validados. 57 capturas PNG auditadas y publicadas, 5 nuevas pendientes. Migración segura para aplanar `evidencias/capturas/` preparada pero **no ejecutada**. Las notas antiguas inferiores con cifras/carpeta previas son históricas. [Continuidad](docs/REANUDAR-AQUI.md) · [Auditoría lote05](docs/evidencias/06-auditoria-lote05-dualnic-noc-2026-10-13.md).

## CHECKPOINT VIGENTE — 13/10/2026 20:52 PANAMÁ | LACP PROBADO + 20 PNG NUEVOS AUDITADOS

**Este estado prevalece sobre notas anteriores sobre LACP y fotos pendientes.** Usuario aportó salida real de Ubuntu: `b2-lacp-8023ad-dos-enlaces.sh --snapshot-confirmado` comprobó **IEEE802.3ad LACP active/fast, dos puertos en agregador de cada extremo, caída a UN puerto tras apagar a1/b1, recuperación a DOS puertos**, HTTP `NETLAB360_LACP_HTTP_OK` en los tres estados, `LACP_8023AD_TRES_ESTADOS=OK`, `RESULTADO_B2_LACP=0`, `RESULTADO_EJECUCION_LACP=0`, `RED_GESTION_INTACTA=SI`. Postcheck **20:51:35** Docker/netns vacíos, ens33 `192.168.47.40/24`, default `192.168.47.2`, docker/ssh/open-vm-tools activos, Git `main...origin/main` limpio en commit local `a8a9879` **antes de nuevos commits documentales**. Módulo bonding estaba disponible en `modinfo bonding`, se autoloadó, no hizo falta instalar programa. [Bitácora LACP](docs/sesiones/2026-10-13-b2-lacp-8023ad-verificado.md).

**S01 ahora 63% técnico estimado (+4 LACP, de 0/10 a 4/10; 37 pts totales pendientes), #1 aún ABIERTA**; no confundir LACP con dual-NIC VMware, switch/host de respaldo ni disponibilidad sin cortes.

**EVIDENCIAS VISUALES RECIBIDAS 20/20:** Usuario adjuntó todos los PNG B2_L2_02–07 (6), B2_L3_01–04_FINAL (4), B3_05–14 (10). **18 VÁLIDAS y 2 VÁLIDAS CON OBSERVACIÓN** (B2_L2_06 líneas nftwrap; B3_09_FINAL prompt sudo sin contraseña); 0 rechazadas, 20 SHA256 individuales registrados en [auditoría lote03](docs/evidencias/04-auditoria-visual-lote03-2026-10-13.md). Paquete ZIP descargable en la conversación `NETLAB360_LOTE03_20PNG_AUDITADOS_2026-10-13.zip` (1,011,954 bytes, SHA256 `9e11e1c3181ba62f53b1bde894f77ae4af0c6417beba1ebf10e578b90a342585`) y CSV manifiesto SHA256 generado. **ATENCIÓN: los 20 PNG están recibidos y auditados, pero NO FUERON subidos binariamente a GitHub aún**; transferir ZIP al clon Ubuntu, verificar SHA256, extraer 20 nuevos PNG a `evidencias/capturas/B2_B3_lote03` y commit/push verificado. **Los 24 PNG anteriores (lotes 01/02) SÍ están subidos**, no volver a solicitarlos ni duplicarlos.

**ÚNICAS FOTOS OBLIGATORIAS PENDIENTES DE RECEPCIÓN INMEDIATA:** `B2_LACP_01_Agregacion_Dos_Enlaces.png`, `B2_LACP_02_Falla_Un_Enlace.png`, `B2_LACP_03_Restauracion_Dos_Enlaces.png`, `B2_LACP_04_Postcheck_Final.png`. Fueron ejecutados los bloques de terminal LACP_01–03 y postcheck 04, pero **no se han recibido estas cuatro imágenes PNG para auditoría visual**. Tres fotos antiguas opcionales siguen opcionales. [Inventario actualizado](docs/evidencias/03-inventario-pendientes-auditoria-2026-10-13.md), issue #43.

**SIGUIENTE SCRIPT PREPARADO EN REPO, NO EJECUTADO:** `scripts/laboratorio/b2-dualnic-activebackup-http.sh` dos namespaces propios, bond `mode active-backup`, dos NIC veth por extremo, HTTP en primaria → falla primaria → HTTP por secundaria → recuperación de primaria disponible; limpieza en trap y prechecks de ens33/GW. [Diseño](docs/sesiones/2026-10-13-b2-dualnic-activebackup-preparado.md). **NO** atribuir puntos dualNIC al mero script. NO es dual NIC física VMware, ni redundancia de equipo real.

**SIGUIENTE RESPUESTA CON 10 PASOS** por preferencia del usuario, cubrir descarga ZIP Windows, SCP al guest, verificación SHA256, extracción segura/importación sólo 20 PNG, commit/push y verificación, 4 fotos LACP desde log, precheck y ejecución del ensayo dual-NIC si entorno libre. Si script falla, abortar pasos dependientes y hacer postcheck sin relanzar. Nunca tocar VMnet8/ens33/firewall/rutas de host.

---


## CHECKPOINT ACTUAL — 2026-10-13 19:45 PANAMÁ | HTTP HQ-S1 REAL SUPERADO, LACP SIGUIENTE

**PREVALECE sobre notas anteriores que decían HTTP E2E fallido o pendiente.** El usuario ejecutó el script corregido `b2-l3-http-clientes-wan.sh --snapshot-confirmado` y mostró: `OSPF_DUAL_FULL: SI`, `RUTAS_OSPF_BIDIRECCIONALES_WAN_P=OK`, `RESULTADO_B2_DUALWAN_UP=0`. Dos hosts namespace (cliente HQ `10.70.10.10/32`, servidor S1 `10.71.10.20/32:8080` unidos vía veth P2P al FRR, sin integración a trunk VLAN) se comunicaron HTTP correctamente tras seleccionar **WAN-P → WAN-B → WAN-P**. Marcadores `HTTP_WAN_PRINCIPAL=OK`, `HTTP_WAN_RESPALDO=OK`, `HTTP_WAN_RESTAURADA=OK`, `B2_L3_HTTP_TRES_ESTADOS=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`, `RESULTADO_EJECUCION_E2E=0`, limpieza B2 código0. **No se probó ausencia absoluta de interrupciones HTTP durante la transición**. [Bitácora real](docs/sesiones/2026-10-13-b2-l3-http-hq-s1-wan-tres-estados-verificados.md).

**Postcheck real 19:44:57:** Docker/netns vacíos, marcador B2 ausente, ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios docker/ssh/open-vm-tools activos, Git limpio sincronizado con `6a3e50f` (antes de nuevos commits). B2_L3_01/02/03/04_FINAL con bloques console realmente emitidos y extraídos, considerados tomados según usuario **pero los PNG no se han recibido ni auditado ni versionado físicamente**. Conservar captura B2_L3_04 anterior como histórico de primer intento fallido. Log original `~/netlab360-bootstrap/evidencias/b2-l3-http-wan-20261013-194254.log` solo VM.

**Matriz S01 ahora 59% técnico provisional** (B2-L3 18/18, +1 pt; resto 41 puntos). La fase S01 está ABIERTA (11 criterios integrales pendientes); semana académica 9. Evitar más pruebas OSPF/HTTP repetidas. El siguiente bloque es LACP/dual-NIC y luego IaC: [plan LACP](docs/sesiones/2026-10-13-lacp-8023ad-preparado-tras-http-wan.md).

**NUEVO SCRIPT YA EN REPO, SIN EJECUTAR:** `scripts/laboratorio/b2-lacp-8023ad-dos-enlaces.sh`. Pide snapshot confirmado, crea solo namespaces `nl360-lacpa` y `nl360-lacpb`, bonds modo IEEE802.3ad a ambos lados con 2 enlaces veth, `miimon100`, `lacp_rate fast`. Prueba agregador realmente activo **2→1→2 puertos** según `/proc/net/bonding/bond0`, HTTP de A→B funcional en tres estados, trap cleanup de sus namespaces y resguardo ens33/rutas. **No acredita doble NIC de VM o equipos, no modifica VMnet8 ni host firewall.** Módulo `bonding` antes no visible en /sys/module; no significa ausencia: si no soportado, aborta con log y cleanup. **No declarar probado/sumar puntos aún.**

**Próxima tanda de 10 pasos, solicitada expresamente:** 105 pull y sintaxis, 106 precheck recursos y gestión, 107 verificar capacidades/soporte bonding no destructivo, 108 imagen/estado Git y preflight snapshot, 109 ejecutar UNA sola vez LACP, 110 inspeccionar resumen log y `LACP_8023AD_TRES_ESTADOS`, 111–113 capturas B2_LACP_01/02/03 desde log sin relanzar, 114 postcheck B2_LACP_04_Final con Docker/netns y ens33/GW intactos, Git limpio. **Si falla alguna guardia, no avanzar al ensayo; si ejecución LACP falla, detener y compartir error sin repetir.** Tras LACP, dar bloque de 8–12 pasos para dual NIC/host y IaC. El usuario pidió mínimo 8–10 pasos por turno, no microfragmentar avances.

---


## NUEVO CHECKPOINT — 2026-10-13 19:16 PANAMÁ | ACL/HTTP INTRA-HQ OK, E2E WAN PREPARADO

**Supera los bloques anteriores que decían ACL pendiente.** El usuario ejecutó realmente y validó `scripts/laboratorio/b2-l2-acl-http-real.sh --snapshot-confirmado` entre 19:14 y 19:15: cliente VLAN110 `10.70.10.10`, servidor VLAN120 `10.70.20.20`, switches con trunk y router con `eth0.110 10.70.10.1` / `eth0.120 10.70.20.1`. Baseline sin ACL: **HTTP8080 OK, HTTP8081 OK** desde cliente. Luego `nft` exclusivamente en router: HTTP8080 permitido, HTTP8081 bloqueado con `curl (28) Connection timed out` esperado **aunque el servicio 8081 seguía activo**; nft contadores **8080 accept 1 pkt/60 bytes, 8081 drop 2 pkt/120 bytes**. `ACL_ROUTER_NAMESPACE=OK`, `RESULTADO_B2_L2_ACL_HTTP=0`, `RESULTADO_EJECUCION_ACL_HTTP=0`, `RED_GESTION_INTACTA=SI`. Postcheck 19:15:56 Docker/netns vacíos, `ens33 192.168.47.40/24`, default `192.168.47.2`, docker/ssh/open-vm-tools activos. `GIT_SINCRONIZADO: SI`, commit local `89c2541` antes de nuevos cambios en GitHub. Bitácora oficial [`docs/sesiones/2026-10-13-b2-l2-acl-http-real-validado.md`](docs/sesiones/2026-10-13-b2-l2-acl-http-real-validado.md). Log original local `~/netlab360-bootstrap/evidencias/b2-l2-acl-http-20261013-191413.log`, **no subido**.

**S01 ACTUALIZADO A 58% TÉCNICO ESTIMADO** (+3 de 55, B2-L2 8/10); mantener issue #1/#30 abiertas por criterios integrales aún pendientes. Capturas **B2_L2_05/06/07** solicitadas/tomadas por convención, pero PNG no recibidos/inspeccionados ni versionados. Los 24 PNG originales auditados permanecen versionados. Importante no confundir HTTP inter-VLAN HQ con HTTP entre HQ-S1.

**PRÓXIMO SCRIPT VERSIONADO, NO EJECUTADO:** [`scripts/laboratorio/b2-l3-http-clientes-wan.sh`](../scripts/laboratorio/b2-l3-http-clientes-wan.sh), hace una sola secuencia automatizada `B2 precheck→up→cliente HQ real 10.70.10.10/32 en namespace→servidor Python HTTP S1 10.71.10.20/32 en namespace→HTTP WAN-P→fail y rutas bidireccionales wan-b→HTTP WAN-B→restore y wan-p→HTTP WAN-P→EXIT cleanup`. Los hosts se conectan a R-HQ/R-S1 **por enlaces veth P2P aislados 169.254.70/71 y rutas /32**, preservando las LAN dummy que anuncia OSPF: es HTTP WAN real pero **NO** significa que los hosts se hayan conectado físicamente al trunk 802.1Q ni que haya VLAN entre sedes. `trap EXIT` borra namespaces y servidores propios y después ejecuta `b2-dualwan-ospf.sh down`, revisa IP/tabla de rutas del host. Scripts nuevos GitHub están por delante de Ubuntu: requiere `git pull --ff-only origin main` y `bash -n` antes de probar.

**SIGUIENTE BLOQUE AGRUPADO:** 1) pull + sintaxis, precheck ningún contenedor ni `nl360-e2e-*` ni `estado-b2-dualwan`, red ens33/GW intactos; 2) ejecutar `bash scripts/laboratorio/b2-l3-http-clientes-wan.sh --snapshot-confirmado` UNA VEZ (puede tardar por OSPF ~60s); 3) capturas `B2_L3_01` (HTTP WAN-P), `B2_L3_02` (HTTP WAN-B), `B2_L3_03` (HTTP WAN-P restaurada), postcheck `B2_L3_04`; 4) exigir `HTTP_WAN_PRINCIPAL=OK`, `HTTP_WAN_RESPALDO=OK`, `HTTP_WAN_RESTAURADA=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`. Cualquier fallo: NO repetir, verificar cleanup y enviar salida. No instalar paquetes ni modificar VMnet8/ens33, firewall o rutas del host. El script **no debe contarse como probado ni sumar puntos hasta ejecución observada**. Después dirigir esfuerzos a LACP/dual NIC e IaC, y documentación académica en paralelo por retraso semana 9.

---


## PUNTO MÁS RECIENTE — 13/10/2026 19:01 PANAMÁ | B2-L2 TRUNK/ISOLAMIENTO 802.1Q REAL APROBADO

**Previo a la próxima sesión en VM:** pull ff-only de nuevos commits GitHub de este turno. El usuario ejecutó **realmente** `bash scripts/laboratorio/b2-l2-trunk-8021q.sh --snapshot-confirmado`; resultados **`RESULTADO_SINTAXIS_TRUNK=0`**, `PRUEBA_TRUNK_VLAN110=OK` (3/3 ping), `PRUEBA_TRUNK_VLAN120=OK` (3/3), aislamientos negativos entre VLAN con prefijo on-link **0 recibidos/3 enviados** y mensajes `Destination Host Unreachable`, ping dentro VLAN110/120 conservó 2/2 cada, `B2_L2_TRUNK_Y_AISLAMIENTO=OK`; `RESULTADO_B2_L2_TRUNK=0` y `RESULTADO_EJECUCION_TRUNK=0`, `RED_GESTION_INTACTA=SI`. Postcheck a **19:01:44** Docker/netns vacíos, `ens33=192.168.47.40/24`, gateway `192.168.47.2`, 3 servicios activos, Git limpio respecto `main...origin/main` del momento. Log ORIGINAL local `~/netlab360-bootstrap/evidencias/b2-l2-trunk-20261013-190000.log`, no copiado al repo. **No repetir trunk aislado** salvo diagnóstico justificado.

**Matriz S01 actualizada a 55% técnico estimado** (+2 B2-L2, de 3/10 a 5/10). Sólo se acreditó VLAN trunk en **dos switches dentro de HQ**, no WAN intersedes, no ACL L3, no servicio HTTP. [Bitácora de prueba realmente superada](docs/sesiones/2026-10-13-b2-l2-trunk-8021q-verificado-y-acl-preparada.md), matriz `docs/control/01-avance-s01.md`, issues #1/#30/#35/#42/#43 actualizadas.

**Nuevo script LISTO, PERO SIN EJECUTAR NI VALIDAR EN VM:** [`scripts/laboratorio/b2-l2-acl-http-real.sh`](../scripts/laboratorio/b2-l2-acl-http-real.sh). Crea exclusivamente namespaces con prefijo `nl360-acl`, switches VLAN110/120 unidos por trunk y router aislado con subinterfaces eth0.110/eth0.120, hosts 10.70.10.10 y 10.70.20.20 y dos servidores Python `HTTP 8080/8081`. Baseline demuestra que **ambos puertos responden antes de ACL**. Después nftables en **network namespace del router, nunca host**, permite TCP8080 y bloquea TCP8081, confirmado con curl y nft counters; cleanup via trap mata servidores en namespaces propios y retira solo recursos creados, comprueba ens33 y tabla host inalterados. Capturas **B2_L2_05** baseline, **B2_L2_06** ACL/negativa, **B2_L2_07** postcheck. **NO concede puntos adicionales hasta ejecución real**; si falla, no repetir. Esta prueba es **intra-HQ**, no convierte LAN de R-S1 ni prueba WAN HQ-S1. **Próxima integración** será cliente/servicio verdaderos atravesando WAN OSPF ya validada (no repetir solo por repetir failover).

**Próximas acciones agrupadas solicitadas por usuario:** pull ff-only; `bash -n scripts/laboratorio/b2-l2-acl-http-real.sh`, herramientas nft/curl, IPAM, precheck red, Docker/netns vacíos, confirmar no hay names `nl360-acl*`. Ejecutar **una sola vez** `bash scripts/laboratorio/b2-l2-acl-http-real.sh --snapshot-confirmado`; exigir `BASELINE_HTTP_8080=OK`, `BASELINE_HTTP_8081=OK`, `ACL_HTTP_8080_PERMITIDO=OK`, `SERVICIO_8081_EN_VLAN120=ACTIVO`, `ACL_HTTP_8081_DENEGADO=OK`, `RESULTADO_B2_L2_ACL_HTTP=0`. Postcheck Docker/netns vacíos, host intacto, Git limpio. Si falla, revisar log y residuo de namespace **sin tocar host firewall, ens33, VMnet8 ni gateway**. B2_L2_02/03/04 consideradas capturadas por usuario, PNG aún no recibidos/inspeccionados.

---


## CHECKPOINT VIGENTE — 13/10/2026 18:36 PANAMÁ | PROMETHEUS ALERTAS FIRING/RESUELTAS, LABORATORIO LIMPIO

**Este bloque prevalece sobre todas las notas anteriores que indican reglas no cargadas o puertos ocupados.** El usuario completó pasos 70–80 y compartió salida real de las tres terminales: **Prometheus 3.7.0 cargó tres reglas** después de generar glob absoluto en `scripts/observabilidad/ejecutar-prometheus-local.sh`; `/api/v1/rules` mostró 1 grupo, 3 reglas, scrape `up=1`, `B3_REGLAS_LISTAS=SI`, código0, evidencia **B3_11**. `b2-dualwan-ospf.sh up` obtuvo doble OSPF Full y ruta WAN-P (código0); `fail` conmutó a WAN-B (`RESULTADO_FAIL_PROMETHEUS=0`). A **18:33:35** Prometheus devolvió **`NETLAB360WANPrimaryDown=firing` (warning)** y **`NETLAB360WanBackupSelected=firing` (info)**; evidencia **B3_12**. A **18:34:09** `restore` retornó WAN-P (`RESULTADO_RESTORE_PROMETHEUS=0`); a 18:34:36 API `ALERTAS_WAN_ACTIVAS=0`, `ALERTAS_WAN_RESUELTAS=SI`, evidencia **B3_13**.

**Cierre confirmado:** `down` B2 código 0, exporter topology OFFLINE, Terminales 1 y 2 detenidas con Ctrl+C limpio. Postcheck **18:36:03** (**B3_14**) `PUERTO_9090_LIBRE:SI`, `PUERTO_9108_LIBRE:SI`, Docker sin contenedores, netns vacíos, `ens33 UP 192.168.47.40/24`, GW `192.168.47.2`, docker/ssh/open-vm-tools activos. `git status` `## main...origin/main` limpio a la hora de esa comprobación **antes** de nuevos commits de documentación. **No volver a ejecutar WAN-P fail/restore por segunda vez** para constatar Prometheus: está demostrado. No hay servicios de laboratorio que dejar corriendo según postcheck.

**Estado de capturas:** B3_05–B3_14 y B3_09_FINAL se presumen **tomadas** por regla del usuario, con resultados de consola del nuevo grupo B3_11–14 inspeccionados textualmente; **sus PNG todavía NO han sido enviados/auditados visualmente ni subidos**. Los 24 PNG originales de lotes 01/02 B1/B2/B3 sí fueron recibidos, visualmente auditados y físicamente publicados GitHub; no confundir conjuntos.

**Resultado y límites:** matriz [`docs/control/01-avance-s01.md`](docs/control/01-avance-s01.md) ahora **53% técnico estimado** (B3 10/15) tras alertas reales. **No Alertmanager ni receptores/notificaciones**, ni dashboard NOC multisitio integral ni SLI/SLO formal. S01 issue #1 permanece ABIERTA; no afirmar aceptación 11/11. [Bitácora B3 Prometheus firing/recuperación](docs/sesiones/2026-10-13-b3-prometheus-alertas-firing-y-resolucion-verificadas.md). [Plan de recuperación desde semana 9](docs/control/02-plan-recuperacion-semana-09.md): prioridad siguiente **B2-L2 VLAN/trunk/ACL y cliente-servicio realmente extremo a extremo**, seguido de LACP/dual-NIC, IaC OpenTofu/Ansible, IA evaluada y entregables/release/OVA, con consulta docente en #36. Evitar seguir sobreoptimizando OSPF y Prometheus.

**Para retomar en Ubuntu:** `cd ~/proyectos/netlab360; GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main; git status --short --branch; sudo docker ps -a; sudo ip netns list; ip -4 -br addr show ens33; ip -4 route show default`. Verificar que los archivos `.gitignore`, scripts y docs nuevos bajaron. **NO** tocar `ens33`, VMnet8, default gateway, NetworkManager ni la red de administración. **No** ejecutar cierre/apagado automáticamente; solo si el usuario lo solicita. Entregar varios pasos de una vez por preferencia expresa del usuario.

---


## ACTUALIZACIÓN MÁS RECIENTE — 13/10/2026 17:45 PANAMÁ | B3 LIVE WAN COMPLETADO, CIERRE DE PUERTOS PENDIENTE

**Falla real y recuperación observadas, NO repetir la topología B2:** prueba 17:38–17:45 reportada por usuario: `status` OSPF 2 vecinos Full, WAN-P UP; `fail` código 0, ruta WAN-B y eventos del exporter `WAN_PRIMARY_DOWN` + `WAN_ROUTE_CHANGED` a **17:39:33.189**. `restore` código 0, `WAN_PRIMARY_RESTORED` a **17:42:05.813** (aún FIB WAN-B) y FIB WAN-P `WAN_ROUTE_CHANGED` a **17:42:15.841**. Contadores down=1, restored=1, route_changed=2; `down` B2 con limpieza código0, `TOPOLOGY_STOPPED` 17:44:56; exporter reflejó `topology=offline`. Cinco eventos JSONL guardados localmente `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl`; **no versionados físicamente**. [Bitácora completa](docs/sesiones/2026-10-13-b3-live-ciclo-incidente-wan-verificado.md).

**Resultado crítico de postcheck:** captura B3_09 a 17:45:10 imprimió `PUERTO_9108_LIBRE: NO`, ya que exporter aún estaba activo; Docker/netns vacíos, host ens33 `192.168.47.40/24`, gateway `192.168.47.2` y servicios activos. PowerShell 3 seguía con túnel `ssh -N -L 9108:127.0.0.1:9108 netlab360` y errores repetidos `Connection refused` hacia destino; **primero terminar con Ctrl+C en PowerShell 3 y Terminal SSH 1 SI AÚN ESTÁN ACTIVAS, sin matar procesos al azar**, luego comprobar con `ss` puerto 9108 libre. Captura adicional **B3_09_Postcheck_Telemetria_Viva_Final.png** solo consulta read-only. B3_05–B3_09 se asumen tomadas según usuario, **sus PNG aún no están recibidos/inspeccionados**, a diferencia de los 24 PNG auditados de B1/B2/B3 anterior.

**Git local sincronizado en commit `2c468d1` pero `git status` NO limpio** por `?? servicios/observabilidad/__pycache__/` y `?? tests/__pycache__/` creados por Python. NUEVA [`.gitignore`](.gitignore) en GitHub para excluirlos; `git pull --ff-only origin main` debe dejarlos ignorados, sin `reset --hard`. **S01 actualizado a 48% estimado** (B3 5/15 por eventos live, Prometheus NO realizado; antes 45%).

**PRÓXIMA ETAPA VERSIONADA PERO NO EJECUTADA:** [plan Prometheus real](docs/operaciones/plan-b3-prometheus-local.md), archivos `servicios/observabilidad/prometheus/prometheus.yml`, `rules/wan-alerts.yml`, `scripts/observabilidad/preparar-prometheus-local.sh` y `ejecutar-prometheus-local.sh`. Estrategia segura: extraer binarios de imagen versionada `quay.io/prometheus/prometheus:v3.7.0` desde contenedor temporal `--network none`, **no se ha comprobado todavía la existencia de esa etiqueta en Ubuntu**, ejecutar Prometheus como proceso de usuario en `127.0.0.1:9090` y exporter habitual en `127.0.0.1:9108`; sin alterar host NIC/gateway, no usar Docker host network ni publicar puertos de VMware. El objetivo es demostrar **scrape real/TSDB y reglas cargadas**; luego un nuevo ensayo de alerta real con WAN-P DOWN/UP si procede. No atribuir Prometheus instalado ni alerta firing antes de pruebas.

**Issues #1/#12/#15/#20/#21/#35/#43** actualizadas; S01 sigue abierta. Evitar nuevos fallos mediante preflight, separación clara de terminales y verificación de puertos.

---


> **Corte B3 verificado — 13/10/2026 16:09 Panamá:** la API Python y el panel NOC **HISTÓRICO / NO EN VIVO** funcionaron en la VM; `GET /`, `/healthz`, `/api/v1/baseline` y `/metrics` respondieron 200, y el navegador quedó documentado mediante **dos PNG realmente recibidos e inspeccionados** (`B3_03` partes 1/2). Hubo postcheck intermedio 15:52 con puerto 8765 ocupado y **postcheck posterior 16:09:58 con puerto libre**. Se recibieron y auditaron **24 PNG (19 B1/B2 + 5 B3)**; [lote 01](docs/evidencias/01-auditoria-visual-b1-b2-2026-10-13.md) / [lote 02](docs/evidencias/02-auditoria-visual-b3-2026-10-13.md). **Los 19 archivos B1/B2 están staged en Ubuntu pero NO subidos**, pues el commit falló por identidad Git; los 5 B3 siguen empaquetados, todavía no importados. **S01 ~45% estimado** ([matriz](docs/control/01-avance-s01.md)); SIN Prometheus ni monitoreo/alarma WAN en vivo. Prioridad inmediata: corregir identidad Git solo en repo, commit/rebase/push de evidencias y empezar instrumentación viva tras revisión.


> **Actualización de B3 (13/10/2026 15:29 Panamá):** la VM se reanudó y mantuvo con red/servicios correctos. El usuario recuperó CSV B2 (76/76 ICMP y `CSV_INTEGRIDAD: OK`) y generó realmente un **resumen JSON y métricas `.prom` retrospectivas**, `B3_ANALISIS_RETROSPECTIVO=OK`. Se versionó un nuevo prototipo de [API y panel NOC histórico](servicios/noc-historico/README.md) basado en Python estándar, **pendiente de validación y ejecución en Ubuntu**. **Prometheus, telemetría en vivo, alertas y dashboard NOC dinámico NO están desplegados.** [Bitácora B3-01](docs/sesiones/2026-10-13-b3-linea-base-retrospectiva-validada.md). S01 se mantiene en **43% estimado**, no se incrementa por preparar código.


> **Estado verificado (2026-10-13, 11:52 Panamá):** S01 **abierta, ~43% estimado** (ver [control ponderado](docs/control/01-avance-s01.md)); base Ubuntu/VMware, VMnet8/SSH y snapshot completos; IPAM draft validado, ensayo VLAN L2 completado y **FRRouting v5 con zebra/ospfd/OSPF local funcionando**, además de **dos routers R-HQ/R-S1 con OSPF Full por WAN principal/respaldo, conmutación y restauración de FIB comprobadas**. Se comprobaron **30/30 pings ICMP entre interfaces LAN simuladas de los routers, en ambos sentidos y tres estados**, más **76/76 sondeos ICMP** durante ensayo temporal de interrupción/restauración (cero pérdidas observadas, sin garantizar continuidad entre muestras). Faltan medición durante la conmutación, clientes/servicios reales, métricas/alertas, API/dashboard, IaC del laboratorio e IA.

**Título académico:** Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico inteligente de redes empresariales multisede.

## Objetivo

Construir una plataforma en una máquina virtual Ubuntu Desktop para reproducir una red empresarial segmentada con sede principal, sucursales, rutas WAN redundantes, agregación de enlaces, equipos con redundancia verificable, herramientas de automatización y dashboards de observabilidad con escenarios de fallas controladas y analítica de anomalías.

## Entregas incrementales

| Hito | Período (2026) | Alcance |
| --- | --- | --- |
| [S01](https://github.com/recm0708/netlab360/issues/1) | 5–11 oct. | MVP transversal, pruebas de viabilidad |
| [S02](https://github.com/recm0708/netlab360/issues/2) | 12–18 oct. | Multisede, LACP y capacidad |
| [S03](https://github.com/recm0708/netlab360/issues/3) | 19–25 oct. | Network as Code, IaC y compliance |
| [S04](https://github.com/recm0708/netlab360/issues/4) | 26 oct.–1 nov. | Observabilidad e incidentes |
| [S05](https://github.com/recm0708/netlab360/issues/5) | 2–8 nov. | Redundancia de equipos y SDN |
| [S06](https://github.com/recm0708/netlab360/issues/6) | 9–15 nov. | Ingeniería de datos e IA evaluada |
| [S07](https://github.com/recm0708/netlab360/issues/7) | 16–22 nov. | AIOps con aprobación humana |
| [S08](https://github.com/recm0708/netlab360/issues/8) | 23–29 nov. | Regresión, documentación y OVA |

El detalle de aceptación por fase se encuentra en las issues semanales. Cada fase debe conservar capacidades verificables de red, automatización, observabilidad, analítica, interfaz y documentación. Las fechas y requisitos se ajustarán cuando la docente confirme la rúbrica.

## Entregables continuos

1. Informe académico en APA 7.
2. Bitácora de implementación con capturas, comandos y evidencias.
3. Manual de usuario ilustrado.
4. VM exportable e importada con éxito, sanitizada y acompañada de SHA-256.

## Fuente de verdad y seguridad

Los archivos de configuración, scripts y documentación se conservarán en Git; el estado observado de la red se validará operacionalmente. No incorporar credenciales, claves privadas, estados sensibles de OpenTofu ni discos de VM en este repositorio.

## Ejecución actual y siguiente paso

- [Plan operativo, fases técnicas y pausas](docs/05-plan-operativo-y-pausas.md): primero B0 (línea base y salud) y B1 (arquitectura/IPAM), después MVP funcional de falla observada, telemetría, interfaz y analítica, con pausas tras avances verificables.
- [Estado de continuidad](docs/00-estado-y-continuidad.md) y [preparación técnica](docs/sesiones/2026-10-12-preparacion-base-validada.md).
- **Issues cerradas:** [#39](https://github.com/recm0708/netlab360/issues/39) (dirección IPv4), [#40](https://github.com/recm0708/netlab360/issues/40) (GitHub CLI y clonación) y [#41](https://github.com/recm0708/netlab360/issues/41) (herramientas y snapshot VMware confirmado). **S01 continúa abierta** en [#1](https://github.com/recm0708/netlab360/issues/1).
- **Subhitos funcionales cerrados dentro de issues abiertas:** B1 IPAM (#11), B2-L2 VLAN aislada (#30/#12) y FRRouting v5 en un contenedor (#42) con [evidencia técnica](docs/sesiones/2026-10-12-smoke-frr-v5-exitoso.md). **Subhito B2 probado:** ICMP LAN bidireccional `30/30` por WAN-P/WAN-B/WAN-P, [bitácora](docs/sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md) y rollback limpio; [ensayo temporal de 76/76 muestras](docs/sesiones/2026-10-13-b2-convergencia-icmp-continuo-verificada.md), primer cambio FIB observado a 0.186 s y retorno a 10.147 s (aproximación por sondeo). **Siguiente prioridad:** telemetría/alarma/dashboard (#12), clientes y servicios reales; #42 abierta hasta criterios restantes.
- **Seguimiento y evidencias:** [control S01](docs/control/01-avance-s01.md), [backlog semanal S01](backlog/semanas/01-semana-1.md), [auditoría posterior de capturas #43](https://github.com/recm0708/netlab360/issues/43).
- El archivo `NETLAB360_Planificacion_v0.2.zip` se importará solo tras revisión y **sin sobrescribir** documentos nuevos ni duplicar issues existentes; no está importado todavía.

**Protección de credenciales:** el GitHub CLI autenticado dentro del invitado puede contener un token local; se debe eliminar/sanitizar antes de compartir OVA y jamás versionarlo.
