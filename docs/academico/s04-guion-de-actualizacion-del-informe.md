# NETLAB360 — Guion documental de la fase 4 para el informe académico

**Estado:** documento de trabajo interno, NO reemplaza el Word/PDF oficial. Base académica actualmente revisada: `1457-Proyecto Semestral_borrador3.2.pdf`, 94 páginas, fases 1–3. La maquetación, las secciones y numeración definitiva se comprobarán en Word antes de insertar el texto. Se deben conservar los estilos y APA 7 ya existentes.

## Resultados verdaderos disponibles desde el primer lote S04

Durante la fase 4 se extendió el prototipo de observabilidad de la primera fase a un colector independiente para las tres sedes de la infraestructura multisede. El nuevo componente consultó la información declarativa del SoT `candidate` y distinguió el estado esperado de los routers, WAN y VLAN de la observación real de los contenedores FRRouting, sin aplicar modificaciones al laboratorio. Una prueba verificó las sedes HQ, S1 y S2, ocho extremos WAN y nueve interfaces VLAN, con 25 series de métricas y una muestra de 3,86 segundos de antigüedad.

Prometheus 3.7.0 se ejecutó en una instancia aislada con `127.0.0.1:9091`, obteniendo correctamente métricas del colector `127.0.0.1:9110`. El estado del objetivo y de la fuente fue `UP`, mientras que las reglas no generaron alertas por la ausencia intencional de los routers, ya que sus interfaces permanecían sin desplegar. Se probaron cuatro condiciones sintéticas de alertas con `promtool`, diferenciando consulta fallida, observación desconocida, WAN administrativamente desactivada y subinterfaz VLAN administrativamente desactivada; esas pruebas sintéticas no constituyen incidentes reales de la topología.

El primer NOC centralizado, accesible solamente mediante loopback y túnel SSH, integró información de las tres sedes, interfaces WAN/VLAN y alertas de Prometheus. Se verificaron una vista central y una vista específica de S1; el tablero mostró `OFFLINE` con fuente fresca, cero alertas activas y los estados no observados de las interfaces. Se comprobaron 20 pruebas automatizadas S04 y una detención ordenada de exporter, Prometheus y NOC con recuperación del estado administrativo del host.

**Limitación obligatoria:** todo este primer bloque se ejecutó con la infraestructura S02 intencionalmente desmontada. No puede afirmarse todavía detección de falla WAN real, vecinos OSPF operativos, servicio HTTP monitorizado, histórico formal, notificación externa ni cálculo de SLI/SLO.

## Ubicación futura en el manuscrito

- **Implementación (capítulo 5, apartado posterior al 5.5 de fase 3):** arquitectura exporter S04 → Prometheus S04 → NOC, enlaces HTTP loopback 9110/9091/9120, SoT declarativo y protecciones de red.
- **Pruebas (capítulo 6, apartado posterior a 6.8):** tabla de ejecución de 20 pruebas offline, Prometheus `up=1`, series=25, observación 3,86 s, 0 alertas con topología desmontada, validación de API y postcheck. Añadir luego la matriz de pruebas con red activa, incidente y recuperación sin inventar cifras.
- **Análisis (capítulo 7):** diferenciar `OFFLINE` esperado, `UNKNOWN` por fuente no confiable y `DOWN` administrativo medido; distinguir funcionalidades del NOC implementadas de SLI/SLO históricos que se prueben después.
- **Conclusiones y recomendaciones (capítulo 8):** integrar avances propios de la fase 4 tras aceptar sus puertas G1–G6; evitar describirla como finalizada mientras siga abierta.
- **Figuras:** las siete capturas S04_01–06 se conservan como evidencia; seleccionar las más representativas en el texto, con número, título, nota y preámbulo según APA 7, sin asumir numeración definitiva antes de cotejar el Word. El informe termina en **Referencias**, no tendrá anexos; código completo y registros irán en TAR externo.

## Puertas pendientes para completar este guion

Validación de la red desplegada y OSPF/HTTP, scrape y panel con WAN/VLAN activas, incidente real con corte/restauración y timestamps, tratamiento de reinicios/retención de métricas, SLI/SLO con definiciones y ventanas verificables, notificación externa solo si se adopta y prueba y cierre limpio con nuevas evidencias S04_07–S04_12.

**Trazabilidad:** [bitácora real](../sesiones/2026-10-26-s04-noc-multisede-offline.md), [plan de cierre](../operaciones/s04-cierre-observabilidad-multisede.md), [issue #4](https://github.com/recm0708/netlab360/issues/4).
