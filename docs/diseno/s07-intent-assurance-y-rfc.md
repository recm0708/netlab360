# Intent Assurance y solicitudes RFC S07

## Intención y cumplimiento

[Evaluador](../../scripts/s07/intent_assurance.py) separa conformidad de los ocho costos OSPF, selección FIB preferida, adyacencias y disponibilidad HTTP observada. La auditoría reutiliza el SoT candidato y el parser de [automatización Ansible S03](../../ansible/s03/README.md) mediante auditoria_costos_rca.py. No acredita disponibilidad extremo a extremo ni causalidad. Una configuración conforme puede coexistir con una ruta alternativa o una adyacencia degradada. Los registros de adquisición y auditoría tienen fechas propias; se exige una separación acotada para la política simulada.

## RFC y política de simulación

[Simulador](../../scripts/s07/rfc_simulacion.py) deniega por defecto todo salvo una propuesta de restauración de costo con drift explícito, objetivo permitido y estado operacional observado conforme. Vincula solicitud, acción, argumentos, recurso, costos observado/deseado, fechas y solicitante. Los roles TEST_REQUESTER y TEST_APPROVER son identidades ficticias; el ledger en memoria demuestra transiciones, separación lógica, vigencia, cancelación, consumo único y rechazo de parámetros alterados. Los registros no constituyen autenticación de usuarios, firmas, autorización real, persistencia resistente a reinicios ni exclusión mutua de procesos. El consumo devuelve exclusivamente SIMULATED_NOOP, sin ejecutar comandos.

## Gate pendiente

Antes de aceptar autorización humana operacional se requiere identidad autenticada, registro persistente protegido, transacciones atómicas de consumo y auditoría, aprobación humana explícita vinculada y controles de ownership/gestión actuales. #193 permanece abierta hasta comprobar su frontera de autorización; #194–195 integran ejecutor, bloqueo, watchdog y rollback. No utilizar los resultados simulados para conceder privilegios. [Pruebas](../../tests/test_s07_intent_rfc.py). Aceptación en VM pendiente.
