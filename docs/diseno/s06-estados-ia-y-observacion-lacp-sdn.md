# Estados de incertidumbre IA y observación LACP/SDN — Fase 06

## Alcance

En el NOC, el panel web distingue con precisión entre tres situaciones: **SIN DATOS / UNKNOWN** cuando la fuente IA no está disponible o la muestra caduca; **DESACUERDO IA / UNKNOWN** cuando existen medidas verificadas, pero los tres modelos no coinciden; e **INDICIO DE DEGRADACIÓN / UNKNOWN** cuando todos los modelos clasifican DEGRADED sin corroboración externa de la falla. Mantiene **NORMAL · EGRESO HQ** exclusivamente con consenso NORMAL válido, sin atribuir salud global ni verdad de terreno.

Se modifica únicamente el HTML/JavaScript y las pruebas de contrato de `servicios/topologia-s05/index.html`, con pruebas bajo `tests/test_s06_noc_ia_bridge.py`. No se cambia `app.py`, FRR, LACP, Faucet, OpenFlow, interfaces ni modelos. El NOC sigue siendo de solo lectura.

## Disponibilidad de fuentes LACP y SDN

La previsualización 9131 fue iniciada como `python3 -u servicios/topologia-s05/app.py --serve --port 9131` **sin** `NETLAB360_PRIV_OBSERVER=/usr/local/libexec/netlab360-observer`. Por contrato, `optional_privileged_snapshot()` devuelve la advertencia `Observaciones LACP/SDN: helper privilegiado no configurado` y los indicadores muestran `SIN DATOS` incluso si los agregadores y el controlador permanecen operativos.

El servicio systemd estable `netlab360-s05-noc.service` **sí** define esa variable y el lote S05-145B verificó dos muestras reales de LACP 2/2 en HQ/S1/S2 y Faucet/OpenFlow conectado. Eso es un antecedente, no evidencia de estado actual. Para conocer el estado **actual** consultar solo el endpoint de producción local `http://127.0.0.1:9130/api/v1/graph`, validando `lacp`, `sdn` y `source_warnings`. Si hay datos, el problema fue solo la previsualización; si no hay datos, diagnosticar lecturas/credenciales/frescura sin modificar la topología.

En futuras vistas temporales, únicamente después de comprobar que el helper existe y que `sudo -n /usr/local/libexec/netlab360-observer snapshot` está autorizado, se puede iniciar el NOC de previsualización con:

```bash
NETLAB360_PRIV_OBSERVER=/usr/local/libexec/netlab360-observer \
  python3 -u servicios/topologia-s05/app.py --serve --port 9131
```

Esto **habilita observación**, no activa ni modifica LACP/SDN. No reiniciar el NOC 9130, no ampliar sudoers ni ejecutar como root.

## Validación

La validación registró `S06-048_VALIDACION_COMPLETA=OK` y `RESULTADO_RC=0`; bitácora `~/netlab360-bootstrap/s06/cierre-s06-048-20261123_055201/S06_048_Cierre_Final.txt`. Los **23 tests específicos** del puente NOC IA finalizaron OK. El servicio NOC `netlab360-s05-noc` y exporter S04 estaban activos, el observador root-owned instalado y configurado. El endpoint original `127.0.0.1:9130/api/v1/graph` reportó tres LACP `up`, con **2/2 miembros** switch/cliente en HQ, S1 y S2, Faucet conectado (`connected=true`) y **25 reglas OpenFlow**, 18 nodos y 21 enlaces, **sin advertencias**. Se comprobó que la falta de datos de LACP/SDN en F09 provenía de la previsualización sin variable de observador, y no era una falla operacional.

El último bloque confirmó `ens33 192.168.47.40/24`, gateway `192.168.47.2`, 21 namespaces, cuatro contenedores, guardia `NONE/BASELINE`, qdisc `noqueue` y Git limpio. Verificó los cuatro textos de estado UI (NORMAL acotado, SIN DATOS, DESACUERDO IA e INDICIO DE DEGRADACIÓN). Ningún servicio, interfaz, contenedor, qdisc ni modelo se reinició o modificó.

[Auditoría prospectiva histórica](s06-auditoria-readiness-prospectiva.md).

## Recarga controlada y regresión transversal

Tras el FAULT HTTP HQ ya restaurado, la auditoría transversal encontró `/healthz=200`, `/api/v1/graph=200` y `/api/v1/s06/diagnostics=404`. El proceso systemd `netlab360-s05-noc.service` (PID **12848**) se había iniciado el **22/11/2026 a las 22:40:42 EST**, mientras el archivo Python instalado incorporó el endpoint S06 el **23/11/2026 a las 04:50:22 EST**. La ruta ya existía en `servicios/topologia-s05/app.py`, pero el proceso Python previo no la había cargado. Se comprobó `ExecStart`, `WorkingDirectory`, código y estado antes de intervenir.

Con autorización literal `AUTORIZO_REINICIO_NOC_9130`, se reinició **solo** la unidad NOC una vez; el proceso nuevo **2138999** devolvió `HTTP_IA=200` en el segundo intento. `/api/v1/graph` y `/healthz` permanecieron operativos tras el reinicio. La comprobación de la respuesta del adaptador dio **`IA_HQ_A_S1=UNKNOWN` y `IA_HQ_A_S2=UNKNOWN`**, conforme al contrato fail-closed ante ausencia de mediciones IA recientes; **no** se ejecutó la API temporal 9145, ni se falseó el diagnóstico NORMAL. Resultado real de la VM: `S06_NOC_IA_RECUPERADO=OK`, `RESULTADO_RC=0`; bitácora `~/netlab360-bootstrap/s06/recuperacion-noc-ia-20261123T180136Z/S06_Recuperacion_NOC_IA.txt`.

**Regresión observada:** 18 nodos, 21 enlaces, HA `BACKEND_HQ` principal, FIB S1 `s1p` / S2 `s2p`, LACP HQ/S1/S2 `up` con 2/2 miembros switch y cliente, Faucet/OpenFlow `connected` con **25 reglas**, ninguna advertencia del NOC, Prometheus listo y WAN/LAN `status` correctos; OSPF FULL **4/2/2** en HQ/S1/S2. Permanecieron 21 namespaces, cuatro Docker, `ens33 192.168.47.40/24`, gateway `192.168.47.2`, controlador `NONE/BASELINE` y qdisc `noqueue`. La observación transversal anterior está en `~/netlab360-bootstrap/s06/auditoria-transversal-http-20261123T175854Z/S06_Auditoria_HTTP_Continuacion.txt` (`RESULTADO_RC=0`).

**Criterio:** el contrato HTTP IA del NOC queda restaurado, pero el modelo no demuestra inferencia en vivo continua, pronóstico de fallas, generalización a FAULT HTTP ni despliegue productivo de la API IA temporal. No reiniciar o ejecutar nuevos experimentos para intentar convertir un `UNKNOWN` honesto en `NORMAL`.
