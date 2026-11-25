# Broker local de diagnóstico

La frontera Unix recibe una selección del contrato de trabajos, una por conexión, con tamaño y plazo de lectura limitados. La identidad autorizada se obtiene de SO_PEERCRED y de la cuenta dedicada netlab360-s08-api. No se acepta un identificador de usuario suministrado por el cliente, comando, dirección o parámetro libre. Se rechazan claves JSON repetidas, selecciones inválidas y perfiles aún deshabilitados.

## Primer alcance

Esta revisión admite exclusivamente las diez selecciones de ping corto y extendido, traceroute y HTTP. El contrato conserva las 34 combinaciones; las transferencias todavía no se despachan desde el broker. Se reutiliza el analizador de diagnóstico y se sustituye sudo por un invocador interno de argumentos fijos para namespaces autorizados. La respuesta distingue rechazo, ocupación y resultado de medición. No modifica SQLite ni el estado de la red.

Un archivo de bloqueo en un directorio propiedad de root limita a una ejecución por broker, incluso con varias conexiones. El bloqueo no abarca comandos manuales ejecutados por administradores fuera del broker. La unidad por conexión tiene límite de tiempo y terminación del grupo de control. El invocador dispone de timeout y terminación de su grupo de procesos; el límite de respuesta evita devolver resultados desmesurados. La limpieza ante terminación abrupta y el comportamiento bajo concurrencia real requieren validación operacional.

## Despliegue previsto

Las plantillas socket y service se versionan sin instalarlas ni activarlas en esta revisión. El socket Unix pertenece exclusivamente a la cuenta dedicada, no escucha TCP y no concede sudo. La entrada exige ejecución como root desde /usr/local/libexec/netlab360/s08-broker y comprueba propiedad y permisos de la copia instalada y sus ancestros antes de importar módulos. El paquete instalado no admite archivos adicionales. El intérprete aislado no carga código desde el repositorio editable ni el directorio personal.

La instalación, la creación de la cuenta de servicio, la validación de permisos, la activación y las pruebas reales se realizan en un bloque posterior. No se conecta aún FastAPI, no se habilitan transferencias y no se autoriza una mutación de enlaces. Para aceptar el despliegue se requieren pruebas de identidad real, concurrencia, timeout, limpieza y continuidad, además de la integración del estado de trabajos.
