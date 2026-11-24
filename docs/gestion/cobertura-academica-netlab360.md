# Cobertura académica y criterios de aceptación de NETLAB360

## Alcance

Este documento relaciona los contenidos académicos de Tópicos Especiales II con las funcionalidades propias de NETLAB360 y establece los criterios de seguimiento para las fases restantes.

Los materiales docentes, los laboratorios individuales y el parcial constituyen referencias metodológicas. Sus datos, configuraciones y resultados no se presentan como mediciones propias de NETLAB360.

## Criterios académicos de entrega

- Informe académico acumulativo de al menos 40 páginas.
- Redacción técnica propia, organizada y sustentada mediante resultados verificables.
- Citas y referencias conforme a APA 7 y al formato institucional aplicable.
- Figuras y tablas contextualizadas mediante su interpretación técnica.
- Presentación PowerPoint derivada del informe.
- Demostración en vivo de los componentes implementados.
- Archivo TAR técnico independiente, conforme a la modalidad registrada para NETLAB360.
- El informe termina en Referencias, sin capítulo de anexos.
- El paquete técnico debe contener únicamente recursos pertinentes del proyecto, sin credenciales, datos personales, archivos temporales ni materiales docentes ajenos.
- La obligatoriedad de entregar una OVA continúa pendiente de confirmación docente.

El título comunicado para el proyecto es «Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede».

## Estructura del informe

El documento comprende portada, introducción, objetivos, planteamiento del problema, fundamento técnico, diseño, implementación, pruebas, análisis de resultados, conclusiones, recomendaciones y referencias.

Las comprobaciones deben identificar las condiciones iniciales, el estímulo experimental, el resultado observado, la recuperación y las limitaciones correspondientes.

## Convenciones editoriales

La documentación se redacta desde la perspectiva del equipo del proyecto, con terminología técnica precisa y una distinción explícita entre diseño, implementación, validación y planificación.

Cada resultado identifica las condiciones del ensayo, el comportamiento observado, su interpretación y sus limitaciones. Las pruebas automatizadas no sustituyen las demostraciones operativas.

Se mantiene un único informe académico acumulativo. La numeración de figuras del informe es independiente de los identificadores de las capturas.

Los documentos técnicos se organizan por función, evitando duplicar cronologías, estados de avance y procedimientos.

## Matriz de cobertura académica — línea base S06

La planificación semestral del 17 de agosto de 2026 comprende cuatro módulos y dieciséis capítulos. Se contrastaron los materiales individuales disponibles I–XII, las guías publicadas de laboratorios 1–4 y 6–8, el parcial 1 y la guía de proyecto final. Para XIII–XVI se utiliza el programa oficial: sus documentos individuales y la guía del laboratorio 5 no se localizaron en esta revisión. La numeración de las actividades publicadas no coincide necesariamente con el cronograma inicial.

