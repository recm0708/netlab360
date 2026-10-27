# NETLAB360 — Política editorial y entregables vigentes

**Revisión vigente: 27/10/2026, tras lectura del borrador 4.0 (94 páginas).** Este archivo recoge los criterios operativos del informe único y del paquete técnico. Sustituye las propuestas anteriores de dos informes y ZIP de anexos, conservadas en el historial Git.

## Informe académico único

NETLAB360 se documenta en **un solo Word/PDF institucional, de mínimo 40 páginas**, con portada, índice, introducción y los siguientes apartados: **1. Objetivos; 2. Planteamiento del problema; 3. Fundamento técnico; 4. Diseño de la solución; 5. Implementación; 6. Pruebas y validación; 7. Análisis de resultados; 8. Conclusiones y recomendaciones; Referencias**.

**No se incluye capítulo de anexos.** La modalidad de entrega aprobada para los archivos técnicos corresponde a un **TAR independiente** con scripts, YAML/JSON, HCL, inventarios, configuraciones propias, pruebas y evidencias pertinentes, además de instrucciones de ejecución, manifiesto SHA-256 y medidas de exclusión de secretos. Véase [criterios docentes](../academico/00-criterios-docentes-y-hitos.md), [plan TAR](../academico/03-anexos-y-demostracion.md) y [issue #45](https://github.com/recm0708/netlab360/issues/45).

El documento se desarrolla por **ocho fases técnicas** dentro de una única investigación. Las funciones de las fases 1 y 2 ya cuentan con pruebas reales, mientras que la fase 3 incorpora Ansible sobre FRRouting activo, OpenTofu **solo de metadatos** y GitOps. La fase S04 ya demostró colector 9110, Prometheus 9091, NOC multisede 9120, alerta WAN real, TSDB/SQLite persistentes, SLI 15m y 60m; **SLO 99 % candidato no ratificado**, sin Alertmanager ni mensajería externa. Su redacción se incorporará por chat a los capítulos 5–8 del Word maestro antes del cierre administrativo. S05–S08 siguen por desarrollar.

## Edición y sustentación de resultados

- Redacción natural y técnica, coherente con [convenciones Markdown](../convenciones/01-redaccion-y-nomenclatura.md), sin referencias a interlocutores que no formen parte del proyecto.
- Párrafos completos y cohesionados; no alargar deliberadamente expresiones que necesitan ser breves.
- Figuras y tablas con preámbulo, numeración consecutiva, título, nota apropiada y referencia cruzada.
- Citas en el cuerpo y referencias APA 7 consistentes; no agregar fuentes bibliográficas para justificar salidas originales de terminal.
- Mantener separados el diseño previsto, el resultado implementado y lo pendiente. No presentar `terraform_data` como aprovisionamiento de routers ni las reglas deterministas como un modelo ML entrenado.
- No atribuir disponibilidad continua, recuperación sin pérdidas ni redundancia física a ensayos que solo demuestran conectividad o conmutación lógica.
- Las capturas son **originales y verificables**, con comandos/resultados visibles y nombres `S01_...`, `S02_...`, etc. Para los archivos nuevos conservar el hash SHA-256 y la correspondencia con el nombre inicial.
- No duplicar en Word los scripts extensos, registros completos o el contenido del TAR técnico.
- La Figura 1 de topología HQ/S1/S2 y las Figuras 2–15 están presentes en el borrador 4.0; verificar legibilidad y notas. **No** declarar incorporadas las figuras S04 ni los apartados 5.6/6.9/7.10 hasta que el usuario los copie al Word y reexporte PDF. La Tabla 5 y la Tabla 12 aún reflejan estados antiguos.

## Fechas académicas y presentación

- **30/10/2026:** revisión por Teams de introducción, objetivos y planteamiento.
- **13/11/2026:** revisión de fundamento y diseño.
- **Demostración final en vivo** con PowerPoint derivado del informe y operaciones normal/falla/recuperación. Fecha y aceptación final, por confirmar.

No se exige un manual técnico independiente para el corte actual. La exportación OVA/OVF tampoco se declara requisito docente hasta contar con confirmación.

## Integridad y control

- Todos los cambios operativos se gestionan en GitHub mediante issues, commits, PR y CI, con pruebas satisfactorias antes de fusionar.
- La administración remota de GitHub se gestiona de forma centralizada; las operaciones locales y la obtención de fotografías se limitan al equipo de laboratorio.
- No versionar llaves privadas, tokens, contraseñas, `terraform.tfstate`, planes guardados, archivos docentes externos ni datos personales.
- Los controles de cierre se basan en la evidencia real de cada fase, sin exigir que una fase inicial complete las funcionalidades de otras fases.

[Punto de reanudación](../REANUDAR-AQUI.md) · [Tablero de fases](../control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [Auditoría de capturas](../evidencias/09-auditoria-zip-fases1-2-3-2026-10-25.md).
