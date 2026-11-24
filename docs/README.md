# Índice de documentación técnica de NETLAB360

La documentación vigente se organiza por responsabilidad. Cada documento describe su alcance, implementación, resultados y limitaciones pertinentes. Los catálogos de capturas y los registros experimentales se conservan separados.

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

- [S05 dominio sdn ovs faucet](diseno/s05-dominio-sdn-ovs-faucet.md)
- [S05 ha servicios multisede](diseno/s05-ha-servicios-multisede.md)
- [S05 lacp 8023ad multisede](diseno/s05-lacp-8023ad-multisede.md)
- [S06 adquisicion observacional](diseno/s06-adquisicion-observacional.md)
- [S06 auditoria muestreo protocolo historico](diseno/s06-auditoria-muestreo-protocolo-historico.md)
- [S06 auditoria preintervencion](diseno/s06-auditoria-preintervencion.md)
- [S06 auditoria readiness prospectiva](diseno/s06-auditoria-readiness-prospectiva.md)
- [S06 baseline ml no supervisado](diseno/s06-baseline-ml-no-supervisado.md)
- [S06 escenarios y etiquetado](diseno/s06-escenarios-y-etiquetado.md)
- [S06 estados ia y observacion lacp sdn](diseno/s06-estados-ia-y-observacion-lacp-sdn.md)
- [S06 evaluacion binaria holdout](diseno/s06-evaluacion-binaria-holdout.md)
- [S06 experimentos hq reales y watchdog](diseno/s06-experimentos-hq-reales-y-watchdog.md)
- [S06 fault http hq etiquetado independiente](diseno/s06-fault-http-hq-etiquetado-independiente.md)
- [S06 guardia root y watchdog noop](diseno/s06-guardia-root-y-watchdog-noop.md)
- [S06 inferencia hq replay readonly](diseno/s06-inferencia-hq-replay-readonly.md)
- [S06 lotes multisesion hq](diseno/s06-lotes-multisesion-hq.md)
- [S06 mediciones rendimiento](diseno/s06-mediciones-rendimiento.md)
- [S06 normalizacion y calidad](diseno/s06-normalizacion-y-calidad.md)
- [S06 panel ia noc readonly](diseno/s06-panel-ia-noc-readonly.md)
- [S06 preregistro futuro modelos congelados](diseno/s06-preregistro-futuro-modelos-congelados.md)
- [S06 protocolo uniforme v2](diseno/s06-protocolo-uniforme-v2.md)
- [S06 recuperacion veth aislada](diseno/s06-recuperacion-veth-aislada.md)
- [S06 restauracion aislada](diseno/s06-restauracion-aislada.md)
- [S06 rollback simulacion](diseno/s06-rollback-simulacion.md)
- [S06 s08 plan maestro y criterios](diseno/s06-s08-plan-maestro-y-criterios.md)
- [S06 telemetria reciente inferencia hq](diseno/s06-telemetria-reciente-inferencia-hq.md)
- [S06 v2 deriva deteccion y limitaciones finales](diseno/s06-v2-deriva-deteccion-y-limitaciones-finales.md)
- [S06 v2 evaluacion cronologica congelada](diseno/s06-v2-evaluacion-cronologica-congelada.md)
- [S06 v2 train freeze modelos](diseno/s06-v2-train-freeze-modelos.md)
- [S06 ventanas normales verificadas](diseno/s06-ventanas-normales-verificadas.md)
- [S06 watchdog rollback gates](diseno/s06-watchdog-rollback-gates.md)
- [S07 api controlada](diseno/s07-api-controlada.md)
- [S07 contexto y correlacion rca](diseno/s07-contexto-y-correlacion-rca.md)
- [S07 contrato eventos e incidentes](diseno/s07-contrato-eventos-e-incidentes.md)
- [S07 ensayos operacionales](diseno/s07-ensayos-operacionales.md)
- [S07 intent assurance y rfc](diseno/s07-intent-assurance-y-rfc.md)
- [S07 intervencion ospf y watchdog](diseno/s07-intervencion-ospf-y-watchdog.md)
- [S07 preflight orquestador](diseno/s07-preflight-orquestador.md)
- [S07 runbooks y recomendaciones](diseno/s07-runbooks-y-recomendaciones.md)
- [S08 consola interactiva y acciones](diseno/s08-consola-interactiva-y-acciones.md)

## Validación

- [S01 s04 resultados](validacion/s01-s04-resultados.md)
- [S05 integracion y aceptacion](validacion/s05-integracion-y-aceptacion.md)

## Evidencias técnicas

- [S03 gitops ci regresion](evidencias/s03-gitops-ci-regresion.md)

## Gestión del proyecto

- [Cobertura academica netlab360](gestion/cobertura-academica-netlab360.md)
- [Convenciones issues etiquetas](gestion/convenciones-issues-etiquetas.md)
- [Gestion milestones s01 s08](gestion/gestion-milestones-s01-s08.md)
- [S05 acta aceptacion tecnica](gestion/s05-acta-aceptacion-tecnica.md)

## Catálogos y componentes

- [Evidencias gráficas](../evidencias/capturas/README.md)
- [Topología de referencia](../topologias/b2-frr/README.md)
- [Topología multisede](../topologias/s02-frr/README.md)
- [Ansible](../ansible/s03/README.md)
- [OpenTofu](../iac/s03/README.md)
- [Observabilidad](../servicios/observabilidad/README.md)
- [NOC S04](../servicios/noc-s04/README.md)
- [NOC S05](../servicios/topologia-s05/README.md)
- [NOC histórico](../servicios/noc-historico/README.md)
