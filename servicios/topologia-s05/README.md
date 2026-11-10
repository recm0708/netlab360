# NETLAB360 S05 — Topología gráfica multisede

**Estado al 10/11/2026:** v3 del visor probado en VM y Windows (13/13 pruebas offline, JavaScript válido, API y reloj Panamá correctos). Las imágenes compartidas son **preliminares**, no evidencias académicas oficiales. V4 de conexiones ortogonales **preparada en GitHub, pendiente de comprobar en la VM y aprobar visualmente**. La [issue #64](https://github.com/recm0708/netlab360/issues/64) permanece abierta.

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

1. Probar visor/API en VM (sin exporter, la topología sigue visible pero UNKNOWN; cero falsos verdes) y auditar capturas S05.
2. Comprobar el visor con exporter activo y S02 levantada mediante los procedimientos protegidos existentes.
3. Instrumentar verificación de selección OSPF/FIB, conectividad entre extremos y tráfico real; diferenciar respaldo standby de respaldo en uso.
4. Mejorar distribución escalable/zoom, visualización de elementos extendidos, accesibilidad y animación únicamente por contadores confiables.
5. Ampliar el inventario y las vistas conforme se incorporen y validen equipos HA, SDN, sedes y servicios posteriores.

**Protecciones:** nunca modificar `ens33 192.168.47.40/24`, gateway `192.168.47.2`, rutas ni servicios de otras materias. Estado de diseño no equivale a descubrimiento real.
