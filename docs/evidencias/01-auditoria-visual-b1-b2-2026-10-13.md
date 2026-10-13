# NETLAB360 — Registro oficial de evidencias recibidas y auditadas visualmente (lote 01)

**Corte:** 13/10/2026, primera recepción de archivos B1/B2. **Auditoría:** efectuada sobre los **19 PNG efectivamente adjuntados a la conversación**, no sobre imágenes presuntas.  
**Responsables del contenido:** capturas reales de terminal suministradas por el usuario. **Estado:** recepción y cotejo visual documentados; este archivo es el **registro oficial** dentro del repositorio.  
**IMPORTANTE:** los **bytes PNG todavía NO se han incorporado físicamente a GitHub**. Se preparó externamente un ZIP con los 19 originales sin modificación visual, usando nombres normalizados, un manifiesto CSV con hashes completos SHA-256 y una copia de este registro. El usuario deberá importarlo al repositorio para archivo binario duradero. **Nunca inventar enlaces de blobs no subidos**.

## Criterio de validación

- **VALIDADA:** la imagen es legible y muestra un resultado coherente con el hito y su alcance.
- **VALIDADA DIAGNÓSTICA:** registro histórico legible y auténtico de un resultado fallido o comprobación solo de lectura. NO acreditar éxito técnico del intento.
- **RENOMBRADA DIAGNÓSTICA:** se corrigió el nombre canónico para reflejar el resultado fallido.
- **VALIDADA CON OBSERVACIÓN:** datos importantes legibles y consistentes, con encuadre/cabecera incompleta; conservar sin repetir el ensayo.
- **RENOMBRADA CON OBSERVACIÓN:** resultado técnico real válido, corregir nombre; se recomienda reconstruir solo la visualización de evidencia desde el log original si el informe requiere delimitadores completos. No repetir el experimento.

## Inventario oficial y huellas de integridad

