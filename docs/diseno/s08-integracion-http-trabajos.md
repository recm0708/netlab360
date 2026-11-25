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

El historial identifica el tipo de prueba y su configuración legible, sin sustituir los identificadores del contrato. Presentamos fechas con el formato y la zona horaria Panamá de la consola; conservamos UTC en la exportación. La consulta de un resultado desplaza el foco al panel seleccionado y mantiene la selección durante el sondeo. Las pruebas ICMP, traceroute y HTTP presentan sus mediciones específicas sin paneles de transferencia vacíos. El CSV incluye identidad de prueba, configuración, resumen y muestras observadas; el JSON conserva el documento original.

La instancia de validación utiliza el puerto local 9145 y su origen exacto, con una base independiente. El servicio existente permanece en el puerto 9140. El piloto verifica el flujo HTTP real y reabre el historial, mientras que la navegación visual y el despliegue definitivo requieren aceptación adicional.

## Convenciones visuales compartidas

Las tablas propias de la consola, incluidas las vistas futuras, heredan una distribución compacta según el contenido, alineación horizontal izquierda y vertical centrada, separación uniforme, cabeceras visibles y desplazamiento horizontal cuando el espacio sea insuficiente. La cabecera Fecha y hora no repite la zona local; las fechas mantienen el reloj de Panamá y la exportación conserva UTC. Swagger mantiene su distribución especializada con celdas compactas y la paleta común.

El único acceso oficial para el equipo será la consola en 9140. Las instancias de validación en 9145 son temporales y no constituyen otro producto. La consolidación definitiva preservará identidades autorizadas, históricos, fuentes y contratos internos; las páginas redundantes se retirarán después de validar equivalencia y recuperación. Los recursos locales de Swagger y las demás dependencias visuales deben estar disponibles en la instancia persistente.
