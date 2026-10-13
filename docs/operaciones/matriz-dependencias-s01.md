# NETLAB360 — Matriz preventiva de dependencias por fase (S01)

**Actualización:** 13/10/2026, tras diagnóstico del exporter B3.  
**Regla:** auditar primero, instalar **solo dependencias faltantes y justificadas**. No instalar ciegamente todas las herramientas previstas para S02–S08: algunas se entregarán como contenedores con versiones y digest fijados, y otras no son necesarias en el host Ubuntu.

## Herramientas y disponibilidad esperada

| Uso | Requisito concreto | Origen/versionado | Estado contrastado |
|---|---|---|---|
| B0 y control | `bash`, `git`, `ssh`, `sudo` | Ubuntu | Git, SSH y sudo confirmados por operación anterior |
| B1 IPAM | `python3`, paquete Python `yaml` (PyYAML) | validador de `scripts/validacion` | `VALIDACIÓN B1: OK` en múltiples ensayos; auditar import |
| B2 redes | utilidades `ip`, `nsenter`, `ss`, `curl` | iproute2, util-linux, curl | Uso observado en laboratorio, curl existe: produjo error de conexión, no *command not found* |
| B2 contenedores | Docker Engine, CLI y FRRouting `quay.io/frrouting/frr:10.7.1` | Docker y imagen de contenedor pinned | Docker/FRR funcionan: `OSPF_DUAL_FULL: SI`, `RESULTADO_UP_B3=0` |
| B3 exporter live | Python biblioteca estándar `argparse`, `json`, `http.server`, `subprocess`; lectura `sudo -n docker inspect` y `nsenter` | `servicios/observabilidad/live_exporter.py` | Python sintaxis OK; error identificado como comparación case-sensitive de texto Docker, **NO falta de herramienta** |
| B3 dashboard | navegador Windows + túnel SSH `ssh -N -L` | Sin paquetes en host | Túnel redirige hacia servidor loopback; si no hay servicio en puerto, Windows reporta `Connection refused` |
| B3 Prometheus (próxima subfase) | imagen Docker Prometheus fijada + `prometheus.yml` y reglas | **por preparar/validar antes del despliegue** | **NO instalado/configurado ni demostrado**; no se confunde con endpoint /metrics |
| B3 Alertmanager (subfase siguiente) | imagen Docker, rutas de alertas y pruebas de envío | **por preparar/validar** | Pendiente, no requerida para corregir el exporter |
| IaC posterior | `tofu`, `ansible`, GitHub CLI `gh` | infraestructura/versiones del laboratorio | Instalados previamente; verificar de nuevo si se van a usar |
| Frontend posterior | `node`/`npm` solo si se elige ese stack | no obligatorio para API Python actual | Revisar al establecer requisitos, no instalar preventivamente sin diseño |

### Fallo real del 13/10/2026 16:40

1. El script `live_exporter.py` realizaba `docker inspect` cuando los routers de B2 todavía no estaban desplegados. Docker devolvió `error: no such object: nl360-b2-r-hq` en **minúsculas**.
2. La condición Python comprobaba solo `"No such object"` / `"No such container"` (mayúscula inicial). Clasificó erróneamente el estado normal **OFFLINE** como problema **DEGRADED**, preflight rc=4.
3. El exporter no abrió `127.0.0.1:9108`. Por ello curl mostró `Failed to connect` y el túnel Windows `connect failed: Connection refused`. Son **consecuencias**, no paquetes ausentes.
4. Luego el usuario ejecutó B2 `up --snapshot-confirmado`: **éxito real** `OSPF_DUAL_FULL: SI`, R-HQ/R-S1 Full/Full y rutas `wan-p`, `RESULTADO_UP_B3=0` a 16:40. Un segundo `up` recibió `ERROR: recursos previos B2` y rc=3: **guarda de seguridad correcta**, NO falta de instalación. Hasta la última salida recibida **no consta `down` ejecutado**, y la topología podría seguir activa. Verificar antes de continuar.
5. En Terminal 2 `sudo` rechazó un primer intento de contraseña y luego permitió continuar; es autenticación, no falta del paquete sudo.
6. **Solución versionada:** `inspect_router` normaliza `stderr/stdout` con `.lower()` antes de detectar `no such object` o `no such container`; conserva cualquier error verdadero (permisos/daemon inaccesible) como DEGRADED. Se agregó `tests/test_b3_live_exporter.py` con regresión offline en variantes mayúscula/minúscula y error real de permisos, sin necesitar Docker, y `scripts/validacion/auditar-dependencias-netlab360.sh` (solo lectura).

### Antes de cada cambio de fase

- Ejecutar `sudo -v` en la **misma terminal** cuando una herramienta usa `sudo -n`.
- `bash -n scripts/validacion/auditar-dependencias-netlab360.sh`, luego `bash scripts/validacion/auditar-dependencias-netlab360.sh` y revisar `RESULTADO_AUDITORIA_DEPENDENCIAS=0`.
- `python3 -m unittest discover -s tests -p 'test_b3_live_exporter.py' -v` y `ast.parse` antes de probar el exporter.
- Antes de `up`, comprobar `sudo docker ps -a --filter name=nl360-b2-` y marcador de propietario `~/netlab360-bootstrap/estado-b2-dualwan/.nl360-owner`. **Nunca ejecutar up dos veces** sobre redes ya desplegadas.
- Para monitorear `--serve`, verificar `--check=0` y puerto libre. Un `curl` fallido **no justifica instalar curl**, pues el ejecutable sí se invocó; primero mirar si el proceso escucha con `ss`.
- No tocar `ens33=192.168.47.40/24`, default `192.168.47.2`, VMnet8, NetworkManager ni rutas de administración.

**Estado final acreditado por logs:** fallo B3 live detectado y corrección publicada en GitHub. **NO afirmar corrección verificada en VM hasta que el usuario ejecute el nuevo código y aporte `RESULTADO_B3_LIVE_CHECK=0`.** El porcentaje S01 permanece **45% técnico estimado**.
