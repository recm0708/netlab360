## Prioridad actual 27/10 — apagado iniciado; informe 4.3

La secuencia `sudo systemctl poweroff` se ejecutó tras `S04_APAGADO_AUTORIZADO=SI`; la VM cerró el SSH. **Confirmación `Powered Off` de VMware pendiente**. No volver a ejecutar el desmontaje. Borrador 4.3 de **99 pp.**, con sección 5.6 completa (5.6.1–5.6.5); resta añadir 6.9, análisis/conclusiones de S04 y actualizar Tabla12, más el preámbulo general del capítulo6. [Bitácora vigente](sesiones/2026-10-27-s04-poweroff-solicitado-borrador43.md).

## Prioridad del corte 27/10 — borrador4.2 y entorno desmontado

**Estado actualizado a partir de evidencia real:** `1457-Proyecto Semestral_borrador4.2.pdf` (**95 páginas**), correcciones 6–13 confirmadas, duplicación obsoleta en 4.7 p.32 a retirar y S04 **todavía sin** 5.6, 6.9 y 7.10. [Bitácora vigente](sesiones/2026-10-27-s04-borrador42-desmontaje-validado.md). Los procesos NOC/exporter/Prometheus se detuvieron, la TSDB quedó respaldada en frío, y la topología S02 fue eliminada correctamente en 4.73/4.74. Validación **4.75**: 12 namespaces LAN ausentes, cuatro WAN retiradas, 3 routers Docker eliminados, 3 eventos G3 conservados, `ens33=192.168.47.40/24`/GW .2 intacto y Git limpio; `S04_APAGADO_PREPARADO=OK`. **VM todavía encendida**, sin constancia de `systemctl poweroff`. Revisión académica 30/10 pendiente. Las referencias inferiores que describen 4.0 o topología activa corresponden a estado **histórico**.

# NETLAB360 — Estado vigente de continuidad (27/10/2026)

**Documento de orientación actual.** El estado histórico de 17/10 se conserva en Git y en bitácoras `docs/sesiones/`, no como situación técnica vigente.

## Alcance y entregables

- Un único informe institucional Word/PDF de mínimo 40 páginas, capítulos 1–8 más Referencias, sin sección de anexos; archivos técnicos en **un TAR independiente** saneado, sin secretos ni materiales docentes originales.
- Presentación PowerPoint y demostración en vivo al cierre S08. No se considera obligatoria una OVA/OVF; manual técnico independiente pospuesto.
- Borrador **4.0 del 27/10**, 94 páginas, recibido y auditado: todavía contiene solo implementaciones documentadas S01–S03, NOC descrito parcialmente como futuro y Tabla 5 S04 «Planificada». **El Word aún no está actualizado al cierre S04**. Correcciones listas para copiar por chat en [guion académico](academico/s04-guion-de-actualizacion-del-informe.md).
- Fechas docentes: **30/10** Introducción, objetivos, planteamiento por Teams, pendiente; **13/11** fundamento y diseño, pendiente. Título comunicado el 17/10, aprobación docente no acreditada.

## Arquitectura y verificación

- Ubuntu Desktop 26.04.1 LTS en VMware; red administrativa `ens33=192.168.47.40/24`, GW `192.168.47.2`. SSH por llave probado, hardening de contraseña aún en #38.
- S02 cerrada: 3 routers FRR, 4 WAN OSPF, 9 VLAN, recuperación por respaldos. S03: Ansible compliance/reconciliación real y OpenTofu 17 `terraform_data` metadata-only, SoT candidate pendiente de ratificar.
- S04: G0–G4 técnicamente probadas; NOC `127.0.0.1:9120`, exporter `:9110`, Prometheus `:9091`, histórico SQLite por sede y TSDB. G3 incidente real HQ/s1p con respaldo s1b, alertas y recuperación comprobadas.
- SLI 15m `450/450=100%`; 60m `1698/1740=97.586%`, **42 fallos**; 99 % es **SLO candidato no aprobado**, error budget a 60m `−25`. No hay aviso externo por Alertmanager; solo alertas y cronología locales.
- Evidencias GitHub remotas auditadas: **129 PNG** (S01 90, S02 9, S03 8, S04 22), CI de SHA-256/dimensiones SUCCESS, G6 postcheck OSPF FULL 4/2/2, LAN 9/9+6/6, NOC active y red de gestión intacta.

## Hitos y prioridades

- Se comprobaron **50/50 issues con milestone**. GitHub calcula porcentaje por *issues cerradas*, no por pruebas realizadas: S01 11/14, S02 3/3, S03 3/6, S04 2/6, S05 0/6, S06 0/4, S07 0/1, S08 1/10. Consultar [tablero de control](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
- La red S02 se encuentra **activa según último postcheck**, los procesos S04 usan cuatro terminales; **no consta apagado posterior**. Seguir [apagado seguro](05-plan-operativo-y-pausas.md): respaldos → parar NOC, Prometheus y exporter → LAN down → WAN down → Docker Compose S02 down → comprobar gestión → poweroff Ubuntu.
- **Primero:** incorporar textos de S04 al Word y verificar PDF actualizado; ratificar el alcance de SLO/avisos y registrar cierre interno apropiado. **Después:** arrancar S05 con criterios específicos ([issue #5](https://github.com/recm0708/netlab360/issues/5), [topología #64](https://github.com/recm0708/netlab360/issues/64)). No volver a provocar G3 para generar nuevas capturas.

[Reanudar aquí](REANUDAR-AQUI.md) · [Control S04](operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md) · [Guion de edición 4.0](academico/s04-guion-de-actualizacion-del-informe.md).
