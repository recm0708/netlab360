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

| Capítulo | Competencias | Estado acreditado al cierre de la fase 7 | Brecha y destino planificado | Demostración prevista en fase 8 |
|---|---|---|---|---|
| I | Redes automatizadas, SoT, intención, drift y convergencia | Validado en alcance delimitado: IPAM, OSPF, reconciliación, ocho costos y RFC protegido | Fase 08 #209/#210: integración de intención y RFC; ampliar solo con ejecutores validados | Inventario, FIB, vecinos, comparación deseado/observado y restauración |
| II | OpenTofu/Terraform, HCL, módulos, providers, state, locking, lifecycle | Limitado: 17 recursos locales terraform_data e idempotencia; no aprovisionamiento externo | Fase 09 #17/#24: recursos reales, módulos, backend, locking, lifecycle y VPN | Evidencia de plan sin cambios y estado declarativo; despliegue fuera del navegador |
| III | Ansible, roles, compliance, idempotencia, multivendor | Validado para FRR; auditoría y reconciliación selectiva | Fase 09 #213: automatización multivendor FRR/VyOS | Informe de cumplimiento y evidencia de reconciliación; no playbook arbitrario |
| IV | NetDevOps, CI/CD, GitOps, Policy as Code | Parcial: Git, CI, política RFC, autorización y auditoría verificados | Fase 09 #214: reconciliación GitOps periódica autorizada | Historial de validaciones, política y solicitudes; CI en segundo plano |
| V | Streaming Telemetry, gNMI, OpenConfig, gRPC, Protobuf | Limitado a adquisición periódica, contrato normalizado y control de vigencia | Fase 09 #215: suscripción gNMI/OpenConfig y gRPC/Protobuf | Series y calidad de fuentes; no rotular polling como streaming |
| VI | Observabilidad, Prometheus, SLI/SLO, error budget, burn rate | Parcial: exportador, TSDB, alertas, NOC, SQLite y SLI de recopilación (97,586 % en 60 min frente a 99 % candidato) | Fase 08 #207/#208: SLI de servicio, error budget, burn rate y alertas | Panel de métricas e incidentes, fuente UNKNOWN y ventana histórica |
| VII | Observabilidad híbrida y cloud-native | Parcial: servicios multisede virtualizados; Docker no equivale a Kubernetes | Fase 09 #216/#217: Kubernetes, Cilium, Hubble, eBPF y OpenTelemetry | Topología y servicios existentes; no mostrar clúster ficticio |
| VIII | Ingeniería de datos, esquemas, calidad, ventanas, leakage | Experimental validado: ICMP V2 cronológico; contrato de 58 señales, persistencia y vigencia en fase 7 | Fase 10 #219: sesiones independientes e ingeniería de características | Dataset, particiones, procedencia y brechas de cobertura |
| IX | Fundamentos IA/ML, reglas, aprendizaje supervisado y no supervisado | Experimental validado: P95, Isolation Forest y regresión logística, cuatro modelos congelados | Fase 10 #220: evaluación y comparación de modelos | Comparación TEST histórica e inferencia actual de solo lectura |
| X | Detección de anomalías y contexto | Experimental: degradaciones ICMP, contexto RCA, abstención y controles negativos | Fase 10 #223: anomalías, controles negativos y contexto RCA | Diagnóstico, score, evidencia y UNKNOWN; HTTP independiente de ML ICMP |
| XI | Predicción de degradación, capacidad y QoE | No demostrada prospectivamente | Fase 10 #221/#222: predicción prospectiva, MAE y QoS/QoE | Solo mediciones actuales e históricas; pronóstico no disponible |
| XII | Evaluación, explicabilidad y concept drift | Parcial: evaluación cronológica, límites, evidencia RCA e incertidumbre | Fase 10 #220: explicabilidad ML y concept drift | Métricas TEST, explicación de reglas y evidencia RCA; no confundir drift OSPF con concept drift |
| XIII | Correlación temporal, topológica y contextual; RCA | Validado experimentalmente: 18 contextos, cinco escenarios, 15 ventanas seleccionadas, 870 observaciones no independientes, 11 hipótesis y recomendaciones coincidentes | Fase 08 #209 y fase 10 #223: integración y evaluación ampliada | Línea de tiempo, evidencias favorables/contradictorias/desconocidas, hipótesis, runbooks y abstención |
| XIV | LLM, RAG, grounding y copilotos | Parcial: recuperación léxica de corpus propio; no RAG generativo validado | Fase 08 #198: copiloto RAG generativo fundamentado | Consulta con citas, evidencia insuficiente, evaluación y controles de inyección; sin privilegios |
| XV | AIOps, orquestación, agentes y human-in-the-loop | Validado en alcance supervisado: ciclo RFC real, API Unix, aprobación, idempotencia, watchdog y postcondiciones | Fase 08 #210: integración de RFC y ejecución protegida | Solicitud, aprobación administrativa separada, ejecución acotada, retorno y auditoría |
| XVI | Integración extremo a extremo, aceptación, confiabilidad y riesgo | Parcial: ciclo técnico integrado y 1258 casos (uno omitido, cero fallos); reconstrucción manual demostrada | Fase 08 #106/#211 y fase 10 #224: recuperación y aceptación integral | Secuencia de extremo a extremo, evidencia y recuperación comprobada |

