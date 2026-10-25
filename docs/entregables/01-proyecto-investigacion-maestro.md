# NETLAB360 — Índice maestro de trabajo del informe académico-técnico

**Actualizado el 25/10/2026.** Un único informe institucional, mínimo **40 páginas**, con estructura técnica continua. La versión de referencia recibida más reciente es `1457-Proyecto Semestral_borrador3.pdf`, de **79 páginas**. El capítulo de la fase 3 sigue pendiente de incorporación al documento, aunque su implementación y pruebas técnicas están comprobadas. Conservar su Word original y proporcionar correcciones por chat; no recrear el archivo sin solicitud.

**Título comunicado por Teams el 17/10/2026:** «Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede». Su aprobación docente sigue por confirmar. **Nombre/encabezado abreviado:** NETLAB360 | Redes Empresariales Multisede.

## Orden editorial vigente del informe

- Portada e índice general institucional.
- Introducción.
- **1. Objetivos** (objetivo general y específicos).
- **2. Planteamiento del problema** (problema y justificación).
- **3. Fundamento técnico** (virtualización/contendores, Linux networking, VLAN, OSPF/FRR, LACP, SoT, OpenTofu, Ansible, observabilidad y diagnóstico; citas verificables).
- **4. Diseño de la solución** (HQ/S1/S2, cuatro WAN, nueve VLAN y sus direcciones, protección VMnet8, módulos pendientes; **Figura 1 debe mostrar la topología real, no texto provisional**).
- **5. Implementación**: 5.1 entorno, 5.2 metodología en **ocho fases internas**, 5.3 fase 1 (antecedentes experimentales) y 5.4 fase 2 (integración multisede y desmontaje seguro); nuevas fases se incorporan progresivamente sin duplicar informes.
- **6. Pruebas y validación** (propósito, baseline, esperado/observado, evidencia y recuperación; diferenciar pruebas de red y offline).
- **7. Análisis de resultados** (interpretación de resultados, limitaciones reales; sin atribuir disponibilidad continua o IA no probadas).
- **8. Conclusiones y recomendaciones**, actualizadas conforme avance la implementación.
- **Referencias**, listado único APA 7, cierre del informe.

**Importante — modalidad docente precisada por estudiante 25/10/2026:** **no insertar capítulo/sección de anexos en el Word**. Los scripts, YAML/JSON, HCL, Ansible, configuraciones, pruebas y evidencias técnicas necesarias se entregarán mediante **un único `.tar` independiente**. La guía académica histórica relaciona doce piezas y contempla anexos, pero la modalidad externa se registró en [criterios](../academico/00-criterios-docentes-y-hitos.md) y [plan TAR](../academico/03-anexos-y-demostracion.md). No crear ZIP ni índice ficticio de anexos dentro del informe.

## Disciplina de actualización y evidencia

- En la narración utilizar **fase 1, fase 2, fase 3**; mantener identificadores S01/S02/S03 cuando son nombres reales de scripts, rutas y evidencias. Ocho fases son hitos internos, no ocho informes separados.
- S01 histórico incluyó LACP virtual, dos WAN HQ/S1, pruebas de automatización candidata, Prometheus y diagnóstico determinista. S02 integró funcionalmente **tres routers, cuatro WAN, nueve VLAN, HTTP y ACL**; desmontada deliberadamente el 23/10 con respaldos.
- S03 cuenta con SoT, auditoría real Ansible y drift/reconciliación de FRR comprobados, pero **OpenTofu metadata-only y CI/PR siguen sin aceptación real**.
- Ninguna captura o tabla implica resultado diferente al observado. Figuras y tablas con preámbulo, título, nota y referencias cruzadas correctos. El borrador 2.5 tenía **Figura 1 pendiente**, y se registró haber aplicado correcciones editoriales sin facilitar aún nuevo PDF verificable.
- Conservar historial técnico de evidencias SHA-256; nunca insertar secretos o archivos docentes recibidos de terceros en GitHub ni en TAR distribuible.
- No cerrar issues técnicas por un borrador narrativo; exigir resultados comprobados, trazabilidad, checklist y aceptación del alcance.
- **30/10/2026:** mostrar en Teams introducción, objetivos y planteamiento, sin PPT adicional (#47). **13/11/2026:** fundamento y diseño (#48). Presentación y demostración final según fecha docente por confirmar. Manual independiente pospuesto.

**Vínculos:** [criterios docentes](../academico/00-criterios-docentes-y-hitos.md) · [TAR externo](../academico/03-anexos-y-demostracion.md) · [fase 2 #2](https://github.com/recm0708/netlab360/issues/2) · [fase 3 #3](https://github.com/recm0708/netlab360/issues/3) · [entrega TAR #45](https://github.com/recm0708/netlab360/issues/45).
