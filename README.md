# NETLAB360 — Plataforma virtualizada de redes empresariales multisede

NETLAB360 es una plataforma académica desarrollada sobre Ubuntu Desktop y VMware Workstation para implementar, automatizar, supervisar y evaluar una infraestructura empresarial de tres sedes (HQ, S1 y S2). El proyecto se organiza en **ocho fases** con comprobaciones técnicas propias, un informe único y una demostración final.

## Estado técnico verificable al 27/10/2026

| Fase | Estado real al corte | Resultados |
|---|---|---|
| S01 | 72 % **histórico de su matriz propia**, aceptación fundacional pendiente | VMware/Ubuntu, FRR OSPF, VLAN/ACL, LACP y bonding virtual, supervisión y diagnóstico por reglas |
| S02 | **Cerrada por alcance técnico** | Tres routers, cuatro WAN, nueve VLAN, OSPF Full 4/2/2, respaldo S1/S2, HTTP/ACL y comprobación de regresión |
| S03 | ~90 % **estimación técnica**; SoT y ownership OpenTofu aún pendientes | Ansible compliance/drift/reconciliación real, OpenTofu 17 `terraform_data` metadatos, GitHub Actions |
| S04 | **G0–G4 y G6 técnico comprobados; G5 medido, SLO por ratificar; escrito pendiente** | Colector 9110, Prometheus 9091, NOC 9120, incidente WAN real, historial persistente TSDB/SQLite, SLI 15m 100 % y 60m 97.586 % |
| S05–S08 | **0 % aceptación técnica de funcionalidades nuevas** | Redundancia/SDN y topología interactiva, IA, integración de servicios y entrega final por desarrollar |

Los porcentajes no son calificaciones ni promedios intercambiables. **99 %** es exclusivamente un SLO académico **candidato** del éxito de scrapes, **no aprobado**: en ventana 60 minutos solo 1698/1740 scrapes tuvieron éxito (97.586 %, 42 fallos, presupuesto propuesto restante −25). La observación condicional de `source_up` no prueba disponibilidad continua. [Matriz S04](docs/operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md).

## Arquitectura y operación

- **Máquina:** Ubuntu Desktop 26.04.1 en VMware; gestión `ens33=192.168.47.40/24` y GW `192.168.47.2`, aislada de la red de laboratorio.
- **Red multisede S02 reutilizada en S04:** tres routers FRRouting `nl360-s02-r-hq/s1/s2`, cuatro enlaces WAN, tres switches virtuales, nueve VLAN. Se comprobó activa en el postcheck S04; **su desmontaje aún no ha sido ejecutado para cierre de la sesión**.
- **Observabilidad S04:** exporter solo lectura `127.0.0.1:9110`, Prometheus `127.0.0.1:9091` con TSDB de 1 día y alertas, NOC `127.0.0.1:9120` con sedes CENTRAL/HQ/S1/S2, histórico SQLite y exportación CSV; el acceso desde Windows usa túnel SSH.
- **Fuente declarativa:** SoT IPAM 3 sedes/4 WAN/9 VLAN, estado `candidate`. OpenTofu S03 `terraform_data` metadata-only, sin aprovisionamiento de contenedores. Ansible consulta y reconcilia configuraciones FRRouting bajo pruebas autorizadas.
- **GitHub:** `main`, PRs y GitHub Actions para pruebas y auditoría de evidencias. Los JSON/SQLite operativos, estados OpenTofu y credenciales permanecen fuera de Git.
- **Capturas versionadas:** **129 PNG** verificadas mediante manifiestos: **S01 90, S02 9, S03 8, S04 22** (S04 lotes de 7+8+7; PRs #58, #67 y #75). Ninguna PNG S05–S08 todavía. [Auditoría por fase](evidencias/capturas/README.md).

La operación de apagado/reanudación de la VM para S05 debe seguir el [plan de parada segura](docs/05-plan-operativo-y-pausas.md), no una parada indiscriminada de Docker ni interfaces.
 
## Entrega académica

El trabajo escrito se presenta como **un único Word/PDF, mínimo 40 páginas**, con apartados 1–8 y referencias APA 7. **No habrá capítulo de anexos**. Los scripts, inventarios, configuraciones y evidencias técnicas pertinentes integrarán un archivo **`.tar` independiente**, con manifiesto de integridad y exclusión de credenciales.

El título comunicado a Teams el 17/10 es: «Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede». La aprobación final del título permanece pendiente de confirmación. Las revisiones del escrito son el **30/10** y **13/11**. La demostración final con PowerPoint será en vivo.

**Borrador académico recibido:** `1457-Proyecto Semestral_borrador4.0.pdf` (94 páginas), aún con S04 no integrada en los capítulos 5–8. Se entregarán correcciones por mensajes para incorporarlas al Word original; no se sustituye automáticamente el PDF adjunto. Revisión Teams 30/10 aún pendiente.

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