| ID | Archivo canónico | Clasificación | Resultado/observación | SHA-256 |
|---|---|---|---|---|
| 01 | `B1_01_Validacion_IPAM_y_Redes.png` | VALIDADA | IPAM 3 sedes/9 VLAN/2 WAN, sin colisiones detectadas, diseño todavía draft | `eb7c0ef189f5170317debdf24a7bc2f92188bed9b00a109d4427fc570f547fa2` |
| 02 | `B1_02_Compatibilidad_Capa2.png` | VALIDADA | Compatibilidad del kernel y diagnóstico L2/L3, host inalterado | `09eb3272328e79b3aaa03d033324f498c5cfe6486ae7be3005141654d491a0f9` |
| 03 | `B2_02_Inspeccion_Imagen_FRR.png` | VALIDADA | Imagen FRR local inspeccionada; no prueba router en marcha | `dd2655388e866c5b0fa752ee587d7553fe67e5d6e09c5d98f67bb2c6a1e711c5` |
| 04 | `B2_03_Arranque_y_Daemons_FRR-1.png` | VALIDADA DIAGNÓSTICA | Preparación/inspección estática FRR, parte 1/2 | `6baaece7f921de4b3826cfe52051a5ccd53ca35038b7208598c677cb5dbc6aed` |
| 05 | `B2_03_Arranque_y_Daemons_FRR-2.png` | VALIDADA DIAGNÓSTICA | Preparación/inspección estática FRR, parte 2/2, lectura sin despliegue | `27a7ecf5e315ec1b2bd3e78341106a7609fdaf3a4b73f3a436f470f96250538a` |
| 06 | `B2_04_Diagnostico_Arranque_FRR.png` | VALIDADA DIAGNÓSTICA | Smoke original: ospfd/vtysh no respondieron a tiempo | `efbd935d05e534d18812fc3aeb2c50096a77ee046156975254051e4fb4e58c0a` |
| 07 | `B2_05_Diagnostico_Estatico_FRR.png` | VALIDADA DIAGNÓSTICA | Verificación estática de permisos/configuración, no arranque real | `bbe3c1a4cb5185f1194f84c66536e9bf83476982804d8188f0916562b71745a1` |
| 08 | `B2_06_Diagnostico_FRR_V2_Permisos.png` | RENOMBRADA DIAGNÓSTICA | Nombre original decía *Exitoso*, pero la captura muestra `RESULTADO_SMOKE_FRR_V2=2` y permiso denegado. Es **diagnóstico de fallo**, no éxito | `307a258202d90932c935bfb4aff32318758acd6d051a33a76e03d0e83a3d1aeb` |
| 09 | `B2_07_Diagnostico_Arranque_FRR.png` | VALIDADA DIAGNÓSTICA | FRR v2 finalizó `exited`; resultado 4 | `05739bb04ba6ebb84e25aaee8946b51c6a341ec0525e1602a44882576cc478a0` |
| 10 | `B2_08_Diagnostico_FRR_V3.png` | VALIDADA DIAGNÓSTICA | V3: montaje legible pero vtysh no disponible; resultado 4 | `e61cafd0b51b69fc7406dd60310723b5dfddd943c09ad8ac5a5ab8dbc0be35b7` |
| 11 | `B2_09_Diagnostico_FRR_V4.png` | VALIDADA DIAGNÓSTICA | V4: problemas de capacidades/permisos; resultado 1 | `b92f8b9def09f75754d5fd51bfbf8f57420ab3018c30dadf8549391d6d8023c7` |
| 12 | `B2_10_Arranque_FRR_V5_Verificado.png` | VALIDADA | FRR v5: zebra y ospfd activos, OSPF local OK, código 0 | `8d67daeb931dd1f36a6a39425358cc1d1e5400e5e530bdee92abc1cc03e0f5b3` |
| 13 | `B2_11_Precheck_Despliegue_DualWAN.png` | VALIDADA | IPAM válido y precheck dual-WAN `RESULTADO_B2_DUALWAN_PRECHECK=0` | `0fdedc766c25be89b403781d737203b0640073ffc9e37c6e3cfee36e32ef370c` |
| 14 | `B2_12_Vecinos_y_Rutas_OSPF_DualWAN.png` | VALIDADA | Dos adyacencias Full, ruta OSPF HQ hacia S1 por WAN-P | `984e11180ea20c3e9a7c797b5df31a96b0c3c374638707d5d176b39b68e4f1b9` |
| 15 | `B2_13_Failover_WAN_Principal_a_Respaldo.png` | VALIDADA | WAN-P DOWN, ruta por WAN-B, código 0 | `df47d84a951c5037db0b729f331b9b27aed9c34be0425f96ef668f64ff26d6a4` |
| 16 | `B2_14_Restauracion_WAN_Principal.png` | VALIDADA | WAN-P UP, ruta restaurada por WAN-P, código 0 | `9dda4bc8784cab82d6e4757534f6515841be1e2eee5ea5edc173aad3baab20d5` |
| 17 | `B2_L2_01_Conectividad_Aislamiento_Recuperacion.png` | VALIDADA CON OBSERVACIÓN | Código 0 y mensaje de aislamiento visibles, pero bajo el encabezado de prueba negativa aparecen **3/3 paquetes recibidos**; esta imagen sola NO demuestra tráfico bloqueado. Cotejar con log L2 original. Encabezado incompleto | `700505d67cc93f8f8dc4f0f409e5f4dff7f84b8e8efaf8d544a4406b9d3b448e` |
| 18 | `B2_15_Conectividad_ICMP_DualWAN_Tres_Estados.png` | VALIDADA CON OBSERVACIÓN | 30/30 ICMP bidireccional en fases normal/respaldo/restaurada, 0% pérdida de esos pings; recorte sin marcador inicial visible | `079e7270c1192cec1765b3f4c20d799e8b6c3b49e7c53615ee9ab157177dac34` |
| 19 | `B2_16_Medicion_Continua_Convergencia.png` | RENOMBRADA CON OBSERVACIÓN | 76/76 sondeos y cleanup correcto; primer sondeo 0.186s/10.147s NO tiempo exacto de convergencia; recorte sin INICIO/hostname visible | `45122d9226527b39a3385b834799891d6a2855ad19a97f32dc7a82d5c8bcecf0` |

**Recuento:** 19 recibidas e inspeccionadas, **8** válidas directas, **7** registros de diagnóstico, **1** diagnóstico renombrado y **3** con observación de encuadre/nombre. Ninguna imagen se descarta por ser diagnóstico: demuestra trazabilidad de las pruebas hasta FRR v5 y la topología exitosa.

### Correspondencia con archivos originales aportados

- Se eliminaron únicamente los sufijos de copia `(1)` en nombres canónicos de B1_01, B1_02, B2_03 partes 1/2 y B2_L2_01.
- `B2_06_Arranque_FRR_V2_Exitoso.png` → `B2_06_Diagnostico_FRR_V2_Permisos.png`.
- `B2_16_Diagnostico_Convergencia.png` → `B2_16_Medicion_Continua_Convergencia.png`.
- No se alteró un solo píxel de las capturas; los hashes SHA-256 anteriores corresponden a los bytes PNG recibidos y empaquetados.

### Uso documental y próximos lotes

La carpeta de capturas B1/B2 constituye **lote 01 auditado**. Registros fallidos B2_04–B2_09 son evidencia interna de diagnóstico, **no imágenes obligatorias de éxito para el informe**. El informe técnico debe priorizar B1_01/02, B2_L2_01, B2_10–B2_16 y los resultados finales de laboratorio. Si las normas exigen encabezado completo, reconstruir B2_L2_01, B2_15 y B2_16 **consultando logs ya existentes**, sin volver a realizar ensayos. La auditoría visual de futuros lotes y la importación física de PNG continúan en [#43](https://github.com/recm0708/netlab360/issues/43).

**Esta auditoría no sube por sí sola capturas binarias a GitHub:** la evidencia está recibida y examinada en la conversación y empaquetada para transferencia. El paso de transferencia/push será verificado por separado. No afirmar que los PNG están ya alojados en el repositorio.
