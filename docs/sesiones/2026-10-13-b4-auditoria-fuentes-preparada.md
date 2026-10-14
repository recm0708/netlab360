# NETLAB360 — B4: auditoría previa de datos reales para análisis de anomalías

**Estado:** preparado en GitHub, **pendiente de ejecución en la VM**. No hay modelo IA/ML entrenado, métricas de clasificación o tasa de falsos positivos aprobadas.

## Fuentes observadas anteriormente

1. **Datos de paquetes ICMP reales:** `~/netlab360-bootstrap/evidencias/17-b2-convergencia-*.csv`; ejecución del 13/10 con 76 muestras, sin pérdidas observadas, cinco fases `normal`, `cambio_respaldo`, `respaldo`, `cambio_principal`, `restaurada`. Disponibilidad a verificar nuevamente, ya que no es un archivo versionado.
2. **Resumen derivado:** `~/netlab360-bootstrap/evidencias/b3-linea-base/b3-resumen-convergencia.json`. No es fuente independiente del CSV: **prohibido** contarlo como nuevas muestras.
3. **Eventos del exporter vivo:** `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events*.jsonl`; categorías `WAN_PRIMARY_DOWN`, `WAN_ROUTE_CHANGED`, `WAN_PRIMARY_RESTORED`, `TOPOLOGY_STARTED`, `TOPOLOGY_STOPPED`, registros observados por muestreo, no ground truth de tráfico continuo.

## Qué mide el auditor

- Inventario real, hashes SHA256, cantidad de filas y nombres de columnas de CSV.
- Validación estricta de JSONL, timestamps y contadores por tipo de evento.
- Advertencias sobre ausencia de archivos, orígenes incompletos, etiquetas de normalidad inexistentes.
- Auditoría JSON fuera del repo `~/netlab360-bootstrap/analitica/b4/inventario-fuentes-reales.json` con permisos 0600.
- **No cambia interfaces, no ejecuta fallas WAN y no crea/mezcla muestras artificiales.**

**IMPORTANTE:** cambios WAN detectados mediante reglas del exporter no son *ground truth* independiente para evaluar la precisión de un detector entrenado sobre esas mismas reglas. Un registro solo de eventos no contiene observaciones periódicas normales; sin etiquetas independientes y particiones train/test rigurosas **no se declarará que ML es apto ni se publicarán métricas infladas**. El análisis inicial puede establecer un baseline estadístico/reglas y determinar qué datos faltan; modelos scikit-learn y comparación evaluada solo después de confirmar tamaño y diversidad.

## Precheck y tareas

```bash
cd ~/proyectos/netlab360
python3 -m unittest discover -s tests -p 'test_b4_fuentes_reales.py' -v
python3 scripts/analitica/b4-auditar-fuentes-reales.py --save
python3 -m json.tool ~/netlab360-bootstrap/analitica/b4/inventario-fuentes-reales.json >/dev/null
```

**Captura** `B4_01_Auditoria_Datos_Reales.png`: desde `INICIO CAPTURA B4_01_Auditoria_Datos_Reales` hasta `FIN CAPTURA B4_01_Auditoria_Datos_Reales` sin perder los recuentos; si es largo, dividir en `-1`/`-2`. El reporte de auditoría (metadatos) no debe subirse automáticamente con los JSONL originales; revisar privacidad e integridad.

## CI offline y limitaciones

Workflow `.github/workflows/ci-regresion-s01.yml` añadido para Python syntax/IPAM/unittest/Bash `-n`. Su ejecución en GitHub debe comprobarse como `success` antes de considerarlo una regresión CI realizada. Un paso `success` valida solo código offline, **no** FRRouting, cambios físicos de VMware ni disponibilidad del dashboard real.

## Próximo paso después del diagnóstico

Diseñar dataset temporal con observaciones periódicas reales de RTT, pérdida, estado WAN y ruta FIB y etiqueta externa del acto de corte/restauración (sin fuga temporal). Separar train/test por ensayo completo, medir TP/FP/FN/TN y precision/recall/F1, y comparar detector ML contra baseline de reglas. Las anomalías simuladas deben marcarse explícitamente, las reales por ensayos se rotulan `incidente inducido real en laboratorio`. No inventar resultados.
