# NETLAB360 S05 · Mapa de terminales y recuperación del NOC

## Estado operativo recuperado — 11/11/2026 (supera el diagnóstico histórico siguiente)

**Recuperación completada:** NOC T1 ahora PID **449431** en `127.0.0.1:9130`, exporter S04 T4 PID **425166** en `127.0.0.1:9110`, túnel T2 funcional y acceso Windows a `/healthz` + grafo. Dos muestras separadas cuatro segundos, **S04 `source_ok=True`, `topology=active`, `errors=[]`, NOC `routing.available=True`, `source_warnings=[]`**, FIB `S1=s1p/10.78.0.2`, `S2=s2p/10.78.0.10`; precheck S1 `OK_SIN_CAMBIOS`; `ens33 192.168.47.40/24` intacto. El procedimiento de recuperación que figura abajo es **histórico o de contingencia**, no se debe ejecutar mientras las fuentes sigan sanas.

**Regla actual:** mantener abiertas T1 (NOC), T2 (túnel) y T4 (S04); T3 realiza git pull y comprobaciones sin reiniciar servidores. T5 registra failover; solo cuando T5 diga `S05_NOC_OBSERVADOR_LISTO=S1`, T6 (PowerShell tras `ssh rc-aa-ec@192.168.47.40`) ejecutará la conmutación S1 con `--hold-seconds 25` y supervisión de restauración. Para capturas 29/30 y lista exacta pendiente consultar [auditoría de cuatro PNG](../evidencias/10-auditoria-s05-png-y-capturas-pendientes-2026-11-11.md).

**Corte:** 11/11/2026. **VM:** `netlab360-lab` / `192.168.47.40/24`; gateway `192.168.47.2` por `ens33`. **Snapshot VMware:** `NETLAB360_S05_PreLAN_20261110` (manual; no tocar).

## Diagnóstico confirmado por el operador

- El auditor encontró `python3 servicios/topologia-s05/app.py --serve --port 9130` en el **PID 334882**, TTY `pts/2`, y puerto `127.0.0.1:9130` **ocupado correctamente**.
- El exporter S04 **no estaba ejecutándose**: no había proceso ni listener `127.0.0.1:9110`; el NOC señaló `Exporter S04 ... sin muestra confiable`, `telemetry.available=false`, `routing.available=false`.
- Se reinició el exporter S04 desde una terminal nueva, tras `sudo -v`; pasó a `source_ok=true` / `topology=active`. En la consulta siguiente el **NOC original** seguía dando `routing.available=false` con `routes={}`. Reiniciar **otro** NOC desde otra terminal produjo `[Errno 98] Address already in use`, porque el antiguo seguía en 9130.
- **Causa operativa más probable de FIB ausente:** el proceso NOC longevo ejecuta en cada consulta `sudo -n docker inspect nl360-s02-r-hq` y `sudo -n nsenter ... ip -j -4 route get`, mientras las credenciales `sudo` pueden caducar **por TTY**. Renovarlas en otra terminal no necesariamente actualiza la autorización de la terminal/proceso NOC. Confirmar con `source_warnings` y la recuperación antes de declarar la causa definitiva.
- La apertura de un túnel SSH devolvió `Connection reset` / `Connection refused` en Windows; ese túnel sólo permite acceso al NOC, **no controla ni repara** los servicios internos de la VM. El cierre accidental de terminales no desmontó WAN/LAN ni detuvo los tres contenedores de FRR.
- **No se ejecutó lote 73 / failover S1** tras la caída del observador en lote 72. Se verificó `ens33 UP 192.168.47.40/24` y gateway `.2`. El lote 70 pasó **36/36** tests y lote 71 pasó con fuente y FIB correctas antes de la interrupción.
- **El lote 72R-C falló después de `S04_FUENTE=True` y `NOC_FIB=False`**, antes de autorizar ninguna perturbación de enlace.

## Terminales fijas (no iniciar procesos duplicados)

