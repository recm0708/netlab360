# NETLAB360 S05 — Topología gráfica multisede

**Estado verificado al 10/11/2026:** diseño V6 aprobado visualmente y **regresión real 18/18 OK**; API, inventario y Git comprobados por el operador. Recibidas y auditadas las capturas **S05_10** (mapa completo), **S05_11** (inspector respaldo HQ–S2) y **S05_12** (UNKNOWN sin exporter, aviso histórico netns por actualizar). El exporter S04 `--once` obtuvo **fuente confiable y topología OFFLINE** con tres routers ausentes, pero el HTTP S04 `127.0.0.1:9110` estaba detenido, por lo que el visor mostró **UNKNOWN por falta de fuente activa**, de forma correcta. Pendientes: importación PNG/manifest y demostración de OSPF/FIB y failover real. [Auditoría de 14 capturas y observación S04](../../docs/sesiones/2026-11-10-s05-auditoria-capturas-y-fuente-s04.md). Mantener abierta la [issue #64](https://github.com/recm0708/netlab360/issues/64).

## V7 — Rutas FIB observadas en tiempo real (código versionado 11/11/2026)

**Estado:** la lectura FIB de HQ y la representación visual están **versionadas en GitHub**, con pruebas offline/CI. **Pendiente ejecutar en la VM original y recibir capturas de navegador/API**, por lo que todavía NO se declara aceptada la demostración visual de failover.

Se consulta únicamente la FIB Linux del namespace del contenedor **`nl360-s02-r-hq`** a través de `sudo -n docker inspect` y `sudo -n nsenter -t PID -n ip -j -4 route get` para `10.79.0.2` y `10.79.0.3`. No se crea ni modifica ruta, interfaz, contenedor, FRR, puente ni equipo. Se compara `Id` de Docker con `~/netlab360-bootstrap/s02/wan-links-state.json` y la etiqueta `netlab360-s02-wan`; el observer rechaza recursos diferentes. La muestra solo se utiliza **si S04 está fresca y confiable** y si la fuente FIB valida ambas sucursales. Si caducan las credenciales `sudo -n`, el state/identidad cambia o el endpoint falla, la selección pasa a `unknown`, no a un verde ficticio.

El grafo conserva `status=admin-up/admin-down/offline/unknown` (ambos extremos desde S04), y añade a las WAN `route_selection=selected/standby/unavailable/unknown`, `route_source` y `route_gateway` cuando realmente se observa la FIB. En `routing` declara explícitamente `traffic_measured=false`.

**Semántica de colores:** principal seleccionada verde; respaldo seleccionado azul; disponible no seleccionada (standby) gris/azul tenue; caída administrativa verificada rojo. Un enlace de respaldo **en uso por FIB no implica tráfico medido**, y la lectura FIB tampoco acredita OSPF FULL sin el comando de OSPF de las pruebas anteriores. El inspector etiqueta `Selección FIB R-HQ` y `Próximo salto FIB`.

### Puesta en servicio segura

1. Mantener exporter S04 ejecutándose `--serve --port 9110 --interval 2`, con lectura Docker autorizada.
2. En la **misma sesión SSH en la que se iniciará el visor**, ejecutar `sudo -v`, y reiniciar `python3 servicios/topologia-s05/app.py --serve --port 9130`. La cache sudo no es permanente: `routing.available=false` si caduca; esto es un resultado seguro, no un error de red.
3. Ejecutar `python3 -m unittest discover -s tests -p 'test_s05_*.py' -v` y extraer el JS del HTML para `node --check`. Se esperan **24 pruebas** si el código nuevo está sincronizado (anterior V6: 18).
4. Validar `/api/v1/graph`: con las 4 WAN y FIB principal, `WAN-PRIMARIA-HQ-S1` y `...S2` deben tener `route_selection=selected`, `WAN-RESPALDO...` `standby`. Si la fuente no está disponible, reportar `unknown` y **no** colorear rutas como elegidas.
5. Capturar evidencia de baseline y de inspección en Windows. Demostración visual bajo failover se realizará **solo después de verificar el baseline**, con una prueba controlada que restaure la interfaz en `finally`.

**Pendiente mayor de la issue #64:** test dinámico de ruta en respaldo durante falla, eventual uso de contadores reales (si se incorpora animación) y evidencias completas. Mantener abierto hasta que estén verificadas.

## V7.1 — Diferenciar visualmente la selección del usuario (11/11/2026)

**Origen de la revisión:** la imagen preliminar del inspector HQ–S1 mostraba FIB correcta (`10.78.0.2 dev s1p`) pero el circuito elegido por el usuario era casi indistinguible de los demás circuitos verdes. Esa captura **no se aprueba como S05_29 definitiva** hasta observar el contraste corregido.

**Cambio exclusivamente visual de `index.html`:** la selección del operador utiliza un **halo violeta de 17 px alrededor del trayecto y de los extremos WAN**, contorno violeta del recuadro pulsado y borde del inspector; el color interno del enlace mantiene el significado de la FIB. Los equipos seleccionados también emplean borde violeta. Un texto explícito explica que la selección **no cambia estado ni rutas**. La leyenda nueva diferencia: **verde** principal seleccionada, **azul discontinuo** respaldo seleccionado, **gris discontinuo** respaldo `standby`, **rojo** admin DOWN comprobado, **gris neutro** offline/unknown y **violeta** elemento seleccionado por clic. `ADMIN UP` no acredita flujo de paquetes. **No** se introducen alarmas o pérdida de rendimiento sin fuente confiable.

**Aceptación pendiente en la VM:** `git pull --ff-only`, 25 tests S05 OK (24 de V7 + 1 de selección V7.1), extracción JS + `node --check`; reiniciar únicamente el visor 9130 tras `sudo -v` en su propia terminal y forzar recarga Chrome con `Ctrl+Mayús+R`. Mantener exporter 9110 y tunel SSH. Seleccionar en vista normal `PRINCIPAL · 10.78.0.0/30` HQ–S1: el trayecto verde debe adquirir **halo violeta** y el inspector mostrar `Selección FIB R-HQ`, `Próximo salto FIB=10.78.0.2` y `Origen ruta=Linux FIB R-HQ` con contorno violeta. **Solo entonces guardar** `S05_29_Inspector_FIB_Ruta_Principal` con ruta y panel completos. La imagen de mapa completo `S05_28` sigue aprobada, sin repetir.

## Inventario representado

Deriva de `inventario/ipam/topologia-s02.yaml`, estado `candidate`. Dibuja **HQ, S1 y S2**, 3 routers FRR, 3 switches de prueba, 9 VLAN, 9 hosts de namespaces aislados y 4 WAN (primaria y respaldo de HQ a cada sucursal). Los equipos que aparecen en diseño no se declaran operativos sin evidencia real. Un host VLAN servicios **no es automáticamente un servidor dedicado**. No hay equipos HA/OVS/Faucet adicionales confirmados todavía.

La API recoge el exporter S04 en `127.0.0.1:9110/api/v1/state` con antigüedad de muestra máxima de 15 segundos, identidad y fuente fiables, y consulta primero `ip netns list` sin privilegios (recurre a `sudo -n` solo si no puede leer) para identificar namespaces. Si la fuente no funciona o el usuario no puede consultar namespaces, el estado correspondiente es **UNKNOWN**, no DOWN falso. Si se observa apagado intencional, queda **OFFLINE**.

Las WAN distinguen trazado primario continuo y respaldo discontinuo. `admin-up` exige ambas puntas con `admin_up=1`, pero **no** demuestra vecindad OSPF Full, ruta activa/FIB, servicio HTTP, tráfico ni utilización de backup. Por ello el visor no anima paquetes ni pinta rutas como seleccionadas solo por flags administrativos.

## Instrucciones de ejecución

Terminal Ubuntu SSH:

```bash
cd ~/proyectos/netlab360
python3 -m unittest discover -s tests -p 'test_s05_topologia.py' -v
python3 servicios/topologia-s05/app.py --check
python3 servicios/topologia-s05/app.py --once
python3 servicios/topologia-s05/app.py --serve --port 9130
```

Otra terminal PowerShell de Windows:

```powershell
ssh -N -L 9130:127.0.0.1:9130 rc-aa-ec@192.168.47.40
```

Abrir **http://127.0.0.1:9130/** en Windows. Todo se sirve en localhost de la VM, sin publicar en VMnet8 ni Internet; los datos viajan por SSH. Actualiza cada 3 segundos, con panel para seleccionar dispositivos y enlaces. Detener con Ctrl+C. No crea ni elimina equipos, modifica interfaces ni lanza FRR/Docker.


## Revisión visual v2 — 10/11/2026

Después de inspeccionar las tres capturas **provisionales** tomadas por el operador, se corrigieron los siguientes defectos del frontend sin alterar la API, inventario ni equipos de red:

- **Bandas separadas:** cada sede tiene encabezado reservado, router, switch y tres hosts sin posiciones coincidentes con los textos. Los nombres de routers y switches van **dentro** de sus símbolos, sin atravesar conexiones LAN.
- **Corredor WAN exclusivo:** cuatro caminos curvos entre el borde inferior de HQ y el borde superior de cada sucursal, con rotulación de principal/respaldo aislada de los nodos. Los cables no pasan por los títulos de sede. Los enlaces se dibujan como rutas lógicas entre routers del IPAM; no representar como interfaces físicas.
- **Dispositivos únicos:** eliminado el renderizado duplicado del router que podía ocultar etiquetas y complicar la selección.
- **Modo presentación:** pulsar `Modo presentación` oculta paneles laterales y resumen, adapta el gráfico al espacio del navegador y facilita una captura general completa. Pulsar de nuevo o `Esc` devuelve la vista de detalle. Fuera de ese modo, el inspector sigue disponible para consultar IP/VLAN/enlaces.
- **Escalabilidad:** los dispositivos adicionales verificados de HQ/S1/S2 se distribuyen bajo el grafo principal, manteniendo su estado `UNKNOWN` hasta tener observación. Las WAN adicionales entre nuevos nodos todavía requieren trazado visual y prueba separados.
- **Regresiones:** además del contrato API, se incluyeron pruebas geométricas offline `tests/test_s05_layout.py` y análisis `node --check` del JavaScript inline mediante CI S05.

La página se lee del archivo `index.html` por cada GET. **Para cambios solo en HTML basta `git pull` y recarga forzada (Ctrl+Mayús+R)**. Para cambios en `app.py` —como la actualización de hora local de la VM en v3— **sí hay que detener con Ctrl+C y reiniciar el servidor Python**. El túnel SSH de Windows puede permanecer abierto.

No convertir las capturas preliminares del defectuoso diseño v1 en evidencias oficiales. Tomar S05_10/S05_11/S05_12 solo después de la verificación de v2.

## Revisión visual v3 — hora Panamá y mejor aprovechamiento del espacio (10/11/2026)

La revisión v2 pasó las **10 pruebas** de API/geometría. La v3 **pasó 13/13 pruebas y `node --check` en Ubuntu**, con reloj VM UTC/Panamá correcto; el operador confirmó el formato en Windows mediante capturas **preliminares**, todavía no oficiales:

- **Hora presentada:** la API entrega `vm_clock.utc` y `vm_clock.panama` correspondientes al *mismo instante del reloj de la VM*. El servidor convierte UTC a `America/Panama` (UTC−5) mediante `zoneinfo`; JavaScript solo da formato legible a ese dato usando `Intl.DateTimeFormat("es-PA")`. El navegador no inventa ni consulta su hora actual. El valor UTC `observed_at_utc` sigue disponible para logs, correlación y monitoreo.
- **Diseño compacto:** reducida la altura base del SVG de 1040 a 920 unidades, sin superponer títulos, routers, switches ni hosts. Se conserva el corredor WAN principal/respaldo, el inspector y el modo presentación.
- **Estado por sede:** chip `RTR: EN EJECUCIÓN / DETENIDO / SIN DATOS`, basado exclusivamente en el estado observado del router FRR; **no** diagnostica por sí mismo el estado de toda la sede.
- **Mejor accesibilidad:** el inspector traduce los estados de `unknown`, `admin-up` y `admin-down` a texto entendible, conservando la distinción entre habilitación administrativa y prueba de disponibilidad.
- **Regresión ampliada:** prueba adicional de reloj UTC/Panamá y verificaciones geométricas de cables/etiquetas. Se validaron **13 tests offline** (7 de grafo y 6 de diseño) en la VM con Git limpio.

**Secuencia operacional v3:** detener `python3 servicios/topologia-s05/app.py --serve --port 9130` con Ctrl+C en la terminal del servidor, sincronizar Git en otra terminal, pasar tests y `--check`, volver a iniciarlo, comprobar JSON `vm_clock` y recargar el navegador Windows. No cerrar el túnel SSH ni modificar `ens33`, Docker, rutas u otros servicios.

## Revisión visual v4 — conexiones WAN ortogonales entre routers (10/11/2026)

La revisión de las capturas de la versión v3 detectó que las curvas WAN parecían salir de la zona de **hosts VLAN** en vez de los routers. El trazado se cambió a conexiones ortogonales (segmentos horizontales/verticales, ángulos de 90°) que **comienzan en el símbolo R-HQ y terminan en los símbolos R-S1/R-S2**, por carriles periféricos. Se comprueba que no cruzan switches, hosts, encabezados ni otros circuitos.

- **Principal:** línea continua, camino externo por el costado de la sucursal.
- **Respaldo:** línea discontinua, camino interior por el espacio entre S1/S2.
- **Etiquetas únicas y legibles:** `HQ ↔ SUCURSAL S1/S2`, tipo de enlace y subred (ej.: `WAN PRINCIPAL · 10.78.0.0/30`). La etiqueta es interactiva y abre el inspector de enlace con ambos extremos.
- **Sin falsos estados:** `unknown` se mantiene como no observado. Ni el color ni el dibujo prueban OSPF Full o uso del respaldo.
- **Fuente de LAN:** la API intenta `ip netns list` sin sudo y conserva el fallback seguro `sudo -n`; así evita avisos innecesarios de permisos en entornos donde la enumeración es pública.
- **Pruebas nuevas:** comprobar puntos de conexión en routers, trayectorias `H/V`, corredor WAN, ausencia de intersecciones y lectura de namespaces sin sudo. Están versionadas, **aún no ejecutadas contra la VM por el operador**.

**Arranque v4:** detener solo el proceso del visor Python (`Ctrl+C`), conservar túnel SSH, sincronizar `main`, ejecutar tests `test_s05_*.py`, comprobar sintaxis JS y `--check`, iniciar `--serve --port 9130` y forzar recarga del navegador (`Ctrl+Mayús+R`). **No tomar capturas oficiales antes de confirmar que la v4 se muestra completa y sin cruces.** No alterar `ens33`, Docker ni los namespaces de otras fases.

## V5 — Diagrama apaisado y dos módulos WAN (10/11/2026)

La ejecución **V4** completó **16/16 pruebas**, `node --check`, `--check`, consulta de los cuatro WAN desde IPAM y lectura `netns` sin credenciales (`NAMESPACES_OBSERVABLES=True`). Las capturas provisionales del operador mostraron una limitación visual no detectada por los tests de V4: cables perimetrales, etiquetas cercanas y nota inferior sobre los enlaces de respaldo. Aunque técnicamente válido, **V4 no se acepta como captura final**.

Se diseñó **V5** sobre una previsualización SVG local y se sustituyó el esquema superior/inferior por una disposición horizontal:

- **Sede central HQ:** columna izquierda, con router, switch y VLAN/hosts claramente diferenciados.
- **Dos sucursales S1/S2:** tarjetas independientes a la derecha, S1 arriba y S2 abajo.
- **Dos módulos WAN centrales:** un módulo por sucursal, cada uno con **PRINCIPAL · subred /30** y **RESPALDO · subred /30** en pistas diferentes. La línea continua y la discontinua siguen representando los dos circuitos de IPAM, sin duplicarlos.
- **Conexiones lógicas entre routers:** las cuatro rutas terminan en los símbolos `R-HQ`, `R-S1` y `R-S2` y pasan por sus respectivas pistas WAN. Los módulos son agrupadores visuales, **no switches, routers adicionales ni dispositivos desplegados**.
- **Sin texto inferior cruzado:** se eliminó la anotación central `PRINCIPAL: CONTINUA · RESPALDO: DISCONTINUA` que se superponía con la ruta; la leyenda del panel derecho continúa vigente.
- **Inspector simplificado:** seleccionando cada circuito se visualiza un nombre legible, subred, extremos, función y estado observado. La selección se resalta en cian, mientras que estado administrativo y respaldo mantienen sus significados.
- **Regresión geométrica V5:** conserva validaciones de títulos y dispositivos y añade pruebas de separación de etiquetas en cada módulo, cuatro extremos sobre routers y ausencia de intersecciones entre circuitos. **Pendiente de ejecutar en Ubuntu; se esperan 17 pruebas** (8 de geometría + 9 del backend).

La V5 cambia solo frontend y pruebas; **si el backend V4 continúa abierto, basta `git pull --ff-only` con árbol limpio y recarga forzada del navegador**. Si el servidor se ha detenido, iniciarlo como siempre en localhost 9130. Conserva la hora Panamá calculada del reloj de la VM, `UNKNOWN` si S04 está detenido, lectura de namespaces solo lectura y protección de `ens33`.

Las próximas ampliaciones deben mostrar enlaces y equipos reales en la misma estructura, pero no marcar primaria elegida, failover exitoso o dispositivos activos sin telemetría verificable.

## V6 — Ajuste de simetría y llegada al router S2 (10/11/2026)

La revisión visual de **V5 en Windows** confirmó que el nuevo diseño apaisado resulta más legible: HQ a la izquierda, S1 arriba a la derecha, S2 abajo, y módulos de enlaces separados. El operador detectó un detalle en la **WAN de respaldo HQ–S2** y propuso, como alternativa, invertir la disposición de S2. Se decidió **conservar la estructura uniforme en ambas sucursales** (título → router → switch → tres VLAN) y corregir únicamente la geometría para no crear una segunda convención visual.

- Se desplazó `R-HQ` a una posición cercana al punto medio vertical entre `R-S1` y `R-S2`, y el switch y los hosts de HQ en correspondencia.
- Los cuatro puntos de salida de WAN desde HQ se distribuyen en orden por el costado derecho del router; principal y respaldo siguen representando enlaces distintos, sin implicar tráfico real.
- El módulo visual `HQ ↔ SUCURSAL S2` subió 30 unidades de SVG; el enlace principal utiliza el carril 577 y el respaldo el 644, manteniendo suficiente separación vertical entre ambos.
- El respaldo HQ–S2 finaliza en `R-S2` mediante un codo corto de 25 unidades verticales, en lugar de un trazado que pareciera perseguir al circuito principal. Los caminos siguen siendo independientes y terminan en los routers.
- Se añadió una prueba `test_v6_hq_balanced_and_s2_backup_entry` para conservar simetría, separación, orden de VLAN y proximidad del último codo. En total se esperan **18 pruebas S05 (9 API y 9 geometría)**.
- No cambian la API, telemetría, hora Panamá, IPAM, Docker, namespaces ni ningún dispositivo de la VM. El servidor en ejecución puede seguir abierto; basta sincronizar Git y refrescar Chrome.

**Estado:** V6 versionada, **pendiente** de ejecutar las 18 pruebas y comprobar las dos vistas en Windows. Las capturas de V5/V6 permanecen provisionales hasta una aprobación visual explícita.

## Aceptación visual V6 y evidencias definitivas — 10/11/2026

Se recibieron **dos capturas provisionales de Chrome** con la V6. El operador indicó que la distribución visual ya era satisfactoria. La revisión muestra dos módulos WAN S1/S2 con etiquetas principal/respaldo, extremos en R-HQ/R-S1/R-S2, VLAN agrupadas y hora Panamá. Se declara **aprobación visual del diseño V6**, no cierre funcional de S05. Ambas capturas están parcialmente desplazadas; no acreditan un pantallazo completo del modo presentación ni el inspector del respaldo S2 seleccionado.

Capturas oficiales a tomar cuando la V6 esté abierta:
- `S05_10_Topologia_General_Tres_Sedes`: **obligatoria**, modo presentación mostrando HQ, S1, S2 y las cuatro WAN en una sola imagen, sin recortes de elementos.
- `S05_11_Topologia_Inspector_Enlace_WAN`: **obligatoria**, vista normal, hacer clic en el circuito `WAN-RESPALDO-HQ-S2` (`10.78.0.12/30`), mostrar rol, extremos y estado en inspector, con diagrama legible.
- `S05_12_Topologia_Estado_Sin_Telemetria`: complementaria, encabezado de estado `UNKNOWN`, fuente S04 no disponible y hora Panamá. No etiquetar `UNKNOWN` como fallo de equipos.

Verificar el código V6 con `python3 -m unittest discover -s tests -p 'test_s05_*.py' -v` (se esperan 18 pruebas), `node --check` al JavaScript extraído, `git status` limpio y API `/healthz`/`/api/v1/graph`. **La transcripción disponible aún no contiene los resultados V6**, por lo que su regresión local sigue pendiente de registro.

**Siguiente paso operacional seguro:** ejecutar auditoría de solo lectura del exporter S04 (`--check`, `--once`, endpoint 9110), SoT y estado Docker; no levantar topología/FRR ni modificar rutas hasta interpretar evidencias. Un `UNKNOWN` confiable es distinto de un equipo demostrado caído.

## Revisión de evidencias y auditoría S04 — resultado vigente

- **Vista V6 y pruebas:** 18/18 tests, `S05_V6_ACEPTACION_TECNICA=OK`, `--check` del visor OK, JSON válido, Git limpio. Dos capturas finales, `S05_10` y `S05_11`, examinadas y aceptadas en contenido; `S05_12` es opcional e histórica (su alerta de namespaces pertenece a la sesión anterior).
- **Fuente S04 offline, no caída comprobada:** `s04_exporter_multisede.py --check` OK; `--once` devolvió `source_ok=true`, `topology=offline`, routers R-HQ/R-S1/R-S2 detenidos o no existentes. Sin contenedores Docker ni namespaces; no se afirma un despliegue multisede activo.
- **Por qué el NOC indica UNKNOWN:** `127.0.0.1:9110/healthz` no respondía porque el servidor S04 no estaba iniciado; `127.0.0.1:9130/healthz` sí estaba saludable. La API del visor no usa datos `--once` almacenados y exige fuente HTTP fresca; es correcto que indique `UNKNOWN` hasta levantar el servicio observador.
- **Seguridad operacional:** iniciar S04 exporter en modo `--serve` **solo lectura** cuando se quiera demostrar `offline` observado, con autorización sudo temporal en la misma sesión SSH para `sudo -n docker inspect`. No levantar routers/FRR ni tocar `ens33`.
- **Archivo académico:** [informe de auditoría de 14 PNG](../../docs/sesiones/2026-11-10-s05-auditoria-capturas-y-fuente-s04.md). Los archivos binarios PNG todavía no se han subido al repositorio; incorporar en lote con SHA-256 antes de cerrar issue.

## Primer estado observado en vivo — S04 HTTP → V6 (10/11/2026)

La primera integración en vivo del exporter S04 fue ejecutada por el operador y comprobada por **dos consultas de API**, no por simulación en frontend:

- En una terminal separada se levantó temporalmente el exporter S04 con `--serve --port 9110 --interval 2`, `S04_MODO=SOLO_LECTURA` y credenciales sudo de la sesión.
- El endpoint `http://127.0.0.1:9110/api/v1/state` devolvió `source_ok=true`, `topology=offline`.
- El visor en `http://127.0.0.1:9130/api/v1/graph` consumió la observación y devolvió `telemetry.available=true`, `telemetry.topology=offline` y los tres routers R-HQ/R-S1/R-S2 `offline`.
- El usuario adjuntó `S05_13_Topologia_Offline_Observado`, **captura 15** recibida, válida para acreditar visualmente el cambio de estado a `Topología OFFLINE` y aviso `Fuente S04 actualizada`.
- `S05_S04_INTEGRACION_OFFLINE=OK` quedó guardado localmente en `~/netlab360-bootstrap/s05/evidencias/observabilidad/02_Integracion_Exporter_S04_V6.txt`.

**Alcance:** evidencia correcta de la transición `UNKNOWN→OFFLINE` por fuente disponible con routers ausentes. No acredita una falla inducida, red desplegada, conectividad OSPF/FIB o tráfico real por enlaces. La fuente depende del proceso y permisos temporales de observación. Mantener `UNKNOWN` cuando falte muestra fresca.

El [informe de auditoría y su anexo](../../docs/sesiones/2026-11-10-s05-auditoria-capturas-y-fuente-s04.md) incluye la transcripción esencial y la revisión de 15 PNG. **Pendiente** copia de originales con hashes al repositorio, precheck operativo S02 y validación de router/enlaces activos.

## Actualización por fases

El inventario S02 fija el núcleo. En `inventario/topologia-extensiones-s05.json` pueden añadirse **solo equipos que se hayan desplegado y verificado**; exige `schema_version=1` y listas `nodes` y `links`. Un elemento nuevo requiere ID único, sede, tipo, evidencia y `realized=true` para registrarse en el modelo; el estado se marca UNKNOWN hasta que se instrumente telemetría específica.

Ejemplo documental, **NO desplegado** y no incluido en el inventario vigente:

```json
{"id":"SRV-HA-HQ-01","site":"HQ","type":"server",
 "label":"Servidor alterno","detail":"Servicio futuro",
 "realized":false,"evidence":"Issue con prueba real pendiente"}
```

La primera versión tiene **layout principal fijo de HQ/S1/S2** y un sector adicional automático para representar con fichas seleccionables los nodos verificados nuevos de cualquiera de esas tres sedes. Para **nuevas sedes**, conexiones extra con trayectorias gráficas y gran escala de equipos será necesario ampliar IPAM, layout del frontend, pruebas y colectores de estado. El catálogo JSON puede añadir enlaces al modelo/API, pero la geometría de conexiones adicionales todavía requiere desarrollo; no se presenta como implementada.

## Pendientes de aceptación

1. **Completado**: visor/API probado en VM y Windows, 18/18 regresiones y capturas S05_10/S05_11 auditadas; fuente desconectada correctamente UNKNOWN.
2. Comprobar el visor con exporter activo y S02 levantada mediante los procedimientos protegidos existentes.
3. Instrumentar verificación de selección OSPF/FIB, conectividad entre extremos y tráfico real; diferenciar respaldo standby de respaldo en uso.
4. Mejorar distribución escalable/zoom, visualización de elementos extendidos, accesibilidad y animación únicamente por contadores confiables.
5. Ampliar el inventario y las vistas conforme se incorporen y validen equipos HA, SDN, sedes y servicios posteriores.

**Protecciones:** nunca modificar `ens33 192.168.47.40/24`, gateway `192.168.47.2`, rutas ni servicios de otras materias. Estado de diseño no equivale a descubrimiento real.
