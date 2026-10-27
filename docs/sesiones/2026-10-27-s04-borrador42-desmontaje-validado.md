# NETLAB360 — S04: desmontaje limpio de la topología y auditoría del borrador 4.2

**Registro: 27/10/2026.** Se basa en el PDF `1457-Proyecto Semestral_borrador4.2.pdf` y la salida real de Ubuntu `Texto pegado(20261027-091901).txt`, aportados por el operador. No se suben aquí las fuentes originales ni registros que podrían identificar usuarios.

## Estado académico

- Último PDF **4.2, 95 páginas**, con correcciones **6–13 efectivamente incorporadas**: 2.4.1, 3.8, introducción de diseño, Tabla 1, 4.7, 4.8, 4.8.1 y capítulo 5/Tabla 5. Se mantienen 15 figuras, 12 tablas, y capítulos 1–8 sin la sección nueva **5.6**, las pruebas **6.9** o el análisis **7.10**. Aceptación del manuscrito S04 pendiente.
- **Un párrafo antiguo duplicado todavía aparece en 4.7, página 32**: «Las funciones de automatización, observabilidad y diagnóstico se desarrollan progresivamente y no constituyen todavía un sistema completamente integrado...», inmediatamente tras el párrafo actualizado. Indicado al usuario eliminar **solo** el párrafo viejo, conservando el texto actual y título 4.7.1.
- SLO 99% exclusivamente **candidato no ratificado**; muestras 15m 450/450=100%, 60m 1698/1740=97.586%, 42 fallos, remanente -25; sin notificaciones externas. No editar PDF directamente; textos se suministran por chat para copiar al Word.

## Preapagado, TSDB y topología — comprobación real

- Paso **4.72**: backup en frío comprimido de TSDB `~/netlab360-bootstrap/s04/evidencias/S04_Preapagado_20261027T084907083378Z/prometheus_tsdb_s04.tar.gz`, legible por tar, SHA256 **`e7602327d233fcb7dccd60f57fc3230202b1998c592655ec75ed20ef06ba49c1`**. Estaban presentes respaldos de `wan-links-state.json`, `lan-vlan-state.json` y `incidentes.sqlite3` (G3 3/3). Estados originales validados con identificadores de propiedad `NETLAB360_S02_WAN_LINKS_V1` y `NETLAB360_S02_LAN_8021Q_V1`; routers `nl360-s02-r-hq/s1/s2` activos y aislados `network_mode=none`. Marcador `S04_RESPALDO_Y_PROPIEDAD=OK`.
- Paso **4.73**: antes de retirar, LAN S02 status correcto sobre tres switches y nueve VLAN; retiradas tres troncales y **12 namespaces** S02 (tres switches+nueve hosts), `S02_LAN_DOWN=OK`. WAN status detectó cuatro adyacencias Full HQ/dos S1/dos S2; retirados **cuatro enlaces veth WAN**, tres loopbacks S02, restaurados `ip_forward` previos, `S02_HOST_POSTCHECK=OK`, `S02_WAN_DOWN=OK`, `S04_TOPOLOGIA_ENLACES_RETIRADOS=OK`. No afecta ens33 ni rutas de gestión.
- Paso **4.74**: Docker Compose limitado al archivo `topologias/s02-frr/docker-compose.yml` devolvió `down 3/3`, tres contenedores retirados y `S04_DESMONTAJE_TOPOLOGIA=OK`.
- Paso **4.75**: `S04_RESPALDOS_CONSERVADOS=OK`, `S04_NAMESPACES_S02_AUSENTES=OK`, puertos 9110/9091/9120 libres, TSDB presente, `PRAGMA integrity_check=ok` SQLite y 3 eventos `verified_G3_terminal_log`, `S04_PERSISTENCIA_FINAL=OK`, `ens33=192.168.47.40/24`, GW `192.168.47.2`, Git `main` limpio commit **`1781ff5`**, `S04_APAGADO_PREPARADO=OK`.
- Las dos primeras solicitudes de contraseña `sudo` en paso 4.72 fueron incorrectas, seguidas de autenticación exitosa y pruebas completas; no afectaron red ni invalidaron el procedimiento. Los mensajes `channel 2: connect failed` corresponden al túnel Windows sin backend NOC ya detenido.

## Condición aún pendiente

**Aún no hay prueba de `sudo systemctl poweroff` ni confirmación de estado `Powered Off` en VMware.** Todo está preparado para apagar **solo** `netlab360-lab`, sin apagar Windows ni VMs de otra materia. Para reanudar S05, arrancar y auditar primero respaldos y administración, después desplegar routers→WAN→LAN siguiendo los scripts con prechecks; no reusar `state.json` guardados para iniciar nuevos recursos.

La documentación administrativa S04 permanece abierta hasta integrar 5.6, 6.9, 7.10 y conclusiones en el Word y resolver alcance de G5. La futura reunión Teams de 30/10 no está celebrada.

[Plan de apagado](../05-plan-operativo-y-pausas.md) · [Guion académico](../academico/s04-guion-de-actualizacion-del-informe.md) · [Issue #4](https://github.com/recm0708/netlab360/issues/4).
