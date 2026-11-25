# Integración HTTP de trabajos de diagnóstico

La aplicación habilita el contrato de trabajos únicamente con un transporte explícito y una base privada. El arranque habitual conserva sus rutas de lectura. La instancia dedicada adquiere un bloqueo exclusivo antes de abrir las rutas y comprobar trabajos interrumpidos.

## Contrato HTTP

| Método | Ruta | Función |
|---|---|---|
| GET | /api/v1/jobs/catalog | Consultar las 34 selecciones y alcance del transporte |
| GET | /api/v1/jobs | Consultar hasta 50 trabajos propios, activos primero |
| POST | /api/v1/jobs | Registrar y despachar un trabajo |
| GET | /api/v1/jobs/{job_id} | Consultar estado, muestras y resultado propios |
| POST | /api/v1/jobs/{job_id}/cancel | Solicitar cancelación de un trabajo en cola o de contenido activo |

Exigimos operador habilitado y sesión vigente. Las escrituras requieren origen exacto y comprobante CSRF. Limitamos cuerpo y parámetros. El actor procede de la sesión, no del navegador. Los sondeos no renuevan la sesión.

## Ejecución y recuperación

El despacho reclama una reserva transaccional una sola vez. Los diagnósticos e iPerf3 conservan el protocolo de respuesta final. El canal de contenido permite muestras independientes del emisor y receptor, con cancelación activa después de la aceptación de la conexión. Cancelación solicitada y cancelación confirmada son estados distintos: la plaza solo se libera con respuesta final que confirme limpieza. Si falta confirmación, conservamos RUNNING con calidad UNCERTAIN; no reintentamos automáticamente.

Al iniciar bajo el bloqueo de instancia, cancelamos trabajos en cola abandonados y marcamos los trabajos en ejecución como inciertos. Nunca inferimos limpieza por tiempo transcurrido. La conciliación de una ejecución incierta requiere comprobación operacional independiente. No se habilita un desbloqueo administrativo por HTTP.

## Vista de pruebas y datos

La vista de pruebas ofrece selección cerrada de acción, ruta y perfil. Los paneles muestran contadores medidos, tasa por intervalo y avance de recepción real cuando existe volumen y observación. Los intervalos de iPerf3 se presentan al finalizar y no como muestras en vivo. Conservamos el historial propio, el resultado detallado y exportación JSON o CSV de las muestras mediante identificadores únicos. No mostramos integridad confirmada de contenido parcial ni estimamos avance a partir del tiempo.

La instancia de validación utiliza el puerto local 9145 y su origen exacto, con una base independiente. El servicio existente permanece en el puerto 9140. El piloto verifica el flujo HTTP real y reabre el historial, mientras que la navegación visual y el despliegue definitivo requieren aceptación adicional.
