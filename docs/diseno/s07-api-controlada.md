# API local S07 v1

## Frontera de confianza

HTTP sobre socket Unix /run/netlab360-s07-api/api.sock, sin puerto TCP. SO_PEERCRED autentica UID del cliente (operador o root); el servidor protegido importa exclusivamente el broker y ejecutor instalados por root, bajo lock del preflight. No ejecutar simultáneamente el broker standalone. S08 podrá consumir la interfaz desde su backend local como operador; la aprobación administrativa permanece fuera del navegador. Root es de confianza, no se afirma separación de personas.

## Contrato

| Método | Ruta | Alcance |
|---|---|---|
| GET | /api/v1/health | Salud de interfaz |
| GET | /api/v1/incidents, /hypotheses, /runbooks | Snapshot de adquisición declarativo, fechado, histórico y no válido para autorizar |
| GET | /api/v1/rfcs/{id} o /execution | Estado protegido del RFC y ejecución |
| GET | /api/v1/rfcs/{id}/intent | Observación privilegiada actual y propuesta de restauración acotada si drift propio y watchdog activos |
| GET | /api/v1/audit | Últimos 100 registros protegidos del broker |
| POST | /api/v1/rfcs | Solicitud experimental fija, operador |
| POST | /api/v1/rfcs/{id}/restore-request | Solicitud de retorno, operador |
| POST | /api/v1/rfcs/{id}/approve-execute | Confirmación root ligada al cuerpo y consumo/ejecución conjuntamente |
| POST | /api/v1/rfcs/{id}/cancel | Cancelación de solicitud por operador |

Todas las escrituras exigen Idempotency-Key; reserva persistente previa, respuesta guardada, mismo cuerpo devuelve resultado histórico (no estado actual; consultar GET), cuerpo distinto 409, resultado incierto 409 y reconciliación sin repetir. No hay ejecución genérica ni autorización por telemetría de cliente. Los resultados de intención son puntuales y no confirman causalidad ni disponibilidad continua. La recomendación exacta S1/s1b 150→100 solo se ofrece con estado privilegiado coincidente con el drift propio. Aprobación y ejecución no se separan en dos llamadas para evitar reutilización y cambio de estado entre ellas. Límite 2048 claves sin borrado automático; servicio local y serializado, no API multiusuario de producción.

Implementación: [API](../../scripts/s07/api_s07.py), [snapshot](../../scripts/s07/api_snapshot_s07.py), [pruebas](../../tests/test_s07_api.py). Aceptación VM pendiente.

## Aceptación S07-008A–C (24/11/2026)

API Unix real validada con socket root:grupo operador 0660, UID ajeno denegado y cinco consultas HTTP 200. Ruta arbitraria 404, esquema inválido 400, acción arbitraria 409, falta de idempotencia 400, conflicto de clave 409 y autoaprobación 403. Repetición de solicitud y repetición tras cancelación devuelven respuesta histórica sin nueva ejecución; estado cancelado consultable por GET. SQLite íntegra, sin reservas inciertas al final. RFC 4eee684ed3a2430ab5911a65149897ac: conformidad inicial MET, drift propio S1/s1b 150 frente a 100, recomendación de restauración, aprobación humana, ejecución y retorno VERIFIED; dos consumos auditados y postcondiciones coincidentes. Se preservaron 21 namespaces, cuatro contenedores, siete servicios, gestión y 116 registros históricos. API detenida, cero watchdogs pendientes. 1258 pruebas ejecutadas, una omitida, cero fallos; CI 45340158821. Los resultados no acreditan disponibilidad continua ni remediación autónoma. La aceptación gráfica, informe y consolidación del catálogo siguen pendientes antes de cerrar la fase.
