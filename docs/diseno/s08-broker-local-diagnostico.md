# Broker local de diagnóstico y transferencias

La frontera Unix recibe una selección del contrato de trabajos por conexión, con tamaño y plazo de lectura limitados. La identidad autorizada se obtiene de SO_PEERCRED y de la cuenta dedicada netlab360-s08-api. No se acepta un identificador de usuario suministrado por el cliente, comando, dirección o parámetro libre. Se rechazan claves JSON repetidas y selecciones inválidas.

## Alcance y supervisión

El broker admite las 34 selecciones del contrato: diez diagnósticos y 24 transferencias TCP, UDP y de contenido reproducible. Los perfiles conservan sus objetivos, plazos, rutas y tamaños cerrados. Se reutilizan los analizadores de ambos extremos; se comprueban las identidades, rutas de ida y retorno y disponibilidad de puertos antes de iniciar cada transferencia. Los workers de datos se ejecutan con una identidad distinta, netlab360-s08-worker, sin grupos suplementarios ni capacidades. Solo el supervisor instalado entra en los namespaces.

El bloqueo de propiedad root serializa todos los trabajos del broker. Cada proceso de transferencia tiene timeout, grupo propio y archivos temporales de salida limitados; la unidad por conexión termina el grupo de control al detenerse. El tiempo máximo de la unidad es de 700 s para admitir el mayor perfil de contenido. La respuesta sigue limitada a 256 KiB. El bloqueo no abarca operaciones manuales de administradores externos.

## Instalación y actualización

La entrada exige ejecución como root desde /usr/local/libexec/netlab360/s08-broker y comprueba propiedad y permisos de la copia instalada y sus ancestros antes de importar módulos. El paquete instalado no admite archivos adicionales. El intérprete aislado no carga código desde el repositorio editable ni el directorio personal. El socket pertenece exclusivamente a la cuenta API, no escucha TCP ni concede sudo. La cuenta worker no puede acceder al socket.

La actualización requiere detener el socket y verificar que no hay instancias activas, conservar la versión instalada anterior, incorporar la cuenta worker bloqueada y copiar únicamente los archivos de la revisión verificada. Se comprueban las unidades antes de reactivar el socket y se conserva la posibilidad de revertir los archivos a la revisión anterior. La persistencia y el arranque en frío se validan por separado.

La terminación administrativa de una instancia no constituye todavía cancelación desde la interfaz. La desconexión del cliente no cancela automáticamente la medición. No se habilitan rutas HTTP, seguimiento en vivo ni intervención de enlaces en este incremento. Las pruebas de instalación deben distinguir mediciones reales, resultados parciales, errores y limpieza. El contrato no afirma disponibilidad web hasta integrar y validar el gestor de trabajos y la autorización HTTP.
