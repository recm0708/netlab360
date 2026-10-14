# NETLAB360 — Auditoría visual y paquete lote 06 (IaC y B4)

**Fecha de auditoría:** 13/10/2026 23:24 Panamá. **Evidencias suministradas por el usuario:** 19 imágenes nuevas recibidas juntas (13 B4 y seis IaC) y cinco imágenes válidas del envío IaC previo conservadas para completar un único lote. **24 PNG seleccionados sin modificación de bytes**, nombres únicos, SHA256 distintos; una observación menor de encuadre.

## Lotes de evidencia seleccionados

| Bloque | Cantidad | Archivos |
|---|---:|---|
| B4 auditoría y análisis | 13 | `B4_00_Regresion_Unitarias.png`, `B4_01_Auditoria_Datos_Reales.png`, `B4_02_Distribucion_Eventos_Reales.png`, `B4_03_Postcheck_Datos_Reales.png`, `B4_04_Tests_Perfil_Estadistico.png`, `B4_05_Perfil_Estadistico_Real.png`, `B4_06_Resumen_Estadistico_Por_Fase.png`, `B4_07_Postcheck_Perfil_Estadistico.png`, `B4_07_Tests_Diagnostico_Reglas.png`, `B4_08_Diagnostico_Reglas_Reales.png`, `B4_09_Integridad_Diagnostico.png`, `B4_10_Sensibilidad_Umbral_RTT.png`, `B4_11_Postcheck_Diagnostico.png` |
| IaC integración B2 | 4 | `IAC_B2_01_Precheck_Origen.png`, `IAC_B2_02_FRR_Configurado_Desde_Ansible.png`, `IAC_B2_03_OSPF_y_Rutas_IAC.png`, `IAC_B2_04_Postcheck_Final.png` |
| IaC drift/reconciliación | 2 | `IAC_S01_08_Drift_Detectado.png`, `IAC_S01_09_Reconciliacion.png` |
| IaC histórico aceptado de lote previo | 5 | `IAC_S01_02_Tofu_Plan-1.png`, `IAC_S01_02_Tofu_Plan-2.png`, `IAC_S01_02_Tofu_Plan-3.png`, `IAC_S01_05_Compliance_FRR.png`, `IAC_S01_07_Postcheck_Final.png` |

**Dictamen:** 23 válidas sin observación sustantiva, 1 válida con observación menor (`IAC_S01_05_Compliance_FRR.png`: solo texto de resultado COMPLIANT, sin comando; la ejecución está acreditada por log y prueba subsiguiente). `IAC_B2_03_OSPF_y_Rutas_IAC.png` contiene salida larga pero legible de ambos routers y sus rutas; `B4_07_Tests_Diagnostico_Reglas.png` y otras capturas de pruebas se aceptan como evidencia cronológica diferente, no duplicados de ejecución.

**FALTAN REEMPLAZOS, NO PUBLICAR COMO COMPLETAS**: `IAC_S01_01_Precheck_IPAM_Herramientas_Final.png`, `IAC_S01_03_Tofu_Apply_Manifest_Final.png`, `IAC_S01_04_Ansible_Render_Candidato_FRR_Final.png`, `IAC_S01_06_Idempotencia_Final.png`. Las fotografías anteriores de esos cuatro bloques eran incompletas/de menor claridad y fueron EXCLUIDAS del lote 06. Recuperar capturas del script ya disponible `scripts/evidencias/resumir-iac-s01.py` (solo logs originales), **NO repetir `tofu apply`** ni reabrir redes solo por fotos. Estas cuatro serán un lote posterior, con nombres explícitos y hashes.

## Integridad del paquete de transferencia

- `NETLAB360_LOTE06_IAC_B4_24PNG_AUDITADOS_2026-10-13.zip`, tamaño **1,293,367 bytes**; SHA256 `803ee03050a2261e938c56ed1c266097639c357f3fc77882a8a18eb5330bc781`.
- Manifiesto dentro del ZIP: `MANIFIESTO_SHA256_NETLAB360_LOTE06_IAC_B4_24PNG.csv`; SHA256 `fbf6b9567ad6249a071ab9b53ba89368d0c0ab275b84b5a00d82eb4e85718c7f`, tamaño 2,799 bytes. Columnas: `archivo,sha256,bytes,grupo,dictamen`, 24 filas.
- Prueba de integridad ZIP: **OK**, comprobación byte a byte de los 24 PNG contra originales recibidos, sin colisiones de hash entre los 24.
- 24 PNG se instalarán directamente en `evidencias/capturas/`; CSV en `evidencias/manifiestos/`. **No crear subcarpetas lote06 ni copiar el ZIP dentro de GitHub.**
- Importador versionado `scripts/mantenimiento/importar-lote06-iac-b4.py`, modos `--verificar` y `--importar`, incluye hash de paquete/manifiesto, 62 PNG y 6 CSV previos, comprobación de colisiones, PNG signature, hashes por archivo y operación exclusiva.
- Auditor `scripts/validacion/validar-capturas-unificadas.py` actualizado para validar lotes 01–06. **Expected AFTER commit/push: 86 PNG planos + 7 CSV**, sin modificar los 62 anteriores. **Antes de recibir el push NO afirmar publicación binaria de lote06.**

## Ensayos técnicos B4 cotejados contra salida de Ubuntu pasos 202–212

- `git pull --ff-only` a `12a9d2f`, sintaxis Python0 y **24 unit tests OK**.
- CSV 76 ICMP históricos con `P95_NORMAL=0.049 ms`, SHA256 contra perfil auditado; `b4-diagnostico-reglas.py --save` rc0.
- **Reglas descriptivas:** `ICMP_FALLIDO=0`, `FIB_INESPERADA_FASE_ESTABLE=0`, `RTT_SOBRE_REFERENCIA=0` con umbral `3×p95_normal=0.147 ms`. Se observan **4 transiciones operativas** de fase (sondeos 15,16,32,61), no incidentes confirmados ni anomalías ML.
- Análisis de sensibilidad factor 5: umbral `0.245 ms`, 0 señales; rc0. Es referencia in-sample, **NO evaluación FP/precision/recall/F1**.
- JSON resultado fuera del repo `~/netlab360-bootstrap/analitica/b4/diagnostico-reglas-real.json` con 0600 y JSON válido.
- GitHub Actions [run 38510552044](https://github.com/recm0708/netlab360/actions/runs/38510552044) **offline-regression completed/success**, job `115677813059`, todos los pasos `success`; actualizaciones checkout@v5/setup-python@v6 mitigaron aviso anterior Node20. Solo queda aviso no bloqueante de migración del runner Ubuntu.
- Postcheck 23:23:26: Docker/netns vacíos, ens33 `192.168.47.40/24`, gateway `192.168.47.2`, 3 servicios activos, Git `main...origin/main` limpio.
- **S01 permanece 72/100 técnico estimado**. No se acredita IA ML ni métricas, y no se aumenta progreso por publicar fotografías.

**Siguiente hito funcional:** diseñar y verificar un recolector real de series temporales con etiquetas externas de control y separación por sesión para una futura evaluación ML. El baseline de reglas y los registros actuales pueden servir de referencia histórica, pero no de evaluación independiente.
