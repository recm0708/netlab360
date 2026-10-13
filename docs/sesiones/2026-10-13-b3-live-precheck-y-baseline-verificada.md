# NETLAB360 B3 — exporter vivo validado antes de prueba de incidencia WAN

**Fecha de ejecución reportada:** 2026-10-13, 17:29–17:31 hora Panamá (UTC−05).  
**Fuente:** salida real del usuario de las Terminales 1 y 2.  
**Estado comprobado:** exporter vivo **funcionando** en localhost, topología FRR activa y WAN primaria seleccionada. **No se ejecutó todavía fail/restore en esta evidencia**.

## Hitos comprobados

- Reutilización de los recursos existentes: `sudo docker ps -a --filter name=nl360-b2-` confirmó ambos contenedores `nl360-b2-r-hq`, `nl360-b2-r-s1` ejecutándose desde 49 minutos antes; el marcador original `~/netlab360-bootstrap/estado-b2-dualwan/.nl360-owner` contiene `netlab360-b2-dualwan`. **No se repitió `up`**.
- `git pull --ff-only origin main` trajo el fix y scripts a `c4f3d47`, `B3_EXPORTER_SINTAXIS: OK`, `bash -n` del script de auditoría OK, árbol Git limpio **antes de nuevos commits remotos**.
- Pruebas Python: **5/5 OK**, `RESULTADO_TESTS_B3=0`: ausencia de contenedor (minúscula/mayúscula), error verdadero de permisos, contenedor iniciado y detenido.
- Auditoría `scripts/validacion/auditar-dependencias-netlab360.sh`: todos los 13 ejecutables requeridos disponibles; Python incl. PyYAML, Docker 29.9.0, imagen FRR 10.7.1, Compose 5.6.0, servicios docker/ssh/open-vm-tools activos, `ens33=192.168.47.40/24`, GW `192.168.47.2`; OpenTofu, Ansible, gh, node, npm disponibles. `DEPENDENCIAS_REQUERIDAS_FALTANTES=0`, `DEPENDENCIAS_PLANIFICADAS_POR_VERIFICAR=0`, `RESULTADO_AUDITORIA_DEPENDENCIAS=0`.
- En **Terminal SSH 1**, `python3 servicios/observabilidad/live_exporter.py --check` dio `B3_LIVE_PREFLIGHT=OK`, `B3_TOPOLOGIA=ACTIVE`, `RESULTADO_B3_LIVE_CHECK=0`.
- El exporter **continúa intencionalmente en primer plano** en Terminal 1 desde aproximadamente 17:31:25: `B3_LIVE_LOCAL=http://127.0.0.1:9108/`, `B3_LIVE_MODO=EN_VIVO_SONDEO | NO_PROMETHEUS | CTRL_C_DETIENE`; proceso espera solicitudes hasta Ctrl+C. **No es bloqueo ni error**.
- En Terminal 2 `GET /healthz` -> HTTP 200, `status=ok`, `source=live`, `live_monitoring=true`, `topology=active`, `fresh=true`, `age_seconds=0.76`.
- `GET /api/v1/live` -> routers hq=1 y s1=1, `wan_primary_admin_up=1`, `selected_link=wan-p`, destino `10.71.10.1`, source_ok=1, `fresh=true`.
- `GET /metrics` -> `netlab360_live_source_up 1`, dos routers operativos, WAN primaria UP, `wan-p=1`, `wan-b=0`, epoch de último sondeo y contadores de eventos `down=0, restored=0, route_changed=0` (sin fallo inducido todavía).
- **No se ha instalado/configurado Prometheus scrape o Alertmanager.** Estas métricas son **actuales del exporter**, no evidencia de recopilación por Prometheus.

## Próxima prueba operacional (pendiente hasta salida real)

1. Conservar Terminal SSH 1 con exporter en foreground; no cerrar. En Terminal SSH 2, `sudo -v`; verificar `GET /healthz` fresh, `GET /api/v1/live` WAN-P UP/ruta wan-p, `b2-dualwan-ospf.sh status` con dos vecinos Full.
2. Captura `B3_05_Exporter_Live_Ruta_Principal.png`: marcadores de inicio/fin, API y métricas.
3. Opcional navegador Windows por túnel `ssh -N -L 9108:127.0.0.1:9108 netlab360`, solo con servicio ya escuchando, página dinámica en localhost. Capturar B3_08 durante falla antes de restaurar.
4. Una sola acción `bash scripts/laboratorio/b2-dualwan-ospf.sh fail`, exigir `CONMUTACION_WAN_B: OK`, esperar 3–5s; `/api/v1/live` debe mostrar `wan_primary_admin_up=0` y ruta `wan-b`, `/api/v1/events` con `WAN_PRIMARY_DOWN` y `WAN_ROUTE_CHANGED`. Captura B3_06 de los resultados reales; **si no aparece evento, documentar diagnóstico, no inventar éxito**.
5. **Restaurar siempre** con `b2-dualwan-ospf.sh restore` mientras ambos routers están activos; esperar `RESTAURACION_WAN_P: OK`, `wan_primary_admin_up=1` y ruta `wan-p`, eventos `WAN_PRIMARY_RESTORED` y `WAN_ROUTE_CHANGED`. Captura B3_07.
6. `bash scripts/laboratorio/b2-dualwan-ospf.sh down` sobre propietario válido, limpiar topología; verificar exporter ve OFFLINE. Cerrar PowerShell túnel y Terminal SSH 1 con Ctrl+C, comprobar `B3_LIVE_SERVIDOR_DETENIDO=SI`, puerto 9108 libre, Docker/netns vacíos, administración intacta. Captura B3_09. **No apagar VM con routers activos**.
7. Guardar eventos reales de `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl` sin publicar secretos, e inspeccionar los PNG después; no aumentar el avance S01 **45%** hasta comprobar incidencia y rollback.

**Issues relevantes:** [#1 S01](https://github.com/recm0708/netlab360/issues/1), [#12 incidente](https://github.com/recm0708/netlab360/issues/12), [#15 dashboard](https://github.com/recm0708/netlab360/issues/15), [#20 Prometheus](https://github.com/recm0708/netlab360/issues/20), [#21 métricas](https://github.com/recm0708/netlab360/issues/21). No cerrar prematuramente.
