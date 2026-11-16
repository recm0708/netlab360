# NETLAB360 — Auditoría de evidencias oficiales IaC y diagnóstico S01

**Validación técnica:** 13 de octubre de 2026; catálogo oficial revisado al 27 de octubre de 2026.

## Pruebas representadas

La fase 1 contiene pruebas comprobadas de OpenTofu y Ansible sobre configuraciones candidatas, utilización de configuraciones generadas sobre FRRouting para comprobar OSPF, y diagnóstico estadístico basado en 76 sondeos auténticos.

| Grupo | Resultados verificados |
|---|---|
| B4, diagnóstico por reglas | 76/76 sondeos ICMP con respuesta; percentiles y umbrales descriptivos; evaluación sin modelo ML entrenado |
| IaC inicial con OpenTofu | Plan y manifiesto declarativo de cinco recursos de metadatos, con alcance limitado |
| Ansible FRR | Generación de candidatos y comprobaciones de consistencia, idempotencia y reconciliación sobre archivos |
| Integración IaC/FRRouting | Arranque con configuraciones generadas y selección OSPF en el escenario HQ/S1 |

Los resultados técnicos de B4 no constituyen mediciones de IA supervisada ni garantizan continuidad sin pérdidas fuera de los instantes de sondeo. La administración real de configuraciones FRRouting se amplió en S03; el NOC centralizado multisede se validó en S04.

## Integridad y consulta

Los archivos pertenecen al catálogo oficial en [S01](../../evidencias/capturas/fase1/README.md), con ruta y huella de integridad trazables a los [manifiestos del proyecto](../../evidencias/manifiestos/). La revisión automatizada se realiza mediante `scripts/validacion/validar-capturas-unificadas.py`.

El informe académico único contiene los resultados relevantes. Las operaciones y pruebas reproducibles se incluirán en el TAR técnico de la entrega final bajo controles de integridad y privacidad.
