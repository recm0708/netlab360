# NETLAB360

**Plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede**

## Descripción

NETLAB360 es una plataforma de laboratorio desarrollada para diseñar, implementar y evaluar una red empresarial de tres sedes: HQ, S1 y S2. Integramos enrutamiento dinámico, segmentación, automatización de configuraciones, observabilidad y escenarios controlados de recuperación de servicios.

## Arquitectura y tecnologías

El laboratorio funciona sobre Ubuntu Desktop en VMware Workstation. La red administrativa está separada de los segmentos experimentales. Las WAN y VLAN virtuales utilizan FRRouting, OSPF, namespaces Linux y contenedores Docker; la plataforma incorpora OpenTofu, Ansible, Prometheus, Open vSwitch y Faucet.

| Componente | Función |
|---|---|
| FRRouting / OSPF | Encaminamiento dinámico y recuperación WAN multisede |
| VLAN / switching | Segmentación de tráfico por sede y servicio |
| OpenTofu / Ansible | Declaración de metadatos, configuración y reconciliación de FRR |
| Prometheus / NOC | Métricas, incidentes y representación del estado de la red |
| LACP 802.3ad | Agregación y recuperación de enlaces en las tres sedes |
| Open vSwitch / Faucet | Segmentación y control SDN de un dominio aislado |
| HTTP HA | Selección de backend principal y alternativo |

## Resultados de las fases

| Fase | Alcance realizado |
|---|---|
| S01 | Preparación del entorno, conectividad inicial y pruebas de referencia |
| S02 | Infraestructura multisede con cuatro enlaces WAN y nueve VLAN |
| S03 | Automatización de FRR, reconciliación y recursos locales OpenTofu |
| S04 | Métricas, incidentes y observabilidad de la red multisede |
| S05 | HTTP HA, LACP, SDN con Faucet y NOC integrado |
| S06–S08 | Funciones avanzadas y entrega final, sujetas a sus propias validaciones |

**Estado actualizado de S06 (23/11/2026):** **≈90 % técnico estimado, fase abierta**. El estudio histórico S06-041–S06-051 se preserva como exploratorio debido a un factor de confusión: 3 ICMP en NORMAL frente a 2 en DEGRADED. La segunda generación V2 tiene 3 ICMP uniformes en TRAIN (40 NORMAL/8 DEGRADED/12 RECOVERY), VALIDATION (20/8/12) y TEST (20/8/12) por ruta, y cuatro modelos congelados antes de las muestras futuras. El TEST prospectivo fue validado: F1 P95/IsolationForest/LogisticRegression HQ→S1 **0.941/0.941/1.000** y HQ→S2 **1.000/0.941/1.000**, 0 FN en los seis resultados y 0 falsas alarmas RECOVERY. El cierre científico validó deriva **descriptiva** KS 0.200 (S1), 0.125 (S2), y primera oportunidad de detección **retrospectiva** a 1416/1402 ms después del estímulo; no es tiempo real de alerta ni pronóstico. Modelos originales/V2 intactos, 21 namespaces, 4 Docker, guardia NONE/BASELINE, NOC/Prometheus/LACP/SDN sanos. **Pendientes:** FAULT independiente con recuperación y etiquetas confiables, alcance de concept drift y pronóstico/MAE como `NO_EVALUABLE` si no hay datos/horizonte, integración y evidencias finales e informe académico. Issues #6/#25/#26 abiertas; ver [plan maestro S06–S08](docs/diseno/s06-s08-plan-maestro-y-criterios.md) y [auditoría científica V2](docs/diseno/s06-v2-deriva-deteccion-y-limitaciones-finales.md).

La validación final de S05 comprobó 21 namespaces, cuatro contenedores y seis servicios activos, así como la conmutación lógica HTTP **HQ → S1 → HQ**. Estas pruebas se realizaron dentro de una máquina virtual; no se atribuye a ellas redundancia física de servidores.

## Estructura del proyecto

