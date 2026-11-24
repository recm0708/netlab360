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

## Matriz de cobertura académica — cierre de la fase 7

Corte: 24 de noviembre de 2026. Contrastamos la planificación semestral de cuatro módulos y dieciséis capítulos, los materiales individuales I–XII disponibles, las guías 1–4 y 6–8, el parcial 1 y la guía final. XIII–XVI se clasifican según el programa oficial: no se localizaron sus documentos individuales ni la guía del laboratorio 5. La matriz distingue alcance técnico acreditado, brechas y destino propuesto; no certifica cumplimiento de todos los contenidos del semestre. El informe acumulativo 7.3 (184 páginas, 42 figuras, 19 tablas y 19 referencias) incorpora los resultados hasta la fase 7; la revisión final de paginación se reserva para la entrega. No se publica el PDF con datos personales.

| Capítulo | Competencias | Estado acreditado al cierre de la fase 7 | Brecha o destino | Demostración prevista en fase 8 |
|---|---|---|---|---|
| I | Redes automatizadas, SoT, intención, drift y convergencia | Validado en alcance delimitado: IPAM, OSPF, reconciliación, ocho costos y RFC protegido | Ampliable a otras intenciones | Inventario, FIB, vecinos, comparación deseado/observado y restauración |
| II | OpenTofu/Terraform, HCL, módulos, providers, state, locking, lifecycle | Limitado: 17 recursos locales terraform_data e idempotencia; no aprovisionamiento externo | Provider, módulos, backend remoto, locking compartido y WireGuard: candidatos #17/#24 | Evidencia de plan sin cambios y estado declarativo; despliegue fuera del navegador |
| III | Ansible, roles, compliance, idempotencia, multivendor | Validado para FRR; auditoría y reconciliación selectiva | VyOS/multivendor no demostrados | Informe de cumplimiento y evidencia de reconciliación; no playbook arbitrario |
| IV | NetDevOps, CI/CD, GitOps, Policy as Code | Parcial: Git, CI, política RFC, autorización y auditoría verificados | GitOps de reconciliación continua no demostrado | Historial de validaciones, política y solicitudes; CI en segundo plano |
| V | Streaming Telemetry, gNMI, OpenConfig, gRPC, Protobuf | Limitado a adquisición periódica, contrato normalizado y control de vigencia | Streaming y modelos de datos específicos no demostrados | Series y calidad de fuentes; no rotular polling como streaming |
| VI | Observabilidad, Prometheus, SLI/SLO, error budget, burn rate | Parcial: exportador, TSDB, alertas, NOC, SQLite y SLI de recopilación (97,586 % en 60 min frente a 99 % candidato) | SLI de servicio, burn rate, notificaciones y fuentes adicionales por validar | Panel de métricas e incidentes, fuente UNKNOWN y ventana histórica |
| VII | Observabilidad híbrida y cloud-native | Parcial: servicios multisede virtualizados; Docker no equivale a Kubernetes | Kubernetes, Cilium, Hubble y eBPF no demostrados | Topología y servicios existentes; no mostrar clúster ficticio |
| VIII | Ingeniería de datos, esquemas, calidad, ventanas, leakage | Experimental validado: ICMP V2 cronológico; contrato de 58 señales, persistencia y vigencia en fase 7 | Más sesiones independientes y características | Dataset, particiones, procedencia y brechas de cobertura |
| IX | Fundamentos IA/ML, reglas, aprendizaje supervisado y no supervisado | Experimental validado: P95, Isolation Forest y regresión logística, cuatro modelos congelados | Generalización no demostrada | Comparación TEST histórica e inferencia actual de solo lectura |
| X | Detección de anomalías y contexto | Experimental: degradaciones ICMP, contexto RCA, abstención y controles negativos | Más fallas y evaluación independiente; no extrapolar tasa de error | Diagnóstico, score, evidencia y UNKNOWN; HTTP independiente de ML ICMP |
| XI | Predicción de degradación, capacidad y QoE | No demostrada prospectivamente | Pronóstico temporal, MAE y QoS/QoE candidatos | Solo mediciones actuales e históricas; pronóstico no disponible |
| XII | Evaluación, explicabilidad y concept drift | Parcial: evaluación cronológica, límites, evidencia RCA e incertidumbre | Explicabilidad ML y deriva inferencial con etiquetas independientes | Métricas TEST, explicación de reglas y evidencia RCA; no confundir drift OSPF con concept drift |
| XIII | Correlación temporal, topológica y contextual; RCA | Validado experimentalmente: 18 contextos, cinco escenarios, 15 ventanas seleccionadas, 870 observaciones no independientes, 11 hipótesis y recomendaciones coincidentes | Cobertura individual de puertos SDN y escenarios independientes | Línea de tiempo, evidencias favorables/contradictorias/desconocidas, hipótesis, runbooks y abstención |
| XIV | LLM, RAG, grounding y copilotos | Parcial: recuperación léxica de corpus propio; no RAG generativo validado | Fase 8 #198 | Consulta con citas, evidencia insuficiente, evaluación y controles de inyección; sin privilegios |
| XV | AIOps, orquestación, agentes y human-in-the-loop | Validado en alcance supervisado: ciclo RFC real, API Unix, aprobación, idempotencia, watchdog y postcondiciones | Integrar consola; no autonomía ni shell libre | Solicitud, aprobación administrativa separada, ejecución acotada, retorno y auditoría |
| XVI | Integración extremo a extremo, aceptación, confiabilidad y riesgo | Parcial: ciclo técnico integrado y 1258 casos (uno omitido, cero fallos); reconstrucción manual demostrada | Consola, RAG, arranque frío automático, regresión y entrega fase 8 | Secuencia de extremo a extremo, evidencia y recuperación comprobada |

