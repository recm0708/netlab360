# NETLAB360 — G5 mediciones 15/60 min y preparación G6 — 27/10/2026

**Fuente:** transcripción real del operador, pasos 4.54–4.57. Todo se ejecutó con FRR/WAN/LAN, exporter 9110, Prometheus 9091 y NOC 9120 activos. No inventar mediciones ni registrar un SLO aprobado por adelantado.

## G5 resultados observados

- `main` sincronizada hasta `ee1eb22`, árbol limpio; **6/6** pruebas offline SLI/SLO y **8/8** historial NOC correctas. NOC `active`, Prometheus scrape `up`, 3/3 eventos auténticos G3 consultables; `S04_G5_PREPARACION=OK`.
- Ventana **15m**, observación UTC **2026-10-27T07:51:08Z**:
  - scrape `up`: **450/450** muestras exitosas = **100.000 %**; 0 fallos, presupuesto propuesto a 99 % **4**, remanente +4.
  - fuente condicional `netlab360_s04_source_up`: **450/450** = 100.000 %, presupuesto candidato 4, remanente +4.
- Ventana **60m**, observación UTC **2026-10-27T07:51:08Z**:
  - scrape `up`: **1698/1740** = **97.586 %**, **42** fallos observados. Presupuesto a 99 % **17**, remanente **−25**, **NO cumpliría** el SLO candidato.
  - fuente condicional: **1698/1698** = **100.000 %** entre series disponibles. La fuente `source_up` puede estar ausente durante scrapes fallidos; NO usar como indicador autosuficiente del servicio.
- Cadencia nominal de scrape 2s → ~**450** posiciones esperadas en 15m y ~**1800** en 60m. Las 60 posiciones de diferencia con los 1740 scrapes registrados en 60m **no se clasifican** automáticamente como indisponibilidad; requerirían corroboración de timestamps/arranque/lagunas de colección. Tampoco se presenta 100 % de cobertura temporal a partir de 100 % de las muestras.
- Archivos **originales fuera de Git**:
  - `~/netlab360-bootstrap/s04/evidencias/S04_G5_SLI_2026-10-27T0751080000_15m.json` (844 B)
  - `~/netlab360-bootstrap/s04/evidencias/S04_G5_SLI_2026-10-27T0751080000_60m.json` (868 B)
- El cálculo de SLO 99 % fue etiquetado explícitamente `S04_G5_SLO_ESTADO=PROPUESTA_NO_APROBADA`, no equivale a SLA contractual ni mide extremo a extremo. El 97.586 % puede reflejar el ensayo controlado de pérdida de exporter, pero no se ha demostrado en el log la atribución temporal exacta de todos los fallos a esa maniobra. Conservar el incumplimiento candidato sin normalizar ni eliminar datos.
- **Política de alcance sugerida, pendiente ratificación**: S04 notificaciones locales mediante alertas Prometheus + NOC y eventos SQLite/CSV comprobados, sin Alertmanager ni envío externo. Toda mejora posterior de notificaciones externas exigirá pruebas de entrega y configuración explícita.

## G6 respaldo SQLite verificado

- Copia consistente por API sqlite3 backup, fuente operativa intacta.
- `PRAGMA integrity_check=ok`, tres eventos G3 fuente `verified_G3_terminal_log`.
- Ruta original: `~/netlab360-bootstrap/s04/evidencias/S04_G6_Respaldo_Historial_20261027T075205880317Z.sqlite3`.
- SHA-256 **`23f1db998a3e9b4811507e3f7b50d063d76e5e3971931acb491683c120f8d820`**. Mantener fuera del repositorio por ser base operacional, salvo decisión explícita de paquete académico con revisión de privacidad/retención.

## G6 siete PNG confirmadas en Windows

El inventario de PowerShell localizó siete archivos legibles, **aún no recibidos ni auditados byte a byte**, en `C:\Users\ruben\Pictures\Screenshots\...`:

| Archivo | Bytes |
|---|---:|
| `S04_12_Historico_Prometheus_G3_Persistente_Tras_Reinicio.png` | 70377 |
| `S04_13_NOC_Fuente_No_Disponible_UNKNOWN.png` | 71918 |
| `S04_14_NOC_Recuperacion_Fuente_Observabilidad.png` | 15303 |
| `S04_15_NOC_Historial_Incidentes_G3_Persistente-1.png` | 82513 |
| `S04_15_NOC_Historial_Incidentes_G3_Persistente-2.png` | 54831 |
| `S04_16_Persistencia_SQLite_Historial_NOC_Tras_Reinicio.png` | 25577 |
| `S04_17_Indicadores_SLI_SLO_Observabilidad.png` | 155595 |

Por publicar después de inspección y SHA256 de bytes reales: lote S04 03, ocho archivos esperados (7 PNG y 1 CSV). Inventario REMOTO al corte **122 PNG (S04=15)**, no incrementar hasta fusionar y contrastar nuevo inventario; objetivo **129 PNG (S04=22)**.

## Puertas

- **G4 aceptada técnicamente** sobre datos originales (Prometheus WAL/TSDB tras reinicio, UNKNOWN sin falsas alertas WAN/VLAN, SQLite tres eventos idénticos tras reiniciar NOC).
- **G5 parcialmente validada:** SLI medidos, ventanas y presupuestos reproducibles; falta decisión de objetivo y alcance formal de notificaciones, correlación/documentación y aceptación.
- **G6 parcialmente preparada:** copia de SQLite autenticada, capturas localizadas; falta importación/publicación manifiesto, postcheck final OSPF/LAN, informe académico en secciones 5/6/7/8 y aceptación de la fase. No desmontar topología antes de programar siguiente etapa.
