# NETLAB360 S05 — Corte operativo 151, 15/11/2026

**Alcance:** fase S05. Continuación del [corte maestro 147A](CORTE-MAESTRO-NETLAB360-S05-147A-20261115.md). No repetir las instalaciones de NOC, FRR, LACP o Faucet ni fallas WAN/SDN ya acreditadas. No reiniciar Ubuntu ni apagar el invitado con 21 namespaces efímeros.

## Lotes recibidos y aprobados

- **148A–148B:** 4/4 originales P1 del 10/11 extraídos de TAR a directorio independiente y comprobados por SHA; segunda corrida 11/11 identificada mediante log y tres JSON, conservada sin reescritura. P1B 5/5 SHA. Diferencias de caudal y retransmisiones entre sesiones documentadas; sin nuevas pruebas iperf3.
- **150 Windows:** CSV original de 70 PNG localizado y hash validado; 70/70 archivos originales correctos por tamaño y SHA; ZIP 5 049 396 bytes con 70/70 miembros verificados; ZIP y CSV transferidos por SCP a Ubuntu. Marcador LOTE150_WINDOWS_TRANSFERENCIA=OK.
- **151 Ubuntu:** ZIP y CSV recibidos; tests del importador 3/3; cruce real ZIP/CSV 70/70 tamaños, SHA-256 y firma PNG, 5 588 763 bytes descomprimidos; pruebas offline watchdog 2/2. Precheck de seis unidades activas y NOC HA HQ/PRINCIPAL correcto; gestión ens33 192.168.47.40/24 y gateway 192.168.47.2 sin cambios, Git limpio. Marcador LOTE151_PRECHECK_PNG_Y_HA=OK.

## Qué falta ejecutar

1. **Un solo ensayo HA de instancia:** ejecutar script versionado scripts/operacion/s05-lote-ha-instancia-con-watchdog.sh con modo --run --confirm-fault, únicamente desde main limpio y seis unidades activas. El script crea antes timer systemd de rescate 120 segundos que arranca solo backend HQ; observa desde NOC BACKEND_HQ→BACKEND_S1→BACKEND_HQ y registra JSONL. No tocar FRR/FIB, WAN, LACP, Faucet ni ens33. Si SSH se cae, **no repetir ejecución**; comprobar timer/restauración. Timer no cubre pérdida del invitado/host.
2. Capturar evidencia del ciclo con nombre S05_64_HA_Instancia_HQ_Respaldo_S1_y_Retorno, con marcadores de tres fases y regreso HQ, **solo después** de salida positiva; complementar con JSONL.
3. **Solo después del ensayo**, copiar ZIP originales mediante scripts/validacion/s05-importar-png-originales.py --import sobre main limpio. Validar manifiesto SHA del directorio fase5 y revisar que ningún PNG exponga secretos antes de hacer push; confirmar blobs Git. Si --import falla parcialmente, detenerse sin borrar archivos. No repetir transferencia.
4. Acta S05 de aceptación solo lectura y enlaces a evidencia; validar aislamiento SDN, tres LACP 2/2, FIB, NOC/HA, servicios, gestión, registro de P1/P1B, integridad PNG. Cerrar issues #23/#31/#32/#64/#105 cuando corresponda; luego issue #5 y milestone S05. Mantener S06–S08 abiertas.
5. Después de S05, preparar informe único S05 y plan de conservación o reconstrucción de los 21 namespaces antes de apagar Ubuntu.

## Estado de milestones

En lote 147A ya se registró que el operador ejecutó PATCH de las descripciones de las cuatro milestones y comprobó los contadores S05 6/1, S06 3/0, S07 1/0, S08 11/2, todas abiertas. Ningún nuevo cumplimiento técnico de ML/AIOps/TAR/entrega fue atribuido a S06–S08 durante 150/151.

**Precisión de alcance:** 151 es precheck, no prueba HA real; 70 PNG validados en ZIP de Ubuntu no equivale a 70 blobs importados en GitHub ni a revisión visual de su contenido.
