# NETLAB360 — Matriz de objetivos internos históricos y criterios DOCENTES

**Revisión 16/10/2026.** Norma docente recibida: un informe de **mínimo 40 páginas**, 12 secciones; PowerPoint y demostración técnica. **Los C01–C11 de abajo fueron inventario INTERNO de validaciones transversales anteriores, NO 11 criterios oficiales entregados por la profesora.** Su trazabilidad se conserva para no omitir funcionalidades; ya no se exige cerrar todo en S01 para autorizar S02.

| Código | Objetivo o comprobación interna | Estado técnico de evidencia al corte S01 | Pendiente/fase principal |
|---|---|---|---|
| C01 | HQ/S1, VLAN/ACL, FRR OSPF y WAN redundante | VLAN/ACL HQ aisladas y HTTP WAN HQ–S1 por separado, correcto | Integración L2→WAN→servicio en S02; expansión S2 y redundancia equipo |
| C02 | LACP, dual-NIC, SoT/OpenTofu/Ansible | LACP 2→1→2 y bonding activo-respaldo virtual; IaC→FRR B2 real | Mediciones multistream S02/S05 y ownership live S03; NIC física no demostrada |
| C03 | API/NOC/Prometheus/alertas | Exporter live, reglas tres, dos alarmas firing/resueltas | Panel por sede/alertas con fuentes reales y entrega externa cuando alcance confirme |
| C04 | IA evaluable | 76 ICMP y 12 eventos independientes, estadística/reglas | Dataset etiquetado real y evaluación ML reproducible S06, si se mantiene |
| C05 | **UN informe académico-técnico de 12 apartados** | Borrador institucional de 65 páginas preparado, sin estructura oficial migrada | Mover capítulos según guía y ampliar Implementación y Pruebas |
| C06 | Pre/postcheck/recuperación/regresión | Pruebas por módulo y 24 tests offline; rollback satisfactorio | Prueba integrada reproducible y contraste esperado/observado |
| C07 | Integración redes/IaC/NOC/analítica | Módulos aislados y subconjuntos integrados | Escenario extremo a extremo, señales y datos coherentes |
| C08 | Capturas, trazabilidad, hash | 86 PNG y 7 CSV SHA256 publicados | Cuatro fotos suplementarias IaC y postcheck no publicados, sin repetir pruebas |
| C09 | **PowerPoint + demostración técnica y anexos** | Guía académica revisada y plan aprobado por usuario | Preparar SOLO después del informe; confirmar aceptación ZIP y entregar evidencia |
| C10 | Control de cambios/release | Git/CI operativos | Demostración de versión/PR/release donde corresponda |
| C11 | Portabilidad VM/OVA | VM limpia funcional y snapshot, **no OVA exportada** | Confirmar obligación OVA; sanitización/packaging cuando proceda |

## Confirmaciones y decisiones

- Guía docente ahora conocida: **un solo documento escrito de al menos 40 páginas**, PowerPoint y demostración. Requisitos narrativos y de pruebas documentados con precisión en guía transcrita.
- **Ya se confirmaron** revisiones parciales del proyecto el **30/10/2026** y **13/11/2026**, ZIP separado de anexos permitido junto al informe y demostración final **EN VIVO**. **Todavía se desconocen** fecha y duración finales, límites de diapositivas, cómputo de las 40 páginas, tamaño máximo del ZIP y obligación de OVA; Parcial 1 se atiende en otro chat.
- S01 continúa ABIERTA en issue #1 con resultados reales parciales; **retirada la prohibición anterior de S02 por falta de dos manuscritos**. Avanzar S02 y mantener trazabilidad de los 11 objetivos a su fase técnica lógica.
- Reducir opcionales sólo con aprobación según exigencias confirmadas; no fingir que topología única o ML ya funcionan.
- El manual técnico independiente #28 se mantiene como **posentrega, no parte de C05/C09 ni de la evaluación**.
- Portada Word confeccionada por el usuario; referencias APA7 y figuras/tablas contextualizadas. Mapa de los 65p.

**Criterio de aceptación académica:** cumplimiento del informe y su estructura, defensa de diseño, evidencias reproducibles y demostración explicada. La ponderación 72/100 NO ES calificación docente.
