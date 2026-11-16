# NETLAB360 — B3 prueba real completa: detección WAN, failover, restauración y limpieza

**Fecha de ejecución:** 13 de octubre de 2026, 17:38–17:45 hora Panamá (-05:00).  
**Fuente:** salida integral realmente enviada por usuario de terminales SSH 1, 2 y PowerShell 3.  
**Estado:** **ciclo WAN dinámico verificado técnicamente**, con eventos en dashboard/API, dos rutas y limpieza B2 completada; **cierre de exporter/puerto 9108 no confirmado en el último postcheck**, ni se han recibido aún los PNG B3_05–B3_09 para inspección visual.

## 1. Baseline (17:38)

- `bash scripts/laboratorio/b2-dualwan-ospf.sh status` -> `RESULTADO_STATUS_B3=0`; R-HQ/R-S1 tienen **dos vecinos OSPF Full por router** y LANs `10.70.10.0/24`, `10.71.10.0/24` con rutas OSPF por WAN-P.
- Exporter HTTP en `127.0.0.1:9108` consultado directamente, `ESTADO_BASELINE_APTO: SI` a 17:38:03.
- Captura solicitada **B3_05** (17:38:10), datos `topology=active`, routers `hq=1,s1=1`, `source_ok=1`, `fresh=true`, `wan_primary_admin_up=1`, `selected_link=wan-p`. `/metrics` source_up=1, WAN-P=1, WAN-B=0, contadores WAN=0 al inicio.

## 2. Corte WAN-P (17:39)

- `bash scripts/laboratorio/b2-dualwan-ospf.sh fail` a **17:39:32 -05:00**, `RESULTADO_FAIL_B3=0`, `WAN_PRIMARIA: DOWN`, `CONMUTACION_WAN_B: OK (sondeo 1)`. FIB HQ `10.71.10.1 via 10.78.0.6 dev wan-b` y vecindad OSPF por WAN-B Full.
- Exporter emitió `WAN_PRIMARY_DOWN` y `WAN_ROUTE_CHANGED` a **17:39:33.189 -05:00**, ambos con `selected_link=wan-b`; severidades warning e info.
- Captura solicitada **B3_06** (17:40:34): API `topology=active`, `fresh=true`, `wan_primary_admin_up=0`, `selected_link=wan-b`, contadores `wan_down=1`, `wan_restored=0`, `route_changed=1`.

## 3. Restauración WAN-P (17:42)

- `bash scripts/laboratorio/b2-dualwan-ospf.sh restore` desde **17:42:05 -05:00**, `RESULTADO_RESTORE_B3=0`, `WAN_PRIMARIA: UP`, `RESTAURACION_WAN_P: OK (sondeo 11)`; FIB regresa `10.71.10.1 via 10.78.0.2 dev wan-p`. OSPF dos vecinos Full de nuevo.
- Exporter registró `WAN_PRIMARY_RESTORED` a **17:42:05.813**, aún con `selected_link=wan-b` en esa instantánea (coherente: la interfaz vuelve UP antes de que la mejor ruta OSPF se seleccione).
- Exporter registró `WAN_ROUTE_CHANGED` a **17:42:15.841** (FIB `wan-p`). Separación entre **observaciones** ~10 s; **no es medida exacta de convergencia** (sondeo y operaciones de script).
- Captura solicitada **B3_07** a 17:42:48: API `topology=active`, WAN-P UP, ruta WAN-P, `fresh=true`; eventos `WAN_PRIMARY_DOWN`, `WAN_ROUTE_CHANGED`(a WAN-B), `WAN_PRIMARY_RESTORED`, `WAN_ROUTE_CHANGED`(a WAN-P); contadores `wan_down=1`, `wan_restored=1`, `route_changed=2`.

## 4. Limpieza de topología y exporter (17:44–17:45)

