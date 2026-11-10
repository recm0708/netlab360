# NETLAB360 S05/P1 — LACP multistream piloto, medición real y retorno

**Ejecución:** 10/11/2026, Panamá UTC−05. **Ubicación del ensayo:** `netlab360-lab`, Ubuntu 26.04.1, kernel `7.0.0-43-generic`. **Estado:** prueba piloto realizada y validada contra transcripción operativa del usuario. No se ha demostrado aún la capacidad máxima ni la integración multisede.

## Topología y método

- Script: [`scripts/laboratorio/s05-lacp-multistream-piloto.sh`](../../scripts/laboratorio/s05-lacp-multistream-piloto.sh); `--precheck` aprobó identidad, Git, IP/GW y namespaces inexistentes.
- Exclusivamente namespaces `nl360-s05-la` y `nl360-s05-lb`; bond `bond0` IEEE 802.3ad activo en ambos extremos, `xmit_hash_policy=layer3+4`, dos pares `veth` (`s5a1↔s5b1`, `s5a2↔s5b2`), red aislada `198.18.251.0/30`. `ens33` y VMnet8 no forman parte del tráfico de laboratorio.
- `iperf3` TCP a `198.18.251.2:5215`, límite **120 Mb/s por flujo**, `-P 1` durante 8 s y `-P 8` durante 10 s. Prueba de falla con `-P 8`, 18 s, 1 s entre muestras, apagar `s5a1` y restaurarlo durante transferencia.
- Estos límites de tráfico son valores de ensayo, **no** una cifra de capacidad máxima de veth, NIC VMware o red física.

## Resultados observados

| Escenario | Caudal recibido | Flujos | Retransmisiones TCP | Contadores de miembros TX |
|---|---:|---:|---:|---|
| Uno solo, LACP 2/2 | **120,06 Mb/s** | 1 | 0 | A1: 135 340 399 B; A2: 2 685 B |
| Ocho concurrentes, LACP 2/2 | **959,81 Mb/s** | 8 | 0 | A1: 826 611 947 B; A2: 495 812 915 B |
| Ocho concurrentes, falla 2→1→2 | **960,31 Mb/s** (promedio) | 8 | **553** | No se capturaron deltas de miembro por subintervalo |

Distribución por bytes TX del ensayo de 8 flujos: **62,51 % A1 / 37,49 % A2** (aproximada). En un flujo casi todos los bytes se observaron en A1. El hash de flujos distribuyó tráfico por ambos enlaces, pero **no** por mitades exactas.

Falla controlada: `S05_FALLA_A1=2026-11-10T11:01:16-05:00`, `S05_RETORNO_A1=2026-11-10T11:01:21-05:00`. Se observó un agregador activo de **2→1→2** puertos en **ambos** extremos. `iperf3` completó el ensayo y se observaron **553 retransmisiones**, de modo que la afirmación «cero pérdidas» o «failover sin perturbación» sería incorrecta. Muestras de 1 segundo incluyen **783,09 Mb/s** (12–13 s aproximadamente; 143 retransmisiones) y **1138,12 Mb/s** (13–14 s; 408 retransmisiones); hubo 2 retransmisiones adicionales en 17–18 s. La falla y el retorno registrados corresponden aproximadamente a los segundos 5 y 10 desde el inicio de iperf3. **551 de las 553 retransmisiones aparecen después de la restauración registrada**, por lo que los contadores no justifican atribuir pérdidas al instante exacto de la caída. La correlación de reloj es aproximada y las métricas de intervalos deben interpretarse con prudencia. El caudal medio cercano al límite ofrecido no demuestra ausencia de interrupción breve.

## Postcheck y trazabilidad

