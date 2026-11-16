# NETLAB360

**Plataforma virtualizada para automatización, observabilidad y diagnóstico de redes empresariales multisede.**

Desarrollamos NETLAB360 como un laboratorio reproducible para estudiar la operación de redes de tres sedes (HQ, S1 y S2). Integramos FRRouting/OSPF, segmentación VLAN, automatización Ansible/OpenTofu, telemetría, un centro de operaciones de red (NOC), agregación LACP, Open vSwitch/Faucet y alta disponibilidad lógica de servicios HTTP.

## Arquitectura y alcance

El entorno se ejecuta en una máquina virtual Ubuntu Desktop con redes experimentales aisladas. La interfaz de administración `ens33` utiliza `192.168.47.40/24` y puerta de enlace `192.168.47.2`; los ensayos no deben modificarla. Los routers virtuales, switches, hosts y servicios se distribuyen entre contenedores y espacios de nombres de red. La plataforma no representa redundancia física del servidor anfitrión.

| Fase | Resultado acreditado | Alcance |
|---|---|---|
| S01 | Línea base FRR/OSPF, VLAN, pruebas de conectividad, automatización inicial | Laboratorio de referencia |
| S02 | Tres sedes, cuatro enlaces WAN, nueve VLAN y conmutación de rutas | Infraestructura multisede |
| S03 | Ansible sobre FRR, reconciliación de desviaciones y GitOps | OpenTofu administra 17 registros locales de metadatos, no routers externos |
| S04 | Métricas, alertas, incidentes y persistencia SQLite/Prometheus | Observabilidad y diagnóstico por reglas |
| S05 | WAN/HTTP HA, LACP HQ/S1/S2, OVS/Faucet, NOC y ensayos de recuperación | Implementación y aceptación técnica comprobadas; publicación de evidencias en preparación |
| S06–S08 | Actividades pendientes según sus criterios específicos | No se declara entrenamiento ML, AIOps ni entrega final sin verificaciones |

## Evidencias y validación

La fase S05 registra **71 capturas PNG originales** y un ciclo de conmutación real del backend HTTP `BACKEND_HQ → BACKEND_S1 → BACKEND_HQ` observado en 17 muestras. El último precheck no destructivo confirmó 21 namespaces, cuatro contenedores, seis servicios, integridad SHA-256 y gestión intacta. Estos archivos se encuentran consolidados en una rama local de evidencias; **su publicación en `main` debe verificarse antes de declarar el catálogo remoto completo**.

Las pruebas de rendimiento se interpretan dentro de las limitaciones de una VM y no se extrapolan a enlaces o equipos físicos de producción.

## Organización del repositorio

- [Estado técnico y continuidad](docs/00-estado-y-continuidad.md)
- [Punto de reanudación](docs/REANUDAR-AQUI.md)
- [Arquitectura, decisiones y diseño](docs/arquitectura/)
- [Plan de operación y conservación de la VM](docs/05-plan-operativo-y-pausas.md)
- [Tablero y aceptación de S05](docs/gestion/s05-tablero-vigente.md)
- [Catálogo de evidencias](evidencias/capturas/README.md)
- [Control del informe académico único](docs/entregables/01-proyecto-investigacion-maestro.md)
- [Criterios editoriales](docs/convenciones/01-redaccion-y-nomenclatura.md)

Los archivos de `docs/sesiones/` y los cortes anteriores de `docs/gestion/` constituyen registros históricos; no deben interpretarse como instrucciones operativas vigentes.

## Continuidad y seguridad

Preservamos los registros originales, manifiestos de integridad y configuraciones de cada fase. Los datos sensibles, estados de OpenTofu y credenciales permanecen fuera del repositorio. Mientras los 21 namespaces efímeros sigan activos, no corresponde apagar ni reiniciar el sistema invitado sin un procedimiento de reconstrucción comprobado. Para una pausa temporal utilizamos suspensión de la VM en VMware, sin confundirla con apagado o recuperación tras reinicio.
