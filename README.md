# NETLAB360

**Proyecto:** diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico inteligente de redes empresariales multisede.

**Estado vigente de planificación:** 14/10/2026. **Fase interna S01 ABIERTA**, 72/100 técnico estimado según matriz interna, no calificación docente. El usuario ordenó no iniciar S02 hasta organizar/terminar los tres documentos maestros y resolver el cierre de S01. La agenda académica/rúbrica definitiva está pendiente de cotejar.

## Puntos de acceso vigentes

- [Checkpoint de continuidad](docs/REANUDAR-AQUI.md): estado más reciente y siguiente actividad segura.
- [Ponderación S01](docs/control/01-avance-s01.md) y [aceptación criterio por criterio](docs/control/03-matriz-aceptacion-y-decisions-s01.md).
- [Política editorial acumulativa](docs/entregables/00-politica-editorial-y-entrega-acumulativa.md).
- [01 — Investigación del proyecto](docs/entregables/01-proyecto-investigacion-maestro.md).
- [02 — Informe técnico/laboratorios](docs/entregables/02-informe-tecnico-maestro.md).
- [03 — Manual de usuario](docs/entregables/03-manual-usuario-maestro.md).
- [GitHub Issues S01](https://github.com/recm0708/netlab360/issues/1); [guía/rúbrica #36](https://github.com/recm0708/netlab360/issues/36); [documentos #35](https://github.com/recm0708/netlab360/issues/35); [evidencias #43](https://github.com/recm0708/netlab360/issues/43).

## Hechos validados a 13/10/2026 23:35 Panamá

1. VM Ubuntu Desktop en VMware con red de gestión aislada VMnet8, ens33 `192.168.47.40/24` y gateway `192.168.47.2`, servicios operativos.
2. IPAM YAML, segmentación VLAN/trunks/ACL y HTTP local; OSPF dual-WAN HQ–S1 con HTTP por WAN-P/B/P; LACP/active-backup de interfaces virtuales.
3. SoT→OpenTofu→Ansible→archivos FRR aplicados al laboratorio. Drift y reconciliación probados en **archivos candidatos**, no FRR vivo.
4. Exporter live, API/NOC inicial y Prometheus con alertas WAN firing y resueltas. Analítica de 76 ICMP históricos y 12 eventos de otras sesiones con reglas deterministas: **NO IA/ML entrenada/evaluada**.
5. **86 PNG planos y 7 CSV** en evidencias, SHA-256 auditados, publicación verificada commit `b410548` y Git local/remoto coincidentes.
6. **24/24 pruebas unitarias locales** y GitHub Actions [run 38511477595](https://github.com/recm0708/netlab360/actions/runs/38511477595) exitosa. Último postcheck: Docker/netns vacíos, gestión y Git intactos.

## Estructura del repositorio

- `inventario/`, `topologias/`: IPAM y topologías.
- `iac/`, `ansible/`: configuración declarativa y automatización.
- `scripts/`, `servicios/`, `tests/`: laboratorios, telemetría y validadores.
- `evidencias/capturas/`: imágenes originales **en una sola carpeta**; `evidencias/manifiestos/`: manifiestos SHA-256.
- `docs/sesiones/`, `docs/evidencias/`, `docs/decisiones/`: bitácoras históricas y trazabilidad. No confundir con estado actual.
- `docs/entregables/`: política editorial y **tres únicos documentos maestros**, ampliados por fases S01–S08.

**Política de continuidad:** las versiones anteriores del README y del control permanecen recuperables mediante historial Git; este archivo evita apilar checkpoints contradictorios. No ejecutar un nuevo laboratorio sin precheck y sin necesidad de aceptación demostrada.