| Capítulo | Competencias | Estado acreditado al cierre S06 | Destino |
|---|---|---|---|
| I | SoT, estado deseado, drift, convergencia e intención | OSPF y reconciliación FRR comprobados; intención integral parcial | S07 |
| II | OpenTofu, HCL, módulos, providers, state, locking y lifecycle | Metadatos locales; recursos externos, backend remoto y WireGuard no demostrados | S09 condicionada (#17, #24) |
| III | Ansible, roles, idempotencia, compliance y multivendor | FRR validado; VyOS y multivendor no demostrados | S07/S09 |
| IV | NetDevOps, CI/CD, GitOps, Policy as Code | Git y CI comprobados; reconciliación continua GitOps y autorización integral pendientes | S07/S08; ampliación S09 |
| V | gNMI, OpenConfig, gRPC, Protobuf, suscripciones | Adquisición periódica comprobada; streaming real no demostrado | S09 |
| VI | Prometheus, señales, SLI/SLO, error budget y burn rate | Exporter, NOC, TSDB, SQLite y SLI experimental comprobados; ampliar observación del servicio | S08/S09 |
| VII | Dependencias híbridas, Kubernetes, Cilium, Hubble y eBPF | WAN/servicios multisede comprobados; cloud-native no demostrado | S09 |
| VIII | Fuentes, esquemas, timestamps, calidad, ventanas y leakage | Estudio ICMP V2 experimental; fuentes heterogéneas y nuevas características ampliables | S07/S09 |
| IX | Reglas, ML supervisado/no supervisado y evaluación | P95, Isolation Forest y regresión logística en ICMP; alcance experimental | S07 |
| X | Anomalías, contexto y errores de detección | Detección controlada y análisis retrospectivo; no toda anomalía confirma incidente | S07/S09 |
| XI | Predicción, capacidad, QoE, incertidumbre | Pronóstico futuro y MAE prospectivo no demostrados | S09 |
| XII | Generalización, explicabilidad y deriva | Separación cronológica y análisis descriptivo; explicabilidad y concept drift inferencial limitados/no demostrados | S07/S09 |
| XIII | Correlación temporal/topológica/contextual y RCA | Señales disponibles; correlación sistemática y priorización pendientes | S07 |
| XIV | LLM, RAG, grounding y copilotos | No demostrado; recuperación documental y generación evaluada pendientes | S07/S08 |
| XV | AIOps, orquestación, agentes y human-in-the-loop | Guardas y rollback acotados existentes; ciclo integral pendiente | S07/S08 |
| XVI | Integración, aceptación, confiabilidad y riesgo | S01–S06 cerradas; ciclo extremo a extremo y arranque frío pendientes | S08, o aceptación final tras S09 si se aprueba |

### Guías prácticas contrastadas

Laboratorio 1: intención y diferenciación de drift/falla. Laboratorio 2: recursos reales, WireGuard y locking. Laboratorio 3: FRR/VyOS e idempotencia. Laboratorio 4: Blackbox, Grafana, SLI/SLO y burn rate. Laboratorio 6: incidentes, RFC, separación de responsabilidades y runbooks; reserva de TEST. Laboratorio 7: Isolation Forest y contexto histórico. Laboratorio 8: pronóstico a diez minutos, MAE, costo y cambio QoS. Parcial 1: integración OSPF con Kubernetes/Cilium/Hubble. Los resultados de esas prácticas no se atribuyen a NETLAB360.

## Estado técnico de referencia

Las fases S01–S06 se encuentran cerradas. La plataforma dispone de enrutamiento multisede, segmentación VLAN, automatización declarativa, observabilidad, LACP, disponibilidad lógica HTTP, SDN y detección experimental de anomalías.

El estudio V2 utiliza particiones cronológicas independientes, modelos congelados y un protocolo uniforme de medición ICMP. La falla HTTP fue evaluada como escenario independiente. No se atribuye a los resultados capacidad de pronóstico futuro, generalización automática entre protocolos ni remediación autónoma.

## Planificación de las fases restantes

S07 desarrollará la operación inteligente supervisada mediante correlación de eventos, diagnóstico, recomendación, aprobación humana, ejecución autorizada, comprobación y rollback.

S08 consolidará la aplicación interactiva, las pruebas reproducibles, el copiloto generativo RAG (#198), la recuperación operativa y la preparación de la entrega según el alcance aprobado. S07 se controla mediante #7 y #190–#197.

La eventual S09 constituye una ampliación condicionada, no una fase aprobada ni implementada. Su necesidad se determinará después de revisar esta matriz al cierre de S07 y S08.

Las tecnologías adicionales deberán responder a un caso de uso propio, contar con recursos suficientes y conservar el aislamiento de la red administrativa.

## Decisión condicionada de ampliación S09

Reevaluar esta matriz al cierre de S07 y S08. No se crea milestone S09 ni se trasladan #17/#24 hasta aprobar alcance, recursos, calendario y valor académico. S08 sigue siendo la entrega comprometida; si S09 se incorpora formalmente al proyecto, la aceptación y empaquetado finales se programarán después de su validación. De lo contrario, S09 será una ampliación posterior.

| Grupo candidato | Prueba requerida |
|---|---|
| IaC y multivendor | Provider real, módulos, data source, ownership, lifecycle, locking, WireGuard y VyOS en recursos aislados |
| GitOps | Reconciliación periódica del estado deseado con autorización y control de cambios |
| Streaming | Suscripciones gNMI/OpenConfig con timestamps, calidad y trazabilidad |
| Observabilidad | Sondas Blackbox, Grafana, Alertmanager, burn rate de servicio y trazas OpenTelemetry cuando proceda |
| Cloud-native | Kubernetes, Cilium, Hubble, eBPF y políticas de flujo verificadas en dominio separado |
| Analítica | Nuevos escenarios y características, pronóstico temporal con MAE, evaluación de QoS/QoE, deriva con etiquetas independientes y explicabilidad |
| Rendimiento | TCP/UDP, pérdida, jitter y capacidad experimental con límites de carga |

Estas capacidades son candidatas, no compromisos de implementación ni resultados demostrados. No es obligatorio incorporar cada herramienta del programa si no resuelve el problema del proyecto.

## Preparación del paquete técnico y demostración

El TAR reunirá configuraciones declarativas, inventarios, scripts, servicios, pruebas reproducibles, registros técnicos pertinentes y evidencias seleccionadas.

Incluirá un README con dependencias, versiones, compatibilidad y orden de ejecución. El paquete se preparará en un directorio independiente y se verificará mediante listado de contenidos y extracción de prueba.

Se excluyen credenciales, llaves privadas, tokens, estados sensibles de infraestructura, entornos virtuales Python completos, cachés, archivos personales y materiales docentes originales.

La demostración deberá acreditar el estado inicial, la intervención controlada, el resultado observado y la restauración. La reconstrucción automática después de apagar la VM continúa pendiente de validación.

## Revisión y aceptación

Cada tecnología se clasificará según su evidencia real: implementada y validada, parcial, experimental, limitada, condicionada o no demostrada.

La ampliación de funcionalidades exige pruebas independientes y no modifica retroactivamente los resultados alcanzados.

[Plan maestro y criterios técnicos](../diseno/s06-s08-plan-maestro-y-criterios.md).
