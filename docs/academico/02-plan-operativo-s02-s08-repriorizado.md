# NETLAB360 — Repriorización de trabajo técnico/academico por 7 iteraciones restantes

**Fecha de decisión:** 16/10/2026. **Prioridad:** recuperar retraso sin perder pruebas verificadas. **Advertencia:** estos son **hitos internos**, NO fechas de entrega finales del semestral; los cortes 30/10 y 13/11 SÍ son comunicados. El roadmap original S01–S08 y milestones históricos siguen en GitHub hasta que las fechas reales del semestral sean confirmadas por la docente; no inventar nuevo calendario.

## Fechas académicas ya comunicadas

- **Título del proyecto:** enviado al chat Teams según confirmación del estudiante el 17/10; falta respuesta/aprobación docente.
- **30/10/2026:** primera revisión de borrador (Introducción, Objetivo general y específicos, Planteamiento del problema), en Teams sin diapositivas; representante asignado.
- **13/11/2026:** segunda revisión (Fundamento técnico y Diseño).
- **Demostración final EN VIVO**: planificar escenarios recuperables; fecha/duración no comunicadas.
- **Anexos en archivo ZIP aparte confirmados** junto al informe.
- **Parcial individual**, plazo 25/10, se realiza fuera del proyecto NETLAB360.

## Bloqueos eliminados

- Ya NO se exige redactar el Manual Técnico 02 antes de continuar S02.
- Ya NO se exige completar en S01 todos los objetivos integrales originally mal agregados (IaC avanzada S03, IA S06, OVA S08) como condición para seguir: permanecen **pendientes y trazados**, no se declaran cumplidos.
- El informe único se alimenta en cada iteración con diseño→implementación→pruebas→análisis; presentación al terminar y congelar el informe.

## Plan provisional S02–S08 (siete hitos, reelaborable)

| Fase interna | Prioridad práctica principal | Prueba concluyente para demostración | Dependencias |
|---|---|---|---|
| **S02** | Integrar una topología persistente HQ–S1–S2 con VLAN por sede, OSPF y WAN doble; clientes→servicio y ACL entre sedes | Enlace primario DOWN→backup activo→restauración, tráfico permitido/denegado, captura pre/post; no afectar VMnet8 | #13 #14 #30 #31; inventario y topología |
| **S03** | SoT e IaC sobre topología integrada con ownership, config FRR live, idempotencia y drift controlado | cambio legítimo/diferencia detectada/reconciliación/restauración + CI/PR acotado | #16–#19 |
| **S04** | NOC central y por sede, exporter, Prometheus/Alertmanager según alcance, SLI/SLO e histórico | incidente WAN, métrica y alerta visibles y resueltas con timestamps correlacionados | #12 #15 #20–#22 |
| **S05** | Doble enlace LACP con medición multistream, equipos/rutas alternas y SDN OVS/Faucet aislado si cabe | falla de miembro vs falla de equipo, HTTP/medición real y recuperación | #23 #24 #31 #32 |
| **S06** | Dataset de incidentes etiquetado por sesiones, reglas baseline y evaluación IA reproducible | matriz de confusión, precision/recall/F1 únicamente si existe ground truth separado, comparación honesta | #25 #26 |
| **S07** | Recuperación operativa, robustez/NOC/automatización integrada y pruebas extremo a extremo | secuencia de fallas, recuperación, tolerancia, rollback, medición/observación | #7 #22 y brechas |
| **S08** | Regresión final, paquete de anexos, informe >=40p, OVA si se exige/compromete, revisión de privacidad, PPT y demo | demo repetible, artefactos íntegros, guía y rúbrica cubiertas | #8 #27 #29 #43 #44 #45 |

## Reglas operativas de aceleración

1. **No reconstruir B0–B4** aprobados ni repetir `tofu apply`, OSPF o LACP solo por fotografías. Priorizar la **integración real** de escenarios aislados.
2. Trabajar en tandas de varios pasos con checkpoints: estado de Git y red administrativa, modificación mínima, comprobación funcional, rollback, postcheck, commit y evidencias.
3. Por cada ensayo nuevo crear **un caso de validación apto para demo** con baseline→estímulo→esperado→observado→restauración; actualizar Documento 01 y ZIP de anexos progresivamente, aunque su edición final sea después.
4. Proteger VMnet8 `ens33 192.168.47.40/24` y gateway `.2`, SSH; evitar cambios al host Windows. Sanitizar credenciales antes de exportar.
5. **La numeración S02–S08 es de planificación interna, no una exigencia oficial de duración de 7 semanas**. Reajustar según fecha final de entrega y duración de defensa todavía no informadas.
6. Priorizar resultado funcional demostrable frente a número de tecnologías prometidas. Reducir **alcance opcional** si hace falta, pero no borrar compromisos técnicos oficiales ni falsificar pruebas.
7. Crear/actualizar el PPT **después del cierre del contenido del informe**, no antes, salvo esquema de demo que puede diseñarse previamente.

## Próximo trabajo operativo inmediato

**S02 / primer sprint de integración:** iniciar Ubuntu tras encendido de VMware, precheck seguro (Docker/netns/ens33/GW/SSH/Git), revisar documentación/scripts ya existentes, diseñar integración HQ–S1–S2 y una ruta de pruebas; NO desplegar o modificar interfaces hasta revisar el plan y conservar recovery. La VM fue apagada limpiamente por el usuario el 16/10; su estado apagada por GUI aún pendiente de observación.

**Estado de documentación:** se dispone ya de fechas parciales y se confirmó demostración en vivo; el parcial se trabaja aparte para resolver criterios de demostración, sin tratar un ejemplo de parcial como rúbrica oficial del semestral.