| Terminal | Equipo / función | Proceso de larga duración | Se debe conservar abierta |
| --- | --- | --- | --- |
| **T1** | Ubuntu SSH: **NOC S05** | `python3 servicios/topologia-s05/app.py --serve --port 9130` | Sí |
| **T2** | Windows PowerShell: **túnel SSH local** | `ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -L 9130:127.0.0.1:9130 rc-aa-ec@192.168.47.40` | Sí |
| **T3** | Ubuntu SSH: **auditoría/control** | Ningún proceso permanente; ejecutar scripts de precheck, `git`, `ss`, API y postcheck | Se puede reutilizar |
| **T4** | Ubuntu SSH: **exporter S04** | `python3 servicios/observabilidad/s04_exporter_multisede.py --serve --port 9110 --interval 2` | Sí |
| **T5** | Ubuntu SSH: **observador temporal** | `python3 scripts/validacion/s05-observar-conmutacion-noc.py --watch --site S1 --seconds 120 --interval 0.5` | Sí durante la toma |
| **T6** | Ubuntu SSH: **simulador de conmutación temporal** | `python3 scripts/laboratorio/s02-failover-wan.py S1 --hold-seconds 25` **sólo después de prechecks sanos** | Sí hasta restauración |

**Reglas de operación:** iniciar primero T4 (exporter), luego T1 (NOC), validar API local con T3, por último abrir T2 y validar navegador. T5/T6 se abren después de línea base correcta. En T4 y T1, ejecutar `sudo -v` en **su propia terminal** justo antes de `--serve`. Si ya hay listener, **no ejecutar otro servidor en ese puerto**. Detener sólo el proceso propio mediante `Ctrl+C` desde su terminal, nunca usar `pkill`, `killall` ni alterar contenedores.

## Recuperación inmediata (sin cambios de red)

1. **T4** exporter S04 ya se inició y se observó `source_ok=True`; no duplicarlo ni detenerlo si sigue escuchando 9110.
2. **T1** es el proceso NOC de 9130 de larga duración. Con su terminal presente: pulsar `Ctrl+C`, confirmar `S05_TOPOLOGIA_DETENIDA=SI`, hacer `sudo -v` **en T1** y lanzar `python3 servicios/topologia-s05/app.py --serve --port 9130`. En caso de que T1 no sea recuperable, identificar proceso/PID exacto y coordinar un apagado acotado; nunca lanzar un duplicado. El proceso en sí es de solo lectura.
3. **T3**, tras recuperación: verificar `sudo ss -lntp '( sport = :9110 or sport = :9130 )'`; S04 `source_ok=true`, `topology=active`, `errors=[]`, muestra fresca; NOC `telemetry.available=true`, `routing.available=true`, FIB `S1.dev=s1p`, `S2.dev=s2p`, `source_warnings=[]`; `sudo -n` para Docker en **T1/T4** no sirve comprobarlo únicamente en T3.
4. **T2** restaurar SSH `-N -L` únicamente cuando 9130 responde en VM; comprobar URL con `Invoke-RestMethod http://127.0.0.1:9130/healthz`. Si PowerShell indica puerto local ocupado, cerrar el túnel anterior con `Ctrl+C` y no duplicarlo. La conexión puede permanecer abierta sin emitir salida.
5. Sólo con **dos muestras consecutivas sanas** y `--precheck --site S1` mostrando `S05_NOC_PRECHECK=OK_SIN_CAMBIOS`, lanzar T5 y, **después de** `S05_NOC_OBSERVADOR_LISTO=S1`, ejecutar T6 (simulador). No ejecutar T6 si el observador aborta, el exporter cae o no hay FIB verificada.
6. Si el observador falla, **no hay motivo para restaurar instantáneas ni reconstruir S02**, pues no se llegó a bajar la WAN.

## Límite operativo detectado

El mecanismo actual de NOC/S04 **no es apto para supervisión desatendida a largo plazo sin abordar la caducidad de `sudo -n`**. `/healthz` sólo prueba que el proceso HTTP responde, no valida privilegios ni fuente FIB. No resolver ejecutando el servidor web completo como root ni concediendo `NOPASSWD: ALL`, acceso al grupo Docker o comodines de `nsenter` en sudoers. Registrar como mejora de arquitectura una **recolección de observabilidad de mínimos privilegios**, con proceso/servicio aislado capaz de leer solo los datos necesarios. No introducir esta autorización privilegiada sin diseño y pruebas de seguridad.

## Hitos y entregables

- Capturas previas **S05_24–S05_28** recibidas/aceptadas; versión V7.2 aprobada en pantalla, pero confirmar **S05_29 / S05_30** como evidencias guardadas antes de dar cierre documental.
- **S05_31** sólo durante conmutación real con backup `s1b` seleccionado, con inspector y próxima salto `10.78.0.6`. Guardar JSONL de observador, log de failover y comprobación de recuperación FIB/gestión. No inferir tráfico medido.
- Mantener abiertas las issues **#64**, **#5** y milestone S05; pendiente NOC failover S1 y S2, HA, SDN y LACP integrado.

