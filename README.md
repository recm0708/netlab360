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

**Estado actualizado de S06 (23/11/2026):** **70 % técnico estimado** (estimación de avance, no calificación académica). En VM real se verificaron **60 ventanas NORMAL** (120 ICMP), 2 modelos IsolationForest exploratorios por ruta y regla P95, además de un primer experimento controlado sobre `nl360-s02-h-hq-120/eth0` con 4 ventanas DEGRADED (RTT 40.440 ms) y 6 RECOVERY (RTT 0.070 ms), recuperación automática `RESTORED`/qdisc `noqueue`, cleanup `NONE` y red administrativa intacta. Las cuatro capturas **S06_F01–S06_F04** ya fueron revisadas como evidencias académicas. **S06-043 ejecutado**: tres ciclos adicionales sobre el mismo cliente existente, watchdogs RESTORED, 12 DEGRADED nuevas y 18 RECOVERY nuevas; acumulado **60 NORMAL, 16 DEGRADED y 24 RECOVERY (100 ventanas)**. F05 también revisada y aprobada. **S06-044 aceptado en VM:** evaluación binaria REAL con holdout por sesión, 23 tests específicos correctos, TRAIN 40 NORMAL + 12 DEGRADED y TEST 20 NORMAL + 4 DEGRADED por ruta, seis RECOVERY en análisis posincidente; **LogisticRegression alcanzó F1=1.000, TP=4, FP=0, TN=20, FN=0 en cada ruta**, P95/IsolationForest tuvieron falsas alarmas NORMAL. Ningún método marcó RECOVERY como degradado. Captura **F06 revisada y aprobada**; `S06-044_EVALUACION_VALIDADA=OK` / `RESULTADO_RC=0`, 21 namespaces/4 contenedores, gestión y NOC intactos. Resultado **exploratorio**, sin holdout global cronológico, con solo cuatro positivos por ruta y retardo fijo de 40 ms; no autoriza producción ni generalización. Próximo incremento: análisis de errores, inferencia exclusivamente de lectura, UNKNOWN y visualización NOC. **No crear dummy, nuevas veth ni namespaces S06**. El punto exacto de reanudación (identificadores, rutas de bitácoras, capturas y pendientes) se conserva en [§4.15 del plan maestro](docs/diseno/s06-s08-plan-maestro-y-criterios.md).

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
- [Diseño del programa interactivo S08 y catálogo de acciones](docs/diseno/s08-consola-interactiva-y-acciones.md)

## Alcance

El repositorio contiene el código y los documentos técnicos que describen el sistema desarrollado y sus resultados. Los registros privados y los recursos de ejecución propios de la VM se mantienen fuera del código fuente. Las ampliaciones no implementadas no se presentan como funcionalidades terminadas.
