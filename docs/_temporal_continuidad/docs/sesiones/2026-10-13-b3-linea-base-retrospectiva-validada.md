# NETLAB360 — B3: línea base retrospectiva y primer módulo NOC preparado

**Fecha de reanudación:** 2026-10-13, 15:27–15:29 Panamá (UTC−05).  
**Estado:** B3-01 **generación de datos validada en Ubuntu**; API/panel local **versionados pero NO ejecutados ni comprobados en la VM**.  
**Seguimiento:** [#15](https://github.com/recm0708/netlab360/issues/15), [#20](https://github.com/recm0708/netlab360/issues/20), [#21](https://github.com/recm0708/netlab360/issues/21), [#12](https://github.com/recm0708/netlab360/issues/12), [#43](https://github.com/recm0708/netlab360/issues/43), S01 [#1](https://github.com/recm0708/netlab360/issues/1).

## 1. Reinicio, mantenimiento y protección

El usuario encendió la VM y accedió mediante PowerShell `ssh netlab360`. A las 15:27:45:
- Ubuntu 26.04.1 LTS, kernel `7.0.0-38-generic`, hostname `netlab360-lab`.
- `ens33 UP 192.168.47.40/24`, default `192.168.47.2 dev ens33`. **No se alteró red administrativa ni VMware VMnet8**.
- `systemctl is-active docker ssh open-vm-tools`: `active` tres veces.
- `sudo docker ps -a`: vacío; `sudo ip netns list`: vacío.
- Raíz `/dev/sda2` 157G, 14G usados, 136G libres, uso 9%. Memoria 15Gi, ~13Gi disponibles.
- `sudo apt-get update` OK; `apt list --upgradable` sin paquetes, simulación `apt-get -s upgrade` = 0 actualizados/nuevos/eliminados, `dpkg --audit` limpio, `apt-get -s autoremove` = 0 modificaciones. `sudo apt-get upgrade -y` = 0, `autoclean` OK, `REINICIO_REQUERIDO: NO`. Mensaje informativo 4 actualizaciones ESM Apps opcionales no modificó APT ordinario.
- `git pull --ff-only origin main`: ya actualizado, `git status` limpio y `GIT_SINCRONIZADO: SI` en commit `c53f0a6` **antes de nuevos commits remotos posteriores**.

## 2. B3-01: datos históricos recuperados y transformados (COMPLETADO)

La prueba base B2-L3 corresponde a `~/netlab360-bootstrap/evidencias/17-b2-convergencia-20261013-115141.csv` y `.log`. Ambos archivos estaban presentes (5,3 KiB CSV; 11 KiB log). CSV con **76 filas, 76 ICMP exitosos, 0 perdidos, secuencia 1–76 íntegra (`CSV_INTEGRIDAD: OK`)**; modo solo datos históricos, no monitor en vivo.

A las 15:28 el usuario generó correctamente:
- `~/netlab360-bootstrap/evidencias/b3-linea-base/b3-resumen-convergencia.json` (~1,3 KiB) con esquema `tipo=analisis_retrospectivo`.
- `~/netlab360-bootstrap/evidencias/b3-linea-base/b3-metricas-retrospectivas.prom` (~653 bytes), texto en formato de exposición Prometheus con nombres `netlab360_icmp_samples` y `netlab360_icmp_losses` por fase.

Resultado `B3_ANALISIS_RETROSPECTIVO=OK`. `python3 -m json.tool` validó sintaxis JSON y `cat` confirmó exposición de métricas. Distribución exacta:

| Fase | Muestras | Fallas ICMP | Rutas FIB | RTT medio |
|---|---:|---:|---|---:|
| normal | 14 | 0 | wan-p:14 | 0.0311 ms |
| cambio_respaldo | 1 | 0 | wan-b:1 | 0.0280 ms |
| respaldo | 16 | 0 | wan-b:16 | 0.0307 ms |
| cambio_principal | 29 | 0 | wan-b:27; wan-p:2 | 0.0288 ms |
| restaurada | 16 | 0 | wan-p:16 | 0.0286 ms |
| **Total** | **76** | **0** | **Muestreo discreto** | — |

**Evidencia `B3_01_Linea_Base_Observabilidad_ICMP.png`:** marcadores `INICIO CAPTURA B3_01` / `FIN CAPTURA B3_01`, fecha de consulta 15:28:32; presumida tomada conforme al usuario, todavía pendiente de revisión visual #43. Captura refleja resultados históricos a partir del CSV de las 11:51, no estado actual de routers.

## 3. Revisión de estructura del repositorio

El usuario ejecutó `find` y confirmó que a 15:28 **NO existían** en Git archivos `Dockerfile`, `compose.yml/yaml`, `package.json`, `pyproject.toml`, `prometheus.yml` ni `requirements.txt`. Estructura del repo previa: `docs/`, `scripts/`, `inventario/`, `topologias/`, `backlog/` y flujos GitHub; las referencias a Prometheus/exporters/dashboard en documentos eran **planes**, no aplicaciones desplegadas.

## 4. Nuevo módulo B3 preparado en GitHub (NO EJECUTADO)

Se creó `servicios/noc-historico/app.py`, servicio Python con biblioteca estándar, sin instalar dependencias y sin tocar Docker/ens33:
- `--check` valida ambos archivos B3 JSON/.prom, el tipo retrospectivo, las cinco fases, conteos y coherencia global.
- `--serve` abre `127.0.0.1:8765` (solo loopback), interfaz HTML informativa `/` (NOC **HISTÓRICO / NO EN VIVO**), `GET /healthz`, `GET /api/v1/baseline`, `GET /metrics` (gauge histórico en texto Prometheus), sin escritura HTTP.
- Vista desde Windows únicamente mediante `ssh -N -L 8765:127.0.0.1:8765 netlab360` en otra terminal o browser de Ubuntu sobre localhost; NO abrir puertos en Windows ni publicar servicio a Internet.
- Portátil y seguro en la VM de laboratorio: usa archivos locales y cabeceras básicas CSP/no-store; no interpreta datos históricos como telemetría en vivo, no tiene alarmas ni scraper.
- **FALTAN pruebas reales:** `python3 -m py_compile` o `ast.parse`, `--check`, arranque localhost, `curl` a cuatro rutas, inspección visual, detención Ctrl+C y postcheck. Registrar sólo cuando el usuario aporte las salidas. **No aumentar S01 43%** por código escrito que aún no se ejecutó.

## 5. Próximas actividades

1. `git pull --ff-only origin main` para traer nuevo `servicios/noc-historico/app.py`; sintaxis, `--check` y estado Git.
2. En una terminal SSH iniciar `python3 servicios/noc-historico/app.py --serve` y conservar ejecución foreground; segunda terminal consultar con `curl --fail-with-body` `127.0.0.1:8765` y comprobar resultados.
3. Revisar vista HTML mediante túnel SSH desde Windows, tomar captura de **pantalla histórica** claramente marcada, registrar evidencia B3_02/B3_03; detener con Ctrl+C, validar puerto liberado, docker/netns vacíos y red protegida.
4. Diseñar siguiente iteración de **telemetría dinámica** (exporter/Prometheus) y un evento WAN con timestamp, sin presentar métricas retrospectivas como incidentes actuales.
5. Actualizar issues y checkpoint tras resultados comprobados; documentos de informe/bitácora/manual siguen pendientes.

**Importante:** el estado de GitHub después de crear el módulo no equivale al checkout de Ubuntu sincronizado en `c53f0a6` antes de esos commits. No publicar CSV o PNG sin revisión del usuario; el dato sensible de red administrativa no se debe incorporar a una OVA pública.
