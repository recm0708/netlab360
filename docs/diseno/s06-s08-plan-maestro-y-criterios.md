# Plan maestro y criterios de aceptación

## Descripción

NETLAB360 estudia redes empresariales multisede dentro de una única VM Ubuntu sobre VMware, con HQ, S1 y S2 y un plano de administración separado. Este documento establece el alcance de las fases, sus dependencias y los criterios de aceptación; los resultados específicos se desarrollan en los documentos de cada componente.

## Estado técnico

| Fase | Estado | Referencia |
|---|---|---|
| Fases 01–04 | Cerradas | [Validación de infraestructura, automatización y observabilidad](../validacion/s01-s04-resultados.md) |
| Fase 05 | Cerrada | [Integración HA, LACP y SDN](../validacion/s05-integracion-y-aceptacion.md) |
| Fase 06 | Cerrada | [Protocolo uniforme V2](s06-protocolo-uniforme-v2.md) |
| Fase 07 | Cerrada; aceptación técnica y documental interna completa | [API controlada](s07-api-controlada.md) · [Ensayos](s07-ensayos-operacionales.md) |
| Fase 08 | En implementación; núcleo gráfico y explorador aceptados, equivalencia y aceptación integral pendientes | [Consola interactiva](s08-consola-interactiva-y-acciones.md) |
| Fase 09 | Planificada; pendiente de implementación | [Issue maestra #212](https://github.com/recm0708/netlab360/issues/212) |
| Fase 10 | Planificada; pendiente de experimentación y entrega | [Issue maestra #218](https://github.com/recm0708/netlab360/issues/218) |

La reconstrucción manual tras el reinicio del invitado acreditó la recuperación de componentes individuales en la fase 06; no acreditó reconstrucción automática integral. Las bibliotecas instaladas tampoco equivalen a funcionalidades implementadas.

## Fase 06 — Diagnóstico inteligente

Se evaluaron P95, Isolation Forest y regresión logística sobre dos rutas ICMP, con muestreo uniforme de tres paquetes por ventana y 140 ventanas por ruta. TRAIN, VALIDATION y TEST se separaron cronológicamente; cuatro modelos quedaron congelados antes de evaluar las particiones posteriores. El estudio previo se conserva como exploratorio.

La [evaluación final](s06-v2-evaluacion-cronologica-congelada.md) acredita F1 entre 0,941 y 1,000 en TEST, sin falsos negativos en las ocho ventanas positivas de cada ruta. La [falla HTTP independiente](s06-fault-http-hq-etiquetado-independiente.md) demuestra conmutación y recuperación del backend HQ sin modificar el conjunto ICMP. No se acredita pronóstico, MAE prospectivo, deriva de concepto inferencial ni generalización a HTTP.

Criterios: adquisición verificable, etiquetas independientes, separación cronológica, comparación con referencia determinista, inferencia de solo lectura, recuperación y limitaciones explícitas. Issues #6, #25 y #26 cerradas. [Evidencias de diagnóstico inteligente](../../evidencias/capturas/fase6/README.md).

## Fase 07 — AIOps supervisado

| Bloque | Issue | Resultado |
|---|---|---|
| Contrato de eventos | [#190](https://github.com/recm0708/netlab360/issues/190) | [Normalización y persistencia](s07-contrato-eventos-e-incidentes.md) |
| Correlación | [#191](https://github.com/recm0708/netlab360/issues/191) | [RCA e incertidumbre](s07-contexto-y-correlacion-rca.md) |
| Recomendaciones | [#192](https://github.com/recm0708/netlab360/issues/192) | [Runbooks y recuperación documental](s07-runbooks-y-recomendaciones.md) |
| Políticas | [#193](https://github.com/recm0708/netlab360/issues/193) | [Intención y aprobación](s07-intent-assurance-y-rfc.md) |
| Orquestación | [#194](https://github.com/recm0708/netlab360/issues/194) | [Preflight protegido](s07-preflight-orquestador.md) |
| Recuperación | [#195](https://github.com/recm0708/netlab360/issues/195) | [Watchdog y rollback](s07-intervencion-ospf-y-watchdog.md) |
| Evaluación | [#196](https://github.com/recm0708/netlab360/issues/196) | [Escenarios y métricas](s07-ensayos-operacionales.md) |
| API | [#197](https://github.com/recm0708/netlab360/issues/197) | [Interfaz local controlada](s07-api-controlada.md) |

Los ocho componentes están aceptados técnicamente. Se verificaron 15 ventanas seleccionadas, 870 observaciones no independientes, 11 hipótesis y recomendaciones coincidentes y un ciclo RFC integrado por API. Se conservaron 116 registros históricos y la red administrativa. Las 49 imágenes están en el [catálogo de AIOps supervisado](../../evidencias/capturas/fase7/README.md).

La autorización es determinista y no concede privilegios a un modelo generativo. UNKNOWN no autoriza cambios. El ciclo de detección, explicación, recomendación, aprobación, ejecución, verificación y restauración requiere evidencia privilegiada, acciones de alcance fijo y retorno independiente. La separación acreditada corresponde a privilegios del sistema operativo, no a personas independientes.

## Fase 08 — Integración y plataforma interactiva

Integramos las capacidades aceptadas de las fases anteriores
mediante una aplicación web local, sin atribuir funcionalidades
todavía pendientes.

| Actividad | Issue | Criterio central |
|---|---|---|
| Integración general | #8 | Plataforma funcional y aceptación de fase |
| Compatibilidad | #34 | Dependencias reproducibles y regresión |
| Recuperación automática | #106 | Reconstrucción desde apagado completo |
| Copiloto generativo | #198 | RAG fundamentado, citas y abstención |
| Arquitectura y API | #204 | FastAPI, persistencia y seguridad |
| Interfaz gráfica | #205 | Menú único y topología integrada |
| Pruebas interactivas | #206 | ICMP, HTTP, traceroute y TCP/UDP |
| Observabilidad de servicio | #207 | Blackbox, SLI/SLO, error budget y burn rate |
| Alertas y paneles | #208 | Alertmanager y evaluación de Grafana |
| Diagnóstico y contexto | #209 | ML, RCA, incidentes y runbooks |
| Intervenciones | #210 | RFC, autorización, watchdog y retorno |
| Aceptación | #211 | Regresión, seguridad y evidencias |

Cada actuación adicional sobre WAN, HTTP, LACP, SDN o netem
requiere validación individual de su ejecutor. No ampliamos
automáticamente los permisos acreditados en la fase 07.

La aceptación exige una aplicación integrada, resultados reales,
recuperación comprobada, seguridad y catálogo gráfico propio.
Consultamos el [diseño de consola](s08-consola-interactiva-y-acciones.md)
para los contratos de integración.

## Fase 09 — Ampliación tecnológica y automatización avanzada

| Actividad | Issue | Criterio central |
|---|---|---|
| Ampliación general | #212 | Integración tecnológica y aceptación |
| OpenTofu | #17 | Providers, módulos, data sources, backend, locking y lifecycle |
| WireGuard | #24 | VPN multisede, aislamiento y recuperación |
| Ansible multivendor | #213 | FRR/VyOS, compliance e idempotencia |
| GitOps periódico | #214 | Drift, reconciliación autorizada y auditoría |
| Streaming telemetry | #215 | Suscripción gNMI/OpenConfig y gRPC/Protobuf |
| Cloud-native | #216 | Kubernetes, Cilium, Hubble, eBPF y NetworkPolicy |
| Trazabilidad | #217 | OpenTelemetry y correlación de solicitudes |

El alcance está aprobado por nuestro equipo. La arquitectura
concreta de cada tecnología se seleccionará conforme a su
viabilidad, compatibilidad, recursos y seguridad.

Conservamos las tres sedes actuales como núcleo. Una cuarta
sede no constituye un requisito automático para WireGuard.
La infraestructura cloud-native debe operar en un dominio
aislado; VyOS podrá utilizar una VM independiente si resulta
necesario.

La aceptación requiere pruebas reales e integración con la
consola, sin confundir una instalación con una capacidad validada.

## Fase 10 — Validación científica, aceptación integral y entrega

| Actividad | Issue | Criterio central |
|---|---|---|
| Validación y entrega general | #218 | Aceptación integral y entregables |
| Dataset | #219 | Sesiones independientes y particiones verificables |
| Evaluación ML | #220 | Comparación, explicabilidad y concept drift |
| Predicción temporal | #221 | Horizonte definido y MAE prospectivo |
| Rendimiento y calidad | #222 | TCP/UDP, QoS e indicadores QoE |
| Diagnóstico y RCA | #223 | Ensayos independientes y controles negativos |
| Aceptación técnica | #224 | Seguridad, regresión y recuperación |
| Informe académico | #27 | Documento acumulativo y referencias |
| Evidencias | #43 | Catálogo definitivo y selección gráfica |
| Presentación | #44 | PowerPoint y demostración interactiva |
| Paquete técnico | #45 | TAR reproducible y verificado |
| Seguimiento docente | #36 / #48 | Confirmaciones académicas documentadas |
| Portabilidad | #29 | OVA/OVF únicamente si se confirma su exigencia |

Los experimentos nuevos conservan independencia respecto al
estudio V2. Mantenemos los modelos, datasets y conclusiones
históricos, con nuevas particiones, etiquetas y protocolos
cuando corresponda.

Actualizamos el informe y el catálogo gráfico al cerrar cada
fase; consolidamos la entrega definitiva tras la aceptación
técnica de las fases 08, 09 y 10.

## Entregables y aceptación

La entrega definitiva de la fase 10 contempla un informe PDF acumulativo, un TAR técnico independiente en sustitución de anexos técnicos y una presentación con demostración mediante la consola. El mínimo del informe es de 40 páginas según los criterios académicos registrados. Excluir credenciales, datos privados, estados de ejecución, respaldos y materiales docentes ajenos. Auditar contenido y extracción del TAR y comprobar reproducibilidad.

Los registros originales, datasets y entornos Python se mantienen fuera de Git en el área de ejecución de la VM. Los antecedentes de desarrollo se conservan en el historial ordinario de Git. Ninguna issue se cierra sin comprobar sus criterios; la milestone requiere todas sus issues y los entregables correspondientes. [Gestión de hitos](../gestion/gestion-milestones-s01-s08.md) · [Cobertura académica](../gestion/cobertura-academica-netlab360.md).

## Estado de integración de la consola

El backend y el diagnóstico técnico están aceptados; las vistas operacionales, históricos, topología resumida y detallada, temas y Swagger fueron validados con 204 pruebas específicas. Conservamos la equivalencia integral y retiro de interfaces independientes como pendientes. Las pruebas de red, sondas Blackbox y objetivos SLI/SLO constituyen el siguiente alcance prioritario. La administración avanzada de identidades sigue diferida.
