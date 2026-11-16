# NETLAB360 — Registro oficial de integridad de evidencias de las fases 1–3

**Corte documental vigente:** 27 de octubre de 2026. Este registro identifica el conjunto de imágenes que sustenta técnicamente los resultados de cada fase.

| Fase | PNG oficiales | Contenido técnico comprobado |
|---|---:|---|
| S01 | **83** | Inventario IPAM, segmentación, FRR/OSPF y conmutación, LACP/active-backup, control HTTP, observabilidad, OpenTofu/Ansible y diagnóstico |
| S02 | **9** | Tres sedes HQ/S1/S2, cuatro WAN, nueve VLAN, failover y restauración, HTTP/ACL |
| S03 | **8** | SoT multisede, Ansible FRR y reconciliación, OpenTofu 17 metadatos y estado idempotente |
| **Total S01–S03** | **100** | Imágenes de resultados verificados |

Los originales están versionados en `evidencias/capturas/fase1/`, `fase2/` y `fase3/`. Las rutas y huellas se verifican mediante `MAPA_RENOMBRADO_FASE1_2026-10-25.csv`, `MANIFIESTO_SHA256_CAPTURAS_2026-10-25.csv` y `scripts/validacion/validar-capturas-unificadas.py`.

Los PNG no se regeneran ni modifican; la auditoría confronta sus bytes y tamaños con los manifiestos. Los límites metodológicos de las pruebas se desarrollan en el informe académico único. Las capturas complementan resultados técnicos reales y no sustituyen logs, pruebas de servicios, revisiones de rutas ni validaciones de automatización.

La evidencia GitOps S03 se conserva en [S03_09: ciclo PR/CI](S03_09_GitOps_CI_Regresion_PullRequest.md).
