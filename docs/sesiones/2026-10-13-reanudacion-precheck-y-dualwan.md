# NETLAB360 — Reanudación matutina, mantenimiento y sincronización

**Ejecución observada:** 13/10/2026 10:47 (Panamá, UTC−05:00).  
**Ventana solicitada:** terminar pruebas antes de las 12:00 y dejar GitHub sincronizado, Ubuntu y Windows apagados a más tardar 12:15. **El apagado no se ha ejecutado todavía.**

## Resultados comprobados

- Desde Windows, `ssh netlab360` funcionó con llave Ed25519 y su passphrase local. Bienvenida Ubuntu 26.04.1 LTS, kernel `7.0.0-38-generic`.
- `date -Is`: 2026-10-13T10:47:03-05:00; `uptime`: 3 minutos tras encender VM; host `netlab360-lab`.
- Red inalterada: `ens33 UP 192.168.47.40/24`, default `192.168.47.2` (metric 100). `systemctl is-active docker ssh open-vm-tools`: tres `active`.
- `sudo docker ps -a` sin contenedores, `sudo ip netns list` sin namespaces residuales.
- Mantenimiento preventivo 10:47:12: `sudo apt update` OK, `apt list --upgradable` vacío, `sudo apt-get -s upgrade` = `0 actualizados, 0 nuevos, 0 para eliminar`, `sudo dpkg --audit` sin incidencias, `/run/reboot-required` ausente. Mensaje opcional de 4 actualizaciones ESM Apps, no bloqueo de APT ordinario.
- Sincronización `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`: fast-forward `c519a02..e9460ee`, incorporó `docs/arquitectura/04-b2-dualwan-plan-ejecucion-segura.md`. Git `## main...origin/main` limpio, último commit visto `e9460ee | 2026-10-13 10:46:41 -0500`. **Esto fue antes de nuevos commits remotos para el orquestador**, por lo que se necesita otro `git pull`.
- Se conserva resultado FRR v5 de anoche: `FRR_DAEMONS_ACTIVOS: SI`, `OSPF_CONTROL_PLANE: OK`, `RESULTADO_SMOKE_FRR_V5=0`; no es necesario repetirlo. Aún no se ha ejecutado ninguna topología HQ-S1 real.

## Nuevo script preparado y riesgos

**Artefacto versionado pero NO EJECUTADO:** `scripts/laboratorio/b2-dualwan-ospf.sh`. Comandos `precheck`, `up --snapshot-confirmado`, `status`, `fail`, `restore`, `down`. Respeta `--network none` y nombres exclusivos `nl360-b2-`, dos pares veth dentro de los namespaces de contenedores, WAN-P y WAN-B con costos OSPF 10/100, LANs dummy de HQ/S1, logs y cleanup de recursos propios.

- Antes de `up`, usuario debe ejecutar `git pull --ff-only`, `bash -n scripts/laboratorio/b2-dualwan-ospf.sh` y `bash ... precheck`; **ni sintaxis ni funcionamiento del nuevo script han sido validados por la VM todavía**.
- Por seguridad se introdujo marcador `.nl360-owner` requerido para `status/fail/restore/down`, y guard de IP y gateway. Ante fallo de `up`, hay trampa para diagnóstico y rollback específico. **No usar `--privileged`, ni `--network host`**. La capability `CAP_SYS_ADMIN` es amplia y solo se concede en contenedores efímeros de la VM de laboratorio porque se observó necesaria para FRR 10.7.1.
- Precheck no construye topología ni altera redes. El `up` quedará sujeto a revisar la salida del precheck y a margen suficiente antes del cierre horario.
- **No declarar** enlaces WAN, adyacencias OSPF ni failover comprobados hasta recibir salida real. Issue #42 sigue ABIERTA.

## Instrucciones de captura y cierre

El usuario considera **todas las capturas solicitadas tomadas**, salvo aviso contrario; todavía pendientes de auditoría visual #43. Para cualquier evidencia nueva, indicar desde `INICIO CAPTURA` hasta `FIN CAPTURA`, nombre PNG, datos a mostrar y comandos que no requieren `clear`.

A las **12:00 Panamá** no iniciar nuevas pruebas: salvar evidencias, actualizar issues y continuidad, sincronizar remoto/local verificando hashes, comprobar ausencia de contenedores/netns y red de gestión intacta. Entre 12:10 y 12:15 `sync; sudo systemctl poweroff`, confirmar VMware Powered Off y luego apagar Windows. Esta nota **no es confirmación de apagado**.

**Ancla:** [docs/00-estado-y-continuidad.md](../00-estado-y-continuidad.md). **Seguimiento:** issues #1, #42 y #12.
