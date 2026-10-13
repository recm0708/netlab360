# NETLAB360 — Planificación semestral

> **Estado verificado (2026-10-12, 23:57 Panamá):** S01 **abierta, ~40% estimado** (ver [control ponderado](docs/control/01-avance-s01.md)); base Ubuntu/VMware, VMnet8/SSH y snapshot completos; IPAM draft validado, ensayo VLAN L2 completado y **FRRouting v5 con zebra/ospfd/OSPF local funcionando**, además de **dos routers R-HQ/R-S1 con OSPF Full por WAN principal/respaldo, conmutación y restauración de FIB comprobadas**. Todavía faltan pings LAN end-to-end, métricas/alertas, API/dashboard, IaC del laboratorio e IA.

**Título académico:** Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico inteligente de redes empresariales multisede.

## Objetivo

Construir una plataforma en una máquina virtual Ubuntu Desktop para reproducir una red empresarial segmentada con sede principal, sucursales, rutas WAN redundantes, agregación de enlaces, equipos con redundancia verificable, herramientas de automatización y dashboards de observabilidad con escenarios de fallas controladas y analítica de anomalías.

## Entregas incrementales

| Hito | Período (2026) | Alcance |
| --- | --- | --- |
| [S01](https://github.com/recm0708/netlab360/issues/1) | 5–11 oct. | MVP transversal, pruebas de viabilidad |
| [S02](https://github.com/recm0708/netlab360/issues/2) | 12–18 oct. | Multisede, LACP y capacidad |
| [S03](https://github.com/recm0708/netlab360/issues/3) | 19–25 oct. | Network as Code, IaC y compliance |
| [S04](https://github.com/recm0708/netlab360/issues/4) | 26 oct.–1 nov. | Observabilidad e incidentes |
| [S05](https://github.com/recm0708/netlab360/issues/5) | 2–8 nov. | Redundancia de equipos y SDN |
| [S06](https://github.com/recm0708/netlab360/issues/6) | 9–15 nov. | Ingeniería de datos e IA evaluada |
| [S07](https://github.com/recm0708/netlab360/issues/7) | 16–22 nov. | AIOps con aprobación humana |
| [S08](https://github.com/recm0708/netlab360/issues/8) | 23–29 nov. | Regresión, documentación y OVA |

El detalle de aceptación por fase se encuentra en las issues semanales. Cada fase debe conservar capacidades verificables de red, automatización, observabilidad, analítica, interfaz y documentación. Las fechas y requisitos se ajustarán cuando la docente confirme la rúbrica.

## Entregables continuos

1. Informe académico en APA 7.
2. Bitácora de implementación con capturas, comandos y evidencias.
3. Manual de usuario ilustrado.
4. VM exportable e importada con éxito, sanitizada y acompañada de SHA-256.

## Fuente de verdad y seguridad

Los archivos de configuración, scripts y documentación se conservarán en Git; el estado observado de la red se validará operacionalmente. No incorporar credenciales, claves privadas, estados sensibles de OpenTofu ni discos de VM en este repositorio.

## Ejecución actual y siguiente paso

- [Plan operativo, fases técnicas y pausas](docs/05-plan-operativo-y-pausas.md): primero B0 (línea base y salud) y B1 (arquitectura/IPAM), después MVP funcional de falla observada, telemetría, interfaz y analítica, con pausas tras avances verificables.
- [Estado de continuidad](docs/00-estado-y-continuidad.md) y [preparación técnica](docs/sesiones/2026-10-12-preparacion-base-validada.md).
- **Issues cerradas:** [#39](https://github.com/recm0708/netlab360/issues/39) (dirección IPv4), [#40](https://github.com/recm0708/netlab360/issues/40) (GitHub CLI y clonación) y [#41](https://github.com/recm0708/netlab360/issues/41) (herramientas y snapshot VMware confirmado). **S01 continúa abierta** en [#1](https://github.com/recm0708/netlab360/issues/1).
- **Subhitos funcionales cerrados dentro de issues abiertas:** B1 IPAM (#11), B2-L2 VLAN aislada (#30/#12) y FRRouting v5 en un contenedor (#42) con [evidencia técnica](docs/sesiones/2026-10-12-smoke-frr-v5-exitoso.md). **Siguiente prioridad:** pruebas ICMP bidireccionales por LAN en estados normal/respaldo/restaurado con `scripts/laboratorio/b2-dualwan-ping-lan.sh` (#42); después evento medido y alarma/dashboard (#12).
- **Seguimiento y evidencias:** [control S01](docs/control/01-avance-s01.md), [backlog semanal S01](backlog/semanas/01-semana-1.md), [auditoría posterior de capturas #43](https://github.com/recm0708/netlab360/issues/43).
- El archivo `NETLAB360_Planificacion_v0.2.zip` se importará solo tras revisión y **sin sobrescribir** documentos nuevos ni duplicar issues existentes; no está importado todavía.

**Protección de credenciales:** el GitHub CLI autenticado dentro del invitado puede contener un token local; se debe eliminar/sanitizar antes de compartir OVA y jamás versionarlo.
