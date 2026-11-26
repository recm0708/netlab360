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
| FastAPI, Uvicorn, Plotly y Swagger UI | Consola web autenticada, visualización y documentación de API |

## Estado de implementación

| Componente | Estado comprobado |
|---|---|
| Entorno, direccionamiento y red multisede | Operativo: tres sedes, cuatro WAN, nueve VLAN |
| Automatización y cumplimiento | Metadatos OpenTofu y reconciliación FRR validados |
| Observabilidad y supervisión | Prometheus, exportador, históricos y alertas consultables |
| Disponibilidad y SDN | HTTP HA, LACP y OVS/Faucet comprobados |
| Diagnóstico inteligente | Modelos históricos congelados e inferencia exploratoria de lectura |
| AIOps supervisado | RCA, Intent Assurance, RFC, watchdog y API protegida validados en su alcance original |
| Consola interactiva | FastAPI, SQLite privado, sesiones, topología SVG, vistas operacionales, históricos Plotly y Swagger integrado validados |
| Pruebas de red y calidad de servicio | Implementación de diagnóstico activo, Blackbox Exporter y SLI/SLO pendiente |
| Actuación integrada, RAG y gestión de identidades | Integración y aceptación pendientes |
| Reconstrucción y extensiones | Arranque en frío, instalación limpia, ampliaciones multivendor y evaluación científica pendientes |

La consola utiliza HTML, CSS y JavaScript locales, temas claro y oscuro, filtros por sede, actualización configurable, consultas históricas por selección y exportaciones delimitadas. La topología única conserva el inventario completo de la fuente NOC y sus observaciones originales; no se atribuye conectividad a un estado administrativo ni a la existencia de un contenedor.

La regresión específica de la consola comprende 204 casos aprobados en el entorno científico de referencia. Validamos Swagger, consultas GET y exportaciones mediante el navegador. Conservamos las interfaces independientes mientras verificamos equivalencia completa, ingestión de alertas y recuperación. La [matriz de cobertura](docs/gestion/cobertura-academica-netlab360.md) registra los resultados y las brechas de validación.

## Documentación

Organizamos la documentación por componente. El [índice completo de documentación técnica](docs/README.md) organiza todos los documentos por su responsabilidad.

| Área | Referencia |
|---|---|
| Arquitectura | [Red multisede](docs/arquitectura/arquitectura-multisede-implementada.md) |
| Infraestructura | [Virtualización](docs/infraestructura/inventario-host-y-vmware.md) · [Ubuntu y SSH](docs/infraestructura/ubuntu-desktop-y-ssh.md) |
| Automatización | [Ansible](ansible/s03/README.md) · [OpenTofu](iac/s03/README.md) |
| Consola | [Aplicación y API](servicios/consola-s08/README.md) |
| Observabilidad | [Prometheus](servicios/observabilidad/README.md) · [NOC](servicios/topologia-s05/README.md) |
| Disponibilidad y SDN | [HTTP HA](docs/diseno/s05-ha-servicios-multisede.md) · [LACP](docs/diseno/s05-lacp-8023ad-multisede.md) · [SDN](docs/diseno/s05-dominio-sdn-ovs-faucet.md) |
| Diagnóstico inteligente | [Protocolo V2](docs/diseno/s06-protocolo-uniforme-v2.md) · [Evaluación](docs/diseno/s06-v2-evaluacion-cronologica-congelada.md) · [Falla HTTP](docs/diseno/s06-fault-http-hq-etiquetado-independiente.md) |
| AIOps supervisado | [Eventos](docs/diseno/s07-contrato-eventos-e-incidentes.md) · [RCA](docs/diseno/s07-contexto-y-correlacion-rca.md) · [Runbooks](docs/diseno/s07-runbooks-y-recomendaciones.md) |
| Actuación y API | [Intent Assurance y RFC](docs/diseno/s07-intent-assurance-y-rfc.md) · [Watchdog](docs/diseno/s07-intervencion-ospf-y-watchdog.md) · [API](docs/diseno/s07-api-controlada.md) |
| Validación | [Entorno, redes y observabilidad](docs/validacion/s01-s04-resultados.md) · [Disponibilidad y SDN](docs/validacion/s05-integracion-y-aceptacion.md) · [Ensayos AIOps](docs/diseno/s07-ensayos-operacionales.md) |
| Evidencias | [Catálogo general](evidencias/capturas/README.md) |
| Planificación | [Plan maestro](docs/diseno/s06-s08-plan-maestro-y-criterios.md) · [Consola interactiva](docs/diseno/s08-consola-interactiva-y-acciones.md) · [Cobertura académica](docs/gestion/cobertura-academica-netlab360.md) |

## Instalación y operación

Centralizamos los requisitos del sistema, las dependencias
y los procedimientos reproducibles en el
[directorio de operación](operacion/README.md).

El [catálogo de comandos](operacion/comandos/README.md) organiza los procedimientos por componente.

La reconstrucción integral desde un sistema limpio y
la compatibilidad con otras distribuciones Linux requieren
validación independiente.

## Comprobaciones

Desde la raíz del repositorio, con las dependencias del entorno técnico disponibles:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/validacion/validar_capturas_unificadas.py
```

Las regresiones de software no sustituyen las comprobaciones de la infraestructura activa. No ejecutar procedimientos de intervención sin verificar el alcance y disponer de los mecanismos de recuperación correspondientes.

## Alcance y limitaciones

El laboratorio funciona dentro de una única máquina virtual. La disponibilidad lógica no acredita redundancia física ni disponibilidad continua. Los modelos de diagnóstico inteligente se evaluaron bajo un protocolo ICMP controlado; el escenario HTTP es independiente. La actuación supervisada conserva incertidumbre, autorización humana y alcance acotado, sin remediación autónoma. La reconstrucción automática tras apagado completo y el despliegue permanente de la consola requieren aceptación independiente.

## Autoría, licencia y contribuciones

Desarrollamos este proyecto como equipo académico de NETLAB360. El material original autorizado se distribuye bajo la [licencia MIT](LICENSE); las dependencias y los recursos de terceros conservan sus licencias respectivas.

**Copyright © 2026 Rubén Enrique Cañizares Miranda.**

Para contribuir, consultar las [convenciones del proyecto](.github/CONTRIBUTING.md), la [política de seguridad](SECURITY.md) y los [datos de citación](CITATION.cff). Los datos privados, credenciales y estados operativos quedan fuera del repositorio.
