# NETLAB360 — Índice maestro OFICIAL del informe final académico-técnico

**Vigente desde 16/10/2026, REV0.3.** ÚNICO informe escrito requerido por las guías oficiales: **mínimo 40 páginas**. Portada institucional por el usuario. Estructura derivada de `1457-Formato Proyecto Final.pdf` y desarrollada con `1457-Elaboración del Trabajo Escrito.pdf`. El usuario preparó ya un borrador académico de **65 páginas** bajo numeración previa; **se debe migrar sin perder contenido**, no destruir ni recrear desde cero.

**Título formal de portada:** NETLAB360: Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede.
**Encabezado abreviado:** NETLAB360 | Redes Empresariales Multisede.

## Orden exigido por la profesora

1. **Portada:** UTP, facultad, carrera, asignatura, título, integrantes **nombre y cédula**, profesor, fecha.
2. **Introducción:** contexto, importancia en redes actuales, síntesis de problema y solución implementada. Sin comandos.
3. **Objetivos:**
   - Objetivo general: verbo en infinitivo, finalidad y resultado medible.
   - Objetivos específicos: diseño→implementación→comprobación, resultados verificables y vinculados con las pruebas.
4. **Planteamiento del problema:**
   - Situación y necesidad concreta.
   - Impacto, consecuencias y limitaciones.
   - Justificación de la solución propuesta; aquí se traslada la anterior sección de justificación separada.
5. **Fundamento técnico:** tecnologías efectivamente usadas y justificación de selección; VMware/Ubuntu, contenedores/netns, VLAN/802.1Q, ACL, FRR/OSPF doble WAN, LACP/bonding, SoT/IPAM, OpenTofu/Ansible, Prometheus/NOC y diagnóstico por reglas. Fuentes bibliográficas oficiales APA7. Evitar historia genérica inconexa.
6. **Diseño de la solución:**
   - Arquitectura lógica por sedes HQ/S1/S2 (S2 reservada hasta implementación), red de gestión VMnet8 aislada.
   - Componentes/roles, topología general, subredes/VLAN, dos enlaces WAN, protocolos, políticas, flujos.
   - Planos lógico/funcional de automatización, telemetría y analítica; figuras con nota que distingan diseño de práctica.
7. **Implementación:**
   - Entorno anfitrión, VM Ubuntu Desktop, recursos, SO, versiones verificadas, SSH y protección de gestión.
   - Secuencia de construcción REAL: inventario/IPAM→VLAN/ACL→routers FRR/OSPF→WAN/LACP/bonding→IaC/Ansible→telemetría/NOC→diagnóstico y siguientes módulos integrados.
   - Explicar las **configuraciones principales y scripts** (entradas, lógica, salidas pertinentes, criterios de reversión) con fragmentos imprescindibles y nombre/ruta de archivos; código completo al anexo, mediante ZIP autorizado.
   - No narrar cada comando de error del operador.
8. **Pruebas y validación:**
   - Baseline de cada escenario; objetivo y condiciones.
   - Resultado esperado; evento inducido (normal, falla o recuperación); **resultado observado cuantificado** y evidencia.
   - Pruebas de WAN primario/respaldo/restaurado, ACL permitida/denegada, LACP dos→uno→dos, IaC idempotencia/drift de archivos, alertas firing/resueltas, datos B4 y postchecks.
   - Distinguir pruebas de subtopologías S01 de futuras pruebas de extremo a extremo. Figuras/tablas preámbulo y nota APA7.
9. **Análisis de resultados:**
   - Comparación de lo esperado contra lo realmente conseguido, precisión/limitación de métricas.
   - **Problemas técnicos reales y mitigación** (p. ej. espera FIB después de OSPF Full; reglas Prometheus que no cargaban por ruta relativa), verificación correctiva, sin inventar causalidad.
   - Limitaciones: S2 no desplegada a la fecha del corte, falta L2→WAN en topología única, LACP virtual ≠ duplicación física, reglas deterministas ≠ IA evaluada, OVA no comprobada.
   - Mejoras priorizadas solo cuando respaldadas.
10. **Conclusiones y recomendaciones:** cumplimiento de objetivos, síntesis probada y recomendaciones específicas coherentes con estado final; evitar conclusiones anticipadas sobre capacidades pendientes.
11. **Referencias:** UN único listado APA7 de fuentes citadas, revisión bidireccional cita/referencia.
12. **Anexos:** descripción del paquete de fuentes/configuraciones/logs y evidencias, listado de archivos, versiones, SHA256 y modo de verificación; si la profesora admite ZIP separado, aportar índice dentro del escrito y ZIP físico fuera.

## Reglas de actualización

- No insertar ocho documentos dentro de uno. Agregar progreso de fases bajo 7 Implementación, 8 Pruebas, 9 Análisis; actualizar diseño y fundamentos solo si cambian tecnologías reales.
- **No alterar directamente la copia Word institucional de usuario.** Proporcionar bloques de revisión para migrar secciones; respetar numeración de figuras/tablas hasta cotejar DOCX/PDF vigente.
- Reporte S01 actual: base técnica aprovechable con 86 PNG/7 CSV, CI 24/24. **Quedan secciones 7 y 8 por ampliar** y orden 1–12 por ajustar. No afirmar informe final aprobado.
- Los criterios anteriores C01–C11 son **matriz interna**, no rúbrica oficial; la guía no los enumera como tales.
- Presentación después de cerrar informe y pruebas; manual técnico 02 **pospuesto para uso posterior**.

**Cruces:** [requisitos oficiales](../academico/00-criterios-docentes-y-hitos.md) · [plan de migración](../academico/01-migracion-borrador-a-formato-docente.md) · [paquete de anexos/demostración](../academico/03-anexos-y-demostracion.md).


## Control de entregas parciales (17/10/2026)

- **Título del semestral:** enviar al chat Teams, documentar respuesta y ajuste si la docente lo solicita. **Estado de envío no confirmado**, issue #46.
- **30/10/2026:** mostrar en Teams borrador institucional de Introducción, Objetivos y Planteamiento del problema, **sin diapositivas**. Responsable del grupo a designar (#47).
- **13/11/2026:** presentar fundamento técnico y diseño del mismo informe (#48).
- **Anexos por separado autorizados**; preparar ZIP de solo código/evidencias propias, sin documentos recibidos de clase ni secretos. Presentación final **EN VIVO** y posterior al informe.
