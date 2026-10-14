# NETLAB360 — Estado actual y continuidad

**Actualización editorial:** 14/10/2026. **Documento operativo canónico:** [REANUDAR AQUÍ](REANUDAR-AQUI.md). En caso de conflicto, consultar GitHub commits y las bitácoras de sesión. El historial completo de esta página está preservado en Git.

## Estado validado
- S01 permanece abierta, **72/100 de avance técnico estimado**; rúbrica/alcance docente sin ratificar.
- B0–B4 tienen subpruebas funcionales comprobadas (VM/VMnet8, IPAM, L2 VLAN/ACL, FRR OSPF dual WAN, LACP/active-backup virtual, IaC→FRR, exporter/Prometheus, reglas descriptivas B4), sin integración integral ni modelo IA evaluado.
- 86 PNG planos y 7 manifiestos CSV SHA256 en GitHub. Lote06 commit b410548 y Git local/remoto iguales tras push del operador.
- CI offline exitosa run 38511477595, 24 unit tests locales. Host postcheck 13/10 23:35:02: Docker/netns vacíos, ens33 192.168.47.40/24, gateway 192.168.47.2, servicios docker/ssh/open-vm-tools activos.
- Archivos posteriores de documentación en GitHub pueden requerir git pull --ff-only en Ubuntu; no existe actividad de laboratorio pendiente de cleanup.

## Política vigente de documentación y calendario
El usuario ha establecido **tres documentos maestros únicos S01–S08**: proyecto académico, implementación/laboratorios y manual usuario. En plantilla Word institucional, texto por secciones, APA 7 y referencias citadas; **un índice automático por documento**. [Política de entrega](entregables/00-politica-editorial-y-entrega-acumulativa.md). Los borradores V0.1 anteriores no se utilizarán. **No iniciar S02** hasta terminar la sección S01 de los tres maestros y resolver brechas de S01 según guía/rúbrica.

## Riesgos y obligaciones pendientes
- La matriz de once criterios S01 contiene elementos marcados en otras issues como S03 (IaC avanzada) y S06 (dataset/ML). No modificar alcance unilateralmente; validar con guía docente [#36](https://github.com/recm0708/netlab360/issues/36).
- Faltan integración de topologías L2→WAN→servicio/NOC, respaldo real de equipo/servidor, evolución IaC/alertas y evaluación ML si se exigen todos los criterios de S01; falta release/OVA cuando corresponda.
- Cuatro capturas IaC desde logs originales y postcheck lote06 nuevo siguen pendientes de incorporación física. No repetir apply por imágenes.

**Rutas de trabajo:** [matriz S01](control/01-avance-s01.md), [aceptación](control/03-matriz-aceptacion-y-decisions-s01.md), [índices maestros](entregables/00-politica-editorial-y-entrega-acumulativa.md), [checkpoint](REANUDAR-AQUI.md).