- [Arquitectura implementada](docs/arquitectura/arquitectura-multisede-implementada.md)
- [Diseño de disponibilidad HTTP](docs/diseno/s05-ha-servicios-multisede.md)
- [Diseño de agregación LACP](docs/diseno/s05-lacp-8023ad-multisede.md)
- [Diseño SDN](docs/diseno/s05-ovs-faucet-vs-bridge-frr-y-limpieza-segura.md)
- [Validación S01–S04](docs/validacion/s01-s04-resultados.md)
- [Validación S05](docs/validacion/s05-integracion-y-aceptacion.md)
- [Evidencias gráficas](evidencias/capturas/README.md)
- [Topología FRRouting](topologias/s02-frr/README.md)
- [Automatización Ansible](ansible/s03/README.md)
- [Infraestructura declarativa OpenTofu](iac/s03/README.md)
- [NOC multisede](servicios/topologia-s05/README.md)
- [Plan maestro S06–S08, objetivos y criterios de aceptación](docs/diseno/s06-s08-plan-maestro-y-criterios.md)
- [Gestión de milestones S01–S08 y reconciliación del contador S05](docs/gestion/s01-s08-hitos-descripciones-y-contador-s05.md)
- [Normalización de títulos y etiquetas de las 53 issues en español](docs/gestion/normalizacion-issues-y-etiquetas-es.md)
- [Adquisición de telemetría S06 y diseño de sesiones de observación](docs/diseno/s06-adquisicion-observacional.md)
- [Pruebas de rendimiento RTT, pérdidas y HTTP S06](docs/diseno/s06-mediciones-rendimiento.md)
- [Normalización y validación de calidad S06](docs/diseno/s06-normalizacion-y-calidad.md)
- [Escenarios S06 y controles de etiquetado verificable](docs/diseno/s06-escenarios-y-etiquetado.md)
- [S06 watchdog y requisitos de rollback seguro](docs/diseno/s06-watchdog-rollback-gates.md)
- [S06 simulación de autorización, TTL y rollback](docs/diseno/s06-rollback-simulacion.md)
- [S06-038A guardia root y temporizador sin cambio de red](docs/diseno/s06-038-guardia-root-y-watchdog-noop.md)
- [S06-038B restauración real de qdisc en namespace aislado](docs/diseno/s06-038b-restauracion-aislada.md)
- [S06-039 auditoría preventiva de cliente conectado](docs/diseno/s06-039-auditoria-preintervencion.md)
- [S06-040 recuperación en par veth aislado tras interrupción](docs/diseno/s06-040-recuperacion-veth-aislada.md)
- [S06-041 ventanas de telemetría con NORMAL operacional verificado](docs/diseno/s06-041-ventanas-normales-verificadas.md)
- [S06-041B IsolationForest baseline exploratorio y comparación P95](docs/diseno/s06-041b-baseline-ml-no-supervisado.md)
- [S06-042 intervención breve y etiquetado en el cliente real HQ](docs/diseno/s06-042-experimentos-hq-reales-y-watchdog.md)
- [S06-043 sesiones independientes y rollback protegido del cliente real HQ](docs/diseno/s06-043-lotes-multisesion-hq.md)
- [S06-044 evaluación binaria por sesión y análisis posrecuperación](docs/diseno/s06-044-evaluacion-binaria-holdout.md)
- [S06-045 replay de inferencia, UNKNOWN y auditoría de errores (aceptado en VM; F07 aprobada)](docs/diseno/s06-045-inferencia-hq-replay-readonly.md)
- [S06-046 telemetría reciente e inferencia exploratoria HQ (validado en VM; F08 aprobada)](docs/diseno/s06-046-telemetria-reciente-inferencia-hq.md)
- [S06-047 panel IA exploratorio en NOC S05 (validado en VM; F09 principal aprobada)](docs/diseno/s06-047-panel-ia-noc-readonly.md)
- [S06-048 estados IA explícitos y auditoría LACP/SDN (validado en VM)](docs/diseno/s06-048-estados-ia-y-observacion-lacp-sdn.md)
- [S06-049 auditoría de cronología y suficiencia prospectiva (validada en VM; gate pendiente de nuevos datos)](docs/diseno/s06-049-auditoria-readiness-prospectiva.md)
- [S06-050 preregistro de TEST futuro y modelos congelados (validado VM; muestreo 2/3 bloqueado)](docs/diseno/s06-050-preregistro-futuro-modelos-congelados.md)
- [S06-051 auditoría del muestreo por clase y split (validada VM; sesgo de protocolo confirmado)](docs/diseno/s06-051-auditoria-muestreo-protocolo-historico.md)
- [S06 — estudio prospectivo uniforme V2 y plan consolidado de cierre (TRAIN/VALIDATION/TEST verificados)](docs/diseno/s06-estudio-prospectivo-uniforme-y-cierre-consolidado.md)
- [S06 V2 TRAIN congelación de modelos (validada en VM)](docs/diseno/s06-v2-train-freeze-modelos.md)
- [S06 V2 evaluación VALIDATION/TEST con modelos congelados (TEST prospectivo validado en VM)](docs/diseno/s06-v2-evaluacion-cronologica-congelada.md)
- [S06 V2 análisis final de deriva, detección temporal y limitaciones (validado en VM)](docs/diseno/s06-v2-deriva-deteccion-y-limitaciones-finales.md)
- [Diseño del programa interactivo S08 y catálogo de acciones](docs/diseno/s08-consola-interactiva-y-acciones.md)

## Alcance

El repositorio contiene el código y los documentos técnicos que describen el sistema desarrollado y sus resultados. Los registros privados y los recursos de ejecución propios de la VM se mantienen fuera del código fuente. Las ampliaciones no implementadas no se presentan como funcionalidades terminadas.
