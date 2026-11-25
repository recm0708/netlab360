# Intent Assurance y autorización RFC

## Intención y cumplimiento

El [evaluador](../../scripts/s07/intent_assurance.py) distingue conformidad de los ocho costos OSPF, selección FIB preferida, adyacencias y disponibilidad HTTP observada. La auditoría reutiliza el SoT candidato y el parser de [automatización Ansible](../../ansible/s03/README.md). Una configuración conforme puede coexistir con una ruta alternativa o una adyacencia degradada; no acredita disponibilidad extremo a extremo ni causalidad. La falta de información se mantiene como UNKNOWN.

## Validación aislada y de lectura

| Implementación | Control | Resultado autorizado |
|---|---|---|
| [Simulador RFC](../../scripts/s07/rfc_simulacion.py) | Roles ficticios, vigencia, parámetros, cancelación, consumo único | SIMULATED_NOOP |
| [Broker preview](../../scripts/s07/rfc_protegido_preview.py) | Socket Unix, SO_PEERCRED, SQLite protegido, plazo de 300 s y consumo atómico | PROTECTED_NOOP |
| [Broker live-read](../../scripts/s07/rfc_live_read.py) | Preflight real al solicitar, aprobar y consumir; edad máxima 10 s; vigencia de 120 s | LIVE_AUDIT_VERIFIED |

Los registros de simulación no constituyen autenticación real. El preview acredita persistencia tras reinicio del broker, consumo único bajo concurrencia y separación de privilegios, sin ejecutor de red. El broker live-read no recibe evidencia del cliente: vincula identidad Docker, boot ID, gestión, costos, adyacencias y rutas; registra tres observaciones coincidentes en 9,102396 s. Rechaza restauración sin drift y no autoriza modificaciones.

## Broker operacional

El [broker operacional](../../scripts/s07/rfc_ospf_operacional.py) reutiliza el ejecutor OSPF protegido. SO_PEERCRED identifica al solicitante y al aprobador (UID 0). Cada RFC vincula acción, argumentos, recurso, snapshot privilegiado, sesión, identidad y plazo monotónico. La aprobación se consume bajo el lock del preflight antes de invocar el ejecutor, que revalida estado, identidad y watchdog.

El alcance fijo es R-S1/s1b: estímulo 100→150 y restauración 150→100 mediante una segunda aprobación con identificador distinto. El retorno de emergencia se autoriza previamente; cancelar la restauración no revoca el watchdog. Se conserva la auditoría de aprobación y rechazo, sin aceptar shell, objetivos alternativos ni telemetría de cliente como evidencia de autorización.

## Validación

Se comprobaron ocho costos conformes, FIB y adyacencias en intención y HTTP observado disponible, cinco escenarios sintéticos de intención y 12 rechazos de política. El preview validó autoaprobación rechazada, persistencia, consumo concurrente único y cancelación. La lectura privilegiada verificó tres observaciones coherentes y rechazó cambios.

El broker operacional completó 15/15 pruebas aisladas y una intervención real con dos aprobaciones de UID 0 y solicitante UID 1000. Se rechazaron acción arbitraria, autoaprobación, alteración de argumentos, solicitud cancelada y reutilización. El vencimiento se probó con backend aislado. El ciclo 100→150→100 terminó VERIFIED, con restauración HUMAN_APPROVED, dos consumos auditados y postcondiciones coincidentes. Se conservaron 21 namespaces, cuatro contenedores, siete servicios y 116 registros. La regresión comprendió 1242 pruebas, una omitida y ninguna fallida.

## Limitaciones

La separación acreditada corresponde a privilegios de Linux, no a dos personas independientes. Root es de confianza; no se demuestra resistencia a un administrador malicioso. La ejecución administrativa directa se conserva como mecanismo separado del broker. La API reutiliza la frontera protegida; la recomendación por sí misma no autoriza cambios. No se acredita disponibilidad continua.

## Documentación relacionada

[Pruebas de intención](../../tests/test_s07_intent_rfc.py) · [Pruebas del broker operacional](../../tests/test_s07_rfc_ospf_operacional.py) · [Watchdog](s07-intervencion-ospf-y-watchdog.md) · [API](s07-api-controlada.md) · [Evidencias](../../evidencias/capturas/fase7/README.md).
