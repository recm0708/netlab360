# Convenciones de contribución de NETLAB360

## Documentación

Cada documento técnico describe un asunto concreto mediante un título H1 único y descriptivo, seguido de secciones de nivel H2/H3. Utilizar **Descripción**, **Arquitectura o implementación**, **Validación**, **Limitaciones** y **Documentación relacionada** cuando sean pertinentes. Los títulos, índices y textos visibles del producto identifican el asunto técnico sin sufijos de fase ni referencias al orden académico. Conservamos los identificadores funcionales, rutas, contratos y catálogos históricos; la planificación se registra en los espacios de gestión correspondientes. Los ADR conservan su identificador.

La documentación vigente describe el sistema y sus resultados. Las instrucciones de continuidad de conversaciones, estimaciones intermedias y bitácoras administrativas de desarrollo no pertenecen a ella. Los registros históricos útiles se identifican como tales y se conservan sin alterar los datos originales. Los catálogos gráficos contienen la lista de imágenes y su alcance.

### Alcance y voz editorial

Redactamos como equipo académico, en primera persona del plural para nuestras decisiones, implementaciones y resultados (por ejemplo, «implementamos», «comprobamos» y «observamos»). Utilizamos la voz técnica impersonal para describir contratos, condiciones, requisitos y procedimientos. Diferenciamos los resultados comprobados, las limitaciones y el trabajo previsto. No atribuimos pruebas ni capacidades que no hayamos validado.

Conservamos el nombre `README.md` en cada directorio que necesita una introducción propia. La ruta identifica su ámbito y el H1 identifica el componente. El README raíz presenta el proyecto; el de docs indexa la documentación; los de servicios, topologías, IaC y Ansible describen sus propios componentes; los de evidencias catalogan exclusivamente las imágenes de su ámbito. No copiamos descripciones ni resultados ajenos al directorio. Los catálogos utilizan Descripción, Capturas disponibles y Uso académico; los documentos técnicos utilizan las secciones pertinentes según su función, sin rellenar secciones vacías.

## Nomenclatura

| Tipo | Convención |
|---|---|
| Markdown técnico | minúsculas ASCII y palabras separadas por guiones; prefijo sNN cuando corresponde |
| Módulos Python | snake_case; identificador válido de Python; conservar `__init__.py` para inicializar paquetes |
| Pruebas Python | test_sNN_componente.py o test_transversal_componente.py para comprobaciones transversales |
| Ejecutables Bash | minúsculas ASCII separadas por guiones; prefijo de fase cuando corresponde |
| Configuración y datos | nombre descriptivo estable, según formato y consumidor |
| Evidencia PNG | SNN_FNN_Descripcion_Tecnica.png |
| Archivos institucionales | nombres reconocidos por GitHub y el ecosistema (README.md, LICENSE, CITATION.cff, SECURITY.md, etc.) |

Los archivos de herramientas con nombres convencionales, las rutas de systemd, las interfaces de importación, los recursos de runtime y las referencias fijadas a revisiones históricas requieren un análisis de compatibilidad antes de modificarse. Los identificadores históricos B1–B4, versiones de ensayos y nombres de registros originales se conservan cuando identifican procedimientos o procedencia experimental. Los archivos .yml y .yaml son válidos según su consumidor; las unidades .service, plantillas .j2, configuraciones .conf, main.tf y nombres reservados conservan su contrato. No renombrar indiscriminadamente por extensión. Las referencias a revisiones históricas permanecen vinculadas a la revisión original.

## Código y pruebas

Documentamos el propósito del archivo, los contratos de entrada/salida, las decisiones relevantes y los límites de seguridad. En Python preferimos docstrings de módulos, clases y funciones cuando aportan información; en Bash explicamos precondiciones, etapas y limpieza; en YAML, HCL, FRR, systemd, Jinja y HTML usamos comentarios compatibles con cada sintaxis. Explicamos bloques no triviales, casos límite y motivos, no cada instrucción evidente. Conservamos shebangs, directivas, delimitadores y los contratos del consumidor.

No añadimos comentarios a JSON, JSONL, PNG, registros originales, archivos de citación o licencia, estados generados ni formatos que no los admiten o cuya identidad debe preservarse. No alteramos corpus congelados, configuraciones históricas ni copias privilegiadas instaladas para aplicar cambios cosméticos. Los cambios de comentarios en código protegido requieren revisión y comprobación de la equivalencia funcional antes de desplegar otra versión.

La autoría académica corresponde al equipo. Centralizamos el aviso de derechos en [LICENSE](../LICENSE) y en el README raíz; los archivos originales de código pueden incluir `SPDX-License-Identifier: MIT` y el aviso de copyright con sintaxis válida. No repetimos la licencia en cada documento ni sustituimos avisos de terceros.

Al cambiar nombres o rutas, actualizar referencias Markdown, importaciones, rutas declarativas, scripts, workflows y pruebas dependientes en la misma integración. Verificar sintaxis, regresión, enlaces y ausencia de secretos. Las pruebas offline no sustituyen las comprobaciones de red activa.

## Gestión de cambios

Mantenemos ramas de trabajo acotadas, historial ordinario y commits descriptivos. Cada PR, abierto o cerrado, debe disponer de al menos una etiqueta temática y un responsable (assignee). Asignamos las etiquetas de fase que describen su alcance real; un PR de gestión general puede no tener fase. El milestone es condicional: lo asignamos únicamente cuando existe un hito de aceptación inequívoco, incluso si el cambio afecta varias fases. Si no existe tal hito, dejamos el campo vacío y conservamos la trazabilidad mediante etiquetas, descripción e issues relacionadas. Antes de fusionar verificamos estos criterios y la CI aplicable; no modificamos estados ni criterios históricos para completar metadatos. No incluir estados privados, credenciales, material ajeno ni copias temporales. Consultar [convenciones de GitHub](../docs/gestion/convenciones-issues-etiquetas.md) y [política de seguridad](../SECURITY.md).
