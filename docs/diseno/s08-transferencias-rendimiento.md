# Transferencias de rendimiento por tiempo y volumen

El ejecutor manual de transferencias usa el catálogo de identidades y rutas de diagnóstico. Admite las rutas HQ_A_S1 y HQ_A_S2, con un flujo y un receptor temporal iPerf3. No habilita solicitudes desde FastAPI ni modifica sudoers.

## Perfiles iniciales

| Perfil | Protocolo | Objetivo | Tasa objetivo | Timeout cliente/receptor |
| --- | --- | --- | --- | --- |
| tcp-10s | TCP | 10 s | 20 Mbit/s | 20/25 s |
| udp-10s | UDP | 10 s | 20 Mbit/s | 20/25 s |
| tcp-100mb | TCP | 100 000 000 bytes | 20 Mbit/s | 60/70 s |
| tcp-500mb | TCP | 500 000 000 bytes | 100 Mbit/s | 65/75 s |
| tcp-1gb | TCP | 1 000 000 000 bytes | 100 Mbit/s | 115/125 s |
| tcp-2gb | TCP | 2 000 000 000 bytes | 100 Mbit/s | 220/230 s |
| tcp-5gb | TCP | 5 000 000 000 bytes | 100 Mbit/s | 520/530 s |

La tasa es un objetivo de pacing, no un policer estricto. El perfil por bytes permite comprobar el volumen recibido; no acredita identidad del contenido de un archivo. Los perfiles extendidos utilizan ventanas de 10 s desde 1 GB para acotar el tamaño del JSON. La verificación de contenido se realiza de forma independiente con el ejecutor TCP de contenido reproducible. El seguimiento en vivo y los escenarios de conmutación no están habilitados.

## Operación local

Desde servicios/consola-s08, como operador no root con autorización sudo existente:

```bash
python -B -m api.transfer_executor --profile tcp-100mb --route HQ_A_S1
```

Antes de emitir tráfico verificamos las identidades y rutas, disponibilidad de puerto 5201 y exclusión por operador. El receptor se enlaza a la dirección del endpoint, atiende una conexión y tiene timeout independiente. Esperamos su terminación y comprobamos la liberación de puertos. No instalamos servicios permanentes ni ejecutamos Python del repositorio como root.

## Interpretación de resultados

Conservamos métricas de emisor y receptor, intervalos, bytes, duración, tasa efectiva y retransmisiones TCP o pérdida y jitter UDP. Un resultado parcial o incompleto no equivale a un error del transporte. Los intervalos se obtienen de los JSON finales, no de telemetría en tiempo real. Tomamos los totales de recepción del resumen local del receptor y contrastamos bytes con el resumen del cliente; para UDP también contrastamos datagramas, pérdidas y jitter. Si los resúmenes son incompatibles rechazamos la medición. La suma de intervalos se registra de forma independiente mediante interval_accounting (MATCH o DISCREPANT), con las diferencias en bytes de ambos extremos. Una discrepancia no se interpreta como pérdida UDP ni se corrige inventando muestras; la serie temporal se debe presentar con su advertencia de calidad. No se deduce pérdida TCP de una diferencia de bytes ni se afirma certificación de fibra física.

La futura frontera privilegiada deberá imponer autorización, exclusión global, cancelación y limpieza; los escenarios de fallos requieren un watchdog y restauración independiente.

## Transferencia verificable de contenido

El ejecutor content_executor admite content-100mb, content-500mb, content-1gb, content-2gb y content-5gb. Cada perfil utiliza TCP, puerto 5202 y una tasa objetivo de 100 Mbit/s; no se acepta una dirección, comando, tamaño o tasa arbitrarios. Desde servicios/consola-s08, con la autorización local ya existente:

```bash
python -B -m api.content_executor --profile content-100mb --route HQ_A_S1
```

Generamos bloques reproducibles SHAKE-256 en memoria, transmitimos exactamente el volumen seleccionado, calculamos SHA-256 de forma independiente en emisor y receptor, y exigimos EOF sin datos adicionales. El resultado separa coincidencia de contenido, volumen y rendimiento. No escribimos archivos de carga de varios gigabytes. La coincidencia SHA-256 verifica el contenido generado y recibido, no autentica un servicio remoto frente a un atacante.

El supervisor verifica identidad y ruta, comparte el bloqueo local, comprueba disponibilidad y liberación de puertos y aplica timeout independiente a cada extremo. setpriv elimina privilegios, grupos suplementarios y capacidades antes de iniciar el intérprete aislado; el código Python se ejecuta como el operador, no como root. El receptor acepta únicamente una conexión desde la dirección HQ. No se instala un servicio privilegiado ni se autoriza acceso desde FastAPI. Los tiempos y perfiles son límites del laboratorio, no certificación de capacidad física de fibra.
