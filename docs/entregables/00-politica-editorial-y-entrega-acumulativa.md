# Criterios editoriales y entrega de NETLAB360

Desarrollamos NETLAB360 en **un único informe académico** y un paquete técnico separado. La escritura documenta procedimientos reproducibles, resultados observados, limitaciones y decisiones de diseño sin mezclar planificación con pruebas concluidas.

## Informe institucional

El manuscrito mantiene un mínimo de 40 páginas según el criterio docente registrado y presenta: portada, índices, introducción, objetivos, problema, fundamento técnico, diseño, implementación, pruebas, análisis, conclusiones y recomendaciones, y referencias. Seguimos APA 7 para citas y fuentes bibliográficas; los resultados propios de laboratorios se respaldan por sus registros y figuras.

No utilizamos un capítulo de anexos en el cuerpo del informe. Los archivos de configuración, scripts, pruebas, datos y manifiestos se seleccionarán para un archivo **TAR técnico independiente**, sujeto a verificación SHA-256, exclusión de credenciales y extracción de prueba. No interpretamos la existencia de archivos en Git como entrega académica efectiva.

## Trazabilidad y voz documental

La documentación se redacta con voz profesional del equipo: «configuramos», «comprobamos», «registramos» o voz técnica impersonal. Presentamos datos verificables, distinguiendo entre escenarios diseñados, implementados, probados y pendientes. Los documentos vigentes tienen una función definida; las notas históricas se conservan como registro, no como instrucciones actuales.

Las figuras y tablas deben tener numeración coherente con la versión del documento, título preciso y notas únicamente cuando aporten contexto. No duplicamos capturas ni repetimos resultados solo para aumentar extensión.

## Precauciones técnicas

No equiparamos recursos `terraform_data` con provisión de redes externas, reglas de monitoreo con IA entrenada, conmutación lógica con redundancia física ni SLI de recolección con SLA contractual. En S05 el núcleo técnico está verificado, pero la publicación Git del material y su incorporación al informe son tareas documentales distintas.

[Criterios docentes](../academico/00-criterios-docentes-y-hitos.md) · [Control del manuscrito](01-proyecto-investigacion-maestro.md) · [Convenciones de redacción](../convenciones/01-redaccion-y-nomenclatura.md).
