# Transferencias de rendimiento por tiempo y volumen

El ejecutor manual de transferencias usa el catálogo de identidades y rutas de diagnóstico. Admite las rutas HQ_A_S1 y HQ_A_S2, con un flujo y un receptor temporal iPerf3. No habilita solicitudes desde FastAPI ni modifica sudoers.

## Perfiles iniciales

| Perfil | Protocolo | Objetivo | Tasa objetivo | Timeout cliente/receptor |
| --- | --- | --- | --- | --- |
| tcp-10s | TCP | 10 s | 20 Mbit/s | 20/25 s |
| udp-10s | UDP | 10 s | 20 Mbit/s | 20/25 s |
| tcp-100mb | TCP | 100 000 000 bytes | 20 Mbit/s | 60/70 s |

La tasa es un objetivo de pacing, no un policer estricto. El perfil por bytes permite comprobar el volumen recibido; no acredita identidad del contenido de un archivo. Los perfiles de mayor volumen, la verificación de contenido, el seguimiento en vivo y los escenarios de conmutación requieren validaciones posteriores.

## Operación local

Desde servicios/consola-s08, como operador no root con autorización sudo existente:

```bash
python -B -m api.transfer_executor --profile tcp-100mb --route HQ_A_S1
```

Antes de emitir tráfico verificamos las identidades y rutas, disponibilidad de puerto 5201 y exclusión por operador. El receptor se enlaza a la dirección del endpoint, atiende una conexión y tiene timeout independiente. Esperamos su terminación y comprobamos la liberación de puertos. No instalamos servicios permanentes ni ejecutamos Python del repositorio como root.

## Interpretación de resultados

Conservamos métricas de emisor y receptor, intervalos, bytes, duración, tasa efectiva y retransmisiones TCP o pérdida y jitter UDP. Un resultado parcial o incompleto no equivale a un error del transporte. Los intervalos se obtienen de los JSON finales, no de telemetría en tiempo real. No se deduce pérdida TCP de una diferencia de bytes ni se afirma certificación de fibra física.

La futura frontera privilegiada deberá imponer autorización, exclusión global, cancelación y limpieza; los escenarios de fallos requieren un watchdog y restauración independiente.
