# Ejecución manual de diagnóstico

El catálogo delimita los orígenes, destinos y perfiles permitidos. El ejecutor manual admite ping corto y extendido, traceroute ICMP y la consulta HTTP del frontal HQ. iPerf3 permanece deshabilitado en este módulo.

## Operación

Ejecutamos como operador local autorizado, desde servicios/consola-s08, con el intérprete del entorno de la consola. Previamente renovamos la autorización sudo habitual mediante sudo -v. Ejemplo:

```bash
python -B -m api.probe_executor --action test.ping.short --route HQ_A_S1
```

No se instala ninguna regla sudoers, servicio, socket ni ruta HTTP. La aplicación web no llama al ejecutor. La ejecución manual utiliza sudo no interactivo para invocar ip netns exec con argumentos fijos y entorno delimitado; no ejecuta Python del repositorio como root. Antes de emitir tráfico comprobamos las identidades de ambos extremos y la ruta elegida. Los procesos tienen timeout interno y supervisor, y se serializan mediante un bloqueo por operador. El límite global y la frontera privilegiada para la aplicación se implementarán con el gestor y el servicio protegido.

## Resultados

El resultado JSON separa transporte OK, ERROR o TIMEOUT del estado observado: OK, PARTIAL, NO_REPLY, NOT_REACHED, HTTP_ERROR o SERVICE_UNAVAILABLE. El código de salida refleja el transporte, no un dictamen de conectividad. Un error de ejecución no se presenta como pérdida del 100 %. Los RTT individuales y P95 se calculan sobre respuestas observadas; no imputamos valores para paquetes perdidos. La latencia HTTP corresponde al tiempo total de curl y la respuesta identifica el backend observado, sin alterar la selección de HA.

Los resultados son observaciones puntuales. El ejecutor no almacena credenciales ni modifica rutas, interfaces, SQLite o servicios. La salida se conserva fuera del repositorio cuando se utiliza como evidencia. No constituye todavía un mecanismo de autorización para solicitudes web ni un sistema de trabajos persistente.
