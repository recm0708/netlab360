# NETLAB360 — Capturas organizadas por fase

Esta carpeta contiene únicamente **capturas auténticas** de NETLAB360. El nombre de archivo comienza por el código técnico `S01` a `S08`, mientras que cada directorio se identifica como `fase1` … `fase8`.

- **fase1:** 86 PNG históricos ya existentes en GitHub, renombrados solo mediante referencias al **mismo blob Git**, sin modificar bytes. Los nombres originales `B1_`, `B2_`, `B3_`, `B4_`, `IAC_` se conservan después del prefijo S01 para rastrear el laboratorio de origen. [Mapa nombre anterior ↔ nuevo](../manifiestos/MAPA_RENOMBRADO_FASE1_2026-10-25.csv).
- **fase2:** preparada para incorporar capturas locales reales de la integración HQ–S1–S2; no afirmar ninguna PNG versionada hasta su auditoría y subida.
- **fase3:** preparada para capturas de automatización/Ansible/OpenTofu; los resultados GitHub Actions del PR #49 están documentados en `docs/evidencias/S03_09_GitOps_CI_Regresion_PullRequest.md`, que **NO** es captura PNG.
- **fase4–fase8:** directorios reservados para evidencias que se obtengan al ejecutar cada fase.

**Integridad:** los manifiestos históricos en `evidencias/manifiestos/` son inmutables y reflejan los nombres anteriores. El mapa adicional proporciona rutas vigentes y SHA-256 originales. El validador `scripts/validacion/validar-capturas-unificadas.py` comprueba los 86 hashes en la estructura nueva. No cambiar nombres de archivos ya citados sin actualizar el mapa.

**Conteos distintos:** el inventario local contiene **93 capturas de fase 1** en su inventario local (no verificadas aquí), mientras GitHub conserva 86; faltan comparar **7 potenciales capturas** antes de declarar completo el lote de fase 1.

**Entrega:** la profesora autorizó los artefactos técnicos en un `.tar` externo al informe; no hay capítulo de anexos en Word/PDF. No añadir capturas innecesarias, credenciales, material de clase ni estados OpenTofu.
