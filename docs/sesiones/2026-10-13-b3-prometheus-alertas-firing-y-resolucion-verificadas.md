# NETLAB360 — B3: Prometheus con alertas WAN `firing`, resolución y limpieza verificadas

**Ejecución real:** 2026-10-13, 18:29–18:36 hora Panamá (UTC−05).  
**Fuente de evidencia:** transcripción completa de Terminales 1, 2 y 3 proporcionada por el operador. **Los PNG B3_11–B3_14 se consideran tomados por su convención, pero NO han sido recibidos ni inspeccionados visualmente, ni subidos al repositorio.** La transcripción aportada tampoco implica respaldo del archivo JSONL o TSDB a GitHub.

## Estado y alcance del hito

Se completó el ciclo **exporter FRR actual → Prometheus 3.7.0 TSDB/scrape → reglas evaluadas → alertas `firing` durante corte WAN-P → resolución observada después de recuperar WAN-P → `down` y cierre sin residuos**. Las reglas de Prometheus sí funcionan. **No existe evidencia de Alertmanager desplegado, receptor de notificaciones, SLI/SLO formal ni interfaz NOC multisitio terminada.**

## Evidencia cronológica

| Hora local | Acción / fuente | Resultado efectivamente observado |
|---|---|---|
| 18:29:16 | Prometheus relanzado con `scripts/observabilidad/ejecutar-prometheus-local.sh` ya corregido | Ruta absoluta `/home/rc-aa-ec/proyectos/netlab360/servicios/observabilidad/prometheus/rules/*.yml`; `promtool check config` SUCCESS, 1 rule file found; `promtool check rules` SUCCESS, 3 rules found; TSDB y regla manager iniciados |
| 18:29:34 | **B3_11** / API Prometheus `/api/v1/rules` | **1 grupo, 3 reglas**, `NETLAB360WANPrimaryDown`, `NETLAB360ExporterUnavailable`, `NETLAB360WanBackupSelected`, scrape `UP=1`, `B3_REGLAS_LISTAS: SI`, código0 |
| 18:30:07–18:30:35 | Precheck/arranque B2 | `RESULTADO_B2_DUALWAN_PRECHECK=0`, `RESULTADO_UP_PROMETHEUS=0`, 2 adyacencias OSPF Full por router, FIB de HQ a S1 por `wan-p`; exporter y queries **de Prometheus** verifican enlace primario `1` y ruta WAN-P `1` |
| 18:33:16–18:33:17 | `fail` de B2 y eventos del exporter | `RESULTADO_FAIL_PROMETHEUS=0`, `CONMUTACION_WAN_B: OK (sondeo 1)`; FIB `10.71.10.1 via 10.78.0.6 dev wan-b`; exporter observó `WAN_PRIMARY_DOWN` y `WAN_ROUTE_CHANGED` a 18:33:17.515 |
| 18:33:35 | **B3_12** / `/api/v1/alerts` | WAN-P administrativamente caída, selección `wan-b`, datos frescos; **`NETLAB360WANPrimaryDown = firing` (warning)** y **`NETLAB360WanBackupSelected = firing` (info)**. `activeAt` de ambas `2026-10-13T23:33:18.919658435Z` |
| 18:34:09–18:34:20 | `restore` | `RESULTADO_RESTORE_PROMETHEUS=0`, `RESTAURACION_WAN_P: OK (sondeo 11)`, 2 vecinos Full de nuevo, FIB HQ→S1 `wan-p`; exporter registró WAN_PRIMARY_RESTORED a 18:34:10.494 y WAN_ROUTE_CHANGED a WAN-P 18:34:20.415; son tiempos observados de muestreo, no medidas exactas de convergencia |
| 18:34:36 | **B3_13** / consulta API | Exporter `wan_primary_admin_up=1`, `selected_link=wan-p`, `fresh=true`; API Prometheus `ALERTAS_WAN_ACTIVAS: 0`, `ALERTAS_WAN_RESUELTAS: SI`. No se probó un receptor de Alertmanager |
| 18:35:20–18:35:25 | `down` de B2 | `RESULTADO_DOWN_PROMETHEUS=0`; Docker y `ip netns` vacíos; exporter `topology=offline`, routers HQ=0, S1=0, seleccion `none`; evento `TOPOLOGY_STOPPED` a 18:35:21.956 |
| 18:35:46–18:35:47 | Cierre de Terminal 1 y 2 | Exporter `B3_LIVE_SERVIDOR_DETENIDO=SI`; Prometheus recibió SIGINT y finalizó de manera ordenada con `See you next time!` |
| 18:36:03 | **B3_14** postcheck | `PUERTO_9090_LIBRE: SI`, `PUERTO_9108_LIBRE: SI`, contenedores y namespaces vacíos; `ens33 UP 192.168.47.40/24`, gateway `192.168.47.2`, servicios Docker/SSH/open-vm-tools activos y Git `## main...origin/main` limpio |

