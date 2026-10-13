# B2 — Segundo smoke FRR: error de acceso a daemons (antes del arranque)

**Fecha real del ensayo:** 2026-10-12 20:48:16–20:48:17 (-05:00, Panamá).  
**Hora de consulta del log:** 2026-10-12 22:35:00 (-05:00).  
**Estado:** intento no superado; falla de permisos en lectura local del script, **no de arranque FRR**.

## Procedimiento observado

- `git pull --ff-only origin main`: fast-forward `2886da9..304e469`, `bash -n` sin error, Git limpio.
- Se ejecutó `bash scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh --snapshot-confirmado`.
- `VALIDACIÓN B1: OK`. Configuración de FRR creada en `/tmp/nl360-smoke-v2.vKNNUFDh`; permisos exactos impresos:
  - Directorio: `755 100:101` (frr:frr).
  - `daemons`: `640 100:101` (frr:frr).
  - `frr.conf`: `660 100:102` (frr:frrvty).
- El script invocó `grep` como `rc-aa-ec`, usuario no propietario del archivo `daemons` con modo 640. Resultado: `Permiso denegado`; `RESULTADO_SMOKE_FRR_V2=2` y `RESULTADO_EJECUCION_FRR_V2=2`.
- **No se ejecutó el bloque `docker run -d` ni se iniciaron zebra, ospfd o routers**. Por ello el motivo identificado es un error de permisos de lectura del propio script, distinto del error de timeout de la versión inicial.
- `cleanup` confirmó sin contenedores/namespace residuales, `ens33=192.168.47.40/24`, gateway `192.168.47.2` intactos, servicios docker/ssh/open-vm-tools activos y Git limpio.
- Log original local `~/netlab360-bootstrap/evidencias/11-b2-frr-smoke-v2-20261012-204817.log`.
- El usuario confirmó una captura denominada `B2_06_Diagnostico_FRR_V2.png`; el PNG aún **no se ha subido** al repositorio. Se tomó de una consulta al log a las 22:35, no de una ejecución nueva.

## Corrección registrada en GitHub

En `scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh` se reemplazó `grep -E '^(ospfd|bgpd|vtysh_enable)=' "$TMP/daemons"` por `sudo grep -E ... "$TMP/daemons"` tras `chown/chmod`. Se mantienen los permisos seguros del archivo; no se otorgan permisos innecesarios al usuario normal.

El script corregido **no se ha ejecutado en esta sesión**. El siguiente ensayo podrá llegar por primera vez al bloque de arranque de Docker y recoger información sobre procesos. Es prematuro declarar zebra/ospfd configurados o funcionando.

## Próximos pasos y evidencias

1. Desde SSH: `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`.
2. Validar sintaxis `bash -n scripts/laboratorio/b2-frr-smoke-v2-con-logs.sh` y comprobar que el archivo contiene `sudo grep` después de los permisos.
3. Ejecutar una sola vez con `--snapshot-confirmado` (instantánea NETLAB360-BASE-HERRAMIENTAS confirmada por el usuario).
4. Comprobar códigos de salida, logs `11-b2-frr-smoke-v2-*.log`, red de gestión y ausencia de residuos.
5. Generar evidencia nueva con marcadores INICIO/FIN delimitando exactamente qué capturar. Usar `B2_07_Arranque_FRR_Verificado.png` si éxito, o `B2_07_Diagnostico_Arranque_FRR.png` si falla. La captura B2_06 anterior queda como histórico de diagnóstico.
6. Actualizar issue #42, este registro y `docs/00-estado-y-continuidad.md` tras verificar resultados.

**Alcance académico:** fase S01 sigue abierta; WAN dual, enrutamiento OSPF, alarma/dashboard y LACP no implementados.
