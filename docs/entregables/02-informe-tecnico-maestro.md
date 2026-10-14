# NETLAB360 — Documento 02: memoria técnico-práctica de implementación y laboratorios

**Propuesta de índice V0.1 para aprobación.** Documento único acumulativo S01–S08. **Propósito:** demostrar de forma auditable lo que realmente se instaló, configuró, ejecutó y comprobó. La plantilla Word institucional y su índice automático serán proporcionados/compuestos por el usuario.

## Preliminares
- Portada institucional.
- Resumen técnico ejecutivo (del laboratorio y del corte).
- Índice general automático único.
- Alcance del entorno y política de evidencia (sin contraseñas ni tokens).

## Índice propuesto
1. **Introducción técnica** (relación con Documento 01, objetivos del laboratorio).
2. **Objetivo general y objetivos específicos de implementación** (no duplicar literalmente objetivos de investigación).
3. **Alcance, condiciones de seguridad y metodología de laboratorio** (precheck, prueba, limpieza, rollback, capturas, SHA/commits).
4. **Inventario de infraestructura y ambiente** (VMware, Ubuntu, recursos, versiones, VMnet8/ens33, herramientas).
5. **Arquitectura de laboratorio y topologías efectivas** (diagrama real, separación gestión/topologías temporales; IPAM y tabla de enlaces).
6. **Bitácora cronológica y ejecución por fases**
   - 6.1 S01 — Preparación y verificación de base B0.
   - 6.2 S01 — Source of Truth, IPAM y topología B1.
   - 6.3 S01 — VLAN, 802.1Q, ACL, HTTP local B2-L2.
   - 6.4 S01 — FRR, OSPF WAN primaria/respaldo, HTTP intersede B2-L3.
   - 6.5 S01 — LACP y active-backup virtual, sin atribuir NIC físicas.
   - 6.6 S01 — OpenTofu/Ansible y configuraciones FRR; idempotencia y drift de archivo.
   - 6.7 S01 — Exporter/NOC/Prometheus y alertas verificadas B3.
   - 6.8 S01 — Datos reales, estadísticas, diagnóstico por reglas y pruebas CI B4.
   - 6.9 S01 — Auditoría de evidencia, integridad Git, limpieza y cierre parcial.
   - 6.10 S02–S08 — Procedimientos ordenados a incorporar al realizarse cada fase (reservado).
7. **Pruebas integrales, matriz de aceptación y reproducibilidad** (prueba/paso/salida/figura/commit, éxito o pendiente; sin falsos 100%).
8. **Observaciones técnicas, limitaciones y gestión de incidentes** (adaptaciones reales y decisiones; evitar relatos innecesarios sobre errores personales).
9. **Seguridad, respaldo, restauración y sanitización de VM** (distinguir procedimiento probado y pendiente).
10. **Resultados finales y validación contra objetivos de laboratorio** (actualizable cada fase).
11. **Recomendaciones técnicas**.
12. **Conclusiones técnicas**.
13. **Referencias técnicas** (únicas y citadas, cuando se utilicen normas/manuales externos).
14. **Anexos técnicos** (logs largos, scripts relevantes, hashes, tablas extensas sólo cuando sea necesario).

## Plantilla obligatoria por práctica o sublaboratorio

- **Objetivo verificable** y alcance real.
- **Prerrequisitos y línea base**: snapshot, versiones, estado Docker/netns/red/servicios.
- **Topología o archivos de entrada** y controles de seguridad.
- **Implementación paso a paso**: comandos EXACTOS que funcionaron (separados de salidas esperadas), ruta/archivo, propósito breve.
- **Evidencia de ejecución y validación**: resultado observado, código de retorno, contadores, tiempos de prueba si hay respaldo documental.
- **Figura(s) seleccionadas**, con preámbulo, identificación y nota APA7 de fuente/interpretación cuando proceda.
- **Pruebas negativas** si aportan valor: denegación ACL, caída WAN, drift de archivo, etc.
- **Limpieza, recuperación, postcheck** y estado final.
- **Trazabilidad**: script, log, hash/manifiesto y commit/issue (sin revelar credenciales).
- **Límites y estado del criterio**: completado/parcial/pendiente.

## Norma de estilo y evidencia
- No incrustar 86 capturas automáticamente: escoger sólo las decisivas, con otras disponibles en GitHub y anexos.
- No traducir una salida de terminal ficticia a resultado real; indicar si es comando de reproducción no reejecutado.
- Las figuras y tablas se presentan con preámbulo, llamada previa en texto y notas APA 7 cuando corresponde.
- Evitar duplicar el fundamento teórico de Documento 01 o la guía de uso cotidiano de Documento 03.
- Registrar red de administración y limpieza antes/después de las fallas.
- Numeración continua de figuras y tablas en este documento.
- El bloque S01 no se declarará cerrado sólo por el conjunto de ensayos parciales; necesita aceptación de criterios de fase o ajuste rubricado.

**Próxima sección tras aprobar índice:** 1. Introducción técnica y 2. Objetivos del laboratorio de S01.
