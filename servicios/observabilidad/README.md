# NETLAB360 B3 — Exporter vivo FRRouting + dashboard de eventos (iteración 2)

**Estado:** nuevo código `servicios/observabilidad/live_exporter.py` ya versionado en GitHub, **PENDIENTE de sintaxis y ejecución en el Ubuntu del usuario**. No atribuir disponibilidad real hasta recibir resultados del usuario.

## Propósito y arquitectura

- Python estándar; API y pantalla dinámica **solo en loopback `127.0.0.1:9108`**, no necesita Dockerfile ni publicar VMnet8/ens33.
- **Solo inspección:** consulta `sudo -n docker inspect` para R-HQ/R-S1, y `sudo -n nsenter -t <pid> -n ip -j link show dev wan-p` + `ip route get` para obtener estado administrador de WAN-P y selección actual de WAN-P/WAN-B.
- `--check`: valida host/admin/sudo/Docker y muestra `B3_TOPOLOGIA=OFFLINE` con laboratorio apagado, sin levantar routers ni servidor. `sudo -v` debe ejecutarse en la **misma terminal** y `--check` usa solo lectura.
- `--serve`: sondeo discreto por defecto 1.0 s; exporta `/healthz`, `/api/v1/live`, `/api/v1/events`, `/metrics` en formato de exposición Prometheus, `/` UI autorrefrescable (2 segundos), POST rechazado y 404 para rutas inesperadas.
- **Eventos observables en logs JSONL** `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl`: `TOPOLOGY_STARTED`, `WAN_PRIMARY_DOWN`, `WAN_ROUTE_CHANGED`, `WAN_PRIMARY_RESTORED`, `TOPOLOGY_STOPPED`. Los eventos se derivan de diferencias reales entre sondeos. El exporter no genera fallas ni restaura interfaces: esto corresponde SOLO al orquestador ya probado `scripts/laboratorio/b2-dualwan-ospf.sh`.
- **NUEVO PERO NO COMPLETO:** la métrica `netlab360_live_...` indica estado actual cuando el recurso está desplegado; no equivale todavía a Prometheus *scrape* ni reglas de `Alertmanager` ni persistencia de TSDB. Un evento visto después de 1 segundo no establece tiempo de convergencia exacto; error del exporter (`source_up=0`) no debe confundirse con WAN down.
- **Guardias:** exige hostname `netlab360-lab`, IP de host `ens33 192.168.47.40/24`, default `192.168.47.2`, `sudo -n -v` y no aplica comandos que cambien red; no guarda contraseñas ni llaves, no instala paquetes.

## Flujo de validación seguro y evidencias

**Terminal SSH 1 — servicio monitor**:
```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
python3 - <<'PY'
import ast
from pathlib import Path
ast.parse(Path("servicios/observabilidad/live_exporter.py").read_text(encoding="utf-8"))
print("B3_EXPORTER_SINTAXIS=OK")
PY
sudo -v
python3 servicios/observabilidad/live_exporter.py --check
echo "RESULTADO_PREFLIGHT_B3=$?"
ss -H -ltn '( sport = :9108 )'
python3 servicios/observabilidad/live_exporter.py --serve
```
Si `--check` falla, no ejecutar `--serve`; compartir diagnóstico. **Terminal 1 permanecerá abierta**.

**Terminal SSH 2 — orquestación B2 (no tocar Terminal 1):**
```bash
cd ~/proyectos/netlab360
sudo -v
bash scripts/laboratorio/b2-dualwan-ospf.sh precheck
bash scripts/laboratorio/b2-dualwan-ospf.sh up --snapshot-confirmado
# Solo si up=0 y dos vecinos Full: consultar live y capturar B3_05 (normal)
curl -fsS http://127.0.0.1:9108/api/v1/live | python3 -m json.tool
curl -fsS http://127.0.0.1:9108/metrics | grep '^netlab360_live_'
# Solo si WAN-P=UP y FIB=wan-p: fail controlado, observación B3_06
bash scripts/laboratorio/b2-dualwan-ospf.sh fail
curl -fsS http://127.0.0.1:9108/api/v1/live | python3 -m json.tool
curl -fsS http://127.0.0.1:9108/api/v1/events | python3 -m json.tool
# Restaurar WAN-P aunque fail haya fallado, si los contenedores están corriendo y el estado B2 es válido
bash scripts/laboratorio/b2-dualwan-ospf.sh restore
curl -fsS http://127.0.0.1:9108/api/v1/events | python3 -m json.tool
# SIEMPRE tras uso de up exitoso: down y postcheck
bash scripts/laboratorio/b2-dualwan-ospf.sh down
```
**ADVERTENCIA:** no ejecutar `fail/restore` si `up` no dio 0 o las adyacencias no están Full; no borrar recursos B2 ajenos. Ante error conservar log y proceder a limpieza autorizada antes de apagar. Durante subidas y bajadas el exporter sigue sondeando; no confundir sus errores con fallas del ruteo.

**Terminal PowerShell 3 — túnel opcional, solo si quieren captura visual:**
```powershell
ssh -N -L 9108:127.0.0.1:9108 netlab360
```
Desde navegador Windows abrir `http://127.0.0.1:9108/`, observar ONLINE/alerta WAN-P/retorno y tomar capturas. Cerrar túnel con `Ctrl+C`; detener exporter con `Ctrl+C` en Terminal 1, observar `B3_LIVE_SERVIDOR_DETENIDO=SI`, puerto `9108` libre, cero Docker/netns y ens33/GW intactos.

**Evidencias propuestas:** 
- `B3_05_Exporter_Live_Ruta_Principal.png` con localhost API/metrics y FIB `wan-p`.
- `B3_06_Alerta_WAN_Principal_Down.png` con `WAN_PRIMARY_DOWN`, WAN-P admin down y ruta `wan-b`.
- `B3_07_Restauracion_y_Eventos_Live.png` con `WAN_PRIMARY_RESTORED`, FIB `wan-p`, JSON de eventos.
- `B3_08_Dashboard_NOC_En_Vivo.png` navegador, banner `EN VIVO`, tarjetas actuales/tabla de eventos (pueden necesitar más de un estado).
- `B3_09_Postcheck_Telemetria_Viva.png` puerto `9108` libre, contenedores/netns vacíos, host intacto.
**Todas se presumen tomadas** salvo aviso del usuario; validación visual y commit físico posteriores, issue #43.

## Pendientes tras este subhito

1. Validar runtime real de script con salidas aportadas; documentar la cadencia y falsos positivos de eventos.
2. Agregar Prometheus real con `scrape_config` al exporter del puerto local y demostrar métricas vigentes dentro de Prometheus, no solo `/metrics` HTTP; seleccionar red/namespace seguro que alcance localhost del invitado sin comprometer VMnet8.
3. Implementar reglas y alertmanager o equivalente más evaluación evento WAN real DOWN/UP con severity/timestamp en NOC y histórico.
4. Resto S01: hosts LAN finales, VLAN/ACL/LACP, IaC OpenTofu/Ansible, anomalías, informes y OVA. **S01 permanece 45%** hasta nueva validación funcional.