- `S05_LACP_ESTADOS_2_1_2=OK`; `S05_RESULTADO_P1=0`; `S05_LIMPIEZA=OK`, namespaces de S05 retirados.
- `S05_RED_GESTION_INTACTA=SI`; `ens33=192.168.47.40/24`, `default via 192.168.47.2 dev ens33`; Git `main...origin/main` limpio.
- Tres archivos JSON `iperf3` pasaron `python3 -m json.tool`; manifiesto SHA-256 generado para los tres JSON y el log de ejecución, y **validado posteriormente (4/4 OK)**. Se creó un segundo manifiesto portátil, con cinco archivos verificados, incluyendo el análisis de JSON.
- El operador **confirmó cuatro capturas tomadas**: `S05_01_LACP_Flujo_Unico`, `S05_02_LACP_Ocho_Flujos_Distribucion`, `S05_03_LACP_Falla_y_Restauracion`, `S05_04_LACP_Limpieza_y_Postcheck`. **Sus archivos PNG no se han recibido ni auditado visualmente**, y aún no están versionados aquí.
- Evidencia primaria local: `~/netlab360-bootstrap/s05/evidencias/lacp-p1/S05_P1_20261110-110047.log`, `01_un_flujo.json`, `02_ocho_flujos.json`, `03_falla_retorno.json`, `MANIFIESTO_SHA256_S05_P1_2026-11-10.txt`.

SHA-256 reportados por el operador y **comprobados posteriormente en la VM** con `sha256sum -c` (4/4 OK):

```text
dcdeef8ba087d9aace2eb0159cc815306bf3970cc983eb286dd1bc5541bfdbbc  S05_P1_20261110-110047.log
c35de996410cdff0b9e158975188c9133e77724acbe3364bc8632dbb7a5b5adb  01_un_flujo.json
cf078a66abb4e44492fe140fa9d5e8b8598e46ca4b12bd7bd955620059bd949a  02_ocho_flujos.json
a14c6b3343d801cb73d81af6a38e4423edafbfaf56026cf139658d2335bf4579  03_falla_retorno.json
```

## Interpretación técnica / próximos controles

**Demostrado:** conectividad local bajo LACP negociado, distribución de múltiples flujos por hash, continuidad de sesión suficiente para completar transferencia de 18 s, detección 2→1→2 y limpieza sin alterar gestión.

**Aún no demostrado:** capacidad máxima sin limitador, continuidad perfecta sin retransmisión, escenario multisede final con equipos de respaldo, conmutación real de switch/router o NIC física, correlación de eventos al milisegundo, aceptación de toda la fase S05. Estos alcances continúan pendientes en [#31](https://github.com/recm0708/netlab360/issues/31), [#32](https://github.com/recm0708/netlab360/issues/32) y [#5](https://github.com/recm0708/netlab360/issues/5).

## Ampliación analítica verificada (10/11/2026)

- Analizador [`s05-analizar-lacp-p1.py`](../../scripts/validacion/s05-analizar-lacp-p1.py) ejecutado: `S05_P1_ANALISIS=OK_CON_LIMITACIONES`, `S05_SHA256_INTEGRIDAD=OK`. CPU local/remota reportada por iperf3: **2,48 % / 1,25 %** para un flujo; **13,31 % / 5,82 %** para ocho; **12,26 % / 5,63 %** para falla/retorno. Estos son datos propios de iperf3, **no** una métrica integral de CPU de la VM.
- Se verificó `sha256sum -c` para el manifiesto original (**4/4 OK**), se produjo `MANIFIESTO_PORTATIL_S05_P1.sha256` y se comprobó (**5/5 OK**). Se creó `~/netlab360-bootstrap/s05/evidencias/NETLAB360_S05_P1_LACP_EVIDENCIA_TECNICA_20261110.tar.gz` que contiene log, tres JSON, análisis y manifiesto portátil, sin publicar aún el TAR binario.
- Precheck P1B de recursos: **8 vCPU, 13 GiB RAM disponible, presión CPU avg10/60/300 = 0,00, 132 GiB de disco, 0 namespaces residuales, 0 contenedores, 0 servicios fallidos**, red de gestión intacta. Estos datos permiten planificar un ensayo acotado de caudal sin tope de `iperf3`, **no garantizan que sea segura cualquier carga ilimitada**.

**Próximo paso:** comparar 1 y 8 flujos TCP sin límite de caudal de aplicación, en un solo miembro y en ambos miembros, con afinidad de CPU limitada para los procesos, duración y timeout controlados. El resultado será rendimiento efectivo del entorno virtual bajo esas condiciones, **no velocidad de NIC física ni capacidad teórica máxima**. No repetir S01 por rutina.
