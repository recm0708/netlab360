# NETLAB360 — Plataforma virtualizada de redes empresariales multisede

NETLAB360 es una plataforma académica desarrollada sobre Ubuntu Desktop y VMware Workstation para implementar, automatizar, supervisar y evaluar una infraestructura empresarial de tres sedes (HQ, S1 y S2). El proyecto se organiza en **ocho fases** con comprobaciones técnicas propias, un informe único y una demostración final.

## Estado técnico al 25/10/2026

| Fase | Avance de seguimiento | Comprobaciones realizadas |
|---|---:|---|
| 1 — Base experimental | 72 % histórico | VMware/Ubuntu, FRR/OSPF, VLAN/ACL local, doble WAN HQ-S1, LACP y bonding virtual, automatización inicial, Prometheus y diagnóstico por reglas |
| 2 — Infraestructura multisede | ≈90 % | Tres routers, cuatro WAN, nueve VLAN, failover y restauración de S1/S2, HTTP/ACL, validaciones y desmontaje controlado |
| 3 — Automatización y GitOps | ≈90 % | Ansible sobre FRR activo con compliance y reconciliación, OpenTofu metadata-only 17/17, CI GitHub Actions, PR #49 fusionado, 87/87 tests offline |
| 4–8 — Módulos posteriores | 0 % de aceptación formal | Observabilidad integrada, redundancia/SDN, diagnóstico inteligente, pruebas extremo a extremo y entrega final |

Los porcentajes son indicadores internos, no calificaciones ni el resultado de una única rúbrica. [Criterios de aceptación por fase](docs/control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).

## Arquitectura y operación

- **Máquina:** Ubuntu Desktop 26.04.1 sobre VMware, interfaz administrativa `ens33=192.168.47.40/24` y puerta de enlace `192.168.47.2`.
- **Red empresarial experimental:** tres routers FRRouting, enlaces WAN principales y de respaldo, tres switches virtuales y nueve VLAN. La fase 2 está **desmontada intencionalmente** tras validar sus escenarios.
- **Administración declarativa:** el inventario IPAM/SoT organiza tres sedes, cuatro enlaces y nueve VLAN. OpenTofu materializa 17 metadatos `terraform_data` y **no** despliega los dispositivos; Ansible valida y reconcilia costos reales de FRRouting.
- **Control de cambios:** repositorio privado, `main` como única rama permanente, scripts versionados, pruebas offline, pull requests y GitHub Actions. Las ramas de trabajo se eliminan tras fusionarse mediante un control que compara su SHA. Los recursos de estado OpenTofu están fuera del clon y se excluyen de entregables.
- **Evidencias:** directorios [`evidencias/capturas/fase1`–`fase8`](evidencias/capturas/README.md). Hay **107 PNG definitivas publicadas**: **90 de fase 1**, **9 de fase 2** y **8 de fase 3**, con integridad verificada. El lote de 21 imágenes se incorporó mediante el [PR #53](https://github.com/recm0708/netlab360/pull/53), acompañado de un [manifiesto SHA-256](evidencias/manifiestos/MANIFIESTO_SHA256_CAPTURAS_2026-10-25.csv) y de [CI posterior satisfactoria](https://github.com/recm0708/netlab360/actions/runs/40241580823).

## Entrega académica

El trabajo escrito se presenta como **un único Word/PDF, mínimo 40 páginas**, con apartados 1–8 y referencias APA 7. **No habrá capítulo de anexos**. Los scripts, inventarios, configuraciones y evidencias técnicas pertinentes integrarán un archivo **`.tar` independiente**, con manifiesto de integridad y exclusión de credenciales.

El título comunicado a Teams el 17/10 es: «Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede». La aprobación final del título permanece pendiente de confirmación. Las revisiones del escrito son el **30/10** y **13/11**. La demostración final con PowerPoint será en vivo.

## Documentación y continuidad

- [Reanudación técnica vigente](docs/REANUDAR-AQUI.md)
- [Puertas de cierre y pendientes comprobados de fases 1–3](docs/control/07-puertas-cierre-fases1-a-3-2026-10-25.md)
- [Convenciones de redacción y nomenclatura](docs/convenciones/01-redaccion-y-nomenclatura.md)
- [Criterios docentes](docs/academico/00-criterios-docentes-y-hitos.md)
- [Política editorial y entrega TAR](docs/entregables/00-politica-editorial-y-entrega-acumulativa.md)
- [Informe académico maestro](docs/entregables/01-proyecto-investigacion-maestro.md)
- [Auditoría de las 111 capturas locales](docs/evidencias/09-auditoria-zip-fases1-2-3-2026-10-25.md)
- [Plan de ocho fases](docs/academico/02-plan-operativo-s02-s08-repriorizado.md)
- [Integridad y carga de imágenes aprobadas](scripts/mantenimiento/importar-capturas-validadas-20261025.sh)
- [Issues de implementación](https://github.com/recm0708/netlab360/issues)

**Seguridad:** no incorporar al repositorio archivos de clase, contraseñas, tokens, llaves privadas, estados OpenTofu ni datos personales. Las cifras, pruebas y evidencias se registran exclusivamente según resultados obtenidos.
