# NETLAB360 — Diagnóstico estático FRR y normas de evidencia

**Fecha original del ensayo:** 2026-10-12 19:21:41 -05:00 (Panamá).  
**Host:** `netlab360-lab`; **issue:** #42.  
**Estado:** `RESULTADO_DIAGNOSTICO_ESTATICO=0`. **Solo lectura; el fallo del arranque de FRR sigue pendiente.**

## Comprobaciones derivadas del archivo de consola aportado

- `git pull --ff-only origin main` sincronizó `ecad53b..2886da9`; análisis Bash con `bash -n` sin error; Git limpio `## main...origin/main`.
- `bash scripts/diagnostico/diagnosticar-smoke-frr-b2.sh` pasó: fecha 19:21:41; `ens33=192.168.47.40/24`, gateway `192.168.47.2`.
- Imagen `quay.io/frrouting/frr:10.7.1` `amd64`, entrypoint `/sbin/tini -- /usr/lib/frr/docker-start`, sin modificaciones.
- `/etc/frr/daemons` pertenece a `frr:frr`; `/etc/frr`, `/run/frr` y `/var/run/frr` también pertenecen al usuario/grupo FRR.
- Las notas **contenidas dentro del propio archivo `daemons`** especifican que un daemon habilitado tradicionalmente requiere archivos de configuración de propiedad `frr:frr` y permisos `u=rw,g=r,o=`. Para `vtysh` describen el grupo `frrvty` y `ug=rw,o=`. Esto es documentación interna de la imagen y no prueba por sí solo la causa del error con el entrypoint Docker.
- `frrcommon.sh` identifica `mgmtd`, `zebra` y `staticd` como procesos de base y contiene lógica de chequeo de `frr.conf`. El `docker-start` usa `watchfrr $(daemon_list)`.
- El contenedor de inspección tenía **`CapEff/CapPrm/CapBnd = 0`**, lo que es coherente con el diagnóstico estático `--cap-drop ALL`. **No equivale a las capacidades del contenedor de smoke que ya terminó**.
- `sudo docker ps -a` no mostró contenedores; `sudo ip netns list` sin namespaces; servicios docker/ssh/open-vm-tools activos; Git limpio al final.
- Bitácora original local: `~/netlab360-bootstrap/evidencias/10-b2-frr-diagnostico-estatico-20261012-192141.log`. Se verificó también mediante `cat`; **no es una segunda ejecución del diagnóstico**.

## Resultado y decisión

El diagnóstico ha sido **válido** (código 0), pero **no soluciona ni demuestra el arranque efectivo de ospfd**. El smoke anterior de las 19:07 falló con código 4. No afirmar causa raíz sin logs del proceso real. Hipótesis: permisos/montaje, conjunto de capacidades insuficiente y pérdida de logs por `--rm`.

La documentación consultada para planear el siguiente ensayo incluye:
- https://docs.frrouting.org/en/latest/vtysh.html — configuración integrada.
- https://hub.docker.com/hardened-images/catalog/dhi/frr/guides — referencia de capacidades de daemon (otra distribución endurecida; usar orientativamente, no asumir equivalencia exacta de imágenes).
- https://github.com/FRRouting/frr/blob/master/tools/etc/frr/daemons — documentación de propietarios, grupos y habilitación.

## Protocolo obligatorio de capturas

Desde ahora toda evidencia debe tener cuatro instrucciones explícitas:

1. **Código de captura y nombre exacto** de PNG.
2. **Comando de vista**, que imprima `========== INICIO CAPTURA ... ==========` y `========== FIN CAPTURA ... ==========` sin limpiar ni editar la salida real.
3. **Límites textuales exactos**: fotografiar desde el marcador INICIO hasta el marcador FIN, si cabe legiblemente; si no, dividir en 2 capturas `_Parte1` y `_Parte2`, con rangos indicados.
4. **Condición de validez:** resultado observable (salida/código) y fecha/hostname; distinguir salida mostrada desde un archivo .log de ejecución nueva. **No tomar captura de éxito si la prueba falla.**

Mantener logs íntegros fuera de Git mientras contienen datos potencialmente sensibles. Los resúmenes versionados deben indicar cuándo el registro ha sido leído y cuándo un experimento realmente se ejecutó.

## Captura pendiente B2_05

El diagnóstico de las 19:21 ya terminó, no repetirlo. Ejecutar una vista corta del log original que imprima la fecha y host del ensayo, las notas de permisos, usuario/grupo, líneas de `daemon_list`, `DIAGNOSTICO_ESTATICO: OK` y el postcheck. Capturar entre los marcadores explícitos. Si un patrón no aparece, conservar el log e investigar sin editar resultados.

## Próximo ensayo

Versionar **smoke v2** que utilice propiedad de archivos FRR apropiada, evite `--rm` hasta guardar `docker inspect`/`docker logs`, capture estado de `vtysh`, limpie únicamente recursos etiquetados NETLAB360 y preserve `ens33` y las rutas del anfitrión. Ejecutarlo una sola vez tras `git pull` y verificación de sintaxis. El snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` está confirmado por usuario; issue #41 cerrada.
