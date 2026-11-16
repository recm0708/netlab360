# NETLAB360 — Prometheus 3.7.0 y scrape real confirmado; reglas aún sin cargar

**Corte:** 2026-10-13 18:12:46 Panamá (-05), salida real de tres terminales recibida.  
**Resultado:** binarios Prometheus y promtool, TSDB y recolección **verificados**. El endpoint de reglas respondió `{"groups":[]}`: **alertas no cargadas**. Antes de otra falla WAN se corrigió el script lanzador en GitHub, pero **NO se ha reejecutado todavía** ese arreglo.

## Resultados realmente observados

1. **Postcheck B3 anterior completado** a 18:08:52: `PUERTO_9108_LIBRE: SI`, `sudo docker ps -a` sin contenedores, `sudo ip netns list` vacío, `ens33 UP 192.168.47.40/24` y default `192.168.47.2` intactos, servicios docker/ssh/open-vm-tools activos. Captura `B3_09_Postcheck_Telemetria_Viva_Final.png` considerada tomada por convención; PNG no recibido todavía.
2. `git pull --ff-only` hasta `a1390bb`, `.gitignore` ignoró correctamente `servicios/observabilidad/__pycache__/` y `tests/__pycache__/`, `GIT_SINCRONIZADO: SI`, sin cambios rastreados.
3. `bash -n` de preparación/lanzamiento OK y PyYAML: `prometheus.yml YAML_VALIDO: True`, `wan-alerts.yml YAML_VALIDO: True`.
4. Script `scripts/observabilidad/preparar-prometheus-local.sh` descargó exitosamente `quay.io/prometheus/prometheus:v3.7.0`, digest real `sha256:29c1e0b48ad816750245dea3d65ac3ce57dda30547e67b1e9a5176e2953cc4dc` linux/amd64; extrajo `prometheus` y `promtool` a `~/netlab360-bootstrap/prometheus/bin/`. Versiones reales 3.7.0.
   - SHA256 binario prometheus: `729b11ab36b7bc33846f6316fa9272835ab43e803eedd56f7431801ebb771e93`.
   - SHA256 promtool: `eec9ef4f0a0669f3c7cd1740d25e6faf13705c44f3cb874cecc50fbea2801370`.
   - `promtool check config`: SUCCESS. `promtool check rules`: SUCCESS, 3 rules found. `PROMETHEUS_BINARIOS: OK`, `PROMETHEUS_CONFIGURACION: OK`, `RESULTADO_PREPARACION_B3=0`. Contenedores Docker vacíos y red administrativa intacta.
5. En **Terminal 1** se volvió a iniciar exporter Python localhost `127.0.0.1:9108`, `B3_LIVE_PREFLIGHT=OK`, `B3_TOPOLOGIA=OFFLINE` (correcto: routers B2 ya retirados). Logs `GET /metrics` cada 2 segundos HTTP **200**.
6. En **Terminal 2** se inició `bash scripts/observabilidad/ejecutar-prometheus-local.sh`, Prometheus real 3.7.0 escuchando `127.0.0.1:9090`, TSDB operativa, `Server is ready to receive web requests`, rule manager iniciado.
7. En **Terminal 3**, Prometheus `/-/healthy` → `Prometheus Server is Healthy.`; consulta **a Prometheus**, no al exporter, `up{job="netlab360-frr-live"}` → **1** e `netlab360_live_source_up` → **1**. La consulta `GET /api/v1/rules` devolvió **`{"groups":[]}`**, por tanto **sin reglas cargadas**. Esto impide acreditar alertas.
8. Captura `B3_10_Prometheus_Scrape_Real.png` a **18:12:46**, delimitada INICIO/FIN, `TARGET: netlab360-frr-live`, `UP: 1` y `LIVE_SOURCE_UP: 1`. Se asume tomada por regla de usuario; imagen no recibida/inspeccionada todavía.

## Diagnóstico y corrección preventiva versionada

El `prometheus.yml` apuntaba al glob relativo `servicios/observabilidad/prometheus/rules/*.yml`; el proceso reconoció sintaxis de config pero la API no halló grupos. Es compatible con que Prometheus evalúe el patrón relativo a un directorio distinto al esperado (hipótesis que deberá comprobarse con el nuevo script). El **lanzador** se modificó para construir `~/netlab360-bootstrap/prometheus/prometheus-runtime.yml` con el **glob absoluto** desde la ruta Git actual y comprobar `promtool check config`, `promtool check rules` y nombres requeridos antes de iniciar. El YAML en Git no se sobrescribe.

**Fix en GitHub, sin validar todavía en el equipo:** `scripts/observabilidad/ejecutar-prometheus-local.sh`. Es indispensable detener SOLO Prometheus con Ctrl+C en Terminal 2 (dejar exporter Terminal 1 operando), `git pull --ff-only`, `bash -n` del lanzador y ejecutarlo de nuevo. Consultar `/api/v1/rules` y exigir 3 reglas cargadas antes de desplegar FRR/OSPF y provocar failover. Si sigue vacío, parar y diagnosticar; no repetir B2.

## Criterio de control

- **S01 físico técnico: 48% → 50% estimado** al acreditar binarios versionados/validados, TSDB real y scrape de fuente viva comprobado por PromQL; B3 ahora 7/15 puntos. No acreditar todavía regla activa, evento `firing` ni Alertmanager. No cerrar #1/#12/#15/#20.
- **Estado de terminales al último dato real:** Terminal 1 exporter en ejecución foreground, Terminal 2 Prometheus en ejecución foreground, Terminal 3 libre. Contenedores y namespaces vacíos; IP/GW intactos. No afirmar nuevas pruebas después del corte sin salida.
- **Próxima etapa:** ajustar y demostrar carga real de las 3 reglas; entonces una sola prueba FRR real de WAN DOWN→WAN-B→WAN-UP con alerta Prometheus `pending`/`firing` y resolución; limpiar mediante `down` sin afectar VMnet8, detener ambos procesos, revisar Git y evidencias.

**Restricción académica:** semana 9, S01 aún sin cierre; priorizar entregables mínimos, evaluación de alcance con profesor y evitar revalidaciones duplicadas sin aporte. No cambiar pesos ni declarar calificación oficial.
