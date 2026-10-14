# NETLAB360

**Proyecto:** diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico inteligente de redes empresariales multisede.

**Política editorial vigente (14/10/2026): exactamente DOS documentos finales únicos**: (01) investigación, diseño, resultados e incidentes técnicos reales mitigados; (02) manual técnico integral para reproducir desde cero, implementar, verificar, operar y solucionar posibles problemas. Las portadas institucionales las crea el usuario; el asistente entrega contenido sección por sección. **No hay un tercer manual independiente**. La edición final se ajustará a las fases realmente implementadas, conservando el roadmap interno S01–S08 como historial verificable.

**S01:** ABIERTA, **72/100 técnico estimado internamente**; guía docente pendiente para determinar qué criterios se exigen ahora. No iniciar S02 hasta concluir documentos S01 y brechas técnicas rubricadas.

## Enlaces de trabajo vigentes

- [Checkpoint](docs/REANUDAR-AQUI.md).
- [Política de dos documentos APA7](docs/entregables/00-politica-editorial-y-entrega-acumulativa.md).
- [01 — Diseño, desarrollo y evaluación](docs/entregables/01-proyecto-investigacion-maestro.md).
- [02 — Manual técnico integral de implementación, administración y uso](docs/entregables/02-informe-tecnico-maestro.md).
- [Figuras y tablas S01](docs/entregables/04-seleccion-figuras-y-tablas-s01.md).
- [Checklist S01](docs/entregables/s01/00-checklist-cierre-y-entrega.md).
- [Matriz ponderada](docs/control/01-avance-s01.md) · [Once criterios](docs/control/03-matriz-aceptacion-y-decisions-s01.md).
- [Issues #1 S01](https://github.com/recm0708/netlab360/issues/1), [#35 documentación](https://github.com/recm0708/netlab360/issues/35), [#36 rúbrica](https://github.com/recm0708/netlab360/issues/36) y [#43 evidencias](https://github.com/recm0708/netlab360/issues/43).

## Resultados demostrados (corte técnico 13/10/2026)

1. VM Ubuntu Desktop VMware/VMnet8; gestión ens33 192.168.47.40/24, gateway 192.168.47.2, SSH y servicios operativos.
2. IPAM YAML, VLAN/trunks/ACL y HTTP, OSPF dual WAN HQ–S1/HTTP en tres estados, LACP 2→1→2 y bonding active-backup **de enlaces virtuales**.
3. SoT→OpenTofu metadata→Ansible candidatos FRR aplicados al entorno B2; drift/reconciliación probado **en archivos candidatos**, no FRR vivo.
4. Exporter/NOC inicial y Prometheus con alertas WAN firing/resueltas; B4 analizó 76 ICMP y 12 eventos de otras sesiones, diagnóstico por reglas **sin ML entrenado/evaluado**.
5. **86 PNG** planos y **7 CSV** SHA-256 en GitHub, commit de lote06 b410548; **24/24** pruebas unitarias y GitHub Actions run 38511477595 exitosa; postcheck Docker/netns vacíos y gestión intacta.

## Organización

Los recursos técnicos residen en inventario/, topologias/, iac/, ansible/, scripts/, servicios/ y tests/. Las capturas originales están en evidencias/capturas/ sin subcarpetas y hashes en evidencias/manifiestos/. Las bitácoras permanecen en docs/sesiones/, docs/evidencias/ y el historial Git. **docs/entregables/ mantiene dos índices maestros activos.**

**Índices 01 y 02 aprobados por el usuario el 14/10/2026**, sujetos a cualquier cambio docente. Próximo: comenzar Documento 01 por la Introducción cuando el usuario confirme «comencemos».