### Elementos técnicos verificados

- **FRRouting:** `quay.io/frrouting/frr:10.7.1` (digest consultado en precheck), topología aislada, dos adyacencias Full, rutas de tráfico según preferencia OSPF, retorno.
- **Exporter:** `servicios/observabilidad/live_exporter.py`, `http://127.0.0.1:9108`, lectura del enlace y de la FIB en la namespace de routers, eventos JSONL.
- **Prometheus:** binarios v3.7.0 obtenidos desde imagen de contenedor; ejecución como usuario normal en `http://127.0.0.1:9090`, TSDB local, fuente `netlab360-frr-live`, scrape `up=1`, tres reglas activas tras corrección de glob absoluto. **No se confunde la exposición /metrics con scrape, ni reglas cargadas con alertas firing; se probaron ambos separadamente.**
- **Evidencias:** B3_11 (reglas), B3_12 (firing doble), B3_13 (resueltas), B3_14 (limpieza) y anterior B3_10 (scrape). Se presumen capturadas por regla del usuario; **no se dice que fueron recibidas ni publicadas**. Las 24 PNG del lote 01/02 anterior sí están auditadas/publicadas.
- **Seguridad:** ningún cambio a VMware VMnet8, `ens33`, rutas administrativas, firewall, ni red de gestión; todo HTTP escuchó en loopback.

### Límites y siguientes bloques

1. **Prometheus sin Alertmanager**: no hay evidencia de entrega de una notificación a un receptor ni historial de resolución transmitido fuera del motor de reglas. Las alertas ya no figuran activas en la API después de recuperación, lo cual sí está demostrado.
2. **S01 aún incompleta:** VLAN/trunks/ACL, LAG/LACP de dos puertos y host dual-NIC, servicio extremo-a-extremo, IaC OpenTofu/Ansible en la topología, prototipo IA evaluable, documentación formal, CI/release, OVA sanitizada/reimportada/SHA256; rúbrica académica por ratificar (issue #36).
3. **Avance técnico provisional:** del **50% al 53%**; B3 pasa de **7/15 a 10/15** por reglas realmente cargadas y alertas firing/resueltas. Los 5 puntos B3 restantes NO se acreditan: Alertmanager/entrega externa, integración NOC multi-sede, niveles de servicio/cadena de extremo a extremo. Este indicador no representa aceptación de S01 ni calificación.
4. **Ritmo de recuperación:** semana 9. El siguiente trabajo debe priorizar la matriz de criterios mínimos para S01, no repetir B3. Recomendación inmediata: B2-L2 VLAN/ACL y servicio cliente real, luego LACP y IaC, con objetivos de evidencias integrales; la secuencia exacta debe alinearse a la rúbrica.

**Scripts/bitácoras relacionados:** `scripts/laboratorio/b2-dualwan-ospf.sh`, `servicios/observabilidad/prometheus/prometheus.yml`, `servicios/observabilidad/prometheus/rules/wan-alerts.yml`, `scripts/observabilidad/ejecutar-prometheus-local.sh`; [checkpoint](../REANUDAR-AQUI.md), [matriz S01](../control/01-avance-s01.md).