### Guías prácticas contrastadas

Laboratorio 1: intención y diferenciación de drift/falla. Laboratorio 2: recursos reales, WireGuard y locking. Laboratorio 3: FRR/VyOS e idempotencia. Laboratorio 4: Blackbox, Grafana, SLI/SLO y burn rate. Laboratorio 6: incidentes, RFC, separación de responsabilidades y runbooks; reserva de TEST. Laboratorio 7: Isolation Forest y contexto histórico. Laboratorio 8: pronóstico a diez minutos, MAE, costo y cambio QoS. Parcial 1: OSPF con Kubernetes/Cilium/Hubble. No atribuimos resultados de esas prácticas al proyecto.

## Matriz tecnológica y ampliaciones

La prioridad distingue brechas académicas y dependencias técnicas. La planificación interna de las fases 08–10 está aprobada, sin convertirla en una exigencia docente adicional. Los estados acreditados de esta matriz corresponden al cierre de la fase 07; la auditoría funcional posterior se documenta por separado.

| Tecnología o capacidad | Estado al cierre de fase 7 | Ampliación o criterio de aceptación | Destino planificado | Prioridad |
|---|---|---|---|---|
| OpenTofu | Limitado a metadatos locales | Provider real, módulos, data sources, lifecycle, locking y recursos aislados | Fase 09 #17 | Alta |
| WireGuard | No demostrado | Túnel multisede aislado, alcance y conectividad comprobados | Fase 09 #24 | Alta |
| Ansible multivendor | FRR validado | VyOS, auditoría e idempotencia multivendor | Fase 09 #213 | Media |
| GitOps | CI y reconciliación controlada | Reconciliación periódica autorizada y auditada | Fase 09 #214 | Alta |
| gNMI/OpenConfig | No demostrado | Suscripción real con calidad, timestamps y trazabilidad | Fase 09 #215 | Alta |
| gRPC/Protocol Buffers | No demostrado | Adquisición estructurada real y validación de esquema | Fase 09 #215 | Media |
| Blackbox Exporter | No acreditado | Sondas HTTP/TCP/ICMP independientes | Fase 08 #207 | Alta |
| Grafana | No acreditado | Dashboard especializado con datos reales; evitar duplicar NOC | Fase 08 #208; evaluación especializada | Media |
| Alertmanager | No demostrado | Agrupación, distribución y recepción comprobadas | Fase 08 #208 | Alta |
| OpenTelemetry | No demostrado | Correlación de métricas y trazas HTTP | Fase 09 #217 | Media |
| Kubernetes | No demostrado | Servicios cloud-native en dominio aislado | Fase 09 #216 | Media |
| Cilium/Hubble/eBPF | No demostrado | Flujos reales y NetworkPolicy comprobada | Fase 09 #216 | Media |
| ML | Experimental ICMP | Nuevas características, etiquetas y sesiones independientes | Fase 08 #209; ampliación fase 10 #219/#220 | Alta |
| Predicción temporal | No demostrada | Horizonte explícito y evaluación prospectiva sin leakage | Fase 10 #221 | Alta |
| MAE | No evaluado prospectivamente | Comparar pronósticos congelados con observaciones futuras | Fase 10 #221 | Alta |
| QoS/QoE | Limitado | Priorización controlada y métricas de experiencia del servicio | Fase 10 #222 | Alta |
| Concept drift | No demostrado inferencialmente | Cambios de contexto y etiquetas independientes | Fase 10 #220 | Alta |
| Explicabilidad ML | Parcial; RCA explicable no equivale a explicar modelos | Contribución de variables y justificación verificable | Fase 10 #220 | Alta |
| Evaluación TCP/UDP | Parcial; ensayos TCP previos | Pruebas acotadas iperf3 TCP/UDP, pérdida, jitter y tasa observada | Fase 08 #206; ampliación fase 10 #222 | Alta |
| RCA y runbooks | Validados experimentalmente | Integración visual y cobertura SDN adicional si se valida | Fase 08 #209; ampliación fase 10 #223 | Alta |
| RAG generativo | Pendiente | Citas fieles, abstención, relevancia, seguridad y evaluación real | Fase 08 #198 | Alta |
| Intent/RFC/API/watchdog | Validados en alcance fijo | Integración con aprobación externa y pruebas de regresión | Fase 08 #210 | Alta |
| Reconstrucción automática | Manual comprobada; automática pendiente | Arranque frío y postcondiciones integrales verificadas | Fase 08 #106 | Alta |

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

Las fases 01–07 están cerradas dentro de su alcance acreditado.
Conservamos 253 capturas oficiales, 49 de la fase 07, y el informe
acumulativo 7.3. La regresión histórica de aceptación de la
fase 07 comprendió 1258 casos, uno omitido y cero fallos.

