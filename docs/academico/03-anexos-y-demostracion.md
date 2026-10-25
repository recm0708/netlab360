# NETLAB360 — Archivo técnico TAR independiente y demostración académica

**Decisión operativa vigente, precisada por el estudiante el 25/10/2026:** la profesora autorizó entregar por separado los archivos técnicos del proyecto. El formato definitivo indicado ahora es **un único archivo `.tar`**, no ZIP, y **no se insertará un apartado de anexos en el informe escrito**, que termina en Referencias. La aprobación previa de archivos externos registrada el 16/10 se conserva como antecedente; el cambio de ZIP a TAR responde a la confirmación reciente del estudiante. **El TAR aún no se ha generado, examinado ni entregado.**

## Propuesta de estructura del TAR final

Nombre provisional: `NETLAB360_Entrega_Tecnica.tar`.

- `00_LEEME.md`: propósito, alcance por fases, versión/tag/commit, compatibilidad, dependencias y orden de ejecución, así como correspondencia con el texto del informe.
- `inventario/`: YAML, IPAM, VLAN y políticas declarativas propias de NETLAB360.
- `topologias/`: definiciones Docker/FRR y materiales de topología necesarios para los escenarios reproducibles.
- `iac/`: HCL y código OpenTofu; incluir **solo configuraciones y ejemplos sanitizados**, sin estados, planes guardados ni secretos.
- `ansible/`: inventarios, roles y playbooks sin credenciales.
- `scripts/`: Bash/Python, validadores, controles preventivos y procedimientos de reversión.
- `servicios/`: configuraciones FRR/exportador/Prometheus y paneles propios, si están validados y son distribuibles.
- `tests/`: pruebas reproducibles y fixtures sin datos sensibles.
- `evidencias/`: registros, mediciones y capturas **seleccionadas**, solamente cuando sean necesarios y estén autorizados; evitar duplicar todo el histórico.
- `MANIFIESTO_SHA256.txt`: huellas verificables de los archivos incluidos, excluyendo el propio manifiesto para evitar autorreferencia.

La estructura final podrá adaptarse a las rutas reales del repositorio y al alcance aprobado hasta la fase final. **No copiar ciegamente todo el clon.**

### Exclusiones de seguridad

No incluir `.git/`, `.env` con secretos, llaves SSH privadas, contraseñas, tokens de GitHub, `terraform.tfstate*`, planes `*.tfplan`, `.terraform/`, caches, archivos personales ni guías/archivos recibidos de la profesora. Sanitizar **copias de distribución**; no borrar datos del entorno original sin respaldo. Los registros técnicos y datos de prueba deben revisarse para evitar direcciones/credenciales personales ajenas al escenario.

### Comprobaciones obligatorias antes de entregar

1. Congelar versión de código y correspondencia con el informe, sin simular funciones no implementadas.
2. Preparar directorio de staging externo a `~/proyectos/netlab360`, con permisos privados; revisar archivo por archivo.
3. Generar `MANIFIESTO_SHA256.txt` y obtener listado de contenidos.
4. Crear TAR con `tar -cf`, verificar con `tar -tf` y extraer en directorio de prueba distinto.
5. Verificar SHA-256 de los archivos extraídos, búsqueda de secretos y pruebas de reproducción que correspondan.
6. Registrar hash SHA-256 del propio TAR y conservar ruta/version/tag/fecha de la entrega; **no marcar entregado hasta constar su recepción**.

## Presentación y demostración final

PowerPoint derivado del informe: título, problema, objetivos, diseño y arquitectura, demostración, conclusiones y referencias. La demostración técnica debe hacerse **en vivo**: estado inicial → modificación controlada → resultado medido → recuperación. Solo se muestran capacidades comprobadas y con procedimientos reversibles. No usar capturas para sustituir una función que se presenta como operativa.

## Otros entregables

- **Informe:** único Word/PDF académico, mínimo 40 páginas, con citas y referencias APA 7; **sin apartado de anexos**. El archivo TAR es entrega separada.
- **OVA/OVF:** no consta exigencia expresa de la profesora; no darlo por obligatorio ni generarlo sin un plan de exportación seguro.
- **Manual independiente:** pospuesto, no parte de la entrega actual.
