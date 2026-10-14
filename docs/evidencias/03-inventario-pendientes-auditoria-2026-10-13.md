# NETLAB360 — Inventario consolidado de capturas pendientes de auditoría

> **ACTUALIZACIÓN VIGENTE 13/10 ~21:20:** lote01/02 = 24 PNG publicados; lote03 = 20 PNG originales + CSV **publicados** commit `0d749df`, verificación remota OK; lote04 = **13 PNG LACP recibidos y auditados visualmente** (4+4+4+1), ZIP con SHA256 preparado pero **no publicados todavía**. [Auditoría lote04](05-auditoria-visual-lote04-lacp-2026-10-13.md). El contenido histórico posterior que menciona pendientes ya superados se conserva como registro cronológico.

## ACTUALIZACIÓN VIGENTE — 13/10/2026 20:52 PANAMÁ | LOS 20 PNG YA FUERON RECIBIDOS Y AUDITADOS

**Esta sección sustituye el estado 'pendiente de recibir' de las tablas históricas siguientes.** El usuario adjuntó de verdad **20 PNG** (B2-L2 seis, B2-L3 cuatro, B3 live/Prometheus diez). Se inspeccionaron visualmente y cotejaron con logs, 20/20 aceptadas: **18 VÁLIDAS y 2 VÁLIDAS CON OBSERVACIÓN** (B2_L2_06 por líneas nft divididas; B3_09_FINAL por prompt sudo sin contraseña). Se calcularon SHA-256 por archivo. [Auditoría y 20 hashes completos](04-auditoria-visual-lote03-2026-10-13.md).

**NO PUBLICADOS COMO PNG BINARIOS EN GITHUB TODAVÍA:** está preparado ZIP `NETLAB360_LOTE03_20PNG_AUDITADOS_2026-10-13.zip` con 20 originales, manifest y README, SHA256 del ZIP `9e11e1c3181ba62f53b1bde894f77ae4af0c6417beba1ebf10e578b90a342585`. Usuario debe transferirlo al clon `~/proyectos/netlab360/evidencias/capturas/B2_B3_lote03/`, validar los 20 hashes, commit/push, y compartir salida; hasta entonces **24 PNG anteriores publicados + 20 PNG nuevos auditados pero no publicados**.

**LABORATORIO LACP AHORA PROBADO (antes futuro):** el 13/10 20:43–20:51 `802.3ad` negoció 2→1→2 miembros activos por ambos extremos, HTTP respondió en tres estados, cleanup `RESULTADO_B2_LACP=0`, gestión intacta. [Bitácora LACP](../sesiones/2026-10-13-b2-lacp-8023ad-verificado.md). **SOLO ESTÁN PENDIENTES DE RECEPCIÓN VISUAL LAS 4 CAPTURAS LACP_01/02/03/04_FINAL**; resultados textuales ya comprobados. Las 3 opcionales históricas se mantienen opcionales. S01 matriz técnica ahora **63% estimado**. No repetir pruebas.

---


**Corte consolidado:** 13/10/2026 después de 19:45 (Panamá, UTC−05).  
**Estado verificado contra registro GitHub:** 24 PNG anteriores **ya publicados y auditados visualmente**, 19 en `evidencias/capturas/B1_B2_lote01/` (commit `d62d33b`) y 5 en `evidencias/capturas/B3_lote02/` (commit `a21b8f8`). **Omitirlos de cualquier nueva solicitud de fotos.** Enlace [auditoría B1/B2](01-auditoria-visual-b1-b2-2026-10-13.md) y [auditoría B3 histórico](02-auditoria-visual-b3-2026-10-13.md). Estas rutas/conteos se basan en la verificación de publicación documentada anteriormente; esta edición no incorpora nuevos PNG.

## I. Prioridad ALTA: 20 capturas pendientes de recepción visual

El operador aportó resultados textuales reales o bloques de comando. Conforme a su convención, se presumen capturadas **salvo que confirme alguna excepción**. No se ha recibido ni inspeccionado físicamente ninguno de estos 20 archivos ni se ha publicado su contenido binario.

