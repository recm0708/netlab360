# Índice y responsabilidades de la documentación

La documentación de NETLAB360 se organiza por **función**, no por número de mensajes ni por fecha de cada prueba. La redacción corresponde al equipo del proyecto y separa resultados probados, planes y referencias académicas.

| Ubicación | Propósito |
|---|---|
| `README.md` | Presentación del proyecto, arquitectura y enlaces principales |
| `docs/00-estado-y-continuidad.md` | Estado general verificado de las fases |
| `docs/REANUDAR-AQUI.md` | Próxima acción y precauciones vigentes |
| `docs/05-plan-operativo-y-pausas.md` | Conservación, suspensión y posterior reanudación de VMware |
| `docs/gestion/s05-tablero-vigente.md` | Resultados técnicos y criterios de aceptación S05 |
| `docs/arquitectura/`, `docs/diseno/`, `docs/decisiones/` | Topología, restricciones, componentes y decisiones |
| `docs/academico/`, `docs/entregables/` | Informe institucional, estructura, selección de figuras y entregables |
| `docs/evidencias/`, `evidencias/capturas/` | Catálogos, manifiestos, procedencia y selección |
| `docs/operacion/`, `docs/operaciones/` | Procedimientos técnicos ejecutables o de referencia |
| `docs/control/` | Criterios de aceptación y seguimiento de fases |
| `docs/sesiones/` | Bitácoras fechadas; histórico inmutable de la ejecución |
| `docs/gestion/CORTE-MAESTRO-*.md`, `docs/gestion/historico-issues/` | Cortes e issues archivados; nunca prevalecen sobre el tablero vigente |
| `ansible/`, `iac/`, `servicios/`, `topologias/` | README específicos de cada componente, sin cronologías duplicadas |

## Depuración

Los antiguos avisos «corte vigente» repetidos y contradictorios se eliminan de los puntos principales de entrada. Los documentos de sesiones, cortes, pruebas y decisiones históricas se conservan cuando tienen valor probatorio o referencias externas. **No eliminamos archivos solo por antigüedad** ni cambiamos contenido histórico que respalda hashes, capturas o issues.

Al cerrar una fase actualizamos el estado general, el tablero correspondiente, el catálogo de evidencia y el control académico; no añadimos copias completas de ese estado en cada README de componente. Los documentos que describen trabajo pendiente nunca lo presentan como ejecutado.

## Criterios de conservación

No incorporar credenciales, llaves privadas, cédulas de integrantes ni estados sensibles de infraestructura. Se preservan cifras, commits, manifestaciones SHA-256 y resultados originales. S01–S05 tienen evidencias técnicas; S06–S08 deberán avanzar únicamente contra sus respectivos criterios.

[Estado consolidado](../00-estado-y-continuidad.md) · [Convenciones](../convenciones/01-redaccion-y-nomenclatura.md).
