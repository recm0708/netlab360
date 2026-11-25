# Integración HTTP de trabajos de diagnóstico

Las rutas de trabajos se registran únicamente si la aplicación recibe un transporte explícito y una base de estado. El arranque normal no habilita estas rutas. La integración permite probar el contrato HTTP con un transporte sintético, sin tráfico ni cambios en la instalación existente.

## Contrato HTTP

| Método | Ruta | Función |
|---|---|---|
| GET | /api/v1/jobs/catalog | Consultar las 34 selecciones del contrato |
| POST | /api/v1/jobs | Registrar un trabajo y solicitar su despacho |
| GET | /api/v1/jobs/{job_id} | Consultar un trabajo propio |
| POST | /api/v1/jobs/{job_id}/cancel | Cancelar un trabajo que todavía está en cola |

Exigimos operador habilitado y sesión vigente. Las escrituras requieren origen exacto y comprobante CSRF. Limitamos el cuerpo y rechazamos claves repetidas, parámetros adicionales y selecciones fuera del catálogo. La identidad del actor procede de la sesión. No renovamos la sesión por sondeos. Un trabajo activo impide otro en la misma base.

El despacho se reclama una sola vez mediante la transición transaccional. Solo una respuesta de medición satisfactoria y concordante con la selección permite cerrar el trabajo. La salud observada es independiente del éxito de la ejecución. Si el transporte se desconecta, devuelve un rechazo, informa error o produce un resultado incompatible, conservamos RUNNING y registramos UNCERTAIN cuando es posible. No reintentamos automáticamente ni liberamos la reserva sin conciliación. Esta política es deliberadamente conservadora: incluso una respuesta BUSY queda pendiente de conciliación hasta distinguir de forma verificable la no ejecución y la limpieza.

## Cliente Unix y despliegue

El cliente real exige la cuenta netlab360-s08-api, valida propiedad y modo del socket, identidad del par servidor, tamaño de respuesta y plazo total de recepción. Solo envía la selección cerrada. No ejecuta sudo ni acepta rutas arbitrarias. El proceso web actual no se cambia de identidad en esta revisión.

Las pruebas HTTP utilizan bases temporales y resultados sintéticos identificados como tales. La validación del cliente Unix real se realiza independientemente con la cuenta dedicada. El despliegue web requiere preparar una instancia aislada con esa identidad y estado propio, verificar acceso a sus recursos, ajustar capacidades publicadas y aceptar recuperación de trabajos pendientes. El despacho posterior a la respuesta HTTP no es una cola durable independiente del proceso: un reinicio puede dejar un trabajo en cola o en ejecución. La cancelación activa, conciliación operacional tras interrupción, histórico y seguimiento en vivo permanecen pendientes. No se habilitan intervenciones de red.
