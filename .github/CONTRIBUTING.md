# Convenciones de contribución de NETLAB360

## Documentación

Cada documento técnico describe un asunto concreto mediante un título H1 único y descriptivo, seguido de secciones de nivel H2/H3. Utilizar **Descripción**, **Arquitectura o implementación**, **Validación**, **Limitaciones** y **Documentación relacionada** cuando sean pertinentes. Los títulos técnicos de fase siguen la forma «Tema — Fase NN»; los documentos transversales identifican su asunto sin añadir una fase ficticia. Los ADR conservan su identificador.

La documentación vigente describe el sistema y sus resultados. Las instrucciones de continuidad de conversaciones, estimaciones intermedias y bitácoras administrativas de desarrollo no pertenecen a ella. Los registros históricos útiles se identifican como tales y se conservan sin alterar los datos originales. Los catálogos gráficos contienen la lista de imágenes y su alcance.

## Nomenclatura

| Tipo | Convención |
|---|---|
| Markdown técnico | minúsculas ASCII y palabras separadas por guiones; prefijo sNN cuando corresponde |
| Módulos Python | snake_case; identificador válido de Python |
| Pruebas Python | test_sNN_componente.py o test_transversal_componente.py para comprobaciones transversales |
| Ejecutables Bash | minúsculas ASCII separadas por guiones; prefijo de fase cuando corresponde |
| Configuración y datos | nombre descriptivo estable, según formato y consumidor |
| Evidencia PNG | SNN_FNN_Descripcion_Tecnica.png |
| Archivos institucionales | nombres reconocidos por GitHub y el ecosistema (README.md, LICENSE, CITATION.cff, SECURITY.md, etc.) |

Los archivos de herramientas con nombres convencionales, las rutas de systemd, las interfaces de importación, los recursos de runtime y las referencias fijadas a revisiones históricas requieren un análisis de compatibilidad antes de modificarse. Los identificadores históricos B1–B4, versiones de ensayos y nombres de registros originales se conservan cuando identifican procedimientos o procedencia experimental. Los archivos .yml y .yaml son válidos según su consumidor; las unidades .service, plantillas .j2, configuraciones .conf, main.tf y nombres reservados conservan su contrato. No renombrar indiscriminadamente por extensión. Las referencias a revisiones históricas permanecen vinculadas a la revisión original.

## Código y pruebas

Los módulos describen su responsabilidad, entradas y efectos. Los scripts explican alcance y precondiciones, especialmente antes de mutaciones. Los comentarios aportan contexto técnico, no reiteran comandos.

Al cambiar nombres o rutas, actualizar referencias Markdown, importaciones, rutas declarativas, scripts, workflows y pruebas dependientes en la misma integración. Verificar sintaxis, regresión, enlaces y ausencia de secretos. Las pruebas offline no sustituyen las comprobaciones de red activa.

## Gestión de cambios

Mantener ramas de trabajo acotadas, historial ordinario y commits descriptivos. No incluir estados privados, credenciales, material ajeno ni copias temporales. Consultar [convenciones de GitHub](../docs/gestion/convenciones-issues-etiquetas.md) y [política de seguridad](../SECURITY.md).
