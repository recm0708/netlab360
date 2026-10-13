# NETLAB360 — Planificación semestral

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
