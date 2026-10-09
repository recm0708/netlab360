# NETLAB360 — Planificación semestral

> **Estado:** planificación inicial aprobada; aplicación todavía no implementada.

**Título académico:** Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico inteligente de redes empresariales multisede.

## Objetivo

Construir una plataforma en una máquina virtual Ubuntu Desktop para reproducir una red empresarial segmentada con sede principal, sucursales, rutas WAN redundantes, agregación de enlaces, equipos con redundancia verificable, herramientas de automatización y dashboards de observabilidad con escenarios de fallas controladas y analítica de anomalías.

## Entregas incrementales

| Hito | Período (2026) | Alcance |
| --- | --- | --- |
| [S01](../../issues/1) | 5–11 oct. | MVP transversal, pruebas de viabilidad |
| [S02](../../issues/2) | 12–18 oct. | Multisede, LACP y capacidad |
| [S03](../../issues/3) | 19–25 oct. | Network as Code, IaC y compliance |
| [S04](../../issues/4) | 26 oct.–1 nov. | Observabilidad e incidentes |
| [S05](../../issues/5) | 2–8 nov. | Redundancia de equipos y SDN |
| [S06](../../issues/6) | 9–15 nov. | Ingeniería de datos e IA evaluada |
| [S07](../../issues/7) | 16–22 nov. | AIOps con aprobación humana |
| [S08](../../issues/8) | 23–29 nov. | Regresión, documentación y OVA |

El detalle de aceptación por fase se encuentra en las issues semanales. Cada fase debe conservar capacidades verificables de red, automatización, observabilidad, analítica, interfaz y documentación. Las fechas y requisitos se ajustarán cuando la docente confirme la rúbrica.

## Entregables continuos

1. Informe académico en APA 7.
2. Bitácora de implementación con capturas, comandos y evidencias.
3. Manual de usuario ilustrado.
4. VM exportable e importada con éxito, sanitizada y acompañada de SHA-256.

## Fuente de verdad y seguridad

Los archivos de configuración, scripts y documentación se conservarán en Git; el estado observado de la red se validará operacionalmente. No incorporar credenciales, claves privadas, estados sensibles de OpenTofu ni discos de VM en este repositorio.

## Próximo paso

Importar el contenido completo del paquete `NETLAB360_Planificacion_v0.2.zip`, dejando sus archivos en la **raíz del repositorio**, no dentro de la carpeta `NETLAB360_Planificacion_Inicial/`. Las 37 issues ya fueron abiertas; el proceso de importación debe evitar duplicarlas.
