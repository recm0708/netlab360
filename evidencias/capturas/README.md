# NETLAB360 — Capturas oficiales organizadas por fase

Evidencias originales obtenidas de la ejecución de los laboratorios. Cada archivo conserva sus bytes y su relación con un manifiesto de integridad SHA-256.

| Fase | PNG versionadas | Resultado principal |
|---|---:|---|
| [S01](fase1/README.md) | 83 | Laboratorios iniciales de redes, redundancia, automatización, observabilidad y análisis |
| [S02](fase2/README.md) | 9 | Integración funcional HQ/S1/S2, WAN/OSPF, VLAN, HTTP/ACL |
| [S03](fase3/README.md) | 8 | Inventario/SoT, cumplimiento y reconciliación Ansible, metadatos OpenTofu |
| [S04](fase4/README.md) | 22 | Colector y NOC multisede, alertas, recuperación, TSDB/SQLite y SLI |
| S05–S08 | 0 | Etapas planificadas |
| **Total** | **122** | Evidencias de las cuatro fases desarrolladas |

La auditoría automatizada `scripts/validacion/validar-capturas-unificadas.py` comprueba rutas, tamaños, SHA-256 y, para los lotes S04, dimensiones PNG. El inventario de S01 utiliza `evidencias/manifiestos/MAPA_RENOMBRADO_FASE1_2026-10-25.csv`, complementado por el manifiesto del lote intersedes; S02–S04 disponen de manifiestos por lote.

GitOps S03 cuenta con un [registro técnico verificable de PR y CI](../../docs/evidencias/S03_09_GitOps_CI_Regresion_PullRequest.md). La evidencia del informe se selecciona por su relevancia y legibilidad; el paquete TAR es independiente y se prepara en S08.
