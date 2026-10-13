# B3 — Primera ejecución del servicio API / panel NOC histórico

## ACTUALIZACIÓN VERIFICADA POSTERIOR A 16:09 — UI EVIDENCIADA Y PUERTO LIBRE

La auditoría visual [lote 02 B3](../evidencias/02-auditoria-visual-b3-2026-10-13.md) recibió y examinó realmente `B3_01`, `B3_02`, dos capturas complementarias `B3_03` y `B3_04`. Las dos B3_03 muestran navegación real `http://127.0.0.1:8765/`, banner **HISTÓRICO / NO EN VIVO**, 76 sondas, 76 éxitos, 0 errores, gráficas de fase y tabla FIB. Ya no está pendiente revisión visual del navegador. B3_04 prueba correctamente que a 15:52 el puerto estaba todavía ocupado; una **salida posterior real de terminal a las 16:09:58** confirmó `PUERTO_8765_LIBRE: SI`, con Docker/netns vacíos y red inalterada. Se valida por tanto el **cierre operativo del servidor**, pero no hay captura PNG del postcheck final; puede tomarse una consulta sin volver a levantar la app. **El túnel SSH del cliente Windows es independiente y quizá permanece abierto**; cerrarlo con Ctrl+C si es el caso.

S01 se estima en **45%** tras acreditar dos puntos B3 por API/HTML retrospectivos ejecutados realmente. NO se han implementado Prometheus scrape, exporter de FRR, alarmas ni dashboard con datos WAN live. Los cinco PNG B3 todavía no están transferidos físicamente a GitHub; se preparó ZIP/manifiesto para ello.

---


**Fuente observada:** salida real aportada por el usuario desde tres terminales el 13/10/2026 entre 15:48 y 15:52 Panamá.  
**Estado:** **API HTTP local probada**, consultas históricas correctas; **cierre completo del proceso pendiente de verificar**. No confundir con NOC en tiempo real.

## Ejecución comprobada

- `git pull --ff-only origin main` trajo la app a Ubuntu, último checkout local comprobado `07c2731` (antes de commits GitHub posteriores), Git `## main...origin/main` limpio.
- `ast.parse` validó `servicios/noc-historico/app.py`: `B3_SINTAXIS: OK`.
- `python3 servicios/noc-historico/app.py --check`: `B3_DATOS_HISTORICOS: OK`, `B3_MUESTRAS: 76`, `B3_METRICAS_LINEAS: 14`, `RESULTADO_B3_CHECK=0`, `RESULTADO_VALIDACION_B3=0`.
- Antes de iniciar, `ss -ltn '( sport = :8765 )'` no mostraba LISTEN; `ens33=192.168.47.40/24` y default `192.168.47.2`.
- Se inició realmente a **15:48:42 -05:00** `python3 servicios/noc-historico/app.py --serve`. Mensaje `B3_NOC_LOCAL: http://127.0.0.1:8765/`, `B3_MODO: HISTORICO | NO EN VIVO`. El servidor escucha solo en loopback de Ubuntu `127.0.0.1`, no publica puerto en VMnet8.
- `GET /healthz` → HTTP **200**, JSON `{"status":"ok","mode":"historical","live_monitoring":false,"samples":76}`.
- `GET /api/v1/baseline` → **200**, los 76 registros históricos en 5 fases con rutas FIB y RTT medio.
- `GET /metrics` → **200**, series `netlab360_icmp_samples` y `netlab360_icmp_losses` por fase. **Prometheus no está configurado ni scrapeando; estas son métricas históricas.**
- `GET /` → **200**; se observaron solicitudes a `/` desde el servidor y se ejecutó el túnel Windows `ssh -N -L 8765:127.0.0.1:8765 netlab360`. La **visualización real en navegador no ha sido aportada como PNG**, así que NO dar por auditada visualmente la UI.
- `GET /no-existe` → **404** y `POST /api/v1/baseline` → **405**. Se observó rechazo a ruta inexistente y operación de escritura.

## Evidencia y estado de limpieza

- **`B3_02_API_y_Metricas_Historicas.png`**: salida de terminal con marcadores `INICIO CAPTURA B3_02` / `FIN CAPTURA B3_02`, hora 15:49:07. **El PNG todavía NO se ha enviado; se considera tomado por convención del usuario, pendiente de inspección visual**.
- **`B3_03_Panel_NOC_Historico.png`**: captura visual del navegador aún NO recibida.
- **`B3_04_Postcheck_Servicio_NOC.png`**: el bloque de terminal enviado a **15:52:24** imprime `PUERTO_8765_LIBRE: NO`. Docker y netns están vacíos, ens33 y GW intactos, los tres servicios activos, Git limpio. **NO MARCAR EL POSTCHECK DE PUERTO COMO SATISFACTORIO.**
- El log de Terminal 1 termina en solicitudes HTTP 404/405, sin evidencia explícita de `B3_SERVIDOR_DETENIDO=SI` o `Ctrl+C` posterior. **Estado actual del puerto después de 15:52 no verificado**; primero se debe detener mediante Ctrl+C en terminal 1 y cerrar túnel en PowerShell, luego ejecutar `ss -H -ltn '( sport = :8765 )'` y registrar `PUERTO_8765_LIBRE: SI` antes de dar por limpio.
- Si el proceso se detuvo después, enviar el postcheck y actualizar este registro; no asumir que sigue activo ni que terminó de forma segura sin salida.

## Criterios pendientes

**Realmente logrado:** validación de esquema, servicio HTTP histórico funcional y respuestas correctas (200/404/405), acceso únicamente por SSH/túnel. **Pendiente:** demostrar visualmente la UI en PNG, cierre de servicio y liberación del puerto; instrumentar **telemetría viva** desde routers/servicios, Prometheus real, eventos y alarmas de WAN, integración S01.

No modificar `ens33`, VMnet8 ni rutas host para resolver un puerto loopback. S01 continúa **43% estimado** hasta que una revisión de control justifique acreditar subhito B3.
