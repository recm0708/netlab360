# Índice de documentación técnica de NETLAB360

Organizamos la documentación vigente por responsabilidad. Cada documento describe su alcance, implementación, resultados y limitaciones pertinentes. Conservamos los catálogos de capturas y los registros experimentales separados. Este índice no reemplaza los README específicos de cada componente.

## Arquitectura

- [Arquitectura multisede implementada](arquitectura/arquitectura-multisede-implementada.md)

## Decisiones arquitectónicas

- [ADR 001 entorno virtualizacion](decisiones/adr-001-entorno-virtualizacion.md)
- [ADR 002 direccion administrativa](decisiones/adr-002-direccion-administrativa.md)
- [ADR 003 aislamiento redes](decisiones/adr-003-aislamiento-redes.md)

## Infraestructura

- [Inventario host y vmware](infraestructura/inventario-host-y-vmware.md)
- [Ubuntu desktop y ssh](infraestructura/ubuntu-desktop-y-ssh.md)

## Diseño técnico

- [Dominio SDN con Open vSwitch y Faucet — Fase 05](diseno/s05-dominio-sdn-ovs-faucet.md)
- [Diseño de disponibilidad HTTP — Fase 05](diseno/s05-ha-servicios-multisede.md)
- [Diseño de agregación LACP — Fase 05](diseno/s05-lacp-8023ad-multisede.md)
- [Adquisición observacional de telemetría — Fase 06](diseno/s06-adquisicion-observacional.md)
- [Auditoría de muestreo ICMP del corpus histórico — Fase 06](diseno/s06-auditoria-muestreo-protocolo-historico.md)
- [Auditoría preventiva del cliente HQ — Fase 06](diseno/s06-auditoria-preintervencion.md)
- [Auditoría de preparación prospectiva del corpus histórico — Fase 06](diseno/s06-auditoria-readiness-prospectiva.md)
- [Línea base no supervisada y regla P95 — Fase 06](diseno/s06-baseline-ml-no-supervisado.md)
- [Escenarios experimentales y etiquetado verificable — Fase 06](diseno/s06-escenarios-y-etiquetado.md)
- [Estados de incertidumbre IA y observación LACP/SDN — Fase 06](diseno/s06-estados-ia-y-observacion-lacp-sdn.md)
- [Evaluación binaria exploratoria por sesiones — Fase 06](diseno/s06-evaluacion-binaria-holdout.md)
- [Intervención controlada y watchdog del cliente HQ — Fase 06](diseno/s06-experimentos-hq-reales-y-watchdog.md)
- [Falla HTTP HQ y etiquetado independiente — Fase 06](diseno/s06-fault-http-hq-etiquetado-independiente.md)
- [Guardia privilegiada y temporizador sin mutación — Fase 06](diseno/s06-guardia-root-y-watchdog-noop.md)
- [Inferencia histórica y API de solo lectura — Fase 06](diseno/s06-inferencia-hq-replay-readonly.md)
- [Adquisición experimental multisesión en HQ — Fase 06](diseno/s06-lotes-multisesion-hq.md)
- [Mediciones activas de rendimiento — Fase 06](diseno/s06-mediciones-rendimiento.md)
- [Normalización y calidad de datos de telemetría — Fase 06](diseno/s06-normalizacion-y-calidad.md)
- [Panel de diagnóstico IA en el NOC — Fase 06](diseno/s06-panel-ia-noc-readonly.md)
- [Prerregistro y congelación del estudio histórico — Fase 06](diseno/s06-preregistro-futuro-modelos-congelados.md)
- [Protocolo experimental uniforme V2 — Fase 06](diseno/s06-protocolo-uniforme-v2.md)
- [Recuperación de veth aislada ante pérdida del controlador — Fase 06](diseno/s06-recuperacion-veth-aislada.md)
- [Restauración de qdisc en namespace aislado — Fase 06](diseno/s06-restauracion-aislada.md)
- [Simulación de seguridad y restauración — Fase 06](diseno/s06-rollback-simulacion.md)
- [Plan maestro y criterios de aceptación — Fases 06–08](diseno/s06-s08-plan-maestro-y-criterios.md)
- [Telemetría reciente e inferencia exploratoria — Fase 06](diseno/s06-telemetria-reciente-inferencia-hq.md)
- [Deriva descriptiva y oportunidad de detección V2 — Fase 06](diseno/s06-v2-deriva-deteccion-y-limitaciones-finales.md)
- [Evaluación cronológica V2 con modelos congelados — Fase 06](diseno/s06-v2-evaluacion-cronologica-congelada.md)
- [Entrenamiento y congelación de modelos V2 — Fase 06](diseno/s06-v2-train-freeze-modelos.md)
- [Ventanas normales con etiquetado independiente — Fase 06](diseno/s06-ventanas-normales-verificadas.md)
- [Temporizador independiente y requisitos de rollback — Fase 06](diseno/s06-watchdog-rollback-gates.md)
- [API local controlada v1 — Fase 07](diseno/s07-api-controlada.md)
- [Contexto topológico y correlación RCA — Fase 07](diseno/s07-contexto-y-correlacion-rca.md)
- [Contrato de eventos e incidentes multisede — Fase 07](diseno/s07-contrato-eventos-e-incidentes.md)
- [Ensayos operacionales y escenarios compuestos — Fase 07](diseno/s07-ensayos-operacionales.md)
- [Intent Assurance y autorización RFC — Fase 07](diseno/s07-intent-assurance-y-rfc.md)
- [Intervención OSPF y recuperación independiente — Fase 07](diseno/s07-intervencion-ospf-y-watchdog.md)
- [Preflight privilegiado del orquestador — Fase 07](diseno/s07-preflight-orquestador.md)
- [Runbooks y recomendaciones — Fase 07](diseno/s07-runbooks-y-recomendaciones.md)
- [Consola interactiva y acciones — Fase 08](diseno/s08-consola-interactiva-y-acciones.md)

## Validación

- [Validación técnica de las fases 01–04](validacion/s01-s04-resultados.md)
- [Validación técnica de la fase 05](validacion/s05-integracion-y-aceptacion.md)

## Evidencias técnicas

- [Evidencia GitOps y CI — Fase 03](evidencias/s03-gitops-ci-regresion.md)

## Gestión del proyecto

- [Cobertura académica y criterios de aceptación de NETLAB360](gestion/cobertura-academica-netlab360.md)
- [Convenciones de issues, pull requests y metadatos de GitHub](gestion/convenciones-issues-etiquetas.md)
- [Gestión y aceptación de hitos de las fases 01–08](gestion/gestion-milestones-s01-s08.md)
- [Acta de aceptación técnica — Fase 05](gestion/s05-acta-aceptacion-tecnica.md)

## Catálogos y componentes

- [Evidencias gráficas](../evidencias/capturas/README.md)
- [Topología de referencia](../topologias/b2-frr/README.md)
- [Topología multisede](../topologias/s02-frr/README.md)
- [Ansible](../ansible/s03/README.md)
- [OpenTofu](../iac/s03/README.md)
- [Observabilidad](../servicios/observabilidad/README.md)
- [NOC de la fase 04](../servicios/noc-s04/README.md)
- [NOC de la fase 05](../servicios/topologia-s05/README.md)
- [NOC histórico](../servicios/noc-historico/README.md)
