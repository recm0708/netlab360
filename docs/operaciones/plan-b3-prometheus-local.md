# NETLAB360 B3 — Prometheus real local: plan de instalación controlada y validación

**Preparación versionada:** 13/10/2026. **Ejecución real en Ubuntu:** PENDIENTE de las salidas del usuario.  
**Origen:** diagnóstico y bitácora del [ciclo completo de telemetría WAN](../sesiones/2026-10-13-b3-live-ciclo-incidente-wan-verificado.md), en el que exporter B3 y eventos sí funcionaron, pero no había Prometheus.

## Propósito

Pasar de **exponer /metrics** a **recopilar en una TSDB real** y **evaluar reglas de alerta**. Se mantiene el controlador/host `ens33=192.168.47.40/24` y ruta `192.168.47.2` sin modificaciones y sin publicar servicios fuera de localhost.

### Elección de arquitectura y aislamiento

- Los dos routers FRR B2 se implementan en contenedores aislados `--network none` y se limpian tras cada prueba. No hay necesidad de alterarlos para la primera prueba de Prometheus.
- El exporter B3 actual se ejecuta como usuario normal escuchando `127.0.0.1:9108`; Prometheus necesita alcanzarlo. Un Prometheus en bridge Docker distinto **NO** podría acceder a este localhost del host de Ubuntu por `127.0.0.1` dentro del contenedor. **No cambiar el exporter a 0.0.0.0 ni abrir port-forward en VMware**.
- Por ello se propone extraer los binarios `prometheus` y `promtool` de una imagen Prometheus versionada usando un contenedor temporal **`docker create --network none` sin ejecución**, y lanzar **Prometheus como proceso de usuario en el propio Ubuntu**, limitado a `127.0.0.1:9090`. No configura systemd ni paquetes APT; no necesita `--network host` ni contenedores privilegiados.
- Imagen de origen **propuesta**: `quay.io/prometheus/prometheus:v3.7.0`. Su **disponibilidad real y digest concreto NO han sido verificados aún en esta VM**, así que el script de preparación comprobará el pull/inspect y reportará el SHA256 efectivo de los binarios. No continuar si descarga o comprobación falla.
- Las reglas de alerting Prometheus se evalúan en el servidor; **Alertmanager y sus notificaciones externas siguen PENDIENTES**, por diseño de iteración.

## Archivos versionados (todavía sin ejecutar)

- `servicios/observabilidad/prometheus/prometheus.yml`: scrape `127.0.0.1:9108/metrics` cada 2 s, timeout 1 s, evaluación de reglas cada 2 s.
- `servicios/observabilidad/prometheus/rules/wan-alerts.yml`: `NETLAB360WANPrimaryDown`, `NETLAB360ExporterUnavailable`, `NETLAB360WanBackupSelected`, con etiquetas de severidad y esperas 4 s o 10 s para evitar picos puntuales.
- `scripts/observabilidad/preparar-prometheus-local.sh`: verifica hostname/IP/GW y puerto 9090 libre, descarga imagen versionada si falta, crea contenedor temporal sin red, copia `/bin/prometheus` y `/bin/promtool` a `~/netlab360-bootstrap/prometheus/bin/`, documenta versión/hash y valida configuración con `promtool`.
- `scripts/observabilidad/ejecutar-prometheus-local.sh`: ejecuta Prometheus foreground sin root en `127.0.0.1:9090` con TSDB local `~/netlab360-bootstrap/prometheus/data/`, retención un día y mensajes de inicio. Detener con Ctrl+C.

## Protocolo próximo (primero cerrar etapa anterior)

1. En PowerShell 3 cerrar `ssh -N -L 9108:127.0.0.1:9108 netlab360` con Ctrl+C si sigue activo, y en Terminal SSH 1 cerrar `live_exporter.py --serve` con Ctrl+C si sigue. `ss -H -ltn '( sport = :9108 )'` debe estar vacío. `docker ps -a` y `ip netns list` vacíos. `ens33` y ruta original intactos.
2. `git pull --ff-only origin main` para obtener `.gitignore` que oculta `__pycache__/`, configuración y scripts nuevos; verificar Git limpio y `bash -n scripts/observabilidad/*.sh`; no borrar código ni repetir OSPF WAN.
3. `sudo -v` y ejecutar `bash scripts/observabilidad/preparar-prometheus-local.sh`; revisar `RESULTADO_PREPARACION_PROMETHEUS=0` y ambos mensajes de `promtool` OK. Si la imagen etiquetada no está disponible, registrar fallo y corregir fuente/version en GitHub; **no hacer modificaciones manuales del host sin revisar**.
4. En Terminal SSH 1, ejecutar `sudo -v`, `python3 servicios/observabilidad/live_exporter.py --check` (topology OFFLINE normal), luego `--serve`. El puerto 9108 debe atender /metrics aun con topología apagada.
5. En otra Terminal SSH 2 ejecutar `bash scripts/observabilidad/ejecutar-prometheus-local.sh`; deberá escuchar exclusivamente `127.0.0.1:9090`. Desde otra sesión, `curl -fsS 'http://127.0.0.1:9090/api/v1/query?query=up%7Bjob%3D%22netlab360-frr-live%22%7D'` debe mostrar una serie con valor 1, y consulta `netlab360_live_source_up` valor 1. Esto acredita **scrape real**. Sin routers, WAN primary `-1` no debe generar alerta DOWN.
6. Consultar `/api/v1/rules` y `/api/v1/alerts` para demostrar que la regla WAN quedó realmente cargada; todavía no habrá evento si WAN-P no se bajó. Se pedirá captura `B3_10_Prometheus_Scrape_Real.png`, sin pretender que contiene incidente no probado.
7. Para comprobar alertas de verdad, habrá un **nuevo laboratorio controlado** separado: desplegar B2 solo una vez, status Full, exporter activo, confirmar up=1/wan-p=1, ejecutar fail, verificar series Prometheus y alerta `NETLAB360WANPrimaryDown` estado `firing` tras la espera, restore y comprobar alerta `inactive` / ya no firing, down y rollback. **Esa prueba NO se ha ejecutado aún**. Capturas futuras B3_11/B3_12/13 para falla/recuperación/limpieza.
8. Detener Prometheus y exporter con Ctrl+C, comprobar puertos 9090/9108 libres, Docker/netns vacíos y red protegida, sincronizar GitHub. Guardar resultados de prueba y snapshots con timestamps y revisar PNG posteriormente.

**Precisión:** un endpoint `/metrics` accesible por curl **no** es un scrape, una regla configurada **no** es una alerta `firing`, y un evento JSONL de exporter **no** es un evento de Alertmanager. Registrar cada subhito por separado.

**Estado inicial de esta guía:** S01 48% estimado tras el ensayo live; ningún punto adicional por solo crear scripts/configuración de Prometheus.