| Grupo | Archivo a enviar | Evidencia respaldada por consola |
|---|---|---|
| B2-L2 | `B2_L2_02_Trunk_8021Q_VLAN110_120.png` | VID 110/120 tagged en trunk, ping 3/3 en cada VLAN |
| B2-L2 | `B2_L2_03_Aislamiento_Trunk_Dos_VLAN.png` | Ruta on-link, ping inter-VLAN 0/3, pings intravlan 2/2 |
| B2-L2 | `B2_L2_04_Postcheck_Trunk_8021Q.png` | Docker/netns vacíos, ens33/GW intactos |
| B2-L2 | `B2_L2_05_Routing_y_HTTP_Sin_ACL.png` | Router-on-a-stick, HTTP 8080/8081 OK antes de ACL |
| B2-L2 | `B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png` | nft accept 8080=1 paquete; drop 8081=2; listener real activo |
| B2-L2 | `B2_L2_07_Postcheck_ACL_HTTP.png` | Cleanup código 0, host intacto |
| B2-L3 | `B2_L3_01_HTTP_WAN_Principal.png` | FIB ambas direcciones wan-p y HTTP real HQ→S1 OK |
| B2-L3 | `B2_L3_02_HTTP_WAN_Respaldo.png` | FIB wan-b y HTTP OK durante fallo WAN-P |
| B2-L3 | `B2_L3_03_HTTP_WAN_Restaurada.png` | FIB wan-p restaurada y HTTP OK |
| B2-L3 | `B2_L3_04_Postcheck_HTTP_WAN_Final.png` | 19:44:57, contenedores/netns vacíos, marcador B2 ausente |
| B3 vivo | `B3_05_Exporter_Live_Ruta_Principal.png` | API live y métricas WAN-P |
| B3 vivo | `B3_06_Alerta_WAN_Principal_Down.png` | API/live WAN-P DOWN, route wan-b, eventos |
| B3 vivo | `B3_07_Restauracion_y_Eventos_Live.png` | WAN-P restaurada y eventos registrados |
| B3 vivo | `B3_08_Dashboard_NOC_En_Vivo.png` | Ventana del navegador durante incidencia (si se tomó; quizá -1/-2) |
| B3 vivo | `B3_09_Postcheck_Telemetria_Viva_Final.png` | Puerto 9108 libre tras cerrar exporter |
| B3 TSDB | `B3_10_Prometheus_Scrape_Real.png` | Prometheus /api/v1/query, up=1 y source_up=1 |
| B3 reglas | `B3_11_Reglas_Prometheus_Cargadas.png` | 1 grupo y 3 reglas cargadas |
| B3 reglas | `B3_12_Alerta_Prometheus_WAN_Down.png` | WAN-P DOWN y dos alertas Prometheus firing |
| B3 reglas | `B3_13_Alerta_Prometheus_Resuelta.png` | WAN-P UP, 0 alertas WAN activas |
| B3 reglas | `B3_14_Postcheck_Prometheus_Final.png` | Puertos 9090/9108 libres, host sin residuos |

**Total prioritario: 20 PNG**, sin contar archivos suplementarios de una misma captura por encuadre (ej. `-1`, `-2`). La lista es de **imágenes pendientes de auditoría visual**, no de pruebas técnicas pendientes: las correspondientes salidas de consola han sido registradas y validadas previamente. La captura B3_08 necesita confirmación de su existencia efectiva si no se llegó a tomar en el navegador.

## II. Capturas opcionales — 3 diagnósticos/cierres históricos

1. `B3_04_Postcheck_Servicio_NOC_Final.png` — consola posterior con puerto 8765 libre; el PNG `B3_04_Postcheck_Servicio_NOC.png` del lote ya publicado es una foto **distinta**, diagnóstica, con puerto 8765 todavía ocupado.
2. `B3_09_Postcheck_Telemetria_Viva.png` — postcheck intermedio con puerto 9108 aún ocupado; no es equivalente a `B3_09_Postcheck_Telemetria_Viva_Final.png`.
3. `B2_L3_04_Postcheck_HTTP_WAN.png` — postcheck del primer intento B2-L3 fallido; se conserva distinto a la foto `B2_L3_04_Postcheck_HTTP_WAN_Final.png` del ensayo HTTP exitoso.

**No recrear fallas ni encender servicios para producir estos archivos opcionales.** Si ya existen, enviarlos; de lo contrario, bastan los registros de consola documentados.

## III. Próximo lote FUTURO LACP — 4 fotos, aún no acreditadas

- `B2_LACP_01_Agregacion_Dos_Enlaces.png` — bonding modo IEEE802.3ad, agregador 2 miembros, HTTP OK.
- `B2_LACP_02_Falla_Un_Enlace.png` — agregador 1 miembro operativo, HTTP OK.
- `B2_LACP_03_Restauracion_Dos_Enlaces.png` — retorno agregador 2 miembros, HTTP OK.
- `B2_LACP_04_Postcheck_Final.png` — Docker/netns sin residuos, IP/GW y Git intactos.

**El script LACP existe en GitHub pero aún no ha sido ejecutado en la VM**, por tanto no se presupone que estas cuatro capturas estén tomadas. Si el ensayo no llega a cada bloque, no deben fabricarse capturas vacías.

## Protocolo de recepción y publicación

1. El usuario puede enviar los PNG agrupados por B2-L2, B2-L3, B3 y LACP futuro, preferiblemente originales sin editar; se comprueban nombre, legibilidad, límites de captura, comando, timestamps, resultados y ausencia de contradicciones con la consola real.
2. Registrar por archivo nombre canónico, SHA-256 de los bytes originales, tamaño, dictamen y nota técnica. Diagnósticos reales se mantienen como tales, no se convierten en éxito artificialmente.
3. Crear manifiesto CSV y lote físico `evidencias/capturas/` con ruta NUEVA; commit/push a GitHub y comprobar la presencia real de los binarios antes de marcar `PUBLICADO`.
4. **No volver a pedir los 24 PNG auditados de los lotes 01/02**. No contabilizar como recibido un PNG que solo se presume tomado por instrucción.

## Control actual

- **S01:** 59/100 puntos técnicos estimados, no calificación y 11 criterios integrales no cerrados.
- **Última prueba funcional real:** servicio HTTP HQ→S1 en los tres estados de WAN, código0 con rollback, 19:44.
- **Siguiente práctica:** LACP 802.3ad en namespaces aislados, pendiente ejecutar.
- [Issue de evidencias #43](https://github.com/recm0708/netlab360/issues/43) · [Checkpoint](../REANUDAR-AQUI.md).
