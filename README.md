**CORTE ACADEMICO VIGENTE — borrador 4.6, 27/10/2026:** informe único de **113 páginas** revisado frente a la guía docente `1457-Formato Proyecto Final.pdf`: portada, introducción, objetivos, problema, fundamento, diseño, implementación, pruebas, análisis, conclusiones, referencias y anexos técnicos remitidos al TAR separado previsto para la entrega final. Contiene **20 figuras (1–20), 13 tablas (1–13), 10 referencias** y **122 PNG oficiales** (S01=83, S02=9, S03=8, S04=22). Capítulos 7.10 y 8 actualizados al cierre técnico de S04; el SLO del 99 % sigue **candidato**, con muestra real 60 min 97,586 %. **Cierre editorial interno del texto hasta S04: validado; aprobación docente pendiente**. S01 conserva cierre SSH/compatibilidad/aceptación; S03 decisiones SoT y alcance de OpenTofu externo; S04 ratificación SLO y aceptación interna/docente. Fechas de revisión previstas: 30/10 y 13/11, no presumir realizadas. La VM se apagó ordenadamente, con sesión SSH cerrada; estado gráfico Powered Off aún por constatar.

*Las menciones posteriores a PDF 4.4/4.5 son registros históricos y no sustituyen este corte vigente.*

# NETLAB360 — Plataforma virtualizada de redes empresariales multisede

Proyecto académico en **Ubuntu Desktop 26.04.1 / VMware Workstation** para diseñar, automatizar, supervisar y validar un laboratorio empresarial multisede HQ/S1/S2. Ocho fases técnicas, **un único informe Word/PDF** con referencias APA 7, demostración final y paquete TAR técnico independiente.

## Estado comprobado — 27 de octubre de 2026

| Fase | Situación | Alcance probado |
|---|---|---|
| S01 | Línea base técnica comprobada; cierre fundacional pendiente | VM, IPAM, VLAN/ACL, FRRouting/OSPF, doble WAN, LACP y bonding virtual, OpenTofu/Ansible inicial, observabilidad y diagnóstico basado en reglas |
| S02 | **Cerrada por alcance** | 3 routers FRR, 4 WAN, 9 VLAN, OSPF Full 4/2/2, rutas 6/6, HTTP/ACL y conmutación S1/S2 |
| S03 | Automatización técnicamente comprobada; decisiones SoT/alcance declarativo pendientes | Ansible FRR activo, drift 100→150→100, OpenTofu 17 recursos de metadatos y GitHub Actions |
| S04 | **Pruebas G0–G4 aprobadas; SLI G5 medidos y G6 técnico comprobado; aceptación académica pendiente** | Colector 9110, Prometheus 9091, NOC 9120, incidente WAN real, UNKNOWN, TSDB/SQLite persistentes |
| S05–S08 | Planificadas | Redundancia/SDN, análisis inteligente, integración final y entrega |

**S04:** SLI del scrape observado 450/450 = 100 % (15m) y 1698/1740 = 97,586 % (60m), con 42 fallos; **99 % es un objetivo académico candidato**, no un SLO ratificado ni un SLA de usuarios. No se acreditaron notificaciones externas ni un modelo de IA.

## Evidencias oficiales de las cuatro primeras fases

| S01 | S02 | S03 | S04 | Total |
|---:|---:|---:|---:|---:|
| 83 PNG | 9 PNG | 8 PNG | 22 PNG | **122 PNG** |

Los archivos versionados están organizados en [evidencias/capturas/](evidencias/capturas/), protegidos por sus manifiestos SHA-256 y pruebas de regresión. Los registros operativos dinámicos, credenciales y estados OpenTofu no se versionan. La carpeta de cada fase contiene únicamente imágenes que corresponden al alcance técnico documentado.

## Arquitectura, operación y estado de la máquina

Gestión Ubuntu por `ens33=192.168.47.40/24`, gateway `192.168.47.2` en VMware VMnet8/NAT. El laboratorio utiliza contenedores FRRouting, redes Linux aisladas, enlaces WAN principal/respaldo y subinterfaces IEEE 802.1Q; la administración queda separada de los experimentos. Ansible realiza comprobaciones y reconciliación bajo autorización; OpenTofu S03 administra exclusivamente metadatos `terraform_data`.

**Corte operativo S04:** TSDB/SQLite respaldadas, WAN/LAN/FRR desmontadas de forma controlada, `sudo systemctl poweroff` ejecutado y conexión SSH cerrada por el servidor. La confirmación visual de estado `Powered Off` en VMware sigue pendiente. No encender Ubuntu solo para continuar la redacción.

## Informe académico y próximas actividades

El borrador **4.4 (110 páginas)** contiene implementación hasta **5.6** y pruebas hasta **6.9**, con figuras 16–20 y Tabla 13 incorporadas. Continúan pendientes actualización del capítulo 7 para reflejar S04, conclusiones y recomendaciones (capítulo 8), reconciliación de cifras oficiales de evidencias y de las tablas 11–13, aceptación interna y las revisiones académicas programadas para **30/10 y 13/11**. La aprobación docente de estas sesiones no se presume.

La fase S05 desarrollará topología interactiva, redundancia avanzada y SDN únicamente sobre señales medidas y pruebas reales.

## Documentación vigente

- [Estado de continuidad](docs/REANUDAR-AQUI.md)
- [Plan seguro de operación/apagado](docs/05-plan-operativo-y-pausas.md)
- [Matriz de fases y pendientes](docs/control/06-tablero-porcentajes-cierre-fases-2026-10-25.md)
- [Cierre técnico S04](docs/operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md)
- [Criterios docentes](docs/academico/00-criterios-docentes-y-hitos.md)
- [Control del escrito académico](docs/academico/s04-guion-de-actualizacion-del-informe.md)
- [Capturas oficiales por fase](evidencias/capturas/README.md)
- [Issues del proyecto](https://github.com/recm0708/netlab360/issues)

**Seguridad:** no almacenar claves privadas, tokens, contraseñas, datos personales ni estados operativos sensibles en Git.
