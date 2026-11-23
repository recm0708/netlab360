# S06-046 — Mediciones frescas HQ, validación de calidad e inferencia exploratoria

## Propósito

Después de S06-045 (replay histórico verificado y captura F07 aprobada) se incorpora una fuente de **mediciones recientes** desde el cliente verdadero `nl360-s02-h-hq-120`, hacia `10.71.20.20` (S1) y `10.72.20.20` (S2). Son seis solicitudes ICMP por ejecución, **tres por ruta**, por `sudo -n ip netns exec` permitido y con origen/destino fijos. No se inducen fallas, no se crean interfaces/namespace ni se cambia qdisc, FRR u otros servicios.

**Esta etapa es observación real de baja carga, no una nueva evaluación independiente de sensibilidad**: las respuestas a mediciones nuevas carecen de etiqueta de verdad de terreno de degradación, que siempre se conserva como `UNKNOWN`. La comparación con modelos de S06-044 es exploratoria y no certifica otras clases de fallo ni predicción temprana.

## Código y contrato

- `scripts/s06/telemetria_hq_live.py` implementa `--collect`, preflight de gestión e infraestructura, verifica estado root `NONE/BASELINE` y snapshot de qdisc/rutas/NOC tanto antes como después de las pruebas; reaprovecha `measure_ping` del capturador existente y genera un archivo privado de cada captura.
- `scripts/s06/inferencia_hq_readonly.py` mantiene los endpoints de S06-045 para replay y amplía `GET /api/v1/s06/live?route=HQ_A_S1` o `HQ_A_S2`. **Los GET no realizan ping**, sino que leen exclusivamente la última observación creada con `--collect`.
- `tests/test_s06_telemetria_live_hq.py` prueba origen/destino allowlist, qdisc/NOC, tiempo, calidad y estados UNKNOWN; utiliza dobles offline, nunca redes reales.
- Archivo actual fijo: `~/netlab360-bootstrap/s06/telemetria-hq-live/ultima.json`. Copia inmutable por captura `S06_046_HQ_*.json` en el mismo directorio privado; no incorporar observaciones privadas al repositorio.

## Comportamiento seguro

La muestra solo es admisible si acredita esquema, origen HQ, dos destinos exactos, tres paquetes enviados y recibidos en cada ruta, cuatro características ICMP finitas, 0 % pérdidas, fuentes NOC/servicios saludables, `noqueue`, control root `NONE/BASELINE` y comprobaciones antes/después. Cualquier pérdida, muestra parcial, fuente fallida, archivo ausente, edad superior a **30 s**, tiempo futuro incompatible, identificación incorrecta o modelo no verificable hace devolver `UNKNOWN`.

Con consenso binario **NORMAL** de los tres métodos y guardas de la red verificadas se devuelve `operational_state=NORMAL` **acotado al egreso de HQ** y sin afirmar normalidad global; la etiqueta ground truth de la medición permanece `UNKNOWN`. Si un modelo discrepa o todos señalan DEGRADED sin corroboración independiente, se devuelve `operational_state=UNKNOWN` junto con la indicación binaria exploratoria. Nunca se autorizan cambios automáticos.

La API temporal sigue en `127.0.0.1:9145`, sin instalación como servicio ni apertura hacia Windows. No modifica el NOC S05 actual. Una integración visual con el NOC requerirá un adaptador de lectura específico después de aprobar la adquisición real.

## Aceptación operativa propuesta

1. Fusionar código tras CI y ejecutar una adquisición en `netlab360-lab` con permisos sudo previamente autenticados, sin ejecutar scripts bajo root.
2. Verificar archivo original reciente, tiempos UTC, features por ruta, estado de guardia y ausencia de modificaciones de red.
3. Ejecutar API temporal en loopback y consultar ambas rutas *antes* de los 30 s de antigüedad. Detenerla y comprobar que el puerto quede libre.
4. Reconsultar el archivo tras vencer 30 s: debe responder `UNKNOWN` con `LIVE_TELEMETRY_MISSING_STALE_OR_INVALID`. No lanzar otra medición para forzar clasificación ni inventar el estado de falla.
5. Comprobar 21 namespaces, cuatro contenedores, `ens33` 192.168.47.40/24, gateway .2, `qdisc noqueue`, NOC/Prometheus activos y árbol Git limpio. **Solo entonces** preparar la captura F08; no declararla aprobada antes de recibir y revisar su PNG.

## Límites

Los modelos se entrenaron y probaron con ventanas de duración y número de paquetes distintos de este muestreo (tres paquetes por ruta). No afirmar equivalencia de distribuciones, confiabilidad productiva ni mejora de F1 en vivo; esta etapa valida el transporte y las condiciones de calidad para inferencia. S06 permanece incompleta; las issues #6, #25 y #26 y S07/S08 permanecen abiertas.