La fase 08 integra plataforma interactiva, pruebas de servicio,
observabilidad avanzada, RAG, intervenciones supervisadas y
recuperación automática. La fase 09 amplía la cobertura
tecnológica y la fase 10 desarrolla la evaluación científica,
aceptación integral y entrega definitiva.

Las tres fases cuentan con milestones propias y las issues
maestras #8, #212 y #218. La aprobación interna no implica
que sus capacidades estén implementadas ni que la docente
haya exigido individualmente cada ampliación.

La recuperación documental de la fase 07 es léxica y no
constituye RAG generativo validado. Tampoco acredita remediación
autónoma, pronóstico futuro, generalización entre protocolos,
separación organizacional de personas ni tolerancia a la pérdida
de la máquina virtual. La recuperación manual tras reinicio no
equivale a reconstrucción automática desde apagado completo.

## Inventario y comprobación funcional previa

Comprobamos el entorno antes de iniciar la implementación.
Registramos las siguientes capacidades disponibles y sus límites:

| Componente | Resultado observado | Implicación |
|---|---|---|
| Infraestructura | 8 vCPU, 15 GiB RAM reconocidos, 130 GiB de almacenamiento disponible | Base para la fase 08; reevaluar recursos antes de ampliaciones |
| Red administrativa | 192.168.47.40/24, gateway 192.168.47.2 | Plano de gestión protegido |
| Topología | 21 namespaces, cuatro contenedores y siete servicios activos | Infraestructura existente conservada |
| OSPF | Ocho adyacencias Full, ocho costos conformes y seis selecciones FIB primarias | Configuración conforme; no acredita medición continua de tráfico |
| HTTP HA | Tres respuestas HTTP 200; HQ como backend activo | Estado funcional observado |
| LACP | Dos miembros activos por cada sede | No constituye medición de throughput efectivo |
| SDN | Faucet conectado; A-B permitido y B-C aislado | Plano de datos funcional en los extremos probados |
| Observabilidad | Prometheus 3.7.0, target UP, cuatro reglas saludables, NOC 18 nodos y 21 enlaces | No se detectaron Alertmanagers activos |
| Automatización | Ansible Core 2.20.1 con colecciones multivendor; OpenTofu 1.13.9 | Disponibilidad de herramientas, no acreditación de nuevas integraciones |
| Desarrollo | Python 3.14.4, FastAPI, Plotly, Dash y bibliotecas ML importables | Dependencias consistentes mediante pip check |
| WireGuard | Módulo del kernel disponible | Túneles aún no implementados |
| eBPF | BTF y herramientas de inspección disponibles | Kubernetes/Cilium/Hubble aún no implementados |
| VyOS | No se detectó virtualización anidada ni dispositivo KVM | Evaluar arquitectura independiente |
| Arranque | Prometheus transitorio y cuatro servicios HA activos sin autoinicio | Reconstrucción automática pendiente de validación |

Estas observaciones proceden de comprobaciones puntuales de
nuestra infraestructura. No sustituyen los ensayos de aceptación
de las fases futuras ni modifican las conclusiones científicas
históricas.

## Extensión de la matriz de demostración

| Bloque | Fase | Presentación prevista |
|---|---|---|
| Observabilidad de servicio | 08 | Sondas, SLI/SLO, burn rate, alertas y evidencia de notificación |
| Paneles especializados | 08 | Evaluación de Grafana sin duplicar el NOC |
| Automatización avanzada | 09 | Estado OpenTofu, cumplimiento multivendor y reconciliación GitOps |
| VPN | 09 | Estado, conectividad, cifrado y retorno verificados |
| Streaming telemetry | 09 | Suscripciones, vigencia, esquemas y eventos reales |
| Cloud-native | 09 | Salud del clúster, políticas, flujos y observación eBPF |
| Trazabilidad | 09 | Solicitudes y trazas correlacionadas |
| Validación científica | 10 | Modelos, resultados independientes, MAE, deriva y explicabilidad |
| Capacidad y calidad | 10 | Comparación TCP/UDP, QoS y métricas QoE delimitadas |
| Aceptación final | 10 | Regresión, demostración integrada, recuperación y entrega |

Cada extensión aparecerá como pendiente hasta disponer de
una implementación y evidencias propias verificables.

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

## Actualización de cobertura de la consola

Al 25 de noviembre de 2026, la consola integra observaciones por sede, topología resumida y detallada, estados WAN/VLAN/HA/LACP/SDN, históricos y alertas consultadas, temas y explorador de API con Swagger. Validamos 204 pruebas específicas y consultas reales en navegador. No se acredita todavía disponibilidad extremo a extremo mediante las observaciones administrativas, ni ingestión continua de alertas, diagnóstico activo, SLI de servicio, RAG generativo, intervención desde la consola o MFA. Estos aspectos permanecen sujetos a sus criterios de aceptación.
