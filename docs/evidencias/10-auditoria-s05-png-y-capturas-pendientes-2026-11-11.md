# NETLAB360 · Auditoría de evidencias S05 y plan de capturas finales

## ACTUALIZACIÓN VIGENTE — 11/11/2026: PNG S05_29–31 RECIBIDOS Y REVISADOS

**Este apartado sustituye los renglones históricos «pendiente» más abajo; consérvense para trazabilidad de la auditoría original.**

- [x] **S05_29_Inspector_FIB_Ruta_Principal.png:** PNG válido. Mapa y WAN HQ–S1 resaltada por selección de usuario en verde lima; inspector confirma FIB elegida con next-hop `10.78.0.2`, origen `Linux FIB R-HQ`.
- [x] **S05_30_Codigo_Colores_y_Estados.png:** PNG válido, tarjeta `Código de colores y estados` completa; distingue verde lima (selección), verde (ruta FIB), azul (respaldo seleccionado), gris (espera), rojo (interfaz deshabilitada). Advertencia semántica: FIB no equivale a medición de tráfico.
- [x] **S05_31_NOC_Conmutacion_S1_Respaldo_Seleccionado.png:** PNG visualmente válido como escenario dinámico: WAN principal HQ–S1 roja, WAN respaldo HQ–S1 azul discontinuo seleccionado, S2 sigue verde. **Salvedad:** no incluye inspector ni texto del next-hop `10.78.0.6`; **se acredita con el registro observador JSONL y la salida del simulador**. No repetir corte solo para mejorar encuadre.
- [x] **Ejecución verificada:** lote 75 **36/36 tests**, lote 76 **119 muestras**, `S05_NOC_CICLO_COMPLETO=OK`, `s1p→s1b→s1p` next-hops `10.78.0.2→10.78.0.6→10.78.0.2`; lote 77 `S02_S1_PRUEBA_COMPLETA=OK`, ventana 25s; lote 78 `S05_FIB_RESTAURADA=OK`, S2 `s2p` y gestión `ens33` intactos.
- [ ] **Pendiente antes de archivar evidencia:** verificar archivo real `S05_NOC_S1_OBSERVACION_20261111T052859Z.jsonl`, logs `10_Observador_Failover_S1.txt`, `11_Failover_Observado_S1.txt`, `12_Postcheck_Failover_Observado.txt` mediante script Python y generar SHA-256; importar los PNG originales al repositorio si la etapa de consolidación lo requiere. Los PNG están recibidos en chat, no commiteados.
- [ ] **Fases técnicas adicionales:** diseño HA [#32](https://github.com/recm0708/netlab360/issues/32), OVS/Faucet [#23](https://github.com/recm0708/netlab360/issues/23), integración de LACP [#31](https://github.com/recm0708/netlab360/issues/31).

Bitácora nueva: [observación y retorno S1 validados](../sesiones/2026-11-11-s05-observacion-failover-s1-validada.md).

**Corte:** 11/11/2026, zona horaria América/Panamá. **Alcance:** cuatro PNG recibidos en la conversación del operador (dos de 00:12, uno de 23:01 y el archivo S05_28 duplicado con sufijo `(1)`), la evidencia previamente verificada en chat y el registro anterior `docs/sesiones/2026-11-10-s05-auditoria-capturas-y-fuente-s04.md`.

## PNG aportados en la revisión actual

| Archivo remitido | Contenido comprobado visualmente | Dictamen / identificador |
| --- | --- | --- |
| `S05_28_NOC_Rutas_FIB_Principales(1).png` | Mapa íntegro HQ/S1/S2; dos WAN principales en verde, los respaldos en gris discontinuo, routers activos y VLAN en las tres sedes; versión anterior del rótulo `RTR: EN EJECUCIÓN` y `SWITCH` | **Técnicamente válido** como `S05_28_NOC_Rutas_FIB_Principales`. Retirar sufijo `(1)`; no repetir por conveniencia estética salvo que se quiera homogeneizar todo |
| `Captura de pantalla 2026-11-10 230134(1).png` | WAN principal HQ–S1 seleccionada en verde lima, inspector con estado FIB elegido y salto `10.78.0.2`, origen `Linux FIB R-HQ` | **Contenido de S05_29 técnicamente válido**, pero no incluye el título `Mapa corporativo` y utiliza versión previa del texto de badges; preferir captura definitiva del diseño nuevo |
| `Captura de pantalla 2026-11-11 001219.png` | Cabecera NOC `Topología ACTIVA`, cinco tarjetas de inventario, hora VM Panamá, supervisión operativa y título de la leyenda | **Captura general complementaria**, no sustituye S05_29 ni S05_30 |
| `Captura de pantalla 2026-11-11 001234.png` | Mapa completo y parte inferior de leyenda `Código de colores y estados` junto con integraciones; verifica paleta visual | **Evidencia complementaria**; parte superior de la leyenda queda fuera de cuadro. Repetir para S05_30 incluyendo título y lista completa de colores en una sola toma |

No se ha demostrado que estos PNG estén importados en el repositorio ni calculado sus hashes SHA-256. La rama `main` tiene carpeta `evidencias/capturas/fase5/.gitkeep` pero no contiene estas capturas. Conservar originales para futura importación y manifiesto. La validación visual en chat no implica integridad binaria ni aceptación académica final.

## Estado de capturas por tramo

- **S05_01–S05_13:** existe auditoría anterior que registra como aceptadas las capturas de LACP P1, P1B y topología V6; `S05_12` tenía reserva histórica porque la leyenda de fuente desconocida correspondía a otra ejecución, y no debe reutilizarse como prueba del NOC actual.
- **S05_14 y S05_15, S05_17–S05_19:** reportadas recibidas y auditadas en issue #64 (FRR aislado, plan WAN, FULL OSPF y FIB). Los números no citados aquí no implican que exista una captura obligatoria ausente.
- **S05_21A, S05_21B, S05_22 y S05_23:** usuario entregó capturas de VLAN/hosts/namespaces y 9 gateways, 3 intersede; validación previa positiva, no rehacer.
- **S05_24, S05_25, S05_26, S05_27:** capturas de failover S1/S2, postcheck y API FIB entregadas en el chat y revisadas antes de esta auditoría; no volver a ejecutar pruebas únicamente por repetición visual.
- **S05_28:** PNG recibido ahora y **validado**. Nombre estable sin sufijo: `S05_28_NOC_Rutas_FIB_Principales`.
- **S05_29:** **pendiente de imagen oficial definitiva**. Seleccionar principal HQ–S1 y encuadrar desde el título `Mapa corporativo · Sede central y sucursales` hasta el campo `Origen ruta: Linux FIB R-HQ` del inspector, mostrando `10.78.0.2`. Nombre `S05_29_Inspector_FIB_Ruta_Principal`. La captura antigua muestra la información, pero no el encabezado requerido.
- **S05_30:** **pendiente de imagen oficial definitiva**. Encuadrar la tarjeta completa desde `Código de colores y estados` hasta la última línea de la explicación de la semántica, en una sola imagen. Nombre `S05_30_Codigo_Colores_y_Estados`.
- **S05_31:** **no se ha podido tomar** porque el failover observado S1 todavía no se ha ejecutado en NOC. Durante respaldo HQ–S1 realmente elegido por FIB, capturar desde `Mapa corporativo · Sede central y sucursales` hasta `Origen ruta` del inspector, señalando respaldo azul, interfaz `s1b` y salto `10.78.0.6`. Nombre `S05_31_NOC_Conmutacion_S1_Respaldo_Seleccionado`. Si la observación no alcanza este estado, no capturar como prueba de failover.

**Nota:** captura 24–28 validadas técnicamente. El único cambio sugerido en la imagen #28 es quitar `(1)`. No completar artificialmente identificadores secuenciales no exigidos.

## Recuperación NOC verificada antes del corte siguiente

- **Terminal 1** NOC reiniciado en puerto 9130 (nuevo PID `449431`) tras `sudo -v` en su propia TTY. **Terminal 4** exporter S04 puerto 9110 con PID `425166`. **Terminal 2** túnel SSH PowerShell activo y **Terminal 6** confirmó `/healthz healthy=True`, FIB real S1 `s1p/10.78.0.2` y S2 `s2p/10.78.0.10`.
- **Terminal 3 / Lote 72R-E**: dos muestras independientes separadas cuatro segundos, S04 `source_ok=True`, `topology=active`, `errors=[]`; NOC `telemetry.available=True`, `routing.available=True`, `source_warnings=[]`, rutas correctas. `S05_S04_Y_NOC_ESTABLES=OK`, `S05_NOC_PRECHECK=OK_SIN_CAMBIOS`, `LOTE72R_FUENTES_RECUPERADAS=OK`. Administración `ens33=192.168.47.40/24` y default `.2` sin cambio.
- **Terminal 2 / Lote 72R-F:** túnel local validado en Windows mediante PowerShell. **No se ha ejecutado la prueba de conmutación S1 en el NOC** después de esta recuperación.
- Continuar con mapa fijo T1=NOC 9130, T2=túnel Windows, T3=auditoría, T4=exporter S04 9110, T5=observador temporal, T6=simulador temporal Ubuntu SSH cuando corresponda. No duplicar procesos HTTP ni operar snapshot VMware `NETLAB360_S05_PreLAN_20261110`.

## Cambio visual puntual solicitado

Reducir el badge de cada sede de `RTR: EN EJECUCIÓN` a `ACTIVO` (verde), de `RTR: DETENIDO` a `INACTIVO` (rojo **solo con observación confiable**), y de `RTR: SIN DATOS` a `SIN DATOS` (gris). Reducir ancho y dejar espacio visual al encabezado. Cambio puro HTML/JS/CSS, sin tocar LAN/WAN/FIB.

El único experimento pendiente inmediato es **S1 principal → respaldo → principal observado desde API/visor**. El código de monitor `s05-observar-conmutacion-noc.py` y `s02-failover-wan.py --hold-seconds 25` ya existe y se había probado unitariamente (36/36). Revalidar ambas fuentes inmediatamente antes de la prueba; no dar por realizada hasta recibir JSONL/log/PNG genuinos. 
