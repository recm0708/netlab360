# Broker local de diagnóstico y transferencias

El socket Unix recibe una selección cerrada por conexión, con tamaño y plazo limitados. La identidad autorizada se obtiene de SO_PEERCRED y de la cuenta netlab360-s08-api. Los workers de datos usan la identidad separada netlab360-s08-worker, sin capacidades ni grupos suplementarios. Solo el supervisor entra en los namespaces autorizados.

## Alcance y supervisión

El protocolo V1 admite las 34 selecciones: diez diagnósticos y 24 transferencias TCP, UDP y contenido. El modo de progreso explícito admite las diez selecciones de contenido verificable. Se conserva el resultado final compatible y los límites de volumen y tasa de los perfiles existentes. No se aceptan comandos ni direcciones libres.

El supervisor comprueba rutas e identidades de ambos extremos y disponibilidad de puertos. El bloqueo root serializa los trabajos del broker; no abarca operaciones administrativas manuales externas. La unidad por conexión tiene timeout y límites de salida. Los workers de contenido escriben contadores reales acumulados independientes en un canal privado; el supervisor valida monotonicidad, rol, plazo y volumen. El cliente calcula tasas por intervalo a partir de diferencias de bytes y tiempo. Las muestras se conservan sin atribuir al receptor bytes observados únicamente en el emisor.

## Canal de progreso y cancelación

La selección con stream=true abre un canal de contenido. La respuesta accepted confirma la reserva; las tramas progress contienen muestras y la trama final contiene el resultado o el estado de cancelación. Solo el mismo canal admite CANCEL. El supervisor comprueba la petición durante la ejecución, termina sus propios grupos de procesos y verifica puertos libres antes de confirmar una cancelación. Una desconexión provoca limpieza cooperativa, pero el cliente no puede afirmar cancelación confirmada si no recibe la respuesta final. No se reintenta automáticamente.

## Instalación

La entrada exige ejecución root desde la copia instalada en /usr/local/libexec/netlab360/s08-broker. Comprueba propietarios, permisos, ancestros y conjunto exacto de módulos antes de importar. El socket pertenece exclusivamente a la cuenta API. No escucha TCP ni concede sudo al servicio web.

La actualización detiene el socket, comprueba ausencia de trabajos, conserva la versión anterior y copia los módulos verificados. El piloto utiliza estado privado aislado y conserva los resultados de cada ejecución. La persistencia al arrancar en frío, la conciliación de trabajos inciertos tras interrupción y la aceptación visual se verifican por separado. No se habilitan mutaciones de enlaces.
