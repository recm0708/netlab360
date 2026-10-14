# NETLAB360 — Documento 03: manual de usuario, administración y operación

**Propuesta de índice V0.1 para aprobación.** Documento único y acumulativo S01–S08. **Destinatarios:** docente/evaluador, estudiante/operador y futuro administrador del laboratorio. No es una transcripción de la bitácora ni un manual de implementación completo.

## Preliminares
- Portada institucional.
- Presentación, finalidad, destinatarios, convenciones de uso.
- Índice general automático único.
- Control de versión y alcance real por fase.

## Índice propuesto
1. **Introducción del manual**.
2. **Descripción general de NETLAB360** (funciones disponibles, alcance de la versión entregada, componentes no implementados).
3. **Requisitos para usar el laboratorio** (hipervisor, VM, RAM, red NAT, snapshot, permisos, SSH, navegador).
4. **Primer acceso y reconocimiento de la plataforma** (iniciar VM, SSH/Ubuntu Desktop, estructura lógica y variables seguras, comprobaciones iniciales).
5. **Interfaz de usuario y navegación** (página inicial/NOC, menús, panel por sede, enlaces, indicadores, alertas; documentar como operativa sólo la función que ya exista).
6. **Operaciones cotidianas**
   - 6.1 Verificar estado y disponibilidad.
   - 6.2 Seleccionar escenario HQ–S1 y distinguir red de gestión del laboratorio.
   - 6.3 Iniciar una simulación permitida.
   - 6.4 Consultar rutas, interfaces y conectividad.
   - 6.5 Visualizar métricas, historial de eventos y alarmas.
   - 6.6 Ejecutar caída controlada y recuperación de WAN (con advertencias y permisos).
   - 6.7 Consultar resultados de IaC/compliance si están expuestos al usuario.
   - 6.8 Interpretar diagnóstico por reglas B4 (sin llamarlo IA).
   - 6.9 Detener una simulación y comprobar limpieza.
7. **Procedimientos ilustrados paso a paso por caso de uso** (cada fase amplía capacidades del mismo manual).
   - Caso inicial S01: iniciar, ver NOC, lanzar/check WAN, observar respaldo y restauración; por ahora sólo ensayos aislados comprobados, no prometer un botón único.
   - Casos S02–S08: se añadirán al implementar sus respectivas funciones.
8. **Interpretación de mensajes, indicadores y estados** (UP/DOWN, OSPF Full, WAN-P/B, alert firing/resolved, modo offline, errores).
9. **Problemas frecuentes y solución segura** (servicio no disponible, SSH, IP, conflictos de puertos, rutas, credenciales, recuperación sin borrar recursos ajenos).
10. **Seguridad de uso y buenas prácticas** (privilegios, secretos, snapshot, no editar ens33/VMnet8, límites y uso educativo).
11. **Mantenimiento, actualización y respaldo** (revisión Git segura, inicio/cierre, snapshots, restauración y soporte; distinguir acciones probadas de las planificadas).
12. **Preguntas frecuentes, glosario y soporte**.
13. **Referencias** (cuando el manual cite normas/manufacturer docs externos, únicas y verificadas).
14. **Anexos operativos breves** (tabla comandos de consulta; las configuraciones extensas pertenecen al Documento 02).

## Formato de los procedimientos del manual
- **Para qué sirve** la función, **cuándo usarla**, **requisitos**.
- **Pasos numerados** desde la perspectiva de quien opera la aplicación; CLI sólo cuando el dashboard no tenga función equivalente.
- **Qué debería ver** el usuario, con figura de pantalla o terminal, preámbulo, título y Nota. APA7 si se necesita.
- **Qué significa** el indicador y cómo reconocer éxito/fallo.
- **Cómo cancelar o cerrar** sin afectar la gestión.
- Advertencias de seguridad si la acción cambia estado; no exponer contraseñas/tokens.
- Mantener índice automático único y numeración de figuras continua.

## Precisión del estado actual S01
- Sí hay VM Ubuntu, SSH, scripts de red y NOC/exporter básico, Prometheus con alerta real, análisis histórico por reglas; algunos usos requieren CLI.
- No se ha probado un panel multisede integral con botones para todos los flujos, un menú de administración final, Alertmanager receptor, IA/ML evaluada, redundancia de equipo física o VM OVA importada.
- Las funcionalidades se documentarán como **disponibles** sólo después de su prueba; el resto como pendientes o fuera de esta versión.
- Este documento no incluirá toda la secuencia de instalación del laboratorio (Documento 02), salvo requisitos del primer uso.

**Próxima sección tras aprobar índice:** 1. Introducción y 2. Descripción general para la versión disponible de S01.
