# NETLAB360

**Plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede.**

Desarrollamos NETLAB360 como proyecto semestral de **Tópicos Especiales II** en la Universidad Tecnológica de Panamá. Integramos tres sedes virtuales (HQ, S1 y S2) para diseñar, validar y documentar conectividad, automatización, supervisión y recuperación de fallos.

## Tecnologías

- **Infraestructura:** VMware Workstation, Ubuntu Desktop, Docker y FRRouting/OSPF.
- **Automatización:** Python, Ansible, OpenTofu y GitHub Actions.
- **Observabilidad:** Prometheus, exportadores propios, NOC web y SQLite.

## Avance verificado — 01/11/2026

| Fase | Alcance | Estado |
|---|---|---|
| S01 | Laboratorio base, conectividad, redundancia y primeros prototipos | **Cerrada** |
| S02 | Topología HQ/S1/S2, cuatro WAN y nueve VLAN | **Cerrada** |
| S03 | SoT candidata, Ansible FRR, 17 metadatos OpenTofu y GitOps | **Cerrada según su alcance real** |
| S04 | NOC multisede, incidente WAN, persistencia y medición SLI | **Cerrada técnicamente** |
| S05–S08 | SDN, redundancia avanzada, diagnóstico, integración y entrega | Pendientes |

No atribuimos al proyecto capacidades aún no implementadas: OpenTofu S03 administra **metadatos locales**, no infraestructura externa. Utilizamos el **99 % como referencia experimental interna** para evaluar el SLI de recolección; la ventana de 60 minutos registró **97,586 %**, por lo que **no cumplió** dicho umbral. No acreditamos notificaciones externas ni un modelo ML entrenado.

La **presentación académica del 30/10/2026 se realizó**. Según la comunicación del equipo, la profesora indicó que el trabajo estaba bien y autorizó continuar con el siguiente entregable. Esto corresponde al avance presentado, no a la evaluación final de S05–S08.

## Documentación y evidencias

- [Reanudación](docs/REANUDAR-AQUI.md) y [control de fases](docs/control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
- [Topología multisede](topologias/s02-frr/README.md), [Ansible](ansible/s03/README.md) y [OpenTofu](iac/s03/README.md).
- [Observabilidad](servicios/observabilidad/README.md), [NOC](servicios/noc-s04/README.md) y [capturas](evidencias/capturas/README.md).
- [Issues y próximos entregables](https://github.com/recm0708/netlab360/issues).

Conservamos **122 PNG oficiales** (S01=83, S02=9, S03=8 y S04=22) bajo manifiestos de integridad. El informe unificado de corte es el borrador 4.6, con 113 páginas, 20 figuras y 13 tablas. Continuaremos con S05 sin repetir las fases ya comprobadas.
