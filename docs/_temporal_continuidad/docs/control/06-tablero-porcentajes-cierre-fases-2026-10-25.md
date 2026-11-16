# NETLAB360 — Control de fases y milestones

**Corte auditado el 10/11/2026 (Panamá).** Los porcentajes de la tabla coinciden ahora tanto con las issues individuales como con los contadores nativos del objeto `milestone` de GitHub. Son indicadores de seguimiento técnico/documental, no notas académicas ni aceptación final de la profesora. S01–S04 están administrativamente cerradas, con cero issues abiertas. El cierre original consta en [Actions #41383586585](https://github.com/recm0708/netlab360/actions/runs/41383586585).

| Milestone | Issues cerradas | Porcentaje | Estado del alcance |
|---|---:|---:|---|
| S01 | 14/14 | **100 %** | Milestone cerrada; base y seguridad SSH cerradas |
| S02 | 3/3 | **100 %** | Milestone cerrada; multisede completada |
| S03 | 5/5 | **100 %** | Milestone cerrada; SoT/Ansible/OpenTofu metadata-only |
| S04 | 6/6 | **100 %** | Milestone cerrada; observabilidad, incidentes y SLI |
| S05 | 0/7 | 0 % | Pendiente |
| S06 | 0/3 | 0 % | Datos, diagnóstico ML y comparación contra reglas pendientes |
| S07 | 0/1 | 0 % | Pendiente |
| S08 | 2/11 | 18,2 % de issues cerradas | Entregables finales y revisión académica 13/11 pendientes |

## Reconciliación de los contadores internos de GitHub — RESUELTA 10/11/2026

El 04/11 la API de GitHub mostraba contadores desincronizados pese a que todas las issues de S01–S04 estaban cerradas: S01=11/3, S03=3/3 y S04=3/3, mientras S05 indicaba 0/6 (faltaba reconocer una issue abierta). Un intento anterior de reabrir/cerrar los propios milestones [#41948944162](https://github.com/recm0708/netlab360/actions/runs/41948944162) no corrigió las cifras.

**Solución comprobada:** desvincular temporalmente una issue de cada milestone afectado y restablecer su asignación original, **sin cambiar el estado abierto/cerrado ni los checkboxes**. El primer ensayo sincronizó S01; la [ejecución #42830631303](https://github.com/recm0708/netlab360/actions/runs/42830631303) corrigió S03, S04 y S05. Todos los scripts temporales con permiso `issues:write` fueron eliminados del repositorio tras las pruebas. Las referencias y números de los milestones originales se conservaron.

| Hito | Contador nativo corregido (`closed/open`) | Progreso | Estado |
|---|---:|---:|---|
| S01 | 14/0 | **100 %** | Cerrado |
| S02 | 3/0 | **100 %** | Cerrado |
| S03 | 5/0 | **100 %** | Cerrado |
| S04 | 6/0 | **100 %** | Cerrado |
| S05 | 0/7 | 0 % | Abierto |
| S06 | 0/3 | 0 % | Abierto |
| S07 | 0/1 | 0 % | Abierto |
| S08 | 2/9 | 18,2 % | Abierto |

**Validación posterior:** los recuentos del objeto milestone coinciden con las issues asignadas y su estado real, sin duplicaciones, sin reabrir trabajo terminado ni declarar S05–S08 completadas. Este incidente queda como antecedente resuelto, no como bloqueo de S05.

**Auditoría de issues cerradas:** revisamos las **30 issues cerradas**; ninguna contiene una casilla `- [ ]` pendiente. Se actualizaron ocho cuerpos con referencias históricas obsoletas, preservando las pruebas originales. De las 30 cerradas, 27 tienen motivo `completed`, dos (#9 y #37) tienen motivo `duplicate` por consolidación documental y una (#28) tiene motivo `not_planned`; estas últimas tres **no deben presentarse como funcionalidades implementadas**. La revisión del 13/11 (#48) se reasignó de S06 a S08 por ser un hito académico transversal. Las milestones S05–S08 siguen abiertas deliberadamente.

**S03:** la ampliación de `data sources` y propiedad OpenTofu de recursos externos quedó registrada en S05 ([#17](https://github.com/recm0708/netlab360/issues/17)); no representa funcionalidad realizada.

**S04:** SLI de scraping 15m 450/450 (100 %), 60m 1698/1740 (97,586 %) y 42 fallos. El 99 % se acepta internamente como **referencia de comparación** y se **incumplió** en 60m. No se afirma SLA contractual ni ratificación específica docente del indicador. Las notificaciones implementadas fueron solo visuales/locales.

**Revisión académica 30/10:** sesión realizada, la profesora consideró adecuado el avance y autorizó continuar, según informó el equipo. No equivale a defensa final aprobada. Próxima revisión: **13/11** [#48](https://github.com/recm0708/netlab360/issues/48).

**Informe:** Word/PDF único, borrador 4.6, 113 páginas, 20 figuras, 13 tablas, 10 referencias. **122 PNG oficiales** (S01=83, S02=9, S03=8, S04=22). No subir duplicados administrativos ni alterar manifiestos sin revalidar la integridad.

[Continuidad](../REANUDAR-AQUI.md) · [Issues](https://github.com/recm0708/netlab360/issues).
