# S06-047 — Diagnóstico IA opcional en el NOC S05 sin cambios de red

## Objetivo y fuentes

Conservar la aplicación visual de topología S05, sus 18 nodos/21 enlaces, FIB WAN, HTTP HA, LACP, SDN y estado administrativo. Añadir **un panel independiente** con diagnóstico IA exploratorio de las dos rutas de egreso del cliente HQ, aprovechando la API read-only de S06-046 en `127.0.0.1:9145`. No se crean namespaces, interfaces, contenedores, reglas, servicios productivos ni una consola NOC paralela permanente.

S06-046 ya produjo **una sola adquisición reciente** verificada con RTT 0.089 ms HQ→S1 y 0.100 ms HQ→S2, 0 % de pérdida, consenso NORMAL de tres métodos. Captura F08 aceptada. Es una observación de laboratorio con `ground_truth=UNKNOWN` que **caduca a los 30 s**; sus valores no pueden pintarse como "vivos" horas después.

## Arquitectura incremental

- `servicios/topologia-s05/app.py` conserva `/api/v1/graph`, `/healthz` y el HTML original. Añade únicamente `GET /api/v1/s06/diagnostics`, que interroga **dos URLs locales fijas**, con timeout de 1.2 s por ruta, sin aceptar IP, hostname, path ni comandos proporcionados por el navegador.
- El adaptador valida schema, modo, ruta, etiquetas, dos límites temporales, tres métodos, coherencia entre consenso y estado operacional, fuentes y alcance experimental. Excluye campos adicionales no reconocidos. Si falla una ruta, esa ruta se presenta como `UNKNOWN`, sin invalidar la otra ni sustituir estados históricos como válidos.
- `servicios/topologia-s05/index.html` añade panel responsive **Diagnóstico IA · Egreso HQ (solo lectura)**. Usa `textContent` para mostrar RTT, porcentaje de pérdida, antigüedad, consenso y resultados de P95 RTT / IsolationForest / LogisticRegression. No dibuja nuevos enlaces, no cambia colores de la topología SVG y no proyecta el diagnóstico sobre OSPF/WAN/servicios.
- El panel consulta `/api/v1/s06/diagnostics` cada tres segundos, separado del refresco S05. Si 9145 no está activo, si falta captura o si los datos superan 30 s, aparece **SIN DATOS / UNKNOWN**, nunca un estado NORMAL almacenado en pantalla.
- `tests/test_s06_noc_ia_bridge.py` evalúa integridad, fuentes, rechazo de falsos estados, pérdida de ruta, muestras obsoletas, datos no numéricos, funcionamiento opcional y la continuidad del contrato S05.

## Criterios de seguridad

Los resultados continúan como **diagnóstico experimental de egreso HQ**: `ground_truth=UNKNOWN`, `production_deployment_authorized=false`, `network_mutations_authorized=false`. Si todos los modelos indican degradación, el adaptador permite mostrar el consenso `DEGRADED` pero conserva el estado operacional `UNKNOWN` por falta de corroboración independiente; ninguna acción de remediación se habilita. No sustituye SNMP, FIB, estado OSPF, calidad QoS WAN ni un test prospectivo de generalización.

Un NOC sano **no requiere** que la API de IA esté disponible: el componente adicional es opcional y no participa en el cómputo de `/healthz`. El navegador no puede invocar `sudo`, shells ni nuevos pings mediante esta vista.

## Despliegue de validación temporal

**No reiniciar el servicio S05 que ya escucha 9130.** Tras aprobar CI, arrancar un NOC de previsualización en `127.0.0.1:9131` usando `app.py --serve --port 9131` (mismo código y catálogo, distinto puerto temporal) y una API IA temporal 9145 con `scripts/s06/inferencia_hq_readonly.py --serve`. Sólo entonces realizar **una** nueva medición de baja carga `scripts/s06/telemetria_hq_live.py --collect`; la API de lectura debe responder con muestras de menos de 30 s, y el NOC de previsualización debe exponer ambas rutas a través de `/api/v1/s06/diagnostics`.

