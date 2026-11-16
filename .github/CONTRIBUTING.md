# Convenciones del proyecto NETLAB360

## Documentación

Los documentos técnicos utilizan un título principal y secciones breves y consistentes: **Descripción**, **Implementación o arquitectura**, **Validación**, **Limitaciones** y **Documentación relacionada**, según corresponda. La redacción representa el trabajo realizado por el equipo, sin narrar conversaciones ni procedimientos internos de seguimiento.

Cada carpeta de capturas contiene únicamente sus archivos PNG y un documento `README.md` con la cantidad y los nombres de las imágenes.

## Código

Los módulos Python incorporan una descripción de su responsabilidad y documentan las funciones cuya lógica, entradas o efectos no sean evidentes. Los scripts Bash identifican propósito y alcance; antes de operaciones destructivas explican las condiciones de seguridad.

Los comentarios describen **por qué** se realiza una acción o qué condición se protege, evitando repetir literalmente el comando. Los nombres de variables y funciones deben ser descriptivos y las secciones del código mantenerse cohesionadas.

## Estructura y compatibilidad

Las rutas de scripts, inventarios y servicios se modifican únicamente cuando también se actualizan las referencias, configuraciones y pruebas dependientes. No se introducen cambios de rutas que impidan iniciar el laboratorio.

La incorporación de funcionalidades S06–S08 mantendrá estas convenciones y diferenciará entre comportamiento implementado y trabajo pendiente.

## Verificación

Antes de integrar cambios se revisan la sintaxis correspondiente, los tests aplicables, los enlaces documentales y la ausencia de credenciales o datos personales.
