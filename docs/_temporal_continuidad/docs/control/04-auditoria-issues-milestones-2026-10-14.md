# NETLAB360 — Auditoría global de issues y milestones

**Fecha:** 14/10/2026 (Panamá). **Estado verificado mediante API GitHub tras modificaciones.** Este archivo es el **resumen canónico de control**, no una lista de tareas nuevas. No altera las evidencias de red ni supone aceptación docente.

## Conteo e hitos

- Total de issues: **43**, abiertas: **38**, cerradas: **5**.
- Milestones de las **38 abiertas:** S01=13; S02=5; S03=4; S04=4; S05=4; S06=3; S07=1; S08=4.
- Issues abiertas sin milestone: **0**.
- Previamente cerradas: #39 IPv4 VMnet8, #40 GitHub CLI/SSH/repositorio, #41 herramientas/snapshot VMware.
- **Cerradas ahora tras cotejo técnico:** #33 (CI segura offline vs pruebas privilegiadas) y #42 (FRR OSPF dual-WAN y HTTP HQ→S1 por WAN-P/B/P). Cada una contiene evidencia, límites y tareas derivadas que permanecen abiertas en issues específicas. **No** se da por cerrado el MVP S01.
- **Issue SSH correcta:** [#38 / tarea [030]](https://github.com/recm0708/netlab360/issues/38). El acceso Ed25519 desde cliente está verificado; NO hay evidencia de `sshd -T`, política de contraseñas en servidor ni rollback de hardening. Continúa abierta.
- Se asignaron milestones a **#27, #28, #29→S08**, **#35, #38, #42, #43→S01**. El milestone S08 de documentos significa entrega consolidada **final**, aunque la redacción comienza en S01.
- La issue #43 recibió las etiquetas `semana:01`, `tipo:docs`, `prioridad:media` para conservar clasificación consistente.
- El usuario aprobó los **dos índices maestros V0.2** como línea editorial, sujeta a futuras indicaciones de la profesora: (01) informe académico del proyecto con incidentes técnicos reales y mitigaciones, (02) manual técnico integrado de reproducción/operación con posibles problemas y solución preventiva. Portadas a cargo del usuario. No empezar texto hasta su orden «comencemos».
- Se actualizaron checklists genéricos de las issues futuras para dejar de exigir documentalmente tres archivos independientes. **No** se han cambiado milestone/calendario ni cerrado fases no ejecutadas.

## Inventario auditado de las 43 issues

| Issue | Título en GitHub | Estado | Milestone | Dictamen/verificación |
|---|---|---|---|---|
| [#1](https://github.com/recm0708/netlab360/issues/1) | [S01] Semana 1: MVP transversal y viabilidad | Abierta | S01 | MVP S01 integral no aceptado; rúbrica aún pendiente |
| [#2](https://github.com/recm0708/netlab360/issues/2) | [S02] Semana 2: Multisede, LACP y capacidad | Abierta | S02 | S02 no iniciada; conservar agenda |
| [#3](https://github.com/recm0708/netlab360/issues/3) | [S03] Semana 3: Network as Code y compliance | Abierta | S03 | S03 no iniciada |
| [#4](https://github.com/recm0708/netlab360/issues/4) | [S04] Semana 4: Observabilidad y gestión de incidentes | Abierta | S04 | S04 no iniciada |
| [#5](https://github.com/recm0708/netlab360/issues/5) | [S05] Semana 5: Equipos redundantes y SDN acotada | Abierta | S05 | S05 no iniciada |
| [#6](https://github.com/recm0708/netlab360/issues/6) | [S06] Semana 6: Datos e IA evaluada | Abierta | S06 | S06 no iniciada |
| [#7](https://github.com/recm0708/netlab360/issues/7) | [S07] Semana 7: AIOps supervisado y recuperación | Abierta | S07 | S07 no iniciada |
| [#8](https://github.com/recm0708/netlab360/issues/8) | [S08] Semana 8: Congelación, regresión y OVA | Abierta | S08 | S08/release pendiente |
| [#9](https://github.com/recm0708/netlab360/issues/9) | [001] Ratificar requisitos oficiales y alcance | Abierta | S01 | Guía y aceptación docente de fusión 2 documentos pendientes |
| [#10](https://github.com/recm0708/netlab360/issues/10) | [002] Validar recursos de Ubuntu Desktop y virtualizador | Abierta | S01 | ISO/CD/DVD/UEFI y cierre compatibilidad de VM pendientes |
| [#11](https://github.com/recm0708/netlab360/issues/11) | [003] Diseñar IPAM y topología multisede | Abierta | S01 | IPAM draft, no aprobación/integración multisede final |
| [#12](https://github.com/recm0708/netlab360/issues/12) | [004] Construir PoC de un evento observable | Abierta | S01 | Exporter/Prometheus validados; falta enlace alertas↔NOC/receptor según criterio |
| [#13](https://github.com/recm0708/netlab360/issues/13) | [005] Emular HQ y dos sucursales con FRR OSPF | Abierta | S02 | HQ y dos sucursales S02: segunda sucursal/integración pendiente |
| [#14](https://github.com/recm0708/netlab360/issues/14) | [006] Validar failover y restauración de WAN | Abierta | S02 | Failover HQ-S1 basal probado, alcance ampliado S02 pendiente |
| [#15](https://github.com/recm0708/netlab360/issues/15) | [007] Implementar dashboard NOC y paneles por sede | Abierta | S01 | NOC básico probado; alertas/paneles por sede incompletos |
| [#16](https://github.com/recm0708/netlab360/issues/16) | [008] Definir source of truth e inventario | Abierta | S01 | SoT YAML consumido, inventory/ownership integral por completar |
| [#17](https://github.com/recm0708/netlab360/issues/17) | [009] Incorporar OpenTofu con ownership explícito | Abierta | S03 | OpenTofu ownership lifecycle S03 pendiente |
| [#18](https://github.com/recm0708/netlab360/issues/18) | [010] Ansible para configuración y cumplimiento | Abierta | S03 | Ansible con candidatos S01; compliance live S03 pendiente |
| [#19](https://github.com/recm0708/netlab360/issues/19) | [011] Configurar validación CI y flujo de PR | Abierta | S03 | Workflow existe; revisión completa de PR/GitOps pendiente |
| [#20](https://github.com/recm0708/netlab360/issues/20) | [012] Integrar exporters y Prometheus | Abierta | S04 | Exporter/Prometheus básico probado; S04 integral pendiente |
| [#21](https://github.com/recm0708/netlab360/issues/21) | [013] Implementar histórico, alertas y SLI/SLO | Abierta | S04 | Alertas con timestamps; SLI/SLO y receptor externos pendientes |
| [#22](https://github.com/recm0708/netlab360/issues/22) | [014] Catálogo seguro de escenarios de fallas | Abierta | S04 | Catálogo total de fallos seguros aún por completar |
| [#23](https://github.com/recm0708/netlab360/issues/23) | [015] Prueba SDN OVS Faucet en dominio acotado | Abierta | S05 | OVS/Faucet del dominio S05 no implementado |
| [#24](https://github.com/recm0708/netlab360/issues/24) | [016] Evaluar WireGuard y sucursales adicionales | Abierta | S05 | WireGuard/sucursales adicionales no evaluados |
| [#25](https://github.com/recm0708/netlab360/issues/25) | [017] Generar dataset etiquetado de incidentes | Abierta | S06 | Dataset ML externo etiquetado no adquirido |
| [#26](https://github.com/recm0708/netlab360/issues/26) | [018] Evaluar detección inteligente de anomalías | Abierta | S06 | Modelo scikit-learn no entrenado/evaluado |
| [#27](https://github.com/recm0708/netlab360/issues/27) | [019] Documento 01 — investigación y evaluación académica APA 7 | Abierta | S08 | Documento 01 aprobado como índice; redacción y versión final pendientes |
| [#28](https://github.com/recm0708/netlab360/issues/28) | [020] Documento 02 — manual técnico integral de implementación y uso | Abierta | S08 | Documento 02 fusionado; redacción/validación final pendientes |
| [#29](https://github.com/recm0708/netlab360/issues/29) | [021] Sanitizar y exportar VM OVA y verificar importación | Abierta | S08 | OVA sanitizada, exportada y reimportada no comprobada |
| [#30](https://github.com/recm0708/netlab360/issues/30) | [022] VLAN, trunks, ACL y separación entre sedes | Abierta | S01 | VLAN/ACL local y HTTP WAN separados; integración misma topología pendiente |
| [#31](https://github.com/recm0708/netlab360/issues/31) | [023] LAG/LACP activo-activo, capacidad y falla de miembro | Abierta | S02 | LACP 2→1→2 probado; throughput multistream pendiente |
| [#32](https://github.com/recm0708/netlab360/issues/32) | [024] Redundancia real de routers, switches y servidor dual-NIC | Abierta | S05 | Redundancia real de equipos/servidores aún no probada |
| [#33](https://github.com/recm0708/netlab360/issues/33) | [025] CI segura y separación de pruebas locales de red | Cerrada | S01 | CI offline seguro y delimitación de ensayos probados; cerrado |
| [#34](https://github.com/recm0708/netlab360/issues/34) | [026] Matriz de versiones de VMware, Ubuntu y dependencias | Abierta | S01 | Matriz versiones base válida; ISO/UEFI/OVS/portabilidad pendientes |
| [#35](https://github.com/recm0708/netlab360/issues/35) | [027] Dos documentos maestros: investigación y manual técnico integral | Abierta | S01 | Índices dos documentos aprobados; texto S01 por redactar |
| [#36](https://github.com/recm0708/netlab360/issues/36) | [028] Matriz de rúbrica y contenidos obligatorios | Abierta | S01 | Matriz docente/rúbrica pendiente; no recortar requisitos unilateralmente |
| [#37](https://github.com/recm0708/netlab360/issues/37) | [029] Ensayar exportación/importación OVA antes de la fase final | Abierta | S02 | Prueba temprana OVA en copia pendiente |
| [#38](https://github.com/recm0708/netlab360/issues/38) | [030] Instalar Ubuntu Desktop y habilitar administración SSH segura | Abierta | S01 | SSH por clave funcional; hardening daemon y rollback pendientes |
| [#39](https://github.com/recm0708/netlab360/issues/39) | [031] Reservar dirección IPv4 fija de NETLAB360 en VMnet8 sin colisiones | Cerrada | S01 | IPv4 .40 fija y persistente en VMnet8; cerrado |
| [#40](https://github.com/recm0708/netlab360/issues/40) | [032] Autenticar GitHub CLI desde Ubuntu mediante SSH y clonar repositorio | Cerrada | S01 | GitHub CLI/SSH/clone verificados; cerrado |
| [#41](https://github.com/recm0708/netlab360/issues/41) | [033] Herramientas base y checkpoint VMware completados | Cerrada | S01 | Herramientas base, checkpoint snapshot y arranque verificados; cerrado |
| [#42](https://github.com/recm0708/netlab360/issues/42) | [034] Implementar FRRouting OSPF dual-WAN con failover y recuperación | Cerrada | S01 | OSPF dual WAN y HTTP HQ–S1 en 3 estados verificados; cerrado |
| [#43](https://github.com/recm0708/netlab360/issues/43) | [035] Auditar capturas y trazabilidad de evidencias S01–S08 | Abierta | S01 | 86 PNG/7 CSV auditados; 4 fotos IaC y postcheck extra pendientes |

## Criterios prudentes de cierre

1. Cerrar solo cuando el objetivo concreto de la issue tenga **pruebas suficientes**. Si la historia acumulada mezcla requerimientos de otras issues, separar y enlazar las dependencias; no afirmar que esas integraciones ya funcionan.
2. **#38 sigue ABIERTA:** no confundir conexión autenticada por llave con endurecimiento completo del servicio SSH. Validar primero mediante consultas de solo lectura y preparar consola de recuperación antes de cualquier cambio.
3. **#10 y #34 abiertas:** firmware/ISO y portabilidad no fueron corroborados; un sistema instalado no prueba que la unidad virtual esté desmontada ni que UEFI se haya validado.
4. **#12/#15/#21 abiertas:** prometheus disparó alarmas reales, pero Alertmanager externo y panel integral no están acreditados.
5. **#30 abierta:** VLAN/ACL HQ y HTTP dual WAN HQ–S1 se probaron en ensayos **separados**, no como una sola cadena VLAN→WAN→servicio.
6. **#31 abierta:** LACP negociado y failover funcionan; no hay medida iperf3 multistream de capacidad agregada.
7. **#27, #28, #35 abiertas:** se aprobó la estructura, no se redactó ni validó la entrega APA 7.
8. El alcance global de [#1 S01](https://github.com/recm0708/netlab360/issues/1) y su 72/100 es **interno**; requiere cotejo de exigencias de la profesora. No iniciar S02 hasta que el usuario complete los documentos S01 y se resuelvan las brechas obligatorias.

## Próximo punto de operación

No se necesitan nuevos ensayos de red para empezar a redactar. El usuario **aún no sincronizó** la VM Ubuntu después de estos commits; antes de iniciar trabajo local ejecutar `git status --short --branch` y `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main` sin descartar modificaciones. Documento 01 comienza por la **Introducción** solo tras petición expresa. [Continuidad](../REANUDAR-AQUI.md) · [Política editorial](../entregables/00-politica-editorial-y-entrega-acumulativa.md).
