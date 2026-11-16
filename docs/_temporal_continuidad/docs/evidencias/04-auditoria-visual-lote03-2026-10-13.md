# NETLAB360 — Auditoría visual del lote 03: B2-L2, B2-L3 y B3 vivo/Prometheus

> **Ubicación VIGENTE desde el commit [570088c](https://github.com/recm0708/netlab360/commit/570088c5ed3fd7ce3b888facecfe79c39e78005f):** los PNG ya versionados se consultan directamente en [`evidencias/capturas/`](../../evidencias/capturas/) y sus CSV en [`evidencias/manifiestos/`](../../evidencias/manifiestos/). 20 capturas del lote03; CSV actual `../../evidencias/manifiestos/MANIFIESTO_SHA256_NETLAB360_LOTE03_20PNG.csv`. Cualquier ruta antigua `.../lote0X/` que figure a continuación describe su **ubicación histórica**, no la actual. La migración conservó los bytes (Git detectó 100% de similitud). El lote05 aún no figura físicamente en GitHub.

> **Actualización posterior verificada:** los 20 PNG y su manifiesto CSV **FUERON PUBLICADOS EN GITHUB** el 13/10/2026 por el usuario, commit [`0d749df`](https://github.com/recm0708/netlab360/commit/0d749dff5a27c4c108aea7cdec8ddb5723394bb1), `PUBLICACION_GITHUB=OK`, `COMMIT_LOCAL=COMMIT_REMOTO=0d749dff5a27c4c108aea7cdec8ddb5723394bb1`, total 21 archivos. Las menciones de “pendiente” abajo describen el estado histórico de las 20:52 y no el vigente.

**Corte:** 13 de octubre de 2026, 20:52 Panamá (UTC−05).  
**Fuente:** **20 imágenes PNG realmente adjuntadas por usuario en conversación** e inspeccionadas visualmente; cálculo SHA256 y dimensiones mediante PIL sobre sus archivos binarios reales, sin OCR y sin modificar bytes. **Dictamen: 18 VÁLIDAS y 2 VÁLIDAS CON OBSERVACIÓN, 0 rechazadas.** Los resultados están respaldados por salidas anteriores de terminal (B2-L2 19:00/19:14, B2-L3 19:43, B3 live 17:38-18:36).

**Estado de publicación binaria: PENDIENTE**. Se ha generado en la conversación un ZIP `NETLAB360_LOTE03_20PNG_AUDITADOS_2026-10-13.zip` de 20 PNG sin modificar, un manifiesto CSV, y fichero de instrucciones. **La ruta de descarga sandbox no es una URL pública estable de GitHub; el usuario debe transferir ZIP al clon de la VM y hacer commit/push, con comprobación de hashes.** No atribuir estos nuevos archivos a GitHub hasta verificar commit remoto.

| N.º | Archivo original | Dictamen | Evidencia/observación | SHA-256 |
|---|---|---|---|---|
| 01 | `B2_L2_02_Trunk_8021Q_VLAN110_120.png` | VALIDA | Trunk VLAN110/120 y 3/3 ICMP en cada VLAN | `266fa7da380fac739674c9c80bfbaa0f896f31a6d88410ab61f3115d81678e89` |
| 02 | `B2_L2_03_Aislamiento_Trunk_Dos_VLAN.png` | VALIDA | Ruta on-link inter-VLAN 0/3; intra-VLAN 2/2 y 2/2 | `8fa81c20d6d6e7efc2b80e6ab55cb0d8f374f5c45c6f6e45d04fb88a6946551f` |
| 03 | `B2_L2_04_Postcheck_Trunk_8021Q.png` | VALIDA | Red de gestion, Docker/netns y Git intactos | `821937a43ec7241b616c2e685d4c6ebf20b1883b96e065382a3ac7a5cefd235d` |
| 04 | `B2_L2_05_Routing_y_HTTP_Sin_ACL.png` | VALIDA | Subinterfaces router y HTTP8080/8081 accesibles sin ACL | `3d8d2a4037245a4be0737217ad799c9d1269a089bb24cf7fc574f6565f89df90` |
| 05 | `B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png` | VALIDA CON OBSERVACION | Nft reglas largas partidas por ancho; 8080 accept 1 pkt, 8081 drop 2 pkt, servicio remoto activo | `130fde1a7275b86e77a7630cff9e66f6545b7d5d8973f81cded6738e68e626bc` |
| 06 | `B2_L2_07_Postcheck_ACL_HTTP.png` | VALIDA | Cleanup sin recursos y red de gestion intacta | `7878ae882d82d572e5389ab9cc8181e237adf485d2a8461fd62a67e1e117c8f2` |
| 07 | `B2_L3_01_HTTP_WAN_Principal.png` | VALIDA | FIB HQ/S1 wan-p y HTTP de host HQ a servidor S1 OK | `0efe4cb57eebce623f376dd2c495226996d1c8ff02e8a0bf3ba6cf61aea5feed` |
| 08 | `B2_L3_02_HTTP_WAN_Respaldo.png` | VALIDA | FIB HQ/S1 wan-b y HTTP de host HQ a servidor S1 OK | `5cfeecbfba9a5ec8da49d6f70021f5e29d9a8823941db9b49244c04cf3bc8fa0` |
| 09 | `B2_L3_03_HTTP_WAN_Restaurada.png` | VALIDA | FIB HQ/S1 wan-p restaurada, HTTP correcto | `926e752dcb18362afec01cd9d1bb8834a78d5125e2e6dcee30f37063208e25a6` |
| 10 | `B2_L3_04_Postcheck_HTTP_WAN_Final.png` | VALIDA | B2 sin estado ni contenedores/netns, gestion intacta | `d4a2dadc093121b6f85c5d648fb8d454f52be88d20c015c5810b22a93ce5199c` |
| 11 | `B3_05_Exporter_Live_Ruta_Principal.png` | VALIDA | Exporter fuente viva, ruta WAN-P, freshness true, series /metrics | `065c0c52119bf875c90cf8a1127d5adb5041794eb363ca0e4223c7b1678a5da0` |
| 12 | `B3_06_Alerta_WAN_Principal_Down.png` | VALIDA | Evento exporter WAN_PRIMARY_DOWN y FIB respaldo WAN-B; no alertmanager | `19529479e05876ae91bfa2f2533fc18a2f5233560e471b82b3ea611ab2b66175` |
| 13 | `B3_07_Restauracion_y_Eventos_Live.png` | VALIDA | WAN-P restaurada, eventos JSON live y conteos | `068155e4b85b9c64c7088b47f7c1c15efd0fae252c96cc22de5709957d1fcf3b` |
| 14 | `B3_08_Dashboard_NOC_En_Vivo.png` | VALIDA | Navegador 127.0.0.1:9108, dashboard exporter WAN-P down/FIB wan-b, NO Prometheus UI | `18e3493e024382f6301dfebd0fd209501dc553d32f0e8e72007c885beabb519b` |
| 15 | `B3_09_Postcheck_Telemetria_Viva_Final.png` | VALIDA CON OBSERVACION | Prompt sudo visible sin password; puerto 9108 libre y servicios activos | `aa42a4bbfd6298ae39a9f51a37e5f16735ba72a29ecf87f415a4e32acae124cf` |
| 16 | `B3_10_Prometheus_Scrape_Real.png` | VALIDA | Target netlab360-frr-live up=1, fuente live=1 | `77ec1ee2651c39ac9bdeaf72525bebbe8c04a3a3f584cf08f72ce88c7aa2f530` |
| 17 | `B3_11_Reglas_Prometheus_Cargadas.png` | VALIDA | 1 grupo, 3 reglas y promtool RC0 | `5d7c0a1b15b61a09238a0c9335de577f707b0735a19e669a2682c83797d653ce` |
| 18 | `B3_12_Alerta_Prometheus_WAN_Down.png` | VALIDA | Dos reglas alertas reales Prometheus firing con timestamp | `fcc6cdfaa81be5d97f8a88a82da33c60e33bddac5042642b5b3a584090163398` |
| 19 | `B3_13_Alerta_Prometheus_Resuelta.png` | VALIDA | WAN-P restaurada y 0 alertas WAN activas | `98457dbbf0e81f7d5549e15bb20972e9edc113720c6a33151dfb5e4bfd86947a` |
| 20 | `B3_14_Postcheck_Prometheus_Final.png` | VALIDA | 9090/9108 libres, Docker/netns vacíos y Git sin cambios | `dfac593c4f9a508de1270870d590a722ccf5c0932e2f80f3505eec23f16e51dc` |

## Integridad de paquete

- ZIP: `NETLAB360_LOTE03_20PNG_AUDITADOS_2026-10-13.zip` — tamaño **1,011,954 bytes**, **SHA-256 `9e11e1c3181ba62f53b1bde894f77ae4af0c6417beba1ebf10e578b90a342585`**.
- CSV manifest: `MANIFIESTO_SHA256_NETLAB360_LOTE03_20PNG.csv` — SHA-256 `64ebe7248eae4659d31df1150320d75011ed473566e0970d4c01e7b08bbe41f9`.
- ZIP contiene `capturas/<20 PNG>`, manifiesto CSV y fichero `INSTRUCCIONES_LOTE03_NETLAB360.txt`. Prueba de integridad ZIP interna exitosa.
- Ruta recomendada dentro del repositorio: `evidencias/capturas/B2_B3_lote03/`. No reutilizar lotes 01/02.
- Las **24 PNG antiguas** están auditadas y publicadas en `B1_B2_lote01` / `B3_lote02`. Lote 03 es adicional, sin duplicarlas.

## Verificación de calidad y límites

- **B2-L2:** trunk/aislamiento y router-on-stick con ACL realmente probado; la línea nft extensa en B2_L2_06 se parte, pero se distinguen reglas, HTTP 8080 aceptado y 8081 rechazado junto a contadores. No se requiere recaptura.
- **B2-L3:** tres bloques llevan rutas FIB y cuerpo HTTP en WAN-P→WAN-B→WAN-P; no se demuestra ausencia de microcortes durante reconvergencia.
- **B3:** `B3_08` muestra **dashboard del exporter local** (en vivo por sondeo, ruta respaldo); `B3_12` muestra **dos alertas firing reales del motor Prometheus**; `B3_13` evidencia ausencia de alertas activas tras restauración. Esto **NO acredita** Alertmanager, entrega externa ni panel multisede final.
- **B3_09_FINAL:** aparece solicitud de autenticación `sudo` sin contraseña visible; captura legítima de cierre limpio (puerto 9108 libre) sin secretos.
- Las capturas delimitadas del log con resultados no muestran siempre el comando original que disparó la prueba; correlacionar con scripts versionados, bitácoras y logs originales al armar informe.

## Próximos lotes y estado real de práctica

**Laboratorio LACP de 20:43–20:51 del 13/10 completado según salida textual:** ambos bonds IEEE802.3ad agregan 2→1→2 puertos, HTTP responde en tres estados, `RESULTADO_B2_LACP=0`, Docker y namespaces limpios, red administrativa intacta. **Todavía no se han recibido PNG LACP_01/02/03/04_FINAL para auditoría visual**, no se incluyen en este ZIP. Los puertos y velocidades reportadas pertenecen a `veth` virtual, no a NIC/switches físicos de VMware.

**Clasificación exacta:** 20/20 imágenes auditadas; 20/20 imágenes *pendientes de publicación física en GitHub*. S01 y estados de la práctica se controlan en `docs/control/01-avance-s01.md`. La siguiente acción del usuario es **transferir el ZIP y publicar solo esos 20 PNG originales**; después verificar la nueva ubicación en GitHub antes de cambiar ese estado.
