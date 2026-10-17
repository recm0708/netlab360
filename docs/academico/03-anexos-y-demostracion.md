# NETLAB360 — Paquete de anexos y demostración académica

**Estado 16/10/2026:** planificado; **NO se ha generado ZIP**, el formato ZIP como adjunto separado confirmado por la profesora. El entregable escrito principal debe ser autocontenido para comprender arquitectura, implementación, pruebas y resultados. No sustituirlo por código suelto.

## Política para anexos de código completo

**Propuesta de un archivo único** `NETLAB360_Anexos_Tecnicos_Final.zip` con:
- `00_LEEME.txt`: versión/tag/commit, requisitos y correspondencia con las secciones 7–9 del informe.
- `01_inventario/`: YAML de sedes, IPAM, VLAN, políticas; datos no secretos.
- `02_topologias/`: archivos y diagramas de escenario, con distinción desplegado/draft.
- `03_iac/`: `.tf`, `.tfvars.example` despersonalizado, HCL/OpenTofu, Ansible/roles/playbooks, **no** `terraform.tfstate`, ficheros lock de estado, passwords ni `.tfvars` con credenciales.
- `04_scripts/`: Bash/Python, validadores, simulaciones seguras y utilidades de rollback.
- `05_servicios/`: FRR, exporter, Prometheus, config NOC sin credenciales.
- `06_tests/`: pruebas unitarias y de integración sin datos sensibles.
- `07_evidencias_seleccionadas/`: logs, outputs y capturas pertinentes, no duplicar por defecto las 86 PNG.
- `08_documentacion/`: matriz de pruebas: ID, etapa, condición inicial, estímulo, resultado esperado/observado, artefacto, commit y estado.
- `MANIFIESTO_SHA256.csv`: hash relativo y tamaño de cada archivo; fecha de empaquetado y script/orden para verificar integridad.

**Exclusiones obligatorias:** tokens GitHub, claves privadas SSH, passwords, `.env` secretos, bases de datos reales con datos privados, caches, `.git/`, estados sensibles de OpenTofu, `__pycache__`, datos de usuario y valores personales ocultos en salidas/logs. Sanitizar **copias de distribución**, no borrar sin respaldo la VM original.

**Verificación previa a la entrega:** ZIP abre sin errores, archivos listados existen, manifiesto SHA256 coincide, README/requisitos completos, referencias cruzadas desde el informe; reproducción inicial con una VM limpia en copia si procede. Nunca llamar «anexos entregados» antes de que se genere, revise y acepte.

## Presentación oficial: desarrollar DESPUÉS del informe

PowerPoint obligatorio: portada/título; introducción; objetivos; planteamiento del problema; diseño; demostración; conclusión y referencias. No existe un número fijo de diapositivas comunicado; el PowerPoint será una síntesis del mismo informe. Para referencias se pueden escoger unas cinco a diez representativas, sin obligación de cantidad exacta. Cantidad y tiempo real aún no confirmados.

**La demostración final debe ser EN VIVO, directamente en el entorno desarrollado.** No basta reproducir imágenes ni videos sin ejecución interactiva. La demostración debe explicar **por qué funcionan** los escenarios y contrastar la respuesta esperada con la real. Diseñar un recorrido técnico con fallos seguros:
1. Mostrar arquitectura y baseline: sedes, VLAN, dos WAN, NOC.
2. Generar tráfico cliente VLAN HQ→servicio S1/S2 con pruebas positivas y negativas de ACL.
3. Interrumpir WAN-P, observar OSPF ruta respaldo, verificar tráfico y NOC/alerta; restaurar y verificar retorno a estado normal.
4. Si se integra y prueba: miembro LACP DOWN y recuperación / redundancia de equipo sin tocar red de administración.
5. Mostrar IaC SoT→Ansible FRR y compliance/drift; diagnóstico basado en datos y límites.
6. Cerrar con postcheck limpio y evidencias con versión/fecha.
**Cada paso se presentará solo si previamente está probado**; nada de demo basada en capturas falsas o funciones simuladas que se etiqueten como reales.

## Estado de otras entregas

- OVA: no hay obligación explícita en estos criterios docentes. Su necesidad/fecha quedan por confirmar en transcripción; si la profesora no la exige, la OVA puede ser complemento recomendable, no requisito asumido.
- Manual técnico 02: **no se entrega ahora**; redacción posentrega/futura conservada en issue #28.
- El ejemplo del parcial aún no ha sido adjuntado en esta revisión; no usarlo como norma oficial ni afirmar que fue auditado.
