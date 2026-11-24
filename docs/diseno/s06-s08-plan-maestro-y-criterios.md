# Plan maestro y criterios de aceptación — Fases 06–08

## Descripción

NETLAB360 estudia redes empresariales multisede dentro de una única VM Ubuntu sobre VMware, con HQ, S1 y S2 y un plano de administración separado. Este documento establece el alcance de las fases, sus dependencias y los criterios de aceptación; los resultados específicos se desarrollan en los documentos de cada componente.

## Estado técnico

| Fase | Estado | Referencia |
|---|---|---|
| Fases 01–04 | Cerradas | [Validación de infraestructura, automatización y observabilidad](../validacion/s01-s04-resultados.md) |
| Fase 05 | Cerrada | [Integración HA, LACP y SDN](../validacion/s05-integracion-y-aceptacion.md) |
| Fase 06 | Cerrada | [Protocolo uniforme V2](s06-protocolo-uniforme-v2.md) |
| Fase 07 | Cerrada; aceptación técnica y documental interna completa | [API controlada](s07-api-controlada.md) · [Ensayos](s07-ensayos-operacionales.md) |
| Fase 08 | Pendiente de implementación y aceptación integral | [Consola interactiva](s08-consola-interactiva-y-acciones.md) |
| Fase 09 | Ampliación condicionada, sin milestone aprobada | [Cobertura académica](../gestion/cobertura-academica-netlab360.md) |

La reconstrucción manual tras el reinicio del invitado acreditó la recuperación de componentes individuales en la fase 06; no acreditó reconstrucción automática integral. Las bibliotecas instaladas tampoco equivalen a funcionalidades implementadas.

## Fase 06 — Diagnóstico inteligente

Se evaluaron P95, Isolation Forest y regresión logística sobre dos rutas ICMP, con muestreo uniforme de tres paquetes por ventana y 140 ventanas por ruta. TRAIN, VALIDATION y TEST se separaron cronológicamente; cuatro modelos quedaron congelados antes de evaluar las particiones posteriores. El estudio previo se conserva como exploratorio.

La [evaluación final](s06-v2-evaluacion-cronologica-congelada.md) acredita F1 entre 0,941 y 1,000 en TEST, sin falsos negativos en las ocho ventanas positivas de cada ruta. La [falla HTTP independiente](s06-fault-http-hq-etiquetado-independiente.md) demuestra conmutación y recuperación del backend HQ sin modificar el conjunto ICMP. No se acredita pronóstico, MAE prospectivo, deriva de concepto inferencial ni generalización a HTTP.

Criterios: adquisición verificable, etiquetas independientes, separación cronológica, comparación con referencia determinista, inferencia de solo lectura, recuperación y limitaciones explícitas. Issues #6, #25 y #26 cerradas. [Evidencias de la fase 06](../../evidencias/capturas/fase6/README.md).

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

Los ocho componentes están aceptados técnicamente. Se verificaron 15 ventanas seleccionadas, 870 observaciones no independientes, 11 hipótesis y recomendaciones coincidentes y un ciclo RFC integrado por API. Se conservaron 116 registros históricos y la red administrativa. Las 49 imágenes están en el [catálogo de la fase 07](../../evidencias/capturas/fase7/README.md).

La autorización es determinista y no concede privilegios a un modelo generativo. UNKNOWN no autoriza cambios. El ciclo de detección, explicación, recomendación, aprobación, ejecución, verificación y restauración requiere evidencia privilegiada, acciones de alcance fijo y retorno independiente. La separación acreditada corresponde a privilegios del sistema operativo, no a personas independientes.

## Fase 08 — Integración y entrega

- Consola web con menú único para topología, WAN/OSPF/VLAN, HA, LACP, SDN, métricas, IA, incidentes, RFC, runbooks, auditoría y resultados.
- Integración de la API de la fase 07 y pruebas acotadas ICMP, traceroute, HTTP e iperf3 TCP/UDP. Catálogo estable; sin shell libre ni privilegios del navegador.
- Copiloto RAG (#198) con corpus propio autorizado, citas verificables, evaluación de fundamentación, abstención y controles frente a instrucciones maliciosas. No autoriza cambios.
- Recuperación desde apagado completo (#106), compatibilidad (#34), regresión, demostración e informe/TAR/PPT (#27, #43, #44 y #45). OVA condicionada a #29.
- Auditoría de inicio con VM reanudada, matriz de cobertura consolidada al cierre de fase 7 y decisión de #17/#24 conforme a evidencia y viabilidad. No habilitar cambios adicionales sin aceptación individual de sus ejecutores.

Criterio de aceptación: integración comprobada, recuperación integral, regresión y entregables reproducibles. Consultar el [diseño de consola](s08-consola-interactiva-y-acciones.md).

## Fase 09 — Ampliación condicionada

La ampliación se decidirá después de la fase 08 conforme a la [matriz académica](../gestion/cobertura-academica-netlab360.md). No se presenta como fase aprobada ni como resultado implementado.

## Entregables y aceptación

La entrega contempla un informe PDF acumulativo, un TAR técnico independiente en sustitución de anexos técnicos y una presentación con demostración mediante la consola. El mínimo del informe es de 40 páginas según los criterios académicos registrados. Excluir credenciales, datos privados, estados de ejecución, respaldos y materiales docentes ajenos. Auditar contenido y extracción del TAR y comprobar reproducibilidad.

Los registros originales, datasets y entornos Python se mantienen fuera de Git en el área de ejecución de la VM. Los antecedentes de desarrollo se conservan en el historial ordinario de Git. Ninguna issue se cierra sin comprobar sus criterios; la milestone requiere todas sus issues y los entregables correspondientes. [Gestión de hitos](../gestion/gestion-milestones-s01-s08.md) · [Cobertura académica](../gestion/cobertura-academica-netlab360.md).
