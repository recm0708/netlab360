# NETLAB360 — S04 G4 terminada y G5 SLI/SLO de observabilidad

**Corte de ejecución real:** 27/10/2026, 02:41:31 (Panamá).

## G4 — Aceptación técnica

- **Persistencia de Prometheus:** tras reiniciar únicamente Prometheus S04, las 68/68 muestras históricas WAN HQ/s1p y 28/28 de la alerta `firing` se conservaron, con `startTime` de proceso distinto, comprobación de WAL y TSDB.
- **Pérdida de fuente:** al detener temporalmente solo el exporter, NOC mostró `UNKNOWN`, Prometheus `scrape=down`, alerta `NETLAB360S04ExporterUnavailable` `firing`, cero falsas alertas WAN/VLAN; al reanudar exporter, NOC volvió a `active`, con fuente fresca, scrape UP y cero alertas activas.
- **Diario SQLite:** se importaron 3 eventos G3 `pending,firing,resolved` desde el log original con SHA-256 verificado; importación repetida agregó cero. API /api/v1/incidents por sede HQ/S2 y CSV funcionaron; el usuario vio tres eventos en el NOC.
- **Persistencia del NOC real:** PID **248883→263894** tras reiniciar sólo el NOC; los 3 eventos SQLite conservaron sus IDs, marcas UTC, valores y fuentes sin cambios. NOC `active`, scrape `up`. Marcadores `S04_G4_SQLITE_PERSISTENCIA=OK` y `S04_G4_CIERRE_TECNICO=OK`.
- Capturas `S04_13` y `S04_14` confirmadas tomadas, `S04_15` confirmada tomada; `S04_16` fue solicitada pero aún no confirmada. `S04_12` tampoco ha sido confirmada. Todas las PNG nuevas siguen pendientes de recepción, auditoría y publicación; 122 PNG remotas = 15 S04.
- **G4 cerrada técnicamente**, pendiente recepción/publicación de capturas y ajustes de escrito en G6. No confundir éxito técnico con aprobación académica.

## G5 — SLI medidos vs SLO propuesto

Medición real del usuario UTC **2026-10-27T07:41:31.956556Z**, ventana retrospectiva 15m:

| Indicador | Numerador | Denominador | Resultado | Alcance |
|---|---:|---:|---:|---|
| Éxito del scrape Prometheus (`up`) | 396 | 396 | 100,000 % | Muestras registradas en la ventana para job S04, no cobertura temporal |
| Fuente confiable (`netlab360_s04_source_up`) | 396 | 396 | 100,000 % | Solo muestras de `source_up` presentes; puede quedar ausente cuando falla el propio scrape |

- La configuración `scrape_interval=2s` sugeriría aproximadamente **450 posiciones nominales** por 15 minutos. Se observaron 396 muestras. Las 54 posiciones de diferencia **no se contabilizan automáticamente como caídas**; tampoco se puede declarar disponibilidad continua 100 % en toda la ventana. Para medir cobertura con rigor deberá cuantificarse ciclo de recolección real, arranque y pérdidas de datos, sin inventar causas.
- Se incorpora `scripts/observabilidad/s04-sli-slo-observabilidad.py`, lectura local sola: `--minutes 15|30|60`, `--proposed-slo 99.0` como **objetivo académico candidato sujeto a aprobación explícita**, `--save` para JSON de auditoría fuera de Git, con no sobrescritura y presupuesto de errores entero.
- Fórmulas: `SLI(%) = 100 * exitos / muestras_registradas`; `presupuesto_propuesto = floor(muestras_registradas*(100-objetivo)/100)`; `remanente = presupuesto_propuesto - fallos_registrados`. Ventana y denominadores siempre declarados. Para 396 muestras y propuesta 99%, presupuesto discreto = **3 fallos**, resultado 0; la propuesta nunca se presenta como objetivo formal aprobado.
- El SLO **no** representa SLA contractual, disponibilidad end-to-end, jitter, latencia HTTP, pérdida de paquetes o promesa de 99 % a usuarios finales. Si se exigiera tal indicador, requiere telemetría nueva y pruebas específicas; no extrapolar métricas de `admin_up`.
- Decisión de alcance a documentar para G5: por ahora **alertas locales en NOC + cronología SQLite/CSV**, sin Alertmanager, correo, WhatsApp ni notificación externa; no dar por aprobada una prueba de entrega no configurada. Puede incorporarse notificación externa en fases posteriores con un requisito separado y pruebas de recepción.
- Aceptación G5 exige: tests offline, salida reproducible en VM con muestra y denominador auténticos, consulta NOC y regla de notificación acotada; redactar SLI/SLO propuesto en sección técnica, luego documentar aprobación o ajuste.
- G6 consolidará capturas posteriores, SHA-256, manifiestos, regresión final y apartados del informe académico.

## Enlaces

[Control S04 #4](https://github.com/recm0708/netlab360/issues/4), [SLI y alertas #21](https://github.com/recm0708/netlab360/issues/21), [historial NOC #15](https://github.com/recm0708/netlab360/issues/15).