### Guías prácticas contrastadas

Laboratorio 1: intención y diferenciación de drift/falla. Laboratorio 2: recursos reales, WireGuard y locking. Laboratorio 3: FRR/VyOS e idempotencia. Laboratorio 4: Blackbox, Grafana, SLI/SLO y burn rate. Laboratorio 6: incidentes, RFC, separación de responsabilidades y runbooks; reserva de TEST. Laboratorio 7: Isolation Forest y contexto histórico. Laboratorio 8: pronóstico a diez minutos, MAE, costo y cambio QoS. Parcial 1: OSPF con Kubernetes/Cilium/Hubble. No atribuimos resultados de esas prácticas al proyecto.

## Matriz tecnológica y ampliaciones

Prioridad propuesta: alta = brecha académica relevante o dependencia de la demostración; media = extensión útil condicionada. No implica aprobación ni obligación de instalar herramientas. Validado significa evidencia previa, no comprobación en vivo de la VM suspendida.

| Tecnología o capacidad | Estado al cierre de fase 7 | Ampliación o criterio de aceptación | Destino propuesto | Prioridad |
|---|---|---|---|---|
| OpenTofu | Limitado a metadatos locales | Provider real, módulos, data sources, lifecycle, locking y recursos aislados | #17 / eventual fase 9 | Alta |
| WireGuard | No demostrado | Túnel multisede aislado, alcance y conectividad comprobados | #24 / eventual fase 9 | Alta |
| Ansible multivendor | FRR validado | VyOS, auditoría e idempotencia multivendor | Eventual fase 9 | Media |
| GitOps | CI y reconciliación controlada | Reconciliación periódica autorizada y auditada | Eventual fase 9 | Alta |
| gNMI/OpenConfig | No demostrado | Suscripción real con calidad, timestamps y trazabilidad | Eventual fase 9 | Alta |
| gRPC/Protocol Buffers | No demostrado | Adquisición estructurada real y validación de esquema | Eventual fase 9 | Media |
| Blackbox Exporter | No acreditado | Sondas HTTP/TCP/ICMP independientes | Evaluar en fase 8; ampliación condicionada | Alta |
| Grafana | No acreditado | Dashboard especializado con datos reales; evitar duplicar NOC | Ampliación condicionada | Media |
| Alertmanager | No demostrado | Agrupación, distribución y recepción comprobadas | Ampliación condicionada | Alta |
| OpenTelemetry | No demostrado | Correlación de métricas y trazas HTTP | Eventual fase 9 | Media |
| Kubernetes | No demostrado | Servicios cloud-native en dominio aislado | Eventual fase 9 | Media |
| Cilium/Hubble/eBPF | No demostrado | Flujos reales y NetworkPolicy comprobada | Eventual fase 9 | Media |
| ML | Experimental ICMP | Nuevas características, etiquetas y sesiones independientes | Mostrar fase 8; ampliar condicionalmente | Alta |
| Predicción temporal | No demostrada | Horizonte explícito y evaluación prospectiva sin leakage | Eventual fase 9 | Alta |
| MAE | No evaluado prospectivamente | Comparar pronósticos congelados con observaciones futuras | Eventual fase 9 | Alta |
| QoS/QoE | Limitado | Priorización controlada y métricas de experiencia del servicio | Eventual fase 9 | Alta |
| Concept drift | No demostrado inferencialmente | Cambios de contexto y etiquetas independientes | Eventual fase 9 | Alta |
| Explicabilidad ML | Parcial; RCA explicable no equivale a explicar modelos | Contribución de variables y justificación verificable | Mostrar límites fase 8; ampliar condicionalmente | Alta |
| Evaluación TCP/UDP | Parcial; ensayos TCP previos | Pruebas acotadas iperf3 TCP/UDP, pérdida, jitter y tasa observada | Fase 8 #8/#44 | Alta |
| RCA y runbooks | Validados experimentalmente | Integración visual y cobertura SDN adicional si se valida | Fase 8; ampliación condicionada | Alta |
| RAG generativo | Pendiente | Citas fieles, abstención, relevancia, seguridad y evaluación real | Fase 8 #198 | Alta |
| Intent/RFC/API/watchdog | Validados en alcance fijo | Integración con aprobación externa y pruebas de regresión | Fase 8 #8 | Alta |
| Reconstrucción automática | Manual comprobada; automática pendiente | Arranque frío y postcondiciones integrales verificadas | Fase 8 #106 | Alta |

