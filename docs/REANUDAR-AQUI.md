# NETLAB360 — REANUDAR AQUÍ

## AUDITORÍA FINAL DE ISSUES (14/10/2026) — ANTES DE SINCRONIZAR UBUNTU

- [Auditoría completa de 43 issues](control/04-auditoria-issues-milestones-2026-10-14.md): **38 abiertas, 5 cerradas, 0 abiertas sin milestone**. Issues #33 CI offline y #42 FRRouting dual-WAN/HTTP fueron cerradas con evidencias y límites; #39, #40, #41 ya estaban cerradas.
- Se asignaron milestones: #27/#28/#29 S08, #35/#38/#42/#43 S01. Las demás ya estaban asignadas; fases S02–S08 no se han declarado ejecutadas.
- **Issue #38 / tarea [030] SSH segura sigue abierta** por política sshd en servidor/rollback no verificados. Conexión por clave Ed25519 desde Windows SÍ está probada; no modificar `sshd_config` sin acceso de recuperación. [Issue actualizada](https://github.com/recm0708/netlab360/issues/38).
- #12 PoC observable, #30 VLAN→WAN y #31 LACP capacidad fueron actualizadas con hechos actuales y brechas genuinas, sin añadir ensayos innecesarios. La guía docente decidirá qué hace falta para S01.
- **Índices 01/02 APROBADOS 14/10/2026 por usuario**, sujetos a indicaciones de profesora. El usuario aún no sincronizó Ubuntu tras esta auditoría; próxima acción técnica solo `git pull --ff-only` limpio y verificar `main...origin/main`. **NO comenzar la redacción del Documento 01 hasta que el usuario diga «comencemos»**.

---


**Checkpoint editorial 14/10/2026.** El usuario redefinió la entrega: **DOS documentos maestros consolidados, no tres**. No comenzar S02 antes de terminar contenido S01 y brechas técnicas exigibles. **Los índices 01/02 fueron APROBADOS por el usuario el 14/10/2026**, salvo modificaciones solicitadas después por la profesora. **No comenzar la redacción hasta que diga «comencemos».** Las portadas las crea el usuario en su formato institucional.

## Política documental actual

- [01 — Investigación y evaluación](entregables/01-proyecto-investigacion-maestro.md): informe académico de lo realizado por el equipo, introducción, objetivos, marco teórico, diseño, desarrollo, resultados, recomendaciones, conclusiones y APA7. **Incidentes técnicos reales y mitigaciones integrados en el subcapítulo afectado**; descuidos personales no se documentan.
- [02 — Manual técnico integral](entregables/02-informe-tecnico-maestro.md): preparación del host, VM, Ubuntu, dependencias, instalación desde cero, scripts/comandos validados, capturas, pruebas, operación, interfaz, mantenimiento, seguridad, troubleshooting **de problemas posibles**; no narrar cronología de errores reales.
- [Política editorial](entregables/00-politica-editorial-y-entrega-acumulativa.md): portada hecha por usuario, **índice automático único por documento**, APA7 citas y referencias, preámbulos de figuras/tablas y notas según necesidad; asistente dará textos listos para copiar en la plantilla institucional.
- Si el proyecto se detiene tras una fase efectiva (ejemplo S06), los dos documentos finales cubrirán **solo ese alcance implementado**, sin capítulos ficticios posteriores; no mentir sobre la planificación histórica S01–S08 ni sobre requisitos docentes.
- El tercer documento independiente se elimina; su contenido de uso forma parte del Documento 02. Antiguos borradores rechazados y archivos del Documento 03 quedan accesibles únicamente en historial Git.

## Estado técnico verificado

**S01 sigue ABIERTA (72/100 estimación interna, NO nota docente).** B0 VM/VMnet8, IPAM B1, VLAN/ACL HTTP y FRR OSPF dual WAN HQ–S1, LACP/bonding virtual, SoT/OpenTofu→Ansible FRR con reconciliación **de archivos**, exporter/NOC básico y Prometheus firing/resuelto, perfil y diagnóstico determinista B4 sin ML. **86 PNG y 7 CSV** publicados, lote06 b410548; **24 pruebas unitarias**, CI GitHub 38511477595 exitosa. Postcheck 13/10 23:35:02: Docker/netns vacíos; ens33 192.168.47.40/24 y gateway 192.168.47.2, servicios activos.

**Pendientes S01:** guía/rúbrica y alcance (índices ya aprobados), contenido de ambos documentos, cuatro fotos IaC desde logs y captura postcheck adicional; componentes L2–WAN integrados, redundancia de equipo, NOC/receptor, ML evaluable, release/OVA **solo cuando rúbrica exija su cierre en S01**. Consulte [once criterios S01](control/03-matriz-aceptacion-y-decisions-s01.md). IaC avanzada se planificó S03 y ML S06 en issues independientes.

## Si se reanuda Ubuntu

Ejecutar desde terminal sólo cuando haga falta sincronización editorial:

    cd ~/proyectos/netlab360
    git status --short --branch
    GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main

No ejecutar reset destructivo, push force, nuevos cortes WAN ni apply por capturas; no hace falta un laboratorio nuevo para comenzar redacción.

## Issues canónicas

[#1 cierre S01](https://github.com/recm0708/netlab360/issues/1) · [#9 requisitos](https://github.com/recm0708/netlab360/issues/9) · [#35 DOS documentos](https://github.com/recm0708/netlab360/issues/35) · [#36 guía docente](https://github.com/recm0708/netlab360/issues/36) · [#43 evidencias](https://github.com/recm0708/netlab360/issues/43) · [#29 OVA](https://github.com/recm0708/netlab360/issues/29).

Evidencias históricas, commits y sesiones preservados; no volver a resumir estados antiguos como actuales.
