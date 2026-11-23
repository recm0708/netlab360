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

**Pendiente de ejecución en VM**: revisar CI, prueba de regresión del adaptador, health y conteo S05 en 9130 y 9131, comparación estructura de graph sin cambios, panel visible con observación fresca seguida de caducidad a UNKNOWN, conservación de `ens33`, 21 namespaces, cuatro Docker, `noqueue`, Prometheus y S04/S05. Sólo después preparar una captura **S06_F09_Panel_IA_NOC_HQ** legible que incluya el panel con ambas rutas o, si se tomó tras caducidad, un texto de validación de diseño temporal y un comando que presente los datos de prueba válidos. No declarar que el panel es productivo ni que F09 existe antes de que el usuario comparta su imagen.

## Estado

Código en PR S06-047; pendiente comprobar CI, fusionar y validar el NOC previsualizado. Issues #6/#25/#26 abiertas; S07/S08 no se consideran implementadas.
