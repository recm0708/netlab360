# NETLAB360

**Plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede.**

Desarrollamos NETLAB360 como proyecto semestral de **Tópicos Especiales II** en la Universidad Tecnológica de Panamá. Integramos tres sedes virtuales (HQ, S1 y S2) para diseñar, validar y documentar escenarios de conectividad, automatización, supervisión y recuperación de fallos.

## Tecnologías

- **Infraestructura:** VMware Workstation, Ubuntu Desktop, Docker y FRRouting/OSPF.
- **Automatización:** Python, Ansible, OpenTofu y GitHub Actions.
- **Observabilidad:** Prometheus, exportadores propios, NOC web y SQLite.

## Avance del proyecto

| Fase | Alcance | Estado |
|---|---|---|
| S01 | Laboratorio base, conectividad, redundancia y primeros prototipos | Cerrada internamente |
| S02 | Topología HQ/S1/S2, cuatro enlaces WAN y nueve VLAN | Cerrada |
| S03 | SoT candidata, cumplimiento Ansible, 17 metadatos OpenTofu y GitOps | Cerrada por alcance implementado |
| S04 | NOC multisede, alertas WAN, persistencia y medición SLI | Implementación validada; decisiones académicas pendientes |
| S05–S08 | Ampliaciones, integración y entregables finales | Pendientes |

No atribuímos al proyecto capacidades que todavía no implementamos: OpenTofu S03 administra **metadatos locales**, el objetivo de SLO 99 % sigue pendiente de ratificación y no hemos acreditado notificaciones externas ni modelos ML.

## Documentación y evidencias

- [Punto de reanudación](docs/REANUDAR-AQUI.md) y [control de fases](docs/control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
- [Topología multisede](topologias/s02-frr/README.md), [Ansible S03](ansible/s03/README.md) y [OpenTofu S03](iac/s03/README.md).
- [Observabilidad](servicios/observabilidad/README.md), [NOC multisede](servicios/noc-s04/README.md) y [catálogo de capturas](evidencias/capturas/README.md).
- [Seguimiento de tareas e hitos](https://github.com/recm0708/netlab360/issues).

Conservamos **122 capturas oficiales** con manifiestos de integridad: S01 (83), S02 (9), S03 (8) y S04 (22). El informe académico unificado, el TAR técnico y la presentación se gestionan como entregables del proyecto; el cierre interno de cada fase no implica aprobación docente.