Tras 30 s la captura caduca; el panel vuelve a UNKNOWN, incluso cuando NOC S05 y sus gráficos siguen funcionando. Detener únicamente los dos procesos de previsualización 9131/9145; no interrumpir el servicio NOC estable 9130. Para ver la interfaz desde Windows durante la validación, usar un túnel SSH temporal sólo sobre 9131, nunca exponer HTTP a 0.0.0.0.

## Aceptación y evidencia

**Ejecución técnica validada en VM**: 21 pruebas de integración S06 y 14 pruebas de S05 aprobadas, health de NOC 9130 y previsualización 9131 correctos, grafo comparado (18 nodos y 21 enlaces), observación nueva recibida por API, fail-closed al detener el servicio de IA, controlador `NONE/BASELINE`, 21 namespaces y cuatro contenedores conservados. **La inspección visual en navegador todavía está pendiente**. Se prepara la captura **S06_F09_Panel_IA_NOC_HQ** mediante previsualización en navegador Windows por túnel SSH, con medición nueva y datos frescos en ambas tarjetas. Debe mostrar el panel y contexto NOC sin confundir estado operacional acotado con ground truth. **No se declara F09 aprobada hasta recibir y revisar su PNG**.

## Estado

**Código y CI aceptados:** PR [#172](https://github.com/recm0708/netlab360/pull/172) fusionado `5fd9986`; regresión general **751 pruebas** (750 aprobadas, una omitida), CI específica S05 correcta. **Aceptación técnica de backend/API en VM lograda** con `S06-047_VALIDACION_COMPLETA=OK` y `RESULTADO_RC=0`; aún falta comprobar el diseño visual en el navegador y aprobar F09. Issues #6/#25/#26 abiertas; S07/S08 no se consideran implementadas.

## Verificación técnica real — 23/11/2026

La VM sincronizó `main` en `70671a4`, ejecutó 21 pruebas unitarias del puente IA y 14 de la topología S05, todas correctas. El NOC estable `9130` respondió `healthy`; las previsualizaciones temporales del NOC `9131` y de IA `9145` estuvieron activas durante la verificación y se detuvieron al concluir, sin reiniciar NOC S05.

**Adquisición inédita limitada a ICMP:** fuente privada `~/netlab360-bootstrap/s06/telemetria-hq-live/S06_046_HQ_20261123T095025Z_065b6b10.json`. HQ→S1 RTT 0.062 ms, consenso de tres métodos NORMAL, edad 0.99 s; HQ→S2 RTT 0.064 ms, consenso NORMAL, edad 1.01 s. `ground_truth=UNKNOWN` conservado, sin aprobación para actuar. Grafo S05 comprobado: **18 nodos, 21 enlaces**, mismo inventario que el servicio original. `PANEL_HTML=INTEGRADO` y `S06_047_DIAGNOSTICO_NOC=OK`.

**Contención:** después de detener la API IA se obtuvieron `HQ_A_S1=UNKNOWN` y `HQ_A_S2=UNKNOWN` desde el NOC de previsualización, `S06_047_FAIL_CLOSED=OK`. Controlador HQ `NONE/BASELINE`, NOC original `healthy`, 21 namespaces, cuatro contenedores, ninguna mutación de red y procesos de preview detenidos. Registro `~/netlab360-bootstrap/s06/validacion-s06-047-20261123_045016/S06_047_Validacion_Completa.txt`, fin `S06-047_VALIDACION_COMPLETA=OK` y `RESULTADO_RC=0`.

**Pendiente concreto:** confirmación visual del panel en navegador de Windows y captura F09; el TXT del comando de validación no reemplaza la evidencia visual. Toda observación fresca caduca en 30 s. No se programa adquisición automática, no se despliega como servicio persistente y no se atribuye capacidad predictiva prospectiva.
