# NETLAB360

**Plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede**

## Descripción

Desarrollamos NETLAB360 para integrar tres sedes (HQ, S1 y S2) en un laboratorio virtualizado que permite estudiar encaminamiento, segmentación, automatización, observabilidad, diagnóstico inteligente y recuperación supervisada. Las intervenciones se limitan a recursos experimentales y conservan separado el plano administrativo.

## Arquitectura y tecnologías

| Componente | Función |
|---|---|
| Ubuntu, VMware y Docker | Entorno virtualizado y aislamiento de recursos |
| FRRouting y OSPF | Enrutamiento y redundancia WAN |
| VLAN y LACP | Segmentación y agregación Ethernet |
| OpenTofu y Ansible | Metadatos declarativos y reconciliación de FRR |
| Prometheus y NOC | Telemetría, incidentes y visualización |
| Open vSwitch y Faucet | Control SDN en dominio aislado |
| HTTP HA | Selección de backend principal y alternativo |
| Python y scikit-learn | Análisis experimental de telemetría |
| SQLite y systemd | Persistencia, autorización, auditoría y recuperación supervisada |
| API HTTP sobre socket Unix | Consultas y actuaciones RFC con control de acceso |

## Estado de implementación

| Fase | Alcance validado |
|---|---|
| S01 | Preparación del entorno y línea base |
| S02 | Tres sedes, cuatro enlaces WAN y nueve VLAN |
| S03 | Automatización, cumplimiento y metadatos OpenTofu |
| S04 | Observabilidad multisede e incidentes |
| S05 | HTTP HA, LACP, SDN y NOC integrado |
| S06 | Detección experimental de anomalías y diagnóstico inteligente |
| S07 | AIOps supervisado, RCA, Intent Assurance, RFC, watchdog y API controlada |
| S08 | Consola, copiloto RAG, recuperación integral y entrega: pendientes de aceptación |

S07 cuenta con las ocho issues técnicas cerradas, 49 capturas y regresión de 1258 pruebas (una omitida y ninguna fallida). El cierre académico de la fase se controla por separado en la [issue maestra #7](https://github.com/recm0708/netlab360/issues/7). La ampliación S09 es condicionada y no dispone de milestone aprobada.

## Documentación

Organizamos la documentación por componente. El [índice completo de documentación técnica](docs/README.md) organiza todos los documentos por su responsabilidad.

| Área | Referencia |
|---|---|
| Arquitectura | [Red multisede](docs/arquitectura/arquitectura-multisede-implementada.md) |
| Infraestructura | [Virtualización](docs/infraestructura/inventario-host-y-vmware.md) · [Ubuntu y SSH](docs/infraestructura/ubuntu-desktop-y-ssh.md) |
| Automatización | [Ansible](ansible/s03/README.md) · [OpenTofu](iac/s03/README.md) |
| Observabilidad | [Prometheus](servicios/observabilidad/README.md) · [NOC](servicios/topologia-s05/README.md) |
| Disponibilidad y SDN | [HTTP HA](docs/diseno/s05-ha-servicios-multisede.md) · [LACP](docs/diseno/s05-lacp-8023ad-multisede.md) · [SDN](docs/diseno/s05-dominio-sdn-ovs-faucet.md) |
| Diagnóstico inteligente | [Protocolo V2](docs/diseno/s06-protocolo-uniforme-v2.md) · [Evaluación](docs/diseno/s06-v2-evaluacion-cronologica-congelada.md) · [Falla HTTP](docs/diseno/s06-fault-http-hq-etiquetado-independiente.md) |
| AIOps supervisado | [Eventos](docs/diseno/s07-contrato-eventos-e-incidentes.md) · [RCA](docs/diseno/s07-contexto-y-correlacion-rca.md) · [Runbooks](docs/diseno/s07-runbooks-y-recomendaciones.md) |
| Actuación y API | [Intent Assurance y RFC](docs/diseno/s07-intent-assurance-y-rfc.md) · [Watchdog](docs/diseno/s07-intervencion-ospf-y-watchdog.md) · [API](docs/diseno/s07-api-controlada.md) |
| Validación | [S01–S04](docs/validacion/s01-s04-resultados.md) · [S05](docs/validacion/s05-integracion-y-aceptacion.md) · [S07](docs/diseno/s07-ensayos-operacionales.md) |
| Evidencias | [Catálogo general](evidencias/capturas/README.md) |
| Planificación | [Plan maestro](docs/diseno/s06-s08-plan-maestro-y-criterios.md) · [Consola S08](docs/diseno/s08-consola-interactiva-y-acciones.md) · [Cobertura académica](docs/gestion/cobertura-academica-netlab360.md) |

## Comprobaciones

Desde la raíz del repositorio, con las dependencias del entorno técnico disponibles:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validacion/validar_capturas_unificadas.py
```

Las regresiones de software no sustituyen las comprobaciones de la infraestructura activa. No ejecutar procedimientos de intervención sin verificar el alcance y disponer de los mecanismos de recuperación correspondientes.

## Alcance y limitaciones

El laboratorio funciona dentro de una única máquina virtual. La disponibilidad lógica no acredita redundancia física ni disponibilidad continua. Los modelos S06 se evaluaron bajo un protocolo ICMP controlado; el escenario HTTP es independiente. S07 conserva incertidumbre, autorización humana y alcance acotado, sin remediación autónoma. La reconstrucción automática tras apagado completo y la consola integrada corresponden a S08.

## Autoría, licencia y contribuciones

Desarrollamos este proyecto como equipo académico de NETLAB360. El material original autorizado se distribuye bajo la [licencia MIT](LICENSE); las dependencias y los recursos de terceros conservan sus licencias respectivas.

**Copyright © 2026 Rubén Enrique Cañizares Miranda.**

Para contribuir, consultar las [convenciones del proyecto](.github/CONTRIBUTING.md), la [política de seguridad](SECURITY.md) y los [datos de citación](CITATION.cff). Los datos privados, credenciales y estados operativos quedan fuera del repositorio.
