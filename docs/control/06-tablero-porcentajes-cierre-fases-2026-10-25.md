# NETLAB360 — Control de fases y milestones

**Corte auditado el 04/11/2026 (Panamá).** Los porcentajes de esta tabla se calculan a partir del estado individual de las issues, no del objeto `milestone` de GitHub. Son indicadores de seguimiento técnico/documental, no notas académicas ni aceptación final de la profesora. S01–S04 están administrativamente cerradas y sin issues abiertas reales. La auditoría original de cierres fue [Actions #41383586585](https://github.com/recm0708/netlab360/actions/runs/41383586585).

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

## Discrepancia de contadores internos de GitHub — verificada el 04/11/2026

La API de GitHub continúa devolviendo **contadores obsoletos**: S01/S03/S04 muestran issues abiertas inexistentes y S05 omite una issue abierta recientemente incorporada (#64). Las consultas de issues individuales son la fuente de verdad:

| Hito | Contador interno `closed/open` | Resultado comprobado por listado de issues |
|---|---:|---:|
| S01 | 11/3 (79 %) | 14 cerradas / 0 abiertas = **100 %** |
| S02 | 3/0 (100 %) | 3 cerradas / 0 abiertas = **100 %** |
| S03 | 3/3 (50 %) | 5 cerradas / 0 abiertas = **100 %** |
| S04 | 3/3 (50 %) | 6 cerradas / 0 abiertas = **100 %** |
| S05 | 0/6 (0 %) | 0 cerradas / **7 abiertas** = **0 %** |

La [ejecución de diagnóstico #41948944162](https://github.com/recm0708/netlab360/actions/runs/41948944162) contrastó para cada hito los listados reales, verificó ausencia de checkboxes pendientes y probó reabrir/cerrar el milestone con permisos de Issues. **El contador no se recalculó**: persistió idéntico antes y después. Se retiró del repositorio el workflow temporal tras la prueba; no quedó automatización privilegiada activa. Existe un [reporte público del mismo síntoma en GitHub Community](https://github.com/orgs/community/discussions/211801). Los campos `open_issues` y `closed_issues` de los milestones son contadores administrados por GitHub; no deben falsificarse ni reemplazarse mediante cambios artificiales de estado de issues. **Hasta que GitHub sincronice sus contadores, la fuente verificable de avance es el listado individual de issues.**

**Auditoría de issues cerradas:** revisamos las **30 issues cerradas**; ninguna contiene una casilla `- [ ]` pendiente. Se actualizaron ocho cuerpos con referencias históricas obsoletas, preservando las pruebas originales. Dos cierres no representan funcionalidades entregadas: #37 consolidada como duplicado y #28 cerrada como no planificada. La revisión del 13/11 (#48) se reasignó de S06 a S08 por ser un hito académico transversal. Las milestones S05–S08 siguen abiertas deliberadamente.

**S03:** la ampliación de `data sources` y propiedad OpenTofu de recursos externos quedó registrada en S05 ([#17](https://github.com/recm0708/netlab360/issues/17)); no representa funcionalidad realizada.

**S04:** SLI de scraping 15m 450/450 (100 %), 60m 1698/1740 (97,586 %) y 42 fallos. El 99 % se acepta internamente como **referencia de comparación** y se **incumplió** en 60m. No se afirma SLA contractual ni ratificación específica docente del indicador. Las notificaciones implementadas fueron solo visuales/locales.

**Revisión académica 30/10:** sesión realizada, la profesora consideró adecuado el avance y autorizó continuar, según informó el equipo. No equivale a defensa final aprobada. Próxima revisión: **13/11** [#48](https://github.com/recm0708/netlab360/issues/48).

**Informe:** Word/PDF único, borrador 4.6, 113 páginas, 20 figuras, 13 tablas, 10 referencias. **122 PNG oficiales** (S01=83, S02=9, S03=8, S04=22). No subir duplicados administrativos ni alterar manifiestos sin revalidar la integridad.

[Continuidad](../REANUDAR-AQUI.md) · [Issues](https://github.com/recm0708/netlab360/issues).
