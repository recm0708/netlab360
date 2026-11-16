# S03 — Network as Code y cumplimiento

**REVISIÓN 16/10/2026.** Fase/hito de gestión **INTERNO**, no fecha docente firme. Prioridades sujetas a transcripción y ejemplo de parcial. [Plan oficial de recuperación](../../docs/academico/02-plan-operativo-s02-s08-repriorizado.md).

## Objetivo técnico
Usar SoT inventario en topología integrada, Ansible/OpenTofu con ownership explícito, config FRR live e idempotencia.

## Prueba concluyente y criterios de cierre
Drift controlado en router activo, detección, reconciliación, retorno al estado esperado; CI/PR sin falsificar privilegios.

## Issues relacionadas
#16 #17 #18 #19

## Acompañamiento académico
- Actualizar **UN informe** 12 apartados, fundamentalmente 7 Implementación, 8 Pruebas, 9 Análisis, con configuración principal, baseline, esperado vs real, mitigación de incidentes auténticos y figuras legibles.
- Fuente completa y salidas extensas van al paquete de anexos **si se acepta ZIP**, con README, sanitización y hash SHA256. No incluir credenciales privadas.
- **Presentación al finalizar informe**, nunca exigir un segundo manual como bloqueo. Manual #28 pospuesto.
- Demostrar solo capacidades efectivamente probadas. No alterar VMnet8/ens33 de gestión ni eliminar recursos de laboratorios ajenos.

**Estado inicial de esta fase: PENDIENTE DE VALIDACIÓN ESPECÍFICA; no equiparar prototipos parciales S01 con implementación integral.**


**Corte académico obligatorio durante el proyecto:** título al chat Teams, primera revisión **30/10/2026** (Introducción, Objetivos, Planteamiento), segunda revisión **13/11/2026** (Fundamento técnico y Diseño). Ambas muestran el **mismo borrador en Teams**, representante designado; no requieren diapositivas. ZIP de anexos externos autorizado con el informe, demo final EN VIVO. [Criterios aplicables](../../docs/academico/00-criterios-docentes-y-hitos.md).
