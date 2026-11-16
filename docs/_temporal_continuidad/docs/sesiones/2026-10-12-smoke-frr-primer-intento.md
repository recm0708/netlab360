# B2-L3 — Primer ensayo de arranque FRR no superado

**Sesión real:** 2026-10-12, 19:07:24–19:08:06 (Panamá). **Issue:** #42; relacionado con #12.  
**Resultado:** ensayo no superado, con limpieza y preservación de gestión comprobadas. **No hay OSPF en ejecución**.

## Datos confirmados en la consola

- Repositorio local avanzó por fast-forward desde `1627726` hasta `ecad53b`, `bash -n scripts/laboratorio/b2-frr-smoke-aislado.sh` sin errores y `## main...origin/main` limpio.
- Ejecutado `bash scripts/laboratorio/b2-frr-smoke-aislado.sh --snapshot-confirmado`, después de verificar IPAM. Imagen FRR 10.7.1 `amd64`, digest `sha256:e995beaa50fdc9edb35eadcfefa29b7f062cc06f2b812613789b68fa541554d2`.
- En directorio temporal se preparó `/etc/frr/daemons` con `ospfd=yes`, `zebra=yes`, `bgpd=no`, `vtysh_enable=yes`. Se generó `frr.conf` mínimo para router-id `10.79.0.254`.
- Se creó un contenedor de prueba con `--network none --cap-drop ALL --cap-add NET_ADMIN --cap-add NET_RAW --security-opt no-new-privileges`. Docker devolvió identificador de contenedor.
- **Fallo reproducido solamente una vez:** `ERROR: ospfd/vtysh no respondieron a tiempo.`; código `RESULTADO_SMOKE_FRR=4`, igualmente `RESULTADO_LANZAMIENTO_FRR=4`. No consta un registro de procesos/zebra/ospfd funcionando, por lo que la prueba no está aprobada.
- Limpieza posterior: `sudo docker ps -a` vacío, `sudo ip netns list` vacío, `ens33=192.168.47.40/24` y ruta predeterminada por `192.168.47.2`, `docker/ssh/open-vm-tools` activos; Git limpio.
- Log original local: `~/netlab360-bootstrap/evidencias/09-b2-frr-smoke-20261012-190727.log`; el comando `tail` confirmó el mismo resultado.
- El script utiliza `docker run --rm` y el contenedor puede desaparecer cuando su proceso sale; el bloque `cleanup` no consiguió mostrar logs de demonios. **No se conoce aún la causa primaria** del fallo. No atribuir con certeza a FRR, Docker, límites de tiempo o contraseñas.

## Hipótesis por investigar (no comprobadas)

1. Los archivos `daemons` y `frr.conf` temporales se montaron propiedad del usuario Linux creador (UID del anfitrión), modo 0644, no del usuario `frr` (UID 100, GID 101). La documentación oficial de FRR requiere propiedad/permisos concretos para configs según el modo de inicio.
2. Se eliminaron todas las capacidades Linux y solo se añadieron NET_ADMIN/NET_RAW. El arranque de FRR puede necesitar otras capacidades para gestionar procesos y privilegios, sujetas al tipo de daemon y a la imagen.
3. El uso de `--rm` pudo borrar el contenedor y sus logs antes del chequeo; no se registraron `docker inspect`, estado de procesos ni stderr del daemon. Es preciso modificar el diagnóstico antes de otro ensayo.

Fuentes oficiales: https://docs.frrouting.org/en/latest/setup.html ; https://docs.frrouting.org/en/latest/ospfd.html ; https://github.com/FRRouting/frr/blob/master/tools/etc/frr/daemons .

## Evidencias gráficas aportadas

- `B2_03_Arranque_y_Daemons_FRR-1.png` y `-2.png`: inspección previa válida, código 0.
- `B2_04_Arranque_Zebra_OSPFD.png`: muestra **fallo** del ensayo, recomendable renombrar `B2_04_Diagnostico_Arranque_FRR.png`; no usar como aprobación de arranque.
- `B2_L2_01_Conectividad_Aislamiento_Recuperacion.png`: prueba histórica L2 con salida 0, válida.
- Las capturas se recibieron en conversación, pero **no se afirma** que estén versionadas en GitHub.

## Siguiente tarea

Sin repetir el ensayo todavía: ejecutar una inspección estática del comportamiento `frrcommon.sh`, el archivo `daemons` y las capacidades esperadas; conservar log. Después versionar una segunda variante del ensayo con propiedad correcta, capacidades justificadas, estado y logs persistidos antes de eliminar el contenedor, timeout explícito, verificaciones antes/después y rollback. No modificar VMnet8 ni `ens33`. La instantánea VMware base fue confirmada por el usuario con anterioridad.
