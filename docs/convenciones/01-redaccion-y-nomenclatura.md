# NETLAB360 — Convenciones de redacción del repositorio

**Aplicación:** todos los archivos Markdown actuales y futuros del proyecto, incluidos README, bitácoras, decisiones de arquitectura, criterios académicos, informes técnicos y notas de evidencias.

## Voz documental

Se utiliza una voz **técnica y natural**, como documentación del propio proyecto: `Se configuró…`, `Comprobé…` cuando se describe una operación personal, `Se verificó…`, `La prueba confirmó…`, `Quedó pendiente…`. Para decisiones del equipo, `Definimos…` o `Se acordó…`. No se introducen interlocutores externos como narradores de la bitácora.

En los documentos del proyecto **no** se escriben expresiones del tipo `el estudiante informó`, `el usuario confirmó`, `el asistente verificó`, `ChatGPT gestionó`, `se le pidió al estudiante` ni fórmulas equivalentes para narrar nuestro propio trabajo. Estas se sustituyen por descripciones comprobables del hecho, de su resultado, de la fuente técnica o de la decisión. **No atribuir a la docente afirmaciones no confirmadas:** distinguir `criterio indicado en clase`, `decisión de entrega comunicada` y `aprobación documentada` según el respaldo disponible.

**Excepciones:** `usuarios` como población de una VLAN, el `usuario final` de una interfaz, el servicio `ChatGPT` cuando sea objeto de estudio, nombres exactos de archivos, terminales, comandos, mensajes de error, resultados literales y citas bibliográficas. Nunca cambiar esos datos por razones de estilo.

## Organización y nomenclatura

- En la narración académica usar `fase 1`, `fase 2`, etc.; conservar `S01`–`S08` exclusivamente como códigos de laboratorio, capturas, scripts, rutas y referencias cruzadas técnicas.
- Capturas: `evidencias/capturas/faseN/SNN_XX_Descripcion_Tecnica.png`. Mantener mayúsculas en siglas FRR, OSPF, VLAN, WAN, LAN, HTTP, ACL, IaC y SoT; palabras descriptivas sin acentos y separadas por guiones bajos. Nombres previamente versionados se conservan cuando cambiarlos rompe trazabilidad; usar mapas de renombrado para excepciones históricas.
- Toda prueba se documenta con condiciones de inicio, comando o procedimiento, resultado observado, limitación y evidencia. No asumir éxito donde no consta registro.
- El Word/PDF oficial **no contiene un capítulo de anexos**. La entrega técnica final se realizará mediante un archivo `.tar` independiente autorizado para este proyecto, excluyendo secretos y estados locales de OpenTofu.
- Preservar cifras, fechas, issues, commits, hashes, URLs y salidas reales; nunca borrar historia técnica al normalizar la redacción.

## Revisión antes de confirmar cambios

1. Revisar si el texto narra una **decisión propia** o describe a un **usuario funcional**; solo cambiar el primer caso.
2. Corregir gramática después de sustituir frases y mantener tiempos verbales coherentes.
3. Comprobar los enlaces internos, rutas y nombres de archivos sin modificar código ni evidencias binarias.
4. Ejecutar la regresión Markdown/CI pertinente y documentar las decisiones de edición sin alterar el historial de Git.
