# NETLAB360 B3 — Diagnóstico y corrección del falso DEGRADED (13/10/2026, 16:40 Panamá)

**Fuente:** salida de terminales 1, 2 y 3 aportada por el usuario. No se observaron fallas por ejecutables `command not found` o módulos Python ausentes.

- `git pull --ff-only` llevó `main` a `9defd03`, `ast.parse` de `servicios/observabilidad/live_exporter.py`: `B3_EXPORTER_SINTAXIS: OK`.
- Antes de B2 `up`, Docker inspect devolvió texto `error: no such object: nl360-b2-r-hq` (minúscula). Exporter viejo lo elevó equivocadamente a `B3_LIVE_PREFLIGHT=ERROR`, `B3_TOPOLOGIA=DEGRADED`, `RESULTADO_PREFLIGHT_B3=4`.
- A continuación el usuario intentó `--serve`, que salió por la misma comprobación sin abrir socket. `curl` a `127.0.0.1:9108` devolvió `curl: (7) Failed to connect`; túnel Windows `ssh -N -L 9108:...` mostró `Connection refused`: síntomas derivados de que **el servicio no escucha**, no prueba de falta de instalación.
- Terminal 2 a 16:40:11 `precheck` retornó `RESULTADO_PRECHECK_TOPOLOGIA=0` y `up` completó `OSPF_DUAL_FULL: SI`, dos vecinos Full por router, FIB por WAN-P, `RESULTADO_B2_DUALWAN_UP=0` / `RESULTADO_UP_B3=0`. Segundo intento de `up` a 16:40:39 dio `ERROR: recursos previos B2`, rc=3, evitando un despliegue duplicado. Ese rc=3 **es esperado cuando ya hay recursos**, no falla del primer `up`.
- En Terminal 2 hubo un intento fallido de contraseña `sudo` antes de autenticarse; no implica que `sudo` no esté instalado.
- No consta `fail`, `restore`, `down` ni un evento B3 capturado a partir de esta salida. **Estado de routers ahora se debe revisar** antes de volver a iniciar pruebas.
- Corrección de `inspect_router()` ya publicada: compara salida de Docker con `message.lower()`. Ausencia de contenedor se clasifica `OFFLINE` en lugar de `DEGRADED`, sin ocultar errores verdaderos de permiso o daemon; prueba de regresión en `tests/test_b3_live_exporter.py`, auditoría read-only en `scripts/validacion/auditar-dependencias-netlab360.sh`; instrucciones en [matriz de dependencias](../operaciones/matriz-dependencias-s01.md).

**Próximo paso:** inspeccionar `sudo docker ps -a --filter name=nl360-b2-`, marcador local y `ens33`; pull nuevo código, ejecutar prueba unitaria y auditoría de dependencias. Si el laboratorio ya está activo, **reutilizarlo** y lanzar exporter para lectura, sin otro `up`. Si los recursos no están, usar precheck y un solo `up` cuando el exporter preflight haya pasado. Conservar rollback exclusivo `bash scripts/laboratorio/b2-dualwan-ospf.sh down` al terminar. **No incrementar S01 45% hasta prueba del evento live.**
