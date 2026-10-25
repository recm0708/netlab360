# NETLAB360 — Auditoría visual y comparación de capturas locales de las fases 1–3

**Fecha:** 25 de octubre de 2026. **Fuente primaria:** ZIP auténtico facilitado en los registros del proyecto, `fase 1-2-3.zip`, procedente de `C:\Users\ruben\Pictures\Screenshots\Proyecto TE2`. **Alcance:** revisión de presencia, nombres, tamaños, huellas de bytes y lectura visual de capturas adicionales. No se alteraron píxeles, resultados ni fechas.

## Inventario contrastado

| Fase | ZIP original | PNG existentes en GitHub antes de la auditoría | Diferencia |
|---|---:|---:|---:|
| Fase 1 | **93** | **86** en `evidencias/capturas/fase1` | **7** |
| Fase 2 | **10** | **0** en `fase2` | **10** |
| Fase 3 | **8** | **0** en `fase3` | **8** |
| **Total** | **111** | **86** | **25** |

ZIP validado sin errores de CRC y 111 archivos PNG decodificables. Las **86 PNG comunes a ZIP/GitHub tienen contenido Git idéntico** (86 blobs; 5.313.907 bytes; comprobación combinada de 160 bits SHA-1 de objetos Git = `8562ca024f6459f069478dacc7e2ae325945e667` en ambos conjuntos). El [PR #50](https://github.com/recm0708/netlab360/pull/50) ya movió esas 86 imágenes sin modificar bytes. **No volver a subirlas ni convertirlas a otro formato**.

## Siete imágenes adicionales de fase 1

| Archivo en ZIP | Dictamen visual | Tratamiento propuesto |
|---|---|---|
| `B2_L3_04_Postcheck_HTTP_WAN.png` | Postcheck anterior del 13/10; existe `B2_L3_04_Postcheck_HTTP_WAN_Final.png` posterior ya versionado | **Histórico, no evidencia principal** |
| `B3_09_Postcheck_Telemetria_Viva.png` | Muestra `PUERTO_9108_LIBRE: NO`; la versión `_Final` versionada muestra puerto libre | **Histórico, no evidencia principal** |
| `IAC_S01_01_Precheck_IPAM_Herramientas.png` | IPAM correcto, pero captura incluye `sudo: Authentication failed, try again` | **Histórico, no evidencia aprobada** |
| `IAC_S01_03_Tofu_Apply_Manifest.png` | Muestra archivo de manifiesto `manifest.json` existente, **no demuestra por sí sola** el éxito de `tofu apply` | **Complementaria**, con log de aplicación |
| `IAC_S01_04_Ansible_Render_Candidato_FRR.png` | Muestra dos archivos FRR generados y sus tamaños | **Complementaria**, debe asociarse al render y resultados |
| `IAC_S01_06_Idempotencia.png` | Muestra solo `RESULTADO_TOFU_SIN_CAMBIOS=0`; no contiene contexto completo | **Complementaria**, con log del segundo plan |
| `LOTE06_Postcheck_Publicacion.png` | Confirma contenedores/namespaces ausentes, `ens33`, GW, servicios activos y Git limpio | **Complementaria útil**, evidencia de postcheck y publicación |

Resultado: **4 capturas de fase1 son candidatas a incorporar como complementarias; 3 deben reservarse como historial técnico y no utilizarse para acreditar una condición corregida**. No es necesario volver a ejecutar los procedimientos iniciales para alcanzar 93 fotografías «principales»: contar archivos no sustituye la valoración de la prueba.

## Diez imágenes de fase 2

Las capturas `S02_01`–`S02_04` muestran preparación, IPAM, tres candidatos FRRouting y precheck administrativo; `S02_06` prueba cuatro adyacencias HQ, dos por sucursal, FIB 6/6 e ICMP 6/6; `S02_07` prueba respaldo y restauración en ambas sucursales; `S02_08` evidencia nueve VLAN/gateways 9/9 y seis comunicaciones; `S02_09` muestra servicios HTTP reales, denegación selectiva, **dos paquetes bloqueados**, y retirada de políticas/servidores.

Hay **dos** imágenes llamadas `S02_05`:
- `S02_05_FRR_Tres_Routers_Aislados.png`: de **17/10** y muestra **solo un contenedor R-HQ**. **No publicarla como prueba de tres routers.**
- `S02_05_FRR_Tres_Routers_Aislados_Validados.png`: del **23/10**, muestra **los tres contenedores** y la red administrativa intacta. **Versión definitiva**.

**Dictamen:** 9 capturas de fase2 aptas para incorporación. La décima es preliminar, no evidencia funcional vigente. Se mantiene la fase2 **pausada intencionalmente**, sin necesidad de desplegarla nuevamente.

## Ocho imágenes de fase 3

| ID | Qué se ve | Alcance |
|---|---|---|
| S03_01 | SoT declara 3 routers, 9 VLAN y 8 extremos de cuatro WAN, más hash del inventario | Fuente de información candidata, no infraestructura viva |
| S03_02 | SoT cotejado con FRRouting realmente observado 3/3, 9/9, 8/8, OSPF 4+2+2, sin aplicar configuración | Correspondencia SoT/estado |
| S03_03 | Ansible 8/8 costos COMPLIANT y dos PLAY RECAP sin cambios y sin fallos | Control de cumplimiento previo |
| S03_04 | Alteración real controlada S1/s1b **100→150**, detector `NON_COMPLIANT` | Detección de drift, antes de reparar |
| S03_05 | Reconciliación **150→100**, siguiente aplicación `changed=0`, cumplimiento 8/8 | Recuperación y idempotencia real |
| S03_06 | OpenTofu plan **17 adds, 0 change, 0 destroy**, guardas metadata-only, SoT 3/4/9 | Plan **previo al apply** |
| S03_07 | Aplicación **17 added, 0 changed, 0 destroyed**, manifiesto 17/17/3/4/9, `SOLO_METADATOS` y validación | Apply real de metadatos, NO redes físicas/lógicas |
| S03_08 | Segundo plan **No changes**, host `ens33` y default gateway intactos | Idempotencia y protección administrativa |

Las ocho son consistentes con registros previos. Nombres descriptivos propuestos para 06–08: `S03_06_OpenTofu_Plan_17_Metadatos.png`, `S03_07_OpenTofu_Apply_Manifest_17_Metadatos.png`, `S03_08_OpenTofu_Segundo_Plan_Sin_Cambios.png`. El renombrado no debe alterar bytes. **S03_09 GitOps** existe como [registro Markdown de PR/Actions auténticos](S03_09_GitOps_CI_Regresion_PullRequest.md), no como PNG y no se exige nueva captura para afirmar checks remotos.

## Publicación definitiva comprobada

La auditoría de 111 fotografías originales permitió seleccionar **21 PNG nuevas** y excluir cuatro históricas o preliminares. El lote definitivo corresponde a **cuatro complementarias de fase 1**, **nueve definitivas de fase 2** y **ocho definitivas de fase 3**.

La transferencia se efectuó desde Windows hacia Ubuntu, se comprobó el contenido contra los 21 SHA-256 previstos, y la incorporación se realizó mediante la [rama y PR #53](https://github.com/recm0708/netlab360/pull/53), fusionado a `main` en el commit `e7f3d3a5ddec191c5144edbeeeb36dcae9abfce7`. La inspección de Git confirmó que **los 21 blobs PNG**, sus tamaños y rutas coinciden con el [manifiesto definitivo](../../evidencias/manifiestos/MANIFIESTO_SHA256_CAPTURAS_2026-10-25.csv), con **996.924 bytes** añadidos. La regresión [Actions run 40241580823](https://github.com/recm0708/netlab360/actions/runs/40241580823) finalizó satisfactoriamente después de la fusión.

**Inventario final en GitHub: 90 PNG fase 1, 9 fase 2 y 8 fase 3; 107 en total**. No se subieron imágenes preliminares ni se reemplazaron las fotografías originales de la fase 1. El registro de GitOps S03_09 continúa como documento Markdown verificable y no se presenta como una imagen.

Las pruebas WAN, FRRouting, Ansible y OpenTofu documentadas no necesitan repetirse para esta tarea. La aceptación académica de las fases se controla por separado, de acuerdo con el informe escrito y el alcance de cada una. Seguimiento documental: [issue #51](https://github.com/recm0708/netlab360/issues/51).
