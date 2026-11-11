# NETLAB360 · S05 — Aceptación visual del NOC V7.2 y preparación de conmutación observada

**Corte:** 11/11/2026, hora de Panamá. **Alcance:** supervisión de rutas FIB desde el NOC y preparación de una prueba controlada de conmutación WAN en S1. Ninguna nueva falla se ha inducido al documentar este corte.

## Diseño V7.2 aceptado por el operador

La imagen aportada muestra la ruta primaria HQ–S1 seleccionada en **verde lima**, diferenciada del verde de la otra primaria; ambos respaldos siguen discontinuos/grises, y el inspector de HQ–S1 muestra **FIB elegida, siguiente salto `10.78.0.2`, origen Linux FIB R-HQ**. No hay borde ni recuadro violeta. El usuario indicó **«ahora sí me parece bien»** respecto al diseño, y solicitó mejorar más adelante los textos de supervisión para una presentación empresarial y avanzar a la siguiente actividad.

**La imagen de revisión no equivale automáticamente a evidencia oficial `S05_29`**: falta confirmar guardado con encuadre desde «Mapa corporativo» hasta «Origen ruta» y la leyenda completa `S05_30`; no repetir S05_24–28.

La ejecución de los 28 tests S05 fue **OK**. El lote 67 posterior no imprimió sus marcas finales porque la instrucción `grep -Fq 'S05_V72_TOGGLE_NODE=OK'` buscó en el log del runner una salida de Node capturada por `subprocess.run(capture_output=True)` dentro de unittest; su ausencia en el TXT **no constituye fallo del test**. Modificar la validación para comprobar únicamente el resumen `Ran 28 tests` + `OK` y el caso `test_v72_real_javascript_toggle_in_node ... ok`, y ejecutar separadamente `node --check` y `app.py --check`.

## Actualización editorial del NOC

Código versionado en `servicios/topologia-s05/index.html`: subtítulo orientado a operaciones, encabezado del mapa centrado en infraestructura observada, resumen de estado **«Supervisión operativa»** según fuentes disponibles; estado FIB presentado como verificado solo cuando `routing.available=true`. El panel «Expansiones futuras» pasó a «Integraciones de infraestructura», con activos adicionales realmente inventariados y sin promesas de implementación. Se mantienen advertencias técnicas verdaderas en la leyenda y los estados desconocidos no se convierten artificialmente en OK.

No se han cambiado rutas, cables, bridges, namespaces ni servicios de red por esta actualización editorial.

## Nuevo experimento preparado (NO EJECUTADO)

- Observador `scripts/validacion/s05-observar-conmutacion-noc.py` **solo lectura**: consulta `http://127.0.0.1:9130/api/v1/graph`, clasifica `PRINCIPAL → RESPALDO → PRINCIPAL` por FIB observada, requiere telemetría S04/FIB confiable y baseline primaria; produce archivo `JSONL` local con sellos UTC, interfaz y siguiente salto. Parámetros `--precheck --site S1` y `--watch --site S1 --seconds 90 --interval 0.5`. No ejecuta Docker, nsenter, ip link, FRR, SSH ni sudo. Límite de observación 15–180 s.
- El script preexistente y ya probado `scripts/laboratorio/s02-failover-wan.py` agregó **opción `--hold-seconds N`** (0–30 s, default **0**, sin alterar el comportamiento histórico). Durante la conmutación validada mantiene el enlace principal abajo de forma acotada y, en `finally`, lo restaura, valida FIB principal y conectividad y verifica `ens33`; maneja SIGHUP/SIGTERM para intentar la restauración. No protege contra SIGKILL ni pérdida de energía.
- Los nuevos tests `tests/test_s05_observador_failover.py` validan estados principal/backup, ausencia de telemetría, precheck, lectura limitada y `finally`. Las pruebas totales S05 pasan de **28 a 36**. Workflow `.github/workflows/ci-s05-topologia.yml` incluye pruebas offline y compilación Python de ambos scripts. CI no ejecuta fallas reales.
- El código del observador y la opción de ventana no están aún sincronizados ni ejecutados en la VM; **primero comprobar Git limpio, tests 36/36, API 9110/9130, sudo -n disponible y FIB principal**.

## Secuencia próxima para reanudación

1. Sincronizar `main`, comprobar `python3 -m unittest discover -s tests -p 'test_s05_*.py' -v` (36/36), `node --check`, `python3 servicios/topologia-s05/app.py --check`, `git status` y origen de telemetría.
2. Consultar `--precheck --site S1` del nuevo observador. Si no declara `S05_NOC_PRECHECK=OK_SIN_CAMBIOS` y `S05_NOC_FASE=PRINCIPAL`, **no inducir falla**.
3. Con dos sesiones SSH, en una ejecutar `--watch --site S1 --seconds 90 --interval 0.5` y esperar `S05_NOC_OBSERVADOR_LISTO=S1`; en otra, con `sudo -v`, ejecutar `python3 scripts/laboratorio/s02-failover-wan.py S1 --hold-seconds 20`. La segunda sesión debe permanecer abierta hasta `S02_S1_PRUEBA_COMPLETA=OK`.
4. En el intervalo de observación, Chrome debe mostrar la primaria S1 con interfaz deshabilitada comprobada y la secundaria elegida por FIB en **azul discontinuo**; obtener evidencia únicamente si el estado puede comprobarse. La propia selección del usuario (verde lima) es distinta de la elección FIB (azul). Confirmar en JSONL `RESPALDO` y `PRINCIPAL`, ambos con FIB verificable.
5. Verificar retorno de S1 a `s1p`, conservación de S2 por `s2p`, conectividad y `ens33=192.168.47.40/24`, default por `192.168.47.2`. Solo después planificar S2.
6. Dejar pendiente cierre de **#64, #5 y milestone S05** hasta validar captura de NOC dinámico, además de HA de equipos, OVS/Faucet y LACP integrado. No tocar instantánea VMware manual **`NETLAB360_S05_PreLAN_20261110`**.

**Regla de evidencia:** al pedir capturas indicar desde qué línea/título hasta cuál otra, el nombre sin extensión y si es obligatoria u opcional. Evidencias deben documentar resultados reales, no el mero funcionamiento del código.
