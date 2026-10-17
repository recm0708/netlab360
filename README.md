# NETLAB360 — Plataforma Virtualizada de Redes Multisede

**Fecha de replanificación:** 16/10/2026. **Normativa docente recibida:** guías 1457 del informe final, elaboración escrita y presentación/demostración. [REQUISITOS OFICIALES](docs/academico/00-requisitos-oficiales-2026-10-16.md). Resumen + SHA-256 de los tres PDF; binarios originales en adjuntos de conversación, **NO en GitHub**.

## Entregables vigentes y prioridad

1. **UN informe escrito académico-técnico obligatorio, mínimo 40 páginas**, siguiendo exactamente 12 apartados: Portada; Introducción; Objetivos; Planteamiento del problema; Fundamento técnico; Diseño; Implementación; Pruebas y validación; Análisis de resultados; Conclusiones y recomendaciones; Referencias; Anexos. Ya existe un borrador institucional S01 de **65 páginas** que será **reordenado y ampliado**, NO eliminado. [Índice maestro oficial](docs/entregables/01-proyecto-investigacion-maestro.md).
2. **Presentación PowerPoint y demostración obligatoria** después de completar el informe; no basta mostrar «funciona», hay que comprobar baseline/falla/recuperación con explicación técnica. [Issue #44](https://github.com/recm0708/netlab360/issues/44).
3. **Anexos técnicos** con código, configuraciones y evidencias pertinentes. El usuario propone ZIP separado (con SHA256), **sujeto a confirmación de aceptación docente**; no consta como formato obligatorio en los PDF. [Issue #45](https://github.com/recm0708/netlab360/issues/45).
4. **Manual técnico 02 POSPUESTO** para después del proyecto, **no entregable oficial**; se conserva su trazabilidad en [issue #28](https://github.com/recm0708/netlab360/issues/28).

## Regla de avance y cronograma

**No bloquear S02 por un manual técnico que dejó de ser requisito.** La fase S01 aportó evidencia experimental sustancial, pero el criterio integral original no está cerrado. Mantener [#1](https://github.com/recm0708/netlab360/issues/1) abierta y rastrear diferencias reales; avanzar con S02 de integración **HQ–S1–S2, VLAN→WAN→servicio, OSPF y dos WAN**, con precheck, postcheck y seguridad VMnet8. Las ocho etapas S01–S08 siguen como [cronograma INTERNO reordenado](docs/academico/02-plan-operativo-s02-s08-repriorizado.md) hasta conocer fechas/alcance docente en transcripción de reunión. **No reducir compromisos formales ni afirmar implementado lo pendiente.**

## Estado técnico comprobado al corte 13–16/10

- Ubuntu Desktop VMware/VMnet8 `ens33 192.168.47.40/24` y gateway `.2`, SSH Ed25519 operativo, pero hardening servidor pendiente (#38).
- IPAM HQ/S1, S2 reservada; VLAN 110/120, trunk 802.1Q y ACL HTTP HQ aislado; FRR/OSPF HTTP dual WAN HQ–S1 en otra topología, failover/restauración.
- LACP veth IEEE 802.3ad 2→1→2 y bonding activo-respaldo virtual; no redundancia física de switches/equipo.
- OpenTofu metadata→Ansible→config FRR ejecutada en B2; idempotencia/drift probado sobre **archivos candidatos**, no FRR vivo.
- Exporter/NOC inicial, Prometheus scraping y alertas firing/resueltas; analítica estadística de 76 ICMP y 12 eventos independientes con reglas deterministas **sin IA entrenada/evaluada**.
- **86 PNG** planos y **7 CSV SHA256**, 24/24 unit tests y CI exitosa. Último apagado Ubuntu ordenado por usuario el 16/10 tras Docker/netns vacíos y Git `main...origin/main`; el estado Powered Off por consola VMware aún no fue confirmado visualmente.

## Navegación principal

- [REANUDAR-AQUÍ](docs/REANUDAR-AQUI.md).
- [Migración del borrador S01 de 65 páginas](docs/academico/01-migracion-borrador-a-formato-docente.md).
- [Plan de siete iteraciones S02–S08](docs/academico/02-plan-operativo-s02-s08-repriorizado.md).
- [Anexos y demostración](docs/academico/03-anexos-y-demostracion.md).
- [Matriz técnica S01 histórica](docs/control/01-avance-s01.md) — **72/100 es estimación interna**, no rúbrica docente.
- [Incidencias docentes por resolver #36](https://github.com/recm0708/netlab360/issues/36).

**Título formal en portada:** NETLAB360: Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede. **Encabezado Word:** `NETLAB360 | Redes Empresariales Multisede`.
