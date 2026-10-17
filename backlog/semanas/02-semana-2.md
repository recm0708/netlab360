# S02 — Multisede funcional

**REVISIÓN 16/10/2026.** Fase/hito de gestión **INTERNO**, no fecha docente firme. Prioridades sujetas a transcripción y ejemplo de parcial. [Plan oficial de recuperación](../../docs/academico/02-plan-operativo-s02-s08-repriorizado.md).

## Objetivo técnico
Integrar HQ/S1/S2, VLAN por sede, dos WAN y servicio extremo a extremo; comparar ACL permitida/denegada y failover OSPF.

## Prueba concluyente y criterios de cierre
Baseline de cliente→servicio, caída WAN-P, ruta WAN-B, restauración, prueba HTTP/ICMP y postcheck.

## Issues relacionadas
#13 #14 #30 #31

## Acompañamiento académico
- Actualizar **UN informe** 12 apartados, fundamentalmente 7 Implementación, 8 Pruebas, 9 Análisis, con configuración principal, baseline, esperado vs real, mitigación de incidentes auténticos y figuras legibles.
- Fuente completa y salidas extensas van al paquete de anexos **si se acepta ZIP**, con README, sanitización y hash SHA256. No incluir credenciales privadas.
- **Presentación al finalizar informe**, nunca exigir un segundo manual como bloqueo. Manual #28 pospuesto.
- Demostrar solo capacidades efectivamente probadas. No alterar VMnet8/ens33 de gestión ni eliminar recursos de laboratorios ajenos.

**Estado inicial de esta fase: PENDIENTE DE VALIDACIÓN ESPECÍFICA; no equiparar prototipos parciales S01 con implementación integral.**
