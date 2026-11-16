# NETLAB360

**Plataforma virtualizada para automatización, observabilidad y diagnóstico de redes empresariales multisede**

NETLAB360 integra infraestructura virtual de tres sedes (HQ, S1 y S2) para analizar el comportamiento de protocolos de encaminamiento, agregación de enlaces, automatización, telemetría y segmentación definida por software. Desarrollamos el laboratorio en Ubuntu Desktop sobre VMware y utilizamos Docker, FRRouting, Ansible, OpenTofu, Prometheus, Open vSwitch y Faucet.

## Arquitectura

La red experimental combina cuatro enlaces WAN, nueve VLAN y tres routers FRRouting con OSPF. La administración permanece separada mediante `ens33 192.168.47.40/24` y puerta de enlace `192.168.47.2`.

- **Infraestructura y encaminamiento:** [topología multisede](topologias/s02-frr/README.md) e [inventario IPAM](inventario/ipam/topologia-s02.yaml).
- **Automatización:** [Ansible/FRR](ansible/s03/README.md), [OpenTofu](iac/s03/README.md) y pruebas de GitOps.
- **Observabilidad:** [métricas y Prometheus](servicios/observabilidad/README.md), [NOC S04](servicios/noc-s04/README.md) y [NOC de topología S05](servicios/topologia-s05/README.md).
- **Alta disponibilidad y LACP:** [diseño y resultados HTTP](docs/diseno/s05-ha-servicios-multisede.md) y [agregación multisede](docs/disenos/s05-lacp-integracion-multisede-candidata.md).
- **Segmentación SDN:** [Open vSwitch/Faucet](docs/diseno/s05-ovs-faucet-vs-bridge-frr-y-limpieza-segura.md).

## Resultados verificados

| Fase | Resultado técnico |
|---|---|
| S01 | Línea base FRRouting/OSPF, VLAN, servicios y automatización inicial |
| S02 | Tres sedes, cuatro enlaces WAN, nueve VLAN y conmutación de rutas |
| S03 | Auditoría y reconciliación Ansible sobre FRR; 17 recursos locales de metadatos OpenTofu |
| S04 | Prometheus, observabilidad WAN, eventos y persistencia de historial SQLite/TSDB |
| S05 | HTTP HA lógico HQ→S1→HQ, LACP 2→1→2 en las tres sedes, segmentación Faucet y NOC integrado |
| S06–S08 | Funcionalidades adicionales, integración académica y entrega final sujetas a validación |

La aceptación técnica S05 comprobó 21 namespaces, cuatro contenedores, seis servicios activos, NOC saludable y gestión intacta. El ciclo de conmutación HTTP cuenta con 17 muestras originales. Estas pruebas acreditan alta disponibilidad **lógica**, no redundancia física de host o hipervisor.

## Evidencias y documentación técnica

Conservamos [193 capturas PNG](evidencias/capturas/README.md) distribuidas entre S01 y S05, acompañadas por inventarios y manifiestos SHA-256. Los ensayos de HA incorporan además registros JSONL y TXT originales.

- [Acta de aceptación técnica S05](docs/gestion/ACTA-ACEPTACION-TECNICA-S05-20261115.md)
- [Arquitectura](docs/arquitectura/) y [decisiones de diseño](docs/decisiones/)
- [Configuración e inventario del entorno](docs/infraestructura/)
- [Pruebas automatizadas](tests/) y [scripts de laboratorio](scripts/)
- [Capturas y registros de evidencia](evidencias/)

Las mediciones se obtuvieron en infraestructura virtualizada; no se atribuyen a equipos de producción. El código y las pruebas se mantienen separados de los registros y credenciales locales. Las actividades pendientes de S06–S08 no se presentan como implementadas.

La carpeta `docs/_temporal_continuidad/` contiene exclusivamente material de seguimiento interno y no corresponde a los entregables técnicos finales.