## Integración y demostración mediante la consola

La aplicación presentará resultados reales sin exigir que todas las herramientas tengan botones propios. Distinguimos visualización en vivo, pruebas interactivas controladas, evidencia histórica y funciones de segundo plano. Las funciones pendientes no se muestran como operativas.

| Bloque | Visible en la consola | Segundo plano / evidencia | Criterio de demostración |
|---|---|---|---|
| Infraestructura | Salud, sedes, inventario y topología | VMware, Ubuntu, Docker, namespaces, veth, bridges | Inventario actual y conectividad administrativa intacta |
| WAN/OSPF/FIB | Vecinos, costos, ruta principal/respaldo | FRR y protocolos de enrutamiento | Cambio de ruta real y retorno, sin confundir FIB con tráfico medido |
| LAN/VLAN/ACL | Segmentos, origen/destino y resultados de pruebas | Linux bridge, nftables y subinterfaces | Comunicación permitida/denegada; recrear ACL temporal solo con procedimiento aceptado |
| HTTP HA | Backend activo, estado, latencia y errores | Frontal, dos backends y monitor | HQ → S1 → HQ con solicitudes reales |
| LACP | Miembros por extremo y estado | Bonding Linux | 2 → 1 → 2, conectividad y restauración |
| SDN | Controlador, puertos cuando medidos, aislamiento | OVS/Faucet/OpenFlow | A–B permitido, A–C restringido, recuperación; no inventar cobertura RCA de puertos |
| Automatización | Inventario, cumplimiento y resultados declarativos | Ansible, OpenTofu, Git y CI | Comparar estado deseado/observado, plan/no cambios y registros reales |
| Observabilidad | Métricas, alertas, historial, vigencia y SLI | Exportadores, Prometheus, SQLite | Cambio observado y fuente UNKNOWN distinguible de falla |
| Pruebas de red | Ping, traceroute, HTTP, TCP/UDP acotados | Ejecutores permitidos y límites de carga | Medidas originales, origen/destino, ventana y resultado |
| ML | Inferencia, score, método y evaluación histórica | Modelos congelados y datos versionados por procedencia | Distinguir inferencia actual de TEST histórico y abstenerse si falta información |
| RCA/RFC | Incidentes, hipótesis, runbooks, solicitudes y auditoría | API local, broker root, políticas y watchdog | Detectar → explicar → recomendar → aprobar por canal administrativo → ejecutar → verificar → restaurar |
| Copiloto | Consulta documental con citas | Recuperación y LLM evaluado, sin permisos | Consulta fundada, caso sin evidencia y resistencia a instrucciones maliciosas |
| Evidencias y recuperación | Registros, catálogo, estado y resultados de reconstrucción | systemd, dependencias, CI, TAR y documentación | Validar recuperación integral y exportación de resultados sin datos privados |

