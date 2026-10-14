# NETLAB360 — Matriz de cierre de Fase S01

**Fecha de corte:** 13/10/2026 después de 23:35. **Avance técnico estimado:** 72/100, no nota oficial. **Criterio:** documentación creada ≠ criterio rubricado aprobado.

## Verificado
- Lote06 publicado, commit b410548f9338233c8dc23816ce78a11d67bb2896; 86 PNG y 7 CSV; SHA256 e integridad OK, Git sincronizado, cero subcarpetas.
- Regresión 24/24 tests y GitHub Actions exitosa, incluido run 38511477595.
- Último postcheck 23:35:02: Docker/netns vacíos; gestión ens33 .40/24, gateway .2, tres servicios activos.
- Resúmenes desde logs originales de IaC 01/03/04/06 generados con código0; las imágenes finales todavía por recibir.
- Borradores versionados informe académico, bitácora técnica y manual; pendientes de edición académica final.

## Ruta crítica, en orden de entrega
1. **Confirmación docente:** cotejar la guía oficial, extensión de documentos y obligatoriedad de los 11 criterios del issue #1 para S01. No reducir unilateralmente.
2. **Documentación:** portada, integrantes/grupo/docente, esquema APA 7 real, referencias verificadas, selección e inserción de capturas con pies; actualizar Word de los tres documentos.
3. **Evidencia faltante:** cuatro fotografías IaC recuperadas y postcheck LOTE06 adicional; auditarlas y publicarlas sin repetir ensayos.
4. **Pruebas técnicas indispensables:** consolidar el ejercicio L2→WAN→servicio y evento visible si la guía lo exige; cubrir respaldo de equipo/servidor si es obligatorio, o registrar restricción de alcance aprobada.
5. **Diagnóstico IA:** si es criterio exigido en S01, reunir sesiones independientes etiquetadas y evaluar modelo separado de reglas; no inventar precision/recall/F1.
6. **Observabilidad:** si se exige, completar receptor/Alertmanager y estado por sede. De otro modo registrar pendiente planificado, condicionado a autorización docente.
7. **Release/VM:** sanitizar tokens e historial sensible, verificar archivos y versión, crear tag/release y exportar/reimportar la VM; comprobar SHA256, si requerido ahora.
8. **Cierre formal:** actualizar matriz con evidencia del alcance exacto, informe/manual definitivos y issue #1 solo tras verificación y aceptación.

## Distinciones obligatorias
- Informe borrador no es entrega con normas APA terminadas.
- Captura de resultado histórico no es nueva ejecución del laboratorio.
- Cero señales en una sesión sana no prueba precisión de detector ML.
- LACP/active-backup con veth no demuestra NIC o switch físico duplicado.
- OpenTofu registra metadata; el script B2 despliega routers con archivos Ansible.
- Estado de Git limpio y VM de laboratorio limpia no equivalen a imagen OVA sanitaria lista.

## Decisiones pendientes del usuario
- Plantilla/rúbrica docente de S01, fechas exactas de entrega y extensión máxima/mínima.
- Datos institucionales y autoría de portada.
- Si la OVA debe entregarse por S01 o únicamente al final de semestre.

**Política desde este corte:** suspender desarrollo B4 extra y trabajar por entregables S01, con una sola tanda de pruebas indispensables antes de release. Mantener pendientes documentados honestamente.