- `bash scripts/laboratorio/b2-dualwan-ospf.sh down` a 17:44:55: `RESULTADO_B2_LIMPIEZA=0`, `RESULTADO_DOWN_B3=0`, rutas/ens33 y GW host preservados.
- Exporter registró `TOPOLOGY_STOPPED` a **17:44:56.282**, con `topology=offline`, routers 0/0 y ruta `none` confirmado `/api/v1/live` a 17:44:59. `fresh=true` significa sondeo actual de topología apagada, NO significa routers activos.
- Archivo local auténtico `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl`, 855 bytes, 5 eventos observados; no versionado/binario descargado automáticamente.
- **POSTCHECK B3_09 AÚN NO CONCLUIDO:** consulta a 17:45:10 mostraba `PUERTO_9108_LIBRE: NO` porque el exporter HTTP seguía funcionando en primer plano y PowerShell túnel permanecía abierto. Contenedores Docker y namespaces vacíos, `ens33=192.168.47.40/24`, gateway `192.168.47.2`, servicios docker/ssh/open-vm-tools activos.
- La Terminal 3 (`ssh -N -L 9108:127.0.0.1:9108 netlab360`) reportó repetidamente `Connection refused` **tras ausencia/interrupción del listener de destino**; no implica falta de Docker/OSPF ni falla del WAN, ya retirada. Última salida Terminal 1 documenta HTTP hasta 17:45:55 pero no contiene `B3_LIVE_SERVIDOR_DETENIDO=SI`. No afirmar que el servidor sigue o está cerrado actualmente sin verificación.
- `git pull --ff-only` a `2c468d1`, `## main...origin/main`, pero `git status` mostró `?? servicios/observabilidad/__pycache__/` y `?? tests/__pycache__/`; `GIT_SINCRONIZADO: NO` por directorios Python no versionados, no por diferencias de commits. Nueva [`.gitignore`](https://github.com/recm0708/netlab360/blob/main/.gitignore) creada para ignorar esas rutas; **no ejecutada por usuario aún**. No `git reset --hard`; el usuario debe hacer `git pull --ff-only origin main` y comprobar limpieza.

## 5. Evaluación técnica y evidencias

**Logrado realmente:** telemetría viva consulta Docker/FIB en loopback, correlaciona eventos de falla/restauración con cambio efectivo de ruta, ofrece API y /metrics, NOC HTML atendió múltiples HTTP 200, archivo JSONL persistió cinco eventos, rollback de routers limpio. No se puede llamar alerta de Prometheus ni afirmar disponibilidad de Prometheus/Alertmanager; **NO hay scraper/TSDB ni regla de alarma configurada**.

**Capturas B3_05, B3_06, B3_07, B3_08 y B3_09:** se consideran tomadas según regla de usuario; solo existe evidencia textual de terminal y HTTP de la página. **PNG aún no recibidos visualmente ni subidos a GitHub**. B3_09 sería **DIAGNÓSTICA** por puerto todavía ocupado; sugerir **B3_09_Postcheck_Telemetria_Viva_Final.png** tras detener exporter/túnel, sin volver a levantar routers. La captura B3_08 debe inspeccionarse luego para confirmar si realmente incluye evento/estado en pantalla.

**Avance S01 técnico provisional:** elevar **45 → 48%** (+3 puntos en B3, ahora 5/15) al comprobar fuente live, evento WAN down, restauración y rutas observadas, sin acreditar Prometheus ni cierre de postcheck; el resto S01 abierto. Este porcentaje es estimación de control, no calificación oficial.

## 6. Instrucciones próximas, sin repetir ensayo WAN

1. Cerrar PowerShell 3 con Ctrl+C si sigue activo; detener `live_exporter.py` en Terminal SSH 1 Ctrl+C si sigue ejecutándose.
2. Terminal SSH 2: comprobar `ss -H -ltn '( sport = :9108 )'`, ambos contenedores y namespaces vacíos, IP/GW/servicios intactos. Capturar **B3_09_FINAL** solo como postcheck de lectura. No repetir `up/fail/restore/down`.
3. Git `pull --ff-only` de la nueva `.gitignore`, comprobar `GIT_SINCRONIZADO: SI` sin alterar código; `git status --short`.
4. Próxima etapa: preparar/deplegar **Prometheus real** con configuración/validación de scrape y reglas; planificar acceso seguro a exporter solo loopback. Después demostrar consulta `up`/series dentro de la TSDB, regla WAN Down y recuperación, manteniendo alcance y host seguro.

**Issues:** #1 fase, #12 incidente, #15 panel, #20 Prometheus, #21 métricas, #43 evidencias futuras; actualizar al resultado real. #12 **todavía abierta** porque no existe alertmanager/cadena Prometheus.