Los escenarios de cambio del menú son propuestas hasta que cada ejecutor, política y retorno se acepte de manera específica. La fase 7 solo acredita intervención protegida sobre el costo OSPF identificado; no habilita por extensión cambios WAN, HTTP, LACP, SDN o netem desde el navegador. La aprobación administrativa se mantiene fuera del navegador salvo un mecanismo posterior expresamente validado, nunca mediante el LLM.

## Auditoría de inicio de la fase 8

Antes de modificar infraestructura, reanudar la VM y sincronizar main mediante fast-forward con árbol limpio. Verificar identidad y red administrativa, namespaces, contenedores, servicios, OSPF/FIB, HA/LACP/SDN/NOC, Prometheus, frescura de datos, integridad de SQLite, RFC no concluidas, reservas de idempotencia, watchdogs y timers. Registrar versiones, dependencias, recursos, servicios activos/inactivos y componentes instalados sin evidencia de uso. Contrastar cada brecha de esta matriz con código, configuración y prueba verificable. No reiniciar, desinstalar ni desplegar para una auditoría de solo lectura.

## Estado técnico y planificación

Las fases 1–7 están aceptadas en su alcance técnico y el informe hasta la fase 7 se revisó. La fase 8 permanece pendiente. Se conservan 253 capturas oficiales, 49 de fase 7, y la regresión de aceptación histórica de 1258 casos (uno omitido, cero fallos). La fase 7 acredita recuperación documental léxica, no generación RAG; tampoco acredita autonomía, predicción futura, generalización entre protocolos, separación organizacional de personas o tolerancia a pérdida de la VM. La recuperación manual tras reinicio no acredita reconstrucción automática.

La fase 8 integra consola, RAG, pruebas acotadas, recuperación y entregables. La fase 9 es una ampliación condicionada: no crear milestone ni trasladar #17/#24 sin decisión expresa basada en la auditoría de inicio, valor académico, recursos, calendario y aceptación de fase 8. Si se aprueba, adaptar el alcance y cronograma; si no, mantener las brechas explícitas. No atribuir a la docente aprobación no confirmada. No instalar tecnologías solo para marcar casillas.

## Preparación del paquete técnico y demostración

El TAR reunirá configuraciones declarativas, inventarios, scripts, servicios, pruebas reproducibles, registros técnicos pertinentes y evidencias seleccionadas.

Incluirá un README con dependencias, versiones, compatibilidad y orden de ejecución. El paquete se preparará en un directorio independiente y se verificará mediante listado de contenidos y extracción de prueba.

Se excluyen credenciales, llaves privadas, tokens, estados sensibles de infraestructura, entornos virtuales Python completos, cachés, archivos personales y materiales docentes originales.

La demostración deberá acreditar el estado inicial, la intervención controlada, el resultado observado y la restauración. La reconstrucción automática después de apagar la VM continúa pendiente de validación.

## Gestión de evidencias gráficas

Las capturas se obtienen y validan durante las actividades técnicas. El catálogo, la transferencia definitiva y la publicación de imágenes se consolidan en un único lote al finalizar cada fase. Las issues técnicas se cierran al cumplir sus criterios comprobados; la consolidación gráfica pendiente se controla en la issue maestra de fase y #43. No se cierra la milestone antes de validar el catálogo y la sincronización final. Se conserva la nomenclatura uniforme y se comparan directamente los contenidos de las copias.

## Revisión y aceptación

Cada tecnología se clasificará según su evidencia real: implementada y validada, parcial, experimental, limitada, condicionada o no demostrada.

La ampliación de funcionalidades exige pruebas independientes y no modifica retroactivamente los resultados alcanzados.

[Plan maestro y criterios técnicos](../diseno/s06-s08-plan-maestro-y-criterios.md).
