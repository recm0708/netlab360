# NETLAB360 — Plataforma virtualizada de redes empresariales multisede

Proyecto académico de Tópicos Especiales II (UTP), desarrollado en Ubuntu Desktop con FRRouting, OSPF, Python, Ansible, OpenTofu, Prometheus y NOC web.

## Estado interno — 01/11/2026

| Fase | Estado | Capacidad demostrada |
|---|---|---|
| S01 | **Cerrada** | Base VMware/Ubuntu, IPAM, OSPF dual WAN, VLAN/ACL, bonding, observabilidad inicial, SSH protegido por clave |
| S02 | **Cerrada** | HQ/S1/S2, cuatro WAN, nueve VLAN, OSPF 4/2/2, conmutación y restauración |
| S03 | **Cerrada por alcance validado** | SoT candidate, Ansible FRR 8/8 y reconciliación 100→150→100, OpenTofu 17 metadatos, GitOps/CI |
| S04 | **Verificada técnicamente; aceptación pendiente** | NOC multisede, Prometheus, incidente WAN real, UNKNOWN, SQLite/TSDB y métricas SLI |
| S05–S08 | Pendientes | SDN/redundancia, análisis inteligente, integración y defensa final |

**Delimitación:** la SoT `candidate` está validada para laboratorio, no para producción. OpenTofu S03 maneja 17 objetos locales `terraform_data`, **no** recursos FRR/WAN externos. El uso de `data sources` y propiedad de recursos externos fue reprogramado a S05+ ([#17](https://github.com/recm0708/netlab360/issues/17)) y no se presenta como cumplido.

**S04:** SLI de scrapes 450/450 (100 %) en 15m y 1698/1740 (97,586 %) en 60m, con 42 fallos. Objetivo académico 99 % candidato, todavía pendiente de decisión. No se acredita un SLA de aplicaciones, notificaciones externas ni modelo ML.

**Informe académico de corte:** versión 4.6 de 113 páginas, 20 figuras y 13 tablas. **122 PNG oficiales**: 83 de S01, 9 de S02, 8 de S03 y 22 de S04. La aprobación docente, demostración, PowerPoint y TAR de anexos se gestionan en el cronograma de entrega final.

## Seguridad y operación

VM `netlab360-lab`, red de gestión `ens33 192.168.47.40/24`, gateway `192.168.47.2`. El 01/11 se verificó la autenticación SSH mediante ED25519, respaldos y recuperación local VMware, con contraseñas remotas deshabilitadas. La VM está en uso nuevamente desde esa fecha; no inferir que continúa apagada por el cierre de S04. No publicar secretos ni respaldos SSH.

[Reanudar aquí](docs/REANUDAR-AQUI.md) · [Control de fases](docs/control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [Evidencias](evidencias/capturas/README.md) · [Issues](https://github.com/recm0708/netlab360/issues).
