# S05 — Integridad de P1 y diagnóstico 146A (15/11/2026)

**Estado:** BLOQUEO DE PROCEDENCIA DE DATOS; no equivale a falla de red activa. El usuario ejecutó el lote 146A, que terminó antes del marcador final al detectar 3 JSON con hashes distintos. **No repetir ensayos de carga, no sobrescribir datos y no actualizar el manifiesto para aceptar bytes distintos.**

## Hechos comprobados de 146A

- Git principal sincronizado al commit 9747fea, test contrato NOC HA **4/4 OK**.
- Gestión ens33 192.168.47.40/24, gateway 192.168.47.2; **21 namespaces**; 4 contenedores (FRR HQ/S1/S2 y Faucet); **6 systemd activos**.
- NOC healthz healthy; FIB S1=s1p, S2=s2p; HA BACKEND_HQ/PRINCIPAL running, sin warnings; muestra monitor S2 0,28 segundos; respuestas correctas de los tres endpoints HTTP desde S2; S05_HA_NOC_PRECHECK=OK_PRINCIPAL_HQ.
- SDN inspect: state active, bridge br-s05-sdn, owner correcto, puertos sdna0/b0/c0, tres namespaces, contenedor y gestión intactos.
- P1: log original S05_P1_20261110-110047.log **SHA OK**, pero 01_un_flujo.json, 02_ocho_flujos.json y 03_falla_retorno.json = **DISTINTO** respecto al manifiesto original, y analizador imprimió S05_ANALISIS_ERROR=SHA256_NO_VALIDADO. 146A-14/15 NO se ejecutaron, marcador LOTE146A_PRECHECK_S05=OK no existe.

## Valores discrepantes (no resolver hasta identificar origen)

| Indicador | Bitácora P1 del 10/11 | JSON P1 actuales del 15/11 |
|---|---:|---:|
| 8 flujos RX Mb/s | 959,81 | 959,356 |
| 8 flujos retransmisiones | 0 | 9 |
| Falla/retorno RX Mb/s | 960,31 | 959,613 |
| Falla/retorno retransmisiones | 553 | 745 |
| 8 flujos A1/A2 TX (%) | 62,51/37,49 | 25,01/74,99 |

El script [piloto LACP](../../scripts/laboratorio/s05-lacp-multistream-piloto.sh) escribe directamente los JSON de nombre fijo (redirección >). Una segunda ejecución **podría** sobrescribirlos sin cambiar el TXT/manifiesto original; **es hipótesis, no hecho**. No descartar ni mezclar dos corridas hasta comprobarlas.

## Hashes históricos comprobados en la bitácora del 10/11

| Archivo | SHA-256 esperado |
|---|---|
| S05_P1_20261110-110047.log | dcdeef8ba087d9aace2eb0159cc815306bf3970cc983eb286dd1bc5541bfdbbc |
| 01_un_flujo.json | c35de996410cdff0b9e158975188c9133e77724acbe3364bc8632dbb7a5b5adb |
| 02_ocho_flujos.json | cf078a66abb4e44492fe140fa9d5e8b8598e46ca4b12bd7bd955620059bd949a |
| 03_falla_retorno.json | a14c6b3343d801cb73d81af6a38e4423edafbfaf56026cf139658d2335bf4579 |

La [bitácora del 10/11](../sesiones/2026-11-10-s05-lacp-multistream-piloto-validado.md) indica TAR histórico en ~/netlab360-bootstrap/s05/evidencias/NETLAB360_S05_P1_LACP_EVIDENCIA_TECNICA_20261110.tar.gz. Se desconoce si hoy sigue allí o si tiene exactamente esos hashes.

## Siguiente control no destructivo

1. Ejecutar python3 scripts/validacion/s05-auditar-origen-p1.py --check: lee archivos actuales y miembros regulares de TAR candidatos por nombre base, calcula SHA y **no extrae ni modifica nada**.
2. Si hay TAR con las cuatro coincidencias históricas, copiar/extractar **solo después de validar** hacia un directorio de recuperación nuevo; nunca en la carpeta de JSON actuales.
3. Conservar las dos versiones y su procedencia. Si hay fuentes alternativas legítimas, documentarlas por separado con nombre de corrida y hashes, sin unir resultados de ejecuciones distintas.
4. Rehacer análisis desde el conjunto histórico validado, no desde ficheros afectados por sobrescritura, y completar #31/#105.
5. Después HA de instancia con temporizador independiente y aceptación integral; no apagar Ubuntu antes de preservar/recuperar los namespaces y evidencias.

## Evidencias PNG locales

En Windows el inventario PowerShell encontró **70 archivos S05_*.png**; el comando mostró solo 48–63 por filtro intencional. El original S05_63 tiene 155432 bytes y su SHA-256 **d3506bdb33d28037f8860bd53bd1bf3bc3c6b33ff7083d58c80e5e377b1cccfe** coincide con la captura adjuntada y auditada visualmente. Falta consolidar el CSV local y agregar imágenes originales/manifiesto al repositorio.
