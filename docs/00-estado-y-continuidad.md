# NETLAB360 — Estado técnico y continuidad (16/10/2026)

**Normativa docente NUEVA:** [tres PDF oficiales](academico/00-requisitos-oficiales-2026-10-16.md). Informe académico-técnico **ÚNICO, mínimo 40 páginas**, PowerPoint y demostración, código en anexos; ZIP separado pendiente de aceptación. Manual 02 pospuesto a después. [Checkpoint canónico](REANUDAR-AQUI.md).

**Trabajo escrito:** existe borrador S01 PDF institucional revisado de 65 páginas, seis figuras y seis tablas en corte anterior, suficiente en extensión pero NO en orden docente: migrar a 12 secciones y fortalecer «Implementación»/«Pruebas». No eliminar capítulos reales, solo reorganizar con control APA7 y figuras.

**Estado de infraestructura:** 86 PNG/7 CSV y CI 24 tests aprobados; gestión `192.168.47.40/24`/GW `.2` preservada. Fases probadas en subtopologías independientes; redes VLAN HQ y WAN HQ–S1 no integradas, S2 reservada, LACP/dual NIC virtual no equipo físico, IaC drift solo en candidatos, no modelo ML. VM apagada limpiamente desde Ubuntu el 16/10, GUI Powered Off sin confirmación directa.

**Gestión de fases:** S01 abierta por 11 criterios internos (72/100 interno), no usar esas casillas como rúbrica oficial ni bloqueo absoluto de S02. Continuar con [integración multisede S02](academico/02-plan-operativo-s02-s08-repriorizado.md), informe único en paralelo, diapositivas después. Las fechas reales quedan por confirmar en transcripción docente.

**Pendientes docentes:** ZIP permitido, fechas/duración, OVA, alcance obligatorio IA/SDN, calendario final, cómo computan las 40 páginas. [Issue #36](https://github.com/recm0708/netlab360/issues/36).

**Repositorio GitHub actualizado de forma remota; Ubuntu requiere pull al volver a arrancar.** No borrar fuentes, scripts ni evidencias. Historial de reglas de «dos documentos» está en Git, ya no vigente.
