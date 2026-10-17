# NETLAB360 — Migración del borrador de 65 páginas al informe obligatorio único

**Fuente de estructura:** tres PDFs oficiales recibidos el 16/10/2026. **Estado:** plan de edición, NO modificación del Word/PDF del usuario. El PDF S01 revisado previamente tenía 65 páginas y seis figuras/seis tablas en su versión entonces recibida; sus detalles y paginación deben volver a cotejarse cuando el usuario envíe la versión vigente.

| Orden oficial | Sección exigida | Material del borrador previo que se reutiliza | Corrección necesaria |
|---|---|---|---|
| 1 | Portada | Portada institucional del usuario | Confirmar integrantes completos **y cédulas**, profesor, fecha, carrera y título |
| 2 | Introducción | Introducción anterior | Reducir/ajustar para problema→importancia→solución, sin comandos |
| 3 | Objetivos | Objetivos previos | Mover ANTES del problema; verificar medibilidad y correspondencia con resultados |
| 4 | Planteamiento del problema | Problema + justificación anteriores | Integrar diagnóstico, consecuencias y justificación, sin redundancias |
| 5 | Fundamento técnico | Marco teórico previo (VLAN/OSPF/LACP/IaC/NOC/AIOps) | Mantener solo teoría directamente usada, citas reales APA7 |
| 6 | Diseño de la solución | Arquitectura anterior (HQ/S1/S2, subredes, doble WAN, roles) | Distinguir planeado vs desplegado; figura general, flujos reales y controles |
| 7 | Implementación | Desarrollo inicial S01 y partes pertinentes de metodología | **Ampliar** recursos y versiones, secuencia y configuraciones *principales*, scripts y explicaciones con pocas líneas de código ilustrativas |
| 8 | Pruebas y validación | Capturas S01, tablas, línea base y registros | **Crear sección autónoma** por caso con baseline/estímulo/resultado esperado/observado/evidencia, incluyendo pruebas de recuperación |
| 9 | Análisis de resultados | Discusión, limitaciones, resultados y mitigaciones dispersas | Reubicar incidentes técnicos reales y su resolución aquí, enlazar a fase; eliminar conclusiones prematuras |
| 10 | Conclusiones y recomendaciones | Conclusiones y recomendaciones existentes | Unificar bajo encabezado oficial, contrastar objetivos con validación final, no decir que faltó plazo si se aprueba corte de alcance; no ocultar obligaciones docentes |
| 11 | Referencias | Bibliografía actual | APA7, cotejo bidireccional cita↔referencia, solo fuentes utilizadas |
| 12 | Anexos | Evidencias extra/archivos completos | Anexo de índice/manifiesto de ZIP propuesto; acceso claro y trazable, previa aceptación docente |

## Resultados del material S01: preservar

- VM Ubuntu Desktop VMware VMnet8 `ens33 192.168.47.40/24` GW `.2`, SSH Ed25519 y postchecks limpios.
- Inventario HQ/S1 y S2 reservada, 9 VLAN y 2 WAN; VLAN 110/120+ACL en escenario aislado.
- FRRouting OSPF HQ↔S1 con HTTP WAN primaria/respaldo/restauración; LACP 2→1→2, active-backup de interfaces virtuales.
- OpenTofu metadata+Ansible candidatos FRR usados en B2 real, drift corregido en **copias de archivo**, no router vivo.
- Exporter/Prometheus NOC inicial alertas WAN firing/resueltas; no alerta externa final.
- 76 ICMP de una sesión y 12 eventos de otras, perfil estadístico/reglas deterministas; no IA/ML entrenada.
- 86 PNG y 7 CSV SHA256, 24 pruebas unitarias, CI exitosa; conservar como material técnico y de anexo.

## Reglas para documentos actuales

- El **único entregable académico escrito** es Documento 01, a incorporar iterativamente en Word institucional del usuario. Renombrar internamente «Informe final académico-técnico NETLAB360».
- El índice del Documento 02 antiguo es documentación **posentrega diferida**, no requisito académico ni bloqueo de S01/S02.
- Mantener una sola introducción, conjunto de objetivos y bibliografía en versión final. Reubicación sin duplicar párrafos ni perder citas.
- **No renumerar tablas/figuras en Git arbitrariamente:** Word del usuario es la autoridad para numeración definitiva; la guía oficial rige la **jerarquía de secciones**, con tablas/figuras continuas y notas APA7.
- Los ejemplos de slides «sistema de monitoreo» y «gestión de usuarios» no exigen construir esos productos; son didácticos.
- Evaluar completitud técnica del informe por casos verificables, no por conteo de páginas.
- Antes de editar 65 páginas, esperar transcripción de reunión para requisitos ambiguos, **pero iniciar avance técnico integrador entretanto** y no rehacer todo el texto en ausencia de nueva indicación.
